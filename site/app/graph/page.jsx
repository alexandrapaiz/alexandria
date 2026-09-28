import Link from "next/link";
import GraphExplorer from "./GraphExplorer";
import { hasSpine } from "../../lib/entitlement";
import { loadGraph } from "../../lib/graph-live";

// The claim graph, live. Owner's ruling of 2026-09-19 put this route back as a
// PAID page, and her dispatch of 2026-09-25 ordered it built from the database
// rather than from the structural fixture the parked `_graph/` folder drew.
// That folder and lib/graph-data.js are gone with this commit.
//
// The gate is the whole page, not an overlay on a rendered graph. An unpaid
// visitor gets the heading and the offer and no claim data of any kind: the
// query below only runs once hasSpine() has returned true, so nothing about
// the graph is serialised into a response they receive. Her words on the
// ruling were "no preview, no teaser rendering".
export const dynamic = "force-dynamic";
export const metadata = { title: "Claim graph — library of alexandr.ia" };

export default async function Graph() {
  const entitled = await hasSpine();
  const graph = entitled ? await loadGraph() : null;

  return (
    <main className="page graph-page">
      <p className="page-kicker">Graph</p>
      <h1 className="page-title">Claim graph</h1>
      <p className="page-intro">
        Each claim the library distilled, and the claims that support,
        refine, or contradict it.
      </p>

      {!entitled ? (
        <div className="graph-gate">
          <h2>Open any node with the paid plan.</h2>
          <p>
            Each node is one claim, with its evidence, its procedure, and the
            paper it came from. The paid plan opens them.
          </p>
          <Link href="/pricing" className="pill">
            See pricing
          </Link>
        </div>
      ) : graph === null ? (
        <p className="graph-unavailable">
          The graph is unavailable right now. Try again in a minute.
        </p>
      ) : (
        <>
          <dl className="graph-counts">
            <div>
              <dt>Claims</dt>
              <dd>{graph.counts.claims.toLocaleString()}</dd>
            </div>
            <div>
              <dt>Linked</dt>
              <dd>{graph.counts.linked.toLocaleString()}</dd>
            </div>
            <div>
              <dt>Edges</dt>
              <dd>{graph.counts.edges.toLocaleString()}</dd>
            </div>
            <div>
              <dt>Papers</dt>
              <dd>{graph.counts.papers.toLocaleString()}</dd>
            </div>
          </dl>
          <GraphExplorer
            claims={graph.claims}
            edges={graph.edges}
            topics={graph.topics}
            counts={graph.counts}
          />
        </>
      )}
    </main>
  );
}
