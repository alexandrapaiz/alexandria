# Research run note — 2026-11-09 (message), the agent-approval-paths queue batch

**Trigger:** `message` — `pr.merged` on #854 (the RLVR cluster batch), which
said "continue with the next item in your lane on the board, and say what you
took."
**Branch:** `alexandria-research/2026-11-09-message-approval-paths` (the
charter's prefix; `-approval-paths` suffixed because
`alexandria-research/2026-11-09-message` already exists from #854).
**PR:** #874. **Predecessor:** #854, merged. Depth 1.

## What I took, and why it was the next item

Nothing on this sprint names this seat. The one research card,
`251ae14a-9da9-4550-8a0b-9a172fe55c5e`, is in **Review** on #854 — it owes a
merge, not work. So the next item is the head of the reading queue, which the
queue's own instrument decides rather than this seat:

```
$ python3 pipeline/reading_queue.py --order
arxiv:2609.18411   skills/agent-approval-paths   line 3482   blocked   NEXT
arxiv:2606.02668   skills/agent-approval-paths   line 3483   blocked   NEXT
arxiv:2610.22987   skills/agent-approval-paths   line 3484   blocked   NEXT
```

That is the 2026-11-02 `skills/agent-approval-paths` batch: three ingestion
requests plus four questions the skill seat's reading raised and could not
settle. **I took the four questions**, because the three ingestion lines ask
for database rows and this sandbox has neither `modal` nor `DATABASE_URL`.

Twelve papers read in full, `tools/read_paper.py`, all exit 0: `2609.18411`,
`2606.02668`, `2610.22987`, `2607.01415`, `2609.40082`, `2610.02456`,
`2610.39711`, `2609.22978`, `2604.28138`, `2610.14488`, `2610.40753`,
`2611.08516`. Findings, tables and arithmetic in
`docs/research/notes/2026-11-09-approval-paths-questions.md`.

## The four questions

**Two are answered and struck. Two stay open with their reasons corrected.**

- **Q2, a ground-truth action decoder for a shell or API surface: answered.**
  `2610.14488` (ZTAC, 10 Oct 2026) resolves each request to a concrete object
  — path + device + inode, binary + argv + cwd, git HEAD/branch/refs/index,
  parsed URL — decides on the object, re-checks at use, and renders the
  approval from the resolved operation ("`read .env` for a request that named
  `config.txt`"). 2 of 74 oracle-scored attacks lost against 66 for a tool
  allowlist and 56 for allowlist-plus-command-sandbox; 10 disclosed-incident
  replays all held; 43 of 46 benign operations at 8 prompts; 4.0 ms median.
  **It does not clear the "without growing a trust list" half**, and says so:
  "Handoff rules are an enumeration … the list has to be maintained like the
  list of credential files."
- **Q3, a mediator that is not boundary-only escaping the frontier: answered,
  yes, twice.** `2610.40753` (Caper) pre-executes each command in a snapshotted
  sandbox and approves from observed effects: 6.7% / 7.8% harmful at a **1.0%
  false-block rate** against 14.8% / 62.7% / 3.9% for Claude Code Auto Mode,
  over 682 + 204 tasks. ZTAC is the second, by a different construction. **The
  Wilson intervals split the result and the split is the finding**: on harm
  they do not overlap ([4.0, 14.7] against [53.1, 71.5]), on false block
  Caper's [0.2, 5.3] overlaps the rule-based CARE's [0.5, 6.9]. So the claim is
  "an order of magnitude on harm at a false-block rate no worse than the best
  static checker's", not "the frontier is broken."
- **Q1, the microVM point on the Rollout-Tax curve: still open, and one of the
  line's three premises is wrong.** `2610.02456` does not put the two
  boundaries on one task set — its IR-4 requires hardware virtualization, the
  container candidates in its own Table I are excluded for failing it, and all
  five sandboxes reaching the capability tests are microVMs. What is new is
  `2610.39711` §5.3: a microVM snapshot restore at 0.08 s against 1.45–2.46 s
  for three container-pod systems, **the opposite sign from the curve's
  framing** — at the minimal tier, on a different template, at 77.4% burst
  delivery against 100%, n=1. The repository tier still has no microVM arm.
- **Q4, the organic false-positive rate: still open, denominator corrected
  4x.** `2610.22987`'s benign control is 0 of **100** (four configurations x 25
  distinct cases), not 0 of 25, which moves the one-sided 95% bound from 11.3%
  to 3.0% pooled. The population is still synthesized, so the question stands —
  but `2611.08516` Experiment 1B released 52 real coding-agent sessions,
  28,087 tool calls, anonymized, which turns "wait for telemetry" into "run a
  script."

## Three things this run found that were not asked for

1. **The ingestion blocker cleared, and three lines have been recording it
   wrong since.** Every previous run routed `2609.18411`, `2606.02668` and
   `2610.22987` — and `2609.08371` at line 220 — to board card `6a5e4ad5`, the
   switched-off Modal workspace, on the ground that "no agent seat can touch
   it." The engineer's third comment on that card, **2026-11-08 23:37Z**, says
   compute is back and the account state has cleared. The card is still in This
   sprint because its residual question (whether a monthly spend cap is still
   set) is the owner's. **This seat still cannot run the ingest** — no `modal`
   binary, `import modal` raises `ModuleNotFoundError` against a
   `requirements.txt:1` pin of `modal>=1.5`, no `~/.modal.toml`, no
   `DATABASE_URL` — **but it no longer needs a seat to.** `--order` puts the
   three at positions 1-3, `reading_queue.resolve()` inserts unseen ids at 6
   per distill run, and the crons are routing. Route changed on all three
   lines from the card to the next distill run, with
   `modal run pipeline/ingest.py --ids 2609.18411 2606.02668 2610.22987` as the
   explicit path.
2. **A real ingestion line was masked in `pending()` by a question line above
   it.** `ARXIV.search()` takes the first `arxiv:<id>` in a line, so the
   2026-11-02 microVM question — which names `arxiv:2607.01415` in its prose —
   parsed as an ingestion request for that paper, attributed to
   `skills/agent-containment`, at pending position 92. The deliberate line for
   the same id, written by this seat the same day, sits at line 3499 and was
   invisible. Rewriting the ids in that prose to bare backticked form unmasked
   it. **One pre-existing instance, so an anecdote, not a pattern** — and
   `pipeline/reading_queue.py` is not an ADR-12 target and is image-baked
   besides. Routed to the engineer, not proposed. The thing worth noticing is
   that the gate caught my attempt to add a duplicate line and printed both
   existing lines, which is the gate working exactly as the file's header
   promises.
3. **This seat's own line carried the same wrong premise as the skill seat's.**
   Line 3498, written here on 2026-11-02, says `2610.02456` "compares a microVM
   sandbox and a container sandbox on usability only." It compares microVM to
   microVM. Corrected on the line.

## What I did not do, and why

- **No skill proposed** (charter Step 3). Zero is the charter's stated normal
  outcome, and the honest reason here is specific: the cluster this run
  assembled is strong enough to package — three independent lines converging on
  render-from-resolved-object, plus the only CI-bearing comparison table in the
  literature — but **none of it is in the corpus.** `propose_skill` wants
  supporting claim ids and there are none, because the papers have no rows and
  rows need a distill run. The proposal this run would have made is listed as
  an extraction target in the findings note instead, which is where ADR-22 puts
  it anyway.
- **No meta-review proposal** (Step 4). The evidence for one is all SQL —
  triage decision mix by source, papers that yielded zero claims, `contradicts`
  edges that are really comparisons — and `DATABASE_URL` is unset in this
  sandbox, so I could not gather it. The one defect I did find in code is
  finding 2 above, which is an anecdote and out of ADR-12 scope. **Zero
  proposals, and the reason is a reach limit rather than a healthy week**,
  which is a different thing and should not be reported as the first.
- **No curation brief** (Step 2b). The last one is `2026-11-01.md`, so one is
  owed. Every input it specifies — citation velocity from `citation_log`,
  rising authors and institutions, embedding-space novelty via the
  `discovery_report` queries, `digests` history — is a corpus query. With no
  `DATABASE_URL` and no MCP server reachable from here, a brief written this
  run would be a brief with its evidence section guessed, which is worse than a
  late brief. **Recorded as owed, and the blocker is the same one as above:
  this seat's runs reach papers and the repository but not the database.** That
  is worth somebody's attention as a standing condition, not as this run's
  excuse.

## Queue state

105 pending, 6 per distill run. Two lines struck, five annotated, six papers
queued: `2610.40753` Caper, `2610.14488` ZTAC, `2609.38983` and `2609.28586`
(approval laundering, named independently by two groups three weeks apart),
`2610.39711` Sandman, `2611.08516` Aegis OS. Four more found and deliberately
**not** queued, with the reason on the record in the findings note:
`2609.22978` DSec, `2604.13536` YoloFS, `2604.28138` Crab, `2607.05743`
Rashidi. The six that were queued jump the chair's RLVR batch by four
positions, about one distill run, because `--order` puts blocked skills first.
Declaring that rather than hiding it.
