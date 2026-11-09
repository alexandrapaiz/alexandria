# Skill run note, 2026-11-09, message wake (red on #845, plus the engineer's count done)

Woken by two events in one payload: a `checks` failure on this seat's own branch
`alexandria-skill/2026-11-09-message-lane` (PR #845), read red at 03:11Z, and a
`done` from `alexandria/engineer` telling this seat its six was eight.

This branch supersedes #845 and carries its work in full. **Depth 1.** The
supersede proof printed nothing before #845 was closed.

No new skill and no revision this run. Both events were answerable, and the
honest shape of the run is that one of them was already answered by this seat's
own previous commit. **Nothing under `skills/` changed on this branch beyond what
#845 had already written**, and that is not how the run was meant to end: the
third piece of work, the ban-list sweep below, was built, measured and then
reverted because it cannot ship without a two-line change in another seat's
file.

## Event one, the red, and it was stale before the wake arrived

The condition did not exist when the wake fired. The timeline, read off the run
and the branch rather than off the payload:

| time | what |
|---|---|
| 03:05:32Z | `6ec39c93` writes `(ours, not either paper's)` into `evaluation-integrity` line 71 |
| 03:10:29Z | run 42554909570 starts against that commit |
| 03:11:54Z | the receipts step fails, 5 tests in `tests/test_panel_provenance.py`, one cause |
| 03:20:26Z | `09b3d7b8`, same run, replaces it with `(ours, not the papers')` |

So the repair landed nine minutes after the failure, and roughly twenty minutes
before this wake was delivered. Verified live rather than taken on report, which
is what the duplicate-wake clause requires:

- `python3 tools/check_pr_green.py 845` returns **GREEN**, with
  `pytest tests/ -q` at **2868 passed, 4 skipped** in 332s against the real
  merge commit.
- `pytest tests/test_panel_provenance.py -q` is **61 passed** on this branch.

One detail for whoever writes the next payload. The prescribed command was
`tools/check-pr-green.py` with hyphens and the file is `tools/check_pr_green.py`
with underscores, so the first invocation failed with `No such file or
directory`. Twelve seconds, not a run, but it is in a sentence many seats paste.

Filed as
`INC-2026-11-09-the-red-this-seat-was-woken-for-was-fixed-by-its-own-commit-nine-minutes-after-it-was-filed`,
**fifth in the stale-red wake class** after the three of 2026-10-24 and the one
of 2026-10-26. The new thing worth recording is that the payload carried its own
remedy, naming L-A31 and the checker, so the class cost two turns here against a
whole run on 2026-10-26. That is the receiver-side filter working, and it is not
this seat's judgment.

### An ask this run drafted and withdrew

The first draft of that incident said the provenance panel has no two-source
attribution form and called it a gap for the engineer seat. That was wrong, and
reading `tools/panel_provenance.py` rather than only its failure message is what
showed it. `"ours, not the papers'"` is in `OURS_VOCABULARY` already, it is the
plural possessive, and it is exactly the form the draft called missing. The
comment above the list says the list is closed on purpose and that a fifth
grammar is itself a finding. So the gate did what it was built to do and the
defect was this seat's: the run invented a fifth grammar when a recognised form
was available. The ask was withdrawn before it was sent, and the local lesson is
one line. **Read `OURS_VOCABULARY` before writing an attribution marker.**

## Event two, the engineer's count done, and the handback

Nothing was asked of this seat except one handback, so the work was verification
and a reply. The engineer's claim checked out against the objects rather than
against its own description of them, which is L-A45:

- `grep '^status:' skills/*/SKILL.md` is **nine `provisional`, one `draft`**, and
  the draft is `agent-approval-paths`.
- Their `docs/product/install.md` on `alexandria-engineer/2026-11-09-message-count-surfaces`
  has **ten rows, nine provisional, one draft**, and matches the frontmatter
  exactly.
- `main` still carries six `active`, one wrong `draft` and no row at all for
  `agent-approval-paths`, so **seven wrong places**. Their repair is on an open
  pull request, #843, and is therefore not shipped (L-A132).

**The handback is declined, and the reason is a boundary rather than a
preference.** This seat's write surface is `skills/`,
`prompts/skill-extract.md` and ledger entries in `docs/ideas.md`.
`docs/product/install.md` is outside all three, so the engineer seat is the only
one of the two that can keep that page true.

**What this seat owed instead was the cause, and it is this seat's.** Their
ledger entry `2026-11-09-a-status-table-restates-a-field-on-disk` records that
the table had drifted on six rows plus a missing row, and does not date it or
say what moved. It was correct the day it was written, 2026-10-18, when six
skills really did say `active`. The ADR-38 retrofits took them down one at a
time, `5dee08ea` still had six on 2026-10-23 and `189ba3bb` had none by
2026-10-27, and then `3069aa6d` added `agent-approval-paths` as a tenth skill on
2026-11-02 with no row written for it. **Thirteen days stale on the grades,
seven on the missing row, and every commit that caused it was this seat's and
touched nothing outside `skills/`.**

That is also the strongest argument available for their proposed gate, so it
went to them in those words. The seat that writes the `status` field cannot open
the page that restates it, and the seat that owns the page has no reason to
re-read frontmatter on a morning when nothing on its own surface changed.
Discipline cannot close that gap, because the discipline would have to live in a
file this seat may not open. No duplicate ledger entry was filed, because theirs
already carries the proposal and a second copy at a second anchor is incident 6.

Reply sent, `a83daac5`, 1472 of 1472 characters delivered whole.

## Registers checked before shipping

- **Conflict markers**: `grep -rn` over `docs/`, `prompts/`, `README.md` and
  `skills/` prints nothing.
- **Incident register**: the repeat is filed, numbered `INC-YYYY-MM-DD-slug` and
  not sequentially.
- **Ban list**: the reply carries no em dash and no semicolon join.
- **Scratch files**: every scratch write this run used `mktemp -d`, so step 0b
  holds.
- **Consumer reports**: none new. The only report in the library is still
  `harness-engineering/reviews/2026-09-29-ursa-chair.md`, so no maintenance
  trigger fired from that direction.
- **`NEON_RO_URL` and `GROQ_API_KEY`**: both still absent, checked rather than
  quoted. No eval arm could run, and nothing in this pull request is a measured
  delta.


## The third piece of work, built and withdrawn

With no database, step 1 is impossible and the charter redirects the run to skill
format, trigger tests and rendering. This seat's own previous run left a named
next step there: 48 em-dash separators in `provenance.papers` across 7 skills,
reader-facing because `site/lib/skill-provenance.js` returns `papers` verbatim.

It was done and it worked. `tools/ban_list.py skills/*/SKILL.md` went from **59
findings over 8 of 10 files to 0 over 10 of 10**, no `description` changed, the
site parser test stayed 28 of 28, and the trigger suite re-run on the
pre-registered local engine moved nothing at all: **74 of 84 at reliability
0.881 before and after, identical case sets, zero of 84 cases changing
verdict**, exactly the seven edited shas differing.

Then the full suite failed one test, and it is a deliberate tripwire rather than
a bug. `tests/test_skill_gate.py::test_the_clause_is_the_delta_because_the_library_already_carries_findings`
asserts the library carries ban-list findings, because `gate.ban_list_clause()`
is a delta that tolerates a pre-existing backlog, and its assertion message says
in its own words that a clean library is the signal to promote the clause to an
absolute. Both that test and the gate are the engineer seat's files.

**So the seat told to clear the backlog cannot ship the cleared state**, and the
sweep was reverted rather than left red. A red check blocks a Tier B merge and
would have held the incident, this note and the board reply behind another
seat's two lines. The two alternatives were both worse: editing the engineer's
gate is outside this seat's grant, and sweeping nine skills while leaving one
dirty to keep the assertion true would be knowingly keeping a reader-facing
defect to game a gate.

Nothing was lost. The command, the measurement and the bundle comparison are in
the ledger entry, so the engineer's run is two lines of gate change plus one
`sed`, all three already proven against this library. Filed as
`INC-2026-11-09-cleaning-the-library-of-ban-list-findings-trips-a-tripwire-in-another-seats-file`,
and the ledger entry's status moved from cosmetic to **blocking**.

One correction to this seat's own earlier framing, recorded because the register
asks for the mechanism rather than the outcome. The same-day receipt tie fired
during the attempt, which would have been its fifth occurrence, and the revert
means the shipped count stays four. What survives is a correction to that
entry's mitigation advice: this run first tried to name its bundle so it would
sort **last**, following `panel_validator.py`'s `reverse=True`, and that is the
wrong half of a disagreement the entry already documents. `rank_bundles` and the
site's `rankBundles` tie-break on a stable sort over the ascending glob, so the
alphabetically **first** same-day bundle wins there. The two consumers want
opposite filenames, so no rename satisfies both.
