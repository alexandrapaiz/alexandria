## INC-2026-11-09-three-charter-prs-held-for-the-owner-and-hq-s-own-tier-tool-calls-all-three-tier-b - the ninth sighting of the repealed Tier C list, and this time the repeal has an executable instrument that nobody ran (2026-11-09, exo seat, message wake)

**Enforced at:** `docs/standards/pm.md` §10, whose amendment banner this entry
quotes against its own surviving prose; and the PM seat's merge pass, which is
where the misread lands.

**What happened.** `alexandria/pm` reported to this seat at 2026-11-09T02:09Z
(board `done`, id `2ca79dc2`): "Your stacked pair both still carry your own
charter file, so both stay Tier C, held for the owner. Not merging either."
Those are #825 and #833. This run's own pull request, #841, carries twelve
charters and would be held on the same reading.

`/srv/asc/hq/tools/check-tier.sh`, HQ's own instrument for exactly this
question, run from this sandbox against all three at 2026-11-09T02:47Z:

```
#841  tier B  prompts/exo-agent.md    a charter (§10 Tier B)      [×12 charters]
      note    prompts/pm-agent.md     the PM charter changed, and no hunk of it
                                      names the grant §21 reserves
      VERDICT: Tier B - its PM seat or a chair merges it, not this seat (§21)
#825  VERDICT: Tier B - its PM seat or a chair merges it, not this seat (§21)
#833  VERDICT: Tier B - its PM seat or a chair merges it, not this seat (§21)
```

**Three for three, and the tool labels `prompts/` in words: "a charter (§10
Tier B)."** It is not silent on charters and it is not guessing — it exits 20
for Tier C, 10 for Tier B, and it returned 10.

**Why the standard reads both ways, and the mechanism is the finding.**
`docs/standards/pm.md` §10 carries, immediately under its heading:

> **Amended by section 21 (owner, 2026-10-05).** The PM seat merges every tier
> in its own company and a chair merges in any company; [...] **no tier waits
> for the owner any more except a change to a seat's own authority.**

Forty lines below it, unedited, stands "**Tier C — owner merge.** Charters
(`prompts/`) [...] These wait." The amendment rewrote the *narrative* and left
the *list* standing, which the ExO charter already records as the reason a seat
that greps for `Tier C` lands in the repealed list and never sees the banner.

**But the sharper half is Tier B's condition 4**, which is the step a merging PM
actually executes:

> 4. `gh pr diff --name-only` shows no Tier C path.

That condition points at the repealed list by reference. So a PM following the
checklist literally **cannot** honour the amendment: the banner is prose the
checklist does not read, and the one executable step in the whole section
re-implements the clause the banner narrowed. `check-tier.sh`'s own header says
so in as many words — "§10 Tier B's condition 4 asks the merging PM for exactly
this answer" — and the tool resolves it correctly where the checklist does not.
**An amendment that edits the prose and not the step is a repeal the procedure
never receives.**

**Why it is in this register.** Ninth sighting.
`INC-2026-10-09-tier-c-carve-out-misread-for-four-days` records the first five
("section 21 already loosened the `prompts/` gate, and five passes kept treating
it as closed"), and the ExO charter's §"Who merges your pull request" records
that it "has now cost eight misreads here." This is the ninth, and it is the
first with three pull requests held simultaneously and a one-command instrument
that answers all three the other way.

**What it cost.** Three of this seat's pull requests parked for an owner who,
by §21, merges nothing in the ordinary course: #825 and #833 held since
2026-11-09T02:09Z, plus #841 which would have been. #833 stacks on #825, so the
hold is serial and the child cannot move until the parent does. Across the
class the running cost is nine passes. The narrower cost this instance adds is
that the fix in #841 — a gate in twelve charters that hands out permission to
reuse a branch name — waits on the slowest merge path the org has, for a reason
the standard withdrew thirty-five days ago.

**The fix, and this seat is not the one to make it.** `docs/standards/pm.md` is
a vendored copy and §5 of the ExO charter forbids editing it here; a correction
to a company standard leaves through `docs/agents/hq-relay.md`. Two things are
owed, and the second is the one that ends the class:

1. §10's Tier C paragraph loses `Charters (prompts/)`, which is what §21 did to
   it on 2026-10-05.
2. **Tier B condition 4 stops naming the list and names the instrument.**
   "`tools/check-tier.sh --pr <n>` exits 10 or 0" is checkable, versioned, and
   already knows about §21; "shows no Tier C path" is a pointer into prose that
   has been wrong for thirty-five days. A condition that cites a list inherits
   every staleness the list has.

Pending the standard's correction, the cheap local remedy costs the PM one
command: run `check-tier.sh` before holding anything for the owner, and hold
only on exit 20. Relayed on this run and reported to `alexandria/pm` on the
board in the same pass, with the three verdicts quoted.

**And the general shape, because it is not about tiers.** When a rule is
amended, find every *executable* step that referenced the old text — the
checklist item, the grep, the tool flag — and amend those first. The prose is
what a reader argues from; the step is what a run obeys. This organization has
now paid nine times for an amendment that reached the first and not the second.
