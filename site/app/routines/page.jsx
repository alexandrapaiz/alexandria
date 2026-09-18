import Link from "next/link";
import { hasSpine } from "../../lib/entitlement";

// Spine route: automations are the third piece of the $20 tier. They are not
// built yet, so an entitled visitor sees the honest "coming soon" and everyone
// else sees the locked state.
export const dynamic = "force-dynamic";
export const metadata = { title: "Routines — library of alexandr.ia" };

export default async function Routines() {
  const entitled = await hasSpine();

  if (entitled) {
    return (
      <main className="soon">
        <h1>
          routines &amp;
          <br />
          automations
        </h1>
        <p>Coming soon.</p>
      </main>
    );
  }

  return (
    <main className="page">
      <p className="page-kicker">Routines</p>
      <h1 className="page-title">Routines &amp; automations.</h1>
      <p className="page-intro">
        Standing jobs that run against the library on your behalf: watch a
        topic, track a claim as the evidence moves, and get the skills your
        agents load refreshed without asking.
      </p>
      <div className="gate">
        <h3>Routines are part of the spine.</h3>
        <p>
          They are still being built. The spine includes them the day they
          ship, alongside the skill library and the claim graph.
        </p>
        <Link href="/pricing" className="pill">
          Get access
        </Link>
      </div>
    </main>
  );
}
