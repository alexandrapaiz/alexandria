import { neon } from "@neondatabase/serverless";
import { pathRow, STEPS, funnel } from "./path-core";

// The buyer-path measurement's I/O. Board card c688ef2e.
//
// Nothing here decides anything. Every judgement is in path-core.js, which
// has no imports and is executed by tests/path.test.mjs. This half is the
// part that cannot be tested without a Postgres, so it is kept as thin as it
// can be made, which is the split site/lib/polar.js already uses.
//
// Secret names only, and there is one that is new and one that already
// exists:
//   DATABASE_URL   already set, and the site already reads it
//                  (lib/waitlist.js, lib/graph-live.js, lib/entitlement.js)
//
// There is no new secret, no new service and no new account, which is the
// whole reason the measurement is first-party: the database this product
// already pays nothing for is the only store it needs.
//
// ## Two rules this file keeps, and they pull in opposite directions
//
// **A measurement must never cost a reader a page.** `record` returns a
// promise that cannot reject and never throws, and the caller runs it after
// the response has gone out. A missing table, a cold database, a closed
// connection: every one of those loses a count and none of them loses a page
// view for the person who was reading.
//
// **A measurement that silently loses rows is worse than no measurement.**
// So the loss is not swallowed into nothing. `record` resolves to a reason,
// `lastRecordError` holds the newest one, and `/api/funnel` publishes it, so
// a count of zero can be told apart from a count that never arrived. Those
// two are the same value and very different facts, which is the distinction
// `tools/delivery_health.py` was written to stop this org from losing.

function db() {
  const url = process.env.DATABASE_URL;
  return url ? neon(url) : null;
}

// 42P01 is undefined_table. Matched on the code rather than the message,
// because the message is localised and the code is not, which is the reason
// site/lib/waitlist.js gives for matching 42703 the same way.
//
// This one is not hypothetical and it is not an error in the ordinary sense.
// `path_events` arrives in db/schema.sql in the same change as this file, and
// applying that file is a step the owner runs through Modal
// (`modal run pipeline/db_setup.py::apply_schema`). For the window between
// the merge and that step the table does not exist, so this is the expected
// state of a correct deploy and it is reported as a reason rather than as a
// fault.
const UNDEFINED_TABLE = "42P01";

export const NO_TABLE_REASON =
  "path_events does not exist yet; apply db/schema.sql with modal run pipeline/db_setup.py::apply_schema";

let lastError = null;

export function lastRecordError() {
  return lastError;
}

function reasonFor(error) {
  if (error?.code === UNDEFINED_TABLE) return NO_TABLE_REASON;
  if (error?.message) return String(error.message).slice(0, 200);
  return "the insert failed";
}

// One row, one insert, no read. There is deliberately no de-duplication and
// no upsert: a second view of the same page by the same person is a second
// event, and this table holds no identifier that could tell those two apart
// anyway.
export async function record(request) {
  const row = pathRow(request);
  if (!row) return { ok: false, reason: "not a counted request" };

  const sql = db();
  if (!sql) {
    lastError = "DATABASE_URL is not set";
    return { ok: false, reason: lastError };
  }

  try {
    await sql`
      insert into path_events (step, path, detail)
      values (${row.step}, ${row.path}, ${row.detail})
    `;
    lastError = null;
    return { ok: true, step: row.step };
  } catch (error) {
    lastError = reasonFor(error);
    return { ok: false, reason: lastError };
  }
}

// ------------------------------------------------------------- the reads
//
// Every read is bounded by a window, because the funnel's question is always
// about a period and an unbounded count over a growing table answers a
// question nobody asked. The window arrives as a number of days and is
// clamped, so a caller cannot turn a public endpoint into a full scan.
const DEFAULT_DAYS = 7;
const MAX_DAYS = 90;

export function clampDays(raw) {
  const n = Number(raw);
  if (!Number.isFinite(n)) return DEFAULT_DAYS;
  return Math.min(MAX_DAYS, Math.max(1, Math.round(n)));
}

// Counts per step, as a plain object keyed by the five words in
// path-core.js. A step with no rows in the window is absent from the result
// rather than zero, and `funnel()` fills it with zero, because the absence of
// a row genuinely is a count of zero here: the table was readable and held
// nothing. That is the one place in this file where zero is the honest answer.
export async function stepCounts(days = DEFAULT_DAYS) {
  const sql = db();
  if (!sql) return { counts: null, reason: "DATABASE_URL is not set" };

  try {
    const rows = await sql`
      select step, count(*)::int as events
      from path_events
      where occurred_at > now() - make_interval(days => ${clampDays(days)})
      group by step
    `;
    const counts = {};
    for (const row of rows) {
      if (STEPS.includes(row.step)) counts[row.step] = row.events;
    }
    return { counts, reason: null };
  } catch (error) {
    return { counts: null, reason: reasonFor(error) };
  }
}

// The card's own question: which skill actually sells. Ordered by the count
// and capped, because a catalogue of nine skills has a short answer and a
// catalogue of nine hundred would still have a short answer worth reading.
const SKILL_LIMIT = 50;

export async function skillCounts(days = DEFAULT_DAYS) {
  const sql = db();
  if (!sql) return { skills: null, reason: "DATABASE_URL is not set" };

  try {
    const rows = await sql`
      select detail as skill, count(*)::int as events
      from path_events
      where step = 'skill'
        and detail is not null
        and occurred_at > now() - make_interval(days => ${clampDays(days)})
      group by detail
      order by count(*) desc, detail asc
      limit ${SKILL_LIMIT}
    `;
    return { skills: rows.map((r) => ({ skill: r.skill, events: r.events })), reason: null };
  } catch (error) {
    return { skills: null, reason: reasonFor(error) };
  }
}

// The payment, which is a state rather than an event, so it is read from the
// billing record `site/lib/polar.js` writes and not counted here. Anything
// other than 'free' is an account that has paid or has been paying, which is
// the number the funnel's last row wants.
//
// `users` predates this change and is created by the same db/schema.sql, so a
// missing table here means the schema has never been applied at all rather
// than that today's migration is pending. The reason says so either way,
// which is enough for the reader to act on.
export async function paidAccounts() {
  const sql = db();
  if (!sql) return { accounts: null, reason: "DATABASE_URL is not set" };

  try {
    const rows = await sql`
      select count(*)::int as accounts
      from users
      where subscription_status <> 'free'
    `;
    return { accounts: rows[0]?.accounts ?? 0, reason: null };
  } catch (error) {
    return { accounts: null, reason: reasonFor(error) };
  }
}

// Everything /api/funnel publishes, assembled once. The install step arrives
// as null from here and always will: GitHub's clone traffic is not readable
// from this app's environment and is not readable from any token this org
// holds today, so the site states the gap and tools/buyer_path.py is the one
// reader that attempts it.
export async function readFunnel(days = DEFAULT_DAYS) {
  const window = clampDays(days);
  const [steps, skills, paid] = await Promise.all([
    stepCounts(window),
    skillCounts(window),
    paidAccounts(),
  ]);

  return {
    days: window,
    funnel: funnel({
      counts: steps.counts ?? {},
      paid: { accounts: paid.accounts, reason: paid.reason },
      install: { clones: null, reason: "the site cannot read GitHub's clone traffic" },
    }),
    // A null count and a zero count are different facts, so the reason a read
    // failed travels with the numbers rather than being inferred from them.
    counts_read: steps.counts !== null,
    counts_reason: steps.reason,
    skills: skills.skills,
    skills_reason: skills.reason,
    last_record_error: lastRecordError(),
  };
}
