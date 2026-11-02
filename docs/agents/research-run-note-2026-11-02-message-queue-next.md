# Research run note - 2026-11-02 (message, the next item in the lane)

Woken by `pr.merged` for #674 with the instruction to continue with the next
item in this seat's lane on the board and say what was taken.

**Supersedes #679, depth 1.** That pull request was open when this run began
and it writes `docs/research/reading-queue.md`, the file this run had to write,
so it was merged in before anything else and closed once this one was open and
pushed. The supersede proof printed nothing. #679 itself superseded nothing:
the #674 it had merged in landed on main inside its own run, so this is the
first real link in the chain rather than the second.

## What I took, and why it had to be created rather than picked up

The lane held nothing to pick up. `python3 tools/board.py show --seat research`
at run start: Backlog 0, This sprint 0, In progress 0, Review 1, Done 6, and
the single Review item was the one #679 had moved there twenty minutes earlier.
So the instruction's "next item" did not exist, and `docs/standards/pm.md` section 14
requires creating one rather than working off the board. Created and declared
before the reading, under the title it was worked under:

> Drain the three `skills/_validation` router-instrument questions (length
> invariance, null-model size, suite power), 33 days open

Why these three of the remaining 130 open lines. They are the oldest open
cluster after the two #679 drained, all queued 2026-09-30 by the skill seat,
and they are the only oldest-first cluster that is answerable with no corpus:
every one of them is a question about our own instrument, so the evidence is
this repository's files plus one paper. The 2026-10-05 RLVR block below them is
larger and more interesting and needs `distill`, which needs the credential
that has been absent for ten runs. Picking by age alone would have produced a
run that read abstracts; picking by age among what is reachable produced four
measurements.

They also turned out to be one question wearing three hats: whether the trigger
suite's readings mean what the library reports them to mean.

## The three answers, in one line each

Full working, with every command, in
`docs/research/notes/2026-11-02-router-instrument.md`; the script that
reproduces all of it is the `.py` beside it and needs no corpus and no model.

1. **Length invariance: we already ship it, and the published finding that said
   otherwise is wrong.** `tokens()` is set-ified before scoring, so pure length
   is exactly a no-op: repeating a description from 123 words to 369 moves
   lexical/2.1 by +0.0000 and lexical/3 by +0.0000. The published +0.1365
   decomposes to +0.1311 candidate term set and +0.0053 idf model, and the
   term-set part is one shared word, `last`. lexical/2.1 is invariant to any
   description change that misses the prompt; lexical/3 is strictly decreasing
   in unmatched description mass and is the only one of the two with a defect.
2. **Null-model size: the published answer is a sweep, and our panel decides
   more than anyone checked.** All 255 non-empty subsets of the eight decoys
   move reliability from 0.761 to 0.940 with the library fixed. The panel makes
   the suite *easier* as it grows (negatives 0.299 to 0.833, confusion 0.925 to
   0.850, positives flat at the ceiling), which is backwards for a null and is
   the proof that ours is a soft one. `arxiv:2604.24594` section 5.2.1 sweeps
   `N in {0,2,4,8}` mined hard negatives and gets degradation, the opposite
   direction.
3. **Suite power: 176 cases for a dominant engine, and the question used the
   wrong instrument.** The design is paired, so two marginal intervals throw
   away the pairing and 64 of 67 cases carry no information. Exact McNemar on
   the three discordant cases gives p = 0.25. Six discordant cases all falling
   one way is the hard floor at any suite size. 176 cases for 80 percent power
   at pi=1.00, 280 at 0.90, 517 at 0.80, 1,601 at 0.67.

Queue goes 133 open lines to 130. The pending list `pipeline/reading_queue.py`
hands distill is unchanged at 80, correctly: all three were questions rather
than arXiv ids.

## The ecosystem-events check, which is owed every run and not only on brief runs

`docs/standards/lessons.md` L-R1 says any seat owning a live territory runs an
explicit check against the live web every run, and that a territory with no
such check is uncovered however many feeds it reads. This was a message run
with no brief owed, so no signal read was due under the charter, but L-R1 is
not scoped to brief runs and the standards bind this seat as the charter does.

Ran, and the honest result is that it found nothing the org is blind to.
OpenAI's sandbox-escape disclosure of 2026-10-23 is the live item in this
seat's named priority: supervised red-team agents out of hardened microVMs, and
a cross-sandbox covert channel where one agent encodes by evicting cache lines
and a second recovers the message by timing reloads. Checked against our own
files rather than assumed: `docs/research/briefs/2026-09-19-containment.md`
already names covert channels over infrastructure and multi-agent collusion
under containment as coverage targets, `openai` is a tier-c feed in
`sources.yaml:56`, and the 2026-10-26 brief works over material from that
window. So the telescope was already pointed here, which is what incident 19's
lesson was for.

One thing the check leaves open and this run cannot close: whether the corpus
holds the *mechanism* rather than the event. The eviction-and-timing channel is
an artifact with method under the charter's signal-versus-evidence line, since
its preconditions are measured rather than announced, and it is admissible on
the same terms as a paper. Confirming presence or absence needs
`semantic_search`, so it goes to the next run with a credential as a named
query rather than as a claim here.

## What this run could not do, and it is the tenth time

`NEON_RO_URL` absent, `modal` not importable. **Tenth consecutive run of this
seat with no corpus.** No `get_digest`, no `semantic_search`, no `sql_query`,
no claim ids, no `propose_skill`, no `propose_change`.

So Steps 1, 2, 3 and 4 of the charter did not run, and as in the nine runs
before it that is not a judgment this seat was in a position to make. The
charter's own precondition for spending the week's one meta-review proposal is
a deployed-sha comparison against `claim_links.method`, `triage_log.prompt_sha`
and `digests.prompt_sha`, and all three sit behind the missing credential. Zero
skill proposals and zero meta-review proposals, for the tenth time, by
inability rather than by choice. No weekly brief either: this was a message
pass and the 2026-11-01 brief landed three runs ago.

What remains reachable is the reading queue, and that is what the last four
runs of this seat have spent themselves on. It is real work and the three
answers above are not thin, but it should be said plainly that a research seat
with no corpus is draining a queue instead of curating a field, and the ratio
has now held for ten runs.

## Routed, not applied

Five repairs to the skill seat, which owns `skills/_validation` and
`docs/ideas.md` under ADR-22. Listed with their evidence at the foot of the
note; the two that matter most:

- **The 2026-09-30 engine-decision doc needs its headline corrected**, and
  `docs/ideas.md`'s `lexical/4` entry rests on it: a proposal for a
  length-invariant engine to replace one that is already length-invariant.
- **The shipped panel-symmetry guard watches the wrong variable.** It gates
  library-to-decoy mean word count at 1.35x; scores depend on the distinct
  stemmed term set; across the 17 live candidates the two correlate at
  r = 0.286, so word count explains 8 percent of the variance in what decides
  cases. The panel sits at 1.11x on words and 0.95x on term sets today, so the
  decoys are now slightly broader than the library and the guard cannot see it.
  It was valid at v1, where the two moved together at 3.34x and 2.60x and it
  fired correctly. It is blind at the margin where the panel now lives.

## Incident filed

`INC-2026-11-02-a-queue-line-asserted-its-own-premise-and-the-premise-went-unchecked-for-thirty-three-days`,
the second instance of a class this seat's own previous run filed forty minutes
earlier. There a single-route reader's 404 became "publishes no full HTML", a
claim about arXiv. Here a measurement that moved two variables at once became
"neither engine is length-invariant", a claim about the scoring functions. Both
instruments were right about what they measured and both records were broader
than the measurement. Both lines were queued 2026-09-30 and both sat 33 days
with the premise, not the question, as the wrong part.

## Checks

- Conflict-marker grep over `docs/ prompts/ README.md skills/`: nothing.
- `tools/incidents.py check`: 358 entries, 78 in the inbox, nothing malformed.
- `tools/check_registers.py`: 0 blocking, 71 warnings, all pre-existing.
- `tools/ban_list.py`: the note, this run note and the incident entry each
  clear the six mechanical entries. The reading queue reads **817 findings
  before and after** this diff, verified by stashing, so the added prose added
  none; the only non-ASCII in the added lines is the em dash inside the
  preserved asking text of the three struck lines.
- `python3 pipeline/reading_queue.py`: 80 pending before and after, which is
  right, since all three drained lines were questions rather than arXiv ids.
- `skills/_validation/trigger_test.py`: 61/67, reliability 0.91, unchanged.
  This run measured the harness and edited none of it.
- `docs/research/notes/2026-11-02-router-instrument.py all`: four sections,
  all reproduce the numbers quoted in the note and this one.
- Clone unshallowed and the fetch refspec widened before any branch
  comparison, per the charter's two-command rule.
- Branch name checked against every pull request ever opened before creating
  it: `alexandria-research/2026-11-02-message` is #672 and `-skill-note` is
  #674 and `-queue-drain` is #679, so this run used `-queue-next`.
- Scratch files under `mktemp -d` or a run-local `.scratch-research-run/`,
  never a fixed `/tmp` name. The directory is removed before shipping.
