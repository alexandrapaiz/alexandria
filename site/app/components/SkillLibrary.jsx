"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

// The catalogue. Built to stay readable at fifty skills, not two: shelves
// with counts, one compact row per skill, and a filter over the lot. The UX
// benchmark the owner named is Clerk, whose docs index carries a grouped
// left-hand list, a search field at the top of it, and one plain sentence per
// entry. That structure is what is borrowed here, in black and white.
//
// Every row says both things at once: the sentence a person reads, and,
// behind a disclosure that names whose text it is, the line an agent matches
// on. Same file, two audiences.

function matches(skill, shelfName, q) {
  if (!q) return true;
  const hay = `${skill.name} ${skill.routing} ${shelfName}`.toLowerCase();
  return q
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((word) => hay.includes(word));
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
                <article key={s.name} className="skill-row">
                  <div className="skill-row-head">
                    <h3>{s.name}</h3>
                    <span className="skill-row-meta">
                      <span>v{s.version}</span>
                      {s.status && s.status !== "active" && (
                        <span>{s.status}</span>
                      )}
                      <span>
                        {s.papers.length}{" "}
                        {s.papers.length === 1 ? "source" : "sources"}
                      </span>
                    </span>
                  </div>
                  <p className="skill-row-summary">{s.summary}</p>

                  <div className="skill-row-more">
                    <details>
                      <summary>The papers behind it</summary>
                      <ul className="skill-sources">
                        {s.papers.map((p) => (
                          <li key={p}>{p.split(" — ")[0]}</li>
                        ))}
                      </ul>
                    </details>
                    <details>
                      <summary>What your agent matches on</summary>
                      <p className="skill-routing">{s.routing}</p>
                    </details>
                  </div>

                  {entitled ? (
                    <article
                      className="digest skill-body"
                      dangerouslySetInnerHTML={{ __html: s.html }}
                    />
                  ) : (
                    <div className="skill-row-lock">
                      <span>The file itself comes with the paid plan.</span>
                      <Link href="/pricing" className="pill ghost">
                        See pricing
                      </Link>
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      ))}
    </>
  );
}
