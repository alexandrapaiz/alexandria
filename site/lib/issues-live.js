import { neon } from "@neondatabase/serverless";

import { HIDDEN_WEEKS, getIssue, listIssues, parseIssue } from "./content.js";
import {
  mergeIssues,
  pickIssue,
  readListing,
  readWeek,
} from "./issues-core.js";

// The archive, read from the record the press actually writes.
//
// `site/lib/content.js` has always claimed in its own header that "in
// production this module swaps to a Neon lookup with the same interface". It
// never did. Every issue the public can read reached the public because a
// person committed a markdown file: four commits under
// `site/content/issues/`, every one of them by hand, while `pipeline/weekly.py`
// wrote its row to `digests` and stopped there. That is the shape this sprint
// exists to close, a fix that is merged and not running, and it is the version
// of it that sits closest to the product: the press can print perfectly and
// the archive still shows last month.
//
// Fails closed, the same contract as lib/entitlement.js, lib/graph-live.js and
// lib/delivery.js. No connection string, or a query that throws, resolves to
// null rather than to an empty archive, and null falls through to the committed
// files. A database this page cannot read therefore publishes exactly what it
// publishes today.

function connect() {
  const url = process.env.DATABASE_URL;
  return url ? neon(url) : null;
}

export async function publishedIssues(sql = connect()) {
  return mergeIssues({
    files: listIssues(),
    rows: await readListing(sql),
    hidden: HIDDEN_WEEKS,
    parse: parseIssue,
  });
}

export async function publishedIssue(week, sql = connect()) {
  return pickIssue({
    week,
    file: getIssue(week),
    row: await readWeek(sql, week),
    hidden: HIDDEN_WEEKS,
    parse: parseIssue,
  });
}
