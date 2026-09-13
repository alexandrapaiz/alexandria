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
          A library <b>live with the latest AI research</b>: what the field
          knows right now, and the <b>best known methods</b>, ready for{" "}
          <b>your agents</b> to load.
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
          The weekly digest tells you where AI actually stands: which new
          techniques work, which ones the field has come to trust, and which
          results no longer hold, in plain language you can read in minutes.
          The library then turns the best of it into ready-to-use skills,
          from agent harness design to training recipes, packaged so your
          own agents can load them and kept current as the research moves.
        </p>
        <p className="metric-line">
          <b>3,431</b> papers ingested this week
        </p>
      </section>
    </main>
  );
}
