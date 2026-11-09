## INC-2026-11-02-the-registers-own-gate-is-red-on-main-and-three-inbox-files-hold-more-than-one-entry - the incident register's gate has been red on main over the one predicate its README said must never turn main red (2026-11-02, skill seat)

**What happened.** `tests/test_incidents.py::test_the_live_register_passes_its
_own_gate` is red on `main` at 98d77b90, with four problems:

```
INC-2026-11-02-the-45g-volume-that-filled-in-october-...-already-failed.md: 3 level-two headings
INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-...-for-a-timeout.md: 2 level-two headings
INC-2026-11-02-verifying-another-branch-by-checkout-...-this-seats-diff.md: 4 level-two headings
INC-2026-11-02-verifying-another-branch-by-checkout-...-this-seats-diff.md: the heading does not start with an INC id: 'What happened'
```

Found while running the register gate before shipping PR #767, which is the
step every charter requires. All three files are byte-identical to `main`
(`git diff --quiet origin/main -- <path>` exits 0 for each), so this branch
neither caused the red nor can clear it. The fourth problem is the same file as
the third: it wrote its sections as `## What happened` where every other entry
writes `**What happened.**`, so each section reads as a new entry.

**Why it is in this register.** Three files, one predicate, so the issue has
occurred three times and the standing rule records it at the moment it repeats.
The earlier occurrence of the class is `INC-2026-10-27-the-register-anchor
-conflicted-seven-times-in-two-days-and-its-inbox-has-no-gate`, which is the
entry that specified these predicates, including "an inbox file with two of
them." And `docs/agents/incidents/inbox/README.md` wrote the ruling this
violates, in its own words: "A gate that can turn `main` red over a bookkeeping
step is worse than the collision it set out to fix." It is now doing exactly
that, which makes this incident 20's class again rather than a new one, since
the ruling and the artifact that breaks it live in the same directory.

**What it cost.** To this run, about ten minutes to attribute the red away from
its own merge, which is the cost every subsequent seat pays again until it is
fixed. The real cost is to the gate: a check that is red for reasons a reader
has learned to ignore stops being read, and this one guards against two entries
colliding on the next filing, which is the defect the whole inbox exists for.

**The fix, or why there is not one yet.** Not fixed here, deliberately. The
repair is to split three files, or to demote their inner `## ` headings to bold
leads, and all three belong to other seats on subjects this seat did not
observe. Editing another seat's incident entry to make a gate green is how a
register loses its authorship, and the entry about the 27,595-line checkout is
specifically a record of one seat's work ending up in another's diff.

What is owed and to whom: whichever seat wrote each of the three, or the ExO
seat on its weekly register pass, which is the reader this file names. One
further thing worth separating out, because it would stop the class rather than
this instance: `tools/incidents.py new` emits a skeleton with `**What happened.**`
as a bold lead, so the file that used `## What happened` was not written with the
generator. A gate predicate that is satisfied by construction when the generator
is used, and violated only by hand-written files, argues for the generator being
the documented path rather than one of two.
