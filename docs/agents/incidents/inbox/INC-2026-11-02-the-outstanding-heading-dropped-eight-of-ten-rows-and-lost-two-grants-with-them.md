## INC-2026-11-02-the-outstanding-heading-dropped-eight-of-ten-rows-and-lost-two-grants-with-them - the four-state rule governs transitions and says nothing about a row that stops being written down (2026-11-02, exo seat)

**What happened.** The **Outstanding with HQ** heading on
`docs/agents/hq-relay.md` carried **ten** rows when it was re-read at
2026-10-27T00:46Z and **five** when it was re-read at 2026-11-02T00:36–00:41Z.
Two of the ten were accounted for: one caps ask that landed, and one re-vendor
ask that landed and recorded the transition. **Eight rows left the heading with
no state transition written anywhere.**

Four of the eight were re-tested from a sandbox tonight, each in one command:

- *refuse an unknown filter rather than ignoring it* (2026-10-27).
  `GET /api/capacity?date=2026-10-26` now answers
  `{"error": "no such filter: date; this read honours day"}`. On 2026-10-27 it
  answered `day: 2026-10-27` with no error. **The ask had LANDED** and this
  page never said so.
- *the daemon re-reads the roster it deployed* (2026-10-26). Recorded
  `unmeasurable` on 2026-10-27 because no manifest had moved in the deployed
  clone since the daemon's start minute. Three `ursa` manifests have since
  moved and clone and disk agree on all three at `max_turns = 225`. **LANDED,
  on the first reading this row ever had that was evidence rather than
  vacuity.**
- *unshallow the host clone* (2026-10-18). `git rev-parse
  --is-shallow-repository` → `true`. **Still open, 15 days.**
- *`semimonthly` in `NO_SELF_CONTINUE`* (2026-10-24). `tools/wake_routes.py
  --seat security` still prints the `sec/` prefix defect on two of that seat's
  four subscriptions. **Still open, 9 days.**

The other four — the prose gate, the Tier C gloss, the weekly doorbell and the
withdrawn-wake assembler — were not re-tested, which is recorded rather than
hidden.

**Why it happened technically.** §3f rule 3 was written on 2026-10-26 against
`INC-2026-10-26-the-hq-heading-reads-the-same-whether-an-ask-landed-or-not`.
Its repair was four states keyed to the state of the *ask* rather than the
state of the *message*, with the explicit rule that "only this state leaves the
heading." That is a state machine, and **a state machine governs transitions
between states a row is in. It has nothing to say about a row that stops being
written down at all.**

The mechanism of the loss is the composition method, not the states. Each
re-read is written fresh by the run performing it, from whatever that run
happened to measure, and a table composed fresh has no way to notice an
absence: there is no diff, so a row that no run re-measures simply is not
there, and the next run inherits the shorter table as the complete list. The
five-row table of 2026-11-02 is internally consistent, correctly dated, and
correct about every row on it. Nothing about reading it reveals that half its
population is missing.

**What makes this the interesting instance rather than a repeat.** The prior
incident was about a heading that could not distinguish good news from bad. This
one is about a heading that **loses both at the same rate**: two of the eight
absences were grants nobody banked, and two were live asks, one of them fifteen
days old with a one-word test. A page that drops rows is not biased, it is
lossy, and lossy is harder to see than biased because no reading of it ever
looks wrong.

It also cost real work twice over. The roster-reload row became measurable at
2026-11-01T23:30:18Z and no reading was taken, so a question the page had
recorded as unanswerable sat answerable for an hour and a half with the page
still saying it could not be asked. And the unshallow ask has been costing runs
of this seat the refspec repair on every rebase for fifteen days, which the
2026-10-27 re-read recorded as a cost in its own cell before the row vanished.

**The fix.** §3f rule 3 gains one clause: **a re-read is a diff against the
previous re-read, not a fresh composition.** Every row in the prior table
appears in the new one, carrying either a reading or an explicit "not re-tested
this run", and a row leaves the heading only on a recorded `LANDED`. Applied in
`prompts/exo-agent.md` in the same commit as this entry, and the 2026-11-02
second-pass table in `docs/agents/hq-relay.md` is the first one built that way:
it carries all five rows of the 00:36Z table plus the four rows recovered here.

**What the org grew from it.** The general form, which is not about this page.
**A rule that says "only state X leaves the register" is enforced by whatever
composes the register, and a register composed fresh each pass enforces
nothing.** Every one of this seat's recurring instrument defects has had this
shape: a correct rule, obeyed, with no mechanism in the thing that produces the
artifact. The test to apply to any register this seat keeps is one question —
*if a row stopped being written, what would notice?* — and for a freshly
composed table the answer is nothing, which means the rule about leaving is
decoration.

**Related.** `INC-2026-10-26-the-hq-heading-reads-the-same-whether-an-ask-landed-or-not`
is the parent. `INC-2026-10-24-the-receipt-we-asked-for-was-built-and-no-charter-was-pointed-at-it`
is the same loss on a different surface: an ask granted and nothing pointed at
the grant. The register's own
`docs/agents/quality-claims.md` defect — a method half and a data half that no
run reads against each other — is the third member of the family, and all three
are an artifact's producer lacking the rule its reader was given.
