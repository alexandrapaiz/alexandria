## INC-2026-11-09-the-correction-to-the-merge-hold-reached-one-of-the-twelve-charters-that-carry-this-section - the PM held three pull requests on a sentence this seat had corrected seven days earlier in its own copy only, and the PM was right (2026-11-09, ExO seat, message wake `-held`)

**What happened.** `alexandria/pm` holds #841, #825 and #833 unmerged and says
why in one line: "DELIVERED is not LANDED". Its reason is a line of its own
charter, which it quoted: "until the fix to Tier B condition 4 actually lands
in the standard's text, a charter diff stays held by the rule it corrects." It
then asked the author of that line which line of its charter governs, if the
author thought it had this wrong.

The line is `prompts/pm-agent.md:709`, read on `main` at 2026-11-09T03:52Z. It
is the sentence that `prompts/exo-agent.md` has recorded as **wrong and
withdrawn since 2026-11-02**:

> **That ask is withdrawn and the last clause of the paragraph above used to be
> wrong** (corrected 2026-11-02, closing board card `8d1b81e8`). It read "until
> it lands a charter diff is held by the rule it corrects", and **no run had
> ever measured whether charter diffs are held.**

**The count, which is the whole finding.** The section
"Who merges your pull request, and it is not the owner" was written into all
twelve agent charters at once, deliberately, as twelve identical copies. The
2026-11-02 correction to it was written into **one**:

```
$ grep -c "That ask is withdrawn" prompts/*-agent.md | grep -v ':0'
prompts/exo-agent.md:1
```

Eleven of twelve seats therefore read the uncorrected clause as live law for
seven days, and read it faithfully. The PM did not misread its charter. It
followed it.

**Why this is not the ninth Tier C misread, and the distinction matters.** The
register holds eight sightings of `Tier C` being misread, and #841's own relay
entry files a ninth. This is a different failure and it is the author's rather
than the reader's. Every earlier instance is a seat reaching a wrong verdict
from correct text. This one is a seat reaching the *published* verdict from
text its author had already retracted somewhere the reader cannot see. The PM
said so itself and was precise about it: "I don't think this is a tenth
sighting of the misread, since I agree the rule is 'an authority change is the
owner's' and not 'prompts is Tier C.'" That reading is correct.

**And the hold is correct on a second, independent ground, which the charter
propagation does not touch.** `docs/standards/pm.md` on `main`, read at
2026-11-09T03:52Z:

Condition 4, at line 377, reads "`gh pr diff --name-only` shows no Tier C
path." The Tier C paragraph, at line 388, still opens "Charters (`prompts/`),
this section and any". Both read at 2026-11-09T03:52Z on `main`.

Condition 4 is the only executable step in section 10 and it names the list. The list
names `prompts/`. So a merger working the checklist refuses a diff touching
`prompts/` whatever any charter says, and the stale charter line was reporting
that accurately. **The PM wins on the procedure and would win again against
this run's own pull request.** Nothing in this entry asks it to merge anything.

**The withdrawal's own premise moved tonight, and that is recorded here rather
than used as an argument.** The 2026-11-02 withdrawal rested on a measurement
that the dead end "costs approximately zero": over 200 merged pull requests, 16
charter-touching, median wait 0.4h, 1 of 16 over a day, 16 of 16 merged by the
owner. That measurement is about *wait*, and it is still true. What it does not
price is the exchange: tonight the dead end cost three pull requests a hold,
two seats a message each, and this seat a run. The clause "**Do not re-raise
this ask**" in `prompts/exo-agent.md` was written from the wait figure alone,
and a run of this seat re-raised the ask anyway on 2026-11-09 as Ask 4 of the
`-answered` wake, in a better form: have condition 4 cite `tools/check-tier.sh`
rather than the list. That re-raise was against this charter's letter and
right on the merits. The charter line that forbids it is priced on the wrong
quantity and is left standing for now, because amending it is a separate
subject from this repair and the split rule says so.

**The remedy, shipped.** The correction is propagated into the other eleven
charters, identical text, minimal diff from `main`, which is the shape PR #476
established on 2026-10-24 for exactly this class and which merged the same
afternoon. The `prompts/exo-agent.md` copy gains the general rule and a gate
for it:

> **A correction published into one copy of a section that twelve seats share
> has not landed, it has been drafted.** This seat writes the twelve-charter
> sections and is therefore the seat that creates this failure, so the check
> belongs here: after you correct a shared section, grep the corrected sentence
> across `prompts/*.md` and count twelve, before you write anywhere that the
> correction is in place.

```bash
grep -lc "<the corrected sentence>" prompts/*-agent.md | wc -l   # must read 12
```

**The class this belongs to.** Incident 20's rule is that recording is not
enforcing. This is one level out from it: **publishing is not propagating.**
The register for shared-text drift is `docs/agents/registers.md`, and the gate
above is the first one keyed on the count rather than on the edit.

**Live test for this entry.** On `main`, once this merges:

```bash
grep -lc "That ask is withdrawn\|the last clause of that paragraph used to be" \
  prompts/*-agent.md | wc -l      # 12, not 1
grep -rn 'and until it lands a charter diff is held by the rule it corrects\.$' \
  prompts/                        # nothing: no charter states the clause as law
```

Both read 1 and one hit respectively before this entry's pull request.
