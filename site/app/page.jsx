import Link from "next/link";
import MarkLive from "./components/MarkLive";
import Waitlist from "./components/Waitlist";
import { weeklyIngestCount } from "../lib/metrics";
import { canonicalAlternates } from "../lib/public-routes";

export const revalidate = 3600;

// The home page had no `metadata` of its own and inherited the layout's whole
// object. It needs one now, for the canonical link, and the thing to know
// before editing it is in `canonicalAlternates`: setting `alternates` here
// replaces the layout's rather than extending it, so the plain-text alternate
// has to travel with the canonical or it leaves this page's head. Title and
// description are deliberately absent and still inherited.
export const metadata = {
  alternates: canonicalAlternates("/"),
};

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
          What changed in AI research this week, written for people who build things.
        </p>
        <div className="hero-act">
          <Waitlist
            source="home"
            note="One issue a week. You can unsubscribe from any of them."
          />
          <Link href="/library" className="pill ghost">
            Read an issue
          </Link>
        </div>
        <p className="about-inline">
          The library grows every day and corrects itself as the research moves, so every finding in it carries its evidence and is replaced when newer work overturns it. Each week the library becomes an issue that tells you what changed and what it means for your work, and the same findings become skills that your agents load and act on.
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
