import Link from "next/link";
import { notFound } from "next/navigation";
import { marked } from "marked";
import { getIssue, listIssues } from "../../../lib/content";

// The digest is free in full (docs/vision.md §0, amended 2026-09-17). There is
// no teaser split and no entitlement check on this route: a signed-out visitor
// reads the entire issue. Gating lives on the spine only, in site/lib/entitlement.js.

export function generateStaticParams() {
  return listIssues().map((it) => ({ week: it.week }));
}

export async function generateMetadata({ params }) {
  const { week } = await params;
  const issue = getIssue(week);
  return {
    title: issue
      ? `${issue.title} — library of alexandr.ia`
      : "Issue — library of alexandr.ia",
    description: issue?.excerpt.slice(0, 200),
  };
}

export default async function Issue({ params }) {
  const { week } = await params;
  const issue = getIssue(week);
  if (!issue) notFound();

  return (
    <main className="page">
      <article
        className="digest"
        dangerouslySetInnerHTML={{ __html: marked.parse(issue.body) }}
      />
      <div className="issue-foot">
        <p>
          Every issue reads like this one, free and in full, in your inbox
          each Monday. The skills and the claim graph behind it come with the
          paid plan.
        </p>
        <div className="issue-foot-cta">
          <Link href="/library" className="pill ghost">
            All issues
          </Link>
          <Link href="/pricing" className="pill">
            See pricing
          </Link>
        </div>
      </div>
    </main>
  );
}
