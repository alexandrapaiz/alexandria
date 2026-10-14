import { renderMarkdown } from "../../lib/markdown.js";
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
      html: entitled ? renderMarkdown(body) : null,
    })),
  }));

  return (
    <main className="page skills-page">
      <p className="page-kicker">Skills</p>
      <h1 className="page-title">
          Skill library
        </h1>
      <p className="page-intro">
          Your agents stay at the frontier without you carrying them there. Each skill in this library gives an agent a way of doing one job that the research has shown to work, and the library keeps every skill current at the pace of the research that is gaining the most traction, so as the field confirms a technique, sharpens it, or overturns it, your agents change with it. You do not schedule the update or read the paper, because the library follows the field and your agents direct themselves from what it holds. What you get is agents that work from the current state of the evidence today and still will next month.
        </p>
      <p className="agent-note">
          The catalogue is open to anyone. The files come with the paid plan, and your agents can read the catalogue directly at{" "}
          <a href="/llms.txt">/llms.txt</a>.
        </p>

      <SkillLibrary shelves={shelves} entitled={entitled} />
    </main>
  );
}
