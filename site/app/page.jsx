import Link from "next/link";
import MarkLive from "./components/MarkLive";

export default function Home() {
  return (
    <main className="home-snap">
      <section className="hero">
        <div className="hero-pin">
          <h1 className="wordmark">
            library of
            <br />
            alexandr.ia
          </h1>
          <div className="hero-mark">
            <MarkLive />
          </div>
        </div>
      </section>

      <div className="scene-gap" aria-hidden="true" />

      <section className="hero-follow">
        <p className="statement">
          The latest in AI research, <b>read in full</b> and{" "}
          <b>distilled weekly</b>: what&rsquo;s new, what&rsquo;s gaining
          acceptance, and what newer evidence has overturned.
        </p>
        <div className="hero-cta">
          <Link href="/pricing" className="pill">
            Subscribe
          </Link>
          <Link href="/library" className="pill ghost">
            Read an issue
          </Link>
        </div>
        <p className="about-inline">
          Abstracts hide the details that make research usable, so the library
          reads each selected paper whole and distills it into claims that
          keep the finding together with its evidence and the procedure behind
          it. Because research keeps moving after publication, every claim
          then lives in a graph where newer evidence attaches to older
          conclusions, and growing support, refinements, and contradictions
          all become part of its record. The procedures that hold up are
          packaged as skills that any AI agent can load, and since each one
          stays traceable to the claims that justify it, a skill is revised as
          its research sharpens and retired with an explanation when the
          research is overturned.
        </p>
        <p className="metric-line">
          <b>3,431</b> papers ingested this week
        </p>
      </section>
    </main>
  );
}
