// The archive's publishing rules, executed.
//
//     node --test tests/issues.test.mjs
//
// tests/test_issue_route.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// site/lib/issues-core.js is loaded by reading its source and evaluating it as
// a module, rather than imported by path, for the reason tests/accounts.test.mjs
// gives: the site's package.json declares no module type, so Node parses its
// .js files as CommonJS and a plain import of an ESM file there fails. The core
// has no imports, so this runs the real source with no build step, no
// node_modules and no database.
//
// What is worth holding here is not the happy listing. It is the three
// properties that decide whether turning this on is safe, every one of them a
// way this could have shipped a regression onto a public page twelve days
// before launch:
//
//   1. A database that cannot be read publishes exactly what the committed
//      files publish, which is today's behaviour.
//   2. HIDDEN_WEEKS still retires a week, including a week that exists only as
//      a row. That set is the owner's veto over the archive and the record is a
//      new way into it.
//   3. The committed file wins over the row, so every correction already made
//      to a published issue still stands.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const path = fileURLToPath(new URL("../site/lib/issues-core.js", import.meta.url));
const source = await readFile(path, "utf8");
const core = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

const HIDDEN = new Set(["2026-W37"]);

// The real derivation, copied in behaviour rather than imported, because
// site/lib/content.js imports node:fs and cannot be loaded this way. The test
// for the real `parseIssue` being the one production uses is in
// tests/test_issue_route.py, which reads the import.
const parse = (week, body) => ({
  week,
  body,
  title: (body.match(/^# (.+)$/m) || [])[1] || "",
  dates: `range(${week})`,
  excerpt: body
    .split(/\n\n+/)
    .map((s) => s.trim())
    .filter((s) => s && !/^[#*\-]/.test(s))[0] || "",
});

const row = (week, text = "body of " + week) => ({
  week,
  body: `# Title of ${week}\n\n*the masthead*\n\n${text}\n`,
});

const file = (week) => parse(week, `# Committed ${week}\n\nthe committed text\n`);

// ---------------------------------------------------------------------------
// 1. The database cannot be read

test("no connection publishes the committed files and nothing less", async () => {
  const files = [file("2026-W39")];
  const list = core.mergeIssues({
    files,
    rows: await core.readListing(null),
    hidden: HIDDEN,
    parse,
  });
  assert.deepEqual(
    list.map((i) => [i.week, i.source]),
    [["2026-W39", "file"]]
  );
});

test("a query that throws publishes the committed files, not an empty archive", async () => {
  const angry = () => Promise.reject(new Error("neon: connection refused"));
  assert.equal(await core.readListing(angry), null);
  assert.equal(await core.readWeek(angry, "2026-W40"), null);

  const list = core.mergeIssues({
    files: [file("2026-W39")],
    rows: await core.readListing(angry),
    hidden: HIDDEN,
    parse,
  });
  assert.equal(list.length, 1, "an outage must not be able to unpublish an issue");
});

test("null rows and no rows are the same answer here, and neither is a failure", () => {
  const files = [file("2026-W39")];
  const a = core.mergeIssues({ files, rows: null, hidden: HIDDEN, parse });
  const b = core.mergeIssues({ files, rows: [], hidden: HIDDEN, parse });
  assert.deepEqual(a, b);
});

// ---------------------------------------------------------------------------
// 2. The owner's veto

test("a hidden week stays retired when it exists only as a row", () => {
  const list = core.mergeIssues({
    files: [],
    rows: [row("2026-W37"), row("2026-W39")],
    hidden: HIDDEN,
    parse,
  });
  assert.deepEqual(list.map((i) => i.week), ["2026-W39"]);
});

test("a hidden week stays retired on its own route, from either source", () => {
  assert.equal(
    core.pickIssue({ week: "2026-W37", row: row("2026-W37"), hidden: HIDDEN, parse }),
    null
  );
  assert.equal(
    core.pickIssue({ week: "2026-W37", file: file("2026-W37"), hidden: HIDDEN, parse }),
    null
  );
});

// ---------------------------------------------------------------------------
// 3. The committed file wins

test("the committed file supplies the text of a week that has one", () => {
  const picked = core.pickIssue({
    week: "2026-W39",
    file: file("2026-W39"),
    row: row("2026-W39"),
    hidden: HIDDEN,
    parse,
  });
  assert.equal(picked.source, "file");
  assert.match(picked.body, /the committed text/);
  assert.doesNotMatch(picked.body, /body of 2026-W39/);
});

test("the listing prefers the file for a week it has and the row for one it does not", () => {
  const list = core.mergeIssues({
    files: [file("2026-W39")],
    rows: [row("2026-W39"), row("2026-W40")],
    hidden: HIDDEN,
    parse,
  });
  assert.deepEqual(
    list.map((i) => [i.week, i.source]),
    [
      ["2026-W40", "record"],
      ["2026-W39", "file"],
    ],
    "newest first, and the file wins where both exist"
  );
});

test("a week that exists only as a row is published, which is the point", () => {
  const picked = core.pickIssue({
    week: "2026-W40",
    file: null,
    row: row("2026-W40"),
    hidden: HIDDEN,
    parse,
  });
  assert.equal(picked.source, "record");
  assert.equal(picked.title, "Title of 2026-W40");
});

// ---------------------------------------------------------------------------
// What a row has to be before it is published

test("a row with no body, or only whitespace, is not an issue", () => {
  for (const body of [null, undefined, "", "   \n\n  "]) {
    assert.equal(
      core.publishable({ week: "2026-W40", body }, HIDDEN),
      false,
      `a row whose body is ${JSON.stringify(body)} must not render as a blank issue`
    );
  }
});

test("a row whose week the site cannot address is skipped rather than thrown", () => {
  const list = core.mergeIssues({
    files: [],
    rows: [
      { week: "nonsense", body: "# x\n\ny\n" },
      { week: null, body: "# x\n\ny\n" },
      row("2026-W40"),
    ],
    hidden: HIDDEN,
    parse,
  });
  assert.deepEqual(list.map((i) => i.week), ["2026-W40"]);
});

test("ISSUE_WEEK is the one week shape, and it is anchored", () => {
  for (const good of ["2026-W01", "2026-W40", "1999-W52"]) {
    assert.ok(core.ISSUE_WEEK.test(good), good);
  }
  for (const bad of ["2026-W1", "2026-W401", "x2026-W40", "2026-W40/../x", ""]) {
    assert.ok(!core.ISSUE_WEEK.test(bad), bad);
  }
});

// ---------------------------------------------------------------------------
// The listing cannot leak a body

test("the listing shape has no body, because the query only read the head of one", () => {
  const list = core.mergeIssues({
    files: [file("2026-W39")],
    rows: [row("2026-W40")],
    hidden: HIDDEN,
    parse,
  });
  for (const issue of list) {
    assert.deepEqual(Object.keys(issue).sort(), [
      "dates",
      "excerpt",
      "source",
      "title",
      "week",
    ]);
  }
});

// ---------------------------------------------------------------------------
// The queries

test("the listing reads the head of each body, newest first, capped", async () => {
  const asked = [];
  const sql = (strings, ...values) => {
    asked.push({ text: strings.join("?"), values });
    return Promise.resolve([row("2026-W40")]);
  };
  const rows = await core.readListing(sql);
  assert.equal(rows.length, 1);

  const q = asked[0];
  assert.match(q.text, /from digests/);
  assert.match(q.text, /left\(body, \?\)/, "only the head of each body");
  assert.match(q.text, /order by week desc/);
  assert.match(q.text, /limit/);
  assert.deepEqual(q.values, [core.LISTING_HEAD, core.LISTING_WEEKS]);
});

test("the week read interpolates the week rather than concatenating it", async () => {
  const asked = [];
  const sql = (strings, ...values) => {
    asked.push({ text: strings.join("?"), values });
    return Promise.resolve([row("2026-W40")]);
  };
  const got = await core.readWeek(sql, "2026-W40");
  assert.equal(got.week, "2026-W40");

  const q = asked[0];
  assert.match(q.text, /where week = \?/);
  assert.deepEqual(q.values, ["2026-W40"]);
  assert.doesNotMatch(q.text, /2026-W40/, "the value must not be in the query text");
});

test("a week the site cannot address never reaches the database", async () => {
  let called = 0;
  const sql = () => {
    called += 1;
    return Promise.resolve([]);
  };
  for (const bad of ["nonsense", "2026-W40'; drop table digests; --", null, ""]) {
    assert.equal(await core.readWeek(sql, bad), null);
  }
  assert.equal(called, 0);
});

test("a week with no row resolves to null, which the route turns into a 404", async () => {
  const sql = () => Promise.resolve([]);
  assert.equal(await core.readWeek(sql, "2026-W40"), null);
});
