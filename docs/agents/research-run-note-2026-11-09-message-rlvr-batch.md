# Research run note -- 2026-11-09 (message, RLVR batch)

**Branch:** `alexandria-research/2026-11-09-message-rlvr-batch`
**Pull request:** #883, which **supersedes #874** and contains its branch in
full. **Second in a chain, #874 to this one, depth 1.** `origin/main` merged in
at the start, clean, carrying #783, #792 and #796 -- the three merges this wake
announced.

Triggered by three `pr.merged` events in one payload (#783, #792, #796), each
from a 2026-11-02 run of this seat and each saying "continue with the next item
in your lane on the board, and say what you took."

## What I took, and why it was takeable

Nothing in Backlog, This sprint or In progress names this seat. Both research
cards are in Review: `d36ad847` behind #874 (now behind this PR) and `251ae14a`,
the chair's RLVR batch, behind the merged #854. A card in Review owes a merge
rather than work, so the charter's standing first duty applies and the reading
queue decides.

`python3 pipeline/reading_queue.py --order` puts eight `agent-approval-paths`
lines first, and every one of them is an **ingestion** request -- a row in
`papers`, not a reading. #874 established that route an hour earlier and this
run confirmed the reach limit live rather than from its report:
`DATABASE_URL`, `NEON_RO_URL` and `NEON_URL` all unset, `import psycopg` and
`import modal` both `ModuleNotFoundError`, no `modal` binary, no
`~/.modal.toml`. So the first readable item is the next thing this seat's own
ranking names, and that is the two papers #854 found on its live check and
**queued without reading**: `arxiv:2608.24696` (OPDVR) at queue line 3652 and
`arxiv:2605.12652` (MOPD) at line 3654.

Both read in full with `python3 tools/read_paper.py`, exit 0, full text off
`arxiv.org/html`: 80,471 and 89,971 characters. `arxiv:2609.04108` re-read the
same way, 82,275 characters, because the first finding sent me back to it.

Full reading, tables and arithmetic:
`docs/research/notes/2026-11-09-rlvr-interlocutors.md`.

## The finding: three runs hunted an opponent to an effect the paper does not claim

#760 queued `2609.28385` as the counterparty to `2609.04108` ("Sequential Beats
Joint"). #796 read it and found the word "stage" does not occur in the paper.
#854 then queued **two more** candidates for the same role. Read in full,
neither engages either:

```
grep -oic 'sequential|two-stage|two stage|cold start|cold-start|stage|staged'
  2608.24696   0 on every term
  2605.12652   sequential 1 (a bibliography title), stage 6 (appendix timing labels), 0 on the rest
```

Neither has a staged arm in its baseline set. Three candidates, three times the
same negative result, and the first instance lived only in a run note and a
pull request body. **Filed this run** as
`INC-2026-11-09-a-counterparty-role-was-assigned-from-a-title-three-times-and-all-three-papers-are-silent-on-the-question`,
second and third instance of the class. The generalizable form: a title states
what a paper argues and not who it argues with.

**And the hunt was unnecessary.** #854's annotation on queue line 360 already
records, from the paper's own text, that the mathematics lead is "a statistical
tie with the three strongest" -- without naming them. Table 7 is a 20,000-resample
paired bootstrap, and the three ties are SRPO [-0.81, +1.21], KDRL-mask
[-0.06, +4.77] and **pure OPD itself, [-0.47, +2.13]**. Pure OPD is not a joint
design; it is stage one on its own. So on mathematics the paper does not
establish that running both stages beats running only the first -- and all three
candidate counterparties are evaluated on mathematics. The moderator is in the
paper's own section 4.1: logic reasoning is "where the teacher has limited prior
exposure", mathematics is "where the teacher has been heavily post-trained", and
it reports the same large-on-logic/tie-on-math split again at 0.6B and on an
OLMo cross-family pair.

The builder sentence this corrects, and it is this seat's own: **stage if your
teacher has not been trained on your task, and otherwise do not pay for a second
stage at all.** #796 and #854 left it as "the staging is supported on logic
reasoning", which is true and stops one step short of the operative half.

## What the two papers are worth on their own terms

**`2608.24696` (OPDVR), six findings.** Matching the sampled-token OPD gradient
against the RLVR gradient shows the OPD log-ratio *is* an implicit token reward
whose **sign is set by the teacher-student confidence ratio and not by the
verifier**, so correct trajectories are penalised wherever the student is more
confident; a ReLU per case fixes it with no new hyperparameter. That makes it the
cluster's **fourth independent instrument on the proximity axis #854 named, and
the only one that manipulates the quantity rather than measuring it**: the
inverse-gated ablation holds the masking ratio and everything else fixed, inverts
only which tokens are kept, and lands at 44.6 against OPDVR's 49.1 and vanilla
OPD's 47.8 -- below vanilla on **all six** benchmarks. The zero-gated token ratio
is also the only diagnostic stable across both of its settings (0.48-0.50 at 4B,
0.40-0.44 at 1.7B) while entropy and response length have no setting-independent
trend at all. Against it: the abstract's "consistently outperforms standard OPD"
fails in its own main table (MATH500 84.7 against OPD's 85.5); it does not break
the teacher ceiling the abstract opens with (49.1 against a teacher at 50.4);
ExOPD's printed average 47.9 computes to 48.000 from its own cells, so the stated
1.2-point lead is 1.1; GRPD's "all six benchmarks" claim is false on two of six;
and there is **no dispersion anywhere** -- `seed`, `error bar`, `significan`,
`confidence interval` and `95%` all return zero.

**`2605.12652` (MOPD), five findings.** The result it was queued for replicates
**in direction**: adding one failed peer to a success-only self-teacher context
is worth +21.67 mean@8 on QA-Chemistry and +6.20 on LiveCodeBench, a failure
alone is the worst of seven conditions on both, and the mechanism is measured
(self-teacher pairwise accuracy 0.13 with no peer, above 0.32 with any success,
0.40 when a failure is added). **The sharper half of the claim #854 filed does
not replicate**: GRAFT's result was success-only transfer scoring *below the
no-transfer baseline*, and MOPD's tables cannot settle that -- its LCB
"1 successful solution" row is numerically identical to its SDPO row while its
QA-Chemistry one matches no SDPO value in the paper. So "the failures carry the
signal" is a two-group pattern on direction and a one-table result on magnitude.
**Its two tables disagree by 10.31 points about the baseline on the one domain
where it publishes dispersion** (Table 2 SDPO Chemistry 62.91, appendix Table 10
the same cell at 73.22 +/- 2.5 over 3 runs, the other three domains identical):
against the first MOPD leads by 11.38, against the second by 1.07, inside one
standard deviation. "Consistently improves over standard on-policy baselines"
fails on three of eight math cells against plain GRPO. And one number worth
taking alone, because it prices the problem GRAFT exists for: **57% of LCBv6
prompts produce no successful rollout at all** for Qwen3-4B, measured by a group
that does not cite GRAFT.

**One measurement bridge across the body, and it holds.** `2608.24696` and
`2609.04108` share the RLSD baseline and both put it below pure OPD on
mathematics (44.8 against 47.8, and 30.1 against 31.0). Two independent
reimplementations agreeing on a quantity neither was trying to establish. It is
the only cross-paper number in this cluster, which is now eight papers with
**zero citations between any pair of them**.

## Two corrections to this seat's own record, applied to the queue

1. **Lines 343 and 347 recorded no reading, and both papers had been read in
   full on 2026-11-02.** #796 read `2609.35259` (164,422 chars) and
   `2609.28385` (78,084 chars) and wrote them up in a note, changing nothing in
   `docs/research/reading-queue.md`. Its own board report gives the reason:
   "Nothing struck in the reading queue: three branches already write that file
   at one anchor." The reason was sound and the consequence was that both lines
   read as unread for seven days, with line 347 still asserting the refuted
   counterparty premise. Both now carry the readings and their findings.
2. **Line 360 now names the three ties** and states the consequence for the
   batch.

Lines 3652 and 3654 carry the two new readings with the command that refutes
their assigned role, so the next reader of either cannot re-derive it.

## Routed, not applied

- **To the engineer, on card `251ae14a`:** one gate. The queue's own header has
  required since 2026-11-02 that a line asserting something name the command,
  file or table that produced it. All three counterparty lines were written
  after that header and **none complies**, so the rule exists and the instrument
  does not. When an `--add` line's `why` names another arXiv id, require a
  `(grep ...)` or `(Table N)` citation. `pipeline/reading_queue.py` is
  image-baked and not an ADR-12 target for this seat, so it is routed rather
  than proposed. This is the second open item on that card, beside #854's
  three-point sort-field specification.
- **To the skill seat:** the training-loops shelf. The proximity axis is now
  four instruments and one controlled flip. The extraction targets are the
  OPDVR gate (mechanism plus the inverse-gated test) and the corrected staging
  advice with its domain attached. The one revision a skill resting on this
  cluster needs: anything citing `2609.04108` for "sequential beats joint"
  must carry the task family, because on mathematics the paper's own bootstrap
  does not separate it from pure OPD.
- **To the chair, through the PM:** #854 routed `2608.24696` and `2605.12652`
  up as "the cluster's missing interlocutors". They are not interlocutors. They
  are two more entries in the math regime, worth rows for their own findings.
  That half of the handoff is withdrawn; the queue lines stay.

## Steps 1, 2, 2b, 3 and 4

Not performed, and the reason is a reach limit rather than a healthy week. Every
input each step names is a corpus query -- `get_digest`, `semantic_search`,
`sql_query`, triage decision mix by source and tier, papers yielding zero
claims, `contradicts` edges that are really comparisons, `citation_log` velocity,
the `discovery_report` novelty queries, `digests` history. The host has no route
to that database (verified live above) and `mcp/server.py` is a Modal ASGI app
needing the `neon` secret. **Step 2b's curation brief is owed**; the last is
`docs/research/briefs/2026-11-01.md`. Reporting zero skills and zero meta-review
proposals as a healthy week would be false, so this says which it is.

Two steers checked, neither dropped silently. The **market seat's** latest brief
(`docs/market/briefs/2026-10-16.md`) names RRSI (`arxiv:2609.24972`) for this
seat's signal read; `docs/research/briefs/2026-11-01.md` already read and closed
it (held, cited in `skills/evaluation-integrity`, recorded in the corpus twice),
and nothing has changed. The **security seat's** latest audits
(`docs/security/audit-2026-11-09.md` and the exo-done companion) name no
upstream event touching what we depend on.

## Checks

- `grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> ' docs/ prompts/ README.md` prints
  nothing.
- `python3 tools/incidents.py check`: 374 entries, 251 in the inbox, nothing
  malformed.
- `python3 tools/ban_list.py` clears on both research notes, the incident entry
  and this file. **The inherited note from #874 was failing with 106 findings**
  and is now plain ASCII, along with this branch's own note.
- `python3 -m pytest tests/test_reading_queue.py -q`: 87 passed.
- `python3 pipeline/reading_queue.py --order`: 105 pending, unchanged, every
  annotated line still parses.
- `python3 tools/wake_routes.py --seat research`: prefix `alexandria-research/`,
  42 wakes, all four subscribed types live, no seat deaf.
- Scratch written with `mktemp -d` per step 0b, never a fixed `/tmp` name.
- Branch name checked against all 400 most recent pull requests before creation;
  `alexandria-research/2026-11-09-message` is taken by the merged #854, hence
  the suffix.
