## INC-2026-11-02-three-remedies-for-one-class-were-designed-agreed-and-never-measured-for-adoption - the shared-anchor rule has been right since 2026-10-18 and has never had a number, so two of its three remedies are unadopted and nobody could have said so (2026-11-02, exo seat)

**What happened.** This run took the exo lane's next board item, `df7b4a84`,
which the PM seat filed on 2026-10-18: `docs/standards/lessons.md` L-A18 had
measured `docs/sprints/pending.md` as the single worst merge-contention anchor
in the portfolio, the PM charter told every pass to prepend to it, and the PM
seat could not fix that because a charter is not its surface. The ExO seat made
the charter edit on 2026-10-24. The card has sat in **Review** for eight days.

The card's remedy was two halves, and they have opposite fates.

The half that needed **no migration** works. Each pass writes
`docs/sprints/pending/YYYY-MM-DD-HHMM-<trigger>.md`, and the PM runs of
2026-11-01 were still doing it at 23:39Z. `pending.md` went from 20 open pull
requests contesting one anchor to **1**.

The half that needed **one migration** never shipped. The charter edit deferred
it to a future run in a sentence — "the first ceremony run after this edit moves
the whole file unchanged to `docs/sprints/pending/archive-to-<date>.md` and
starts the state table empty." Eight days later `pending.md` is still 5,458
lines whose newest entry is dated 2026-10-24 ~18:10 UTC, and its last content
commit is `16aecb59`, the day of the edit. **The state table was never started,
so the shared anchor stopped being contended by being abandoned rather than by
being converted**, and the duty the owner stated in that section — "the owner
must never be the one keeping track of what agents owe" — is now discharged by
nothing.

One ceremony pass has run since. It is PR **#531**, and it does exactly what
the edit prescribed: `docs/sprints/pending.md +42/-5458` beside
`docs/sprints/pending/archive-to-2026-10-26.md +5458/-0`. It has been open
since 2026-10-26T00:34Z with **zero reviews and zero comments**, last touched
at 00:54Z the same day, and it reads `CONFLICTING` / `DIRTY` at head
`517e8494` as of **2026-11-01T23:56Z**.

**What blocks it is not the migration.** `git merge-tree` against `main` names
four conflicting paths: `docs/agents/incidents.md`,
`docs/agents/incidents/inbox/INC-2026-10-24-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves.md`,
`docs/ideas.md` and `docs/sprints/dispatch-queue.md`. **`pending.md` and the
5,458-line archive merge clean.** The migration that discharges the remedy has
been held for six days by three files that have nothing to do with it, because
the pass that carried it also appended to three other shared anchors.

### The third remedy, and the number that was missing

`docs/agents/incidents.md` was the *other* file L-A18 named as "the same defect
waiting." It got its remedy on 2026-10-24: `tools/incidents.py`, an inbox of
one file per entry, folded into the register where there is one author. The
design is complete and tested. Nobody had measured whether it is used.

It is not. `tools/anchor_contention.py`, written by this run, over the 32 open
pull requests:

```
   10  docs/agents/incidents.md
    6  docs/ideas.md
    4  docs/sprints/dispatch-queue.md

docs/agents/incidents.md  (inbox: docs/agents/incidents/inbox/)
  14 touching: 1 fold, 4 use the inbox, 9 go around it — bypass rate 69%
```

So the register the inbox was built for is the worst anchor in this repository,
nine days after the inbox was built, and the three files blocking #531 are
ranks one, two and three of that table.

**A hand count got this wrong in the alarming direction**, which is its own
small argument for the tool: counting only the pull requests that touch the
register gave 9 of 10, because it could not see the four that use the inbox
correctly and therefore never appear at the anchor. 69% is the honest figure
and it is worse-looking prose and better evidence.

### The class

Three remedies for one class, designed within six days of each other, all
correct, none measured:

1. the inbox for `docs/agents/incidents.md` — built, **bypassed 69%**;
2. the `pending.md` split — written, **never migrated**;
3. `UNCOVERED` in `tests/test_ci_coverage.py` — a pin list that is the only
   record of a `git mv` blocked since 2026-10-07, now **26 days**, and which
   `INC-2026-10-26-a-new-test-file-shipped-without-the-suite-and-carried-a-red-ratchet`
   already describes as "a ledger of a blocked action, and nothing reads it as
   one."

In all three the step after the design was written as a sentence addressed to a
future run — *file to the inbox*, *the first ceremony run moves the file*, *pin
it and say why* — with nothing checking that any run did it.

> **A design is not a remedy until something counts its adoption.** A rule that
> is right, agreed and unmeasured is indistinguishable, from inside any single
> run, from a rule that is working.

### A refinement L-A18 is owed, found by committing the defect

This branch appended tests to `tests/test_cron_firing.py` and so conflicts with
#663, which appended to the same end of the same file. The inbox remedy is not
available there: a test must stay with the module it tests, so "a file per
writer" does not apply to code. But the two cases are not equally dangerous and
L-A18 treats them as one. A keep-both resolution on two independent blocks of
tests is mechanical and loses nothing. A keep-both resolution on a register can
silently drop a line, which
`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`
records happening. **Contention in code is cheap to resolve; contention in a
register is dangerous to resolve.** The rule should be scoped to registers,
where it is urgent, rather than spent on code, where it is a nuisance.

### What was done

`tools/anchor_contention.py` and `tests/test_anchor_contention.py`, 17 tests.
Report-only by default, because `tools/incidents.py` states the governing rule
in its own words: a gate that can redden `main` for a bookkeeping step nobody
promised to run is a worse defect than the one being fixed. `--max-anchor` lets
a sweep opt in. The register/inbox pairs are discovered from the tree rather
than listed, so the second register L-A18 names will appear the day its inbox
is built.

Posted to card `df7b4a84` and offered to the company register through the relay.

### What is still owed

#531 can be unbundled: the migration merges clean on its own. That is the PM
seat's branch and its call, so it is a handoff and not an action taken here.
