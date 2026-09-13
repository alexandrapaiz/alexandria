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
    </main>
  );
}
