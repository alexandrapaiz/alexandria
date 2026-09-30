export const metadata = { title: "Mission — library of alexandr.ia" };

export default function Mission() {
  return (
    <main className="page">
      <p className="page-kicker">Mission</p>
      <h1 className="page-title">Accelerate every builder to frontier speed.</h1>
      <div className="prose">
        <p>
          Thousands of AI papers appear every week, more than anyone can read,
          and nobody keeps an honest record of what they add up to.
        </p>
        <p>
          alexandria is that record, a library of findings, each kept with its
          evidence and the procedure behind it, and linked to the findings that
          support, refine, or contradict it. The library grows every day and
          corrects itself when new work overturns what it held before.
        </p>
        <p>
          Once a week the library becomes an issue that tells you what changed
          and what it means for your work. The same findings become skills,
          which are procedures that held up, written as files your agents load
          and act on. Every skill names the papers it comes from, so a skill is
          revised when the research moves and retired with an explanation when
          the research is overturned.
        </p>
      </div>
    </main>
  );
}
