import Link from "next/link";
import MarkLive from "./components/MarkLive";

export default function Home() {
  return (
    <main>
      <section className="hero">
        <h1 className="wordmark">
          library of
          <br />
          alexandr.ia
        </h1>
        <div className="hero-mark">
          <MarkLive />
        </div>
      </section>

      <section className="hero-follow">
        <p className="hero-sub">
          The latest in AI research, read in full and distilled weekly:
          what&rsquo;s new, what&rsquo;s gaining acceptance, and what newer
          evidence has overturned.
        </p>
        <div className="hero-cta">
          <Link href="/pricing" className="pill">
            Subscribe
          </Link>
          <Link href="/library" className="pill ghost">
            Read an issue
          </Link>
        </div>
        <div className="stats">
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
        </div>
      </section>

      <section className="tri">
        <div>
          <h3>Read in full</h3>
          <p>
            Abstracts compress away the details that make research usable, so
            the library reads each selected paper whole and keeps every finding
            together with its evidence and the exact procedure that produced it.
          </p>
        </div>
        <div>
          <h3>Tracked over time</h3>
          <p>
            Research keeps moving after publication, and a result that stood in
            March can be overturned by June. Every claim therefore enters a
            graph where newer evidence attaches to older conclusions, so that
            growing support, refinements, and contradictions all become part of
            a claim&rsquo;s record.
          </p>
        </div>
        <div>
          <h3>Turned into skills</h3>
          <p>
            Procedures that hold up under accumulating evidence are packaged
            as skills that any AI agent can load, each traceable to the claims
            and papers that justify it. Because that provenance stays live, a
            skill is revised whenever its research sharpens and retired with
            an explanation if the research is overturned.
          </p>
        </div>
      </section>
    </main>
  );
}
