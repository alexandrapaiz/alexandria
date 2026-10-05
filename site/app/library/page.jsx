import Link from "next/link";
import { publishedIssues } from "../../lib/issues-live.js";
import ShelvesLive from "../components/ShelvesLive";

export const metadata = { title: "Library — library of alexandr.ia" };

// Per request, for the reason the issue route gives at more length: the list
// of published weeks is the `digests` table now, and that table gains a row
// on Monday morning without a deploy. A build-time listing would show last
// week until somebody noticed.
export const dynamic = "force-dynamic";

export default async function Library() {
  const issues = await publishedIssues();
  return (
    <main>
      <section className="hero lib-hero">
        <div className="lib-art">
          <ShelvesLive />
        </div>
      </section>

      <section className="hero-follow lib-scene2">
        <p className="page-kicker">Library</p>
        <h1 className="page-title">
          Every issue
        </h1>
        <p className="page-intro">
          The weekly issue is free and complete, and it tells you what changed in AI research that week and what it means for the things you are building.
        </p>
        {issues.length === 0 ? (
          <p className="desk-empty">
            The first issue is on its way. Check back on Monday.
          </p>
        ) : (
          <div className="issue-list">
            {issues.map((it) => (
              <Link key={it.week} href={`/library/${it.week}`} className="issue">
                <span className="issue-week">[{it.dates}]</span>
                <h2>{it.title}</h2>
                <p>{it.excerpt.slice(0, 220)}…</p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
