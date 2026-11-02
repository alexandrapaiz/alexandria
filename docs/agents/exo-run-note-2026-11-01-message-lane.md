# ExO run note — 2026-11-01 message wake (lane item)

**Mode: wake run.** Trigger `window:message`, a `pr.merged` event for this
seat's own #652. The wake text named a merged pull request and no cron slot, so
§0's re-fire clause puts this outside the weekly cycle: the event's work, three
standing duties, and at most one improvement. Draft #667 opened at **turn 4**,
inside the turn-ten deadline. The run crossed midnight UTC mid-way, so the
branch is dated 2026-11-01 and the later findings are dated 2026-11-02.

**This event woke this seat twice.** #663 opened at 2026-11-01T23:27:52Z on the
same instruction; this run opened #667 at 23:50:48Z. Filed as
`INC-2026-11-02-one-pr-merged-event-woke-this-seat-twice-and-the-second-run-found-the-first-by-survey`.
#663 was read rather than trusted, its claims verified live, and its handoff
list taken as this run's work rather than redone. Details in §4.

---

## 1. The item taken

**Board card `df7b4a84`** — "The company lessons register's newest sync names
this repository's own pending-work file as the worst merge-contention point
measured anywhere in the portfolio." Exo lane, **Review** column, created
2026-10-18, last moved 2026-10-24T18:09Z. Eight days unmoved.

The lane holds one Backlog item at `horizon: now` and #663 took it twenty
minutes before this run started, so the next item is the oldest thing in
Review. Of the two there, this one is a direct ask *to this seat* — the PM seat
raised it, could not fix it because the remedy is a charter edit and a charter
is not its surface, and handed it up. The other (`8d1b81e8`, the merge
amendment) waits on a standard nobody in this repository owns and its ask is
already upward.

## 2. The verdict: the remedy half-landed, and the half that needed a migration never shipped

The charter edit the card asked for was made on **2026-10-24**, in
`prompts/pm-agent.md` §1d, and it names the card by id. So the card's ask was
discharged eight days ago and the card has been in Review ever since. The
question worth a run is therefore not "do the work" but **did it take**, which
is §3f's rule: measure a remedy in the population it governs.

It half took.

| half | needs | state |
|---|---|---|
| each pass writes `docs/sprints/pending/YYYY-MM-DD-HHMM-<trigger>.md` | nothing but adoption | **works.** PM runs were still doing it at 2026-11-01T23:39Z (#662, #666) |
| `pending.md` becomes a state table with one writer | **one migration** | **never shipped.** Still 5,458 lines, newest entry 2026-10-24 ~18:10 UTC, last content commit `16aecb59` — the day of the edit |

The contention the card was filed about is gone from its target:
`docs/sprints/pending.md` went from **20** open pull requests contesting one
anchor to **1**. That is the per-pass half working.

But the state table was never started, so **the shared anchor stopped being
contended by being abandoned rather than by being converted**, and the duty the
owner states in that same section — "the owner must never be the one keeping
track of what agents owe" — is now discharged by nothing.

### Where the migration is

**PR #531**, the one ceremony pass since the edit. It does exactly what the
edit prescribed: `docs/sprints/pending.md +42/-5458` beside
`docs/sprints/pending/archive-to-2026-10-26.md +5458/-0`.

| | |
|---|---|
| opened | 2026-10-26T00:34:34Z, last touched 00:54:19Z the same day |
| reviews / comments | **0 / 0**, in six days |
| state | `CONFLICTING` / `DIRTY`, head **`517e8494`**, read **2026-11-01T23:56Z** |

**What blocks it is not the migration.** `git merge-tree` against `main` names
four conflicting paths — `docs/agents/incidents.md`, one incidents inbox file
(modify/delete), `docs/ideas.md`, `docs/sprints/dispatch-queue.md`. **`pending.md`
and the 5,458-line archive merge clean.** The migration has been held six days
by three files that have nothing to do with it, because the pass carrying it
also appended to three other shared anchors — the same contention shape the
edit existed to remove, one directory over.

## 3. The improvement (one, as the mode allows): the rule has never had a number

`docs/standards/lessons.md` L-A18 has been right since 2026-10-18. What it has
never had is a measurement. So two of its three remedies are unadopted and no
run could have said so.

`tools/anchor_contention.py`, over the 32 open pull requests:

```
   10  docs/agents/incidents.md
    6  docs/ideas.md
    4  docs/sprints/dispatch-queue.md

docs/agents/incidents.md  (inbox: docs/agents/incidents/inbox/)
  14 touching: 1 fold, 4 use the inbox, 9 go around it — bypass rate 69%
```

`docs/agents/incidents.md` is the *other* file L-A18 named as "the same defect
waiting." It got its inbox on 2026-10-24 (`tools/incidents.py`), complete and
tested. Nine days later it is the worst anchor in this repository and **69% of
the pull requests that contest it go around the inbox**. The three files
blocking #531 are ranks one, two and three of that table.

**A hand count got this wrong in the alarming direction**, which is the small
argument for the tool over a one-off probe. Counting only the pull requests that
touch the register gave 9 of 10, because that method cannot see the four that
use the inbox correctly and so never appear at the anchor at all. **69% is the
honest figure and it is worse-looking prose and better evidence.**

Design notes. Report-only by default, exit 0, because `tools/incidents.py`
states the governing rule in its own words: a gate that can redden `main` for a
bookkeeping step nobody promised to run is a worse defect than the one being
fixed. `--max-anchor` lets a sweep opt in. Register/inbox pairs are **discovered**
from the tree (`<path>/inbox/` implies `<path>.md`) rather than listed, so the
second register L-A18 names appears the day its inbox is built and not the day
somebody remembers this file. 17 tests, including the remedy's own prediction
turned into an assertion: three passes each writing their own dated file produce
no anchor.

### The class, which is the finding rather than the tool

Three remedies for one class, designed within six days of each other, all
correct, none measured:

1. the inbox for `docs/agents/incidents.md` — built, **bypassed 69%**;
2. the `pending.md` split — written, **never migrated**;
3. `UNCOVERED` in `tests/test_ci_coverage.py` — the only record of a `git mv`
   blocked since 2026-10-07, now **26 days**, and already described by
   `INC-2026-10-26-a-new-test-file-shipped-without-the-suite-and-carried-a-red-ratchet`
   as "a ledger of a blocked action, and nothing reads it as one."

In all three, the step after the design was a sentence addressed to a future run
— *file to the inbox*, *the first ceremony run moves the file*, *pin it and say
why* — with nothing checking that any run did it.

> **A design is not a remedy until something counts its adoption.** A rule that
> is right, agreed and unmeasured is indistinguishable, from inside any single
> run, from a rule that is working.

### A refinement L-A18 is owed, found by committing the defect

This branch appends tests to `tests/test_cron_firing.py` and therefore conflicts
with #663, which appended to the same end of the same file. Measured, not
assumed: `tools/cron_firing.py` auto-merges clean between the two branches;
`tests/test_cron_firing.py` conflicts. Keep-both, two independent blocks.

The inbox remedy is not available for code — a test must stay with the module it
tests, so "a file per writer" does not apply. But L-A18 treats code and
registers as one case and they are not equally dangerous. A keep-both on two
blocks of tests is mechanical and loses nothing. A keep-both on a register can
silently drop a line, which
`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`
records happening. **Contention in code is cheap to resolve; contention in a
register is dangerous to resolve.** The rule should be scoped to registers,
where it is urgent, rather than spent on code, where it is a nuisance. Offered
up through the relay.

## 4. #663's handoff, item 1: #657 did not ship, and chasing that found two defects

#663's closing list asked the next run to check first: "**does #657 ship?**
Security's duty row is answerable on that and nothing else. The run was still
going when this one ended — read it, do not assume it."

It did not ship. The board's run record has security's re-fire at
2026-11-01T23:04:44Z with **`exit 124`**, `turns` null and `refusal` null — a
timeout, not a refusal. #657 is still a **draft** at head `fcefba6a`, last
updated 23:48:00Z: the run was killed before `gh pr ready`.

So #663's own restated gate decides it. "A row is answerable on the seat's
first slot that is not refused; a refused slot re-dates the gate; a slot the
retry rescues does consume it, **because a re-fire that ships is an observation
of the seat**." This re-fire did not ship, so security's Class A row is **not**
answerable on it and the gate is not consumed. #663's reading — "in recovery
behind #657, answerable today" — was correct when written at 23:34Z and is
falsified by the exit code.

**Then the instrument disagreed, three times, about the same slot.** Reading
`tools/cron_firing.py --day 2026-11-01 --seat alexandria-security`:

| reading | verdict | why it said that |
|---|---|---|
| 1 | `LOST?` — "that run opened no pull request either" | `_branch_prefixes` forms `alexandria-security` and `security`; the seat ships from **`sec/`**. The index was blind to it |
| 2 | `retried` — "the retry carried the cycle" | with `sec/` aliased, #657 became visible — and #657 is a **draft** |
| 3 | `LOST?` — "opened #657 and left it a draft, which no gate can reach" | right answer, right reason |

Reading 1 is the worst way for an instrument to be wrong: **the right answer by
a broken route**, which nothing finds until the day the answer should differ.
Reading 2 is what the first fix alone would have shipped, which is why the alias
could not go in without the draft check.

Both fixes, and the general form of each beside the instance:

- `index_is_blind_to(seat, pr_index)` — "this seat opened no pull request" and
  "I cannot see this seat's branches" are different claims and only the first is
  evidence. This is the distinction the file already draws for the firing record
  with `unseen`, applied one surface over. `ALIASES` repairs the one instance
  and is a maintained list, so it is explicitly *not* the remedy; the blindness
  check is, and it fires for the next seat whose convention nobody wrote down.
- A draft successor no longer promotes a slot out of `lost`. L-A32: no gate can
  reach a draft, and GitHub refuses to merge one at all. An index built without
  `isDraft` reads as **unknown rather than readied**, which is how the claim file
  is already read.

This is the same class as §3 one level down: `_branch_prefixes` was a design
never measured against the population it governs. One seat of ten ships from a
prefix no rule derives, and nothing had ever checked.

7 tests, both directions plus the absent-field case, so the draft check cannot
pass by refusing everything.

## 5. The three standing duties

- **Failure sweep (§2b).** Board run record, `runs_since_hours=12`,
  `runs_saturated: false`, 17 rows, **7 non-zero exits**. Six are the provider's
  weekly limit at turn 1 — one cause, already measured portfolio-wide in the
  relay entry filed before #663, nothing per-seat to triage. **The seventh is
  new and is the finding above**: security's `window:hook` re-fire, `exit 124`,
  `turns` null, **`refusal` null**. Worth naming against §2b's standing
  complaint that the refusal column is null on the refusals that cost work:
  here the null is *correct*, because this was a timeout and not a refusal. A
  sweep that reads null as "refusal, unrecorded" would have mis-filed the one
  row of the seven that mattered.
- **Outstanding with HQ (§3f).** #663 re-read the rows at 23:34–23:41Z and
  moved one to LANDED (HQ PR 545, merged 2026-11-01T23:30:15Z). This run
  re-ran the live tests on the open rows itself at **00:20Z** rather than
  inherit the reading: writer `max_turns = 225`, skill `270`, engineer `300`,
  this seat `200` with `cron = "0 1 * * 1"` — all consistent with the page's
  newest table, nothing moved in the intervening 40 minutes. **The unshallow
  row (decision 056, ask 1) is still open, and this run is first-hand evidence
  of it:** the clone arrived at 23:49:45Z with 2 commits and
  `is-shallow-repository: true`, and needed `--unshallow` plus a refspec widen
  before any branch could be compared — the same cost the page's last three
  readings record. No new ask carried up; the two offerings in §2 and §3 go to
  the company register through the relay rather than to HQ.

  **One correction to this run's own first read, kept because the shape is
  worth more than the fact.** The writer's cap looked like a row that had
  moved with nothing on `main` recording it: the table at the top of
  `docs/agents/hq-relay.md` reads `150` / "still open, 8 days" and disk reads
  `225`. That table is a **2026-10-26T14:15Z snapshot**. The page appends a
  dated table per pass and the newest one governs, and that one already
  carries the cap as LANDED on the 15:32:23Z daemon restart. So the row is
  closed and the page is right. **A register whose newest reading is at the
  bottom will hand its oldest reading to anyone who stops at the top**, and
  this run nearly filed that as a finding. The fix is not an edit to this
  page; it is to read the last table first.
- **Learning log (§6).** Below.

## 6. Learning log

- **A design is not a remedy until something counts its adoption.** Three
  instances in one repository in nine days, §3. The common defect is that the
  step after the design was addressed to a future run in prose.
- **Measure the remedy, not the rule.** The card had been Review-ready for eight
  days with its charter edit merged. The run's whole value came from asking
  whether the edit changed anything rather than whether it was made.
- **Build the instrument before quoting the number.** The hand probe said 90%
  bypass; the tool said 69%. The hand probe was wrong in the direction that
  made the finding sound better.
- **The right answer by a broken route is the expensive bug.** §4, reading 1.
- **A fix that moves an error to the other side is not a fix.** §4, reading 2.
  The alias alone would have shipped a false `retried`.
- **Read the newest table, not the first one.** The relay page appends per
  pass; its top table was eight days old and said the opposite of disk. Nearly
  a false finding, caught by reading further down.
- **A duplicate wake is only waste if the second run repeats the first.** #663
  left a four-item handoff list and item 1 was this run's cheapest contribution.
  A seat that leaves no handoff list cannot be continued.

### Still owed

1. **#531 can be unbundled** — the migration merges clean on its own. PM seat's
   branch and PM seat's call; a handoff, not an action taken here.
2. **`pending.md` has had no writer for eight days** and the owner-facing duty
   in `prompts/pm-agent.md` §1d is discharged by nothing until it does.
3. **Security's Class A row** is not answerable on the 2026-11-01 slot. Next
   un-refused slot, or #657 readied by someone.
4. **Card `8d1b81e8`** still waits on a standard nobody here owns.
5. **Class B** still waits on the owner's word, now eighteen wakes deep.
6. **`tests/test_cron_firing.py`** conflicts with #663, keep-both.
7. **`tools/board.py comment` has no `--data` flag**, and the board refuses a
   card comment whose prose carries ids: *"prose must not carry codes or PR
   numbers ('PR 531'); say what happened in words and put ids in the data
   field."* There is no data field on that command to put them in. So this
   seat's own rule — every verdict about a pull request names the head commit
   and the clock it was read at — cannot be satisfied on a card, and the
   comment posted says so and points at this note. #663 met the same refusal on
   the relay page, where a data field does exist. Small, and a gap rather than
   a defect in either surface; recorded here rather than filed, because one
   missing flag is not yet a class.

   The second refusal is worth copying for its own sake: *"prose must be
   scannable: one thought per line, a blank line between thoughts; a block over
   420 characters is not."* Both refusals named their own rule, which is §2a-0's
   standing instruction — **when a surface refuses you, read the refusal** — and
   twice tonight it was the whole answer.
