export const metadata = { title: "Mission — library of alexandr.ia" };

export default function Mission() {
  return (
    <main className="page">
      <p className="page-kicker">Mission</p>
      <h1 className="page-title">Accelerate every builder to frontier speed.</h1>
      <div className="prose">
        <p>
          AI research moves faster than any person can read. Thousands of
          papers appear every week, and keeping an honest record of what they
          add up to is more work than a person has hours for. alexandria keeps
          that record instead, and it does so without a person in the loop.
        </p>
        <p>
          The library reads the field&rsquo;s output and breaks each paper
          down into <b>claims</b>, which are single findings kept with their
          evidence and the procedures behind them. Those claims are linked to
          each other, so support, refinement, and contradiction collect in one
          place instead of scattering across the literature.
        </p>
        <p>
          Once a week the library writes the digest from that record. Because
          it is drawn from the claims rather than from headlines, it reads as
          a current statement of where the field stands rather than as a feed
          of what was loud.
        </p>
        <p>
          The same record turns into work your agents can do. You read the
          digest to decide what matters, and your agents load the skills to
          act on it, from the same claims either way. Procedures that hold up
          become <b>agent skills</b>, each one tied to the claims that justify
          it. That link stays live, so a skill is revised when its research
          sharpens and retired with an explanation when the research is
          overturned.
        </p>
        <p>
          The library also reads itself. It proposes improvements to its own
          prompts and to the pipeline that runs them, which is how a system
          that studies a moving field manages to move with it.
        </p>
      </div>
    </main>
  );
}
