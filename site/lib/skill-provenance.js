// A skill's receipts: where its frontmatter says it came from, and what the
// last trigger test measured against the exact text on the page.
//
// This module is import-free on purpose, the same way site/lib/markdown-core.js
// and site/lib/account-core.js are, so tests/skill-provenance.test.mjs can load
// it by evaluating its source with no node_modules present. Everything that
// touches the filesystem or hashes a file stays in site/lib/content.js.
//
// Why it exists at all: every provenance field in a SKILL.md is indented under
// a `provenance:` key, and the reader in content.js matched keys anchored at
// column 0. So `validated`, `extracted` and the claim ids parsed as empty on
// every skill in the library, and the page had been quietly saying nothing
// about provenance since 2026-09-18. A field that silently reads as absent is
// worse than one that fails, because the page still renders.

// ------------------------------------------------------------- frontmatter

// The frontmatter this library writes is a two-level subset of YAML: scalars,
// one nested map, inline arrays of numbers, and block lists of quoted strings.
// Parsed structurally rather than by key regex, because a key regex cannot
// tell `papers:` inside `provenance:` from a `papers:` at the top level, and
// a description is free prose that may begin a line with anything at all.
export function splitFrontmatter(raw = "") {
  const m = String(raw).match(/^---\n([\s\S]*?)\n---/);
  return { fm: m ? m[1] : "", body: m ? String(raw).slice(m[0].length).trim() : String(raw).trim() };
}

function unquote(value) {
  const v = value.trim();
  if (v.length > 1 && ((v[0] === '"' && v.endsWith('"')) || (v[0] === "'" && v.endsWith("'")))) {
    return v.slice(1, -1);
  }
  return v;
}

// Inline arrays only ever hold claim ids here, so a non-numeric entry is
// dropped rather than guessed at.
function inlineArray(value) {
  return value
    .slice(1, -1)
    .split(",")
    .map((x) => unquote(x))
    .filter(Boolean);
}

// Lines are read as (indent, text) pairs and a key with no value on its own
// line is resolved by looking at the next one: a `- ` opens a block list, a
// deeper indent opens a map, and anything else leaves it an empty scalar.
// Lookahead rather than guesswork, because guessing is what the old reader did.
export function parseFrontmatter(fm = "") {
  const lines = String(fm)
    .split("\n")
    .filter((l) => l.trim() && !l.trimStart().startsWith("#"))
    .map((l) => ({ indent: l.length - l.trimStart().length, text: l.trim() }));

  const out = {};
  const stack = [{ indent: -1, node: out }];
  let list = null;

  for (let i = 0; i < lines.length; i++) {
    const { indent, text } = lines[i];

    const item = text.match(/^-\s+(.*)$/);
    if (item) {
      if (list) list.push(unquote(item[1]));
      continue;
    }

    const kv = text.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!kv) continue;
    const [, key, rawValue] = kv;
    const value = rawValue.trim();

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) stack.pop();
    const node = stack[stack.length - 1].node;
    list = null;

    if (value === "") {
      const next = lines[i + 1];
      if (next && next.indent > indent && /^-\s+/.test(next.text)) {
        node[key] = [];
        list = node[key];
      } else if (next && next.indent > indent) {
        node[key] = {};
        stack.push({ indent, node: node[key] });
      } else {
        node[key] = "";
      }
      continue;
    }
    node[key] =
      value.startsWith("[") && value.endsWith("]") ? inlineArray(value) : unquote(value);
  }
  return out;
}

// ---------------------------------------------------------------- provenance

// Provenance moved under a `provenance:` map on 2026-09-12 and the first
// skills wrote the same fields at the top level, so both shapes are read.
export function readProvenance(raw = "") {
  const { fm, body } = splitFrontmatter(raw);
  const f = parseFrontmatter(fm);
  const p = f.provenance && !Array.isArray(f.provenance) ? f.provenance : {};
  const claims = (Array.isArray(p.claims) ? p.claims : Array.isArray(f.claims) ? f.claims : [])
    .map((c) => String(c).trim())
    .filter((c) => /^\d+$/.test(c));
  const papers = Array.isArray(p.papers) ? p.papers : Array.isArray(f.papers) ? f.papers : [];
  return {
    name: typeof f.name === "string" ? f.name : "",
    description: typeof f.description === "string" ? f.description : "",
    version: typeof f.version === "string" ? f.version : "",
    status: typeof f.status === "string" ? f.status : "",
    extracted: typeof p.extracted === "string" ? p.extracted : "",
    validated: typeof p.validated === "string" ? p.validated : typeof f.validated === "string" ? f.validated : "",
    claims,
    papers,
    body,
  };
}

// ----------------------------------------------------------------- receipts

// Which bundle counts as the library's result for a skill. Newest first, and
// at one date the pre-registered engine wins: an experimental engine's run is
// a measurement of the engine, not a verdict on the skill, and the policy in
// skills/_validation/README.md is that only a pre-registered policy judges.
export function rankBundles(bundles = []) {
  return [...bundles]
    .filter((b) => b && typeof b.generated === "string")
    .sort((a, b) => {
      if (a.generated !== b.generated) return a.generated < b.generated ? 1 : -1;
      const pa = a.policy && a.policy.pre_registered ? 0 : 1;
      const pb = b.policy && b.policy.pre_registered ? 0 : 1;
      return pa - pb;
    });
}

// The receipt for one skill: what was measured, when, by which engine, and
// whether the text measured is the text on the page. `current` is the whole
// point of recording a sha per suite. A pass rate carried over from an earlier
// revision of the file is a claim about a document the reader cannot see, so
// the page says which revision it describes rather than implying today's.
export function latestValidation(bundles, skillName, skillSha = "") {
  for (const bundle of rankBundles(bundles)) {
    const suite = (bundle.suites || []).find((s) => s && s.skill === skillName);
    if (!suite || !suite.total) continue;
    const ci = Array.isArray(suite.reliability_ci95) ? suite.reliability_ci95 : null;
    return {
      date: bundle.generated,
      engine: bundle.engine || "",
      preRegistered: Boolean(bundle.policy && bundle.policy.pre_registered),
      passed: suite.passed,
      total: suite.total,
      rate: suite.total ? suite.passed / suite.total : 0,
      ci95: ci ? [ci[0], ci[1]] : null,
      narrow: suite.narrow_decisions || 0,
      sha256: suite.skill_sha256 || "",
      // no sha to compare against is not the same as a match, so an unknown
      // stays unknown rather than defaulting to reassuring
      current: skillSha && suite.skill_sha256 ? skillSha === suite.skill_sha256 : null,
    };
  }
  return null;
}

// "8/8, 100%" reads as a measurement. "100%" alone hides that it is eight
// cases, which is the number a reader needs to judge the claim.
export function formatRate(v) {
  if (!v || !v.total) return "";
  return `${v.passed}/${v.total} cases, ${Math.round(v.rate * 100)}%`;
}

// "2026-09-24" -> "September 24, 2026". A date a reader can say out loud,
// with no timezone in it, because a receipt's date is a calendar day and
// constructing a Date from it would shift it west of UTC.
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export function formatDate(iso = "") {
  const m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return String(iso);
  const month = MONTHS[Number(m[2]) - 1];
  return month ? `${month} ${Number(m[3])}, ${m[1]}` : String(iso);
}

// The receipt in words, composed here rather than in the component so the
// sentences a visitor reads are covered by tests. Each qualifier is a separate
// sentence and every one of them is a caveat the page owes the reader: the
// library's whole pitch is that a skill is checked, so the page has to be as
// plain about what a check did not establish as about what it did.
export function receiptSentences(v) {
  if (!v) {
    return ["No trigger test has been recorded against this skill yet."];
  }
  const cases = v.total === 1 ? "case" : "cases";
  const out = [
    `${v.passed} of ${v.total} trigger ${cases} passed on ${formatDate(v.date)}, engine ${v.engine}.`,
  ];
  if (v.current === false) {
    out.push(
      "The file has been revised since, so this result describes an earlier version of the text below."
    );
  } else if (v.current === true) {
    out.push("Measured against the exact text below.");
  }
  if (v.narrow > 0) {
    const n = v.narrow;
    out.push(
      `${n} of those ${n === 1 ? "decisions was" : "decisions were"} narrow, which means the skill outranked the decoy panel by less than the margin the policy sets in advance.`
    );
  }
  if (!v.preRegistered) {
    out.push(
      "The engine's policy was not registered before the run, so this measures the engine rather than settling anything about the skill."
    );
  }
  return out;
}
