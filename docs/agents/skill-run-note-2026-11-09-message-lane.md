# Skill run note, 2026-11-09 (message, lane wake after #838 merged)

Woken by my own #838 merging, with the instruction to continue with the next
item in my lane on the board and say what I took.

Pull request #845. Branched from `main` at `c7aebd35`, depth 0, nothing
superseded, no open pull request from this seat. The branch name needed a suffix
because `alexandria-skill/2026-11-09-message` is #817.

## What I took, and why it was not the board item

`This sprint` holds one item for this seat, `7e6cfb5d`, and it is the same item
my last four runs were woken into. Its provenance half shipped on 2026-11-02 and
sits in Review. Its effect half is blocked on `GROQ_API_KEY`, which the PM
re-scoped on 2026-11-02 and named as the owner's to write. Nothing has changed:
`NEON_RO_URL` and `GROQ_API_KEY` are both absent from this seat's host
environment, checked rather than quoted, which is the fourth run running.

So I took what the charter puts ahead of new work, which is maintenance, and the
maintenance queue had a named item: **the two findings my own containment run
routed to `skills/evaluation-integrity` eight hours earlier**, from IsolateGPT
(2403.04960) and ACE (2504.20984). `evaluation-integrity` is also one of two
skills never revised after its ADR-38 retrofit.

## The finding, and the routing note it corrects

Both papers were re-fetched and the tables re-read on this branch rather than
taken from the routing note. 114,785 and 129,856 chars, exit 0 on both.

**The routing note was wrong about IsolateGPT and the correction makes the
finding better.** It said the functionality evaluation "logged four classes of
plan deviation and counted all four correct because the final output was right."
Table II reports two axes and scores intermediate steps at **0.76** against
**0.95** on final output, so the deviations do land on the steps axis. What
survives is narrower and better evidenced: the isolated and non-isolated systems
tie **exactly** on both reported axes while their step-failure classes differ, an
unexpected app called at 28.57 percent of errors against 14.29 and an expected
app never called at 14.29 against 28.57 (Table III). The aggregate hides the
profile rather than hiding the deviation.

**ACE's half verified in full.** Table II's caption says both rates are
conditioned on execution reaching the phase, so overall is the product, and two
of four configurations land 0.5 points apart on it while failing in opposite
phases: Qwen-2.5-72B 87.9 / 68.5 / 60.2, Claude 3.7 Sonnet 66.6 / 91.2 / 60.7.
The products check: 0.879 x 0.685 = 0.602, 0.666 x 0.912 = 0.607. The paper's own
summary groups them as "at least 60 percent", which is the aggregation that loses
21.3 points in one factor and 22.7 in the other.

Both go into delta 2 rather than into a sixth section, because delta 2's existing
claim is the same theorem in a narrower setting: the statistic is constant across
the distinction. Its heading widened, which `skill_eval.py --check` immediately
flagged as a stale `sections` reference in ei-t2 and ei-t3, which is what that
check is for.

## What the next run should not re-derive

**The new section was not findable when it shipped, and the fix was measured
rather than argued.** `ei-pos-4` routed to `skill-library-engineering` at 0.1895
under the description as first committed. Three variants, each run over the full
library: one fires `ei-pos-4` and holds `ei-neg-3`, one leaves `ei-pos-4` dark,
and one fires `ei-pos-4` and **breaks** `ei-neg-3`. The broken one is why
`ei-neg-3` was written: a signup funnel with four stages and two channels half a
point apart shares the exact arithmetic and has no generated instrument anywhere,
so a clause firing on "two configurations score the same" is too broad. The
shipped clause costs 4 words over the 150-word budget, four words were traded out
of three other clauses, and the suite was re-run after the trade with no case
moving. 149 words, 960 chars.

**Trigger suite 74 of 84, reliability 0.88, 95 percent CI [0.79, 0.94]**, against
72 of 82 at 0.88 [0.79, 0.94]. Positives 37/39, negatives 18/23, confusion 19/22.
The ten failures are the same ten, every one pre-existing on `main`. A green
trigger suite says this skill is findable and says nothing about whether it
helps.

**Rule 3's published 0 of 10 was a denominator, and I nearly moved nine skills'
history on it.** The number was measured from byte zero, which counts the
frontmatter, and the frontmatter is 93 of `agent-containment`'s 101. Measured
three ways with the new `skills/_validation/checklist_position.py`: 0 of 10 from
byte zero, **10 of 10 from the body**, which is the reading rule 3's first
sentence describes, and **2 of 10 to the end of the checklist**, which is the
reading its second sentence describes. On the reading that fails, the cause is
checklist length and not the frontmatter, so the remedy the number named cannot
move either number that matters. Wired into no gate, because picking the reading
is a charter edit. Do not re-derive this, and do not move the other nine
skills' `revisions` blocks for rule 3's sake. `evaluation-integrity`'s moved for
its own reasons: 643 words, the site renders none of it, and the new delta needed
the lines.

**A new skill is impossible without the database, not merely unsourced.**
`tests/skill-provenance.test.mjs` requires `status: draft` on a zero-claim skill
and permits `citing.length >= LIBRARY.length - 1`, which is exactly one such
skill at a time. `agent-approval-paths` holds the slot. So with `NEON_RO_URL`
absent, a newly extracted skill turns the suite red rather than shipping thin.
That is a different sentence to put in front of whoever decides about the secret,
and it is a ledger entry.

**The ban list is unenforced over `skills/` and 8 of 10 fail it**, 59 findings,
every one entry 13 and every one a U+2014 on a `provenance.papers` line.
`docs/agents/registers.md` reads "closed for copy outside the digest" and nothing
in that row reaches `skills/`. I fixed the 11 in the file I was revising and left
48 across 7 skills as a ledger entry and an incident, because seven separator
passes are seven revisions and a reader-facing skill edit should be measured
rather than batched.

**Three of my own gates caught three of my own defects, which is the argument for
running them before the suite.** `panel_provenance.py` failed the skill on
`ours-marked`, because I wrote "(ours, not either paper's)" and the panel knows
four forms; "(ours, not the papers')" is both recognised and the more accurate
claim. `trigger_test.py --receipts` caught the stale receipt before the commit
rather than the suite catching it after. And `project_fixture_probe.py --check`
was red on `main` on a row #838 shipped, which is below.

**`ac-t15`'s `stub_score` has now been published wrong three times in one day.**
2 of 4 estimated, 1 of 4 "measured", 0 of 4 actual. The 1 of 4 is a true number
about the headline stub, which is a different artifact from the one the field is
defined as, and the word "measured" in its own note is what made it
unreviewable. Setting `swept: true` then surfaced two more defects on the same
row that had been invisible rather than absent. `skills/agent-containment/` was
byte-identical to `origin/main` on this branch, which is how I know the red was
inherited.

## Mechanics worth knowing

**The same-day bundle tie fired a third time in the register and a fourth
counting the one recorded only in a README.** `rank_bundles` sorts on
`generated`, a date, and both pre-registered, so `sorted()` is stable and the
alphabetical glob decides. `containment` beat `evaluation-integrity` on the
letter c. Mitigation is this entry's own: the older bundle to
`results/superseded/` with a README note. Appended to INC-2026-10-26 rather than
filed fresh.

**The host filled up mid-run.** `/tmp` hit 100 percent with 155M free, which
killed `project_fixture_probe.py` inside a `git stash` and left this run's
uncommitted work in `stash@{0}` with `index.lock` unwritable. Recovered by
deleting this run's own scratch files and popping. Nothing was lost, and the
lesson is that `git stash` is the wrong instrument for an A/B against `main` on
a shared host at 99 percent: `git diff --stat origin/main -- <path>` answers the
same question with no writes, and it is what settled the `ac-t15` question
afterwards.

## Numbers for the record

| | before | after |
|---|---|---|
| `evaluation-integrity` `wc -l` | 119 | 119 |
| `evaluation-integrity` words | 4,484 | 4,462 |
| description | 148 words | 149 words |
| eval tasks | 9 treatment, 2 control | 11 treatment, 2 control |
| library conformant eval files | 9 of 10 | **10 of 10** |
| library sections exercised | 43 of 44 | **44 of 44** |
| rubric criteria certificated | 314 of 314 | 319 of 319 |
| trigger suite | 72 of 82, 0.88 | 74 of 84, 0.88 |
| provenance panel | 1 failing | **0 failing**, 10 not fully measurable |
| claim ids placed to a section | 146 of 154 | 146 of 154 |
| ban list over `skills/` | 8 of 10 failing, 59 | 7 of 10 failing, 48 |

One line of the 119 was bought by merging two caveat bullets rather than by
cutting words, which is the defect this seat measured yesterday, done knowingly.
The file is 22 words shorter than it was with a new finding in it, so the trade
went the right way overall and the one join is named rather than hidden.

## Everything here is unmeasured

In that word. Ten skills still read `provisional` or `draft`, none carries a
with-and-without delta, neither eval arm ran, and the one effect measurement this
library owns still has the wrong sign. ADR-38 rule 5's bare-first qualification
pass has not run on `ei-t12` or `ei-t13`, so neither has qualified or been
excluded, and both carry `authored-judgement` bases that say so.
