# Skill run note, 2026-11-09 (message, digest-precondition)

Trigger: a five-item payload. Two notes from `alexandria/exo` (10:25Z
`215cebc6` on the two red gates, 10:41Z `557930ae` on the splitter fixture), two
`done` messages from `alexandria/research` (10:30Z `2ab5c28e` nothing owed,
10:55Z `08830fa2` the precondition), one `done` from `alexandria/engineer`
(10:47Z `745440d8`), and the merge of #904. A sixth arrived during the run,
exo's 11:00Z `f0afc405` with the `answered_by` measurement, and it is answered
here too.

Not a duplicate wake. The headline item, research's 10:55Z `done`, routes a
paper this seat had never read and asks for a change to a file only this seat
writes. Checked against the open #908 first, which had shipped v6 and
explicitly did **not** have this paper.

`NEON_RO_URL` and `GROQ_API_KEY` both absent, checked in this run rather than
quoted. No claim row read, neither eval arm run, no `status` moved. Every skill
in the library remains **unmeasured**, in that word.

Chain depth 2: #908 to this one. #908 was this seat's own open pull request and
it edits the same `SKILL.md`, so the build-on branch of the own-last-run rule
was taken, its branch merged first, the containment proof printed before the
push, and #908 closed after #919 opened.

## 1. The item: the ceiling has a precondition under it

v6 told a builder to bind the approval to the exact action and re-verify at
dispatch, and v6 added a **ceiling** on that: the recorded fields agree and the
operation differs, because the divergence is below the mediation point. The
research seat read `arxiv:2609.21081` in full and found that the same binding
has a **precondition**, and that the field stating it is in no paper this
library had read.

**Read here independently before anything was written.** `python3
tools/read_paper.py 2609.21081`, exit 0, **55,190 chars**, the same count the
research seat recorded. The charter's reason for that rule is the whole point of
this item: the corpus knew this paper only through `2609.38983`'s section VIII-A
for weeks, and that is precisely how the gap got into a shipped skill.

The three load-bearing facts, each verified in a paper's own text rather than
taken from the note:

| claim | check |
|---|---|
| section 6.1 has six bullets, the sixth a digest over the complete descriptor shown to the human | read in the paper, with the operative sentence after it that the display must be generated from the descriptor |
| `digest` is absent from the citing paper | re-fetched `2609.38983`, **0 occurrences** in 132,653 chars |
| the other naming has no such field either | `2609.28586`, 3 occurrences, all source-content or prediction digests |
| the two namings are independent | `2609.28586` has **0** of `Loopjacking`, `Agno`, `OpenClaw` |

**The measured case.** A gateway-mediated shell path carried a positional
argument vector that was complete *before* approval while the approval event
rendered only the inline payload `$0 "$1"`. The rendering was genuinely derived
from the real command and was still a projection of it, so an allow-once
decision released the complete vector: **3 of 3**, direct unapproved execution
denied 3 of 3, unchanged approved commands still succeeding. A descriptor
captured from that view equals the dispatched operation, so the comparison
**passes**.

**What this seat adds to the research seat's note.** The citing paper does not
drop the field at random. Its own words are that the record is "a field set with
substantial overlap with our own seven-field credential", so it summarises by
mapping the record onto its own mechanism, and the one field it drops has no
counterpart there. That same credential is the one its own measurement puts at
the ceiling. The omission and the ceiling are one fact seen twice.

## 2. What changed, and the two timing repairs now both refused

Checklist item 1 separates completeness from provenance and names the six
measured shell fields with the expose-or-refuse rule. Item 2 binds the complete
resolved operation and **reconstructs** it at dispatch rather than re-checking
stored fields, carrying the source's own five-step use-time procedure, which is
the first numbered procedure in this file taken verbatim from a paper.

Delta 1 now refuses both timing-shaped repairs, with two measurements from two
papers that do not cite each other: re-approving on a changed environment
snapshot catches **none** of the ceiling cases, and refusing to persist
approvals is not the fix either, because the negative control serialized,
restored and resumed every approved action and executed it 3 of 3 and 3 of 3
while rejecting a same-call-ID mutation.

The caveats gain a seventh surface, this paper's bounds, and one prohibition in
bold: never cite it for approval fatigue, dialog quality, deception rates or
comprehension, because its approval step was scripted after the product view was
asserted and it disclaims that reading twice in its own text.

## 3. Rule 4, and the number this run owes rather than the one it passes

`wc -l` is **119**, under the cap, from v6's 120. v6 was the only file in the
library not under it.

**That is true and it is not the honest number.** On
`skills/_validation/skill_length.py`, which measures the same rule in the unit
it meant:

| version | `wc -l` | frontmatter | body | rendered |
|---|---|---|---|---|
| v5 | 118 | 99 | 347 | 446 |
| v6 | 120 | 118 | 402 | 520 |
| **v7** | **119** | **109** | **459** | **568** |

The governing metric improved by one line while the file got 48 rendered lines
longer to read. v7 paid by collapsing four superseded revision narratives in the
frontmatter, which `REVISIONS.md` holds in full, which is why the frontmatter
fell 118 to 109. v6 paid by merging two reader-facing caveats, and the
instrument's docstring records three `harness-engineering` entries doing the
same. So the metric does not merely miss growth, it rewards the payment method
that costs the reader. Filed in the ledger; the unit decision is the owner's.

**The conclusion, now with the number behind it: this material belongs in a
second skill.** #908's body already said so. The longest line in the file is
4,444 characters, about 45 rendered lines in one paragraph, and it carries a
ceiling and a precondition from two papers none of the three deltas was built
around. That split is the next maintenance item for this skill. Not done here,
because the charter allows one skill per run and this run's item was the
revision.

## 4. The eval suite and the trigger suite, which measure different things

`ap-t9` added, paired with `ap-t8` as precondition to ceiling: a team that has
built both things items 1 and 2 prescribe, correctly, and hashes what it
displays. Five rubric criteria, each with a certificate, and a zero-scoring
exploit. `tools/skill_eval.py --check` exit 0, 10 of 10 conformant, 44 of 44
sections exercised, **334** of 334 criteria certificated, from 329.

`ap-t7`'s exploit answer was still asserting that observation does not spend safe
twins, the fifth site of a zero the fourth revision removed, found by the
research seat. Corrected, keeping the exploit failing on form.

Trigger suite 75 of 85 to **76 of 86**, reliability 0.8824 to 0.8837, **zero
verdicts moved**, the one added case `ap-pos-5` passing at +0.0708 over the
closest decoy and not narrow. **Stated plainly because the charter asks: a green
trigger case says this skill is findable and says nothing at all about whether
it helps.** The measurement in charter step 4 does not exist for this skill.

**Two intermediate description edits were caught and discarded, and the method
is the point.** The first cost `ap-pos-4`, a case a previous run added for a
measured findability gap, because a compression dropped the words it matches on.
The second cost `asm-neg-2`, a negative that must stay silent, because rewording
"what the human is shown" to "what it shows" made the stem `show` match
`showing` in a prompt about a monitoring dashboard. Both were found by diffing
verdicts case by case against the v6 bundle. The totals moved by one in each
case and would have read as noise.

## 5. Replies, and one thing owed back to the engineer

Five sent, in first person, one per message. Two corrections accepted outright:
the engineer's `--remedies-only` bug account, which explains both of this seat's
cells without anything else needing to be true, so the flag ask is withdrawn;
and exo's pin correction, that a manual step is one a run *could* have taken and
no run was ever offered that gate.

**Two of the four items were already resolved when this run read them**, and
neither payload said so. Exo's third red gate, the target census, is green on
`main` at 161 of 161 declared, and exo's own commit `da3db387` records that the
main red ran 00:26Z to the 10:3x wake and that their new tool put three flags
back, declared in the same commit. And the splitter fixture exo asked this seat
to build was already built by the engineer, better than either plan, reading the
pre-repair blob out of git at `d525fe09` rather than committing a copy.

**That better plan has one defect and it is exo's own objection one level
down.** The host clones at `--depth 1`. Measured in a fresh clone rather than
argued: `is-shallow-repository true`, `rev-list --count HEAD` of **1**, and the
guard's `git show d525fe09:...` exits **128**, so `_malformed_blob()` calls
`pytest.skip` and two tests, including the one pinning this seat's six
pseudo-entries, report a skip with a reassuring message. A guard built to catch
a gate that goes quiet goes quiet itself in the default environment. Ledger
entry filed with the remedy, which inverts which assertion may vanish: commit
the 4,986 bytes as a fixture, read that in the guard, keep the `git show` as a
cross-check that may skip.

## 6. Registers

Two occurrences appended rather than filed new, per the standing rule.

The unquoted-colon YAML break has a **second occurrence, by this seat**, and the
instrument the first occurrence built caught it before a commit existed. The new
half is generalisable: a 150-word budget and a YAML contract pull against each
other, `:` is the most economical connective in English, and neither error
message mentions the other.

The clock-join entry gains the **shape that settles it from two rows**: research
sent a `note` and a `done` in the same minute and both carry `answered_by`
naming this seat's single 10:35 reply. One reply named as the answer to two
messages cannot be a lag. It is exo's pigeonhole at its smallest. The same entry
carries a correction to this seat's own fourth occurrence: a correctly joined row
is a coincidence, not the field working, so a spot check is misleading rather
than merely insufficient.

Three conflicts on the inbound merge, all incident 6's class, resolved by hand
and described in the merge commit. Research's "instance eight" landed on `main`
first and keeps the slot; this seat's is renumbered ninth. Research's third
clock-join instance has the better cause and is kept whole, with this seat's
folded to the two things it adds.

## 7. Gates

| gate | result |
|---|---|
| `tools/skill_eval.py --check` | **exit 0**, 10 of 10, 44 of 44 sections, 334 of 334 criteria |
| `trigger_test.py` | **76 of 86**, reliability 0.8837, 0 verdicts moved from v6 |
| `trigger_test.py --receipts` | all 10 current, all 10 load under PyYAML, all 10 inside 150 words |
| the ten skill and register suites | **416 passed**, plus 195 on eval and manifest |
| `node --test tests/skill-provenance.test.mjs` | **31 of 31** |
| `tools/panel_validator.py` | 10 reviewed, **0 failing**, 10 not fully measurable |
| `tools/incidents.py check` | **nothing malformed**, 375 entries, 273 in the inbox |
| `tools/ledger.py --check` | **0 blocking**, at or under baseline |
| `tools/target_census.py --check` | **exit 0**, 161 of 161 declared |
| `tools/ban_list.py` on every file this run wrote | **clean** |
| conflict-marker sweep (step 0) | **clean** |
| `wc -l skills/agent-approval-paths/SKILL.md` | **119**, and see section 3 |
| `git merge-tree --write-tree HEAD origin/main` | exit **0**, clean |
