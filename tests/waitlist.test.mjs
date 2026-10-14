// The signup path's decision logic, executed. Sprint 2026-10-05 item 2.
//
//     node --test tests/waitlist.test.mjs
//
// tests/test_waitlist.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// site/lib/waitlist-core.js is loaded by reading its source and evaluating it
// as a module rather than importing it by path, for the reason
// tests/accounts.test.mjs gives at length: the site is a Next.js app whose
// package.json declares no module type, so Node parses its .js files as
// CommonJS and an ordinary import of an ESM file there fails.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const path = fileURLToPath(new URL("../site/lib/waitlist-core.js", import.meta.url));
const source = await readFile(path, "utf8");
const core = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

// ------------------------------------------------------ which addresses

test("an address is folded to lower case and trimmed", () => {
  assert.equal(core.normalizeEmail("  Ada@Example.COM "), "ada@example.com");
});

test("the plausible-address check rejects what a person can see for themselves", () => {
  for (const bad of ["", "   ", "ada", "ada@", "@example.com", "ada@example",
                     "ada example@com", "ada@@example.com", null, undefined, 7]) {
    assert.equal(core.normalizeEmail(bad), null, `${bad} was accepted`);
  }
});

test("an address longer than RFC 5321 allows is refused", () => {
  const long = "a".repeat(250) + "@example.com";
  assert.ok(long.length > 254);
  assert.equal(core.normalizeEmail(long), null);
  const fine = "a".repeat(230) + "@example.com";
  assert.ok(fine.length <= 254);
  assert.equal(core.normalizeEmail(fine), fine);
});

test("an unusual but real address still gets through", () => {
  for (const good of ["ada+digest@example.co.uk", "a.b-c_d@sub.example.io",
                      "ada@example.museum"]) {
    assert.equal(core.normalizeEmail(good), good);
  }
});

// ------------------------------------------------------------ the source

test("the source is bounded and stripped to what a page slug can hold", () => {
  assert.equal(core.normalizeSource("/pricing"), "/pricing");
  assert.equal(core.normalizeSource("Home"), "home");
  // `/` survives on purpose, because a source is a page path. Everything a
  // tag or a quote needs does not.
  assert.equal(core.normalizeSource("<script>alert(1)</script>"), "scriptalert1/script");
  assert.equal(core.normalizeSource("x".repeat(80)).length, 32);
  assert.equal(core.normalizeSource(""), null);
  assert.equal(core.normalizeSource("!!!"), null);
  assert.equal(core.normalizeSource(undefined), null);
});

// --------------------------------------------------------------- the row

test("a signup is active and comped, which is what makes it not a waitlist", () => {
  // The whole of the sprint item, as one assertion. pipeline/weekly.py sends
  // to `status = 'active'` only, so any other status is a row somebody has to
  // promote by hand, which clause 1 of the definition of done rules out.
  const row = core.signupRow("Ada@Example.com", "home");
  assert.deepEqual(row, {
    email: "ada@example.com",
    tier: "digest",
    status: "active",
    comp: true,
    source: "home",
  });
});

test("no signup ever carries the status the old holding pen asked for", () => {
  // Over every input that produces a row at all, not just the happy one,
  // because `status` is the field the sprint item is actually about.
  for (const [email, src] of [["ada@example.com", "home"], ["b@c.io", null],
                              ["  D@E.ORG ", "/pricing"], ["f@g.dev", "!!!"]]) {
    assert.equal(core.signupRow(email, src).status, "active");
  }
});

test("a signup claims no money, because the phase charges nobody", () => {
  assert.equal(core.signupRow("ada@example.com").comp, true);
  assert.equal(core.signupRow("ada@example.com").tier, "digest");
});

test("a bad address produces no row at all rather than a row to clean up", () => {
  assert.equal(core.signupRow("ada", "home"), null);
  assert.equal(core.signupRow("", "home"), null);
});

// ----------------------------------------------------------- the outcome

test("the three outcomes are told apart", () => {
  assert.equal(core.signupOutcome({ inserted: true }), "created");
  assert.equal(core.signupOutcome({ inserted: true, wasUnsubscribed: true }), "created");
  assert.equal(core.signupOutcome({ inserted: false, wasUnsubscribed: true }), "resubscribed");
  assert.equal(core.signupOutcome({ inserted: false, wasUnsubscribed: false }), "already");
  assert.equal(core.signupOutcome(null), null);
});

test("every outcome is a success to the person who submitted the form", () => {
  for (const o of ["created", "resubscribed", "already"]) {
    assert.equal(core.isSuccess(o), true, o);
  }
  for (const o of [null, undefined, "refused", ""]) {
    assert.equal(core.isSuccess(o), false, String(o));
  }
});
