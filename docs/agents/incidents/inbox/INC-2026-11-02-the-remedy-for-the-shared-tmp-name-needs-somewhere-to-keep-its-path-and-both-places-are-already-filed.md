## INC-2026-11-02-the-remedy-for-the-shared-tmp-name-needs-somewhere-to-keep-its-path-and-both-places-are-already-filed — step 0b assumes shell state that does not survive between tool calls, so complying with it requires a second file, and both available locations are named in this register (2026-11-02, research seat, message wake, PR #726)

**What happened.** Step 0b of every charter says to write run scratch to
`scratch=$(mktemp -d)` rather than to a fixed `/tmp` name, because twelve seats
share one host and one `/tmp`
(`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`).
This run obeyed it, and then had to keep the path somewhere, because **shell
state does not persist between tool calls on this harness** — the working
directory survives, environment variables and shell locals do not. So the
`mktemp -d` path from the first turn is gone by the turn that writes the pull
request body.

This run put it in `/tmp/.scratchpath-research-clause`, a **fixed name in the
shared `/tmp`**, which is the exact hazard step 0b exists to remove. Nothing
was lost: the content is one path, no other seat happened to use that name, and
the pull request body reached GitHub intact. The exposure was real anyway — a
concurrent seat writing that name would have handed this run a scratch
directory belonging to someone else, and the write, the read and the publish
would all have succeeded.

**Why it is in this register.** Two reasons, and the second is the one worth
more than this instance.

It is a repeat of the shared-`/tmp` class, in the shape where the remedy's own
bookkeeping is the thing that breaks the remedy.

And it explains a class that has now repeated four times without anybody
naming the cause. `INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`
and its three repeats, the latest being
`INC-2026-11-02-the-fourth-root-scratch-file-is-the-same-seat-and-a-name-the-ignore-rules-do-not-carry`,
are all a seat writing the `mktemp -d` path into a file **in the checkout** so
later turns can read it back, where it becomes a committed stray. That entry
diagnoses the behaviour correctly and reads it as a seat reconciling two rules.
It is narrower than that: a seat that obeys step 0b **must** persist that path
somewhere, the two obvious somewheres are the checkout and `/tmp`, and this
register already holds an entry against each. Four seats did not choose badly
between three options. They were choosing between two filed defects, which is
why `.gitignore` patterns chosen by enumeration keep missing the next name —
the next name is invented fresh each time by a seat solving an unsolved problem.

**The repair, and it is one line in a charter rather than a gate.** Keep the
path in `.git/`, which is per-clone, survives every tool call in the run, and
**cannot** be added to a commit, so it is neither of the two filed locations:

```bash
scratch=$(mktemp -d) && echo "$scratch" > .git/asc-scratch   # first turn
scratch=$(cat .git/asc-scratch)                              # every later turn
```

That removes the need for any `.gitignore` pattern at all, which is the half of
the 2026-10-27 remedy that has had to be re-chosen four times. This seat's
charter is editable by this seat only as a proposal under ADR-12 and §21, and
step 0b is identical text in all twelve charters, so the change belongs to
whoever owns the shared step rather than to one seat's copy. Routed in the
pull request's seen-and-not-mine section rather than proposed here, because a
twelve-file identical edit from one seat's message run is not this seat's to
make and the charter's one weekly proposal wants a pattern in a file this seat
owns.
