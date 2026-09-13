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
          attached. Every claim then lives in a graph that records how the
          field treats it over time, so that accumulating support, later
          refinements, and outright contradictions all become part of its
          record rather than scattered across the literature.
        </p>
        <p>
          Once a week the library writes. The digest reports what is genuinely
          new, what is gaining acceptance, and what has been left behind,
          because knowing what stopped being true is worth as much as knowing
          what just became true.
        </p>
        <p>
          The library also builds. Procedures that survive scrutiny become{" "}
          <b>Claude skills</b> that carry full provenance back to the claims
          justifying them, and because that provenance stays live, movement in
          the graph flows into the skills themselves: a skill is revised as its
          research sharpens and retired with an explanation if the research is
          overturned. The result is knowledge that maintains itself.
        </p>
        <p>
          The pipeline runs without supervision, reading, distilling,
          publishing, and proposing its own improvements. The human role is
          optional, and consists mostly of reading the digest like everyone
          else.
        </p>
      </div>
    </main>
  );
}
