"""Distill: extract claims from triage-routed papers into silver, with embeddings.

Production model: gpt-oss-120b on Groq — chosen by blind human bake-off over
Qwen3.8-27B (4-1-3; see docs/evals/2026-09-07-distill-bakeoff.json). Claims are
embedded in-process with Qwen3-Embedding-0.6B (pinned open weights; the embedding
model must never change silently — all vectors must come from one model).

Scheduled at 11:30 UTC, BEFORE triage's 12:00 run: both share Groq's daily token
budget, and distill is the higher-value-per-token job, so it spends first and
processes yesterday's triage output.

    python3 pipeline/budget.py                       # gate 1: does it fit
    modal run pipeline/distill.py::preflight         # gate 2: does the model exist
    modal run pipeline/distill.py::rehearse          # gate 3: one real call, no write
    modal deploy pipeline/distill.py                 # then, and only then, deploy

    modal run pipeline/distill.py --max-papers 5     # manual production run
    modal run pipeline/distill.py::bake_off          # rerun the model bake-off

## What changed on 2026-09-26

Two things, both about the claim being findable after it is written.

The topic list in `prompts/distill.md` has always called itself closed and
nothing enforced it, so tags went into `claims.topics` exactly as the model
returned them: 3.9% off the list, 18 claims tagged with a non-breaking-hyphen
twin of a real topic and invisible to every query the product runs, 22 tags
invented outright. `pipeline/topics.py` is now the only place that decides what
a topic is, it is enforced here at the one place claims are written, and the
off-list rate is printed every run. `reasoning` joined that list by the owner's
directive of 2026-09-26, and a brand new tag whose adoption cannot be counted
is a tag nobody can show is working.

Every claim now carries `prompt_sha`, the 12 hex the press and triage have
always recorded. Before this, the deploy state of this prompt was knowable only
by inference from the shape of the output, which is how the interpret prompt
went seven days stale unnoticed while its output reached readers
(INC-2026-09-26-interpret-stale-third-sighting).

## What changed on 2026-09-27

The job reads the paper now, and it did not before.

`FULLTEXT_CHARS` was 24,000 and a 24,000-character request never fitted Groq's
free tier — not by 109 tokens, which is what this file said yesterday, but by
about 1,900. The 109 came from sizing a paper with a prose filler that runs
6.17 chars/token against a real paper's 3.35, and it was wrong in five places
at once (INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper). So every
full-text call was refused, the retry below fell back to `abstract[:6000]`, and
the run reported success. "164 papers read in full out of 8,956" is that
sentence, counted.

`FULLTEXT_CHARS` is 12,000 now, which every one of 14 real papers fits inside
with room, and the job declares `MAX_COMPLETION_TOKENS` instead of leaving the
reservation to be assumed by whoever is doing the arithmetic. The receipt is
docs/evals/2026-09-27-fulltext-token-density.json and
`python3 tools/fulltext_density.py` reproduces it against the live papers.

Twelve thousand characters of a paper's body is not a paper. It is twice what
the job was actually reading, it is the part with the method in it, and
`papers.fulltext_chars` has always recorded the true number per paper. Reading
a whole paper needs a provider with a larger per-request window, which costs
money and is the owner's call, priced in docs/ideas.md.
"""

import hashlib
import json
import pathlib
import time

import modal

PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "openai/gpt-oss-120b",
        "key_env": "GROQ_API_KEY",
        "pause": 3,
    },
    # gemini was evaluated and dropped: 7/8 calls failed with 429 even under
    # exponential backoff on the free tier — disqualified on reliability
    "qwen": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "qwen/qwen3.8-27b",
        "key_env": "GROQ_API_KEY",
        "pause": 3,
    },
}

PRODUCTION_PROVIDER = "groq"
EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# Full-text distillation: skills are the product, and abstracts don't contain
# procedures — so every arXiv paper in the run gets its HTML full text, not
# the abstract. Triage routes ~3-6 papers/day to distill, so this fits the
# Groq budget; the cap is a safety valve for backlog days (deep_read papers
# sort first in the queue, so they always get full text).
FULLTEXT_MAX_PER_RUN = 15

# 24000 until 2026-09-27, which never fitted and never could. Measured against
# 14 real papers (receipt: docs/evals/2026-09-27-fulltext-token-density.json),
# 24,000 characters of cleaned arXiv HTML is 5,600 to 6,600 tokens, so the
# request came to between 8,600 and 9,600 against 6,800 usable. Groq refused it
# every time, the code below retried with abstract[:6000], and the run reported
# success. That is the whole of "164 papers read in full out of 8,956".
#
# 12000 is what is left for the payload after the prompt (990), the declared
# reservation (2,000) and the envelope (32) come out of 6,800, at the density of
# the densest paper measured: 3,582 tokens, 196 to spare. All 14 papers fit at
# this size and one of them does not fit at 13,000, which is how the number was
# chosen — by sending it, not by dividing. `python3 pipeline/budget.py`
# recomputes it on every change to the prompt and fails CI if it stops fitting,
# so this number does not need to be remembered, only lowered when the guard
# says so.
#
# It is not "in full" and this file will not pretend otherwise. It is 12,000
# characters of the paper's own body — abstract, introduction and usually the
# method — against 6,000 characters of abstract, which is what the job actually
# read before today. `papers.fulltext_chars` records exactly how much, per paper,
# and the digest's `papers_read_in_full` counts rows where that column is set.
# On a 90,000-character paper this reads the first 13% of it. Saying so is the
# owner's and the writer's call, not this file's, and it is flagged in the pull
# request that changed this line.
FULLTEXT_CHARS = 12000

# The job sent no reservation until 2026-09-27, so the provider was free to
# spend the rest of the window on output and the budget guard had to assume a
# number. 2,000 is that assumption made explicit rather than a new, smaller
# guess: 1 to 5 claims with evidence and a numbered procedure measures around
# 1,500 tokens, and an under-sized reservation truncates the JSON mid-object,
# which surfaces as a json.JSONDecodeError and loses the whole paper. Buying
# 600 more characters of paper with that risk is a bad trade. Lower it only
# against a measurement from `rehearse`, which prints the real usage block.
MAX_COMPLETION_TOKENS = 2000

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1", "sentence-transformers")
    .add_local_file("prompts/distill.md", "/root/prompts/distill.md")
    .add_local_file("pipeline/evidence.py", "/root/evidence.py")
    # The taxonomy travels with the job, so the list the tests check is the list
    # the insert enforces.
    .add_local_file("pipeline/topics.py", "/root/topics.py")
    # The reader and the queue parser travel too, so the job reads a paper the
    # same way the seats do (tools/read_paper.py) and drains the same file the
    # skill seat writes (ADR-35).
    .add_local_file("tools/read_paper.py", "/root/read_paper.py")
    .add_local_file("pipeline/reading_queue.py", "/root/reading_queue.py")
    # The queue's CONTENT is baked at deploy time, which is the one thing to
    # know about it: a line appended today reaches the cron on the next
    # `modal deploy`. A manual `modal run` sends the working copy instead, so
    # an urgent request is one command rather than a deploy.
    .add_local_file("docs/research/reading-queue.md", "/root/reading-queue.md")
)

app = modal.App("alexandria-distill", image=image)

hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


def evidence():
    """pipeline/evidence.py, wherever this is running from.

    Modal drops it at /root/evidence.py; a local `python3 pipeline/distill.py`
    import finds it beside this file. Same trick weekly.py uses for the token
    budget, for the same reason: the rules the tests check are the rules the
    run applies.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import evidence as module

    return module


def topics():
    """pipeline/topics.py, wherever this is running from. The same two-path trick.

    The taxonomy has to be one object shared by the insert and the tests. A
    second copy of the list is how `prompts/distill.md` came to offer tags the
    database never accepted.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import topics as module

    return module


def _sibling(name: str):
    """Import a module Modal dropped at /root, or that sits beside this file.

    The same two-path trick `evidence()` and `topics()` use, once, for the two
    modules added since. `tools/read_paper.py` lands at /root/read_paper.py in
    the image and at ../tools/read_paper.py in a checkout.
    """
    import importlib
    import sys

    here = pathlib.Path(__file__).resolve().parent
    for path in ("/root", str(here), str(here.parent / "tools")):
        if path not in sys.path:
            sys.path.insert(0, path)
    return importlib.import_module(name)


def read_paper():
    """tools/read_paper.py — the one reader, shared by this job and the seats."""
    return _sibling("read_paper")


def reading_queue():
    """pipeline/reading_queue.py — the parser for docs/research/reading-queue.md."""
    return _sibling("reading_queue")


def load_prompt() -> tuple[str, str]:
    """The distill prompt and the first 12 hex of its sha256.

    Written onto every claim as `claims.prompt_sha`, the way triage writes it
    onto every decision and the press writes it onto every issue. Until this
    landed, the deploy state of `prompts/distill.md` was unverifiable except by
    inference from the shape of the output: the research seat's brief of
    2026-09-26 found the interpret prompt seven days stale that way, after the
    stale prompt's output had already reached readers.
    """
    text = open("/root/prompts/distill.md").read()
    return text, hashlib.sha256(text.encode()).hexdigest()[:12]


def has_column(conn, table: str, column: str) -> bool:
    """Whether db/schema.sql has been applied since `column` landed.

    The column ships in the same PR as the code that writes it, and the schema
    is applied by hand (`modal run pipeline/db_setup.py`). Asking the database
    rather than assuming means a deploy that lands before the schema run
    distills normally instead of failing every insert.
    """
    return conn.execute(
        """
        select 1 from information_schema.columns
        where table_name = %s and column_name = %s
        """,
        (table, column),
    ).fetchone() is not None


def has_evidence_grade(conn) -> bool:
    """Whether db/schema.sql has been applied since evidence_grade landed.

    The column ships in the same PR as the code that writes it, and the schema
    is applied by hand (`modal run pipeline/db_setup.py`). Asking the database
    rather than assuming means a deploy that lands before the schema run
    distills normally instead of failing every insert.
    """
    return conn.execute(
        """
        select 1 from information_schema.columns
        where table_name = 'claims' and column_name = 'evidence_grade'
        """
    ).fetchone() is not None


def fetch_fulltext(paper_id: str) -> str | None:
    """arXiv's HTML full text, cut to FULLTEXT_CHARS, or None for the abstract.

    The fetching and the cleaning live in `tools/read_paper.py` now, so that
    the job and the seats read a paper the same way and there is one place to
    fix when arXiv changes. What stays here is the only part that is distill's
    own: the cut to FULLTEXT_CHARS, which is a provider limit and not a fact
    about the paper. A seat running `python3 tools/read_paper.py <id>` gets the
    whole thing.
    """
    return read_paper().fetch_fulltext(paper_id, max_chars=FULLTEXT_CHARS)


def extract_claims(provider: str, title: str, abstract: str) -> list[dict]:
    import os

    import httpx

    p = PROVIDERS[provider]
    prompt, _ = load_prompt()
    for attempt in range(4):
        resp = httpx.post(
            p["url"],
            headers={"Authorization": f"Bearer {os.environ[p['key_env']].strip()}"},
            json={
                "model": p["model"],
                "temperature": 0.2,
                "max_completion_tokens": MAX_COMPLETION_TOKENS,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"title: {title}\n\ncontent: {abstract}"},
                ],
            },
            timeout=180,
        )
        if resp.status_code == 429 and attempt < 3:
            wait = float(resp.headers.get("retry-after") or 20 * (attempt + 1))
            print(f"  {provider} rate limited; backing off {wait:.0f}s")
            time.sleep(min(wait, 120))
            continue
        resp.raise_for_status()
        out = json.loads(resp.json()["choices"][0]["message"]["content"])
        return out
    raise RuntimeError(f"{provider}: exhausted retries")


# The payload is a fixed sample carried in this file, the way triage's rehearsal
# batch is, so the gate needs no database. What must be real is its SIZE IN
# TOKENS, because the question this gate answers is whether a full paper fits.
#
# "Length" is not size. Until 2026-09-27 this was prose alone, which runs 4.24
# chars/token, so at FULLTEXT_CHARS the rehearsal sent 750 fewer tokens than the
# densest real paper and would have passed a request that Groq refuses. That is
# the same mistake as the budget guard's prose filler
# (INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper), made independently, in
# the gate whose whole job is to catch it.
#
# A real paper is prose with tables in it, and the tables are what make it dense.
# Five parts prose to one part table lands at 3.30 chars/token against the 3.35
# of arxiv:2407.21783, the densest of the 14 papers in
# docs/evals/2026-09-27-fulltext-token-density.json. Slightly worse than the
# worst real paper is the correct place for a gate to sit.
# `tests/test_distill_fulltext_budget.py` holds that, so the ratio cannot drift
# back toward prose.
REHEARSAL_PROSE = (
    "We introduce a two-stage procedure for aligning a reward model to human "
    "preference pairs. In the first stage the policy is trained with supervised "
    "fine-tuning on 12,400 demonstrations. In the second stage we distil the "
    "reward model into the policy with a KL penalty of 0.02, which we ablate in "
    "Table 4. On the held-out split the aligned policy reaches 71.3% pairwise "
    "win rate against the SFT baseline, measured by three annotators with "
    "Krippendorff alpha 0.81. Training used 64 A100-hours. "
)

REHEARSAL_TABLE = (
    "Table 4: ablation over KL penalty. beta 0.005 0.01 0.02 0.05 0.10 0.20 | "
    "MMLU 5-shot 66.1 68.4 71.3 70.9 69.2 64.8 | GSM8K 8-shot maj@1 74.2 78.0 "
    "82.4 81.7 79.3 71.5 | HumanEval pass@1 55.4 59.8 64.0 63.1 60.2 52.7 | "
    "MATH 4-shot 28.3 31.6 34.9 34.1 32.0 26.4 | ARC-C 25-shot 81.2 83.5 85.7 "
    "85.0 83.8 79.1 | HellaSwag 10-shot 82.0 83.9 85.2 84.8 83.6 80.3 | "
    "TruthfulQA mc2 44.7 47.2 49.8 49.1 47.5 43.0 | avg 61.8 64.6 67.6 66.9 "
    "65.1 59.7 | Delta vs. SFT +0.0 +2.8 +5.8 +5.1 +3.3 -2.1 | n=3 seeds, "
    "sigma<=0.4. "
)

REHEARSAL_SAMPLE = REHEARSAL_PROSE * 5 + REHEARSAL_TABLE

REHEARSAL_TITLE = "A two-stage procedure for distilling reward models into policies"


@app.function(
    secrets=[modal.Secret.from_name("groq")],
    timeout=300,
)
def preflight() -> str:
    """Gate 2: do the models exist? Run before every deploy.

        modal run pipeline/distill.py::preflight

    `modal deploy` runs no entrypoint, so without this nothing asks the provider
    between one day's cron and the next. Incident 24 is the reason the press has
    this and it applies here unchanged: a model can be retired under a running
    schedule and the first thing that notices is a cron with nobody watching.

    It asks the provider's `/models` endpoint and nothing else. Whether the
    request FITS is gate 1's question, `python3 pipeline/budget.py`, and that
    separation is deliberate: three gates that each ask one question can each
    fail for one reason.

    It raises, so a failure stops the chair's `&&` chain before the deploy.
    """
    import os

    import httpx

    wanted = {name: PROVIDERS[name]["model"] for name in PROVIDERS}
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "preflight: GROQ_API_KEY is absent, so nothing can be asked. "
            "Set it with `modal secret create groq GROQ_API_KEY=...`.")

    resp = httpx.get("https://api.groq.com/openai/v1/models",
                     headers={"Authorization": f"Bearer {key}"}, timeout=30)
    resp.raise_for_status()
    listed = {m["id"] for m in resp.json().get("data", [])}

    print("distill preflight:")
    missing = []
    for name, model in wanted.items():
        mark = "ok" if model in listed else "MISSING"
        note = "  (production)" if name == PRODUCTION_PROVIDER else ""
        print(f"  [{name}] {model}: {mark}{note}")
        if model not in listed:
            missing.append(f"{name} -> {model}")

    production = PROVIDERS[PRODUCTION_PROVIDER]["model"]
    if production not in listed:
        raise RuntimeError(
            f"preflight: {production} is not listed by Groq for this key, so "
            f"distill cannot read a single paper. It is PRODUCTION_PROVIDER in "
            "pipeline/distill.py, and the bake-off that chose it is "
            "docs/evals/2026-09-07-distill-bakeoff.json. Nothing was deployed.")
    if missing:
        print(f"  NOTE: {len(missing)} non-production model absent ({', '.join(missing)}). "
              "The daily run never reaches it, and the bake-off would fail.")
    print("  fit is gate 1's question: python3 pipeline/budget.py")
    return f"preflight ok: {production} is listed and would read the paper"


@app.function(
    # Neon is deliberately absent. A rehearsal must not be able to write a claim,
    # and the strongest form of that promise is a missing credential rather than
    # a missing function call. This is the shape pipeline/triage.py::rehearse
    # established and the reason is the same.
    secrets=[modal.Secret.from_name("groq")],
    timeout=900,
)
def rehearse(allow_abstract_only: bool = False) -> str:
    """Gate 3: one real call on the real prompt, writing nothing.

        modal run pipeline/distill.py::rehearse
        modal run pipeline/distill.py::rehearse --allow-abstract-only

    The first two gates ask questions about the request. This one exercises the
    provider, and every one of the four failures of
    INC-2026-09-24-press-provider-migration was on this question. The prompt, the
    provider, the key, the temperature, the `response_format` and the 180-second
    timeout are the real ones, because it calls `extract_claims` rather than
    reimplementing it. What is fake is the paper, and what is absent is the
    database.

    **It asks distill's own question, which no other gate asks: can this job
    read the paper it was handed?** Until 2026-09-27 the answer was no and
    nothing said so out loud: the request was refused every time, the run
    degraded to `abstract[:6000]`, and it succeeded. A job that succeeds while
    doing the lesser thing is the shape of the owner's finding of 2026-09-25,
    that the corpus is not being read: 164 papers read in full out of 8,956
    ingested. So a rehearsal that got claims out of an abstract and called
    itself green would be the same defect in a smaller box.

    `python3 pipeline/budget.py` now says the request fits, with 241 tokens to
    spare at `FULLTEXT_CHARS` of 12,000. This gate is what turns that arithmetic
    into a fact, because the arithmetic has been wrong before: the payload it
    sends is 50 tokens heavier than the densest of the 14 real papers in
    docs/evals/2026-09-27-fulltext-token-density.json, so a provider that
    accepts this accepts them.

    It therefore raises when the full-text request does not survive, and
    `--allow-abstract-only` is the escape hatch for the day the chair is
    deploying an unrelated fix and knows the payload still does not fit. The
    hatch prints what it is forgiving, so the receipt says which of the two
    things was proved.
    """
    import os

    import httpx

    prompt, sha = load_prompt()
    taxonomy = topics()

    # The worst case by construction: exactly what the daily run sends when
    # fetch_fulltext succeeds, which is the request that must fit.
    body = (REHEARSAL_SAMPLE * (FULLTEXT_CHARS // len(REHEARSAL_SAMPLE) + 1))[:FULLTEXT_CHARS]

    print("distill rehearsal:")
    print(f"  model: {PROVIDERS[PRODUCTION_PROVIDER]['model']}   prompt_sha: {sha}   "
          f"payload: {len(body)} chars (FULLTEXT_CHARS)   timeout: 180s")

    read_in_full = True
    started = time.monotonic()
    try:
        out = extract_claims(PRODUCTION_PROVIDER, REHEARSAL_TITLE, body)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        print(f"  the full-text request was refused: HTTP {status}")
        if not allow_abstract_only:
            raise RuntimeError(
                f"the rehearsal's full-paper request was refused with HTTP "
                f"{status}, so a deploy today installs a job that reads "
                "abstracts and reports papers. `python3 pipeline/budget.py` "
                "says this request fits, so either the prompt grew since the "
                "guard last ran, or the provider's limit moved, or the guard's "
                "measured density is stale. `python3 tools/fulltext_density.py` "
                "says which, against real papers. Lower FULLTEXT_CHARS until it "
                "stops printing REFUSED. Pass --allow-abstract-only to deploy "
                "anyway, knowingly. Nothing was deployed."
            ) from exc
        read_in_full = False
        print("  --allow-abstract-only: retrying at abstract size, as the run does")
        out = extract_claims(PRODUCTION_PROVIDER, REHEARSAL_TITLE, body[:6000])
    elapsed = time.monotonic() - started

    claims = [c for c in out.get("claims", []) if isinstance(c, dict)]
    with_text = [c for c in claims if (c.get("claim") or "").strip()]
    kept, dropped = 0, {}
    for c in claims:
        tags, off = taxonomy.normalize(c.get("topics"))
        kept += len(tags)
        for tag in off:
            dropped[tag] = dropped.get(tag, 0) + 1

    print(f"  {len(claims)} claims back, {len(with_text)} with text, in {elapsed:.1f}s")
    print(f"  read in full: {read_in_full}")
    print(f"  topics: {kept} on the closed list, {sum(dropped.values())} dropped "
          f"{sorted(dropped) if dropped else ''}")
    for c in with_text[:3]:
        print(f"    - {(c.get('claim') or '')[:110]}")
        print(f"      evidence: {str(c.get('evidence'))[:90]}")
    print(f"  institutions: {out.get('institutions')}")
    print("  wrote nothing: this container has no database credential")

    if not with_text:
        raise RuntimeError(
            "the rehearsal got no claim with text back. A distill run that "
            "answers with an empty claims list writes nothing and logs nothing "
            "unusual, so the paper is marked processed and never revisited. "
            "Nothing was deployed.")
    if dropped:
        raise RuntimeError(
            f"the model tagged claims with {sum(dropped.values())} topics off "
            f"the closed list ({sorted(dropped)}), which pipeline/topics.py "
            "drops. Dropped tags mean claims no query can match, which is "
            "incident 30 and the 18 invisible claims of 2026-09-26. Fix "
            "prompts/distill.md and pipeline/topics.py together. Nothing was "
            "deployed.")

    verdict = "in full" if read_in_full else "from an abstract only"
    return (f"rehearsal ok: {len(with_text)} claims read {verdict} at prompt "
            f"{sha} in {elapsed:.1f}s, wrote nothing")


@app.function(
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq")],
    timeout=3600,
)
def bake_off(n_papers: int = 8) -> list[dict]:
    import os

    import psycopg

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        papers = conn.execute(
            """
            select id, title, abstract, url, triage_decision
            from distill_queue
            where abstract is not null and length(abstract) > 200
            order by case triage_decision when 'deep_read' then 0 else 1 end,
                     case tier when 'b' then 0 when 'c' then 1 else 2 end,
                     published_at desc nulls last
            limit %s
            """,
            (n_papers,),
        ).fetchall()

    results = []
    for pid, title, abstract, url, decision in papers:
        entry = {"paper_id": pid, "title": title, "url": url, "decision": decision}
        for provider in PROVIDERS:
            try:
                entry[provider] = extract_claims(provider, title, abstract[:6000]).get("claims", [])
            except Exception as exc:
                entry[provider] = [{"claim": f"PROVIDER ERROR: {exc}", "evidence": "", "topics": []}]
            time.sleep(PROVIDERS[provider]["pause"])
        results.append(entry)
        print(f"distilled both: {title[:60]}")
    return results


@app.function(
    schedule=modal.Cron("30 11 * * *"),  # after ingest, BEFORE triage (budget priority)
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq")],
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=3600,
)
def distill(max_papers: int = 30, queue_text: str | None = None):
    """The day's drain: the reading queue first, then the daily intake.

    `queue_text` is docs/research/reading-queue.md's content. The scheduled run
    leaves it None and reads the copy baked into the image; `modal run` passes
    the working copy, so a line appended this morning is read this morning
    rather than after the next deploy.
    """
    import os

    import httpx
    import psycopg
    from sentence_transformers import SentenceTransformer

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # ADR-35: what the skill seat could not read comes before what the
        # firehose happened to deliver, because a queue line is a person
        # asking and the intake is a subscription.
        queue = reading_queue()
        text = queue_text
        if text is None:
            text = queue.read_file("/root/reading-queue.md") or queue.read_file(queue.QUEUE_PATH)
        if text:
            waiting = queue.pending(text, limit=None)
            requested = waiting[:queue.MAX_PER_RUN]
            print(f"reading queue: {len(waiting)} pending, {len(requested)} taken this run")
        else:
            requested = []
            print("reading queue: unreadable from here, so the day's intake only. "
                  "The file is baked into the image; check the deploy.")
        first = queue.resolve(conn, requested,
                              fetch_metadata=read_paper().fetch_metadata) if requested else []
        # Committed before a single claim is written: a paper ingested because
        # someone asked for it should stay in the corpus even if the provider
        # rate-limits this run to a stop two papers later.
        conn.commit()

        intake = conn.execute(
            """
            select id, title, abstract, triage_decision, source
            from distill_queue
            order by case triage_decision when 'deep_read' then 0 else 1 end,
                     published_at desc nulls last
            limit %s
            """,
            (max_papers,),
        ).fetchall()
        papers = queue.merge(first, intake, max_papers)
        print(f"{len(papers)} papers to distill: {len(first)} from the reading "
              f"queue, {len(papers) - len(first)} from the day's intake")
        if not papers:
            return 0

        marking_fulltext = has_column(conn, "papers", "fulltext_chars")
        if not marking_fulltext:
            print("papers.fulltext_chars is missing, so the weekly issue cannot "
                  "say how much was read in full; run db/schema.sql")
        grading = has_evidence_grade(conn)
        grader = evidence() if grading else None
        if not grading:
            print("claims.evidence_grade is missing; run db/schema.sql to start grading")
        stamping = has_column(conn, "claims", "prompt_sha")
        if not stamping:
            print("claims.prompt_sha is missing, so nothing records which distill "
                  "prompt wrote a claim; run db/schema.sql")
        taxonomy = topics()
        _, sha = load_prompt()
        print(f"prompt_sha {sha} ({len(taxonomy.TOPICS)} topics accepted)")
        off_list: dict[str, int] = {}

        wrote_any = False
        finished: list[str] = []   # papers this run actually got through
        fulltexts_used = 0     # the fetch budget: how many HTML pulls were tried
        read_in_full = 0       # how many papers' claims actually came from one
        graded: dict[str, int] = {}
        for pid, title, abstract, decision, source in papers:
            body = None
            if fulltexts_used < FULLTEXT_MAX_PER_RUN:
                body = fetch_fulltext(pid)
                if body:
                    fulltexts_used += 1
                    print(f"  full text ({len(body)} chars): {title[:50]}")
            used_fulltext = body is not None
            if body is None:
                body = (abstract or "")[:6000]
            try:
                out = extract_claims(PRODUCTION_PROVIDER, title, body)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    print("rate limited by Groq; stopping — next run resumes")
                    break
                if body is not None and len(body) > 6000:
                    # full text too large for the provider — fall back to abstract.
                    # The claims then came from the abstract, so this paper was
                    # NOT read in full and the marker has to say so: a stat the
                    # issue prints cannot be generous about what was read.
                    print(f"  provider rejected full text ({exc.response.status_code}); retrying with abstract")
                    used_fulltext = False
                    out = extract_claims(PRODUCTION_PROVIDER, title, (abstract or "")[:6000])
                else:
                    raise
            claims = out.get("claims", [])
            institutions = [i for i in (out.get("institutions") or []) if i][:3]
            if institutions:
                conn.execute(
                    "update papers set institutions = %s where id = %s",
                    (institutions, pid),
                )
            for c in claims:
                text = (c.get("claim") or "").strip()
                if not text:
                    continue
                # The taxonomy is enforced here, at the only place claims are
                # written. Tags are folded onto the closed list and anything
                # still unknown is dropped and counted, never stored: a tag that
                # no query can match is worse than no tag, because it looks like
                # coverage. pipeline/topics.py explains what the fold will and
                # will not do.
                tags, dropped = taxonomy.normalize(c.get("topics"))
                for tag in dropped:
                    off_list[tag] = off_list.get(tag, 0) + 1
                # Columns are assembled rather than branched because two optional
                # columns is four INSERTs, and the next one is eight. Every name
                # here is a literal from this file, so nothing user-supplied ever
                # reaches the statement text.
                cols = ["paper_id", "claim", "evidence", "topics", "procedure"]
                vals = [pid, text, c.get("evidence"), tags, c.get("procedure")]
                if grading:
                    row_grade = grader.grade(pid, c.get("evidence"), c.get("measured"), source)
                    graded[row_grade] = graded.get(row_grade, 0) + 1
                    cols.append("evidence_grade")
                    vals.append(row_grade)
                if stamping:
                    cols.append("prompt_sha")
                    vals.append(sha)
                conn.execute(
                    f"insert into claims ({', '.join(cols)}) "
                    f"values ({', '.join(['%s'] * len(cols))})",
                    tuple(vals),
                )
                wrote_any = True
            # fulltext_chars is how the weekly issue knows how much was read in
            # full. NULL means the abstract, which is the honest answer when
            # arXiv served no HTML.
            if used_fulltext:
                read_in_full += 1
            if marking_fulltext:
                conn.execute(
                    "update papers set distilled_at = now(), fulltext_chars = %s "
                    "where id = %s",
                    (len(body) if used_fulltext else None, pid),
                )
            else:
                conn.execute("update papers set distilled_at = now() where id = %s", (pid,))
            conn.commit()
            finished.append(pid)
            print(f"  {len(claims)} claims <- {title[:60]}")
            time.sleep(PROVIDERS[PRODUCTION_PROVIDER]["pause"])

        # The research seat strikes the queue line, and it strikes what this
        # log says was read. One line, greppable, naming the ids.
        if first:
            done = [pid for pid, *_ in first if pid in set(finished)]
            left = [pid for pid, *_ in first if pid not in set(finished)]
            if done:
                print("reading-queue: read this run, the lines for these ids can "
                      f"be struck in {queue.QUEUE_PATH}: {', '.join(done)}")
            if left:
                print("reading-queue: not reached this run, still pending: "
                      + ", ".join(left))

        print(f"read {read_in_full} papers in full, "
              f"{len(papers) - read_in_full} from the abstract alone")
        if graded:
            tally = ", ".join(f"{g} {n}" for g, n in sorted(graded.items()))
            print(f"evidence grades this run: {tally}")
        # The off-list rate, printed every run. It was 3.9% for the pipeline's
        # whole life and nobody could have known, because nothing counted it.
        if off_list:
            worst = sorted(off_list.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
            print("tags dropped as off-list: "
                  + ", ".join(f"{t!r} x{n}" for t, n in worst))
            print("  a tag dropped often is a proposal for prompts/distill.md, "
                  "which belongs to the research seat (ADR-12 whitelist)")

        # Embedding is blackboard work: sweep every unembedded claim and paper,
        # not just this run's, so any crash or missed backfill heals next run.
        pending = conn.execute(
            "select id, claim from claims where embedding is null"
        ).fetchall()
        pending_papers = conn.execute(
            """
            select id, title, coalesce(abstract, '')
            from papers where embedding is null
            order by fetched_at limit 500
            """
        ).fetchall()
        if pending or pending_papers:
            model = SentenceTransformer(EMBED_MODEL)
            hf_cache.commit()  # persist downloaded weights for future runs
        if pending:
            vectors = model.encode([t for _, t in pending], normalize_embeddings=True)
            for (claim_id, _), vec in zip(pending, vectors):
                conn.execute(
                    "update claims set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), claim_id),
                )
            conn.commit()
            print(f"embedded {len(pending)} claims with {EMBED_MODEL}")
        if pending_papers:
            texts = [f"{t}\n\n{a[:2000]}" for _, t, a in pending_papers]
            vectors = model.encode(texts, normalize_embeddings=True)
            for (paper_id, _, _), vec in zip(pending_papers, vectors):
                conn.execute(
                    "update papers set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), paper_id),
                )
            conn.commit()
            print(f"embedded {len(pending_papers)} papers with {EMBED_MODEL}")
        return len(pending)


@app.local_entrypoint()
def main(max_papers: int = 30, queue: str = "docs/research/reading-queue.md"):
    """A manual run sends the working copy of the reading queue, not the baked one.

        modal run pipeline/distill.py --max-papers 8
        modal run pipeline/distill.py --queue /dev/null     # the intake alone
    """
    text = pathlib.Path(queue).read_text() if pathlib.Path(queue).exists() else None
    if text is None:
        print(f"no reading queue at {queue}; the run will use the image's copy")
    print(f"claims written: {distill.remote(max_papers, queue_text=text)}")


@app.local_entrypoint()
def run_bake_off(n_papers: int = 8):
    results = bake_off.remote(n_papers)
    with open("bakeoff_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote bakeoff_results.json with {len(results)} papers")
