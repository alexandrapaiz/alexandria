// Generates DUMMY FIXTURE skills under skills/fixture-* so list surfaces are
// judged at the volume the design targets (fifty), not the inventory of the
// day. The pattern is gitignored. Shapes are deliberately lumpy: ban list
// entry 28 says a layout judged at evenly sized demo data is not judged.
import fs from "node:fs";
import path from "node:path";

const ROOT = process.argv[2];
if (!ROOT) throw new Error("usage: make-fixtures.mjs <repo-root>");
const SKILLS = path.join(ROOT, "skills");

// Spread across every shelf, including the catch-all, with a long tail.
const SHELF_WORDS = [
  ["harness", "Agent harnesses"],
  ["context", "Context engineering"],
  ["multi-agent", "Multi-agent systems"],
  ["post-training", "Training loops"],
  ["serving", "Serving and inference"],
  ["multi-modal", "Multi-modal systems"],
  [null, "catch-all"],
];

// Names of real varying length, because a row's identifier is what it sorts
// on and a uniform-length name hides every wrap bug.
const STEMS = [
  "retrieval-budgeting", "tool-schema-design", "rollout-replay", "kv-cache-shaping",
  "judge-calibration", "handoff-contracts", "span-level-attribution",
  "speculative-decoding-economics", "reward-hacking-detection", "window-compaction",
  "episodic-memory-indexing", "delegation-audit", "trace-sampling",
  "preference-data-hygiene", "batch-scheduling-under-latency-objectives",
  "vision-grounding-checks", "audio-turn-segmentation", "subagent-budgets",
  "prompt-regression-suites", "frontier-eval-drift", "cost-aware-routing",
  "long-horizon-planning", "checkpoint-selection", "distillation-targets",
  "tokenizer-edge-cases", "streaming-partial-tool-calls", "retry-semantics",
  "observability-for-loops", "guardrail-placement", "context-poisoning",
  "self-consistency-economics", "curriculum-ordering", "tool-result-truncation",
  "agent-state-snapshots", "multi-turn-reward-shaping", "embedding-staleness",
  "fallback-model-selection", "schema-coercion-failures", "latency-budget-accounting",
  "cross-encoder-reranking", "synthetic-task-generation", "harness-escape-hatches",
  "evaluation-set-leakage", "memory-write-policies", "parallel-tool-fanout",
];

function rng(seed) {
  let s = seed;
  return () => ((s = (s * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
}
const rand = rng(20261007);
const pick = (a) => a[Math.floor(rand() * a.length)];

let made = 0;
for (let i = 0; i < STEMS.length; i++) {
  const stem = STEMS[i];
  const [word] = SHELF_WORDS[i % SHELF_WORDS.length];
  const dir = path.join(SKILLS, `fixture-${String(i + 1).padStart(2, "0")}-${stem}`);
  fs.mkdirSync(dir, { recursive: true });

  // Lumpy: most skills carry a couple of papers, a few carry many, and a
  // long tail carries one. Same for claims.
  const heavy = i % 11 === 0;
  const tail = i % 3 === 2;
  const papers = heavy ? 6 + Math.floor(rand() * 4) : tail ? 1 : 2 + Math.floor(rand() * 3);
  const claims = heavy ? 14 + Math.floor(rand() * 7) : tail ? 1 : 2 + Math.floor(rand() * 6);
  const status = pick(["draft", "draft", "draft", "validated", "deprecated"]);

  // The description is written the way a real one is: what it is, then a long
  // "Use when" trigger list, because splitDescription() cuts on exactly that
  // and a short description would never exercise the disclosure.
  const subject = stem.replace(/-/g, " ");
  const triggers = Array.from({ length: 3 + Math.floor(rand() * 5) }, (_, k) =>
    `when ${subject} is ${pick(["unmeasured", "assumed", "the current defence", "chosen by habit", "copied from a demo"])} and ${pick(["the loop stalls", "the budget is exceeded", "the receipt is missing", "the result cannot be reproduced", "a reviewer asks for evidence"])}`
  ).join("; ");
  const description =
    `DUMMY FIXTURE for layout verification, not a real skill. ${subject.charAt(0).toUpperCase()}${subject.slice(1)}` +
    `${word ? ` for ${word} work` : ""}: what the decision actually turns on and what each option costs in measured terms. ` +
    `Use when ${triggers}.`;

  const fm = [
    "---",
    `name: fixture-${String(i + 1).padStart(2, "0")}-${stem}`,
    `description: ${description}`,
    "version: 1",
    `status: ${status}`,
    "provenance:",
    "  extracted: 2026-10-07",
    `  validated: ${status === "validated" ? '"2026-10-07"' : '""'}`,
    "  reviews:",
    '    - "DUMMY FIXTURE. No review filed."',
    "  claims:",
    ...Array.from({ length: claims }, (_, k) => `    - "DUMMY FIXTURE claim ${k + 1} about ${subject}"`),
    "  papers:",
    ...Array.from({ length: papers }, (_, k) =>
      `    - "DUMMY FIXTURE: ${subject} paper ${k + 1} — arxiv.org/abs/2610.${String(1000 + i * 7 + k)}"`),
    "---",
    "",
    `# ${subject.charAt(0).toUpperCase()}${subject.slice(1)} (DUMMY FIXTURE)`,
    "",
    "This file exists only so the skills library can be judged at the volume the",
    "design targets. It is never committed; skills/fixture-* is gitignored.",
    "",
  ].join("\n");
  fs.writeFileSync(path.join(dir, "SKILL.md"), fm);
  made++;
}
console.log(`wrote ${made} fixture skills into ${SKILLS}`);
