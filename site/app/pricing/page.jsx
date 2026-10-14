import Waitlist from "../components/Waitlist";
import { checkoutOffers } from "../../lib/polar-core";

export const metadata = { title: "Pricing — library of alexandr.ia" };

// The three offers ADR-31 decided, read out of the environment rather than
// hard-coded, so the owner can create the products in Polar and the page
// becomes buyable without a deploy. Until a checkout link is set, each
// paid plan shows what it costs and says the door is not open yet, which
// is the truth and is better than a button that goes nowhere.
function Offer({ offer }) {
  if (!offer.live) return <span className="pill ghost">Opens shortly</span>;
  return (
    <a className="pill" href={offer.href}>
      {offer.label}
    </a>
  );
}

export default function Pricing() {
  const offers = checkoutOffers(process.env);
  const byId = Object.fromEntries(offers.map((offer) => [offer.id, offer]));

  return (
    <main className="page">
      <p className="page-kicker">Pricing</p>
      <h1 className="page-title">Read for free. Build for $20.</h1>
      <p className="page-intro">
        The weekly digest stays free and arrives in full. The paid plan opens
        the skill library, in the same files you read and your agents load,
        and the routines that keep it current as the research moves.
      </p>
      <div className="tiers three">
        <div className="tier">
          <h2>Digest</h2>
          <div className="price">Free</div>
          <span className="per">every Monday</span>
          <ul>
            <li>The weekly digest, by email</li>
            <li>Every issue in full</li>
            <li>The complete archive</li>
          </ul>
          <a className="pill ghost" href="#waitlist">
            Start reading
          </a>
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
          <p className="tier-note">
            Three days free first, and the card is only charged when the
            trial ends.{" "}
            {byId.trial.live ? <a href={byId.trial.href}>Start the trial</a> : null}
          </p>
          <Offer offer={byId.monthly} />
        </div>
        <div className="tier">
          <h2>Lifetime</h2>
          <div className="price">$200</div>
          <span className="per">once</span>
          <ul>
            <li>Everything in Full access</li>
            <li>One payment, kept for good</li>
            <li>No renewal to remember</li>
          </ul>
          <Offer offer={byId.lifetime} />
        </div>
      </div>
      <section className="waitlist-block" id="waitlist">
        <h3>Start reading</h3>
        <p>
          The weekly issue is free while subscriptions are comped, so there is
          nothing to pay and nothing to cancel. Nothing else arrives.
        </p>
        <Waitlist
          source="pricing"
          note="One issue a week. You can unsubscribe from any of them."
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
        <p>
          Payment and invoicing run through Polar, which is the seller of
          record and handles tax wherever you are. Your card details never
          reach this site.
        </p>
      </div>
    </main>
  );
}
