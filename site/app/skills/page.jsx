import Link from "next/link";
import { marked } from "marked";
import { listSkills } from "../../lib/content";
import { hasSpine } from "../../lib/entitlement";

// Spine route: the skill files themselves are the $20 product. The card for
// each skill stays public, because the catalogue is the pitch, but the body
// of a skill only renders for an entitled visitor.
export const dynamic = "force-dynamic";
export const metadata = { title: "Skills — library of alexandr.ia" };

export default async function Skills() {
  const skills = listSkills();
  const entitled = await hasSpine();

  return (
    <main className="page">
      <p className="page-kicker">Skills</p>
      <h1 className="page-title">Skills your agents can load.</h1>
      <p className="page-intro">
        Each skill is a file your agent loads to do one thing well, from
        designing an agent harness to running a training loop. Every skill
        names the papers it came from, and it is revised when the research
        moves and retired with an explanation when it is overturned.
      </p>
      {skills.map((s) => (
        <div key={s.name} className="skill-card">
          <div className="skill-meta">
            <span>v{s.version}</span>
            <span>{s.status}</span>
            <span>{s.papers.length} sources</span>
          </div>
          <h2>{s.name}</h2>
          <p>{s.description}</p>
          <ul className="skill-sources">
            {s.papers.map((p) => (
              <li key={p}>{p.split(" — ")[0]}</li>
            ))}
          </ul>
          {entitled ? (
            <article
              className="digest skill-body"
              dangerouslySetInnerHTML={{ __html: marked.parse(s.body) }}
            />
          ) : (
            <div className="skill-lock">
              <span>The full skill file comes with the paid plan.</span>
              <Link href="/pricing" className="pill">
                See pricing
              </Link>
            </div>
          )}
        </div>
      ))}
    </main>
  );
}
