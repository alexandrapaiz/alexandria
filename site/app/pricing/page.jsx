import Waitlist from "../components/Waitlist";

export const metadata = { title: "Pricing — library of alexandr.ia" };

export default function Pricing() {
  return (
    <main className="page">
      <p className="page-kicker">Pricing</p>
      <h1 className="page-title">Two ways in.</h1>
      <p className="page-intro">
        Subscriptions open soon. Every plan starts with the weekly digest,
        delivered by email and archived in the library.
      </p>
      <div className="tiers">
        <div className="tier">
          <h2>Digest</h2>
          <div className="price">$10</div>
          <span className="per">per month</span>
          <ul>
            <li>The weekly digest by email</li>
            <li>The complete issue archive</li>
            <li>Every issue, past and future</li>
          </ul>
          <span className="pill ghost">Coming soon</span>
        </div>
        <div className="tier featured">
          <h2>Full library</h2>
          <div className="price">$30</div>
          <span className="per">per month</span>
          <ul>
            <li>Everything in Digest</li>
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
