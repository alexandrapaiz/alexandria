import { loadLeftBehind } from "../../lib/left-behind-live.js";
import { claimRef } from "../../lib/left-behind-core.js";

// The Left-Behind Index. Sprint-2026-10-12 item 4, carried from
// sprint-2026-09-28 and sprint-2026-10-05.
//
// PUBLIC, not paywalled, and the decision is vision.md's rather than this
// seat's. §4 priced a $10 digest tier and said the digest must be worth $10
// before a paywall goes up, but §0's amendment of 2026-09-17 supersedes those
// tiers in its own words: the digest is free, full issues, as the acquisition
// engine, and the paid spine is the operational layer at $20. §1 then names
// "left behind" as one of the digest's three kinds of finding, alongside
// trailblazing and matured, and names the `deprecated_claims` view as its
// evidence. So this page is digest content on the free side of the line, and
// the line itself is drawn around the operational layer: the skill library,
// the claim graph, automations.
//
// Two pieces of evidence that this reading is the standing one rather than a
// convenient one. lib/entitlement.js says in its header that "no digest route
// ever calls into this module", and this route does not. And
// pipeline/weekly.py:402 already prints this exact pair, the flagged finding
// against the newer one that contradicts it, inside the weekly issue that
// lib/library/[week] serves free and in full to a signed-out visitor. The
// pair is public today; this page is a second surface over it, not a new
// disclosure.
//
// What is deliberately NOT here. No mention of the claim graph and no link to
// /graph, which is paywalled by the ruling of 2026-09-19 and unlisted until
// its UI is fixed. And no intro paragraph: the writer seat owns the words, the
// frontend seat sets them (owner's division of 2026-09-19), and no approved
// line under docs/voice/ covers this surface. The two state lines below are
// the only prose on the page and they are named in this run's ledger note as
// provisional, pending the writer's round.
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Left behind — library of alexandr.ia",
  description:
    "Findings the library has stopped standing behind, with the newer work that contradicted each one.",
};

// The two states a reader can reach that are not a list, kept in one place
// because they are the lines this page cannot source from an approved file.
// They distinguish an empty index from an unreadable one on purpose: one is a
// fact about the research and the other is a fact about our infrastructure,
// and a page that renders both as emptiness tells a reader the first when the
// truth is the second.
const NOTHING_FLAGGED = "No finding is flagged.";
const UNREADABLE = "The library could not be read.";

export default async function LeftBehind() {
  const index = await loadLeftBehind();

  return (
    <main className="page">
      <p className="page-kicker">Library</p>
      <h1 className="page-title">Left behind</h1>

      {index === null ? (
        <p className="lb-state">{UNREADABLE}</p>
      ) : index.findings.length === 0 ? (
        <p className="lb-state">{NOTHING_FLAGGED}</p>
      ) : (
        <div className="lb-index">
          {/* Column labels, not a table header: the rows below are
              disclosures rather than table rows, so nothing here claims
              table semantics it does not have. They sit on the same declared
              grid as every row, which is what keeps the three fields on three
              x positions down the whole list (ban list entry 30). */}
          <p className="lb-head">
            <span className="lb-ref">Finding</span>
            <span className="lb-claim">What it said</span>
            <span className="lb-flagged">Flagged</span>
          </p>
          {index.findings.map((f) => (
            <Finding key={f.id} finding={f} />
          ))}
        </div>
      )}
    </main>
  );
}

// A row is a native <details>, the same decision SkillLibrary.jsx made and for
// the same reasons: it opens on click, on Enter and on Space, it is announced
// as a disclosure, and it works before the JavaScript lands.
//
// At rest a finding is ONE line: its identifier, what it said, and the date it
// was flagged. Everything else waits behind the disclosure, because ban list
// entry 22 is a list whose every row renders its full description at rest, and
// a claim is two or three sentences long. The volume this is judged at is 50
// findings, not the 22 the database holds today.
function Finding({ finding: f }) {
  return (
    <details className="lb-row">
      <summary className="lb-line">
        <span className="lb-ref">{claimRef(f.id)}</span>
        <span className="lb-claim">{f.claim}</span>
        <span className="lb-flagged">{f.flagged || "—"}</span>
      </summary>
      <div className="lb-panel">
        <div className="lb-panel-in">
          <p className="lb-full">{f.claim}</p>
          {f.paper && <Source label="From" paper={f.paper} />}

          {/* A bare noun, at every count. Taste register: never append
              explanatory subtitles to a heading, and a number is a
              clarification. The blocks below it carry their own count by
              being there. */}
          <h2 className="lb-detail-head">Contradicted by</h2>
          {f.contradictions.map((c) => (
            <dl className="lb-against" key={`${f.id}-${c.id}`}>
              <div>
                <dt>{claimRef(c.id)}</dt>
                <dd>{c.claim}</dd>
              </div>
              {c.paper && (
                <div>
                  <dt>From</dt>
                  <dd>
                    <PaperLink paper={c.paper} />
                  </dd>
                </div>
              )}
              <div>
                <dt>Confidence</dt>
                <dd>{c.confidence == null ? "—" : c.confidence.toFixed(2)}</dd>
              </div>
              <div>
                <dt>Flagged</dt>
                <dd>{c.flagged || "—"}</dd>
              </div>
            </dl>
          ))}
        </div>
      </div>
    </details>
  );
}

function Source({ label, paper }) {
  return (
    <dl className="lb-against">
      <div>
        <dt>{label}</dt>
        <dd>
          <PaperLink paper={paper} />
        </dd>
      </div>
    </dl>
  );
}

function PaperLink({ paper }) {
  const title = paper.title || paper.url;
  if (!paper.url) return <>{title}</>;
  return (
    <a className="lb-paper" href={paper.url}>
      {title}
    </a>
  );
}
