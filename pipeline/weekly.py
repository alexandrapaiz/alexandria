"""The digest loop: one scheduled function, running every day at 15:00 UTC.

Two kinds of issue come out of it, and they are deliberately different reads
(owner's order, 2026-09-19):

- **Daily**, Tuesday through Sunday. What changed in the last 24 hours, short,
  150 to 400 words. Dispatch, not synthesis. A day whose papers were routine
  produces a one-line honest issue instead of a padded one; the emptiness check
  lives in code (`daily_is_empty`) so a genuinely empty day never reaches the
  model at all.
- **Weekly**, Monday. The deeper synthesis this file has always written, plus
  the citation slow loop that feeds it. Unchanged in scope.

The daily jobs, in order on a Monday:

1. **Slow loop** (Monday only) — batch-check citation counts on aged papers via
   Semantic Scholar's free API into the append-only citation_log. Trajectory
   (count now vs. last check) is the "gaining traction" evidence: the claim
   graph shows what our corpus thinks, citations show what the field thinks.
2. **Issue** — fixed SQL gathers the evidence streams for the day or the week;
   gpt-oss-120b writes it; it lands in the `digests` table (database of record,
   `kind` = 'daily' or 'weekly') and goes to subscribers by email via the
   owner's Gmail over authenticated SMTP. Issues are deliberately NOT published
   to the public repo (docs/vision.md §4).

Everything shares one scheduled function deliberately: Modal's free plan caps
scheduled functions at 5 and all five are taken (ingest, distill, triage,
interpret, and this one), so a daily issue could not have its own slot. Running
the citations inside the Monday branch also keeps the trajectories maximally
fresh. Either issue is a workflow, not an agent (ADR-6): every query is known
in advance, so the model only writes.

Needs secrets: `neon`, `groq`, and the Gmail secret(s) (GMAIL_ADDRESS +
GMAIL_APP_PASSWORD) once the newsletter is live; until then the run succeeds
and only skips the email.

    modal run pipeline/weekly.py                 # one-off, today's kind
    modal run pipeline/weekly.py --kind daily    # force a daily issue
    modal run pipeline/weekly.py --kind weekly   # force the weekly (+ citations)
    modal deploy pipeline/weekly.py              # install the daily schedule

NOTE: editing the schedule below changes nothing until `modal deploy` runs.
Merging a pull request does not deploy anything; there is no CI deploy job.
"""

import hashlib
import json
import re
import time
from datetime import date, timedelta

import modal

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"

S2_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
S2_BATCH_SIZE = 100       # ids per API call (S2 allows up to 500; be gentle)
MAX_PAPERS_PER_RUN = 400
MIN_AGE_DAYS = 7          # first check is the baseline; the second makes a trajectory
RECHECK_DAYS = 6          # at most one check per paper per weekly cycle

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1", "markdown==3.7")
    .add_local_file("prompts/digest.md", "/root/prompts/digest.md")
    .add_local_file("prompts/daily.md", "/root/prompts/daily.md")
)

app = modal.App("alexandria-weekly", image=image)


# ---------------- slow loop: citations ----------------

def s2_id(paper_id: str) -> str | None:
    """papers.id 'arxiv:2409.01234v2' -> Semantic Scholar id 'ARXIV:2409.01234'."""
    if not paper_id.startswith("arxiv:"):
        return None  # blog posts aren't in the citation graph
    raw = re.sub(r"v\d+$", "", paper_id.removeprefix("arxiv:"))
    return f"ARXIV:{raw}"


def check_citations(conn, max_papers: int = MAX_PAPERS_PER_RUN) -> int:
    import httpx

    rows = conn.execute(
        """
        select p.id
        from papers p
        join triage_log t on t.paper_id = p.id
            and t.decision in ('index', 'distill', 'deep_read')
        left join lateral (
            select max(checked_at) as last_check
            from citation_log where paper_id = p.id
        ) c on true
        where p.id like 'arxiv:%%'
          and p.published_at <= current_date - %s
          and (c.last_check is null or c.last_check < now() - make_interval(days => %s))
        order by c.last_check asc nulls first
        limit %s
        """,
        (MIN_AGE_DAYS, RECHECK_DAYS, max_papers),
    ).fetchall()
    ids = [r[0] for r in rows]
    print(f"{len(ids)} papers due for a citation check")

    written = 0
    for i in range(0, len(ids), S2_BATCH_SIZE):
        chunk = ids[i : i + S2_BATCH_SIZE]
        resp = httpx.post(
            S2_BATCH_URL,
            params={"fields": "citationCount"},
            json={"ids": [s2_id(pid) for pid in chunk]},
            timeout=60,
        )
        if resp.status_code == 429:
            print("rate limited by Semantic Scholar; continuing with what we have")
            break
        resp.raise_for_status()
        # response aligns positionally with the request; unknown papers are null
        for pid, result in zip(chunk, resp.json()):
            if result is None or result.get("citationCount") is None:
                continue
            conn.execute(
                "insert into citation_log (paper_id, citations) values (%s, %s)",
                (pid, result["citationCount"]),
            )
            written += 1
        conn.commit()
        time.sleep(2)
    print(f"citation checks written: {written}")
    return written


# ---------------- digest ----------------

def gather(conn) -> dict:
    """Fixed queries; the model never chooses what to retrieve."""
    stats = conn.execute(
        """
        select
          (select count(*) from papers where fetched_at > now() - interval '7 days'),
          (select count(*) from claims where created_at > now() - interval '7 days'),
          (select count(*) from claim_links where created_at > now() - interval '7 days')
        """
    ).fetchone()

    new_claims = conn.execute(
        """
        select c.id, c.claim, c.topics, p.title, p.url, p.tier,
               t.decision, t.score,
               coalesce(array_agg(l.relation || ' -> claim ' || l.to_claim)
                        filter (where l.from_claim is not null), '{}'),
               c.evidence, c.procedure, p.authors[1:3], p.institutions
        from claims c
        join papers p on p.id = c.paper_id
        left join triage_log t on t.paper_id = c.paper_id
        left join claim_links l on l.from_claim = c.id
        where c.created_at > now() - interval '7 days'
        group by c.id, c.claim, c.topics, p.title, p.url, p.tier, t.decision, t.score,
                 c.evidence, c.procedure, p.authors, p.institutions
        order by case t.decision when 'deep_read' then 0 else 1 end,
                 t.score desc nulls last
        limit 22
        """
    ).fetchall()

    superseded = conn.execute(
        """
        select old.claim, new.claim, l.confidence,
               po.title, po.url, pn.title, pn.url
        from claim_links l
        join claims old on old.id = l.to_claim
        join claims new on new.id = l.from_claim
        join papers po on po.id = old.paper_id
        join papers pn on pn.id = new.paper_id
        where l.relation = 'refines'
          and coalesce(l.confidence, 0) >= 0.75
          and l.created_at > now() - interval '7 days'
          and old.paper_id != new.paper_id  -- a paper refining itself is not a supersession
        order by l.confidence desc
        limit 10
        """
    ).fetchall()

    supported = conn.execute(
        """
        select c.id, c.claim, p.title, p.url, count(*) as supports
        from claims c
        join papers p on p.id = c.paper_id
        join claim_links l on l.to_claim = c.id and l.relation = 'supports'
        group by c.id, c.claim, p.title, p.url
        having count(*) >= 2
        order by count(*) desc
        limit 12
        """
    ).fetchall()

    movers = conn.execute(
        """
        with checks as (
            select paper_id, citations, checked_at,
                   row_number() over (partition by paper_id order by checked_at desc) as rn
            from citation_log
        )
        select p.title, p.url, prev.citations, latest.citations
        from checks latest
        join checks prev on prev.paper_id = latest.paper_id and prev.rn = 2
        join papers p on p.id = latest.paper_id
        where latest.rn = 1 and latest.citations > prev.citations
        order by latest.citations - prev.citations desc
        limit 12
        """
    ).fetchall()

    deprecated = conn.execute(
        """
        select old.claim, new.claim, l.confidence, p.title, p.url
        from claim_links l
        join claims old on old.id = l.to_claim
        join claims new on new.id = l.from_claim
        join papers p on p.id = old.paper_id
        where l.relation = 'contradicts'
          and coalesce(l.confidence, 0) >= 0.7
          and l.created_at > now() - interval '7 days'
        """
    ).fetchall()

    deep_reads = conn.execute(
        """
        select p.title, p.url, t.reasoning
        from triage_log t
        join papers p on p.id = t.paper_id
        where t.decision = 'deep_read'
          and t.created_at > now() - interval '7 days'
        limit 10
        """
    ).fetchall()

    return {
        "stats": {"papers_ingested": stats[0], "claims_distilled": stats[1], "edges_drawn": stats[2]},
        "new_claims": [
            {
                "claim_id": r[0], "claim": r[1][:280], "topics": r[2],
                "paper": r[3], "url": r[4], "tier": r[5],
                "triage": r[6], "score": r[7], "edges": r[8],
                "evidence": (r[9] or "")[:350] or None,
                "procedure": (r[10] or "")[:600] or None,
                "authors": r[11] or None,
                "institutions": r[12] or None,
            }
            for r in new_claims
        ],
        "superseded": [
            {"old_claim": r[0][:280], "new_claim": r[1][:280], "confidence": r[2],
             "old_paper": r[3], "old_url": r[4], "new_paper": r[5], "new_url": r[6]}
            for r in superseded
        ],
        "traction": {
            "supported_claims": [
                {"claim_id": r[0], "claim": r[1][:400], "paper": r[2], "url": r[3], "supports": r[4]}
                for r in supported
            ],
            "citation_movers": [
                {"paper": r[0], "url": r[1], "citations_before": r[2], "citations_now": r[3]}
                for r in movers
            ],
        },
        "deprecated": [
            {"old_claim": r[0][:400], "contradicted_by": r[1][:400], "confidence": r[2],
             "paper": r[3], "url": r[4]}
            for r in deprecated
        ],
        "deep_reads": [{"paper": r[0], "url": r[1], "why": (r[2] or "")[:200]} for r in deep_reads],
    }


# ---------------- daily issue ----------------

# How many claims the daily issue may see. The weekly takes 22 because it is
# synthesising a week; a daily that considered twenty findings would be a
# weekly with the wrong date on it.
DAILY_CLAIM_LIMIT = 10

# The window, in hours. The daily crons run 11:00 (ingest), 11:30 (distill),
# 12:00 (triage) and 14:00 (interpret) UTC, and this function runs at 15:00, so
# a 24-hour lookback from here covers exactly one complete pipeline day and
# nothing twice.
#
# It goes through make_interval() rather than straight into the SQL, because
# Postgres reads INTERVAL as a type name expecting a literal after it and will
# not accept a placeholder there. check_citations() above solves the same
# problem the same way.
DAILY_WINDOW_HOURS = 24


def gather_daily(conn) -> dict:
    """The last 24 hours only. Same discipline as gather(): fixed queries.

    Deliberately narrower than the weekly's payload. No traction streams
    (supported claims, citation movers), because acceptance accumulates over
    weeks and reporting it daily would be noise dressed as news, and because
    the citation loop only refreshes on Mondays anyway.
    """
    stats = conn.execute(
        """
        select
          (select count(*) from papers where fetched_at > now() - make_interval(hours => %s)),
          (select count(*) from claims where created_at > now() - make_interval(hours => %s)),
          (select count(*) from claim_links where created_at > now() - make_interval(hours => %s))
        """,
        (DAILY_WINDOW_HOURS, DAILY_WINDOW_HOURS, DAILY_WINDOW_HOURS),
    ).fetchone()

    new_claims = conn.execute(
        """
        select c.id, c.claim, c.topics, p.title, p.url, p.tier,
               t.decision, t.score,
               coalesce(array_agg(l.relation || ' -> claim ' || l.to_claim)
                        filter (where l.from_claim is not null), '{}'),
               c.evidence, c.procedure, p.authors[1:3], p.institutions
        from claims c
        join papers p on p.id = c.paper_id
        left join triage_log t on t.paper_id = c.paper_id
        left join claim_links l on l.from_claim = c.id
        where c.created_at > now() - make_interval(hours => %s)
        group by c.id, c.claim, c.topics, p.title, p.url, p.tier, t.decision, t.score,
                 c.evidence, c.procedure, p.authors, p.institutions
        order by case t.decision when 'deep_read' then 0 else 1 end,
                 t.score desc nulls last
        limit %s
        """,
        (DAILY_WINDOW_HOURS, DAILY_CLAIM_LIMIT),
    ).fetchall()

    superseded = conn.execute(
        """
        select old.claim, new.claim, l.confidence,
               po.title, po.url, pn.title, pn.url
        from claim_links l
        join claims old on old.id = l.to_claim
        join claims new on new.id = l.from_claim
        join papers po on po.id = old.paper_id
        join papers pn on pn.id = new.paper_id
        where l.relation = 'refines'
          and coalesce(l.confidence, 0) >= 0.75
          and l.created_at > now() - make_interval(hours => %s)
          and old.paper_id != new.paper_id  -- a paper refining itself is not a supersession
        order by l.confidence desc
        limit 5
        """,
        (DAILY_WINDOW_HOURS,),
    ).fetchall()

    deprecated = conn.execute(
        """
        select old.claim, new.claim, l.confidence, p.title, p.url
        from claim_links l
        join claims old on old.id = l.to_claim
        join claims new on new.id = l.from_claim
        join papers p on p.id = old.paper_id
        where l.relation = 'contradicts'
          and coalesce(l.confidence, 0) >= 0.7
          and l.created_at > now() - make_interval(hours => %s)
        limit 5
        """,
        (DAILY_WINDOW_HOURS,),
    ).fetchall()

    deep_reads = conn.execute(
        """
        select p.title, p.url, t.reasoning
        from triage_log t
        join papers p on p.id = t.paper_id
        where t.decision = 'deep_read'
          and t.created_at > now() - make_interval(hours => %s)
        limit 5
        """,
        (DAILY_WINDOW_HOURS,),
    ).fetchall()

    return {
        "stats": {"papers_ingested": stats[0], "claims_distilled": stats[1], "edges_drawn": stats[2]},
        "new_claims": [
            {
                "claim_id": r[0], "claim": r[1][:280], "topics": r[2],
                "paper": r[3], "url": r[4], "tier": r[5],
                "triage": r[6], "score": r[7], "edges": r[8],
                "evidence": (r[9] or "")[:350] or None,
                "procedure": (r[10] or "")[:600] or None,
                "authors": r[11] or None,
                "institutions": r[12] or None,
            }
            for r in new_claims
        ],
        "superseded": [
            {"old_claim": r[0][:280], "new_claim": r[1][:280], "confidence": r[2],
             "old_paper": r[3], "old_url": r[4], "new_paper": r[5], "new_url": r[6]}
            for r in superseded
        ],
        "deprecated": [
            {"old_claim": r[0][:400], "contradicted_by": r[1][:400], "confidence": r[2],
             "paper": r[3], "url": r[4]}
            for r in deprecated
        ],
        "deep_reads": [{"paper": r[0], "url": r[1], "why": (r[2] or "")[:200]} for r in deep_reads],
    }


def daily_is_empty(payload: dict) -> bool:
    """True when the day produced nothing an issue could honestly be about.

    This is the hard floor under the owner's quality bar, and it is in code on
    purpose. The prompt also tells the model to write the one-line issue when
    the day is merely routine, but a model asked to write about an empty
    payload will find something to say, every time. When all four evidence
    streams are empty there is nothing to find, so the model is never asked.
    """
    return not any(
        payload.get(key) for key in ("new_claims", "deprecated", "superseded", "deep_reads")
    )


def empty_issue(dates: str) -> str:
    """The honest one-line issue. Same wording the prompt uses for a routine
    day, so a reader cannot tell which path produced it, because the message is
    the same either way: we looked, and there was nothing worth your time."""
    return (
        f"# Nothing worth your time today [{dates}]\n\n"
        "Today's papers were routine, so there is no issue. The next one comes "
        "tomorrow, and Monday's weekly synthesis covers the whole week."
    )


# Groq's free tier caps request size (413 above it); trim the least-critical
# evidence (the tail of new_claims, already sorted best-first) until we fit
# the request Groq sees is prompt + payload, and the prompt has grown with
# editorial rules — keep the sum under the free tier's 413 threshold
MAX_PAYLOAD_CHARS = 17000


def shrink(payload: dict) -> str:
    body = json.dumps(payload, separators=(",", ":"), default=str)
    while len(body) > MAX_PAYLOAD_CHARS and payload["new_claims"]:
        payload["new_claims"].pop()
        body = json.dumps(payload, separators=(",", ":"), default=str)
    return body


# The weekly's depth sections got truncated at the default cap, so it asks for
# room. The daily is 150-400 words by design, and a generous cap on a short
# issue is an invitation to pad; 1200 is comfortably above a 400-word issue and
# well below a weekly one.
MAX_TOKENS = {"weekly": 6000, "daily": 1200}


def write_digest(payload: dict, prompt: str, kind: str = "weekly") -> str:
    import os

    import httpx

    user = shrink(payload)
    print(f"payload: {len(user)} chars, {len(payload['new_claims'])} new claims kept")
    for attempt in range(4):
        resp = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY'].strip()}"},
            json={
                "model": MODEL,
                "temperature": 0.3,
                "max_completion_tokens": MAX_TOKENS[kind],
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user},
                ],
            },
            timeout=300,
        )
        if resp.status_code == 429 and attempt < 3:
            wait = float(resp.headers.get("retry-after") or 30 * (attempt + 1))
            print(f"rate limited; backing off {wait:.0f}s")
            time.sleep(min(wait, 180))
            continue
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    raise RuntimeError("groq: exhausted retries")


# The standing introduction under the title. Fixed in code, not written by the
# model, so the brand line never drifts issue to issue. One per kind, because
# the two issues promise the reader different things and each line should say
# which one they are holding.
MASTHEAD = {
    "weekly": (
        "*The latest in AI research, read in full: the week in synthesis. "
        "What's new, what's gaining acceptance, and what newer evidence has "
        "overturned.*"
    ),
    "daily": (
        "*The latest in AI research, read in full: what changed in the last "
        "24 hours. The week in synthesis arrives every Monday.*"
    ),
}


def add_masthead(body: str, kind: str = "weekly") -> str:
    masthead = MASTHEAD[kind]
    lines = body.split("\n")
    if lines and lines[0].startswith("#"):
        return "\n".join([lines[0], "", masthead, ""] + lines[1:])
    return f"{masthead}\n\n{body}"


def send_newsletter(conn, key: str, body: str) -> str:
    """Email the issue to active subscribers (friends-and-family phase).

    Sends through the owner's Gmail via authenticated SMTP: at this scale
    (<20 recipients) Gmail's own sender reputation is the deliverability
    strategy, and no domain or email service is needed. Past ~20 subscribers
    this graduates to SES + a purchased domain + a real unsubscribe endpoint
    (docs/vision.md §4). No-op until the `gmail` secret exists
    (GMAIL_ADDRESS + GMAIL_APP_PASSWORD)."""
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    addr = os.environ.get("GMAIL_ADDRESS", "").strip()
    pw = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    if not addr or not pw:
        return "no gmail secret; email send skipped (digest is in the database)"
    rows = conn.execute(
        "select email, name from subscribers where status = 'active'"
    ).fetchall()
    if not rows:
        return "no active subscribers; nothing to send"

    import markdown as md

    def is_list_line(line: str) -> bool:
        return bool(re.match(r"^\s*([-*] |\d+[.)] )", line))

    # markdown only recognizes a list after a blank line; without one the
    # literal dashes leak into the rendered email
    lines, spaced = body.split("\n"), []
    for line in lines:
        if is_list_line(line) and spaced and spaced[-1].strip() and not is_list_line(spaced[-1]):
            spaced.append("")
        spaced.append(line)

    html_body = md.markdown("\n".join(spaced), extensions=["extra"])
    html = (
        "<div style='max-width:640px;margin:0 auto;font-family:Georgia,serif;"
        "font-size:16px;line-height:1.6;color:#222'>"
        f"{html_body}"
        "<hr><p style='font-size:12px;color:#888'>You're receiving this as a "
        "friend of alexandria. Reply to this email to unsubscribe.</p></div>"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(addr, pw)
        for email, name in rows:
            msg = MIMEMultipart("alternative")
            # subject = the issue's editorial title (the digest's own H1);
            # the W code is an internal id and never reader-facing
            subject = f"alexandria digest — {key}"
            if body.startswith("# "):
                subject = body.split("\n", 1)[0][2:].strip()
            msg["Subject"] = subject
            msg["From"] = f"alexandria <{addr}>"
            msg["To"] = email
            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html, "html"))
            smtp.sendmail(addr, [email], msg.as_string())
    return f"sent {key} to {len(rows)} subscribers via Gmail"


# ---------------- issue keys ----------------

# Both kinds share the digests table and its one unique key, so their key
# formats must never collide. '2026-W38' and '2026-09-19' cannot, and the
# `kind` column carries the distinction explicitly rather than leaving it to
# whoever next reads a key and guesses.

def weekly_key(today: date) -> tuple[str, str]:
    """Monday's run labels the ISO week that just ended (yesterday = Sunday)."""
    y = today - timedelta(days=1)
    key = f"{y.isocalendar().year}-W{y.isocalendar().week:02d}"
    monday = y - timedelta(days=6)
    if monday.month == y.month:
        dates = f"{monday.strftime('%B')} {monday.day}–{y.day}, {y.year}"
    else:
        dates = (f"{monday.strftime('%B')} {monday.day} – "
                 f"{y.strftime('%B')} {y.day}, {y.year}")
    return key, dates


def daily_key(today: date) -> tuple[str, str]:
    """The daily covers the 24 hours ending at this 15:00 UTC run, which is
    overwhelmingly today, so it is dated today."""
    return today.isoformat(), f"{today.strftime('%B')} {today.day}, {today.year}"


def kind_for(today: date) -> str:
    """Monday is the weekly synthesis. Every other day is the daily dispatch."""
    return "weekly" if today.weekday() == 0 else "daily"


# ---------------- the scheduled run ----------------

@app.function(
    # Every day at 15:00 UTC, after the four daily crons (ingest 11:00,
    # distill 11:30, triage 12:00, interpret 14:00) have finished the day's
    # pipeline. Monday's run is the weekly; the rest are dailies.
    schedule=modal.Cron("0 15 * * *"),
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq"),
             modal.Secret.from_name("Gmail"), modal.Secret.from_name("gmail_pass")],
    timeout=1800,
)
def digest(kind: str = "") -> str:
    import os

    import psycopg

    today = date.today()
    kind = kind or kind_for(today)
    if kind not in MASTHEAD:
        # a typo in a manual --kind would otherwise fall through to the daily
        # branch and quietly write the wrong issue under the wrong key
        raise ValueError(f"kind must be 'weekly' or 'daily', got {kind!r}")
    if kind == "weekly":
        key, dates = weekly_key(today)
        prompt_path = "/root/prompts/digest.md"
    else:
        key, dates = daily_key(today)
        prompt_path = "/root/prompts/daily.md"
    prompt = open(prompt_path).read()
    sha = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        if kind == "weekly":
            # the slow loop feeds the weekly's traction section, so it runs
            # with it and only with it
            try:
                check_citations(conn)
            except Exception as exc:
                print(f"citation check failed ({exc}); digest proceeds without fresh citations")
            payload = gather(conn)
        else:
            payload = gather_daily(conn)
        payload["dates"] = dates
        payload["week" if kind == "weekly" else "date"] = key
        print(f"{kind} {key}: {payload['stats']} | new_claims={len(payload['new_claims'])} "
              f"deprecated={len(payload['deprecated'])}")

        if kind == "daily" and daily_is_empty(payload):
            # nothing to write about, so nothing is written about it
            print("no new evidence in the last 24 hours; sending the one-line issue")
            body = empty_issue(dates)
            model = None
        else:
            body = write_digest(payload, prompt, kind)
            model = MODEL
        body = add_masthead(body, kind)

        conn.execute(
            """
            insert into digests (week, kind, body, model, prompt_sha)
            values (%s, %s, %s, %s, %s)
            on conflict (week) do update
                set kind = excluded.kind, body = excluded.body,
                    model = excluded.model, prompt_sha = excluded.prompt_sha,
                    created_at = now()
            """,
            (key, kind, body, model, sha),
        )
        conn.commit()
        try:
            print(send_newsletter(conn, key, body))
        except Exception as exc:
            # the digests table is the record of record; a send failure must
            # never fail the run
            print(f"newsletter send failed ({exc}); digest is safe in the database")
    return body


@app.local_entrypoint()
def main(kind: str = ""):
    """`modal run pipeline/weekly.py` writes today's kind; pass --kind daily or
    --kind weekly to force one."""
    body = digest.remote(kind)
    print("\n" + body)
