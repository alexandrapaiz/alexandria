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
        <p>Still being built. We will write to you the day they ship.</p>
      </main>
    );
  }

  return (
    <main className="page">
      <p className="page-kicker">Routines</p>
      <h1 className="page-title">Standing jobs, run for you.</h1>
      <p className="page-intro">
        A routine is a standing job the library runs on your behalf. None of
        them are built yet. When they ship, one will watch a topic, another
        will follow a claim as the evidence moves, and another will refresh
        the skills your agents load without being asked.
      </p>
      <div className="gate">
        <h3>Routines come with the paid plan.</h3>
        <p>
          It will include them the day they ship, alongside the skill library
          and the claim graph.
        </p>
        <Link href="/pricing" className="pill">
          See pricing
        </Link>
      </div>
    </main>
  );
}
