import fs from "node:fs";
import path from "node:path";

// Digests are the paid product: bodies stay out of the public repo (the
// content/ folder is gitignored). Locally they are markdown fixtures; in
// production this module swaps to a Neon lookup with the same interface.

const DIGEST_DIR = path.join(process.cwd(), "content", "digests");
const SKILLS_DIR = path.join(process.cwd(), "..", "skills");

export function listIssues() {
  if (!fs.existsSync(DIGEST_DIR)) return [];
  return fs
    .readdirSync(DIGEST_DIR)
    .filter((f) => f.endsWith(".md"))
    .map((f) => {
      const week = f.replace(/\.md$/, "");
      const body = fs.readFileSync(path.join(DIGEST_DIR, f), "utf8");
      return { week, ...splitDigest(body) };
    })
    .sort((a, b) => (a.week < b.week ? 1 : -1));
}

export function getIssue(week) {
  const file = path.join(DIGEST_DIR, `${week}.md`);
  if (!/^\d{4}-W\d{2}$/.test(week) || !fs.existsSync(file)) return null;
  return { week, ...splitDigest(fs.readFileSync(file, "utf8")) };
}

// The teaser is everything before the first section heading: title,
// masthead, and the opening. The gate hides the rest server-side, so
// locked content never reaches a non-member's browser.
function splitDigest(body) {
  const cut = body.indexOf("\n## ");
  const teaser = cut === -1 ? body : body.slice(0, cut);
  const locked = cut === -1 ? "" : body.slice(cut);
  const firstGraf =
    teaser
      .split(/\n\n+/)
      .map((s) => s.trim())
      .filter((s) => s && !s.startsWith("#") && !s.startsWith("*"))[0] || "";
  // The issue's editorial title lives in its own H1: "Title [Month D–D, YYYY]".
  const h1 = (body.match(/^# (.+)$/m) || [])[1] || "";
  const dm = h1.match(/^(.*?)\s*\[(.+)\]\s*$/);
  return {
    teaser,
    locked,
    excerpt: firstGraf.replace(/\*\*/g, ""),
    title: dm ? dm[1] : h1,
    dates: dm ? dm[2] : "",
  };
}

export function listSkills() {
  if (!fs.existsSync(SKILLS_DIR)) return [];
  return fs
    .readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      const file = path.join(SKILLS_DIR, d.name, "SKILL.md");
      if (!fs.existsSync(file)) return null;
      return parseSkill(fs.readFileSync(file, "utf8"));
    })
    .filter(Boolean);
}

function parseSkill(raw) {
  const m = raw.match(/^---\n([\s\S]*?)\n---/);
  const fm = m ? m[1] : "";
  const get = (key) => {
    const line = fm.match(new RegExp(`^${key}:\\s*(.+)$`, "m"));
    return line ? line[1].trim().replace(/^"|"$/g, "") : "";
  };
  const papers = [...fm.matchAll(/^\s+- "(.+?)"$/gm)].map((x) => x[1]);
  return {
    name: get("name"),
    description: get("description"),
    version: get("version"),
    status: get("status"),
    validated: get("validated"),
    papers,
  };
}
