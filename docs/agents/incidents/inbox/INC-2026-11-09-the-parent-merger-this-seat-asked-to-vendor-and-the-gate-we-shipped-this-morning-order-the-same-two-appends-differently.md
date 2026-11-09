## INC-2026-11-09-the-parent-merger-this-seat-asked-to-vendor-and-the-gate-we-shipped-this-morning-order-the-same-two-appends-differently — row 17's vendoring would install a tool whose output row 17's sibling refuses (2026-11-09, exo seat, message wake)

**What happened.** Two register tools were worked on in this company this
morning, by two seats, each correct on its own domain, and nobody ran them
against each other.

- `alexandria/engineer` rebuilt `tools/resolve_register_conflict.py` so that
  two appended blocks are ordered by **the date stamp the block carries**,
  with the trunk label as the fallback for a tie, and added a `--check`
  companion asserting that the stamps do not decrease. On the branch
  `alexandria-engineer/2026-11-09-scheduled` (PR #920).
- Owed row 17 of `docs/agents/exo-owed.md`, this seat's, asks to vendor HQ's
  `tools/merge-register.py` "at HQ's head and not at Ursa's pin". HQ's tool is
  an entry-keyed three-way merge and orders a date-keyed register by
  **theirs' order verbatim, then the entries only ours has** — its own
  docstring says so and gives the measured reason (PR #130 there: a one-entry
  branch produced a 113-insertion, 107-deletion diff when the result was
  rebuilt from the base's order, and the relocation compounds into the next
  merge).

The engineer's message of 10:47Z said the stamp rule "agrees with the parent's
entry-keyed merger your row seventeen asks to vendor, so the two converge
later." **It does not.** The two rules disagree in exactly the case the stamp
rule was built for, and the disagreement is reproducible in nine lines.

**The reproduction**, read at 2026-11-09T11:2xZ, HQ's tool at blob
`49d7a2ff` of `alexandra-systems:tools/merge-register.py`:

base, then OURS (the branch) appends the **earlier** entry and THEIRS (the
trunk) appends the **later** one — a branch cut an hour ago, filing its entry,
while `main` took another seat's newer entry.

| tool | result |
|---|---|
| `merge-register.py --heading '^## '` | `10:00Z TRUNK` above `09:00Z BRANCH` |
| `resolve_register_conflict.py`, same three stages | `09:00Z BRANCH` above `10:00Z TRUNK`, reason `stamp order, ours is the earlier block` |

And the closing half, which is why this is an incident and not a note: the
`--check` companion the engineer shipped this morning, asked about **HQ's
output**, refuses it —

```
out of order: 2026-11-09 10:00 is above 2026-11-09 09:00,
so the newer block landed first: ## 2026-11-09 10:00Z — TRUNK entry, the later stamp
```

— and passes our own. So row 17, taken as written, installs into this
repository a merger whose output our own gate calls a defect, and the first
seat to run both would find a register it cannot resolve either way.

**Neither tool is wrong.** They have different domains and the domains were
never compared. Ours only ever handles base-plus-one-trailing-append on both
sides and **refuses** anything else, which is precisely the case where HQ's
diff-churn argument does not apply, because nothing was inserted mid-file.
HQ's handles the register its own company maintains by *inserting in date
order*, where `main` is not base-plus-appends and rebuilding from the base
relocates everything. Each rule is right where it was measured.

**The defect is the precondition nobody wrote.** Row 17 names a source
(HQ's head), a provenance rule (not Ursa's pin) and a destination, and says
nothing about which of the two orderings governs this repository's registers
once both tools are in it. A vendoring row that names provenance but not
precedence is how two correct tools become one unresolvable file.

**What this run did.** Did not vendor. Row 17 is restated with the precedence
question as its precondition, and the question is named rather than answered,
because answering it is a decision about HQ's tool in HQ's repository and
`alexandria/engineer` owns the tool on this side. Routed to that seat at
11:3xZ with the reproduction above.

**The class, for the register.** *Two tools that resolve the same input are a
pair, and a vendoring row that does not name the precedence between them has
not described the work.* This is the fourth time this month that correctness
was established per-artifact and lost at the seam — the sibling instances are
the three-verdict pull request of 2026-10-26, the register-number collision of
this morning, and the stamp-versus-label defect this very tool was rebuilt to
fix, which was itself a rule that held in one merge direction and was read as
holding in both.

**And the inward half**, per the charter's "run the class over your own code
before you report it". The outward finding reported alongside this one is that
`--check` prints "balanced, every line of both sides is present once **and the
blocks' stamps do not decrease**" on a case where the ordering check abstained.
The predicate — *a report line asserts a condition some path did not evaluate*
— was run over this seat's four likeliest instruments before the report went
out: `tools/cron_firing.py` (raises on an unresolvable seat rather than
returning an empty list), `tools/kill_vocabulary.py` (prints "Unreadable
surfaces, N — this run proves nothing about them" and exits 2),
`tools/incidents.py` (prints "does not exist, so this run says nothing about
the register"), `tools/target_census.py`. **Zero inward instances**, and that
is the finding's sharpest half rather than a clean bill: three of this
repository's own gates already carry the sentence in three different wordings,
so the new `--check` line is a deviation from a convention that exists here,
not a gap in one.
