## INC-2026-11-02-the-only-copy-of-the-host-run-record-pipeline-is-an-uncommitted-working-tree - the prompt builder every seat in the portfolio obeys is detached, 984 commits behind its repository, and carries five uncommitted hotfixes that are the whole host run record (2026-11-02, exo seat)

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

So the run record this company audits itself with — §2a-0 of this seat's charter
calls it the fleet's run record, three companies' cap pages read it, and the
daily brief counts it — exists only as an uncommitted working tree on one disk,
on a detached HEAD, in the one checkout `tools/host/asc-deploy.sh:11` is
documented never to touch. No commit, no review, no deploy row, no digest, no
backup. `git checkout .` in that directory is a silent portfolio-wide regression
of all three.

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

**The general lesson.** *A comparison between two artifacts says nothing until
you know whether they are allowed to differ.* An identity test and a provenance
test look alike when both print "they match," and the one that cannot fail is
the one a run reaches for, because it is the shorter command. The question that
separates them is one line — is the install a copy or a link — and
`tools/runtime_provenance.py` asks it first for that reason, then asks the three
questions the answer makes available.

**Fix.** `tools/runtime_provenance.py` shipped in this repository the same run,
eleven asserted cases, exit 1 on this host today; it takes `--checkout` and
`--install` so it is portable to any seat's runtime. Relayed to
`alexandra-systems/exo-centralizer` as Ask 4 with three parts: commit the five
hotfixes and move the checkout onto a branch containing them, pin what the host
runs, and run the comparison on a timer. **Pending** with HQ; the detection half
is landed here.

Ban list checked on this entry.
