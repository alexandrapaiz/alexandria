# ExO run note — 2026-11-02, third message wake of the night

**Trigger.** `window:message`, a note from `alexandria/writer`
(`22e71126-f2be-4a0d-aa85-3e741dfac661`, 01:36:03Z) confirming this seat's
cadence count at the sources, filing an incident on the class, and **returning
one limit** on the tail of this seat's previous reply. **Mode: wake run** per
§0 — the event's work, three standing duties, one improvement, no weekly
cycle. Draft PR **#690 opened at turn 4**, the fastest this seat has shipped.

Full writeups: `docs/agents/quality-claims.md` ("The limit the writer seat
returned"), `docs/agents/learning-log.md` (2026-11-02, third entry),
`docs/agents/hq-relay.md` (2026-11-02, third wake) and
`docs/agents/incidents/inbox/INC-2026-11-02-an-absent-run-record-was-read-as-a-missing-run-and-it-is-a-claim-about-one-line.md`.
This note is the short form.

## Not a duplicate wake, and the chain is declared

Two pull requests of this seat were open when this run started, #680 (register
rows) and #686 (security's sweep, stacked on #680), both ready, neither merged.
Neither answered this payload: #680 produced the claim the writer returned and
#686 answered a different message. The survey ran **after** the push, as the
reordered rule directs, and cost one rebase — **onto #686 rather than onto
`main`**, deliberately, because the rule this run amends is §3g step 6 and step
6 exists only on #680. A main-based branch would have had to invent the step
again and then conflict with it. Chain depth 2, declared in the PR title.

## The event's work

**The return is correct, and it understates the gap.** Verified at the code at
01:47Z rather than accepted. `pipeline/weekly.py`: the `try` opens at **1874**,
`check_availability()` is at **1879**, `psycopg.connect` at **1881**, and
`record_runtime` at **1885**. The writer's sentence stops there. Three further
calls run *before* the `try` — `week_just_ended()` 1846, `week_window()` 1862,
the two `open("/root/prompts/digest*.md")` reads 1863–1864 — and `notify_owner`
(defined 1367) is called from the `except` at the foot of that same `try`, so
the handler cannot see anything above 1874.

So the write site cuts a press run into **three** zones, not two:

| zone | row on the receipt | mail to the owner | readable by a seat |
|---|---|---|---|
| reached 1885 | yes | n/a | yes |
| raised 1874–1884 | no | **yes** | **no** |
| raised 1846–1873, or never invoked | no | no | no |

The sentence this seat shipped twelve hours earlier said the run record
"separates absent from broken from unscheduled-since-the-last-repair." It
separates nothing, and the repair it implied — a deploy — fixes one of the three.

**Two findings the return did not contain.**

1. **`first_seen_at` has the same defect and it is worse here.** Its comment at
   `pipeline/runtime_sha.py:253` calls it "when did this exact deploy start
   running", and the upsert moves it only at line 1885. For `weekly`,
   `first_seen_at` and `recorded_at` are the **same instant**
   (2026-10-19T09:01:21.333Z), so the drift guard is blind for precisely the app
   that is missing its slot: a deploy landing this minute would not appear until
   a run reached 1885, which is the event in question. Confirmed by replaying
   the digest myself with the limit raised 40 → 400 against `origin/main`:
   `deployed_commit None` after **227** candidate commits, so the recovery route
   is exhausted rather than shallow-clone-limited.
2. **The sibling read narrows and does not settle.** All four siblings recorded
   runs on 2026-11-01 on `first_seen_at` values unchanged since mid-October, so
   the workspace is back and no re-deploy was needed to restore *those*
   schedules. But each pipeline module is its own `modal.App`
   (`alexandria-weekly`, `alexandria-ingest`, …), so a sibling that ran is not
   evidence about a peer that did not.

**"Today's firing settles which" is one-sided, and that is this run's answer to
the question the note left open.** A 09:00Z run that reaches 1885 proves the
schedule is installed and retroactively makes 2026-10-26 a death. A 09:00Z that
leaves the field at 2026-10-19 is consistent with all three zones and licenses
nothing. The firing is seven hours past this run's budget either way.

**So the repair is a question, not an instrument.** Zone 2 *is* recorded — by
SMTP, to the owner, subject `ALARM_SUBJECT_CANNOT_PRINT`, into no table. One
question to the one reader of that surface separates two of the three zones
today: **did such a mail arrive on 2026-10-26?** Yes takes the deploy off the
table and routes the repair to the engineer seat; no narrows it to zones 1 and
3. It has been answerable for seven days. Filed as **Owner Ask 1** on the relay
page and sent this run. The code half — move the first durable write ahead of
the first thing that can fail, or give `notify_owner` a row — is carded for the
engineer seat rather than asked, because an ask is cheaper than an instrument.

## The one improvement: §3g step 6 amended in place

The overclaim is in a paragraph this seat wrote twelve hours ago, so it is
**rewritten** rather than followed by a correction, which would leave both
readings in the file for the next run to choose between. The general form:
**before you read an absence as evidence of an absent event, find the line that
writes the row and count what runs ahead of it.** The only proposition an empty
field supports is that nothing reached that line. Three sub-rules, each learned
by doing it this run: read upward until you leave the handler, because the zone
outside it is silent and not merely unrecorded; name the surface that holds the
second source even when you cannot read it; and say which side of a firing test
a result can settle before you spend a run waiting on it.

The precedent is older than the rule and is in this repository.
`tools/cron_firing.py` opens with "Three states, because two is what gets this
wrong" and scores a **seat's** cron slot three ways. The product's five
`modal.App`s have no such reader, and the receipt's `deploy` block is the
two-state instrument that file was written to replace.

## Four instances of one class in one run

This is why it is a rule and not a correction.

1. `weekly.recorded_at`, read as "the job did not run".
2. `first_seen_at`, same write site, blind for the app that needs it.
3. The board's `pr_url: null` on the `security` 23:04:44Z row — the previous
   run's §2b finding, and **now closed with evidence**: that run opened PR #657
   at 23:06:23Z, ninety-nine seconds in, and #657 merged at 01:13:17Z and is
   `main`'s head. The field said null about a run whose work is on the trunk.
4. §2b's own red-main command, below.

## Standing duties

- **§2b failure sweep.** `runs_since_hours=12`, `runs_saturated: false`, 35
  rows, read 01:55Z. 29 `exit 0`; three `exit 124` wall-clock kills (`skill`
  00:28:54 / #675, `engineer` 23:06:00 / #659, `security` 23:04:44 / #657);
  three turn-one weekly-limit `exit 1` refusals, all before the 23:00Z reset.
  **No post-reset failure.** And **main's health is stated as "no verdict on
  the head" rather than as green**: `checks.yml` is path-filtered on
  `pull_request` *and* on `push: branches: [main]`, main is `729b0d58`, and the
  #657 merge touched `mcp/server.py`, `site/lib/path.js`,
  `tests/path.test.mjs`, `tests/test_ci_coverage.py` and
  `tests/test_mcp_dsn_redaction.py` — not one in the filter. `deploy-main` ran
  and passed, which is a deploy and not a test. `tools/ci_coverage.py` exits 1:
  **14 of 78** test files run in any workflow, and two of the five files in
  main's own head merge carry tests among the 64. Folded into the one
  improvement as a §2b clause and **labelled as such**, because it is the same
  rule applied to this duty's own command.
- **§3f Outstanding with HQ.** Re-read 01:51–01:55Z as a **diff** against the
  01:26Z table. Nine rows carried, nothing landed, nothing regressed — the
  third agreeing reading of this heading in one night, which is what the diff
  rule was added to produce. One row added: Owner Ask 1. Clone depth
  re-measured on **this run's own log** (`git clone --depth 1`, 15 days open,
  and it cost this run an unshallow plus a refspec widen before it could read a
  sibling branch). The cadence word at **9 days** is the oldest open row.
- **§6 learning log.** Written, seven carried items.

## What this run did not do

The §3g register sweeps other than the row the event named, the unowned-duty
hunt, the step-5 public-claim surface pass (**ten days** stale and owed by the
next weekly cycle), the queue re-verification, and the weekly cycle. All
skipped per the wake-run mode. It also did not wait for the 09:00Z firing, and
says what that firing would and would not settle instead of claiming to have
read it.
