// Every decision site/lib/skill-provenance.js makes, executed, plus the four
// real SKILL.md files and the four real result bundles run through it.
//
//     node --test tests/skill-provenance.test.mjs
//
// tests/test_skill_receipts.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// This needs no node_modules: the core module is import-free, so it loads by
// evaluating its source, the same way tests/markdown.test.mjs loads
// markdown-core.js. The bug that makes this file necessary is the one it opens
// with: a frontmatter reader whose key regex was anchored at column 0, reading
// a file whose every provenance field is indented.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";

const REPO = new URL("../", import.meta.url);
const core = await import(
  "data:text/javascript;base64," +
    Buffer.from(
      await readFile(fileURLToPath(new URL("site/lib/skill-provenance.js", REPO)), "utf8")
    ).toString("base64")
);

// ------------------------------------------------------------- frontmatter

test("an indented field is read, which is the whole bug", () => {
  const f = core.parseFrontmatter(
    ["name: a-skill", "provenance:", "  extracted: 2026-09-12", '  validated: "held up"'].join("\n")
  );
  assert.equal(f.name, "a-skill");
  assert.equal(f.provenance.extracted, "2026-09-12");
  assert.equal(f.provenance.validated, "held up");
});

test("a nested key does not leak to the top level", () => {
  const f = core.parseFrontmatter(["provenance:", "  extracted: 2026-09-12"].join("\n"));
  assert.equal(f.extracted, undefined);
});

test("an inline array of claim ids parses, and a stray quote is stripped", () => {
  const f = core.parseFrontmatter("provenance:\n  claims: [476, 477, 478]");
  assert.deepEqual(f.provenance.claims, ["476", "477", "478"]);
});

test("a block list of quoted strings attaches to the key that opened it", () => {
  const f = core.parseFrontmatter(
    ["provenance:", "  papers:", '    - "One — arxiv.org/abs/1"', '    - "Two — arxiv.org/abs/2"'].join("\n")
  );
  assert.deepEqual(f.provenance.papers, ["One — arxiv.org/abs/1", "Two — arxiv.org/abs/2"]);
});

test("a key that follows a block list is read as a key, not as another item", () => {
  const f = core.parseFrontmatter(
    ["provenance:", "  papers:", '    - "One"', "  extracted: 2026-09-12", "status: active"].join("\n")
  );
  assert.deepEqual(f.provenance.papers, ["One"]);
  assert.equal(f.provenance.extracted, "2026-09-12");
  assert.equal(f.status, "active");
});

test("a key whose value is an empty string stays an empty string", () => {
  const f = core.parseFrontmatter(['provenance:', '  validated: ""', "  claims: [1]"].join("\n"));
  assert.equal(f.provenance.validated, "");
});

test("a description that mentions a colon is not cut at it", () => {
  const f = core.parseFrontmatter("description: Use when: a thing happens, or when b: happens.");
  assert.equal(f.description, "Use when: a thing happens, or when b: happens.");
});

test("no frontmatter at all yields the whole file as the body", () => {
  const p = core.readProvenance("# Just a heading\n\nand a paragraph.");
  assert.equal(p.name, "");
  assert.deepEqual(p.claims, []);
  assert.equal(p.body, "# Just a heading\n\nand a paragraph.");
});

test("provenance written at the top level, the pre-2026-09-12 shape, still reads", () => {
  const p = core.readProvenance(
    ['---', "name: old-skill", 'validated: "an old note"', "claims: [7, 8]", '---', "body"].join("\n")
  );
  assert.equal(p.validated, "an old note");
  assert.deepEqual(p.claims, ["7", "8"]);
});

test("a non-numeric claim id is dropped rather than rendered", () => {
  const p = core.readProvenance(['---', "provenance:", "  claims: [12, tbd, 13]", '---', ""].join("\n"));
  assert.deepEqual(p.claims, ["12", "13"]);
});

// ----------------------------------------------------------------- receipts

const BUNDLE = (generated, engine, preRegistered, suites) => ({
  generated,
  engine,
  policy: { pre_registered: preRegistered },
  suites,
});
const SUITE = (skill, passed, total, sha, extra = {}) => ({
  skill,
  passed,
  total,
  skill_sha256: sha,
  reliability_ci95: [0.5, 1],
  narrow_decisions: 0,
  ...extra,
});

test("the newest bundle wins", () => {
  const v = core.latestValidation(
    [
      BUNDLE("2026-09-18", "lexical/2.1", true, [SUITE("a", 4, 6, "aaaa")]),
      BUNDLE("2026-09-24", "lexical/2.1", true, [SUITE("a", 6, 6, "aaaa")]),
    ],
    "a",
    "aaaa"
  );
  assert.equal(v.date, "2026-09-24");
  assert.equal(v.passed, 6);
});

test("at one date the pre-registered engine wins over the experiment", () => {
  const v = core.latestValidation(
    [
      BUNDLE("2026-09-24", "lexical/3", false, [SUITE("a", 2, 6, "aaaa")]),
      BUNDLE("2026-09-24", "lexical/2.1", true, [SUITE("a", 6, 6, "aaaa")]),
    ],
    "a",
    "aaaa"
  );
  assert.equal(v.engine, "lexical/2.1");
  assert.equal(v.preRegistered, true);
});

test("a bundle that never judged this skill is skipped, not reported as zero", () => {
  const v = core.latestValidation(
    [
      BUNDLE("2026-09-24", "lexical/2.1", true, [SUITE("b", 6, 6, "bbbb")]),
      BUNDLE("2026-09-18", "lexical/2.1", true, [SUITE("a", 5, 5, "aaaa")]),
    ],
    "a",
    "aaaa"
  );
  assert.equal(v.date, "2026-09-18");
  assert.equal(v.passed, 5);
});

test("no receipt at all is null, and the page says so in words", () => {
  assert.equal(core.latestValidation([], "a", "aaaa"), null);
  assert.deepEqual(core.receiptSentences(null), [
    "No trigger test has been recorded against this skill yet.",
  ]);
});

test("a sha that matches says so, and one that does not says the file moved", () => {
  const fresh = core.latestValidation([BUNDLE("2026-09-24", "e", true, [SUITE("a", 6, 6, "aaaa")])], "a", "aaaa");
  assert.equal(fresh.current, true);
  const stale = core.latestValidation([BUNDLE("2026-09-24", "e", true, [SUITE("a", 6, 6, "aaaa")])], "a", "zzzz");
  assert.equal(stale.current, false);
  assert.match(core.receiptSentences(stale)[1], /revised since/);
});

test("an unknown sha stays unknown rather than defaulting to reassuring", () => {
  const v = core.latestValidation([BUNDLE("2026-09-24", "e", true, [SUITE("a", 6, 6, "")])], "a", "aaaa");
  assert.equal(v.current, null);
  // no revision sentence at all, because the page cannot honestly write one
  assert.equal(core.receiptSentences(v).length, 1);
});

test("a narrow decision is disclosed, not rounded away by a 100% pass rate", () => {
  const v = core.latestValidation(
    [BUNDLE("2026-09-24", "e", true, [SUITE("a", 6, 6, "aaaa", { narrow_decisions: 1 })])],
    "a",
    "aaaa"
  );
  assert.equal(v.rate, 1);
  const said = core.receiptSentences(v).join(" ");
  assert.match(said, /narrow/);
});

test("an unregistered policy is disclosed as a measurement of the engine", () => {
  const v = core.latestValidation([BUNDLE("2026-09-24", "lexical/3", false, [SUITE("a", 2, 6, "aaaa")])], "a", "aaaa");
  const said = core.receiptSentences(v).join(" ");
  assert.match(said, /not registered before the run/);
});

test("the rate is stated as a count as well as a percentage", () => {
  assert.equal(
    core.formatRate({ passed: 6, total: 8, rate: 0.75 }),
    "6/8 cases, 75%"
  );
  assert.equal(core.formatRate(null), "");
});

test("a one-case suite is singular", () => {
  const v = core.latestValidation([BUNDLE("2026-09-24", "e", true, [SUITE("a", 1, 1, "aaaa")])], "a", "aaaa");
  assert.match(core.receiptSentences(v)[0], /1 of 1 trigger case passed/);
});

test("a date is a calendar day and never shifts a timezone", () => {
  assert.equal(core.formatDate("2026-09-24"), "September 24, 2026");
  assert.equal(core.formatDate("2026-01-01"), "January 1, 2026");
  assert.equal(core.formatDate(""), "");
  assert.equal(core.formatDate("not a date"), "not a date");
});

// ------------------------------------------------------- the real library

const SKILLS = fileURLToPath(new URL("skills/", REPO));
const RESULTS = fileURLToPath(new URL("skills/_validation/results/", REPO));

async function realSkills() {
  const dirs = (await readdir(SKILLS, { withFileTypes: true }))
    .filter((d) => d.isDirectory() && !d.name.startsWith("_"))
    .map((d) => d.name);
  const out = [];
  for (const name of dirs) {
    let raw;
    try {
      raw = await readFile(`${SKILLS}${name}/SKILL.md`, "utf8");
    } catch {
      continue;
    }
    out.push({ dir: name, raw, provenance: core.readProvenance(raw) });
  }
  return out;
}

async function realBundles() {
  const files = (await readdir(RESULTS)).filter((f) => f.endsWith(".json"));
  return Promise.all(files.map(async (f) => JSON.parse(await readFile(RESULTS + f, "utf8"))));
}

const LIBRARY = await realSkills();
const BUNDLES = await realBundles();

test("the library is not empty, so the assertions below mean something", () => {
  assert.ok(LIBRARY.length >= 4, `${LIBRARY.length} skills found`);
  assert.ok(BUNDLES.length >= 1);
});

test("every skill in the library has a name, a version and a distilled date", () => {
  for (const s of LIBRARY) {
    assert.equal(s.provenance.name, s.dir, `${s.dir}: name does not match its directory`);
    assert.notEqual(s.provenance.version, "", `${s.dir}: no version`);
    assert.match(s.provenance.extracted, /^\d{4}-\d{2}-\d{2}$/, `${s.dir}: no distilled date`);
  }
});

// A draft may cite no claim ids. The authority for that is
// `waiting_on_the_queue` in tools/panel_provenance.py, which is the gate that
// turns `main` red, and tests/test_skill_receipts.py calls it directly rather
// than restating it. This file cannot: it is import-free by design and runs
// without node_modules. So it checks the weaker half of the same law, the half
// that needs no reading queue, and it checks the direction that keeps the gate
// shut: published advice must cite its claims, and a draft is the only thing
// that may be waiting.
//
// `skills/agent-containment` is the live case. It landed on 2026-09-30 naming
// six papers and zero claims because none of the six had a claim id in the
// database yet, and docs/research/reading-queue.md carries the unchecked lines
// that fix that.
test("every skill renders papers, and only a draft may still cite no claims", () => {
  for (const s of LIBRARY) {
    assert.ok(s.provenance.papers.length > 0, `${s.dir}: no papers parsed`);
    for (const c of s.provenance.claims) assert.match(c, /^\d+$/);
    if (s.provenance.claims.length === 0) {
      assert.equal(
        s.provenance.status,
        "draft",
        `${s.dir}: published advice citing no claim ids`
      );
    }
  }
});

// The companion to the test above, and the reason the carve-out is still a
// gate. One draft waiting on a read is the state the law describes; a library
// where most skills cite nothing is the state the law was meant to catch, and
// it would read as green under the test above alone.
test("the claim ids still reach almost every skill, so the carve-out is not the rule", () => {
  const citing = LIBRARY.filter((s) => s.provenance.claims.length > 0);
  assert.ok(
    citing.length >= LIBRARY.length - 1,
    `${LIBRARY.length - citing.length} of ${LIBRARY.length} skills cite no claim ids`
  );
});

// This used to assert `claims.includes("199")` as its proof that ids parse.
// The proxy broke for a correct reason: ADR-38's quality bar cut three sections
// from this skill on 2026-09-30, and the skill's own `revisions:` entry records
// that claims 199, 136, 140, 190 and 243 left the provenance with the sections
// they supported. Pinning one id forbids the revision the library's law
// requires, so the assertion is the law now: ids parse, and a retired id does
// not come back without its section.
test("harness-engineering's validated note renders, the sprint item's named case", () => {
  const he = LIBRARY.find((s) => s.dir === "harness-engineering");
  assert.ok(he, "harness-engineering is missing from the library");
  assert.match(he.provenance.validated, /A\/B trial/);
  assert.ok(he.provenance.claims.length > 0, "no claim ids parsed");
  for (const retired of ["199", "136", "140", "190", "243"]) {
    assert.ok(
      !he.provenance.claims.includes(retired),
      `claim ${retired} was retired by the 2026-09-30 revision and is back on the page`
    );
  }
});

test("every skill in the library has a dated validation result", () => {
  for (const s of LIBRARY) {
    const sha = createHash("sha256").update(s.raw, "utf8").digest("hex").slice(0, 16);
    const v = core.latestValidation(BUNDLES, s.provenance.name, sha);
    assert.ok(v, `${s.dir}: no trigger-test result in skills/_validation/results`);
    assert.match(v.date, /^\d{4}-\d{2}-\d{2}$/);
    assert.ok(v.total > 0, `${s.dir}: a receipt with no cases in it`);
    assert.notEqual(v.engine, "");
    // the receipt must be readable as prose, since that is what ships
    for (const line of core.receiptSentences(v)) assert.ok(line.endsWith("."), line);
  }
});

test("the receipt shown for each skill is the pre-registered engine's", () => {
  for (const s of LIBRARY) {
    const v = core.latestValidation(BUNDLES, s.provenance.name, "");
    assert.equal(v.preRegistered, true, `${s.dir}: the experiment is being shown as the verdict`);
  }
});
