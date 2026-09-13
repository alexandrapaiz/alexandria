import Link from "next/link";
import MarkLive from "./components/MarkLive";

export default function Home() {
  return (
    <main className="home-snap">
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
          The library reads papers in full and keeps what matters: the
          finding, the evidence, and the procedure that produced it. Every
          claim then lives in a graph that records how the field treats it
          over time, so you see what gains acceptance and what falls. The
          procedures that survive become skills any AI agent can load,
          revised as the research sharpens and retired when it is overturned.
        </p>
        <p className="metric-line">
          <b>3,431</b> papers ingested this week
        </p>
      </section>
    </main>
  );
}
