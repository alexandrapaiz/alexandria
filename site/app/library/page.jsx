import Link from "next/link";
import { listIssues } from "../../lib/content";
import ShelvesLive from "../components/ShelvesLive";

export const metadata = { title: "Library — library of alexandr.ia" };

export default function Library() {
  const issues = listIssues();
  return (
    <main>
      <section className="hero">
        <div className="lib-head">
          <p className="page-kicker">Archive</p>
          <h1 className="page-title">The Library</h1>
          <p className="page-intro">
            The opening of each issue is free to read. Members read
            everything.
          </p>
        </div>
        <div className="lib-art">
          <ShelvesLive />
        </div>
      </section>

      <div className="scene-gap" aria-hidden="true" />

      <section className="hero-follow lib-scene2">
        <p className="page-kicker">Archive</p>
        <h1 className="page-title">The Library</h1>
        <p className="page-intro">
          The opening of each issue is free to read. Members read everything.
        </p>
        <div className="issue-list">
          {issues.map((it) => (
            <Link key={it.week} href={`/library/${it.week}`} className="issue">
              <span className="issue-week">[{it.dates}]</span>
              <h2>{it.title}</h2>
              <p>{it.excerpt.slice(0, 220)}…</p>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
