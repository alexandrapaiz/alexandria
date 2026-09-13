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
          An autonomous library that <b>researches the research</b>: it reads
          the field in full, keeps a <b>living record</b> of what holds true,
          and <b>rewrites itself</b> as the science moves.
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
          Every week the pipeline ingests thousands of papers, reads the ones
          that matter in full, and distills them into claims connected in a
          graph. Because the graph records how each claim fares as new
          evidence arrives, the weekly digest is not a feed of announcements
          but an updated statement of where the field stands. The same record
          produces skills any AI agent can load, and the library maintains
          all of it on its own, proposing its own improvements as it learns.
        </p>
        <p className="metric-line">
          <b>3,431</b> papers ingested this week
        </p>
      </section>
    </main>
  );
}
