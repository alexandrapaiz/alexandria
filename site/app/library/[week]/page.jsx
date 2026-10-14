import Link from "next/link";
import { notFound } from "next/navigation";
import { renderMarkdown } from "../../../lib/markdown.js";
import { publishedIssue } from "../../../lib/issues-live.js";

// The digest is free in full (docs/vision.md §0, amended 2026-09-17). There is
// no teaser split and no entitlement check on this route: a signed-out visitor
// reads the entire issue. Gating lives on the spine only, in site/lib/entitlement.js.

// Rendered per request, which is the whole point of the change that brought
// `publishedIssue` here. The set of published weeks now comes from `digests`,
// the table the press writes when it mails an issue, so it grows on a Monday
// morning with no deploy behind it. A route that fixed its own list of weeks
// at build time could not see that row, which is the condition this replaces.
//
// It also retires the `dynamicParams = false` guard this file used to carry.
// That guard existed because an unpublished address went through on-demand
// static generation, and the 404 it rendered read headers through the root
// layout's ClerkProvider, which is a static-to-dynamic error and a 500 rather
// than a clean 404. A route that is dynamic from the start has no static
// render to bail out of, so `notFound()` renders a clean 404 here. There is a
// test for that sentence, because it is the reason the old guard existed and
// an argument is not evidence: tests/test_issue_route.py builds the site and
// asks an unpublished week for its status code.
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }) {
  const { week } = await params;
  const issue = await publishedIssue(week);
  return {
    title: issue
      ? `${issue.title} — library of alexandr.ia`
      : "Issue — library of alexandr.ia",
    description: issue?.excerpt.slice(0, 200),
  };
}

export default async function Issue({ params }) {
  const { week } = await params;
  const issue = await publishedIssue(week);
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
