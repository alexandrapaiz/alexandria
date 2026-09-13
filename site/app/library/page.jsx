import Link from "next/link";
import { listIssues } from "../../lib/content";
import Shelves from "../components/Shelves";

export const metadata = { title: "Library — library of alexandr.ia" };

export default function Library() {
  const issues = listIssues();
  return (
    <main className="page">
      <div className="shelf-art">
        <Shelves />
      </div>
      <p className="page-kicker">Library</p>
      <h1 className="page-title">Every issue, kept.</h1>
      <p className="page-intro">
        The weekly digest, archived in full. The opening of each issue is free
        to read. Members read everything.
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
    </main>
  );
}
