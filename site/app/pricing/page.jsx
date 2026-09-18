import Waitlist from "../components/Waitlist";

export const metadata = { title: "Pricing — library of alexandr.ia" };

export default function Pricing() {
  return (
    <main className="page">
      <p className="page-kicker">Pricing</p>
      <h1 className="page-title">Two ways in.</h1>
      <p className="page-intro">
        The weekly digest is free, in full, and always will be. One paid plan
        adds the operational layer underneath it: the skills your agents load,
        the claim graph they are drawn from, and the automations that keep both
        current.
      </p>
      <div className="tiers">
        <div className="tier">
          <h2>Digest</h2>
          <div className="price">Free</div>
          <span className="per">every Monday</span>
          <ul>
            <li>The weekly digest by email</li>
            <li>Every issue in full, nothing held back</li>
            <li>The complete archive in the library</li>
          </ul>
          <span className="pill ghost">Coming soon</span>
        </div>
        <div className="tier featured">
          <h2>The spine</h2>
          <div className="price">$20</div>
          <span className="per">per month</span>
          <ul>
            <li>Everything in the free digest</li>
            <li>The full skill library, for any AI agent</li>
            <li>The claim graph, explorable</li>
            <li>Skill revisions as the research moves</li>
            <li>Routines &amp; automations (coming soon)</li>
          </ul>
          <span className="pill">Coming soon</span>
        </div>
      </div>
      <section className="waitlist-block" id="waitlist">
        <h3>Be told when they open</h3>
        <p>
          Leave an email and we will write to you once, on the day
          subscriptions open. Until then nothing else arrives.
        </p>
        <Waitlist
          source="pricing"
          note="One email, and you can leave the list from any of them."
        />
      </section>
      <div className="billing-note">
        <h3>How billing works</h3>
        <p>
          You choose how your subscription behaves. It can renew automatically,
          or it can stop at the end of each month until a reminder arrives and
          you decide to continue. Subscription businesses often count on being
          forgotten, and we would rather earn the renewal than collect it.
        </p>
      </div>
    </main>
  );
}
