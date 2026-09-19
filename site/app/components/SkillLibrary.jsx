"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

// The catalogue. Built to stay readable at fifty skills, not two: shelves
// with counts, one compact row per skill, and a filter over the lot. The UX
// benchmark the owner named is Clerk, whose docs index carries a grouped
// left-hand list, a search field at the top of it, and one plain sentence per
// entry. That structure is what is borrowed here, in black and white.
//
// Row anatomy, rebuilt for volume on the owner's order of 2026-09-18. At rest
// a skill is ONE line: its name, its version, its source count, and nothing
// else. Everything a row used to say at rest, the description and the papers
// and the routing text and the entitlement, now lives behind the disclosure,
// because fifty rows saying all of it is a page nobody reaches the bottom of.
//
// The pricing call to action appears once, at the end of the page, rather
// than once per row. Fifty identical buttons is not an offer, it is noise;
// an open row still states the entitlement in words, so a reader never has to
// guess what comes with the paid plan.
//
// A row is a native <details>, so it opens on click, on Enter, and on Space,
// it is announced as a disclosure, and it works before the JavaScript lands.

function matches(skill, shelfName, q) {
  if (!q) return true;
  const hay = `${skill.name} ${skill.routing} ${shelfName}`.toLowerCase();
  return q
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((word) => hay.includes(word));
}

function SkillRow({ skill, entitled }) {
  const s = skill;
  return (
    <details className="skill-row">
      <summary className="skill-line">
        <span className="skill-line-name">{s.name}</span>
        <span className="skill-line-meta">
          <span>v{s.version}</span>
          {s.status && s.status !== "active" && <span>{s.status}</span>}
          <span>
            {s.papers.length} {s.papers.length === 1 ? "source" : "sources"}
          </span>
        </span>
      </summary>
      <div className="skill-panel">
        <div className="skill-panel-in">
          <p className="skill-row-summary">{s.summary}</p>

          <h4 className="skill-detail-head">The papers behind it</h4>
          <ul className="skill-sources">
            {s.papers.map((p) => (
              <li key={p}>{p.split(" — ")[0]}</li>
            ))}
          </ul>

          <h4 className="skill-detail-head">What your agent matches on</h4>
          <p className="skill-routing">{s.routing}</p>

          {entitled ? (
            <article
              className="digest skill-body"
              dangerouslySetInnerHTML={{ __html: s.html }}
            />
          ) : (
            <p className="skill-row-lock">
              The file itself comes with the paid plan.
            </p>
          )}
        </div>
      </div>
    </details>
  );
}

export default function SkillLibrary({ shelves, entitled }) {
  const [q, setQ] = useState("");
  const filtering = q.trim().length > 0;

  const view = useMemo(
    () =>
      shelves
        .map((shelf) => ({
          ...shelf,
          hits: shelf.skills.filter((s) => matches(s, shelf.name, q.trim())),
        }))
        // while filtering, a shelf with no hit is noise rather than
        // information, so only the resting page shows the empty shelves
        .filter((shelf) => (filtering ? shelf.hits.length > 0 : true)),
    [shelves, q, filtering]
  );

  const total = shelves.reduce((n, s) => n + s.skills.length, 0);
  const shown = view.reduce((n, s) => n + s.hits.length, 0);

  return (
    <>
      <div className="lib-controls">
        <label className="lib-filter">
          <span className="sr-only">Filter skills</span>
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Filter skills"
            autoComplete="off"
          />
        </label>
        <p className="lib-count" aria-live="polite">
          {filtering
            ? `${shown} of ${total} ${total === 1 ? "skill" : "skills"}`
            : `${total} ${total === 1 ? "skill" : "skills"} on ${shelves.length} shelves`}
        </p>
      </div>
      {!filtering && (
        <p className="lib-note">
          A shelf fills when the research supports a skill, and not before.
        </p>
      )}

      {shown === 0 && filtering && (
        <div className="lib-empty">
          <p>No skill matches that yet.</p>
          <button type="button" className="pill ghost" onClick={() => setQ("")}>
            Clear the filter
          </button>
        </div>
      )}

      {view.map((shelf) => (
        <section
          key={shelf.id}
          className={shelf.hits.length === 0 ? "shelf is-empty" : "shelf"}
        >
          <div className="shelf-head">
            <h2>{shelf.name}</h2>
            <span className="shelf-count">
              {shelf.hits.length === 0
                ? "none yet"
                : `${shelf.hits.length} ${shelf.hits.length === 1 ? "skill" : "skills"}`}
            </span>
          </div>
          <p className="shelf-blurb">{shelf.blurb}</p>

          {shelf.hits.length > 0 && (
            <div className="shelf-rows">
              {shelf.hits.map((s) => (
                <SkillRow key={s.name} skill={s} entitled={entitled} />
              ))}
            </div>
          )}
        </section>
      ))}

      {/* The one pricing call to action on the page. It sits after the last
          shelf, where a reader has seen what the library holds, rather than
          on all fifty rows. */}
      {shown > 0 && !entitled && (
        <div className="lib-offer">
          <p>
            The catalogue is public. The skill files themselves come with the
            paid plan.
          </p>
          <Link href="/pricing" className="pill ghost">
            See pricing
          </Link>
        </div>
      )}
    </>
  );
}
