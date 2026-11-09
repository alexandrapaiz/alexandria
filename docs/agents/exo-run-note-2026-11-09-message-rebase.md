# ExO run note — 2026-11-09 (message, rebase)

Branch `alexandria-exo/2026-11-09-message-rebase`, PR #894. Suffix `rebase`
because `alexandria-exo/2026-11-09-message` and twelve other suffixes of this
date are already taken, and the run-note filename carries the branch's suffix
so this wake does not clobber an earlier wake's note.

**Mode: wake run.** Trigger `message`, wake text names PR #886's merge and a
handoff, not a cron slot and not a capacity re-fire of a cron log, so §0 puts
this in the wake-run mode: the event, three standing duties, one improvement.
**Not done, and named here so the pull request need not be read to know it:**
the register sweeps (§3d, §3b), the unowned-duty hunt, the public-claim sweep
(§3g), the queue re-verification, the weekly cycle. `cycle-taken:` not written;
next due slot 2026-11-16T01:00Z; nineteenth consecutive wake to decline it.

## What the event asked and what I took

Two events. PR #886 merged, with *continue with the next item in your lane on
the board, and say what I took*. And a handoff from `alexandria/pm`
(`3afd19ed`, 08:24:53Z) saying the held charter draft on #879 needs a hand
rebase.

**The lane's next item is card `2ee0f59f` and none of it is takeable today.**
Class A is closed but for market, re-dated to 2026-11-13T11:00Z, four days out.
Class B is with the owner and may not move because it widens this seat's own
budget. Class C is class C. This is the fifth consecutive wake to read that
card and find no open gate; I commented that on the card rather than only here,
because five run notes saying the same thing is not a record a card's reader
sees.

So I took the handoff, and then one improvement out of it.

## 1. #879 resolved by hand, before the clock rather than after it

PM's handoff was right in every particular and I re-measured it rather than
trusting it: #879 at `9c9bec42` against `main` `6b63a3fa` conflicted on
`exo-owed.md`, `hq-relay.md`, `learning-log.md`.

It said to expect to resolve them *when the ask's clock runs out* (2026-11-11).
I did it now, on `docs/standards/pm.md` §864's own rule that **a decision that
waits grows** — every window merges to stay mergeable and every merge imports
what the other branch carried; §864 measures a two-file question becoming a
twelve-file question in six days. Waiting does not hold a register conflict
still on a file this seat appends to every wake.

Resolution, and nothing is blended:

- `exo-owed.md` is a **numbered** register and both sides allocated row 14.
  Main's rows 14 and 15 are the published side and keep their numbers; this
  branch's row became **16**, and the prose below it that named row 14 was
  renumbered with it.
- `hq-relay.md` and `learning-log.md` are chronological appends. Both sides
  kept, the branch's 07:2xZ section ahead of main's 08:0xZ section, which is
  the order both files already run in.

**#879 reads `MERGEABLE` / `CLEAN` at head `20567a62`, taken 2026-11-09T08:44:26Z.**
`prompts/pm-agent.md` is byte-identical across the merge, so the charter diff
the owner ask `cdfa18e3` is about is unchanged — the fact that made resolving
early safe, which is why it is stated rather than assumed.

**The one cost, named rather than left to be found.** The ask was posted against
`9c9bec42`; the head is now `20567a62`. Any pin the ask carries is stale, and I
moved it, so I sent PM the new head in the same board reply instead of leaving
the receiver to discover it.

## 2. The improvement: this seat's merge debt is one mechanism, and the cure is in the parent

Measured, every open PR of this seat against `main` `6b63a3fa` at
2026-11-09T08:42:31Z: **7 of 8 conflict, and every conflicting file is an
append-only register under `docs/agents/`** — `hq-relay.md` in six,
`learning-log.md` in five, no code file, no charter, no test. The full table is
in this run's learning-log entry.

`pm.md` §864 names the cure and it is not a merge driver (L-A49 refuted all
three `.gitattributes` arms, and `union` corrupts entries): it is HQ's
`tools/merge-register.py`, which merges entry by entry. **This repository has
no copy under any name, no `.gitattributes`, and no registered merge driver.**

**Then I ran it instead of recommending it, and it refused** — correctly, on a
defect in our own register: `learning-log.md` on `main` carried
`## 2026-09-19 — Fifth run …` **twice**, lines 463–636 and 908–1086, bodies
differing by exactly the two lines recording the supersession, the stale copy
also out of date order. Fifty-one days old, in the file §2 makes the first thing
every run of this seat reads. Registered as
`INC-2026-11-09-the-exo-learning-log-carried-one-entry-twice-for-fifty-one-days-and-the-instrument-that-would-have-caught-it-is-the-one-it-blocks`.

Repaired here, by content match and not by line number, with assertions on both
sides of the edit. Then swept all five of this seat's registers for duplicate
entry keys: **1 instance, and it is this one.**

**And the sequence is the finding.** With the repair on a branch only, the
refusal does not disappear, it moves to `theirs` — so the vendoring cannot pay
until the repair is on `main`. Both directions verified: refusal while either
side carries the duplicate; **exit 0 and output byte-identical to `main` plus
this run's entry** once both sides are repaired. **Repair → merge → vendor.** A
run that vendors first reads a correct refusal as a broken tool.

**Vendor from HQ's head, not from Ursa's pin.** Ursa vendored the tool
2026-10-24T01:46:01Z at sha256 `aead15d7def3ff46…`, 523 lines — HQ's content
from 2026-10-18T12:24:51Z. HQ has taken **four** commits to that path since and
now reads `8ff0a4d0…`, 599 lines. The first of the four, `9a12e957` at
2026-10-24T13:38:37Z, **eleven hours fifty-two minutes after the pin**, is *"a
heading inside a fenced code block is not an entry start"* — a correctness fix
to the exact entry-boundary parser the pin froze, and our registers are full of
fenced blocks containing `#` lines.

`pm.md` §864's *"byte for byte identical"* **was true when written**: the sha it
publishes is still Ursa's file today and was HQ's file on the day of the pin.
The repair is a date beside the hash, not a retraction. The general form:
**a provenance sentence that records a hash with no date reads as current
forever.**

Routed and not reached into: vendoring is engineer surface. **Owed row 17**,
numbered 17 because row 16 is allocated on #879's unmerged branch, and the hole
is explained at the foot of `exo-owed.md` rather than left for a reader.

## 3. Standing duties

- **§2b failure sweep.** `?day=2026-11-09` at 08:43Z: 224 runs, 196 finished,
  10 running, 18 failed, 16 `timeout`, **no refusal clause**. `?day=2026-11-08`:
  39 of 70 refused, 56%, six windows 00:06Z→18:20Z, 21.4 h idle, all the
  monthly spend cap. 3,377 `run.end` rows. Both already-open asks, neither
  re-asked — a second quiet day is not evidence the cap was raised, and this
  seat has no surface that reads the cap's value.
- **§3f Outstanding with HQ.** A delta table on `hq-relay.md`, plus the
  vendored-copy pass §3f's own command block asks for: `lessons.md` pinned
  `e3f30ec7` against HQ head `37fe1254`, **15 commits behind**; `pm.md` pinned
  `becae2c2` against `ea002e4b`, 1 behind. Both are the centralizer's sync
  lane's lag under ADR-011, recorded as a measurement so the next run does not
  rediscover it as a finding. **Nothing asked upward this run**, because
  nothing found is HQ's to decide.
- **§6 learning-log entry.** Written, and it is the long form of this note.

## What the next run should know

1. **#879 is mergeable at `20567a62`**, held only by owner ask `cdfa18e3`, 48
   hours expiring 2026-11-11T08:05Z. Do not re-resolve it; re-read its head.
2. **Owed row 17 has a prerequisite and it is this pull request.** Vendoring
   before the repair merges produces a refusal that looks like a broken tool.
3. **This branch will conflict with #879 if #879 merges first**, on the same
   three registers — the finding demonstrating itself a third time inside one
   run. Chronological appends keep both sides in time order; the numbered table
   keeps the published side's numbers.
