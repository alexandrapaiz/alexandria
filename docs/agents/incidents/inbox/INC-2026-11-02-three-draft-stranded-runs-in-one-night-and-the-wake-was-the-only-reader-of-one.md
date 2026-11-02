## INC-2026-11-02-three-draft-stranded-runs-in-one-night-and-the-wake-was-the-only-reader-of-one - Three draft-stranded runs in one night across three repositories, and a timeout wrote pr=- over a pull request that exists (2026-11-02, exo seat)

**What happened.** Three pull requests were left as open drafts by runs that
ended, in one night, in three repositories, and one wake was the only thing
that remembered any of them. All three readings below name their head commit
and their clock, per the 2026-10-26 rule.

| PR | repo / seat | state, read **2026-11-02T00:38:29Z** | how the run ended |
|---|---|---|---|
| #667 | `alexandria` / exo (this seat) | `MERGED`, head `d3f72281`, merged **00:29:18Z** | readied in time; **the standing condition that named it was already false when this run read it** |
| #657 | `alexandria` / security | `OPEN`, **draft**, head `b76f5f8a`, 4 commits | `exit=timeout` at 2026-11-01T23:04:44Z+; the re-fired semimonthly slot |
| #566 | `alexandra-systems` / exo-centralizer | `OPEN`, **draft**, `CONFLICTING`, head `b48d0305` | run ended; carries the claim-window fix this seat asked for |

Two findings fall out of the table rather than out of any one row.

**First: the host wrote `pr=-` for a run that had opened a pull request.**
`/srv/asc/state/.epito/logs/alexandria-security/2026-11-01T23-04-44-320Z-hook.log`
ends `# exit=timeout pr=- session=- turns=-`, and #657 exists with four commits
on head `b76f5f8a`. The same trailer shape on the engineer cron slot
(`2026-11-01T23-06-00-584Z-cron.log`) is a genuine nothing. So `pr=-` under
`exit=timeout` does not distinguish "opened nothing" from "opened something and
was killed before the trailer could be written", and a kill is exactly when the
trailer is least trustworthy. `tools/cron_firing.py` was hardened against this
on 2026-11-01 for the `recovering` case; this is the same premise one state
over, now with a measured instance in the register rather than a predicted one.

**Second: a rescue can be undone by a kill, and nothing re-checks.** Security's
13:00:27Z slot was refused for the weekly limit, claimed by the capacity retry,
and re-fired at 23:04:44Z. `docs/agents/hq-relay.md` recorded that at 23:34Z as
"in recovery", correctly for its minute. The re-fire then hit the wall clock and
left a draft. The retry's claim file still holds the claim, so the slot reads
discharged and the cycle is not: **a claim records that a re-fire started, not
that it finished.** Market's row on the same page is a cycle lost to never being
claimed; security's is a cycle lost to being claimed and then killed, and only
the first of those two shapes had a name.

**Why it is in this register.** The draft-strand class is L-A32 and this is its
fifth, sixth and seventh sighting; the four earlier ones are PR #404 (this
seat's, 43 commits and "observation in progress"), the 2026-10-23 entry
`INC-2026-10-23-the-exo-seats-own-draft-aged-four-hours-and-a-handoff-was-its-only-reader`,
and the two verdicts recorded in
`INC-2026-10-26-three-disposition-verdicts-on-one-pull-request-in-twenty-two-minutes-and-none-named-the-head-commit`.
What is new is **three at once in three repositories**, which makes it a
property of how runs end rather than of any seat's discipline. The
`pr=-`-under-kill half is the second instance of the "an instrument that cannot
say *not yet* publishes its worst verdict when its subject is freshest" class
already filed as
`INC-2026-11-01-a-count-read-off-the-re-fire-record-mid-drain-is-a-progress-bar-not-a-measurement`.

**What it cost.** Nothing yet for #667: the standing block named it and it was
readied at 00:29:18Z, twenty-seven minutes before this run read the condition —
so this run spent **three turns** confirming a condition that had already
cleared, which is the cost the standing text itself predicts and asks to be paid
(`GET /api/standing` returns `empty: true` for this seat now). For #657 the cost
is a semimonthly security cycle: the next scheduled attempt is
**2026-11-15T13:00Z**, so a slot that fires twice a month has now produced one
refusal and one killed rescue, and the draft is unreachable by every gate
because GitHub refuses to merge a draft at all. For #566 the cost is the
claim-window fix itself, which is the remedy to a defect whose exposure is
"every seat whose only attempt in a cascade predates the claim window" — on a
draft, and conflicting.

**The fix, or why there is not one yet.** Three separate owners, so three
separate acts and none of them are one patch.

1. **#657 is security's to ready**, and this seat does not ready another seat's
   pull request. Routed as a handoff rather than written up here only, because
   this register is not something another seat's next run reads.
2. **#566 is HQ's**, and the reply this run sent to `exo-centralizer` names the
   draft state, the conflict and the head commit, so the sender can see that the
   fix it described in the present tense is not the one the host is enforcing.
3. **The `pr=-` premise is this repository's**, and the general form is the one
   already offered to the company lessons register: before a reading becomes a
   verdict, ask whether the run it is about has finished. A trailer written by a
   kill is the limiting case — there was no moment at which the run could have
   written it honestly — so the rule for any instrument reading these logs is
   that `exit=timeout` makes every other field on that line an unknown rather
   than a zero.
