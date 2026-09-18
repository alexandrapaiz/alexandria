import { marked } from "marked";
import { listSkills } from "../../lib/content";
import { shelveSkills } from "../../lib/skill-shelves";
import { hasSpine } from "../../lib/entitlement";
import SkillLibrary from "../components/SkillLibrary";

// Spine route: the skill files themselves are the $20 product. The catalogue
// stays public, because the catalogue is the pitch, and the body of a skill
// only renders for an entitled visitor. The bodies are parsed here rather
// than in the client component so an unentitled visitor is never sent one.
export const dynamic = "force-dynamic";
export const metadata = { title: "Skills — library of alexandr.ia" };

export default async function Skills() {
  const entitled = await hasSpine();
  const shelves = shelveSkills(listSkills()).map((shelf) => ({
    ...shelf,
    skills: shelf.skills.map(({ body, ...s }) => ({
      ...s,
      html: entitled ? marked.parse(body) : null,
    })),
  }));

  return (
    <main className="page skills-page">
      <p className="page-kicker">Skills</p>
      <h1 className="page-title">One library, two readers.</h1>
      <p className="page-intro">
        A skill is a file that does one thing well, from designing an agent
        harness to running a training loop. You read it to decide. Your agents
        load the same file to act. Every skill names the papers it came from,
        and it is revised when the research moves and retired with an
        explanation when it is overturned.
      </p>
      <p className="agent-note">
        Your agents can read this catalogue on their own, at{" "}
        <a href="/llms.txt">/llms.txt</a>.
      </p>

      <SkillLibrary shelves={shelves} entitled={entitled} />
    </main>
  );
}
