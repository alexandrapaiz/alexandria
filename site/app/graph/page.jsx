import Link from "next/link";
import GraphFull from "../components/GraphFull";

export const metadata = { title: "Graph — library of alexandr.ia" };

export default function Graph() {
  return (
    <main className="page graph-page">
      <p className="page-kicker">Graph</p>
      <h1 className="page-title">A graph that never forgets.</h1>
      <p className="page-intro">
        Every claim the library has distilled, and every relation drawn between
        them: which findings support each other, which refine each other, and
        which are in contradiction. The graph is appended daily and never
        rewritten, so it remembers what the field believed and when it changed
        its mind.
      </p>
      <div className="graph-stage">
        <GraphFull />
        <div className="graph-gate">
          <h3>The full graph is for members.</h3>
          <p>
            Each node is a claim with its evidence, procedure, and paper.
            Members open any node and follow the argument.
          </p>
          <Link href="/pricing" className="pill">
            Subscribe
          </Link>
        </div>
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
