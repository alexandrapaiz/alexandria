import { neon } from "@neondatabase/serverless";
import { signupRow, signupOutcome } from "./waitlist-core";

// Where an email goes when somebody asks for the digest: into `subscribers`,
// which is the list pipeline/weekly.py reads on Monday morning. One insert,
// no file, and nobody has to promote anybody.
//
// What this replaced, and why the replacement is the whole change. Until today
// this module appended to `.data/waitlist.jsonl` on local disk, with the real
// insert left as "the seam the engineer wires later". On a serverless host that
// file does not survive a redeploy, so the holding pen was a list that could
// lose the list. Sprint 2026-10-05 item 2 is this seam and clause 1 of its
// definition of done is a stranger becoming a real row with no owner action in
// between. site/lib/waitlist-core.js carries the reasoning about the row.
//
// The legacy file is not drained here. Any rows it holds are on whichever
// serverless instance wrote them, unreachable from a later deploy by
// construction, so a drain path would be code that cannot run against the data
// it exists for. Said plainly rather than left as a silent loss.

function db() {
  const url = process.env.DATABASE_URL;
  return url ? neon(url) : null;
}

// `xmax = 0` is Postgres's own answer to "was this row inserted or updated" on
// an upsert, and it is read here rather than guessed, because a second query
// to find out would race with a concurrent signup for the same address.
//
// The conflict updates rather than doing nothing, so that somebody who
// unsubscribed and has now signed up again comes back. `tier` and `comp` are
// deliberately left alone on that path: if the owner has comped or upgraded
// somebody by hand, a signup form must not undo it.
const INSERT_WITH_SOURCE = (sql, row) => sql`
  insert into subscribers (email, tier, status, comp, source)
  values (${row.email}, ${row.tier}, ${row.status}, ${row.comp}, ${row.source})
  on conflict (email) do update
    set status = 'active',
        unsubscribed_at = null
  returning id, (xmax = 0) as inserted
`;

// The same insert for a database that has not had today's migration applied
// yet. `source` arrives in the same change as the column, and the deploy that
// applies db/schema.sql is a separate step the owner runs
// (pipeline/db_setup.py), so for the window between the merge and that step
// the column does not exist. Dropping attribution for that window beats
// refusing the signup, which is the only other option and loses the person.
const INSERT_WITHOUT_SOURCE = (sql, row) => sql`
  insert into subscribers (email, tier, status, comp)
  values (${row.email}, ${row.tier}, ${row.status}, ${row.comp})
  on conflict (email) do update
    set status = 'active',
        unsubscribed_at = null
  returning id, (xmax = 0) as inserted
`;

// 42703 is undefined_column. Matching on the code rather than the message,
// because the message is localised and the code is not.
const UNDEFINED_COLUMN = "42703";

function isMissingColumn(error) {
  return error?.code === UNDEFINED_COLUMN;
}

export async function subscribe(rawEmail, rawSource) {
  const row = signupRow(rawEmail, rawSource);
  if (!row) return { ok: false, retryable: false, reason: "not an email address" };

  const sql = db();
  if (!sql) return { ok: false, retryable: true, reason: "DATABASE_URL is not set" };

  // Read the status first so the answer can tell a returning subscriber from
  // one who never left. The upsert overwrites it, so after the write there is
  // nothing left to read.
  let wasUnsubscribed = false;
  try {
    const before = await sql`
      select status from subscribers where email = ${row.email} limit 1
    `;
    wasUnsubscribed = before[0]?.status === "unsubscribed";
  } catch {
    // A subscriber who looks new when they are returning is a wrong count,
    // not a wrong row. The insert below is what has to succeed.
  }

  let rows;
  try {
    rows = await INSERT_WITH_SOURCE(sql, row);
  } catch (error) {
    if (!isMissingColumn(error)) {
      return { ok: false, retryable: true, reason: "the insert failed" };
    }
    try {
      rows = await INSERT_WITHOUT_SOURCE(sql, row);
    } catch {
      return { ok: false, retryable: true, reason: "the insert failed" };
    }
  }

  const result = { inserted: Boolean(rows[0]?.inserted), wasUnsubscribed };
  return {
    ok: true,
    id: rows[0]?.id ?? null,
    email: row.email,
    outcome: signupOutcome(result),
  };
}
