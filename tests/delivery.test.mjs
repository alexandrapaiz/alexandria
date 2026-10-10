// The delivery receipt's shaping layer, executed.
//
//     node --test tests/delivery.test.mjs
//
// tests/test_delivery_receipt.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// site/lib/delivery-core.js is loaded by reading its source and evaluating it,
// rather than imported by path, for the reason tests/accounts.test.mjs gives:
// the site's package.json declares no module type, so Node parses its .js files
// as CommonJS and a plain import of an ESM file there fails. This runs the real
// source with no build step.
//
// What is worth testing here is not the happy shape. It is that a column added
// to one of these tables cannot escape through this endpoint, because the
// endpoint is public and the issue body and the claim text are the product.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const path = fileURLToPath(new URL("../site/lib/delivery-core.js", import.meta.url));
const source = await readFile(path, "utf8");
const core = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

const FULL = {
  digest: { week: "2026-W39", model: "kimi-k2", created_at: new Date("2026-09-28T09:03:00Z") },
  papers: new Date("2026-09-30T12:01:00Z"),
  claims: new Date("2026-09-30T14:02:00Z"),
  // Postgres returns `count(*)` as a bigint, which the Neon driver hands back
  // as a string. The fixture carries the strings for that reason and not by
  // accident: a receipt publishing "212" would make the reader's `depth == 0`
  // comparison read a deep queue as neither empty nor deep.
  queues: { triage_pending: "41", distill_pending: "212", interpret_pending: "7" },
  deploy: [
    {
      app: "triage",
      runtime_sha: "0a1b2c3d4e5f",
      entrypoint: "pipeline/triage.py",
      file_count: 4,
      recorded_at: new Date("2026-09-30T12:00:10Z"),
      first_seen_at: new Date("2026-09-26T12:00:10Z"),
      notified_at: null,
    },
  ],
  observedAt: new Date("2026-10-01T02:00:00Z"),
};

test("the receipt names itself and its version, so a reader can refuse an unknown one", () => {
  const r = core.buildReceipt(FULL);
  assert.equal(r.receipt, "alexandria-delivery");
  assert.equal(r.version, core.RECEIPT_VERSION);
  assert.equal(r.observed_at, "2026-10-01T02:00:00.000Z");
});

test("the five facts come through in one shape", () => {
  const r = core.buildReceipt(FULL);
  assert.deepEqual(r.press, {
    newest_week: "2026-W39",
    created_at: "2026-09-28T09:03:00.000Z",
    model: "kimi-k2",
  });
  assert.deepEqual(r.pipeline, {
    papers_newest: "2026-09-30T12:01:00.000Z",
    claims_newest: "2026-09-30T14:02:00.000Z",
  });
  assert.deepEqual(r.queues, {
    triage_pending: 41,
    distill_pending: 212,
    interpret_pending: 7,
  });
  assert.equal(r.deploy[0].app, "triage");
  assert.equal(r.deploy[0].runtime_sha, "0a1b2c3d4e5f");
  assert.equal(r.deploy[0].file_count, 4);
  assert.equal(r.deploy[0].notified_at, null);
});

test("the issue body cannot escape, even when the row carries it", () => {
  // The route does not select `body` and this is the second line of defence:
  // every field is built by name, so a wider query cannot publish the product.
  const r = core.buildReceipt({
    ...FULL,
    digest: { ...FULL.digest, body: "# The whole issue\n\nevery paid word", prompt_sha: "deadbeef" },
  });
  const json = JSON.stringify(r);
  assert.equal(Object.keys(r.press).sort().join(","), "created_at,model,newest_week");
  assert.ok(!json.includes("every paid word"));
  assert.ok(!json.includes("deadbeef"));
});

test("a deploy row carrying an unexpected column does not widen the receipt", () => {
  const r = core.buildReceipt({
    ...FULL,
    deploy: [{ ...FULL.deploy[0], secret_note: "do not publish me" }],
  });
  assert.ok(!JSON.stringify(r).includes("do not publish me"));
  assert.equal(
    Object.keys(r.deploy[0]).sort().join(","),
    "app,entrypoint,file_count,first_seen_at,notified_at,recorded_at,runtime_sha"
  );
});

test("the top level has exactly six keys", () => {
  assert.deepEqual(Object.keys(core.buildReceipt(FULL)).sort(), [
    "deploy",
    "observed_at",
    "press",
    "pipeline",
    "queues",
    "receipt",
    "version",
  ].sort());
});

test("the queue depths come back as numbers, from the driver's bigint strings", () => {
  const r = core.buildReceipt(FULL);
  assert.deepEqual(r.queues, {
    triage_pending: 41,
    distill_pending: 212,
    interpret_pending: 7,
  });
});

test("a queue of zero and an unreadable queue are different answers", () => {
  // The same distinction `deploy` makes, and the reason it matters more here:
  // zero is half of the diagnosis. An empty distill queue says the stage had
  // nothing to read, so a failed read that reported zero would name a cause
  // that nobody established.
  const empty = core.buildReceipt({
    ...FULL,
    queues: { triage_pending: 0, distill_pending: 0, interpret_pending: 0 },
  });
  assert.equal(empty.queues.distill_pending, 0);
  assert.equal(core.buildReceipt({ ...FULL, queues: null }).queues, null);
  assert.equal(core.buildReceipt({ ...FULL, queues: undefined }).queues, null);
});

test("a queue row carrying an unexpected column does not widen the receipt", () => {
  const r = core.buildReceipt({
    ...FULL,
    queues: { ...FULL.queues, next_title: "do not publish me" },
  });
  assert.ok(!JSON.stringify(r).includes("do not publish me"));
  assert.equal(
    Object.keys(r.queues).sort().join(","),
    "distill_pending,interpret_pending,triage_pending"
  );
});

test("an empty digests table is null, which is a fact and not a failure to read", () => {
  const r = core.buildReceipt({ ...FULL, digest: null });
  assert.equal(r.press, null);
});

test("deploy null and deploy empty are different answers", () => {
  // null is "the query could not run", [] is "the table is empty". Collapsing
  // them would make a missing table look like three jobs that never reported,
  // and the drift alarm would fire on a pending schema step.
  assert.equal(core.buildReceipt({ ...FULL, deploy: null }).deploy, null);
  assert.deepEqual(core.buildReceipt({ ...FULL, deploy: [] }).deploy, []);
});

test("timestamps normalise from a Date, a string, or nothing at all", () => {
  assert.equal(core.iso(new Date("2026-09-28T09:03:00Z")), "2026-09-28T09:03:00.000Z");
  assert.equal(core.iso("2026-09-28T09:03:00+00:00"), "2026-09-28T09:03:00.000Z");
  assert.equal(core.iso(null), null);
  assert.equal(core.iso(undefined), null);
  assert.equal(core.iso("not a date"), null);
});

test("text fields are bounded, so a corrupt row cannot make a large response", () => {
  const r = core.buildReceipt({
    ...FULL,
    digest: { ...FULL.digest, model: "m".repeat(5000) },
  });
  assert.equal(r.press.model.length, 120);
});

test("a non-numeric file_count becomes null rather than a NaN that JSON cannot carry", () => {
  const r = core.buildReceipt({
    ...FULL,
    deploy: [{ ...FULL.deploy[0], file_count: "four" }],
  });
  assert.equal(r.deploy[0].file_count, null);
  assert.ok(JSON.stringify(r).includes('"file_count":null'));
});
