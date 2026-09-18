import { marked } from "marked";

export const revalidate = 60;
export const metadata = { title: "Desk — library of alexandr.ia" };

const REPO = "alexandrapaiz/alexandria";
const LANES = {
  engineer: "engineer",
  pm: "pm",
  market: "market",
  okr: "okr",
  exo: "exo",
  sec: "sec",
  skill: "skill",
  weekly: "weekly",
  fe: "fe",
  fin: "fin",
  sales: "sales",
};

const lane = (branch) => LANES[branch.split("/")[0]] || "other";

// The repo is private (owner's call, 2026-09-17), so the desk needs a
// read token: put GITHUB_TOKEN=<fine-grained read token> in site/.env.local
const auth = () =>
  process.env.GITHUB_TOKEN
    ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` }
    : {};

async function gh(path) {
  try {
    const r = await fetch(`https://api.github.com/repos/${REPO}/${path}`, {
      headers: { Accept: "application/vnd.github+json", ...auth() },
      next: { revalidate: 60 },
    });
    return r.ok ? r.json() : null;
  } catch {
    return null;
  }
}

async function raw(path) {
  try {
    const r = await fetch(
      `https://raw.githubusercontent.com/${REPO}/main/${path}`,
      { headers: auth(), next: { revalidate: 60 } }
    );
    return r.ok ? r.text() : null;
  } catch {
    return null;
  }
}

// ideas.md entries: "### YYYY-MM-DD — Name" blocks with a "- Status: x" line
function parseIdeas(md) {
  if (!md) return [];
  return md
    .split(/^### /m)
    .slice(1)
    .map((block) => {
      const [head, ...rest] = block.split("\n");
      const status = (rest.join("\n").match(/- Status:\s*(\w+)/) || [])[1];
      return { head: head.trim(), status: (status || "").toLowerCase() };
    });
}

async function newestFile(dir, prefix) {
  const listing = await gh(`contents/${dir}`);
  if (!Array.isArray(listing)) return null;
  const names = listing
    .map((f) => f.name)
    .filter((n) => n.startsWith(prefix) && n.endsWith(".md"))
    .sort()
    .reverse();
  return names[0] ? { name: names[0], text: await raw(`${dir}/${names[0]}`) } : null;
}

const ago = (iso) => {
  const m = Math.round((Date.now() - new Date(iso)) / 60000);
  if (m < 60) return `${m}m ago`;
  if (m < 1440) return `${Math.round(m / 60)}h ago`;
  return `${Math.round(m / 1440)}d ago`;
};

export default async function Desk() {
  const [open, closed, ideasMd, sprint] = await Promise.all([
    gh("pulls?state=open&per_page=50"),
    gh("pulls?state=closed&per_page=15"),
    raw("docs/ideas.md"),
    newestFile("docs/sprints", "sprint-"),
  ]);

  const openPRs = Array.isArray(open) ? open : [];
  const merged = (Array.isArray(closed) ? closed : []).filter((p) => p.merged_at);
  const ideas = parseIdeas(ideasMd);
  const verdictQueue = ideas.filter((i) => i.status === "proposed" || i.status === "urgent");
  const offline = open === null;

  return (
    <main>
      <section className="hero-follow desk">
        <p className="page-kicker">Owner</p>
        <h1 className="page-title">The Desk</h1>
        <p className="page-intro">
          Every agent&apos;s output lands here as a pull request. Your merge is
          the gate; your verdicts steer the ledger.
        </p>

        {offline && (
          <p className="desk-empty">
            GitHub could not be reached just now. Reload in a minute.
          </p>
        )}

        <h2 className="desk-h">
          Awaiting your merge <span className="desk-count">{openPRs.length}</span>
        </h2>
        {openPRs.length === 0 && !offline && (
          <p className="desk-empty">Nothing waiting. The queue is clear.</p>
        )}
        <div className="desk-list">
          {openPRs.map((pr) => (
            <a key={pr.number} href={pr.html_url} target="_blank" rel="noreferrer" className="desk-row">
              <span className="desk-lane">{lane(pr.head.ref)}</span>
              <span className="desk-main">
                <b>{pr.title}</b>
                <i>
                  #{pr.number} · {pr.head.ref} · opened {ago(pr.created_at)}
                </i>
              </span>
              <span className="desk-go">review →</span>
            </a>
          ))}
        </div>

        <h2 className="desk-h">
          Awaiting your verdict <span className="desk-count">{verdictQueue.length}</span>
        </h2>
        {verdictQueue.length === 0 && (
          <p className="desk-empty">No proposed ideas in the ledger.</p>
        )}
        <div className="desk-list">
          {verdictQueue.map((i) => (
            <a
              key={i.head}
              href={`https://github.com/${REPO}/blob/main/docs/ideas.md`}
              target="_blank"
              rel="noreferrer"
              className="desk-row"
            >
              <span className="desk-lane">{i.status}</span>
              <span className="desk-main">
                <b>{i.head}</b>
                <i>docs/ideas.md · mark accepted or rejected</i>
              </span>
              <span className="desk-go">open →</span>
            </a>
          ))}
        </div>

        <h2 className="desk-h">Current sprint</h2>
        {sprint?.text ? (
          <div
            className="prose desk-doc"
            dangerouslySetInnerHTML={{ __html: marked.parse(sprint.text) }}
          />
        ) : (
          <p className="desk-empty">
            No sprint on main yet. The PM&apos;s plan arrives as a PR above;
            merging it starts the sprint.
          </p>
        )}

        <h2 className="desk-h">Recently merged</h2>
        <div className="desk-list">
          {merged.slice(0, 8).map((pr) => (
            <a key={pr.number} href={pr.html_url} target="_blank" rel="noreferrer" className="desk-row done">
              <span className="desk-lane">{lane(pr.head.ref)}</span>
              <span className="desk-main">
                <b>{pr.title}</b>
                <i>#{pr.number} · merged {ago(pr.merged_at)}</i>
              </span>
            </a>
          ))}
        </div>

        <p className="desk-foot">
          Agent runs live in{" "}
          <a href={`https://github.com/${REPO}/actions`} target="_blank" rel="noreferrer">
            GitHub Actions
          </a>
          . Charters in{" "}
          <a href={`https://github.com/${REPO}/tree/main/prompts`} target="_blank" rel="noreferrer">
            prompts/
          </a>
          .
        </p>
      </section>
    </main>
  );
}
