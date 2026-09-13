import Link from "next/link";
import { listSkills } from "../../lib/content";

export const metadata = { title: "Skills — library of alexandr.ia" };

export default function Skills() {
  const skills = listSkills();
  return (
    <main className="page">
      <p className="page-kicker">Skills</p>
      <h1 className="page-title">Research that installs.</h1>
      <p className="page-intro">
        The best techniques the research has produced, packaged so your
        agents can use them: harness design, training recipes, debugging
        methods for multi-agent systems. Each skill is proven before it
        ships, updated as the science sharpens, and retired with an
        explanation if it is overturned.
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
          <div className="skill-lock">
            <span>Full skill file is for members.</span>
            <Link href="/pricing" className="pill">
              Get access
            </Link>
          </div>
        </div>
      ))}
    </main>
  );
}
