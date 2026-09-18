import Link from "next/link";
import { listIssues } from "../../lib/content";
import ShelvesLive from "../components/ShelvesLive";

export const metadata = { title: "Library — library of alexandr.ia" };

export default function Library() {
  const issues = listIssues();
  return (
    <main>
      <section className="hero lib-hero">
        <div className="lib-art">
          <ShelvesLive />
        </div>
      </section>

      <section className="hero-follow lib-scene2">
        <p className="page-kicker">Library</p>
        <h1 className="page-title">Every issue, in full.</h1>
        <p className="page-intro">
          The weekly digest is free to read and nothing in it is held back.
          Start with the most recent issue.
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
