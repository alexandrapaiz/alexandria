// Generates DUMMY FIXTURE rows for the Left-Behind Index so the list is judged
// at the volume the design targets (fifty findings) rather than at the twenty
// two the database holds today. Writes the JSON wherever it is told; the run
// points LEFT_BEHIND_FIXTURE at it and `site/lib/left-behind-live.js` reads it
// through the production path.
//
// The shape is deliberately lumpy, because ban list entry 28 says a layout
// judged at evenly sized demo data is not judged, and entry 30 says the field
// a row exists to identify is the one that gets compressed. So:
//
//   - claim text runs from 40 to 420 characters, which is the real range: the
//     distiller writes a sentence or it writes a paragraph
//   - most findings carry one contradiction and a few carry three or four,
//     because ADR-10 makes the graph append-only and a second opinion is a
//     second row
//   - ids span one to four digits, so the monospace column is tested at its
//     widest and its narrowest
//   - some rows have no confidence and some have a paper with no url, both of
//     which the database permits
//   - paper titles include the long ones, because a title is the string most
//     likely to break a definition list's second column
import fs from "node:fs";

const OUT = process.argv[2];
if (!OUT) throw new Error("usage: make-left-behind-fixture.mjs <out.json>");

function rng(seed) {
  let s = seed;
  return () => ((s = (s * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
}
const rand = rng(20261015);
const pick = (a) => a[Math.floor(rand() * a.length)];
const between = (lo, hi) => lo + Math.floor(rand() * (hi - lo + 1));

const SUBJECTS = [
  "token-level supervision", "imitation fine-tuning", "speculative decoding",
  "retrieval reranking", "self-generated skills", "chain-of-thought distillation",
  "KV cache eviction", "reward model ensembling", "tool-call repair",
  "context compaction", "process supervision", "majority-vote self-consistency",
  "curriculum ordering", "preference-pair mining", "long-horizon planning",
  "subagent delegation", "embedding staleness", "judge calibration",
];

const SHORT = [
  "DUMMY FIXTURE. %S leaves downstream behaviour unchanged.",
  "DUMMY FIXTURE. %S does not transfer past the 7B scale.",
  "DUMMY FIXTURE. %S overfits to the corruption pattern it was trained on.",
];

const MEDIUM = [
  "DUMMY FIXTURE. Under a fixed compute budget, %S recovers most of the reported gain, " +
    "but the effect disappears once the baseline is tuned on the same data.",
  "DUMMY FIXTURE. %S improves the headline metric while regressing the held-out split, " +
    "which the original report does not measure.",
];

const LONG = [
  "DUMMY FIXTURE. Across three model families and two task suites, %S produces a gain that " +
    "is indistinguishable from the variance between seeds, and the paper's own ablation " +
    "removes the component it credits without changing the result. The authors note this in " +
    "an appendix and the abstract does not, which is the shape of claim this index exists to " +
    "carry rather than to settle.",
  "DUMMY FIXTURE. %S is reported as a general improvement, but every experiment holds the " +
    "retrieval corpus fixed, so the measured effect is a property of that corpus rather than " +
    "of the method, and nothing in the setup separates the two. A replication at a different " +
    "corpus size would answer it and none has been run.",
];

const PAPERS = [
  ["Scaling laws for supervised fine-tuning under distribution shift", "https://arxiv.org/abs/2610.01234"],
  ["A critical look at process supervision", "https://arxiv.org/abs/2610.02345"],
  ["On the limits of self-generated curricula for agentic tasks, with an extended analysis of seed variance across three model families", "https://arxiv.org/abs/2610.03456"],
  ["Retrieval reranking revisited", "https://arxiv.org/abs/2610.04567"],
  ["Cache eviction policies for long-context serving", null],
  ["Judge calibration and the illusion of agreement", "https://arxiv.org/abs/2610.06789"],
];

const rows = [];
let id = 89;

for (let i = 0; i < 50; i++) {
  id += between(3, 180);
  const subject = pick(SUBJECTS);
  const bucket = rand() < 0.45 ? SHORT : rand() < 0.75 ? MEDIUM : LONG;
  const claim = pick(bucket).replace("%S", subject);
  const [paperTitle, paperUrl] = pick(PAPERS);
  const created = `2026-${String(between(8, 10)).padStart(2, "0")}-${String(between(1, 28)).padStart(2, "0")}`;

  // Most findings carry one edge. A few carry several, which is the state the
  // panel's hairline separator exists for.
  const edges = rand() < 0.78 ? 1 : between(2, 4);
  for (let e = 0; e < edges; e++) {
    const [np, nu] = pick(PAPERS);
    rows.push({
      id,
      claim,
      topics: [],
      evidence_grade: pick(["A", "B", "C", null]),
      created_at: created,
      paper_title: paperTitle,
      paper_url: paperUrl,
      new_id: id + between(20, 900),
      new_claim: pick(rand() < 0.5 ? SHORT : MEDIUM).replace("%S", pick(SUBJECTS)),
      new_paper_title: np,
      new_paper_url: nu,
      // The judge writes thirty distinct values in the real graph and the
      // column is nullable, so both are represented.
      confidence: rand() < 0.1 ? null : Math.round((0.7 + rand() * 0.25) * 100) / 100,
      flagged_at: `2026-10-${String(between(1, 15)).padStart(2, "0")}`,
    });
  }
}

fs.writeFileSync(OUT, JSON.stringify(rows, null, 1));
console.log(`wrote ${rows.length} DUMMY FIXTURE edges over 50 findings into ${OUT}`);
