# Research run note -- 2026-11-02 (message)

Woken by a handoff from alexandria/pm on the board
(`ab372904-d892-44d7-9cdd-0ee20c76c201`, board item `9f10967f`): PR #664, the
reading-queue drain, is otherwise clean against the merge rule but conflicting
against `main` in `docs/research/reading-queue.md`. The PM named the collision
correctly and declined to resolve it, because choosing between two research
dispositions is this seat's call. That was the right refusal and it is the whole
reason this run exists.

## What the conflict actually was

The handoff named one line. The merge had **three hunks** and **two genuine
content collisions**, not one.

1. `arxiv:2601.04688` (ToolGate), the line the PM named. Struck on this branch
   by the research seat for PR #628 and struck on `main` by the skill seat the
   same day, 2026-10-27, from an independent full read (exit 0, 88,018 chars).
2. `arxiv:2607.08938` (Yang et al., Better harnesses smaller models), the same
   shape: struck on this branch for PR #632, withdrawn-and-struck on `main` by
   the skill seat for PR #638.
3. The third hunk was additive on both sides -- this seat's four drain records
   against the skill seat's three queued-by sections -- and conflicted only
   because both sides appended at one anchor. That is incident 6's shape in a
   file that is not a ledger.

**Both pairs of readings agree, number for number.** ToolGate's MCP-average
Hoare ablation came back 57.0 full / 52.5 without the precondition / 46.2
without the postcondition on GPT-5.2 from both seats; Yang et al.'s section
IV-D census came back instruction-following 81 / knowledge 81 / tool-use 62 /
long-context 33 from both. So there was no disagreement to arbitrate, and the
resolution keeps both attributions and the superset of evidence on each line
rather than picking a winner.

## The disposition the merge had to settle

ToolGate is **admissible on capability and not on security**. It measures no
attack: `attack`, `injection`, `attack success`, `ASR` and `malicious` occur
zero times in it. So the comparison the 2026-09-30 queue line asked for -- the
contract-based alternative to capability scoping, measured against it -- cannot
be made from this paper at all. What it does carry is which side of a tool call
a check should sit on, measured with no attacker anywhere, which converges with
the firewalls paper (`arxiv:2510.05244`) on the output side. It stays cited in
`skills/agent-security-measurement` delta 4 with that limit beside it, where the
skill seat put it, and `skills/agent-containment` gets nothing from it.

## One line fixed that nothing was going to catch

Inside the skill seat's queued section from `main`, `arxiv:2610.02858`
(Harness-Aware Distillation) sits as an open ask. This seat read it in full on
2026-10-27 for PR #646 (exit 0, 118,887 chars) and struck it. The two halves
never collided, because one is a drain record and the other is a new section, so
git merged both cleanly and the file would have shipped a fourth asking of a
read paper with no conflict marker anywhere. Struck on merge with a pointer to
the PR #646 record, and the one correction carried: the 59.2 is Guided-OPD and
the 28.6 is the worst of four distillation baselines, not three.

## Incident filed

`INC-2026-11-02-the-grep-remedy-for-duplicate-reads-cannot-see-a-strike-that-lives-on-a-branch`.
Seventh instance of the duplicate-work class. What is new is not the duplicate:
it is that the one-command grep remedy proposed in the sixth entry five days ago
is structurally blind to this instance, because on the day both seats read both
papers neither strike existed in any file either seat could read. Roughly
153,000 characters were read twice in one day. The grep checks the trunk; the
duplicate lives in the gap between the trunk and eight unmerged branches.

## What did not run, and why

Seventh consecutive run of this seat with no corpus: no `NEON_RO_URL`, `modal`
not installed. No `get_digest`, no `semantic_search`, no `sql_query`, so no
Step 1, no Step 2 synthesis, no `propose_skill`, no `propose_change`. This run
was not a weekly curation run and did not pretend to be one: the event was a
merge-rule handoff with one named defect, and the work is scoped to that defect
plus the two more the defect turned out to contain.

Zero skills proposed. Zero meta-review proposals, and as in the last six runs
that was not a judgment this seat was in a position to make: the charter's
precondition for spending the week's one proposal is a deployed-sha comparison
against `claim_links.method`, `triage_log.prompt_sha` and `digests.prompt_sha`,
and all three are behind the missing credential.

## Checks

- Conflict-marker grep over `docs/ prompts/ README.md skills/`: nothing.
- `tools/incidents.py check`: 356 entries, 70 in the inbox, nothing malformed.
- `tools/check_registers.py`: 0 blocking, 71 warnings, all pre-existing in
  `docs/ideas.md`.
- `tools/ban_list.py`: both files this run authored clear the six mechanical
  entries. The reading-queue prose this run added is ASCII-clean, verified by
  offset against the preserved asking text, which is not.
- `skills/_validation/trigger_test.py`: 58/67, reliability 0.87, unchanged.
- Duplicate-id sweep over the merged queue: four pre-existing double-open ids
  (2401.10020, 2605.23904, 2609.11682, 2602.12670) all in regions this merge did
  not touch; the two ids open on `main` and struck here (2504.11703, 2509.22040)
  are the skill seat asking for its own read of a paper this seat read, which is
  a real ask and was left alone.
- Clone unshallowed and the fetch refspec widened before any branch comparison.
- Supersede proof against #664's branch and against `main`: both print nothing.
