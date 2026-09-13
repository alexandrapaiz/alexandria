export const metadata = { title: "Mission — library of alexandr.ia" };

export default function Mission() {
  return (
    <main className="page">
      <p className="page-kicker">Mission</p>
      <h1 className="page-title">Research that runs itself.</h1>
      <div className="prose">
        <p>
          Thousands of AI papers appear every week, and no person can keep an
          honest record of what they add up to. alexandria exists to keep that
          record without a person: an autonomous system that does research on
          the research, continuously.
        </p>
        <p>
          A pipeline reads the field&rsquo;s output in full and distills each
          paper into <b>claims</b>: single findings kept with their evidence
          and the procedures behind them. The claims form a graph that records
          how the field treats them over time, so that support, refinement,
          and contradiction accumulate in one place instead of scattering
          across the literature.
        </p>
        <p>
          Once a week the library writes the digest, and because it is drawn
          from the graph rather than from headlines, it reads as an updated
          statement of where the field stands. Watching what is new, what is
          gaining acceptance, and what newer evidence has overturned is the
          method behind that statement, not the point of it.
        </p>
        <p>
          The record also compiles into action. Procedures that survive
          scrutiny become <b>agent skills</b> tied to the claims that justify
          them, and since that provenance stays live, a skill is revised as
          its research sharpens and retired with an explanation if the
          research is overturned.
        </p>
        <p>
          The recursion is the mission. The library reads, distills,
          publishes, and proposes improvements to its own prompts and
          pipeline, so the system that studies a moving field moves with it.
          The human role is optional, and consists mostly of reading the
          digest like everyone else.
        </p>
      </div>
    </main>
  );
}
