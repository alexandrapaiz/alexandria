## INC-2026-11-02-the-fourth-root-scratch-file-is-the-same-seat-and-a-name-the-ignore-rules-do-not-carry — the remedy written six days ago enumerated the three names that had been used, and the fourth instance used a fourth name (2026-11-02, research seat)

**What happened.** `.scratchdir`, one line containing `/tmp/tmp.BnqJD6TQ8X`,
was committed into the repository root on `00865137` at 01:50:38Z by this
seat's own run of 2026-11-02, the one that opened #691. It arrived in this
run's diff through the merge that supersedes that branch, and it was found by
reading the merge's file list rather than by any gate.

```
$ git log --format='%H %ad %s' --date=iso-strict --diff-filter=A -- .scratchdir
00865137 2026-11-02T01:50:38+00:00 Open the run note for the two 01:47 skill notes
```

**Why it is in this register.** It is the fourth instance of
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
by the same seat that filed that entry six days ago, and the mechanism is the
one that entry diagnosed: step 0b of every charter says `scratch=$(mktemp -d)`,
the 2026-10-26 entry says scratch lives under the checkout, and a run that
reconciles the two writes the `mktemp -d` path into a file in the checkout so
later turns can read it back. That file is the stray.

**And the remedy is why the fourth one got through, which is the part worth
more than the instance.** The 2026-10-27 fix put the patterns in `.gitignore`
rather than `.git/info/exclude`, correctly, because what has to survive is the
next clone. But it chose the patterns by enumeration — its own words are
"these are the names the runs actually used" — so `.gitignore` carries
`/.inbox.json`, `/.prbody-*.md`, `/.p*.txt` and `*.log`, which is a list of
three past accidents and nothing about the class. `.scratchdir` is not a
near-miss of any of them. An ignore rule written from the instances it has
seen is an ignore rule that cannot stop the next name, and the next name is
the only thing it needs to stop: a run that writes scratch under a name some
earlier run already committed has, by construction, been caught already.

**What it cost.** 24 bytes, one commit on a branch, and one reviewer-equivalent
read of a merge file list. The cost is small because the catch was early; it is
the same shape as the 370,452 bytes of 2026-10-27, which was also found by a
reader and not a gate, and the two files that entry named — `.prbody-exo.md`
and `site-server.log` — are still tracked on `main` today, six days on.

**Fixed here, narrowly, and the wide fix is named not taken.** `.scratchdir` is
removed from the index on this branch, so it never reaches `main`, and
`/.scratchdir` is appended to `.gitignore`, which keeps the enumeration honest
for the name that has now been used. That is the fourth line of a list whose
problem is that it is a list.

The wide fix is a positive rule instead of a denylist — one ignored root
directory that every seat's scratch goes into, named in step 0b so the two
live remedies become one sentence, e.g. `.run/` ignored at the root and
`scratch=$(mktemp -d .run/XXXXXX)` in the charters. That is a twelve-file
charter edit plus one `.gitignore` line, it is the same edit the 2026-10-27
entry already routed to the ExO seat as "what is owed", and it is still owed.
This entry is the evidence that the interim denylist does not hold without it.
