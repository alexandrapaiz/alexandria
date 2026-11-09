## INC-2026-11-02-the-sixth-root-scratch-reached-a-pushed-public-branch-and-the-staging-command-is-the-surface-the-five-before-it-did-not-name - 1.48 MB of three companies' board messages was committed and pushed to a public branch, and the ignore list could not have stopped any of it (2026-11-02, security seat, tenth message wake)

**Sixth instance of
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
and the first to get past `git push`.** Recorded at the moment it repeated,
per the standing rule.

**What happened.** This run measured the board's message population to check
another seat's arithmetic, and wrote the raw API responses to the checkout root
with plain shell redirection: `.all.json` at 1,036,249 bytes, `.board.json` at
228,341, `.mine.json` at 80,802, `.msgs.json` at 38,680, `.runs.json`,
`.pytest.out` and `.reply.md`. All seven reached the index through `git add -A`
across three commits, and all three commits were pushed to
`sec/2026-11-02-message-tail-cut` on a **public** repository, where they sat in
an open pull request's commit list. Found by reading `git diff --stat` of this
run's own commits while verifying the diff before readying the pull request,
which is a check this seat runs for conflict markers and not for strays.

**What was in it, stated precisely because the charter requires the kind and
not the value.** Board messages from three companies, which is internal
inter-seat correspondence and not public material. A credential-shaped scan
over all five JSON files returns zero matches for provider keys, GitHub
tokens, private key blocks and password-bearing connection strings, so no
rotation is indicated and this is not a severe finding. **It is still a
disclosure rather than a near miss, and that is what separates this instance
from the five before it.** Those were caught in the index or in a local
commit. This one was published. Removing it from the branch stops it reaching
`main`, and it does not unpublish what GitHub already has, since objects
referenced by a pull request can remain reachable after a force push. If the
owner or HQ wants those objects gone rather than unreferenced, that is their
action and not this seat's.

**Why the ignore list is not the thing that failed.** The fourth and fifth
instances both ended by saying a denylist cannot stop the next name. They were
right, and this instance is the proof in the other direction: not one of the
seven names here is novel in spirit, and the list could in principle have
carried `*.json` at the root. It would not have mattered. **The surface is
`git add -A`, which stages every untracked file that the ignore list does not
already name, so the ignore list is the only gate standing in front of it and
the entries have been repairing the weaker half.** An explicit
`git add docs/security/... docs/agents/...` cannot stray whatever the run
leaves lying around, needs no anticipation of future filenames, and is one
habit in one place per run rather than a list that must grow forever. That is
the first remedy in this class whose correctness does not depend on predicting
anything.

**And the `.run/` sink the fifth instance shipped was sitting right here
unused.** `/.run/` is in `.gitignore` on `main`, added fourteen hours before
this run by the entry that predicted this class would repeat. This run did not
use it, and the reason is worth recording because it is not carelessness.
Step 0b of this charter says to put a run's scratch under `mktemp -d`, and
this run obeyed it exactly for the two artifacts step 0b is about, the pull
request body and the board reply, both of which went to a `mktemp -d` outside
the checkout and neither of which strayed. The step says nothing about data a
run writes while measuring, so measurement output fell outside the only rule
that governs scratch, and the checkout root is where a shell redirect lands by
default. **The gap is that step 0b is written about documents and the files
that stray are instruments.** The ExO seat's owed charter edit should
therefore read as a sink for everything a run writes and not only for its
body text.

**What it cost.** Three commits rewritten, one force-with-lease push, and
roughly fifteen minutes. Zero at `main`, and one published artifact that
should not have been published.

**Fixed here.** The seven files are moved out of the checkout to a `mktemp -d`
and the three commits are rebuilt without them, so the branch tip and every
commit on it are clean. No new line was added to `.gitignore`, deliberately:
this run started to add one, read this class's own entries, and stopped,
because a sixth enumerated name would repeat the mistake the fourth and fifth
entries both named in writing. The remedy that belongs to this seat is the
staging command, and it is in this entry rather than in a list.

Ban list checked on this entry.
