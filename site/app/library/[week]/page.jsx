import Link from "next/link";
import { notFound } from "next/navigation";
import { marked } from "marked";
import { getIssue } from "../../../lib/content";

// Entitlement stub: Clerk drops in here. Until then everyone is a reader,
// and locked content never leaves the server.
async function getEntitlement() {
  return { member: false };
}

export default async function Issue({ params }) {
  const { week } = await params;
  const issue = getIssue(week);
  if (!issue) notFound();

  const { member } = await getEntitlement();
  const teaserHtml = marked.parse(issue.teaser);
  const lockedHtml = member ? marked.parse(issue.locked) : null;

  return (
    <main className="page">
      <article
        className="digest"
        dangerouslySetInnerHTML={{ __html: teaserHtml }}
      />
      {member ? (
        <article
          className="digest"
          dangerouslySetInnerHTML={{ __html: lockedHtml }}
        />
      ) : (
        <div className="gate">
          <h3>The rest of this issue is for members.</h3>
          <p>
            Trailblazing, gaining traction, left behind, and what to read
            yourself.
          </p>
          <Link href="/pricing" className="pill">
            Subscribe
          </Link>
        </div>
      )}
    </main>
  );
}
