# The rehearsal print: what the engineer should build

**Enforced at:** `docs/agents/runtime-changes.md`, the ladder for a
provider or model change, gate 3. The engineer charter names this file
in its register list.

**Status: built, 2026-09-24, engineer seat.** `rehearse()` is in
`pipeline/weekly.py` beside `preflight` and `weekly`, the
`press_rehearsals` table is in `db/schema.sql`, the `&&` link is in this
module's deploy docstring, and `tests/test_press_rehearsal.py` holds the
two promises that leave no trace when they are kept: no write to
`digests`, no mail credential in the container. The ladder has three
working links. Two notes for a reader of the specification below.

- The deploy chain in `pipeline/weekly.py`'s docstring is the
  authoritative one and it carries a fourth link this file does not:
  `python3 tools/rehearse_email.py --quiet`, the email half, which
  shipped first and costs nothing.
- The rehearsal has never run against the live provider, because no seat
  holds the Moonshot key. Its first real execution is the chair's, on
  the next deploy. Everything a test can hold without a key is held.

Written by the ExO seat on 2026-09-24, on the owner's dispatch, after
INC-2026-09-24-press-provider-migration. This is a specification and a
request, not code. `pipeline/` belongs to the engineer seat and this
seat does not write there.

## Why

The press moved to a new provider and failed four times in one evening.
Every failure was an integration property that only a real call reveals,
and one real call before the deploy would have found all four. The org
had no way to make one real call without writing to the database of
record and mailing the subscribers, so nobody made one.

That is the entire gap. The press has a preflight that asks the provider
whether a model exists, and a budget guard that asks whether the request
fits, and nothing that asks whether the thing works.

## What to build

A third Modal function in `pipeline/weekly.py`, beside `preflight` and
`weekly`.

```
@app.function(secrets=[neon, moonshot, groq, ...], timeout=1800)
def rehearse() -> str
```

It is `weekly()` with two differences and no others.

1. **It writes to `press_rehearsals`, never to `digests`.** A new table,
   its own primary key, holding at minimum: `created_at`, `week`,
   `model`, `prompt_sha`, `body`, `elapsed_seconds`, and the payload
   stats. The real table is the record the site and the readers depend
   on, and a rehearsal must not be able to overwrite a published week
   even by accident.
2. **It sends nothing.** `send_newsletter` is not called. Instead it
   prints every subject line it would have produced, on the success path
   and on the alarm path both, so the chair can read them against
   `docs/voice/taste.md` without a message leaving the building. Failure
   4 of the incident was an alarm subject, and an alarm subject is only
   visible to a rehearsal that renders it.

Everything else is the real thing, and this is the part worth being
stubborn about. The real prompt from `/root/prompts/digest.md`. The real
payload from `gather()` against the real database. The real provider,
the real key, the real `MAX_COMPLETION_TOKENS`, the real client timeout,
the real connection open-and-close sequence around the model call. A
rehearsal that mocks the provider tests the mock.

Three of the four failures were in that list. The reservation, the
timeout and the connection handling are precisely the parameters a
rehearsal must not simplify away.

## What it must print

Verbatim output, because incident 8 is the standing reason: judge a run
by its artifacts, never by its conclusion.

```
rehearsal: <model id> wrote <n> words in <m>s
  prompt_sha: <sha>   reservation: <MAX_COMPLETION_TOKENS>   timeout: <s>
  payload: <the same stats line weekly() prints>
  finish_reason: <as returned>
  saved to press_rehearsals id <n>
  subject it would have sent:  <the real success subject>
  subject on the alarm path:   <the real alarm subject>
  first 400 characters of the body:
  ...
```

`finish_reason` is on that list because of failure 1. A `length` finish
with empty content is the exact signature of a reasoning model
overrunning its reservation, and printing it turns a silent empty
response into a legible one.

It raises on any failure, loudly, the way `preflight` does. No email: a
human is watching a rehearsal by definition, and the emailing path
belongs to the scheduled run where nobody is.

## The receipt, which is what makes it a gate

A rehearsal a chair can skip is advice. The gate is the deploy command
refusing without it.

```bash
python3 pipeline/budget.py \
  && modal run pipeline/weekly.py::preflight \
  && modal run pipeline/weekly.py::rehearse \
  && modal deploy pipeline/weekly.py
```

For the last link to mean anything, `rehearse` has to be able to tell a
fresh rehearsal from a stale one. So the scratch row is the receipt, and
`rehearse` refuses to report success unless the row it just wrote
carries the model id and `prompt_sha` that are about to be deployed. A
receipt from a different model, or from last week's prompt, is not a
receipt.

Suggested, and the engineer should overrule it if there is a cleaner
shape: have `rehearse` compare against `FALLBACK_MODELS[0]` and the
current prompt hash, and raise `PressCannotPrint` with both values when
they disagree.

## Cost, which the owner will ask about

One Kimi call per rehearsal, roughly $0.05 by ADR-32's own arithmetic,
paid only when the press's model, provider, reservation, timeout or
prompt changes. The evening it is written to prevent cost four failed
prints, four alarm emails, four chair diagnoses and one issue that was
written and could not be saved.

## What this does not cover

The rehearsal proves the press can print. It does not prove the press
did print, and those are different duties. The second one is
`docs/agents/delivery-health.md` and the PM's standup line, and neither
substitutes for the other. A rehearsal is a gate before the machinery
goes unattended. Delivery health is the watch on it afterwards.

The daily corpus crons (ingest, distill, triage, interpret) have no
rehearsal and no availability check either. They are named here so the
gap is written down rather than discovered, and they are a separate
piece of engineer work with a separate trigger.

**Update, 2026-09-26, engineer seat.** The closing paragraph above named the
daily corpus crons as having no rehearsal and no availability check. Three of
the four now have both. `triage` and `interpret` got `preflight` and `rehearse`
when they moved to Kimi earlier tonight, and `distill` got both in the same run
that wrote this note, with its three-gate chain in its module docstring the way
this file asks for the press's.

Two things the reader should carry away rather than infer.

`ingest` still has neither, and it does not need them in this form, because it
calls no model. What it lacks is an availability check on its feeds, which is a
different question with a different answer.

`distill`'s rehearsal found something while being built, and it is worth more
than the gate. `python3 pipeline/budget.py`, with tiktoken installed so the
count is exact, says distill's full-paper request misses Groq's usable free tier
by 109 tokens, and that the run then retries at `abstract[:6000]` and succeeds.
The job whose entire purpose is reading papers in full cannot read one, and it
reports success when it reads the abstract instead. That is the arithmetic under
the owner's finding of 2026-09-25 and under the press's own number, 164 papers
read in full out of 8,956 ingested. So `rehearse` raises on the degradation
rather than accepting it, and the ledger entry of 2026-09-26 prices the three
ways to close 109 tokens.
