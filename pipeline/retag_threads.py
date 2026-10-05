"""One-time retag: Layer 4's claims get Layer 4's tags.

    modal run pipeline/retag_threads.py::count    # the dry run. Writes nothing,
                                                  # calls no model, costs $0.
    modal run pipeline/retag_threads.py::retag    # then, and only then

Owner directive 2026-10-05. `pipeline/topics.py` gained `protocols`,
`containment`, `security` and `self-improvement` today, which fixes every claim
distilled from tomorrow. It does nothing for the claims already in the table,
and those are the whole reason the tags were added: the research seat's census
of 2026-09-30 found 71 claims from containment, protocols and security papers,
of which 2 carried a tag anybody could query for. The graph page, the skill
agent and the digest all filter on `topics @> '{...}'`, so until this job runs
the four new tags describe a corpus of almost nothing and the directive's
"findable today" is not met.

## What it judges, and what it refuses to decide by rule

Candidates are chosen by rule and tagged by a model, and the split matters.

The RULE picks the population: a claim whose paper's title or abstract matches
one of `pipeline/priority.py`'s thread terms. That file is the owner's standing
threads and it is already what decides reading order, so this job inherits the
definition of a thread rather than inventing a second one. Title *or* abstract,
per the directive, which is wider than `priority.is_priority`'s title-only test
on purpose: that one orders a queue and over-promoting is expensive, this one
assembles a candidate list and a false candidate costs one model call.

The MODEL makes every tag decision. Nothing here tags a claim because its paper
matched a keyword, and that restraint is the finding this job was built around.
The same census read all 24 claims then credited to the containment thread and
found **none of them about containment**: they are reinforcement-learning and
harness papers that matched on "terminal", "isolated" and "container". A
keyword retag would have written `containment` onto every one of them and the
tag would have been born meaning nothing, which is exactly the failure
`pipeline/topics.py` exists to prevent one spelling at a time. So the model is
shown the claim, its evidence, and the thread definitions out of
`prompts/distill.md`, and it is told that answering with no tags at all is a
correct answer. It usually will be.

Tags are only ever ADDED. No existing tag is removed, because a tag already on
a claim was the distiller's judgment about a text this job cannot see, and
`security` arriving does not make `evals` wrong. The off-list tags the earlier
census counted (`safety` x3 and its friends) are left exactly where they are:
`pipeline/backfill_topics.py` already refuses to promote them by rule, and this
job does not delete them either. A claim can come out of here carrying both
`safety` and `security`, and the first one is still a proposal for the research
seat.

## Resumable, and why that needs a table rather than a fixed point

`backfill_topics.py` is resumable for free: its fold is a pure function, so a
repaired row repairs to itself and a killed run is resumed by running it again.
This job cannot borrow that. A model that reads a claim and correctly decides
it needs no new tag leaves the row byte-identical to a row nobody has looked
at, so "has this been judged" is not derivable from the claims table.

Hence `retag_log`, one row per claim judged, written in the same transaction as
the tags. A killed run is resumed by running it again and it skips what it has
already paid for. Re-running after it finishes is a no-op that calls no model.
The table is also the audit trail: it records which model answered and what it
added, so a tag written by this job is distinguishable forever from one the
distiller chose.

## The cheapest model in the table, read out of the table

`MODELS` below is sorted by `price_in + price_out` out of `pipeline/budget.py`
rather than hardcoded, so "the cheapest model" stays true when the table
changes instead of becoming a stale comment. Today that is Groq's free tier at
$0.00 per million tokens both ways, and the walk falls through all three of
them before it would reach a paid model, which it is capped out of anyway.

The real constraint is not money, it is 30 requests a minute and 1,000 a day on
that tier, which is why `MAX_CLAIMS_PER_RUN` exists and why the job is
resumable. `CAP_USD` is a guard and not a budget: at $0.00 a call it should
never bind, and if it ever does, the model list moved under us and the run
stopping is the correct outcome.

    python3 -m pytest tests/test_retag_threads.py -q
"""

from __future__ import annotations

import pathlib

import modal

# How many claims one run judges. Groq's free tier allows 1,000 requests a day
# and 30 a minute; one claim is one request, and 200 leaves the day's other
# jobs their share while draining the whole candidate population in a handful
# of runs. The job is resumable, so this is about politeness to a shared rate
# limit rather than about the size of the work.
MAX_CLAIMS_PER_RUN = 200

# Rows per transaction. Small, because the cost of losing progress here is a
# model call rather than a pure recomputation.
BATCH = 20

# A guard, not a budget. See the docstring: the model list is free today, so a
# run that reaches this ceiling has been pointed at a paid model by an edit
# nobody meant to make, and stopping is right.
CAP_USD = 0.10

# Output per claim is a short JSON object naming at most four tags. 300 is
# roughly four times what a full answer needs.
MAX_COMPLETION_TOKENS = 300

# The threads this job can write. The keys of `priority.THREAD_TERMS` minus
# `reasoning`, which is on the closed list already and has been since
# 2026-09-26: re-judging 846 claims against a tag that is already in use would
# be a second taxonomy change dressed up as a backfill.
THREADS = ("protocols", "containment", "security", "self-improvement")

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "requests==2.32.3")
    .add_local_file("pipeline/topics.py", "/root/topics.py")
    .add_local_file("pipeline/priority.py", "/root/priority.py")
    .add_local_file("pipeline/budget.py", "/root/budget.py")
    .add_local_file("pipeline/llm.py", "/root/llm.py")
    .add_local_file("prompts/distill.md", "/root/distill.md")
)

app = modal.App("alexandria-retag-threads", image=image)


def _sibling(name: str):
    """A pipeline module, wherever this is running from.

    Modal drops these at /root; a local import finds them beside this file. The
    same two-path trick distill.py and backfill_topics.py use, for the same
    reason: the fold the tests exercise is the fold the run uses.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    return __import__(name)


def topics():
    return _sibling("topics")


def priority():
    return _sibling("priority")


def llm():
    return _sibling("llm")


def cheapest_first(guard, threads=THREADS) -> list[str]:
    """Production model ids from `budget.MODELS`, cheapest first.

    "Cheapest in the budget table" read out of the budget table. Sorted by the
    sum of the two prices, with the id as the tiebreak so the order is stable
    across runs rather than dictionary-insertion luck. `preview` models are
    skipped: a one-time job over the whole corpus is not where a preview id
    should be discovered to have gone.
    """
    usable = [
        (spec["price_in"] + spec["price_out"], model)
        for model, spec in guard.MODELS.items()
        if spec.get("status") == "production" and model not in guard.DECOMMISSIONED
    ]
    return [model for _, model in sorted(usable, key=lambda pair: (pair[0], pair[1]))]


# ---------------------------------------------------- what the model is asked

SYSTEM = """You are tagging claims that are already in a research library.

Four topic tags were added to the library's closed vocabulary today. Every
claim below was extracted from a paper whose title or abstract matched one of
these threads by keyword, which is a reason to LOOK and not evidence of
anything. Decide, for this one claim, which of the four tags genuinely apply.

{definitions}

Rules, in order of importance:

1. Tag the CLAIM, never the paper. A reinforcement-learning result from a paper
   that happens to mention sandboxes is not a containment claim.
2. Answering with an empty list is correct and common. Most claims selected by
   keyword will take none of these four tags. Do not reach.
3. A claim may take more than one, and the definitions say when: a measured
   attack that crossed a boundary is both `containment` and `security`.
4. Do not comment on the tags the claim already carries. You are only deciding
   which of the four to add.

Respond with JSON only: {{"topics": [...], "why": "one short sentence"}}
Use only these exact strings in `topics`: {allowed}
"""


def definitions(prompt_text: str, threads=THREADS) -> str:
    """The four definitions, lifted out of `prompts/distill.md`.

    Read from the prompt rather than restated here, for the reason
    `topics.prompt_topics` exists: the prompt is what the distiller is told, and
    a retag judging by a second, drifting copy of a definition would write tags
    the distiller would not have chosen. A definition this cannot find is a
    thread this job will not offer the model, which fails loudly in `count`
    rather than quietly in the middle of a write.
    """
    out = []
    lines = prompt_text.splitlines()
    for thread in threads:
        opener = f"`{thread}` covers"
        for i, line in enumerate(lines):
            if opener not in line:
                continue
            block = [line.strip()]
            for follow in lines[i + 1:]:
                if not follow.strip():
                    break
                block.append(follow.strip())
            out.append("- " + " ".join(block))
            break
    return "\n\n".join(out)


def render(claim: str, evidence: str, title: str, tags) -> str:
    return (f"Paper title: {title}\n"
            f"Claim: {claim}\n"
            f"Evidence: {evidence or '(none recorded)'}\n"
            f"Tags it already carries: {list(tags or []) or '(none)'}")


def chosen(answer: dict, taxonomy, threads=THREADS) -> list[str]:
    """The tags from one model answer, folded and filtered to the four.

    Folded through `topics.normalize`'s own machinery so a model that answers
    `Containment` or with a non-breaking hyphen is read as having said the tag,
    and filtered to `threads` so a model that decides to volunteer `evals` is
    ignored rather than obeyed. This job's mandate is four tags wide.
    """
    out: list[str] = []
    for raw in answer.get("topics") or []:
        if not isinstance(raw, str):
            continue
        folded = taxonomy.ALIASES.get(taxonomy.fold(raw), taxonomy.fold(raw))
        if folded in threads and folded in taxonomy.TOPICS and folded not in out:
            out.append(folded)
    return out


def merged(existing, additions: list[str], taxonomy) -> list[str]:
    """Existing tags in their order, then the new ones. Never a removal.

    `other` comes off when a real tag arrives, and that is the one exception to
    "only ever adds". `other` is on the closed list for exactly one purpose,
    which `topics.py` states: it is the tag a claim gets when every tag it came
    with was dropped, so that an untagged claim is at least countable. A claim
    that now carries `containment` is countable by a better name, and leaving
    both would file it under the fallback and the real thing at once.
    """
    out = [t for t in (existing or []) if t != taxonomy.FALLBACK or not additions]
    for tag in additions:
        if tag not in out:
            out.append(tag)
    return out[:taxonomy.MAX_PER_CLAIM] if len(out) > taxonomy.MAX_PER_CLAIM else out


# --------------------------------------------------------- selecting the work

LOG_DDL = """
create table if not exists retag_log (
    claim_id   bigint primary key references claims(id),
    judged_at  timestamptz not null default now(),
    model      text not null,
    added      text[] not null default '{}',
    why        text
)
"""

CANDIDATES = """
select c.id, c.claim, c.evidence, c.topics, p.title
from claims c
join papers p on p.id = c.paper_id
where (p.title ilike any(%(patterns)s) or coalesce(p.abstract, '') ilike any(%(patterns)s))
  and not exists (select 1 from retag_log r where r.claim_id = c.id)
order by c.id
limit %(limit)s
"""

# The same population without the `retag_log` exclusion and without the limit,
# for the dry run's denominator: "71 claims, 0 judged so far" is the sentence
# the directive asked for and it needs both numbers.
POPULATION = """
select count(*) filter (where true) as candidates,
       count(*) filter (where exists (select 1 from retag_log r where r.claim_id = c.id)) as judged
from claims c
join papers p on p.id = c.paper_id
where (p.title ilike any(%(patterns)s) or coalesce(p.abstract, '') ilike any(%(patterns)s))
"""


def patterns_for(threads, thread_terms) -> list[str]:
    """`%term%` for every term in `threads`, for Postgres `ilike any`."""
    return [f"%{term}%" for thread in threads for term in thread_terms[thread]]


def already_tagged(conn, threads=THREADS) -> dict[str, int]:
    """How many claims carry each of the four today. The before picture."""
    out = {}
    for thread in threads:
        out[thread] = conn.execute(
            "select count(*) from claims where topics @> %s", ([thread],)
        ).fetchone()[0]
    return out


# ------------------------------------------------------------- the entrypoints

@app.function(secrets=[modal.Secret.from_name("neon")], timeout=600)
def count() -> str:
    """The dry run, and it is a real one: no model is called and nothing is written.

    The directive asks for a count before a write. A dry run that spent money
    to produce the count would not be one, so this reports the size of the work
    and what it would cost rather than sampling the model's answers. What the
    model will decide is exactly the part this cannot predict.
    """
    import os

    import psycopg

    taxonomy, order, client = topics(), priority(), llm()
    guard = client.budget()
    models = cheapest_first(guard)
    patterns = patterns_for(THREADS, order.THREAD_TERMS)

    text = (pathlib.Path("/root/distill.md").read_text()
            if pathlib.Path("/root/distill.md").exists()
            else pathlib.Path("prompts/distill.md").read_text())
    defs = definitions(text)
    missing = [t for t in THREADS if f"`{t}` covers" not in defs]

    lines: list[str] = []
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute(LOG_DDL)
        conn.commit()
        candidates, judged = conn.execute(POPULATION, {"patterns": patterns}).fetchone()
        before = already_tagged(conn)
        lines.append(f"{candidates} claims come from papers matching the four threads "
                     f"by title or abstract; {judged} of them have been judged already, "
                     f"so {candidates - judged} remain")
        lines.append("carrying one of the four tags today: "
                     + ", ".join(f"{k} {v}" for k, v in before.items()))
        remaining = candidates - judged
        runs = -(-remaining // MAX_CLAIMS_PER_RUN) if remaining else 0
        lines.append(f"at {MAX_CLAIMS_PER_RUN} a run that is {runs} run(s)")
        lines.append(f"model: {models[0]} at ${guard.MODELS[models[0]]['price_in']:.2f}"
                     f"/${guard.MODELS[models[0]]['price_out']:.2f} per million, "
                     f"cheapest of {len(models)} production ids in budget.MODELS; "
                     f"fallbacks {models[1:]}")
        lines.append(f"cost ceiling for the whole population: "
                     f"{client.calls_within(CAP_USD, 900, MAX_COMPLETION_TOKENS, models[0])}")
        if missing:
            lines.append(f"REFUSING: no definition in prompts/distill.md for {missing}. "
                         "The model would be asked to apply a tag nobody defined.")
        sample = conn.execute(CANDIDATES,
                              {"patterns": patterns, "limit": 5}).fetchall()
    for claim_id, claim, _evidence, tags, title in sample:
        lines.append(f"  claim {claim_id} {list(tags or [])} from {title[:60]!r}: "
                     f"{claim[:90]}")
    lines.append("wrote nothing, called no model")
    print("\n".join(lines))
    return lines[0]


@app.function(
    secrets=[modal.Secret.from_name("neon"),
             modal.Secret.from_name("groq"), modal.Secret.from_name("moonshot")],
    timeout=3600,
)
def retag(max_claims: int = MAX_CLAIMS_PER_RUN, cap_usd: float = CAP_USD,
          dry_run: bool = False) -> str:
    """Judge and write. Run `count` first.

    `dry_run=True` judges exactly as the real run does and rolls back instead of
    committing, which is the rehearsal `docs/agents/runtime-changes.md` asks for
    before a job that calls a model goes live. It is not the same thing as
    `count`: this one spends the calls.
    """
    import os

    import psycopg

    taxonomy, order, client = topics(), priority(), llm()
    guard = client.budget()
    models = cheapest_first(guard)
    cap = client.Cap(cap_usd, label="retag-threads")
    patterns = patterns_for(THREADS, order.THREAD_TERMS)

    text = (pathlib.Path("/root/distill.md").read_text()
            if pathlib.Path("/root/distill.md").exists()
            else pathlib.Path("prompts/distill.md").read_text())
    defs = definitions(text)
    missing = [t for t in THREADS if f"`{t}` covers" not in defs]
    if missing:
        raise RuntimeError(
            f"prompts/distill.md defines no boundary for {missing}, so this job "
            "would ask a model to apply a tag nobody defined. Fix the prompt "
            "first; pipeline/topics.py and that file are one list.")
    system = SYSTEM.format(definitions=defs, allowed=", ".join(THREADS))

    available, notes = client.usable_models(models, os.environ)
    for note in notes:
        print(f"availability: {note}")
    pause = client.pace(models[0])
    print(f"models cheapest-first: {models}; pacing {pause:.1f}s between calls")

    judged = added_rows = 0
    tally: dict[str, int] = {t: 0 for t in THREADS}
    stopped = "population exhausted"
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute(LOG_DDL)
        conn.commit()
        before = already_tagged(conn)
        print("before: " + ", ".join(f"{k} {v}" for k, v in before.items()))
        rows = conn.execute(CANDIDATES,
                            {"patterns": patterns, "limit": max_claims}).fetchall()
        print(f"{len(rows)} unjudged candidates taken this run")

        for n, (claim_id, claim, evidence, tags, title) in enumerate(rows, start=1):
            try:
                answer, model = client.ask_json(
                    models, system, render(claim, evidence, title, tags),
                    os.environ, cap, max_completion=MAX_COMPLETION_TOKENS,
                    temperature=0.0, available=available)
            except client.CapReached as exc:
                print(exc)
                stopped = "spend cap"
                break
            except client.NoModelAnswered as exc:
                print(f"  claim {claim_id}: no model answered ({exc}); stopping")
                stopped = "no model answered"
                break

            additions = chosen(answer, taxonomy)
            after = merged(tags, additions, taxonomy)
            judged += 1
            for tag in additions:
                tally[tag] += 1
            if additions:
                added_rows += 1
                print(f"  claim {claim_id}: +{additions} "
                      f"({str(answer.get('why') or '')[:70]})")
            # The log row and the tags in one transaction. A row in retag_log
            # with the tags not written would make a claim look judged and
            # leave it untagged forever, which is the one outcome resumability
            # must not produce.
            if additions:
                conn.execute("update claims set topics = %s where id = %s",
                             (after, claim_id))
            conn.execute(
                "insert into retag_log (claim_id, model, added, why) "
                "values (%s, %s, %s, %s) on conflict (claim_id) do nothing",
                (claim_id, model, additions, str(answer.get("why") or "")[:500]))
            if n % BATCH == 0:
                if dry_run:
                    conn.rollback()
                else:
                    conn.commit()
                print(f"  {judged} judged, {added_rows} retagged, {cap.line()}")
            if pause:
                import time
                time.sleep(pause)

        if dry_run:
            conn.rollback()
            print("dry run: rolled back, nothing written")
        else:
            conn.commit()
        after_counts = already_tagged(conn)

    summary = (f"judged {judged} claims, retagged {added_rows}; "
               + ", ".join(f"{t} {before[t]}->{after_counts[t]}" for t in THREADS)
               + f"; stopped: {stopped}; {cap.line()}")
    print(summary)
    return summary


@app.local_entrypoint()
def main(dry_run: bool = True):
    """Local smoke path. Defaults to the dry run, because this job writes."""
    print(count.remote() if dry_run else retag.remote())
