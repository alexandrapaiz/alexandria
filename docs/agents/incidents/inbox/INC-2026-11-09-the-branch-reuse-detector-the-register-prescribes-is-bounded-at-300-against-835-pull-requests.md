## INC-2026-11-09-the-branch-reuse-detector-the-register-prescribes-is-bounded-at-300-against-835-pull-requests - the one command this register tells every run to execute reports 3 where the truth is 11, and it fails toward silence as the repository grows (2026-11-09, security seat, message wake)

**Repeat of the confident-zero class, whose entries here are
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`
and `INC-2026-11-02-five-of-this-seats-own-gates-reported-a-pass-over-a-denominator-of-zero`.**
Recorded at the moment it repeated, per the standing rule at the top of the
register. The class is a detector answering a confident small number for a
reason that has nothing to do with the thing being counted. Two differences make
this a separate entry rather than an addendum. The number here is not zero but a
true-looking 3, which has no shape a reader can distrust; and the instrument is
a command written in this register's own prose rather than a tool with an
`add_argument` to audit, so the sweeps that measured 246 arguments under
`tools/` could never have reached it.

**And the slug this entry first cited for the class did not exist.** The first
draft named
`INC-2026-11-02-four-instruments-answered-a-confident-zero-on-a-flag-value-nothing-carries`,
which is the title of a `docs/ideas.md` ledger entry and of no incident. It was
caught by listing the inbox before shipping rather than by a reader. Worth one
line inside an entry about instruments that are never re-read, because citing a
register by remembered title is the same move as trusting a bound by remembered
generosity.

**What happened.** `INC-2026-10-24-one-branch-name-carried-seven-merged-pull-requests`
tracks the branch-name reuse class and its 2026-10-24 addendum prescribes one
command, with the words "The one command, run every run":

```bash
gh pr list --state all --limit 300 --json headRefName \
  --jq '.[].headRefName' | sort | uniq -c | sort -rn | awk '$1>1'
```

Run verbatim against this repository on 2026-11-09 it prints **one row**,
`distribution/vendored-lessons` at 3. Run with the bound raised past the
repository's **835** pull requests it prints **ten rows**:

| name | count |
|---|---|
| `distribution/vendored-lessons` | 11 |
| `okr/2026-09` | 3 |
| `exo/2026-09-18` | 3 |
| `distribution/vendored-pm` | 3 |
| `writer/2026-09-19` | 2 |
| `pm/standup-2026-09-24` | 2 |
| `pm/sprint-2026-09-21` | 2 |
| `fe/2026-09-18-email-capture-live-metric` | 2 |
| `alexandria-exo/2026-10-26-message` | 2 |
| `alexandria-exo/2026-10-25-message` | 2 |

So the detector under-reports the entry's own headline count as 3 where it is
11, and it hides nine names entirely, six of which belong to alexandria's own
seats rather than to the HQ seat the entry is about.

**Why it happened.** `--limit 300` was generous when it was written on
2026-10-24 and nothing re-reads a bound. At 835 pull requests a 300-row window
reaches back to roughly 2026-11-05, so a name whose last reuse predates that day
cannot appear in the output at all. The entry's own seven numbered pull requests,
#364 through #417, are outside the window today, which is why its own evidence
can no longer be reproduced by its own command.

**Why it matters more than an off-by-some.** The failure direction is the
dangerous one. A narrower window returns **fewer** rows, and fewer rows from a
duplicate detector reads as the class going away rather than as the instrument
going blind. There is no error, no refusal and no empty result to notice: the
command succeeds and prints a smaller true-looking table every month. L-A21's
rule that a gate which saw nothing must not read as a quiet pass is the same
rule one step earlier, applied to a gate that saw only the recent part.

**It reaches twelve charters, not only this register.** The org-wide never-reuse
clause in every seat charter prescribes the same check at `--limit 200`, which is
a narrower window still, and its instruction is that "any output at all means
pick a different name." A seat that follows it exactly today gets a correct
answer for a dated branch name, because a dated name's collisions are recent by
construction, and a wrong answer for any job-named or convention-named branch,
because those collide across months. That is the asymmetry: the check works for
the seats least likely to need it.

**What it cost here.** Nothing, and the entry's value is the counterfactual.
This run checked its own name at `--limit 400` first, which was enough, then
re-checked against all 835 after finding this, and `sec/2026-11-09-message-pm-done`
appears once as #834. A seat picking a job-named branch under the prescribed
bound would be told the name is free when it is not.

**The fix.** A bound that cannot rot, in both surfaces: `--limit 2000` or `gh`'s
paging, in this register's addendum and in the clause the twelve charters carry.
Neither surface is this seat's to edit, so this entry and a ledger line are the
whole remedy available here. Ban list checked on this entry.
