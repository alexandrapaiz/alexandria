export const metadata = { title: "Mission — library of alexandr.ia" };

export default function Mission() {
  return (
    <main className="page">
      <p className="page-kicker">Mission</p>
      <h1 className="page-title">Nothing left unread.</h1>
      <div className="prose">
        <p>
          Thousands of AI papers appear every week. No person can read them, so
          builders run on summaries of summaries, and on results that were
          quietly overturned months ago.
        </p>
        <p>
          alexandria is a library that reads. A pipeline ingests the field's
          output, reads papers in full, and distills each one into{" "}
          <b>claims</b>: single findings with their evidence and procedures
          attached. Claims live in a graph that records how the field treats
          them over time. Support accumulates. Refinements land. Contradictions
          are drawn the day they arrive.
        </p>
        <p>
          Once a week the library writes. The digest reports what is genuinely
          new, what is gaining acceptance, and what has been left behind,
          because knowing what stopped being true is worth as much as knowing
          what just became true.
        </p>
        <p>
          The library also builds. Procedures that survive scrutiny become{" "}
          <b>Claude skills</b> with full provenance back to the claims that
          justify them. When the graph moves under a skill, the skill is
          revised or retired. Knowledge that maintains itself.
        </p>
        <p>
          The pipeline runs alone: reading, distilling, publishing, and
          proposing its own improvements. A human is optional, and mostly
          reads the digest like everyone else.
        </p>
      </div>
    </main>
  );
}
