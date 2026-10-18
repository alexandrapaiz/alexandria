// The buyer-path measurement's decision logic, executed. Board card c688ef2e.
//
//     node --test tests/path.test.mjs
//
// tests/test_buyer_path.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// site/lib/path-core.js is loaded by reading its source and evaluating it as a
// module rather than importing it by path, for the reason
// tests/accounts.test.mjs gives at length: the site is a Next.js app whose
// package.json declares no module type, so Node parses its .js files as
// CommonJS and an ordinary import of an ESM file there fails.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const load = async (relative) => {
  const path = fileURLToPath(new URL(relative, import.meta.url));
  const source = await readFile(path, "utf8");
  return import("data:text/javascript;base64," + Buffer.from(source).toString("base64"));
};

const core = await load("../site/lib/path-core.js");
const schema = await readFile(
  fileURLToPath(new URL("../db/schema.sql", import.meta.url)), "utf8");

// ------------------------------------------------- the promise, as assertions
//
// These three are the whole reason this measurement is shaped the way it is.
// site/app/privacy/page.jsx tells a reader there is no third-party script
// watching them read, and a later edit that quietly adds an identifier is the
// one change to this file that would break a promise rather than a build.

// Comments are stripped first, because this file's header explains at length
// what it refuses to do and the words it uses to explain it are the words
// being searched for. A check that reads prose would fail on the explanation
// of why it passes, which is the kind of gate someone switches off.
const codeOnly = (text) =>
  text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");

test("no function here produces an identifier of any kind", async () => {
  const source = codeOnly(await readFile(
    fileURLToPath(new URL("../site/lib/path-core.js", import.meta.url)), "utf8"));
  // A hash of an address and a user agent is what every cookieless analytics
  // product ships, and it is still a pseudonymous identifier for one person.
  for (const banned of ["createHash", "sha256", "node:crypto", "cookie",
                        "localStorage", "sessionStorage", "headers.get(\"x-forwarded-for\")",
                        "user-agent"]) {
    assert.ok(!source.includes(banned), `path-core.js reaches for ${banned}`);
  }
});

test("neither does the half that talks to the database", async () => {
  // The I/O half is where an identifier would actually have to be written, so
  // it is checked on the same list rather than trusted to the core's purity.
  for (const file of ["../site/lib/path.js", "../site/middleware.js",
                      "../site/app/api/funnel/route.js"]) {
    const source = codeOnly(await readFile(
      fileURLToPath(new URL(file, import.meta.url)), "utf8"));
    for (const banned of ["createHash", "x-forwarded-for", "user-agent",
                          "cookies", "localStorage"]) {
      assert.ok(!source.includes(banned), `${file} reaches for ${banned}`);
    }
  }
});

test("the row a request becomes holds three fields and none of them is a person", () => {
  const row = core.pathRow({ pathname: "/skills/agent-memory-selection" });
  assert.deepEqual(Object.keys(row).sort(), ["detail", "path", "step"]);
});

test("a query string never reaches the row, because that is where an address lands", () => {
  const row = core.pathRow({ pathname: "/pricing?email=ada@example.com&utm=x" });
  assert.equal(row.path, "/pricing");
  assert.equal(row.detail, null);
  assert.ok(!JSON.stringify(row).includes("ada"));
});

// ------------------------------------------------------- the steps agree
//
// The five words exist in two places and must stay one list.

test("the five steps in the core are exactly the five the schema accepts", () => {
  const body = schema.match(
    /create table if not exists\s+path_events\s*\(([\s\S]*?)\n\);/i)[1];
  const allowed = body.match(/check \(step in \(([\s\S]*?)\)\)/i);
  assert.ok(allowed, "path_events.step accepts any string");
  const words = allowed[1].match(/'(\w+)'/g).map((w) => w.slice(1, -1));
  assert.deepEqual(words.sort(), [...core.STEPS].sort());
});

test("the two steps that are not rows in that table are named and are not in it", () => {
  // Named constants rather than strings scattered through the reader, because
  // a funnel that silently skips a step reads as a funnel with no such step.
  assert.equal(core.INSTALL_STEP, "install");
  assert.equal(core.PAYMENT_STEP, "payment");
  assert.ok(!core.STEPS.includes(core.INSTALL_STEP));
  assert.ok(!core.STEPS.includes(core.PAYMENT_STEP));
});

// ------------------------------------------------------ which requests count

test("a prefetch is not a visit, whichever header announces it", () => {
  for (const headers of [
    { "next-router-prefetch": "1" },
    { purpose: "prefetch" },
    { "x-purpose": "Prefetch" },
    { Purpose: "PREFETCH" },
  ]) {
    assert.equal(core.isCounted({ pathname: "/pricing", headers }), false,
      JSON.stringify(headers));
  }
  assert.equal(core.isCounted({ pathname: "/pricing", headers: {} }), true);
});

test("a prefetch header is read off a real Headers object too", () => {
  const headers = new Headers({ "next-router-prefetch": "1" });
  assert.equal(core.isPrefetch(headers), true);
  assert.equal(core.isPrefetch(new Headers({})), false);
});

test("only a GET is a page view", () => {
  for (const method of ["POST", "HEAD", "PUT", "DELETE", "OPTIONS"]) {
    assert.equal(core.isCounted({ method, pathname: "/pricing" }), false, method);
  }
  assert.equal(core.isCounted({ method: "get", pathname: "/pricing" }), true);
});

test("the framework, the assets and this measurement's own surface are never counted", () => {
  for (const pathname of ["/_next/static/x", "/favicon.ico", "/robots.txt",
                          "/sitemap.xml", "/llms.txt", "/api/funnel",
                          "/__clerk/handshake", "/globals.css"]) {
    assert.equal(core.isCounted({ pathname }), false, pathname);
  }
});

test("a path that is not a path is refused rather than guessed at", () => {
  for (const pathname of ["", "pricing", "https://elsewhere.example/x"]) {
    assert.equal(core.isCounted({ pathname }), false, JSON.stringify(pathname));
  }
  assert.equal(core.pathRow({ pathname: "" }), null);
});

// --------------------------------------------------------------- which step

test("every page a buyer walks lands on the step it belongs to", () => {
  const cases = {
    "/": "visit",
    "/mission": "visit",
    "/library": "visit",
    "/library/2026-W39": "visit",
    "/skills": "catalog",
    "/skills/agent-memory-selection": "skill",
    "/pricing": "pricing",
    "/api/checkout/monthly": "checkout",
  };
  for (const [path, step] of Object.entries(cases)) {
    assert.equal(core.stepForPath(path), step, path);
  }
});

test("the catalogue and one skill are different steps, which is the card's question", () => {
  // "Without it nobody can tell which skill actually sells" is the card's own
  // sentence. A catalogue view and a skill view counted as one step cannot
  // answer it.
  assert.equal(core.stepForPath("/skills"), "catalog");
  assert.equal(core.stepForPath("/skills/"), "catalog");
  assert.equal(core.stepForPath("/skills/harness-engineering"), "skill");
});

// --------------------------------------------------------------- the path

test("a path with a per-week or per-skill identifier collapses to one value", () => {
  assert.equal(core.groupedPath("/library/2026-W39"), "/library/:week");
  assert.equal(core.groupedPath("/library/2026-W40"), "/library/:week");
  assert.equal(core.groupedPath("/skills/harness-engineering"), "/skills/:slug");
  assert.equal(core.groupedPath("/api/checkout/lifetime"), "/api/checkout/:plan");
  // The pages themselves keep their own names.
  assert.equal(core.groupedPath("/library"), "/library");
  assert.equal(core.groupedPath("/skills"), "/skills");
});

test("a trailing slash is the same page, and the root is still the root", () => {
  assert.equal(core.normalizePath("/pricing/"), "/pricing");
  assert.equal(core.normalizePath("/"), "/");
  assert.equal(core.normalizePath(""), "/");
});

test("the path is bounded, because it arrives in a request and ends in a column", () => {
  assert.ok(core.normalizePath("/" + "a".repeat(400)).length <= 128);
});

// ------------------------------------------------------------- the detail

test("a skill row carries which skill and a checkout row carries which plan", () => {
  assert.equal(core.detailFor("skill", "/skills/harness-engineering"),
    "harness-engineering");
  assert.equal(core.detailFor("checkout", "/api/checkout/monthly"), "monthly");
});

test("every other step carries no detail rather than a copy of its own path", () => {
  for (const step of ["visit", "catalog", "pricing"]) {
    assert.equal(core.detailFor(step, "/pricing"), null, step);
  }
});

test("the detail is bounded and stripped to what a slug can hold", () => {
  assert.equal(core.normalizeDetail("Harness-Engineering"), "harness-engineering");
  assert.equal(core.normalizeDetail("<script>alert(1)</script>"), "scriptalert1script");
  assert.equal(core.normalizeDetail("x".repeat(200)).length, 64);
  assert.equal(core.normalizeDetail("!!!"), null);
  assert.equal(core.normalizeDetail(undefined), null);
});

// -------------------------------------------------------------- the funnel

test("the funnel prints the install between the catalogue and the pricing page", () => {
  // Where the gap actually is, rather than appended at the end where a reader
  // would read it as the last thing a buyer does.
  const rows = core.funnel({}).rows.map((r) => r.step);
  assert.deepEqual(rows, ["visit", "catalog", "skill", "install", "pricing",
                          "checkout", "payment"]);
});

test("a step with no rows reads zero and a step nobody can read reads null", () => {
  const { rows } = core.funnel({ counts: { visit: 9 } });
  const by = Object.fromEntries(rows.map((r) => [r.step, r]));
  assert.equal(by.visit.events, 9);
  // Readable and empty: the table answered and held nothing.
  assert.equal(by.catalog.events, 0);
  assert.equal(by.catalog.measured, true);
  // Unreadable: never zero, and it carries the reason.
  assert.equal(by.install.events, null);
  assert.equal(by.install.measured, false);
  assert.ok(by.install.note);
  assert.equal(by.payment.events, null);
  assert.equal(by.payment.measured, false);
});

test("an install count arrives the day a reader for it exists, with no other change", () => {
  const { rows } = core.funnel({ install: { clones: 12 } });
  const install = rows.find((r) => r.step === "install");
  assert.equal(install.events, 12);
  assert.equal(install.measured, true);
});

test("a payment is read from the billing record and zero is a real answer there", () => {
  const { rows } = core.funnel({ paid: { accounts: 0 } });
  const payment = rows.find((r) => r.step === "payment");
  assert.equal(payment.events, 0);
  assert.equal(payment.measured, true);
});

test("the funnel refuses a conversion rate and says why in the field itself", () => {
  const out = core.funnel({ counts: { visit: 100, checkout: 1 } });
  assert.equal(out.rate, null);
  assert.match(out.rate_reason, /not counts of people/);
});

test("a nonsense count cannot become a number in the funnel", () => {
  const { rows } = core.funnel({ counts: { visit: "many", catalog: -4 } });
  const by = Object.fromEntries(rows.map((r) => [r.step, r]));
  // Falls back to the zero a readable-and-empty table means, never to NaN.
  assert.equal(by.visit.events, 0);
  assert.equal(by.catalog.events, 0);
});
