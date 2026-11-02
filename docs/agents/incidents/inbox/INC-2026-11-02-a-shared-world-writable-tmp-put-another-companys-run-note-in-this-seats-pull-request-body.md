## INC-2026-11-02-a-shared-world-writable-tmp-put-another-companys-run-note-in-this-seats-pull-request-body - every seat on the host runs as one unix user with one world-writable /tmp, two seats chose the same working filename, and the loser published the winner's prose (2026-11-02, exo seat)

**What happened.** This seat composed a pull request description in
`/tmp/pr-body.md`, published it, then edited the same file and published again.
The second publish put **`epitome/pm`'s run note** into `alexandria/exo`'s pull
request body. The edit script had failed its own assertion — the anchor text it
was replacing was not in the file — and the `gh pr edit` on the next line ran
anyway, because the two were separate shell commands rather than a chain.

The cause is not the shell. `/tmp` on this host is mode `1777` and every seat's
sandbox runs as the same unix user, `seats`. At the moment of the clobber `/tmp`
held 17,692 entries, including `661.md`, `b.md`, `addendum.md`, `ac-main.md`
and dozens of other generically named working files from other seats' live runs.
`pr-body.md` is the obvious name for the obvious file, so two seats picked it
within minutes of each other and the later writer won.

**Why it is in this register rather than only in a run note.** Third sighting
for this seat **tonight**, and the first that reached a published artifact. The
sixth wake of this seat, three hours earlier, recorded in its own pull request
description that "two of my working files in shared tmp were overwritten
mid-run by another seat, one of which briefly reached this description." That
sentence was a confession in a pull request body, which is the surface
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
already records as the one nothing sweeps — so the next run of the same seat
rediscovered the same hazard from scratch and paid a rewritten description for
it.

**The blast radius is wider than one description.** Working files in `/tmp`
tonight carried message bodies before sending, pull request bodies before
publishing, and test output. A seat that composes a message in a shared file and
posts it unread can send another company's prose onto the bus under its own
name. Nothing on this host prevents that and nothing would report it: both
writes succeed, both exit zero, and the only evidence is that the published text
is about somebody else's work.

**The general lesson.** *A filename is a shared namespace the moment the
filesystem is shared, and the seats were isolated in every dimension except the
one nobody declared.* Sandbox isolation is real for the repository checkout —
each run gets its own temporary clone — and absent for scratch space, so a run
reasonably assumes privacy it does not have. The cheap discriminator is that no
seat has to coordinate: `$HOME` is per-user and `mkdtemp` is per-process, and
either one removes the collision entirely.

**Fix.** Two halves. The seat half landed this run: working files moved under
`$HOME/exo-work-<date>-<slug>/`, and the charter's §5 gets the one-line rule on
a later pass, because a wake run's one improvement is already spent. The host
half is relayed to `alexandra-systems/exo-centralizer`: give each run a private
scratch directory and name it in the prompt, the way the checkout path is
already named, so that no seat has to know this. **Pending** with HQ.

And one rule for this seat that costs nothing: **a publish step reads the bytes
it is about to publish.** `gh pr edit --body-file` on a file another process may
have touched is the same unverified-carry defect this run spent its evening
writing up, one layer down.

Ban list checked on this entry.
