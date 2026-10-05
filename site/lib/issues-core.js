// Which weeks the public archive publishes, and where each one's text comes
// from. Pure and import-free, so tests/issues.test.mjs runs this exact source
// with no build step and no database.
//
// Two places hold an issue and they are not the same place. `digests` is the
// record: the press writes a row there at the moment it mails the issue to
// subscribers, so a row means a reader already has that text in an inbox.
// `site/content/issues/<week>.md` is the committed copy, which exists because
// until now the archive had no other way to learn that an issue existed, and
// which the owner edits (2026-09-19's corrections to 2026-W37, 2026-09-24's
// reprint of 2026-W39 under canon law 14).
//
// So the rule is: the record decides which weeks exist, the committed file
// decides the text of any week that has one.
//
// Both halves of that matter. The record half is why a Monday send is public
// on Monday rather than whenever somebody remembers to commit it. The file
// half is why every correction the owner has already made to a published
// issue still stands, and why turning this on cannot change a single
// character of what is live today.

export const ISSUE_WEEK = /^\d{4}-W\d{2}$/;

// A row is publishable if it is addressable, not retired, and has text. The
// three are checked separately because they fail for different reasons: a
// malformed week is a bug upstream, a hidden week is the owner's decision
// (HIDDEN_WEEKS in site/lib/content.js), and an empty body is a press run that
// stored nothing, which is the shape incident 24's empty `length` finish
// produced and which must not render as a blank issue.
export function publishable(row, hidden) {
  return (
    !!row &&
    ISSUE_WEEK.test(row.week ?? "") &&
    !hidden.has(row.week) &&
    typeof row.body === "string" &&
    row.body.trim() !== ""
  );
}

// The archive listing, newest first.
//
// `rows` is null when the database could not be read, and null is not the same
// as an empty archive: a Neon outage must never be able to unpublish an issue
// that is live. Null and [] both fall through to the committed files, which is
// exactly today's behaviour, so the worst case of this whole change is the
// behaviour it replaces.
//
// Nothing here returns a body. The listing renders a title and an excerpt, and
// the query behind `rows` reads only the head of each body to keep the read
// small, so a full body is not available here and a page must not be able to
// ask for one by accident.
export function mergeIssues({ files = [], rows = null, hidden, parse }) {
  const byWeek = new Map();

  for (const row of rows ?? []) {
    if (!publishable(row, hidden)) continue;
    byWeek.set(row.week, { ...parse(row.week, row.body), source: "record" });
  }
  for (const issue of files) {
    if (hidden.has(issue.week)) continue;
    byWeek.set(issue.week, { ...issue, source: "file" });
  }

  return [...byWeek.values()]
    .map(({ week, title, dates, excerpt, source }) => ({
      week,
      title,
      dates,
      excerpt,
      source,
    }))
    .sort((a, b) => (a.week < b.week ? 1 : -1));
}

// One week's issue, or null for the route to turn into a 404.
//
// `file` wins over `row` for the reason the header gives. The week is matched
// against ISSUE_WEEK before anything else because it arrives from the URL: it
// never reaches a query (the reader parameterises), and it never reaches the
// filesystem as a path component without passing this test first.
export function pickIssue({ week, file = null, row = null, hidden, parse }) {
  if (!ISSUE_WEEK.test(week ?? "") || hidden.has(week)) return null;
  if (file) return { ...file, source: "file" };
  if (publishable(row, hidden)) return { ...parse(week, row.body), source: "record" };
  return null;
}

// ---------------------------------------------------------------------------
// The two reads, and the one rule they share: they return null when they could
// not look.
//
// The queries live here, in the import-free half, so that tests/issues.test.mjs
// can execute them against a fake tagged template and assert what they ask for
// and what they do with a refusal. A query inside the Neon-specific module
// could only be read as a string, and the properties worth holding here are
// behavioural: that the week from the URL is interpolated rather than
// concatenated, and that a throw resolves to null rather than to an empty
// archive.
//
// `sql` is a tagged template function, which is the whole interface
// `@neondatabase/serverless`'s `neon()` presents. Null means there is no
// connection string, and it is handled the same way a failure is.

// One year of issues on the listing. The archive is the product's shop window
// and a year of it is more than any visitor reads, so this is a ceiling on the
// read rather than an editorial decision. A 53rd week will need a pager on the
// page before it needs a larger number here.
export const LISTING_WEEKS = 52;

// The listing renders an H1, the masthead line it skips, and one paragraph.
// 4,000 characters covers that with a wide margin on every issue printed so
// far (the shortest is 7.4 KB) and keeps the listing's read at a fifth of a
// megabyte at the full 52 rows rather than at whatever the archive grows to.
// `mergeIssues` drops `body` from the listing shape, so no page can render
// this truncated text as if it were an issue.
export const LISTING_HEAD = 4000;

export async function readListing(sql) {
  if (!sql) return null;
  try {
    return await sql`
      select week, left(body, ${LISTING_HEAD}) as body
      from digests
      order by week desc
      limit ${LISTING_WEEKS}
    `;
  } catch {
    return null;
  }
}

export async function readWeek(sql, week) {
  if (!sql) return null;
  // Tested before the query runs, and not only inside it. The value arrives
  // from the URL; the driver parameterises it anyway, and this is the belt the
  // route wears over that brace, because a week that cannot be addressed can
  // never be published and there is no reason to ask the database about one.
  if (!ISSUE_WEEK.test(week ?? "")) return null;
  try {
    const rows = await sql`select week, body from digests where week = ${week}`;
    return rows[0] ?? null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// L-E9 in docs/standards/lessons.md: before a host connection is called done,
// ask what the host actually meters, because "an agent company produces that
// unit at a rate no human team does". This change moves `/library/<week>` from
// prerendered HTML to a per-request render, which is the one rendering-mode
// change it makes (`/library` and sixteen of the site's eighteen routes were
// already server-rendered on demand, measured on both branches with `next
// build`). So the listing's database read is bounded here.
//
// Why the listing and not the week route. The listing is the page every seat's
// delivery check fetches, twelve times a day before any visitor, and it is one
// read of up to 52 rows. The week route is a single lookup on a unique index,
// keyed by a value from the URL, and a keyed cache for it would be a map this
// file would then have to bound. One is worth collapsing and the other is not.
//
// A failed read is deliberately not remembered. `null` means "could not look",
// and caching that would turn one unreachable moment into a minute of them,
// which is the opposite of failing closed.
export function memo(load, { ttlMs = 60_000, now = () => Date.now() } = {}) {
  let at = null;
  let value = null;
  return async (...args) => {
    const t = now();
    if (at !== null && t - at < ttlMs) return value;
    const fresh = await load(...args);
    if (fresh !== null) {
      value = fresh;
      at = t;
    }
    return fresh;
  };
}
