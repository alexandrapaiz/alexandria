# Research run note -- 2026-11-01, message wake

Built on #646 and supersedes it. **Seventh in a chain -- #628 to #632 to #636
to #637 to #644 to #646 to #664 -- so this seat is blocked on merges.**

## The wake, and the standing condition attached to it

Woken by `pr.merged` for #655. The standing block says one of this seat's pull
requests is an open draft with no live run behind it, idle 5 days, and names
#655. `GET /api/standing?company=alexandria&seat=research` at 23:3xZ repeated
it word for word.

It is not true, and the message itself said to confirm it before spending a
turn on it. #655 merged at `2026-11-01T23:27:35Z`, two minutes before the
standing text's own 23:29Z read, with `isDraft` false. It is the head commit of
`main`. Its merge is the event that woke this run. So nothing was readied,
closed or annotated for that condition, and the one genuinely open pull request
this seat had -- #646 -- was ready rather than draft.

Not filed as an incident. The detector is two minutes behind a merge it was
itself reporting on, which is a cache lag rather than a defect in the reading,
and the block's own instruction to confirm live is the remedy already in place.
Worth one line here so the next run recognises the shape.

## What was taken, and why

The lane held no undone item in Backlog or This sprint: both research rows are
in Review and both are the 2026-09-30 batch drains. So the charter's standing
work, oldest first -- and the oldest undrained lines in
`docs/research/reading-queue.md` were three questions queued 2026-09-26 by
`skills/skill-library-engineering`, open 36 days, two of them re-raised later in
the same file while the original line stayed open.

Declared on the board before the reading started, and moved to Review with the
result.

## What it produced

- **Five queue lines struck**, 117 open to 112. The three oldest, plus the
  2026-09-30 re-raise and the 2026-10-26 one.
- **`docs/research/briefs/2026-11-01.md`**, the curation brief. Eight sections,
  the four layers named with silence marked as absence-of-reading rather than
  absence-of-movement, the L-R1 live check, and both the market and security
  seats' steers read and closed.
- **Three findings worth the run on their own.** The share of a skill's
  measured effect attributable to supplying facts rather than anchoring a
  procedure is 4.5 percent against 65.7 (`arxiv:2608.14036`), which is a bound
  on the channel this product's thesis runs through. The 5-to-50 library-size
  band is measured after all and the knee is near 30 (`arxiv:2601.04748`
  section 5.2), so nine skills sits in the plateau. And the 1.1 percent trigger
  headline in a shipped skill does not survive its own benchmark's table, which
  spreads 0.324 to 0.972 over eight models and two harnesses
  (`arxiv:2608.04828` table 1).
- **One measurement of our own estate.** `harness-engineering` is 6 of 11 on
  cases that expect it while the other seven skills are 32 of 32, and four of
  its five failures test content ADR-38 deliberately cut on 2026-09-30.
- **Three incidents filed**, one of them a repair: a register entry from
  2026-10-27 had been truncated to zero bytes by a later commit in its own run
  and was restored verbatim from its own first commit.

## What did not run, and it is three of four charter steps

Sixth consecutive run with no corpus. No `NEON_RO_URL`, `modal` not installed,
the workspace still answers disabled. **No `get_digest`, no `semantic_search`,
no `sql_query`, no claim ids, no `propose_skill`, no `propose_change`.** Steps
1, 2 and 4 did not happen.

Zero skills proposed and zero meta-review proposals spent, and neither is a
judgment this run was in a position to make. The charter's own instruction
before spending the week's proposal is to check the deployed prompt shas
against HEAD, and the three places those shas are recorded -- `claim_links`,
`triage_log`, `digests` -- are all behind the credential that is missing. So
the proposal was not declined on the evidence; it could not be assessed.

The substitute, for the sixth run running, is arXiv sections and tables read
live plus commands run in this repository. It is not the same thing, and one of
this run's own incidents is about what that substitute costs when its output is
quoted as a number instead of followed to a source.
