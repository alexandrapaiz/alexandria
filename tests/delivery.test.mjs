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
  // Newer than `claims` on purpose. That ordering is the whole point of the
  // field: distill marked a paper read after it last wrote a claim, which is
  // the shape that says the stage ran and extracted nothing.
  distilled: new Date("2026-10-01T15:04:00Z"),
  // The two sibling Kimi stages' newest rows. Triage's is fresher than the
  // distill marker on purpose, because that ordering is the one version 4 was
  // added to detect: the shared account answered a caller after distill last
  // did any work, which rules the provider out and leaves distill's own cron
  // and caps. `claim_links.method` carries `model@prompt_sha` as it does in
  // the table, so the fixture exercises the half that has to be dropped.
  siblings: {
    triage: { newest: new Date("2026-10-02T12:06:00Z"), model: "kimi-k2.6" },
    interpret: { newest: new Date("2026-10-01T14:03:00Z"), model: "kimi-k2.6@deadbeef" },
  },
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
  // The till's open exceptions, version 5. Two rows, one of each kind, so the
  // fixture exercises the split the verdict turns on: a `no_account` refusal
  // that will never clear itself and a `no_users_row` deferral that Polar will
  // bring back. The counts are bigint strings for the same reason the queue
  // depths are.
  payments: {
    unresolved: "2",
    needs_a_hand: "1",
    oldest: new Date("2026-09-30T18:00:00Z"),
    newest: new Date("2026-10-01T01:30:00Z"),
    codes: [
      { code: "no_account", n: "1" },
      { code: "no_users_row", n: "1" },
    ],
  },
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
    distilled_newest: "2026-10-01T15:04:00.000Z",
  });
  assert.deepEqual(r.siblings, {
    triage: { newest: "2026-10-02T12:06:00.000Z", model: "kimi-k2.6" },
    interpret: { newest: "2026-10-01T14:03:00.000Z", model: "kimi-k2.6" },
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

test("a column of nulls publishes null, not a stage that never ran", () => {
  // `max(distilled_at)` over a table where no paper carries the marker comes
  // back as null, and so does the field on a receipt published before version
  // 3. Both have to arrive at the reader as the same thing, because the reader
  // has one sentence for "cannot say" and it must not be able to reach the
  // sentence that names the cron.
  const r = core.buildReceipt({ ...FULL, distilled: null });
  assert.equal(r.pipeline.distilled_newest, null);
  assert.equal(r.pipeline.claims_newest, "2026-09-30T14:02:00.000Z");
  const absent = core.buildReceipt({ ...FULL, distilled: undefined });
  assert.equal(absent.pipeline.distilled_newest, null);
  assert.ok("distilled_newest" in absent.pipeline);
});

test("a sibling stage with no row publishes null, and an unreadable block is null", () => {
  // Three states and they are genuinely different. An empty `claim_links` is a
  // stage with no row, which is a fact. A `siblings` of null is the site
  // failing to run the query. And a receipt published before version 4 has no
  // block at all. The last two have to reach the reader as the same thing,
  // because it has one sentence for "cannot say" and it must not be able to
  // reach the sentence that names the Moonshot account on no evidence.
  const empty = core.buildReceipt({
    ...FULL,
    siblings: { triage: FULL.siblings.triage, interpret: null },
  });
  assert.equal(empty.siblings.interpret, null);
  assert.deepEqual(empty.siblings.triage, {
    newest: "2026-10-02T12:06:00.000Z",
    model: "kimi-k2.6",
  });
  assert.equal(core.buildReceipt({ ...FULL, siblings: null }).siblings, null);
  assert.equal(core.buildReceipt({ ...FULL, siblings: undefined }).siblings, null);
  // And the marker these two are the control for is untouched by their absence.
  assert.equal(empty.pipeline.distilled_newest, "2026-10-01T15:04:00.000Z");
});

test("a sibling row carrying an unexpected column does not widen the receipt", () => {
  // Every field built by name, the same defence the press block has.
  // `triage_log.reasoning` is a model's prose about a paper, so a row that
  // arrived with it must not be able to publish it.
  const r = core.buildReceipt({
    ...FULL,
    siblings: {
      triage: { ...FULL.siblings.triage, reasoning: "do not publish me" },
      interpret: FULL.siblings.interpret,
    },
  });
  assert.ok(!JSON.stringify(r).includes("do not publish me"));
  assert.equal(Object.keys(r.siblings.triage).sort().join(","), "model,newest");
});

test("the prompt sha in claim_links.method is dropped, as digests.prompt_sha is", () => {
  const r = core.buildReceipt(FULL);
  assert.equal(r.siblings.interpret.model, "kimi-k2.6");
  assert.ok(!JSON.stringify(r).includes("deadbeef"));
});

test("the pipeline block has exactly the three markers and nothing else", () => {
  assert.equal(
    Object.keys(core.buildReceipt(FULL).pipeline).sort().join(","),
    "claims_newest,distilled_newest,papers_newest"
  );
});

test("the top level has exactly eight keys", () => {
  assert.deepEqual(Object.keys(core.buildReceipt(FULL)).sort(), [
    "deploy",
    "observed_at",
    "payments",
    "press",
    "pipeline",
    "queues",
    "receipt",
    "siblings",
    "version",
  ].sort());
});

// ------------------------------------------------- the till (version 5)
//
// This block is the first one on the receipt whose rows are about a person.
// `payment_exceptions` holds the buyer's address and the Polar ids, the
// endpoint is public and unauthenticated, and the tests below are the second
// of the two defences the header names: lib/delivery.js does not select those
// columns, and this builds every field by name so a row carrying them anyway
// cannot widen the response.

test("the till publishes counts, codes and two timestamps, and nothing else", () => {
  const r = core.buildReceipt(FULL);
  assert.deepEqual(Object.keys(r.payments).sort(), [
    "codes",
    "needs_a_hand",
    "newest_unresolved_at",
    "oldest_unresolved_at",
    "unresolved",
  ].sort());
  assert.equal(r.payments.unresolved, 2);
  assert.equal(r.payments.needs_a_hand, 1);
  assert.equal(r.payments.oldest_unresolved_at, "2026-09-30T18:00:00.000Z");
  assert.equal(r.payments.newest_unresolved_at, "2026-10-01T01:30:00.000Z");
});

test("a payer cannot escape, even when the rows carry one", () => {
  const r = core.buildReceipt({
    ...FULL,
    payments: {
      ...FULL.payments,
      email: "buyer@example.com",
      polar_customer_id: "cus_leak",
      detail: "no Clerk account for this buyer (no match)",
      codes: [
        {
          code: "no_account",
          n: "1",
          email: "buyer@example.com",
          detail: "no Clerk account for this buyer (no match)",
        },
      ],
    },
  });
  const json = JSON.stringify(r);
  assert.ok(!json.includes("buyer@example.com"));
  assert.ok(!json.includes("cus_leak"));
  assert.ok(!json.includes("no Clerk account"));
  assert.deepEqual(r.payments.codes, [{ code: "no_account", n: 1 }]);
});

test("a till with nothing open and an unreadable one are different answers", () => {
  const clear = core.buildReceipt({
    ...FULL,
    payments: { unresolved: "0", needs_a_hand: "0", oldest: null,
                newest: null, codes: [] },
  });
  assert.equal(clear.payments.unresolved, 0);
  assert.equal(clear.payments.needs_a_hand, 0);
  assert.equal(clear.payments.oldest_unresolved_at, null);
  assert.deepEqual(clear.payments.codes, []);
  // Null and not a zero, because zero is the good news and it is only good
  // news when somebody looked.
  assert.equal(core.buildReceipt({ ...FULL, payments: null }).payments, null);
  assert.equal(core.buildReceipt({ ...FULL, payments: undefined }).payments, null);
});

test("a codes list that is not a list is an empty one, never a crash", () => {
  for (const codes of [undefined, null, "no_account", 7, {}]) {
    const r = core.buildReceipt({ ...FULL, payments: { ...FULL.payments, codes } });
    assert.deepEqual(r.payments.codes, [], String(codes));
  }
});

test("a code row with no code is dropped rather than published as null", () => {
  const r = core.buildReceipt({
    ...FULL,
    payments: { ...FULL.payments, codes: [{ n: "3" }, { code: "no_account", n: "1" }] },
  });
  assert.deepEqual(r.payments.codes, [{ code: "no_account", n: 1 }]);
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

// ------------------------------------------------- version 6: the reason why

test("a receipt whose every query ran carries no unreadable block at all", () => {
  const r = core.buildReceipt(FULL);
  assert.equal("unreadable" in r, false);
  // And the same for an explicit empty one, because the reader of this block
  // is a guard that treats the field's presence as the finding.
  assert.equal("unreadable" in core.buildReceipt({ ...FULL, unreadable: {} }), false);
});

test("a null block says which of the three things happened to it", () => {
  const r = core.buildReceipt({
    ...FULL,
    payments: null,
    deploy: null,
    unreadable: { payments: "no such table", deploy: "query failed" },
  });
  assert.equal(r.payments, null);
  assert.equal(r.deploy, null);
  assert.deepEqual(r.unreadable, { payments: "no such table", deploy: "query failed" });
});

test("a reason outside the vocabulary cannot reach the response", () => {
  // The one block on this receipt built from a value a caught exception
  // produced, so this is the one place a driver's own text could escape. A
  // Neon error names the host and the role it failed to authenticate.
  const r = core.buildReceipt({
    ...FULL,
    payments: null,
    unreadable: {
      payments: 'password authentication failed for user "alexandria" at ep-xyz',
    },
  });
  assert.deepEqual(r.unreadable, { payments: "query failed" });
  for (const value of Object.values(r.unreadable)) {
    assert.ok(core.UNREADABLE_REASONS.includes(value));
  }
});

test("a key for a block this receipt does not publish is dropped", () => {
  const r = core.buildReceipt({
    ...FULL,
    unreadable: { press: "no such table", pipeline: "query failed", "../etc": "x" },
  });
  assert.equal("unreadable" in r, false);
});

test("the vocabulary is frozen, so no caller can widen it at runtime", () => {
  assert.ok(Object.isFrozen(core.UNREADABLE_REASONS));
  assert.deepEqual([...core.UNREADABLE_REASONS].sort(),
                   ["no such column", "no such table", "query failed"]);
});
