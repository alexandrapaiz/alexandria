import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { latestValidation, readProvenance } from "./skill-provenance.js";

// The digest is free in full (docs/vision.md §0, amended 2026-09-17), so an
// issue has no teaser split and no entitlement check: the whole body is
// public. Locally the bodies are markdown fixtures under site/content/issues;
// in production this module swaps to a Neon lookup with the same interface.

const ISSUE_DIR = path.join(process.cwd(), "content", "issues");
const SKILLS_DIR = path.join(process.cwd(), "..", "skills");
const WEEK = /^\d{4}-W\d{2}$/;

// Weeks the public site does not publish. This hides an issue from the
// listing and from its own route; it deletes nothing. The markdown file
// stays on disk and the row stays in the database, so removing a week from
// this list is all it takes to publish it again.
//
// 2026-W37 is retired here on the owner's order (2026-09-19) so that
// Monday's issue is the pilot the public reads first.
export const HIDDEN_WEEKS = new Set(["2026-W37"]);

export function listIssues() {
  if (!fs.existsSync(ISSUE_DIR)) return [];
  return fs
    .readdirSync(ISSUE_DIR)
    .filter((f) => f.endsWith(".md") && WEEK.test(f.replace(/\.md$/, "")))
    .map((f) => f.replace(/\.md$/, ""))
    .filter((week) => !HIDDEN_WEEKS.has(week))
    .map((week) =>
      parseIssue(week, fs.readFileSync(path.join(ISSUE_DIR, `${week}.md`), "utf8"))
    )
    .sort((a, b) => (a.week < b.week ? 1 : -1));
}

export function getIssue(week) {
  const file = path.join(ISSUE_DIR, `${week}.md`);
  if (!WEEK.test(week) || HIDDEN_WEEKS.has(week) || !fs.existsSync(file)) {
    return null;
  }
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

const VALIDATION_DIR = path.join(SKILLS_DIR, "_validation", "results");

export function listSkills() {
  if (!fs.existsSync(SKILLS_DIR)) return [];
  const bundles = listValidations();
  return fs
    .readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      const file = path.join(SKILLS_DIR, d.name, "SKILL.md");
      if (!fs.existsSync(file)) return null;
      return parseSkill(fs.readFileSync(file, "utf8"), bundles);
    })
    .filter(Boolean);
}

// Every recorded trigger-test run. A bundle that will not parse is skipped
// rather than thrown: one corrupt receipt must not take the catalogue down
// with it, and a skill with no readable receipt already renders as unmeasured.
export function listValidations() {
  if (!fs.existsSync(VALIDATION_DIR)) return [];
  return fs
    .readdirSync(VALIDATION_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => {
      try {
        return JSON.parse(fs.readFileSync(path.join(VALIDATION_DIR, f), "utf8"));
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

// The same digest skills/_validation/trigger_test.py records per suite:
// sha256 of the file's bytes, first 16 hex characters. Computed here so the
// page can say whether the receipt describes the text it is showing.
export function skillSha(raw) {
  return crypto.createHash("sha256").update(raw, "utf8").digest("hex").slice(0, 16);
}

function parseSkill(raw, bundles = []) {
  // Provenance is nested under `provenance:` in the frontmatter, so it is read
  // structurally by site/lib/skill-provenance.js rather than by key regex.
  const p = readProvenance(raw);
  return {
    name: p.name,
    description: p.description,
    version: p.version,
    status: p.status,
    extracted: p.extracted,
    validated: p.validated,
    claims: p.claims,
    papers: p.papers,
    validation: latestValidation(bundles, p.name, skillSha(raw)),
    // The skill file itself is the spine's product, so the body is read here
    // but only ever handed to an entitled visitor (site/lib/entitlement.js).
    body: p.body,
  };
}
