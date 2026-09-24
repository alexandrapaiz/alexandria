"""Weekly loop: refresh citation trajectories, then write and publish the digest.

One scheduled function doing two jobs, in order:

1. **Slow loop** — batch-check citation counts on aged papers via Semantic
   Scholar's free API into the append-only citation_log. Trajectory (count now
   vs. last check) is the "gaining traction" evidence: the claim graph shows
   what our corpus thinks, citations show what the field thinks.
2. **Digest** — fixed SQL gathers five evidence streams (new claims, claims
   with 2+ supports edges, citation movers, fresh deprecations, deep-read
   flags); the generator model writes the three-section digest; it lands in the
   `digests` table (database of record) and goes to subscribers by email via
   the owner's Gmail over authenticated SMTP. The issue itself is free in
   full (docs/vision.md §0, amended 2026-09-17): it is the acquisition
   engine, and it is also published on the site at /library/<week>. The
   paid product is the spine, the skills and the graph, not the issue.

They share one function deliberately: Modal's free plan caps scheduled
functions at 5, and the citations exist for the digest — running them in the
same Monday process makes the trajectories maximally fresh and costs no slot.
The digest is a workflow, not an agent (ADR-6): every query is known in
advance, so the model only writes.

Needs secrets: `neon`, `groq`, and the Gmail secret(s) (GMAIL_ADDRESS +
GMAIL_APP_PASSWORD) once the newsletter is live; until then the run succeeds
and only skips the email.

    python3 pipeline/budget.py                    # does the request fit?
    modal run pipeline/weekly.py::preflight        # does the model still exist?
    modal run pipeline/weekly.py                  # one-off manual run (both, then print)
    modal deploy pipeline/weekly.py               # install the Monday schedule

The deploy command, as one line, which is what the chair runs after a merge
that touches this file or prompts/digest.md:

    python3 pipeline/budget.py \
      && modal run pipeline/weekly.py::preflight \
      && modal deploy pipeline/weekly.py

Neither guard is optional ceremony, and they check different things.

**Does the request fit?** Incident 22: an editorial merge grew the generator
prompt past the model's per-request token ceiling, Groq answered 413, and no
issue was written. `pipeline/budget.py` owns that arithmetic and runs in CI on
every change to a generator prompt or this pipeline, before deploy, and again
inside the container before it calls Groq.

**Does the model still exist?** Incident 24: Groq withdrew `groq/compound`, the
press answered 404 for three days, and the discovery was the owner noticing that
Monday's issue never arrived. The budget guard had been perfectly happy: it
checks that a request fits, not that there is anything to send it to. So
`preflight` asks `GET /models` before the deploy, `check_availability` asks
again at the start of every run, `FALLBACK_MODELS` gives the run somewhere to
go when the answer is no, and `notify_owner` mails the owner the moment the
press cannot print. That last one is the important one. A press that fails
silently has no failure mode the org can respond to.
"""

import hashlib
import pathlib
import re
import time
from datetime import date, timedelta

import modal

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Incident 24, 2026-09-23: Groq withdrew `groq/compound` and the press answered
# 404 for three days without telling anyone. The press had been moved to it on
# 2026-09-19 (PR #51) for one reason, its 70,000 TPM, and a capacity number
# turned out to be the worst possible reason to pick a model: compound was an
# agentic *preview* system, and previews are withdrawn without the deprecation
# notice production models get.
#
# So the press no longer has a model. It has an ordered list, and three rules
# about it.
#
# 1. **Production before preview.** `openai/gpt-oss-120b` is the primary
#    because Groq lists it as a production model, which is the only status that
#    carries a deprecation commitment.
# 2. **A different vendor at rank two.** `qwen/qwen3.8-27b` is preview rather
#    than production, and it is second anyway, because the failure this list
#    exists to survive is a *family* withdrawal. If OpenAI's two gpt-oss models
#    go the way compound went, they will very likely go together, and a
#    fallback list of three OpenAI models is one point of failure wearing three
#    hats.
# 3. **Rank three covers capacity, not deprecation.** `openai/gpt-oss-20b` is
#    the same family and the same limits as the primary, so it does nothing
#    against a withdrawal, but it is a real second chance against a 429 or a
#    single-model outage.
#
# Every entry is verified by pipeline/budget.py, which reads this list out of
# this file rather than keeping a copy, and refuses the deploy if any entry has
# no published limits or has been withdrawn.
FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]

# The default. `write_digest` walks the list from here and may end up further
# down it; whichever model actually wrote the issue is what lands in the
# `digests.model` column, never this constant.
MODEL = FALLBACK_MODELS[0]

# Retries per model before the press gives up on it and tries the next one.
# 429 is the case this exists for: Groq's TPM is per model, so moving down the
# list is itself a rate-limit remedy and not only a deprecation remedy.
RETRIES_PER_MODEL = 4
BACKOFF_SECONDS = 30      # doubled each attempt, capped below
BACKOFF_CEILING = 180

S2_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
S2_BATCH_SIZE = 100       # ids per API call (S2 allows up to 500; be gentle)
MAX_PAPERS_PER_RUN = 400
MIN_AGE_DAYS = 7          # first check is the baseline; the second makes a trajectory
RECHECK_DAYS = 6          # at most one check per paper per weekly cycle

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1", "markdown==3.7",
                 "tiktoken==0.8.0")
    .add_local_file("prompts/digest.md", "/root/prompts/digest.md")
    # the budget guard runs in the container too, so a request that cannot fit
    # is refused here with the arithmetic rather than 413'd by Groq
    .add_local_file("pipeline/budget.py", "/root/budget.py")
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
        order by l.confidence desc
        limit 8
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


def budget():
    """pipeline/budget.py, wherever this is running from.

    Modal drops it at /root/budget.py; a local `python3 pipeline/weekly.py`
    import finds it beside this file. Either way the constants the guard
    checks in CI are the constants the run uses, which is the whole point.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import budget as module

    return module


class ModelGone(RuntimeError):
    """The provider does not have this model any more. Incident 24's 404."""


class RateLimited(RuntimeError):
    """429 survived every retry on this model."""


class PressCannotPrint(RuntimeError):
    """No model in the fallback list could write the issue.

    This is the exception the owner gets an email about. It carries the whole
    trail, one line per model, because the point of the email is that she
    should not have to open Modal's logs to know what happened.
    """


# Depth sections got truncated at the default cap, so the issue asks for room.
# Every one of these tokens is spent the moment the request is sent, whether or
# not the model writes them: Groq's per-request ceiling counts the reservation,
# not the output. The one issue the press has actually written came to 1,103
# tokens, so 6,000 is generous rather than tight.
MAX_COMPLETION_TOKENS = 6000


def log_limits(resp, model: str) -> None:
    """Groq's own account of the budget, which outranks anything we assume."""
    limit = resp.headers.get("x-ratelimit-limit-tokens")
    remaining = resp.headers.get("x-ratelimit-remaining-tokens")
    if limit:
        print(f"groq says: limit {limit} tokens, {remaining} remaining. If that "
              f"disagrees with budget.MODELS[{model!r}], the header is right.")


def check_availability() -> set[str]:
    """Which models Groq actually has, right now, for our key.

    Incident 24's standing fix. The budget guard checks that the request fits;
    this checks that there is something to send it to. It costs no tokens
    against any ceiling, so it runs at deploy and again at the start of every
    run, and it raises loudly rather than guessing.
    """
    import os

    guard = budget()
    available = guard.available_models(os.environ.get("GROQ_API_KEY", ""))
    print(f"groq has {len(available)} active models for this key")
    usable = [m for m in FALLBACK_MODELS if m in available]
    missing = [m for m in FALLBACK_MODELS if m not in available]
    for name in missing:
        print(f"AVAILABILITY: {name} is in FALLBACK_MODELS but Groq does not "
              "list it. A request to it would 404, as it did in incident 24.")
    print(f"fallbacks present: {usable or 'NONE'}")
    if not usable:
        raise PressCannotPrint(
            "Groq lists none of the press's fallback models "
            f"({', '.join(FALLBACK_MODELS)}). The press cannot print until "
            "pipeline/weekly.py FALLBACK_MODELS and pipeline/budget.py MODELS "
            "are updated from https://console.groq.com/docs/models."
        )
    return available


def call_model(model: str, prompt: str, user: str) -> str:
    """One model, with backoff on 429. Raises so the caller can move down the list."""
    import os

    import httpx

    for attempt in range(RETRIES_PER_MODEL):
        resp = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY'].strip()}"},
            json={
                "model": model,
                "temperature": 0.3,
                "max_completion_tokens": MAX_COMPLETION_TOKENS,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user},
                ],
            },
            timeout=300,
        )
        log_limits(resp, model)

        # 404 is a withdrawn or misspelled model, and no amount of waiting fixes
        # it. Going straight to the next model is the whole point of the list.
        if resp.status_code == 404:
            raise ModelGone(f"404 Not Found: {resp.text[:400]}")

        if resp.status_code == 429:
            wait = float(resp.headers.get("retry-after")
                         or BACKOFF_SECONDS * (2 ** attempt))
            wait = min(wait, BACKOFF_CEILING)
            if attempt < RETRIES_PER_MODEL - 1:
                print(f"{model}: rate limited (attempt {attempt + 1} of "
                      f"{RETRIES_PER_MODEL}); backing off {wait:.0f}s")
                time.sleep(wait)
                continue
            raise RateLimited(
                f"429 after {RETRIES_PER_MODEL} attempts: {resp.text[:400]}")

        if resp.status_code >= 400:
            # incident 22 cost a day partly because raise_for_status() prints
            # the status and throws the body away. The body is where Groq
            # states the actual limit and the actual request size.
            print(f"groq {resp.status_code} on {model}: {resp.text[:1000]}")
            # 400 on a model that exists is usually an unsupported parameter,
            # which the next model may well accept
            raise ModelGone(f"{resp.status_code}: {resp.text[:400]}")

        choice = resp.json()["choices"][0]
        message = choice["message"]
        fired = message.get("executed_tools") or []
        if fired:
            # No model in FALLBACK_MODELS is agentic today. If one ever is, the
            # issue may contain something that did not come from our corpus,
            # and that is a fact about the issue, not a warning about the call.
            names = ", ".join(sorted({t.get("type", "?") for t in fired}))
            print(f"WARNING: {model} executed built-in tools ({names}). Treat "
                  "this issue as unverified and check it against the payload "
                  "before sending.")
        content = message.get("content")
        if not content:
            raise ModelGone(
                f"{model} returned no content (finish_reason "
                f"{choice.get('finish_reason')!r}); no issue was written")
        return content.strip()
    raise RateLimited(f"{model}: exhausted retries")


def write_digest(payload: dict, prompt: str,
                 available: set[str] | None = None) -> tuple[str, str]:
    """Write the issue, walking the fallback list. Returns (body, model used).

    Each model gets its own copy of the payload, because `fit_payload` trims in
    place: sharing one payload would mean the second model inherits the first
    model's trimming and writes a thinner issue than it had room for.
    """
    import copy

    guard = budget()
    tried: list[str] = []

    for model in FALLBACK_MODELS:
        if available is not None and model not in available:
            tried.append(f"{model}: not listed by Groq for this key; skipped "
                         "without a request (this is incident 24's 404)")
            continue
        try:
            user = guard.fit_payload(copy.deepcopy(payload), prompt,
                                     MAX_COMPLETION_TOKENS, model)
        except (guard.BudgetExceeded, KeyError) as exc:
            tried.append(f"{model}: does not fit. {exc}")
            print(f"{model}: over budget, trying the next fallback. {exc}")
            continue

        report = guard.check_request(prompt, user, MAX_COMPLETION_TOKENS, model)
        print(f"{model}: payload {len(user)} chars; budget: {report.summary()}")
        if not report.fits:
            # fit_payload should have made this impossible; if it did not, say
            # so here rather than letting Groq say it with a 413
            tried.append(f"{model}: {report.summary()}")
            continue

        try:
            body = call_model(model, prompt, user)
        except (ModelGone, RateLimited) as exc:
            tried.append(f"{model}: {exc}")
            print(f"{model} failed ({exc}); trying the next fallback")
            continue
        print(f"issue written by {model}")
        return body, model

    raise PressCannotPrint(
        "every model in the press's fallback list failed:\n  "
        + "\n  ".join(tried)
    )


# The standing introduction under the title. Fixed in code, not written by the
# model, so the brand line never drifts issue to issue.
MASTHEAD = (
    "*The latest in AI research, read in full and distilled weekly: "
    "what's new, what's gaining acceptance, and what newer evidence has "
    "overturned.*"
)


def add_masthead(body: str) -> str:
    lines = body.split("\n")
    if lines and lines[0].startswith("#"):
        return "\n".join([lines[0], "", MASTHEAD, ""] + lines[1:])
    return f"{MASTHEAD}\n\n{body}"


def send_newsletter(conn, week: str, body: str) -> str:
    """Email the digest to active subscribers (friends-and-family phase).

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
            subject = f"alexandria digest — {week}"
            if body.startswith("# "):
                subject = body.split("\n", 1)[0][2:].strip()
            msg["Subject"] = subject
            msg["From"] = f"alexandria <{addr}>"
            msg["To"] = email
            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html, "html"))
            smtp.sendmail(addr, [email], msg.as_string())
    return f"sent {week} to {len(rows)} subscribers via Gmail"


def notify_owner(subject: str, detail: str) -> str:
    """Tell the owner the press could not print, by email, immediately.

    Incident 24's real cost was not the 404. It was that the 404 was discovered
    three days later, by the owner noticing her inbox was empty. A press that
    fails silently has no failure mode the org can respond to, so every path
    out of this run that ends without an issue goes through here first.

    Same SMTP path the newsletter already uses, so it needs no new secret and
    no new service. The alert goes to the owner's own Gmail address, the one
    the `Gmail` secret provides, unless `PRESS_ALERT_TO` names another; a
    self-addressed mail is the cheapest reliable channel we have.

    Never raises. A failure to deliver the alarm must not replace the original
    error with a different one, so this returns a status string and the caller
    prints it.
    """
    import os
    import smtplib
    from email.mime.text import MIMEText

    addr = os.environ.get("GMAIL_ADDRESS", "").strip()
    pw = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    to = os.environ.get("PRESS_ALERT_TO", "").strip() or addr
    if not addr or not pw:
        return ("NOT NOTIFIED: no gmail secret in this environment, so the "
                "owner was not told. This is the incident 24 failure mode and "
                "it is still open here.")
    body = (
        f"{detail}\n\n"
        "-- \n"
        "This is an automated alarm from alexandria's weekly press "
        "(pipeline/weekly.py). It means no issue was written and nothing was "
        "sent to subscribers.\n\n"
        "What to check, in order:\n"
        "  1. modal app logs alexandria-weekly\n"
        "  2. https://console.groq.com/docs/models, against "
        "pipeline/weekly.py FALLBACK_MODELS\n"
        "  3. python3 pipeline/budget.py, which prints the arithmetic for "
        "every fallback\n"
    )
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = f"[alexandria] {subject}"
        msg["From"] = f"alexandria press <{addr}>"
        msg["To"] = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(addr, pw)
            smtp.sendmail(addr, [to], msg.as_string())
    except Exception as exc:
        return f"NOT NOTIFIED: the alarm email itself failed ({exc})"
    return f"owner notified at {to}: {subject}"


@app.function(
    secrets=[modal.Secret.from_name("groq")],
    timeout=300,
)
def preflight() -> str:
    """Can the press print at all? Run this before every deploy.

    `modal deploy` does not run a local entrypoint, so without this function
    nothing checks the provider between one Monday and the next. It needs the
    real key, which only exists inside Modal, which is why it is a deployed
    function rather than a local script.

    Loud on purpose: it raises, so a failed preflight stops the chair's deploy
    command at the `&&`. No email here, because a human is watching a deploy;
    the emailing path is the scheduled run, where nobody is.
    """
    guard = budget()
    available = check_availability()
    prompt = open("/root/prompts/digest.md").read()
    payload_json = guard.encode(guard.worst_case_payload())
    choice = guard.choose_model(FALLBACK_MODELS, available, prompt,
                                payload_json, MAX_COMPLETION_TOKENS)
    print("preflight, worst-case payload:")
    print(choice.summary())
    if not choice.model:
        raise PressCannotPrint(
            "preflight: no model in the fallback list can write this issue.\n"
            + choice.summary()
        )
    return f"preflight ok: {choice.model} would write the issue"


@app.function(
    # Monday 09:00 UTC. Moved from 15:00 on 2026-09-24 for incident 24's part
    # (d): the press shares one Groq key, and therefore one TPM budget, with
    # four daily crons. Groq's own words, read from the live rate-limit docs
    # this day: "Rate limits apply at the organization level, not individual
    # users." A second API key on the same account is therefore worth nothing,
    # which rules out the dedicated-key option as stated; the press has to run
    # when the crons are idle instead.
    #
    # The daily crons occupy 11:00 (ingest), 11:30 (distill), 12:00 (triage)
    # and 14:00 (interpret), each with a one-hour timeout, so the contested
    # band is 11:00 to 15:00 and the old 15:00 slot sat directly against
    # interpret's worst case. 09:00 is two clear hours ahead of the earliest
    # cron, and it is the right editorial slot anyway: the issue covers the
    # week that ended Sunday, so Monday's own ingest is not in it, and 09:00
    # UTC is 5am in New York, which puts the issue in a reader's inbox before
    # the working day rather than in the middle of it.
    #
    # Runtime change under docs/agents/runtime-changes.md. Its smoke test is
    # the deploy command in this module's docstring: preflight, then one manual
    # `modal run`, then the deploy that installs this schedule. The next cron
    # is not the first execution of this machinery.
    schedule=modal.Cron("0 9 * * 1"),
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq"),
             modal.Secret.from_name("Gmail"), modal.Secret.from_name("gmail_pass")],
    timeout=1800,
)
def weekly() -> str:
    import os

    import psycopg

    # label with the ISO week that just ended (yesterday = Sunday)
    y = date.today() - timedelta(days=1)
    week = f"{y.isocalendar().year}-W{y.isocalendar().week:02d}"
    monday = y - timedelta(days=6)
    if monday.month == y.month:
        dates = f"{monday.strftime('%B')} {monday.day}–{y.day}, {y.year}"
    else:
        dates = (f"{monday.strftime('%B')} {monday.day} – "
                 f"{y.strftime('%B')} {y.day}, {y.year}")
    prompt = open("/root/prompts/digest.md").read()
    sha = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    try:
        # Run-start availability check, before a single token is spent and
        # before the citation pass burns twenty minutes writing nothing.
        # Incident 24: the budget guard proved the request fit a model that no
        # longer existed.
        available = check_availability()

        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            try:
                check_citations(conn)
            except Exception as exc:
                print(f"citation check failed ({exc}); digest proceeds without "
                      "fresh citations")
            payload = gather(conn)
            payload["week"] = week
            payload["dates"] = dates
            print(f"{week}: {payload['stats']} | "
                  f"new_claims={len(payload['new_claims'])} "
                  f"deprecated={len(payload['deprecated'])}")
            body, model = write_digest(payload, prompt, available)
            body = add_masthead(body)
            conn.execute(
                """
                insert into digests (week, body, model, prompt_sha)
                values (%s, %s, %s, %s)
                on conflict (week) do update
                    set body = excluded.body, model = excluded.model,
                        prompt_sha = excluded.prompt_sha, created_at = now()
                """,
                (week, body, model, sha),
            )
            conn.commit()
            try:
                print(send_newsletter(conn, week, body))
            except Exception as exc:
                # the digests table is the record of record, so a send failure
                # must never fail the run. It must still be loud: an issue
                # written and never delivered is the same silence to a reader
                # as an issue never written.
                print(f"newsletter send failed ({exc}); digest is safe in the "
                      "database")
                print(notify_owner(
                    f"{week} was written but NOT sent",
                    f"The {week} issue is in the digests table and on the site, "
                    f"but the email send failed:\n\n{exc}\n\n"
                    f"It was written by {model}, so nothing needs rewriting. "
                    "The send is the part that needs retrying."))
    except Exception as exc:
        # Every path out of this run that ends without an issue comes through
        # here. This is incident 24's standing fix: the discovery must never
        # again be the owner's inbox being empty.
        print(f"PRESS FAILED: {exc}")
        print(notify_owner(
            f"{week} could not be printed",
            f"The weekly press failed and no issue was written for {week}.\n\n"
            f"{type(exc).__name__}: {exc}"))
        raise
    return body


@app.local_entrypoint()
def main():
    # Two checks before anything is spent, in this order, because they fail for
    # different reasons and the operator needs to know which one bit.
    #
    # 1. The budget: does the request fit? Incident 22. Runs locally, needs no
    #    key, and is the same check CI runs
    #    (.github/workflows-pending/checks.yml).
    # 2. Availability: does the model exist? Incident 24. Needs the real key,
    #    so it runs inside Modal via preflight.
    if budget().main() != 0:
        raise SystemExit(
            "budget check failed; the request would not fit any model in the "
            "fallback list and no issue would be written. Nothing was run."
        )
    print(preflight.remote())
    body = weekly.remote()
    print("\n" + body)
