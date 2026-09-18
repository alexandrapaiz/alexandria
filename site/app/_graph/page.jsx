import Link from "next/link";
import GraphFull from "./GraphFull";
import { hasSpine } from "../../lib/entitlement";

// PARKED, owner's order of 2026-09-18. The knowledge graph is hidden from
// visitors completely: no nav link, no mention on any page, and no route.
// The leading underscore makes this a Next private folder, so /graph is a
// 404 rather than a page. Nothing here was deleted. Drop the underscore to
// put it back when the graph is industry standard.
export const dynamic = "force-dynamic";
export const metadata = { title: "Graph — library of alexandr.ia" };

export default async function Graph() {
  const entitled = await hasSpine();

  return (
    <main className="page graph-page">
      <p className="page-kicker">Graph</p>
      <h1 className="page-title">A graph that never forgets.</h1>
      <p className="page-intro">
        Every claim the library has distilled, with the links between them.
        You can see which findings support each other, which refine each
        other, and which contradict each other. The graph is only ever
        appended to, so it keeps a record of what the field believed and when
        it changed its mind.
      </p>
      <div className="graph-stage">
        <GraphFull />
        {!entitled && (
          <div className="graph-gate">
            <h3>Open any node with the paid plan.</h3>
            <p>
              Each node is one claim, with its evidence, its procedure, and
              the paper it came from. The paid plan opens them.
            </p>
            <Link href="/pricing" className="pill">
              See pricing
            </Link>
          </div>
        )}
      </div>
      <div className="graph-legend">
        <span>● claim</span>
        <span>○ claim with procedure</span>
        <span>─ supports</span>
        <span>━ refines</span>
        <span>┄ contradicts</span>
      </div>
    </main>
  );
}
