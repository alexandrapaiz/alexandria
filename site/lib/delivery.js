import { neon } from "@neondatabase/serverless";
import { buildReceipt } from "./delivery-core.js";

// Reads the four facts the delivery receipt publishes.
//
// Fails closed, the same contract as lib/entitlement.js and lib/graph-live.js,
// and returns `{ receipt }` or `{ reason }`, never a receipt full of nulls. The
// route turns a reason into a 503, because "the press has printed nothing" and
// "this endpoint could not look" are different facts and the whole point of
// tools/delivery_health.py's third state is not to confuse them.
//
// The two failures are kept apart on purpose. A missing DATABASE_URL in this
// project's environment is one setting away from working and a query that
// throws is not, and a seat reading this from a sandbox cannot see the
// environment, so this field is its only diagnosis.
//
// Four queries, and no parameter from the request reaches any of them. Two are
// cheap by construction: `digests` is ordered on its unique `week` index and
// `deploy_runtime` has one row per scheduled job. The two `max()` reads over
// `papers` and `claims` have no index to use and scan, which is thousands of
// rows rather than millions today and is the same pair of queries
// `tools/delivery_health.py` has always run against this database. The route
// caches at the edge, so repeat traffic does not reach Neon at all. If either
// table grows enough for the scan to matter, the answer is an index on the two
// timestamps rather than a different endpoint.
export async function loadDeliveryReceipt() {
  const url = process.env.DATABASE_URL;
  if (!url) return { reason: "DATABASE_URL is not set in the site's environment" };

  try {
    const sql = neon(url);

    // `order by week desc` and not `created_at`, so this agrees with
    // tools/delivery_health.py's own query. A backfilled week would otherwise
    // make the two disagree about which issue is newest.
    const digests = await sql`
      select week, model, created_at
      from digests
      order by week desc
      limit 1
    `;
    const papers = await sql`select max(fetched_at) as newest from papers`;
    const claims = await sql`select max(created_at) as newest from claims`;

    // deploy_runtime lands with the drift guard and `apply_schema` is a hand
    // step, so a missing table is a state this really meets. It is the one
    // query allowed to fail without failing the receipt: the press and the
    // pipeline are the surfaces the ledger calls urgent, and losing them
    // because a newer table is absent would be the wrong trade.
    let deploy = null;
    try {
      deploy = await sql`
        select app, runtime_sha, entrypoint, file_count,
               recorded_at, first_seen_at, notified_at
        from deploy_runtime
        order by app
      `;
    } catch {
      // null, not []: an empty array would tell the drift guard that every job
      // has failed to report, and it would raise the alarm this endpoint
      // exists to make readable.
      deploy = null;
    }

    return {
      receipt: buildReceipt({
        digest: digests[0] ?? null,
        papers: papers[0]?.newest ?? null,
        claims: claims[0]?.newest ?? null,
        deploy,
        observedAt: new Date(),
      }),
    };
  } catch (error) {
    // The error's class and nothing else. A Neon error's message carries the
    // host and the role it failed to authenticate, which is not for a public
    // response, and the reader of this field only needs to know that a query
    // failed rather than that a setting is absent.
    return { reason: `a query failed: ${error?.name ?? "Error"}` };
  }
}
