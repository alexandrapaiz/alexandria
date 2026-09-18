import fs from "node:fs";
import path from "node:path";

// The digest is free in full (docs/vision.md §0, amended 2026-09-17), so an
// issue has no teaser split and no entitlement check: the whole body is
// public. Locally the bodies are markdown fixtures under site/content/issues;
// in production this module swaps to a Neon lookup with the same interface.

const ISSUE_DIR = path.join(process.cwd(), "content", "issues");
const SKILLS_DIR = path.join(process.cwd(), "..", "skills");
const WEEK = /^\d{4}-W\d{2}$/;

export function listIssues() {
  if (!fs.existsSync(ISSUE_DIR)) return [];
  return fs
    .readdirSync(ISSUE_DIR)
    .filter((f) => f.endsWith(".md") && WEEK.test(f.replace(/\.md$/, "")))
    .map((f) => {
      const week = f.replace(/\.md$/, "");
      return parseIssue(week, fs.readFileSync(path.join(ISSUE_DIR, f), "utf8"));
    })
    .sort((a, b) => (a.week < b.week ? 1 : -1));
}

export function getIssue(week) {
  const file = path.join(ISSUE_DIR, `${week}.md`);
  if (!WEEK.test(week) || !fs.existsSync(file)) return null;
  return parseIssue(week, fs.readFileSync(file, "utf8"));
}

function parseIssue(week, body) {
  // The issue's editorial title lives in its own H1. Newer issues carry their
  // dates with it ("Title [Month D–D, YYYY]"); the first editions did not, so
  // the week's own Monday-to-Sunday range stands in.
  const h1 = (body.match(/^# (.+)$/m) || [])[1] || "";
  const dm = h1.match(/^(.*?)\s*\[(.+)\]\s*$/);
  const firstGraf =
    body
      .split(/\n\n+/)
      .map((s) => s.trim())
      .filter((s) => s && !/^[#*\-]/.test(s))[0] || "";
  return {
    week,
    body,
    excerpt: firstGraf.replace(/\*\*/g, ""),
    title: dm ? dm[1] : h1,
    dates: dm ? dm[2] : weekRange(week),
  };
}

// "2026-W37" -> "September 7–13, 2026". ISO 8601: week 1 is the week holding
// January 4th, and weeks run Monday to Sunday.
export function weekRange(week) {
  const m = week.match(/^(\d{4})-W(\d{2})$/);
  if (!m) return week;
  const jan4 = new Date(Date.UTC(Number(m[1]), 0, 4));
  const monday = new Date(jan4);
  monday.setUTCDate(
    jan4.getUTCDate() - ((jan4.getUTCDay() || 7) - 1) + (Number(m[2]) - 1) * 7
  );
  const sunday = new Date(monday);
  sunday.setUTCDate(monday.getUTCDate() + 6);
  const month = (d) =>
    d.toLocaleString("en-US", { month: "long", timeZone: "UTC" });
  const tail =
    month(monday) === month(sunday)
      ? sunday.getUTCDate()
      : `${month(sunday)} ${sunday.getUTCDate()}`;
  return `${month(monday)} ${monday.getUTCDate()}–${tail}, ${sunday.getUTCFullYear()}`;
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
    // The skill file itself is the spine's product, so the body is read here
    // but only ever handed to an entitled visitor (site/lib/entitlement.js).
    body: m ? raw.slice(m[0].length).trim() : raw.trim(),
  };
}
