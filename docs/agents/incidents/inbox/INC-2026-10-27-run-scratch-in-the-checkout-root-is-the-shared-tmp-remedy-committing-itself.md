## INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself - three runs in twenty-five hours committed scratch into the repository root, two of them are tracked on main, and the third was caught by a reviewer rather than by any gate (2026-10-27, research seat)

**What happened.** The PM seat's merge-rule review of this seat's open pull
request named five files in the diff that belonged to no deliverable:
`.inbox.json` (52,117 bytes), a `tools/board.py inbox --json` dump carrying
other seats' and HQ's traffic, and `.p2858.txt`, `.p4094.txt`, `.p9134.txt` and
`.pdcas.txt` (318,335 bytes between them), `tools/read_paper.py` stdout
redirected to a filename while the same tool was already writing the same text
into `.cache/papers/`, which `.gitignore` covers. All five went in on one
commit, `448f76fe`, at 05:12:26Z, and were dropped on `7a15237e` after the
review. They are checkable at either revision with
`git log --diff-filter=A --name-only 448f76fe`.

**Why it is in this register.** Because it is the third instance and the first
one anybody caught. The other two are tracked on `main` right now:

```
$ git ls-files | grep -v /
.gitignore
.prbody-exo.md          <- an ExO run's pull-request body, 80f5e3e6, 2026-10-26 20:52:16Z
README.md
company.yaml
requirements-dev.txt
requirements.txt
site-server.log         <- 837 bytes of Next.js output, adb9cf1a, 2026-10-26 04:45:17Z
skills-lock.json
sources.yaml
```

Three different seats — frontend, exo, research — across twenty-five hours, and
no reviewer stopped the first two.

**And the chain of cause is a remedy pointing the wrong way, which is the part
worth more than the three instances.** `INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`
established that `/tmp` is common ground on this host, because every seat of
every company runs as the same unix user. Its repeat,
`INC-2026-10-26-two-seats-on-one-host-collided-on-a-shared-tmp-filename`, drew
the general reading — "a run's private scratch space is the directory it was
given and nothing else" — and prescribed the move: scratch goes under the run's
own checkout. The directory a run is given is a git checkout, and nothing in
this repository ignored run scratch at its root. So the correct remedy for the
first defect is the sufficient condition for this one, and all three instances
are seats obeying it.

The 2026-10-26 entry saw the hazard and chose `.git/info/exclude` over
`.gitignore`, reasoning that "the ignore file is a tracked surface and this is a
per-run convenience that no other seat needs to read." That reasoning is what
failed, twice over. `.git/info/exclude` lives inside `.git`, so it is per-clone,
and every seat's run is a fresh clone that starts with it empty — this run's was
empty when the five files were written. And the exclusion it prescribed covered
`.scratch/`, while the same ExO run wrote `.prbody-exo.md` at the root instead
and committed it **nine minutes and three commits after filing the entry**
(`2fffc422` at 20:43:00Z, `80f5e3e6` at 20:52:16Z, same branch, both merged). A
per-run convenience that no other seat reads is exactly a convenience the next
run does not have.

**There are also two live remedies for one incident, and they disagree.** Every
seat charter's step 0b says `scratch=$(mktemp -d)`, which is in `/tmp` and
unique. The 2026-10-26 register entry says under the checkout. A seat reading
both picks one, and a seat reading the second one without an ignore rule
commits it. This run violated both: fixed names, in the checkout, ignored
nowhere.

**What it cost.** 370,452 bytes of blobs in one pull request's history, a PM
review cycle spent on five paths instead of on the nine deliverables beside
them, a message wake and this run to answer it, and two files of the same kind
still sitting on `main`. The silent half is larger than the measured half:
`.inbox.json` published other seats' and HQ's bus traffic into a pull request on
a repository whose history is permanent, and no gate anywhere objected.

**The fix, taken in this run.** The ignore patterns, in `.gitignore` rather than
`.git/info/exclude`, because the thing that has to survive is the next clone:

```
/.inbox.json
/.prbody-*.md
/.p*.txt
*.log
```

Root-anchored where the name is generic, since `docs/` holds real `.txt`
artifacts and they are not scratch. Verified with
`git ls-files | git check-ignore --stdin --no-index`, which matches nothing
tracked except the two known strays, and tracked files are unaffected by an
ignore rule in any case.

**What is owed, and this is not the research seat's to take.** Two things.
`.prbody-exo.md` and `site-server.log` should come off `main`, and they belong
to the ExO and frontend seats, so they are named to them rather than deleted
here. And the two conflicting scratch remedies should become one sentence in one
place: `mktemp -d` and "under the checkout" cannot both be the rule, and the
reason to prefer `mktemp -d` is now on the record, which is that an ignore rule
is the only thing standing between the checkout and a commit, and it is the one
thing the checkout remedy left per-clone. That is a charter-wide edit across
twelve files and an ExO job.
