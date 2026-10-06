// The unsubscribe path's decision logic, executed. Sprint 2026-10-05 item 3.
//
//     node --test tests/unsubscribe.test.mjs
//
// tests/test_unsubscribe.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// site/lib/unsubscribe-core.js is loaded by reading its source and evaluating
// it, for the reason tests/accounts.test.mjs gives at length: the site is a
// Next.js app whose package.json declares no module type, so Node parses its
// .js files as CommonJS and an ordinary import of an ESM file there fails.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const path = fileURLToPath(new URL("../site/lib/unsubscribe-core.js", import.meta.url));
const source = await readFile(path, "utf8");
const core = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

const TOKEN = "3f2504e0-4f89-11d3-9a0c-0305e82c3301";

// --------------------------------------------------------------- the token

test("a token is read case-insensitively and trimmed", () => {
  assert.equal(core.normalizeToken(` ${TOKEN.toUpperCase()} `), TOKEN);
});

test("anything that is not a uuid never reaches the database", () => {
  for (const bad of ["", "   ", "junk", TOKEN.slice(0, -1), TOKEN + "0",
                     TOKEN.replace("-", ""), "ada@example.com",
                     "' or 1=1 --", null, undefined, 7, {}]) {
    assert.equal(core.normalizeToken(bad), null, `${bad} was accepted`);
  }
});

test("a uuid with a character outside hex is not a uuid", () => {
  assert.equal(core.normalizeToken("3g2504e0-4f89-11d3-9a0c-0305e82c3301"), null);
});

// ---------------------------------------------------------------- the link

test("the link is the site root plus the token, with one slash", () => {
  const want = `https://libraryofalexandria.dev/unsubscribe?t=${TOKEN}`;
  assert.equal(core.unsubscribeUrl("https://libraryofalexandria.dev", TOKEN), want);
  assert.equal(core.unsubscribeUrl("https://libraryofalexandria.dev/", TOKEN), want);
  assert.equal(core.unsubscribeUrl("https://libraryofalexandria.dev///", TOKEN), want);
});

test("there is no link without a token and none without a base", () => {
  assert.equal(core.unsubscribeUrl("https://libraryofalexandria.dev", "junk"), null);
  assert.equal(core.unsubscribeUrl("https://libraryofalexandria.dev", null), null);
  assert.equal(core.unsubscribeUrl("", TOKEN), null);
  assert.equal(core.unsubscribeUrl(null, TOKEN), null);
});

test("no email address is ever in the link", () => {
  // The whole reason the link carries a token. An address in it means anybody
  // who knows an address can unsubscribe that person.
  const url = core.unsubscribeUrl("https://libraryofalexandria.dev", TOKEN);
  assert.ok(!url.includes("@"));
});

// --------------------------------------------------------------- the states

test("the four states are told apart", () => {
  assert.equal(core.unsubscribeState({ ok: true, found: true, changed: true }), "done");
  assert.equal(core.unsubscribeState({ ok: true, found: true, changed: false }), "already");
  assert.equal(core.unsubscribeState({ ok: true, found: false }), "unknown");
  assert.equal(core.unsubscribeState({ ok: false, retryable: true }), "unavailable");
  assert.equal(core.unsubscribeState({ ok: false, retryable: false }), "unknown");
});

test("a missing answer is unknown rather than a crash or a success", () => {
  for (const bad of [null, undefined, "done", 7]) {
    assert.equal(core.unsubscribeState(bad), "unknown", String(bad));
  }
});

test("clicking an old link a second time is not a failure", () => {
  // The most ordinary thing a person can do with a link in an email they kept.
  assert.equal(core.unsubscribeState({ ok: true, found: true, changed: false }), "already");
});

// --------------------------------------------------------------- the method

test("only a POST may change the row", () => {
  assert.equal(core.methodChangesTheRow("POST"), true);
  assert.equal(core.methodChangesTheRow("post"), true);
  for (const m of ["GET", "HEAD", "OPTIONS", "PUT", "DELETE", "", null, undefined]) {
    assert.equal(core.methodChangesTheRow(m), false, String(m));
  }
});

test("a mail scanner's HEAD and GET are the ones this is for", () => {
  // Mail scanners, link previewers and corporate security proxies fetch every
  // link in a message before any person reads it. A GET that flipped the row
  // would unsubscribe people who never clicked anything.
  assert.equal(core.methodChangesTheRow("GET"), false);
  assert.equal(core.methodChangesTheRow("HEAD"), false);
});
