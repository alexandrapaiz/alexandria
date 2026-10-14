import { subscriberForToken } from "../../lib/unsubscribe";

export const metadata = { title: "Unsubscribe — library of alexandr.ia" };
export const dynamic = "force-dynamic";

// The page the unsubscribe link in every issue opens. It does not unsubscribe
// anybody by itself, because a link in an email is fetched by mail scanners
// and link previewers before a person reads it, and a page that flipped the
// row on load would remove subscribers who never clicked anything. So the
// page asks, and the button posts to /api/unsubscribe.
//
// Sprint 2026-10-05 item 3, clause 2 of the definition of done. The reasoning
// about the token is in site/lib/unsubscribe-core.js.

// No address here, and that is on purpose. The POST redirects back to this
// page with only the outcome in the query string, because an email address in
// a URL ends up in browser history, in a referrer header and in any log the
// request passes through, and the person already knows which address they
// just removed.
function Done() {
  return (
    <>
      <h1 className="page-title">You are unsubscribed.</h1>
      <p className="page-intro">
        No issue is going to that address. Nothing else needs doing, and you
        are welcome back whenever you want to read again.
      </p>
    </>
  );
}

function Already() {
  return (
    <>
      <h1 className="page-title">You were already unsubscribed.</h1>
      <p className="page-intro">
        This link still works, so clicking it again changed nothing. No issue
        is going to that address.
      </p>
    </>
  );
}

function Unknown() {
  return (
    <>
      <h1 className="page-title">We could not read that link.</h1>
      <p className="page-intro">
        The link at the foot of any issue you have will work. If none of them
        do, write to the address the issue came from and we will take you off
        the list by hand.
      </p>
    </>
  );
}

function Unavailable() {
  return (
    <>
      <h1 className="page-title">We cannot reach the list right now.</h1>
      <p className="page-intro">
        This is ours, not yours. Try the same link again in a few minutes, and
        it will work.
      </p>
    </>
  );
}

function Confirm({ token, email }) {
  return (
    <>
      <h1 className="page-title">Unsubscribe from the weekly issue?</h1>
      <p className="page-intro">
        {email
          ? `${email} is on the list. One click takes it off, and nothing is sent after that.`
          : "One click takes you off the list, and nothing is sent after that."}
      </p>
      <form method="post" action="/api/unsubscribe">
        <input type="hidden" name="t" value={token} />
        <button className="pill" type="submit">
          Unsubscribe
        </button>
      </form>
    </>
  );
}

export default async function Unsubscribe({ searchParams }) {
  const params = await searchParams;
  const state = typeof params?.state === "string" ? params.state : null;
  const token = typeof params?.t === "string" ? params.t : "";

  // After the POST the route redirects back here with the outcome, so this
  // page is both the question and the answer and there is one URL to remember.
  if (state === "done") return <main className="page"><Done /></main>;
  if (state === "already") return <main className="page"><Already /></main>;
  if (state === "unavailable") return <main className="page"><Unavailable /></main>;
  if (state === "unknown") return <main className="page"><Unknown /></main>;

  const found = await subscriberForToken(token).catch(() => ({
    ok: false,
    retryable: true,
  }));

  if (!found.ok) return <main className="page"><Unavailable /></main>;
  if (!found.found) return <main className="page"><Unknown /></main>;
  if (found.alreadyUnsubscribed) return <main className="page"><Already /></main>;

  return (
    <main className="page">
      <Confirm token={token} email={found.email} />
    </main>
  );
}
