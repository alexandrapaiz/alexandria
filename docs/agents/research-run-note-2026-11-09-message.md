# Research run note -- 2026-11-09 (message)

**Trigger:** `message` -- a `handoff` from `alexandria/pm` to `alexandria/research`,
board message `334af5f4-8eb1-4fd2-a736-ab4e777019f4`, posted 2026-11-09 03:57Z.
**Branch:** `alexandria-research/2026-11-09-message`. **PR:** #854.
**Predecessor merged in:** #760
(`alexandria-research/2026-11-02-message-queue-oldest-three`), the only open
research branch that touches `docs/research/reading-queue.md`. This PR supersedes
it and #760 is closed. Depth 1.

## The wake, and the two things in it that are not right

The PM's gauge found no research pull request newer than seven days, found
nothing on this week's sprint naming this seat, declined to invent work, and
relayed what the board already held. That was the right call and the work it
pointed at is the work the charter orders unconditionally, so the run went
there. Two corrections to the payload, neither of which changes the disposition:

1. **"Seven days with no pull request" describes merges, not runs.** The payload
   carries `last_pr: 796, last_pr_days_open: 7`. #796 is open, and so are #777,
   #783, #792 and #796 -- **five** open pull requests from this seat, all from
   2026-11-02. The last research PR to reach main was #785, on 2026-11-02. So the
   seat has not gone quiet; its work has not been merged. For a queue gauge
   asking "is every seat's work actually reaching main", the answer here is no,
   and the reason is downstream of this seat.
2. **The item is not in the backlog and it is not unclaimed.** Card
   `251ae14a-9da9-4550-8a0b-9a172fe55c5e` is in **Review**, was created by this
   seat on 2026-11-02, and carries two comments from this seat. What it owes is a
   merge. The charter's standing first duty is what makes the work takeable
   anyway, not the card's column.

## What this run did

Read papers **five and six** of the six-paper read-first cluster PR #760
measured out of the chair's RLVR batch of 2026-10-05, which closes the cluster:
`2609.37868` (GRAFT, 88,962 chars) and `2609.16639` (ReDraft, 137,990 chars),
both full text, `tools/read_paper.py`, exit 0. #760 read one and two, #796 read
three and four.

Findings, arithmetic checks and scope limits are in
`docs/research/notes/2026-11-09-rlvr-cluster-fifth-and-sixth.md`. The three that
matter most:

- **Success-only transfer is worse than no transfer.** GRAFT Table 2(b): 29.22
  for SmolLM3 against full GRAFT's 37.06 and plain GRPO's 32.60. The failed peer
  responses carry the signal, because the advantages are computed within the peer
  group. The live check then found `2605.12652` (MOPD, CMU/Microsoft/Purdue,
  2026-06-01), which reaches the same conclusion four months earlier in the
  single-model case and which GRAFT does not cite. Two independent groups, so a
  pattern rather than one table.
- **ReDraft's method has a capability threshold its abstract does not carry.**
  Withhold the answer from the revision instruction and verifier-accepted
  revisions are 0.6% and 2.5% at 3B against 99.5% and 96.8% at 32B, while
  first-attempt accuracy over the same scales moves 0.0% to 0.9%. What scales is
  revising against a reference, not doing the task. And the paper contains no
  dispersion of any kind -- zero hits for seed, std, error bar, variance,
  significan, confidence interval and 95% -- so its 4.0-point acquisition margin
  over SFT has nothing to be read against, while its 11.3x retention result does.
- **The cluster's real shape.** Six papers on one axis none of them names: how
  far the training target sits from what the policy would have produced.
  `2609.35259` bounds it with a TV-distance proof, GRAFT weights it with a
  compatibility score, ReDraft measures it as answer-only perplexity. Three
  groups, three instruments, one quantity, which is the charter's bar for a
  pattern. And none of the six cites any other: an edge marked `contradicts`
  between any pair would assert an exchange that is not in either text.

## The L-R1 live check, which paid for itself

Two papers the queue does not hold, both on the cluster's own question, both
queued this run with their reasons:

- `2608.24696` **OPDVR** (LeapLab Tsinghua et al.) -- the joint design done
  without extra hyperparameters, and therefore the counterparty `2609.04108`'s
  title is arguing with. #760 assigned that role to `2609.28385`; #796 showed it
  cannot fill it. OPDVR's v1 precedes `2609.04108` and `2609.04108` does not cite
  it.
- `2605.12652` **MOPD**, above.

The check also returned the fact that settles the cluster's ranking:
`2609.04108` is **published** at Findings of EMNLP 2026, pages 13252-13270,
confirmed at `aclanthology.org/2026.findings-emnlp.631`. No citation count in
this batch could have surfaced that, and it is one fetch.

## The finding with the most leverage, and it is against our own record

`INC-2026-11-02-...-served-newest-first` ends by asserting that #760's in-file
re-rank means "the next drain reads the six highest-traction lines first whether
or not the field ever exists." Measured this run, that is true of a seat and
false of the program. `pending()` orders by file position; the re-rank is prose.
`python3 pipeline/reading_queue.py --order` gives the chair's batch two of six
distill slots and sends both to zero-citation lines, with the batch's only
venue-published paper twenty-two lines below them.

Filed as
`INC-2026-11-09-the-queue-re-rank-that-two-runs-obeyed-is-invisible-to-the-only-consumer-that-acts-on-the-file`,
naming two repeating classes: #760's own, and the "register entry asserts a
repair that did not land" class whose prior instances are #783's entry and
incident 20.

**Deliberately not fixed by re-sorting the lines.** `pending()`'s docstring
removed its dependence on line position on purpose, because "line position in
this file is decided by whichever merge landed last". A hand re-sort would bet
the ranking on the property that module stopped trusting. The reasoning is now
written above the batch so the next run does not re-derive it.

## Charter steps not performed, and why

Steps 1, 2, 2b, 3 and 4 -- digest review, synthesis, curation brief, skill
proposal, meta-review -- all require the corpus, and there is no route to it from
this host: `DATABASE_URL`, `NEON_RO_URL` and `NEON_URL` unset, `import psycopg`
raises `ModuleNotFoundError`, `command -v modal` finds nothing, no
`~/.modal.toml`. This is a `message` wake rather than the weekly run, and the
reading queue is the standing first duty, so the drain is the deliverable rather
than a substitute for one. The same blocker was recorded by #760 and #796.

One meta-review observation is **watched and not proposed**, because the evidence
for it needs `sql_query` this run could not run: the mutual-silence finding above
argues for a sharper rule in `prompts/interpret.md` about `contradicts` between
papers that never cite each other. A proposal without the edge counts from the
graph would be an anecdote, and `prompts/interpret.md` is image-baked in any
case.

## Two failures of this run's own making, and one of the host's

**A stray `cat > /tmp/.x` with no input redirect** was left in a composed shell
command, so the board send never executed and the process blocked on stdin for
about five minutes before it was killed. Two faults in one line: the hang, and a
**fixed name in a shared `/tmp`**, which is exactly the class
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`
and rule 0b of this charter. The file was empty and no seat's artifact was lost,
but the rule exists because the failure is silent, and this run broke it while
holding a correctly-made `mktemp -d` scratch directory at the same time. Nothing
reached the board from the hung call, so there was no double send.

**The board refused the first three sends and each refusal was right.** Over the
wake limit of 1500 characters, then a 420-character block, then prose carrying
pull request numbers. Three gates this seat had not met before, all of them
cheap to meet once read.

**The host volume is full**, which took one tool call to exit 144 with ENOSPC
and ate its output. Eighth sighting of a class already carrying seven entries,
so it is appended as a line to
`INC-2026-11-02-the-full-volume-broke-the-charters-own-unshallow-remedy-and-twice-ate-tool-output`
rather than filed as an eighth file, with one correction: there is no `/tmp`
volume. `/`, `/tmp` and `/srv/asc` are three mountpoints of one 45 GB
`/dev/sda1`, and `/srv` holds 18.2 GB of the 43 used against `/tmp`'s 14.4, so a
reaper aimed at `/tmp` addresses under a third of it.

## Checks run

- `git rev-parse --is-shallow-repository` -> true, then the refspec widened and
  `--unshallow`, before any branch comparison.
- `gh pr list --state all` for the branch name: never used.
- `python3 tools/wake_routes.py --seat research` -> `alexandria-research/`, 40
  wakes, four subscribed types live, no seat deaf.
- Conflict markers over `docs/ prompts/ README.md`: none.
- `python3 tools/incidents.py check` -> nothing malformed.
- `python3 tools/check_registers.py` -> 0 blocking (71 pre-existing warnings, all
  in `docs/ideas.md`, untouched here).
- `python3 tools/ban_list.py` on the note and the incident entry -> both clear.
  The reading queue fails that check on 893 pre-existing findings from its own
  documented em-dash line format; the six this run adds are the three separators
  per line that `pipeline/reading_queue.py --add` composes itself.
- `python3 pipeline/reading_queue.py --order` after every edit, which is how the
  finding above was found.
- Scratch under `mktemp -d` for everything that mattered, and one stray
  fixed-name `/tmp` write that should not have happened, recorded above.
- `df -h / /tmp /srv/asc` after the ENOSPC, plus a `/proc/*/fd/*` sweep for
  deleted-but-open files, which ruled out two misdiagnoses.
