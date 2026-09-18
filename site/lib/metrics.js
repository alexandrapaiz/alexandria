// The home page's hero metric. It reports the pipeline's own count of papers
// ingested in the last seven days, and it must never be a decorative number:
// the repo is public and this audience reads source, so a static figure
// styled as telemetry costs exactly the trust it is meant to buy
// (docs/market/report-2026-09.md §6).
//
// The definition is the same one the weekly digest uses, so the site and the
// digest can never disagree about the week's count:
export const WEEKLY_INGEST_SQL =
  "select count(*) as n from papers where fetched_at > now() - interval '7 days'";
//   (pipeline/weekly.py, gather(): "select count(*) from papers
//    where fetched_at > now() - interval '7 days'")
//
// Wiring, one seam: the site has no database client yet (adding one is the
// engineer's call this sprint, and a new dependency needs a ledger proposal
// first), so the count arrives over HTTP from INGEST_COUNT_URL, a JSON
// endpoint answering { "papers_ingested": <n> }. When the Neon client lands,
// replace the fetch below with the query above and nothing else changes.
//
// If the count cannot be read, this returns null and the home page renders no
// metric at all. That is deliberate: no number is honest, a stale number is
// not.

export async function weeklyIngestCount() {
  const url = process.env.INGEST_COUNT_URL;
  if (!url) return null;
  try {
    // the desk page's pattern: fetch with a revalidate window, never a
    // request-time query, so a slow or down source cannot slow the page
    const res = await fetch(url, { next: { revalidate: 3600 } });
    if (!res.ok) return null;
    const data = await res.json();
    const n = Number(data?.papers_ingested ?? data?.n ?? data?.count);
    return Number.isFinite(n) && n >= 0 ? Math.round(n) : null;
  } catch {
    return null;
  }
}
