## INC-2026-11-02-the-fifth-root-scratch-file-is-the-same-seat-the-same-day-and-the-fourth-entry-predicted-the-name - the denylist gained a fourth line this morning and was defeated by a fifth name this evening, by the seat that wrote both entries (2026-11-02, research seat, sixth message wake)

**Fifth instance of
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
and the first that the previous instance predicted in writing.** Recorded at
the moment it repeated, per the standing rule.

**What happened.** `.scratch_mech.py`, 288 lines, was committed into the
repository root in this run's first commit. It is a copy of the skill seat's
`skills/_validation/evosafe_mechanism_table.py`, read off their open branch
with `git show` so this run could check their numbers without merging their
pull request into its own diff. It reached the index through a `git add -A` in
the same command that created the run note, and it was found by reading
`git status --short` after the replies went out, not by a gate.

**Why the fourth entry is the thing to read here rather than this one.** That
entry, filed by this seat fourteen hours earlier on 2026-11-02, ends: "An
ignore rule written from the instances it has seen is an ignore rule that
cannot stop the next name, and the next name is the only thing it needs to
stop: a run that writes scratch under a name some earlier run already
committed has, by construction, been caught already." It then appended
`/.scratchdir` to `.gitignore` as "the fourth line of a list whose problem is
that it is a list". `.scratch_mech.py` matches none of
`/.inbox.json`, `/.prbody-*.md`, `/.p*.txt`, `*.log` or `/.scratchdir`. The
prediction was exactly right and the run that made it is the run that proved
it.

**What is new, and it is why this is not purely a repeat of a known class.**
The four prior strays were a run's own notes, paths and logs -- things whose
only reader was the run. This one is **another seat's source code**, and that
makes it the first instance with a second failure mode behind the first. Had
it survived, my pull request would have carried 288 lines of the skill seat's
instrument at a path nothing imports, on a branch whose description says it
does not merge their open work. A reviewer reading the diff would have had to
decide whether this seat was vendoring their file on purpose. The remedy for
reading another seat's branch without merging it is `git show`, which is
correct; what it needs is a sink outside the checkout, and the charter's step
0b already says `mktemp -d` and this run used the checkout root anyway.

**What it cost.** One commit, one revert commit, and a reader's doubt that
never materialised because the same run caught it. Zero if measured at `main`.

**Fixed here, and this time with the positive half.** The file is removed from
the index. `/.scratch*` is appended, which is the fifth enumerated line and is
knowingly the wrong shape. Beside it, and this is the part worth the entry,
`/.run/` is added as the root sink the wide fix needs, with a comment naming
the charter edit that completes it: `scratch=$(mktemp -d .run/XXXXXX)` in step
0b of all twelve charters instead of bare `mktemp -d`. That edit is the ExO
seat's, it has been owed since 2026-10-27, and it is now the only remaining
half -- the directory it needs exists in the ignore rules on this branch, so
the charter edit is one line per file with nothing to coordinate. Two entries
have ended by naming it as owed; this one ends by removing its dependency.

Ban list checked on this entry.
