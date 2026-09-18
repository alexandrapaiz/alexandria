import Link from "next/link";
import MarkLive from "./components/MarkLive";
import Waitlist from "./components/Waitlist";
import { weeklyIngestCount } from "../lib/metrics";

export const revalidate = 3600;

export default async function Home() {
  const papersThisWeek = await weeklyIngestCount();

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
        <div className="hero-act">
          <Waitlist
            source="home"
            note="One email when subscriptions open. Nothing else."
          />
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
        {papersThisWeek !== null && (
          <p className="metric-line">
            <b>{papersThisWeek.toLocaleString("en-US")}</b> papers ingested
            this week
          </p>
        )}
      </section>
    </main>
  );
}
