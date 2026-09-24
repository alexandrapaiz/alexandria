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

Needs secrets: `neon`, `moonshot`, `groq`, and the Gmail secrets
(GMAIL_ADDRESS + GMAIL_APP_PASSWORD) once the newsletter is live; until then
the run succeeds and only skips the email.

**The one command the chair runs before the first deploy** (ADR-32). The press
writes on Moonshot's Kimi now, and the key lives in a Modal secret named
`moonshot`. Only the owner holds the key. Paste it at the prompt rather than
putting it on the command line, so it never lands in a shell history or a
transcript:

    modal secret create moonshot MOONSHOT_API_KEY=<paste>

No agent creates this, no agent reads it, and the value appears nowhere in this
repository. The name does, and the name is all the code needs.

**Then the deploy**, unchanged in shape and with one more thing checked:

    python3 pipeline/budget.py                    # does the request fit?
    python3 tools/rehearse_email.py               # does the email still render?
    modal run pipeline/weekly.py::preflight        # does the model still exist?
    modal run pipeline/weekly.py                  # one-off manual run (both, then print)
    modal deploy pipeline/weekly.py               # install the Monday schedule

As one line, which is what the chair runs after a merge that touches this file
or prompts/digest.md:

    python3 pipeline/budget.py \
      && python3 tools/rehearse_email.py --quiet \
      && modal run pipeline/weekly.py::preflight \
      && modal deploy pipeline/weekly.py

No guard in that chain is optional ceremony, and each checks a different
thing.

**Does the email still render?** The owner's ruling of 2026-09-24: the
emails had no UI and only the site did. The designed template had been in
the repo since 2026-09-19 and the press had never opened it, because the
only code path that rendered an email ran inside a container, at the
moment of sending, to real subscribers. Nobody could look at one without
mailing it. `tools/rehearse_email.py` fills the template through the
press's own `build_messages()` and prints the result, sends nothing, costs
nothing, and exits non-zero if any slot is left unfilled. It is the email
half of docs/agents/press-rehearsal.md. The model-call half, `rehearse()`,
is still unbuilt and still the third gate that document specifies.

**Does the request fit?** Incident 22: an editorial merge grew the generator
prompt past the model's per-request token ceiling, the provider answered 413,
and no issue was written. `pipeline/budget.py` owns that arithmetic and runs in
CI on every change to a generator prompt or this pipeline, before deploy, and
again inside the container before the writing call.

**Does the model still exist?** Incident 24: Groq withdrew `groq/compound`, the
press answered 404 for three days, and the discovery was the owner noticing that
Monday's issue never arrived. The budget guard had been perfectly happy: it
checks that a request fits, not that there is anything to send it to. So
`preflight` asks `GET /models` before the deploy, `check_availability` asks
again at the start of every run, `FALLBACK_MODELS` gives the run somewhere to
go when the answer is no, and `notify_owner` mails the owner the moment the
press cannot print. That last one is the important one. A press that fails
silently has no failure mode the org can respond to.

Both questions are now asked of both providers, because the fallback list
crosses providers on purpose and a check that only covers one of them is a
check with a hole in it exactly where the press lives.
"""

import hashlib
import pathlib
import re
import time
from datetime import date, timedelta

import modal

# ADR-32 (2026-09-24): the press's single writing call runs on Moonshot's Kimi.
# Groq stays as the corpus's brain and as the press's last resort.
#
# Neither URL is written out here. `pipeline/budget.py` owns the provider table
# (base URL, key environment variable, Modal secret name, docs) so that one
# file answers "where does this model live and what will it accept", and the
# guard cannot be checking a different endpoint from the one the press calls.

# Incident 24, 2026-09-23: Groq withdrew `groq/compound` and the press answered
# 404 for three days without telling anyone. The press had been moved to it on
# 2026-09-19 (PR #51) for one reason, its 70,000 TPM, and a capacity number
# turned out to be the worst possible reason to pick a model: compound was an
# agentic *preview* system, and previews are withdrawn without the deprecation
# notice production models get.
#
# Then the whole free tier turned out to be too small: every remaining Groq
# free model caps a single request at 8,000 tokens and the generator prompt
# alone is 9,865. ADR-32 is the owner's answer. The press writes on Kimi, which
# she funded, and the list below is what happens when Kimi is not there.
#
# 1. **`kimi-k2.6`, on Moonshot, is the press.** 256K of context against a
#    ~36,000-token worst case, a prepaid account rather than a free tier, and
#    open weights, which is what makes the destination in ADR-32 reachable:
#    the same class of model served by alexandria itself, so no provider can
#    withdraw the press's model a third time.
#
#    The id is `kimi-k2.6` and not `kimi-k2`. The bare series was discontinued
#    on 2026-05-25, so the obvious id is the one that 404s. That is incident 24
#    exactly, and the only reason it did not happen again here is that
#    `check_availability` asks the provider before the run trusts the name.
#
# 2. **Then Groq, in the order incident 24 argued for**: production before
#    preview, and a second vendor at rank two so a family withdrawal cannot
#    take the whole list. Be honest about what these three are worth today:
#    at 8,000 TPM they cannot print the issue at the current prompt size, and
#    the budget guard prints that arithmetic on every run. They are here for
#    the day the prompt gets shorter or a ceiling moves, and if they ever do
#    write, they will write a short issue. A last resort that prints something
#    small beats a last resort that does not exist.
#
# Every entry is verified by pipeline/budget.py, which reads this list out of
# this file rather than keeping a copy, and refuses the deploy if any entry has
# no published limits or has been withdrawn.
FALLBACK_MODELS = [
    "kimi-k2.6",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]

# The default. `write_digest` walks the list from here and may end up further
# down it; whichever model actually wrote the issue is what lands in the
# `digests.model` column, never this constant.
MODEL = FALLBACK_MODELS[0]

# Retries per model before the press gives up on it and tries the next one.
# 429 is the case this exists for: a per-model rate limit means moving down the
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
    # The designed email (site/emails/digest.html) and the renderer that
    # fills it. Owner's ruling 2026-09-24: the emails get the UI, not just
    # the site. Both are data-and-stdlib, so the press gains no dependency.
    .add_local_file("site/emails/digest.html", "/root/emails/digest.html")
    .add_local_file("pipeline/email_render.py", "/root/email_render.py")
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


class MissingKey(RuntimeError):
    """A provider's API key is not in this environment.

    Its own class rather than a bare KeyError, so the fallback walk can treat
    "we cannot reach this provider" the same way it treats a withdrawn model:
    record it, say which Modal secret is missing, and try the next one.
    """


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
MAX_COMPLETION_TOKENS = 24000  # kimi-k2.6 reasons before it writes; 6000 was consumed by hidden thinking (finish_reason length, empty content, 2026-09-24)


def log_limits(resp, model: str) -> None:
    """The provider's own account of the budget, which outranks what we assume.

    Groq sends these headers on every response. Moonshot does not always, and
    silence is not a problem: the header is a cross-check on budget.MODELS, not
    an input to any decision.
    """
    limit = resp.headers.get("x-ratelimit-limit-tokens")
    remaining = resp.headers.get("x-ratelimit-remaining-tokens")
    if limit:
        print(f"provider says: limit {limit} tokens, {remaining} remaining. If "
              f"that disagrees with budget.MODELS[{model!r}], the header is "
              "right and the table is the thing to fix.")


def api_key_for(provider: str) -> str:
    """The key for `provider`, or a loud failure naming the Modal secret.

    ADR-32 gave the press a funded account, and the chair creates the secret
    from the owner's key. This seat never sees the value and must never print
    it; what it can do, when the value is not there, is say exactly which
    secret is missing and what command creates it. A press that dies on a
    KeyError for `MOONSHOT_API_KEY` tells the owner nothing.
    """
    import os

    spec = budget().PROVIDERS[provider]
    key = os.environ.get(spec["key_env"], "").strip()
    if not key:
        raise MissingKey(
            f"{spec['key_env']} is not in this environment, so the press "
            f"cannot reach {provider}. It comes from the Modal secret named "
            f"`{spec['secret']}`, which the chair creates with:\n"
            f"    modal secret create {spec['secret']} {spec['key_env']}=<paste>\n"
            f"Then redeploy: modal deploy pipeline/weekly.py"
        )
    return key


def check_availability() -> set[str]:
    """Which models the press's providers actually have, right now, for our keys.

    Incident 24's standing fix. The budget guard checks that the request fits;
    this checks that there is something to send it to. It costs no tokens
    against any ceiling, so it runs at deploy and again at the start of every
    run, and it raises loudly rather than guessing.

    One provider being unreachable is a note, not the end of the run, because
    the fallback list crosses providers on purpose. What ends the run is no
    usable model anywhere, and the missing primary key, which is a
    configuration fact the owner can fix in one command.
    """
    import os

    guard = budget()
    primary = guard.PRIMARY_PROVIDER
    # fail here rather than three functions later, and name the secret
    try:
        api_key_for(primary)
    except MissingKey as exc:
        raise PressCannotPrint(str(exc)) from exc

    available, notes = guard.available_everywhere(FALLBACK_MODELS, os.environ)
    for note in notes:
        print(f"availability: {note}")
    usable = [m for m in FALLBACK_MODELS if m in available]
    for name in FALLBACK_MODELS:
        if name in available:
            continue
        provider = guard.MODELS.get(name, {}).get("provider", "?")
        print(f"AVAILABILITY: {name} is in FALLBACK_MODELS but {provider} does "
              "not list it. A request to it would 404, as it did in incident 24.")
    print(f"fallbacks present: {usable or 'NONE'}")
    if not usable:
        docs = ", ".join(
            guard.PROVIDERS[p]["docs"] for p in guard.providers_for(FALLBACK_MODELS))
        raise PressCannotPrint(
            "no provider lists any of the press's fallback models "
            f"({', '.join(FALLBACK_MODELS)}). The press cannot print until "
            "pipeline/weekly.py FALLBACK_MODELS and pipeline/budget.py MODELS "
            f"are updated from {docs}."
        )
    return available


def call_model(model: str, prompt: str, user: str) -> str:
    """One model, with backoff on 429. Raises so the caller can move down the list.

    The request body is the OpenAI-compatible minimum and nothing else. Both
    providers speak that dialect, so there is one code path and no provider
    branch to get wrong. Two deliberate absences:

    * **No `compound_custom`.** It was a Groq-only block for the agentic
      compound system, and compound is gone. ADR-6 holds regardless: the press
      is a workflow, one prompt in, one issue out, no tools.
    * **No `temperature` on Kimi.** Moonshot documents temperature, top_p, n
      and both penalties as fixed values on k2.6, so sending 0.3 would be a
      parameter the model overrides. Sending settings that do nothing is how a
      reader comes to believe a knob exists.
    """
    import httpx

    guard = budget()
    provider = guard.provider_of(model)
    url = guard.endpoint(provider, "/chat/completions")
    key = api_key_for(provider)

    body = {
        "model": model,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user},
        ],
    }
    if provider != "moonshot":
        body["temperature"] = 0.3
    else:
        # kimi-k2.6 and kimi-k3 are thinking models. On the 10K-token
        # editorial instruction the hidden reasoning consumed a 24,000-token
        # output reservation twice (finish_reason 'length', no content,
        # 2026-09-24). The instruction is the thinking, so it is off here;
        # verified by probe: thinking disabled returns full content with zero
        # reasoning tokens on both models.
        body["thinking"] = {"type": "disabled"}

    for attempt in range(RETRIES_PER_MODEL):
        resp = httpx.post(
            url,
            headers={"Authorization": f"Bearer {key}"},
            json=body,
            timeout=1500,  # kimi-k2.6 reasons for minutes before writing; 300s timed out on 2026-09-24
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
            # the status and throws the body away. The body is where the
            # provider states the actual limit and the actual request size.
            print(f"{provider} {resp.status_code} on {model}: {resp.text[:1000]}")
            # 400 on a model that exists is usually an unsupported parameter,
            # which the next model may well accept
            raise ModelGone(f"{resp.status_code}: {resp.text[:400]}")

        choice = resp.json()["choices"][0]
        message = choice["message"]
        fired = message.get("executed_tools") or []
        if fired:
            # No model in FALLBACK_MODELS is agentic today, and ADR-6 says the
            # press never gets tools. If one ever fires anyway, the issue may
            # contain something that did not come from our corpus, and that is
            # a fact about the issue, not a warning about the call.
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
            provider = guard.MODELS.get(model, {}).get("provider", "?")
            tried.append(f"{model}: not listed by {provider} for this key; "
                         "skipped without a request (incident 24's 404)")
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
        except (ModelGone, RateLimited, MissingKey) as exc:
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


def email_render():
    """pipeline/email_render.py, wherever this is running from.

    Same two-path trick as budget(): Modal drops it at /root/email_render.py
    and a local run finds it beside this file. The template it fills travels
    the same way, bundled at /root/emails/digest.html.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import email_render as module

    return module


def legacy_html(body: str) -> str:
    """The pre-2026-09-24 email: markdown in an inline Georgia div.

    Kept only as the fallback under a rendering failure. An issue that reaches
    its readers plain is a bad day; an issue that reaches nobody because the
    template moved a comment marker is an outage.
    """
    try:
        import markdown as md
    except ImportError:
        # The image pins markdown==3.7, so this is not the production path.
        # It exists because this function is the last thing standing between
        # a rendering failure and an issue nobody receives, and a last resort
        # that can itself raise is not one.
        import html as _html

        return (
            "<div style='max-width:640px;margin:0 auto;font-family:Georgia,serif;"
            "font-size:16px;line-height:1.6;color:#222'>"
            f"<pre style='white-space:pre-wrap;font-family:Georgia,serif'>"
            f"{_html.escape(body)}</pre></div>"
        )

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
    return (
        "<div style='max-width:640px;margin:0 auto;font-family:Georgia,serif;"
        "font-size:16px;line-height:1.6;color:#222'>"
        f"{html_body}"
        "<hr><p style='font-size:12px;color:#888'>You're receiving this as a "
        "friend of alexandria. Reply to this email to unsubscribe.</p></div>"
    )


def build_messages(key: str, body: str, rows, addr: str) -> list[tuple[str, str, str, str]]:
    """(email, subject, plain_text, html) per recipient, and nothing sent.

    Split out from the SMTP loop so a rehearsal can print exactly what the
    press would send without opening a connection to Gmail. That is the whole
    reason this function exists: docs/agents/press-rehearsal.md's rule is that
    a rehearsal renders the real thing, and a renderer only a live send can
    reach is a renderer nobody checks before it goes out.
    """
    render = email_render()
    subject = render.subject_for(body)
    # No unsubscribe endpoint exists yet, and the slot contract
    # (site/emails/README.md) accepts a mailto until one does.
    unsubscribe = f"mailto:{addr}?subject=Unsubscribe"

    try:
        issue = render.parse_issue(body)
        messages = []
        for email, _name in rows:
            meta = render.build_meta(key, issue, email, unsubscribe)
            messages.append((email, subject, body, render.render(issue, meta)))
        return messages
    except Exception as exc:
        print(f"designed template failed to render ({exc}); falling back to "
              "the plain email. The issue still goes out.")
        fallback = legacy_html(body)
        return [(email, subject, body, fallback) for email, _name in rows]


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

    # The designed email, one render per recipient because the footer names
    # the address it was sent to. Subject stays the issue's own editorial
    # title, and the plain-text part stays the markdown body: a multipart
    # alternative without a real text part is what filters read as spam.
    messages = build_messages(week, body, rows, addr)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(addr, pw)
        for email, subject, text, html in messages:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"alexandria <{addr}>"
            msg["To"] = email
            msg.attach(MIMEText(text, "plain"))
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
        "  2. https://platform.kimi.ai/docs/models and "
        "https://console.groq.com/docs/models, against "
        "pipeline/weekly.py FALLBACK_MODELS\n"
        "  3. python3 pipeline/budget.py, which prints the arithmetic for "
        "every fallback\n"
    )
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = f"alexandria press <{addr}>"
        msg["To"] = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(addr, pw)
            smtp.sendmail(addr, [to], msg.as_string())
    except Exception as exc:
        return f"NOT NOTIFIED: the alarm email itself failed ({exc})"
    return f"owner notified at {to}: {subject}"


@app.function(
    # Both providers, because preflight's whole job is to ask each of them
    # whether the models named in FALLBACK_MODELS still exist. Values are never
    # read by this seat; only the names appear in the repository.
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
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
    if choice.model:
        print(f"  cost at list price, worst case: ${choice.report.cost:.4f} "
              "an issue")
    if not choice.model:
        raise PressCannotPrint(
            "preflight: no model in the fallback list can write this issue.\n"
            + choice.summary()
        )
    return f"preflight ok: {choice.model} would write the issue"


@app.function(
    # Monday 09:00 UTC. Moved from 15:00 on 2026-09-24, and it stays at 09:00
    # now that the press writes on Moonshot, for a different and better reason.
    #
    # The original reason was contention: the press shared one Groq key, and
    # therefore one 8,000-token-per-minute budget, with four daily crons, and
    # Groq applies rate limits "at the organization level, not individual
    # users". ADR-32 ends that argument. The press has its own provider and its
    # own prepaid account, so it no longer competes with triage, distill or
    # interpret for anything. The Groq fallbacks still would, which is one more
    # reason for the press to keep out of the 11:00-to-15:00 band the daily
    # crons occupy (11:00 ingest, 11:30 distill, 12:00 triage, 14:00 interpret,
    # each with a one-hour timeout).
    #
    # The reason to keep 09:00 is editorial. The issue covers the week that
    # ended Sunday, so Monday's own ingest is not in it, and 09:00 UTC is 5am
    # in New York, which puts the issue in a reader's inbox before the working
    # day rather than in the middle of it.
    #
    # Runtime change under docs/agents/runtime-changes.md. Its smoke test is
    # the deploy command in this module's docstring: preflight, then one manual
    # `modal run`, then the deploy that installs this schedule. The next cron
    # is not the first execution of this machinery.
    schedule=modal.Cron("0 9 * * 1"),
    secrets=[modal.Secret.from_name("neon"),
             # ADR-32: the press writes on Kimi. `moonshot` holds
             # MOONSHOT_API_KEY and the chair creates it from the owner's key.
             modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq"),
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
        # The read connection closes here, on purpose. Kimi reasons for
        # minutes before it writes, and Neon terminates a connection left
        # idle inside a transaction (IdleInTransactionSessionTimeout,
        # 2026-09-24: the issue was written and could not be saved). The
        # model call runs with no connection open; a fresh one saves and sends.
        body, model = write_digest(payload, prompt, available)
        body = add_masthead(body)
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
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
                    "This week's issue was written but not sent",
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
            "The press could not print this week's issue",
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
