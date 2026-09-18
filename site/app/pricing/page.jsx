import Waitlist from "../components/Waitlist";

export const metadata = { title: "Pricing — library of alexandr.ia" };

export default function Pricing() {
  return (
    <main className="page">
      <p className="page-kicker">Pricing</p>
      <h1 className="page-title">Read for free. Build for $20.</h1>
      <p className="page-intro">
        The weekly digest stays free and arrives in full. The paid plan opens
        the skill library, in the same files you read and your agents load,
        and the routines that keep it current as the research moves.
      </p>
      <div className="tiers">
        <div className="tier">
          <h2>Digest</h2>
          <div className="price">Free</div>
          <span className="per">every Monday</span>
          <ul>
            <li>The weekly digest, by email</li>
            <li>Every issue in full</li>
            <li>The complete archive</li>
          </ul>
          <span className="pill ghost">Opens October 13</span>
        </div>
        <div className="tier featured">
          <h2>Full access</h2>
          <div className="price">$20</div>
          <span className="per">per month</span>
          <ul>
            <li>Everything in the digest</li>
            <li>The full skill library, file by file</li>
            <li>The same files your agents load</li>
            <li>Skill updates as the research moves</li>
            <li>Routines, once they ship</li>
          </ul>
          <span className="pill">Opens October 13</span>
        </div>
      </div>
      <section className="waitlist-block" id="waitlist">
        <h3>Hear when it opens</h3>
        <p>
          We write once, on the day subscriptions open. Nothing else arrives
          before then.
        </p>
        <Waitlist
          source="pricing"
          note="We send one email, and it carries an unsubscribe link."
        />
      </section>
      <div className="billing-note">
        <h3>How billing works</h3>
        <p>
          You choose how your subscription behaves. It can renew
          automatically, or it can stop at the end of each month until a
          reminder arrives and you decide to continue. Many subscription
          businesses count on being forgotten, and we would rather earn the
          renewal than collect it.
        </p>
      </div>
    </main>
  );
}
