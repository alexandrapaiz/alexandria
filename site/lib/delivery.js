import { neon } from "@neondatabase/serverless";
import { buildReceipt } from "./delivery-core.js";

// Reads the four facts the delivery receipt publishes. Fails closed, the same
// contract as lib/entitlement.js and lib/graph-live.js: no connection string,
// or a query that throws, resolves to null rather than to a receipt full of
// nulls. The route turns that null into a 503, because "the press has printed
// nothing" and "this endpoint could not look" are different facts and the
// whole point of tools/delivery_health.py's third state is not to confuse
// them.
//
// Four queries, all of them an index read or a primary-key scan of a table
// with three rows, and no parameter from the request reaches any of them. The
// route caches on the CDN, so repeat traffic does not reach Neon at all.
// Returns `{ receipt }` on success and `{ reason }` on failure, never a receipt
// full of nulls. The two failures are kept apart on purpose: a missing
// DATABASE_URL in this project's environment is one setting away from working,
// and a query that throws is not, and the seat reading this from a sandbox has
// no other way to tell which it is looking at.
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
    // The message and nothing else. A Neon error carries the host and the role
    // it failed to authenticate, which is not for a public response, and the
    // reader of this field only needs to know a query failed rather than a
    // setting being absent.
    return { reason: `a query failed: ${error?.name ?? "Error"}` };
  }
}
