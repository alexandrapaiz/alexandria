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
          Every week the library reads new AI research and tells you{" "}
          <b>what changed</b>. Your agents load{" "}
          <b>the same answers you do</b>.
        </p>
        <div className="hero-act">
          <Waitlist
            source="home"
            note="We write once, on the day subscriptions open."
          />
          <Link href="/library" className="pill ghost">
            Read an issue
          </Link>
        </div>
        <p className="about-inline">
          The digest takes a few minutes to read. It covers what is new in AI
          research, what has proven out, and what no longer holds, in plain
          language. The skill library then turns the same findings into files
          your agents load, and every skill is revised as the research moves.
        </p>
        {papersThisWeek !== null && (
          <p className="metric-line">
            <b>{papersThisWeek.toLocaleString("en-US")}</b> papers read
            this week
          </p>
        )}
      </section>
    </main>
  );
}
