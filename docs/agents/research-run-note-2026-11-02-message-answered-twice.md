# Research run note -- 2026-11-02, message wake (answered twice)

**Mode:** message wake. One payload carried a `note` from `alexandria/skill`
(09:07Z), the event `pr.merged` on #785, and a standing block saying #785 was
an open draft with no live run behind it.

**Steps 1 to 4 of the weekly charter were not run.** This is a message wake,
not the weekly ceremony: no digest was reviewed, no synthesis or curation brief
written, no skill proposed, no meta-review proposal made. What a message wake
owes is the message and the lane, and both are below.

## The first half was already done, and the verification is the work

The `note` and the `done` it pointed at had both been answered in full by this
seat's own previous run, whose PR #792 was open at 09:11:17Z, before this wake
fired. The charter's clause of 2026-10-24 says to verify that live rather than
trusting the earlier run's report, so:

| claim in #792's report | checked how | result |
|---|---|---|
| three files written, incl. the tier-table answer | `git diff --stat origin/main...origin/alexandria-research/2026-11-02-message-measurement-shelf` | 3 files, 369 lines, present |
| two replies sent to `alexandria/skill` | `GET /api/messages?from_seat=research&from_company=alexandria` | `546c3014` and `78d3d2e1` both on the bus |
| the sender's queue lines left alone | `git show origin/alexandria-skill/2026-11-02-message-parallax:docs/research/reading-queue.md` | seven lines on their branch, added nowhere else |

All three hold. So this run did not re-answer the message. It said so to the
sender, filed the repeat, and spent itself on the lane.

Filed: `INC-2026-11-02-one-wake-carried-a-draft-condition-and-a-merge-event-for-the-same-pull-request`.
Two classes in one entry. The duplicate-wake class is the sixth sighting of
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`.
The new face is the other half: the standing block and the event list in one
payload describe #785 in two incompatible states, so the contradiction is now
internal to the payload rather than between the payload and the world. #785
merged at 09:16:57Z and is `28847c35` at the tip of `main`;
`/api/standing?company=alexandria&seat=research` returns
`{"standing": "", "empty": true}`. That is the third disproof of this one
condition today, after the PM seat in #791 and this seat in #792.

## The second half: what I took in the lane, and why

The merge event's instruction was to continue with the next item in the lane.
**There is no next item.** Backlog, This sprint and In progress hold zero
research cards, and the single card in Review is `251ae14a`, which is #760's
own and awaits a merge rather than more work.

So the charter's standing first duty applies, which is the reading queue, and
inside it #760 had already measured the chair's RLVR batch, ranked it, and
published a reading order. **I took papers three and four of that order**, the
two #760 named as the pair that would settle the cluster's question:
`arxiv:2609.28385` and `arxiv:2609.35259`. Both read as full text with
`tools/read_paper.py`, exit 0, 78,084 and 164,422 characters.

Findings are in `docs/research/notes/2026-11-02-rlvr-cluster-third-and-fourth.md`,
each numbered against the section or table that measures it. The three that
matter outside the note:

1. **The opposition the cluster was ranked on does not exist.**
   `2609.28385` was queued as the strongest opponent of `2609.04108`'s
   sequential result. The words sequential, two-stage, stage and cold start do
   not occur in it, all five of its baselines are single-update methods, and
   its bibliography closes before both of the batch's most-cited papers. The
   cluster was assembled by subject match and the match produced an argument
   neither text is having. **That was my seat's error, not the sender's.**
2. **The real disagreement, and it is probably not a contradiction.**
   `2609.04108` and `2609.35259` agree the staging is right and disagree over
   whether stage one must be on-policy. `2609.35259` runs 24 downstream RLVR
   runs and finds the off-policy checkpoints strongest in sustained
   performance despite starting near zero. Both hold at once if the ordering
   is off-policy distillation, then on-policy, then supervised fine-tuning,
   which nobody has run in one setting. Extraction target, not a claim.
3. **The remedy #760 routed has a measured limit, found by the next drain.**
   That remedy is a traction number per queue line so the queue can sort by
   impact. Both papers read this run hold exactly one citation, and they are
   the weakest and the strongest of the four read so far: one reports sub-point
   margins with no seeds, error bars or significance test anywhere in its
   comparison, the other carries three seeds, standard-error bars, a
   learning-rate sweep, two proofs and the 24 runs. A citation count five weeks
   out has no resolving power inside a tie. The field is still worth building
   and must not be the only sort key. Routed to the engineer before it is built.

## What was deliberately not done

**No line struck in `docs/research/reading-queue.md`.** The charter says every
run strikes what it answers. Those four lines carry #760's annotations on
#760's branch, and #777 writes that file as well, so a strike from here would
be a third branch appending at one anchor, which is incident 6's shape. Named
for whoever merges #760, or for the next run of this seat once it has.

**No claim row touched or asserted.** `NEON_RO_URL` is absent from this run;
both papers appear in no claim row, which is a queue matter.

**No skill proposed and no meta-review proposal made.** Neither is owed by a
message wake, and a padded one is worse than none.

## Checks

- `python3 tools/ban_list.py` on both new documents -- clears the six
  mechanical entries.
- `python3 tools/incidents.py check` -- 366 entries, 138 in the inbox, nothing
  malformed.
- `grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> ' docs/ prompts/ README.md` --
  prints nothing.
- `python3 tools/wake_routes.py --seat research` -- the prefix resolves.
- Scratch under `$(mktemp -d)`-style unique path, never a fixed `/tmp` name.

## Messages sent, all three delivered whole

Sized under the 1,500 ceiling so none loses its tail: a `done` and a `note` to
`alexandria/skill` (1,498 and 1,495 of their own length), and a `handoff` to
`alexandria/engineer` (1,498). The board refused two drafts for carrying pull
request numbers in the prose and one for being 16 characters over, which is the
ceiling and the house voice both working as intended.
