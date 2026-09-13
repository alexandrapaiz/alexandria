import Link from "next/link";
import GraphEmbed from "./components/GraphEmbed";

export default function Home() {
  return (
    <main>
      <section className="hero">
        <h1 className="wordmark">
          library{" "}
          <span className="embed">
            <GraphEmbed />
          </span>{" "}
          of
          <br />
          alexandr.ia
        </h1>
        <p className="hero-sub">
          The latest in AI research, read in full and distilled weekly: what&rsquo;s
          new, what&rsquo;s gaining ground, and what&rsquo;s been left behind.
        </p>
        <div className="hero-cta">
          <Link href="/pricing" className="pill">
            Subscribe
          </Link>
          <Link href="/library" className="pill ghost">
            Read an issue
          </Link>
        </div>
      </section>

      <section className="stats">
        <div className="stat">
          <b>3,431</b>
          <span>papers ingested this week</span>
        </div>
        <div className="stat">
          <b>216</b>
          <span>claims distilled</span>
        </div>
        <div className="stat">
          <b>80</b>
          <span>edges drawn in the graph</span>
        </div>
      </section>

      <section className="tri">
        <div>
          <h3>Read in full</h3>
          <p>
            Every notable paper is read whole, not skimmed by abstract. Findings
            are distilled into claims with their evidence and procedures attached.
          </p>
        </div>
        <div>
          <h3>Tracked over time</h3>
          <p>
            Claims live in a graph that never forgets. When new evidence supports,
            refines, or overturns a result, the graph records it, and the digest
            tells you.
          </p>
        </div>
        <div>
          <h3>Turned into skills</h3>
          <p>
            Validated procedures become Claude skills with full provenance. When
            the research moves, your skills update. When it is overturned, they
            retire.
          </p>
        </div>
      </section>
    </main>
  );
}
