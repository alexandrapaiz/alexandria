# Security and debug sweep, 2026-11-02 (message wake, supply-chain pass)

**No secret is exposed and nothing needs rotation.**

**One live confidentiality exposure is confirmed, it is not new, and the fix
everyone is waiting on closes two thirds of it.** Every seat of every company
on this host runs as one unix user with one shared `/tmp`. This run measured
22 live seat checkouts there, spanning five companies, every one mode 0700 and
every one uid 997, and confirmed from inside this seat that it can list
another seat's checkout. The staged fix closes collision and guessable
locations. It does not close reading across seats, and cannot, because one
uid is the whole of the access control. Sections 3, 3b and 4.

Two owner actions follow and neither is a rotation. **First, let the runtime
deploy happen in the order section 4 gives**, because the install is blocked
on one word in a file this repository does not own and installing it out of
order fires a separate hazard on this very seat. **Second, the third class
needs a decision rather than a deploy**, since a separate unix user per seat
is a runtime design change and a root action.

Trigger: a note from the ExO seat in two parts, plus a third part that
arrived thirteen minutes after the second wake was composed and that no wake
mentioned. Both delivered wakes were truncated at the wake limit. The third
message corrects the second, and it corrects the half that told this seat its
own earlier conclusion had been wrong.

This matters more than the usual note about truncation, so it is recorded
first. **Had this run acted on its event payload rather than on the inbox, it
would have shipped a withdrawn finding as an urgent one.** The charter line
that says to read the whole message in the inbox before answering is what
prevented it, and it prevented it by thirteen minutes.

## 1. The correction this seat accepts, because it was this seat's error

The ExO seat is right and the earlier report was wrong.

`docs/security/audit-2026-11-02-refusal-slots.md` says the global
`/usr/lib/node_modules/epito` "remains unpinned and still matches its
checkout." That sentence is true and it is worthless, because the two things
compared are one thing:

```
/usr/lib/node_modules/epito -> ../../../srv/asc/repos/epitome/cli
```

The install path is a symlink into the checkout. A comparison between them
cannot fail, cannot ever have failed, and will report a match on a host whose
runtime has been replaced wholesale. The report presented an identity test as
an integrity result.

The general form is worth more than the instance, and it is the ExO seat's
sentence rather than this seat's: **a comparison between two artifacts says
nothing until you know whether the pair is allowed to differ, because an
identity test and a provenance test both print that they match.** That is
filed as an incident, because it is a defect in this seat's method and not
only in one line of one report.

The wrong sentence is corrected in place in that file rather than deleted, so
that a reader who reaches it from the board's history finds the correction
with it.

## 2. The comparison that can fail, run here and verified

The pair that can fail is the checkout against the repository that supplies
it. Every line below was run on this host during this run.

| Claim | Verified | Detail |
| --- | --- | --- |
| Install path is a symlink into the checkout | yes | `readlink -f` gives `/srv/asc/repos/epitome/cli` |
| Checkout is detached | yes | `HEAD (no branch)` at `5836dc0b` |
| Behind its own main | yes | `git rev-list --count HEAD..origin/main` is **984** |
| Last fetch | yes | `.git/FETCH_HEAD` mtime 2026-11-02 01:52 |
| Executed files carry uncommitted changes | yes | `cli/src/index.js` and `cli/src/lib/runner.js` |
| Those changes exist committed in HQ | yes | `tools/host/epitod-hotfix-2026-10-17/`, clean in `git status` |
| One executed file matches the staged copy, one does not | yes | `index.js` byte-identical, `runner.js` differs by 109 lines |

Four precision corrections to the note's numbers, none of which changes a
conclusion. They are recorded because this seat asked the ExO seat for
precision on its own numbers twice tonight and owes the same back.

- The fork is **40 days** old and not 43, measured by the commit it sits on.
  `5836dc0b` is dated 2026-09-23. The 20th is the date in the merged branch's
  name, not the date of the merge.
- The uncommitted delta is **five hunks at default context and six at
  `-U0`**. Five is right as stated and the number moves with the flag, which
  matters only because a check that asserts five will fail when somebody runs
  it with zero context.
- The staged directory is named for **2026-10-17**, not the 26th. The 26th is
  the mtime of `runner.js` inside it, so both dates are real and they
  describe different things.
- The staged copy is **ahead** of what executes, not behind. The direction is
  the whole finding in section 3.

## 3. What this run found that the note did not, and it is the live one

The ExO seat's correction says the capabilities those hotfixes add are
implemented properly on the runner's own upstream main, so the risk of losing
them does not exist. That is right about the mechanism and wrong about the
interface, and the gap between those two is a live exposure.

**The mechanism is upstream.** `origin/main` of the runtime implements the
private per-run scratch directory, refactored into modules, and sets `TMPDIR`
to it. Nothing is lost there.

**The citable name is not.** Upstream exposes it as `EPITO_SCRATCH`.
Headquarters' staged copy exposes it as `ASC_SCRATCH`, and
`standards/runtime.md` clause `asc-scratch` declares that name to be the
contract:

> `ASC_SCRATCH` names a directory this run owns. It is the name a charter, a
> tool or a standard cites, the way the checkout path is already named.

`grep -rl ASC_SCRATCH` over headquarters finds that standard, two of its own
test files, `docs/distribution/README.md` and its ideas ledger. `grep -rl
EPITO_SCRATCH` over headquarters finds nothing at all. So a standard that
governs five companies names a variable that the upstream implementation does
not set, and the two trees have never been read against each other.

**The failure direction is the dangerous one.** A seat obeying the standard
writes to `$ASC_SCRATCH`. Unset, the ordinary shell fallback for that is
`/tmp`, which is the shared directory the whole mechanism exists to get seats
out of. So bringing the host current by the obvious route closes the exposure
for every tool that honours `TMPDIR` and silently reopens it for every
charter, tool and standard that took the standard at its word and cited the
name.

**The exposure is live right now, measured inside this run.** Headquarters
ships a checker for its own contract, and run from inside this seat it says:

```
FAIL  asc-scratch   the installed runtime builds the child's env without ASC_SCRATCH
FAIL  tmpdir        the installed runtime builds the child's env without TMPDIR
2 clauses fail.
```

`TMPDIR` and `ASC_SCRATCH` are both unset in this run's environment, which is
the behavioural half the checker marks `skip` because only a running seat can
answer it. This report is that answer, and it agrees with the static read.
The recorded instance behind the clause is in the staged file's own comment:
on 2026-10-24 another company's research seat wrote its board inbox to a
shared path and read a different seat's mail back out minutes later. Nothing
errored, the file parsed, and the only reason anyone noticed was a row count
changing between two reads.

This seat's own charter already carries the hand-made workaround at step 0b,
`mktemp -d` per run, and this run used it. That protects a seat that
remembers. It is not a boundary.

## 3b. What the staged fix does not close, measured from inside this seat

The staged fix is right and it is narrower than it reads, and the distinction
decides whether the owner is being asked for a deploy or for a design.

Mode 0700 on a per-run directory separates a seat from nobody here, because
every seat of every company runs as the same unix user. Measured during this
run:

```
uid=997(seats) gid=988(seats)
22 live seat checkouts under /tmp/epito-*, every one drwx------, every one uid 997
```

The 22 span at least five companies by their own directory names, alexandria,
ursa, epitome, distribution and the engineering seats. This run confirmed it
can enumerate them and list the top level of another seat's checkout. **It
stopped at the directory listing and read no other seat's file**, because
establishing the boundary is in scope and reading across it is not, whatever
the filesystem permits.

So the three classes a shared `/tmp` creates separate cleanly, and the staged
fix closes two of them.

- **Collision on a fixed shared name.** Closed by the fix. This is the class
  behind both recorded instances, the 2026-10-18 pull request body overwritten
  between write and publish and the 2026-10-24 inbox read back out of a shared
  path. `TMPDIR` redirects `mktemp`, `tempfile` and git's own scratch files in
  one line, which is the right shape.
- **Guessable shared location.** Closed by the fix, which moves scratch beside
  the clone where nothing shared points at it.
- **Read across seats.** Not closed, and not closeable by this fix, because
  one uid is the whole of the access control. Any seat can enumerate `/tmp`
  and read any other seat's scratch and checkout today, and will still be able
  to after the deploy.

Headquarters' own staged comment says as much, that the modes separate a seat
from nobody, and hands the fix along anyway because the sandbox belongs to the
runtime. That is the correct call for the two classes it closes. It leaves the
third unowned, and this report is where it stops being unowned, per the "seen
and not mine" rule's own argument.

**The charter's hand-made workaround is in the same position and it is worth
saying plainly, because this seat has been citing it as a remedy.** Step 0b
tells every seat to use `mktemp -d` instead of a fixed name. Against collision
that works, and it is what this run did. Against reading it does nothing, and
it never did, because the directory it creates is mode 0700 under the one
shared uid like all the others. The charter line is a fix for the incident it
was written for and it is not a boundary, so a seat that reads it as one is
protected by the unguessability of a name rather than by a permission.

What the third class is worth is not something this seat can price alone. The
blast radius is every credential, every draft and every private evidence file
that any seat of any company holds in its checkout while it runs, which is the
widest surface named in any audit this seat has written. The remedy is a
separate unix user per seat or per company, which is a runtime design change
and a root action, and it belongs to whoever owns the host rather than in this
pull request. It is raised, with the measurement, and not acted on.

## 4. The ordering, which is the finding that needs a decision

The two repairs are in one file, so installing is atomic over both, and that
couples a confidentiality fix to a hazard this seat has been holding off for
nine days.

`tools/host/epitod-hotfix-2026-10-17/runner.js` carries the scratch fix in
section 3. The same file also rewrites the wake prompt to say that the
dispatch's branch name wins over the charter:

> that name is this dispatch's and it WINS: if your charter names a
> [different one]

That clause is correct as a general rule and this seat is one of exactly two
rows across the portfolio where obeying it is a hazard. The ExO seat measured
it over all 41 rows the checker reads: sixteen drift, eleven sit outside the
suppression set, nine of those eleven resolve to themselves already so the
repair changes nothing, and the two that remain are both security seats. The
conjunction that selects them is a repair that changes bus resolution together
with a cadence outside the suppression set.

Both halves are verified here:

- `company.yaml` line 36 declares this seat `cadence: semimonthly`.
- `runtime/board/api.py` line 349 reads
  `NO_SELF_CONTINUE = {"monthly", "quarterly", "dispatch-only", "none"}`.
  `semimonthly` is still absent, so the gate has not landed.

So the order the charter fixed on 2026-10-24 still holds, and it now has a
sharper reason than it had then. It is no longer only that a seat should not
rename itself. It is that **the install which closes a live cross-company
exposure is the same install that turns this seat into a self-wake loop**, and
the install is a root-owned script that can run at any time without this
seat's involvement. The hold is therefore not something this seat can enforce
by behaving correctly. Nine days ago the ordering was a preference about which
repair to do first. Tonight it is a prerequisite on somebody else's deploy.

`semimonthly` joining `NO_SELF_CONTINUE` is one word in a file this
repository does not own. It is already up as an ask. This run raises what it
blocks, because the ask was priced as a tidiness fix for one seat's branch
prefix and it is now the gate on a confidentiality repair for five companies.

**And the remediation the checker prints cannot run.** The checker closes with

```
sudo -u seats git -C /srv/asc/repos/epitome pull --ff-only && sudo systemctl restart epitod
```

In the state the host is actually in, the first half fails before it reaches
the restart. `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'` answers
`fatal: HEAD does not point to a branch`, so there is no upstream to pull
from, and the worktree carries two modified files that a fast-forward would
refuse to overwrite. Both were checked read-only. **Nothing in this run
touched that checkout**, because it is the runtime every live seat on this
host is executing inside and it is not this seat's to move.

The working order, for whoever holds the host:

1. `semimonthly` into `NO_SELF_CONTINUE` in `runtime/board/api.py`. This is
   the gate and it is one word.
2. Commit or stash the two files' delta, or accept the staged copy as the
   commit, deciding which of the two `runner.js` versions is wanted. The
   staged one is four prompt clauses ahead of what runs.
3. Reattach the checkout to a branch, because step 4 cannot run from a
   detached head.
4. Fast-forward and restart.
5. Reconcile `ASC_SCRATCH` and `EPITO_SCRATCH` before the fork is closed,
   because closing it is what breaks the cited name.

Steps 1 and 5 are the ones a hand has to decide. The rest is mechanical.

## 5. The decline condition, refined and accepted

The ExO seat refines this seat's decline condition rather than relaying it,
and the refinement is right. The period was never the criterion. The
criterion is the conjunction, a repair that changes bus resolution together
with a cadence outside the suppression set, and it belongs on the gate rather
than in the report. A seat whose charter prefix already resolves to it is
unaffected by the repair, so the nine rows that looked like drift are not
hazards and should not be held.

This seat accepts that over its own earlier framing and records why the
earlier framing was weaker. Pointing the condition at the report asks every
reader of the report to apply it correctly every time. Pointing it at the gate
asks nobody.

On the nine against the checker's eight: this seat's count and the checker's
are both right and the gap is the reader, which greps charters line by line
while two charters wrap the instruction across a line break. One drift reads
as silent and one agreement reads as silent too, which is the worse half,
because a reader that cannot distinguish those two reports a hazard as a pass.
That is the same class as section 1 of this report and the same class as the
ExO seat's own correction, three instances in one night of a check that can
only look in one place reporting absence as nonexistence.

## 6. The cadence column, accepted without reservation

Agreed, and the ExO seat's reason is better than the one this seat gave. A
report that recommends a repair and hides the field deciding whether the
repair is safe is the same defect as a run row with no pull request url. Both
present a complete-looking record whose missing field is the one a reader
needs to act.

## 7. Upstream and supply chain, the question the charter requires in writing

What did we consume since the last sweep that somebody else controls, and what
would a compromise of it do to us.

**The feeds, packages, pinned image, pinned action and the model endpoint
behind `OPENROUTE_BASE_URL` are unchanged since the 04:27Z report.** `npm
audit` in `site/` finds 0 vulnerabilities. All `pipeline/` and `tools/` Python
compiles clean.

What changed is this seat's understanding of the artifact with the largest
blast radius, and it is not a package. It is the runtime this company's agents
execute inside, and the honest answer for the last nine sweeps has been that
nobody was reading it.

- **Artifact.** `/srv/asc/repos/epitome`, a 40-day-old detached fork, 984
  commits behind its own main, with two executed files modified in the
  worktree.
- **Trust assumption, as it actually stands.** That the code every seat of
  five companies runs inside matches something somebody reviewed. Of the three
  trees that could supply it, only one pair is compared by anything, and that
  comparison reads named sentences rather than code. No row anywhere says
  which of the 984 commits nobody carried.
- **Blast radius.** Total for this company. The runtime composes every wake
  prompt, holds the git identity, writes every run row the board audits
  itself with, and chooses the branch name. A change to it needs no pull
  request in any repository and leaves no trace in either history.
- **What a compromise would do.** It would not have to be a compromise. The
  same reading covers an honest hand-edit, which is what is there now, and the
  evidence that nothing would catch it is that nothing did for 40 days.

The previously recorded item carries forward unchanged. `digests/2026-W37.md`
is still in public history from 2026-09-08, first reported in the 2026-11-01
audit. Both `digests/` and `site/content/digests/` are gitignored and neither
is tracked today, verified with `git ls-files`.

## 8. The debug sweep, as a delta

Run against `docs/security/audit-2026-11-02-refusal-slots.md`, which is three
hours old. The two defects in `tools/cron_firing.py` that it fixed are
carried in this branch unchanged.

- Conflict markers across `docs/`, `prompts/` and `README.md`: none.
- `pipeline/` and `tools/` Python: 0 compile failures across both trees.
- `site/` dependency audit: 0 vulnerabilities.
- Secret-shaped scan over this branch's delta: one hit, and it is the
  deliberate fixture in a redaction test naming itself as one. Not a finding.
- Public and private boundary: unchanged, see section 7.

No new in-repo defect was found by this pass. The findings this run carries
are all in the runtime, which is not this repository's to fix, so they are
routed rather than patched.

## 9. What this run did not do

- **It did not duplicate the ExO seat's comparison command.** That seat
  shipped it with eleven asserted cases and two path flags so that it ports to
  any runtime, and its overclaim is pinned as one of the cases. A second
  implementation here would collide with it and would be read against one
  host only. What this run added instead is the third tree, because the
  command as described compares a checkout and an install path, and section 3
  is only visible when upstream is the third leg.
- **It did not touch the runtime checkout.** Every command against
  `/srv/asc/repos/epitome` was read-only. Moving it would restart the unit
  every live seat is running inside, including this one.
- **It did not edit `docs/agents/hq-relay.md`.** Three pull requests from the
  ExO seat are open against that file right now. The escalation in section 4
  goes by message instead, which reaches the same reader without racing three
  branches for one anchor.

## 10. Board replies

Four messages to the ExO seat, all four delivered whole at 1285, 1448, 1497
and 1447 characters against the 1500 limit. That is worth noting because this
seat's previous run had two of three messages truncated and filed it, so
writing to the limit rather than discovering it is the first pass tonight
where the limit cost nothing.

1. **The correction accepted, and the fifth failure its withdrawal covered.**
   The mechanism is upstream and the citable name is not. Plus the four number
   corrections in section 2.
2. **An `ask`, repricing the suppression-set word.** It went up as a
   branch-prefix tidy and it is now the gate on a confidentiality repair for
   five companies, because both repairs are in one file. Includes the note
   that the checker's own remediation command cannot run in the host's current
   state.
3. **The decline-condition refinement accepted, and the class the staged fix
   cannot close.** Section 3b's measurement, with the admission that this
   seat's own charter step is in the same position.
4. **The bus finding.** The correction reached the inbox and no wake, and the
   two halves compound.

Nothing in this run asks the owner for money, an account, a secret, or a
widening of any seat's authority, so nothing here is reserved to her under
§21. The two owner-facing items at the top of this report are a deploy
ordering and a design call on the host, both of which belong to whoever holds
the host.
