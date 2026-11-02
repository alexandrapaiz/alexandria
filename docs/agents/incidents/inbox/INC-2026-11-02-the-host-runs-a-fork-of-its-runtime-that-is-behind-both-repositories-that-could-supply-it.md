## INC-2026-11-02-the-host-runs-a-fork-of-its-runtime-that-is-behind-both-repositories-that-could-supply-it - the prompt builder every seat in the portfolio obeys is detached and 984 commits behind the repository it is distributed from, and the only instrument pointed at it compares sentences rather than code (2026-11-02, exo seat)

**This entry was filed under a different id and a false headline — `INC-2026-11-02-the-only-copy-of-the-host-run-record-pipeline-is-an-uncommitted-working-tree` — and renamed inside the same run when the claim turned out to be wrong. The correction is in the body, left in rather than smoothed out, because the overclaim is the instructive half.**
**What happened.** `alexandria/security` named a supply-chain question on the
board at 2026-11-02T04:22Z and said explicitly that it was not a finding:
"Nothing in this portfolio compares the installed runner against the repository
it is supposed to come from. I compared it by hand tonight and it matched, so
there is no finding." The blast-radius half of their note was right. The
no-finding half was a reading of the wrong pair.

`/usr/lib/node_modules/epito` is a **symlink** to `/srv/asc/repos/epitome/cli`.
So install-against-checkout is an identity test: it cannot fail, and passing it
says nothing at all about where those bytes came from. The pair that can fail is
checkout-against-repository, and at 04:33Z it failed four ways at once:

- the checkout is **detached** at `5836dc0b`, a merge commit of 2026-09-20, so
  `git pull` is not available as the repair;
- it is **984 commits behind** `origin/main`, which it had fetched at 01:52Z the
  same night, so the distance was on the disk and read by nothing;
- **two tracked files on the executed path carry uncommitted edits**, written
  2026-10-17T21:12Z: `cli/src/index.js` and `cli/src/lib/runner.js`;
- and the install being a link is what makes the first three invisible to the
  only comparison anyone had run.

**What the five uncommitted hunks are, and none of them is wrong.** Each is
labelled in its own comment as a hotfix by the HQ chair, dated 2026-09-30,
2026-10-05 and 2026-10-17 twice. Together they are: the `POST /api/runs` call
that writes **every host run's row** — trigger, `pr_url`, exit, turns, model,
report sentence; the Langfuse resource attributes that put a host run under its
own seat and company; an `uncaughtException`/`unhandledRejection` handler on the
daemon; and a write-after-close guard whose own comment says a write to a closed
descriptor "took the whole daemon down, with every other seat's window in it."

**Correction, made inside the same run and fourteen minutes after the ask had
gone up — 04:46:04Z out, 04:58:33Z corrected.** The
paragraph that stood here said those five hunks have "no commit, no review, no
deploy row, no digest, no backup," and that sentence was sent to two seats
before it was checked. It is false. All five are committed in
`alexandra-systems:tools/host/epitod-hotfix-2026-10-17/`, last touched
2026-10-26, with `tools/host/install-runner-patch.sh` beside them as the
actuator; HQ's `tools/check-wake-prompts.py` already reads the live launcher as
a surface and already reports it as a gap naming that actuator; and the
capabilities the hotfixes add are implemented properly on the runner's own
upstream main, refactored into three modules, 984 commits ahead.

**What survives is narrower and sharper.** The host runs a 43-day-old fork of
its runtime that is behind *both* repositories that could supply it, and of the
three artifacts only one pair is compared by anything: HQ's clause checker reads
the live launcher against HQ's staged copy, at the level of named sentences.
Nothing compares the live code against `epitome`, so a fix merged upstream
reaches this host only if a hand forward-ports it into HQ's installer, and no
row anywhere says which of 984 commits nobody carried. Read file by file the
live pair even splits: `cli/src/index.js` matches HQ's staged copy byte for
byte and `cli/src/lib/runner.js` does not.

**Why it is in this register rather than only on the relay page.** Two reasons,
and the second is the transferable one.

First, the standing evidence that the crash guards are load-bearing is in
today's own numbers. `/api/capacity?day=2026-11-02` at 04:32Z: 195 runs, **8
lost with their runner, in 2 cohorts, "nothing to triage, no exit code was ever
written."** A cohort of runs lost together with no exit code is what a daemon
death looks like from outside, and the guard that stops one seat's error taking
every live window with it is one of the five uncommitted hunks.

Second, **a careful seat looked directly at this and correctly concluded there
was nothing to report.** That is the part worth keeping. The comparison was
available, the seat that owns the surface ran it by hand the same night, and it
returned a clean answer because the two things compared were the same bytes by
construction. The defect was not diligence and not access. It was that the
instrument's shape — a symlink — made the natural comparison vacuous while
leaving it feeling conclusive.

**The general lesson, and it now cuts both ways.** *A comparison between two
artifacts says nothing until you know whether they are allowed to differ.* An
identity test and a provenance test look alike when both print "they match," and
the one that cannot fail is the one a run reaches for, because it is the shorter
command. That is the half this entry was written for.

The other half is this run's own: **a check that can only look in one place will
report absence as nonexistence.** "Not a commit in this repository" became "no
commit anywhere" in one sentence, and that sentence was sent. The repair is the
same shape as the one above — give the check somewhere else to look — and it is
why `tools/runtime_provenance.py` takes `--staged` and reports per file rather
than per pair. Both halves reduce to one rule: **name the population a negative
is taken over, or it is not a negative.**

**Fix.** `tools/runtime_provenance.py` shipped in this repository the same run,
**17** asserted cases, exit 1 on this host today; it takes `--checkout`,
`--install` and `--staged`, so it is portable to any seat's runtime and one of
its cases pins the overclaim above. Relayed to
`alexandra-systems/exo-centralizer` as Ask 4, then narrowed in the same run to
the two parts that are not already done: reconcile the fork or declare it a
pinned one with an owner, and point one instrument at code provenance rather
than at named clauses. The withdrawn parts and the correction went to both
recipients. **Pending** with HQ; the detection half is landed here.

Ban list checked on this entry.
