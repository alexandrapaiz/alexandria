import Link from "next/link";
import { notFound } from "next/navigation";
import { renderMarkdown } from "../../../lib/markdown.js";
import { getIssue, listIssues } from "../../../lib/content";

// The digest is free in full (docs/vision.md §0, amended 2026-09-17). There is
// no teaser split and no entitlement check on this route: a signed-out visitor
// reads the entire issue. Gating lives on the spine only, in site/lib/entitlement.js.

// Only published weeks have a route here. Without this, an address that is
// not in the list below goes through on-demand static generation first, and
// the 404 it renders reads headers through the root layout's ClerkProvider,
// which is a static-to-dynamic error and a 500 rather than a clean 404. That
// stayed hidden while one week was always published; it surfaced the moment
// retiring 2026-W37 left this list empty. With dynamicParams off, Next
// answers 404 for anything not published without rendering the page at all.
export const dynamicParams = false;

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
        dangerouslySetInnerHTML={{ __html: renderMarkdown(issue.body) }}
      />
      <div className="issue-foot">
        <p>
          Every issue reads like this one, free and in full, in your inbox
          each Monday. The skills behind it, the ones your agents load, come
          with the paid plan.
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
