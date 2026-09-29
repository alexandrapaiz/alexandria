#!/usr/bin/env python3
"""Graph audit: what shape is the claim graph actually in.

    python3 tools/graph_audit.py                     # every metric, for a human
    python3 tools/graph_audit.py --json              # the same answer, for a script
    python3 tools/graph_audit.py --sample 40 > sheet.json    # edges to label
    python3 tools/graph_audit.py --labels sheet.json         # precision, from the labels

The owner's directive, verbatim, on 2026-09-18: the knowledge graph "is very
junior and behind and prehistoric and almost like a toy". That is a judgment
about a thing nobody has measured. `claim_links` has existed since the founding
night, it has been written by three different judges under at least two prompts,
and not one number about its quality has ever been produced. So the first step
of the upgrade is not a new relation vocabulary or a graph database. It is an
instrument, because an upgrade whose before-state is an impression can only be
argued about.

`docs/product/graph-quality.md` is the design this file is the first slice of.
It holds the reasoning behind every bound below and the slices that come after.

## What is measured without judgment, and what needs it

Most of what is wrong with a young claim graph is visible in the edges
themselves and needs no reader. A graph where four claims in five have no edge
is a list with a table next to it. A judge that writes 0.9 on every edge has not
scored anything. An edge from a claim to its own sibling in the same paper is a
paper agreeing with itself, which is true, cheap, and worth nothing to a reader.
Every metric in `analyze()` is of that kind: it comes out of SQL, it is
reproducible, and it moves when the graph changes.

Precision does not work that way. Whether `contradicts` on a given pair is
correct is a reading, and the only honest way to get it is to have someone read.
So `--sample` draws edges by a seeded hash, which means the same seed always
draws the same edges and a later run can re-measure the same sample under a new
judge, and writes them out with both claim texts and a `verdict` field left
null. `--labels` reads that file back and reports precision overall, per
relation, and per confidence band. The last of those is calibration: of the
edges this judge called 0.9, how many were right.

## The three states

Same vocabulary as `tools/delivery_health.py`, for the same reason.

    ok        measured, and inside the bound this file sets
    failing   measured, and outside it
    unknown   not measurable from here

`failing` is a finding about the graph, not about the machine. An audit whose
every metric reads `ok` on the first run it is pointed at a real database is an
audit with bounds set too loose to be worth running.

    exit 0    every metric was measured and every one is inside its bound
    exit 1    at least one metric is outside its bound
    exit 2    nothing is outside a bound, and something could not be measured

## What it needs

`DATABASE_URL`, read-only, and `psycopg`. Nothing here writes: every statement
in `QUERIES` is a SELECT, and `tests/test_graph_audit.py` asserts that by
parsing them rather than by trusting this sentence. No seat in this org holds
that credential today, which is the ledger entry of 2026-09-28 and the owner's
to close. Until she does, this command answers `unknown` from a seat sandbox and
runs where the corpus does.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

OK, FAILING, UNKNOWN = "ok", "failing", "unknown"

# pipeline/interpret.py NEIGHBORS. The shortlist a claim is judged against is
# five candidates long, so five is the largest number of distinct neighbors any
# claim can be linked to on the run that interpreted it. A claim sitting exactly
# at that number is a claim whose edge count was decided by a constant in a
# Python file rather than by the corpus, and the share of claims in that state
# is how you find out whether the constant is binding.
SHORTLIST = 5

# Cosine distance under which two claims are treated as saying the same thing
# for the purposes of the dedup probe. Qwen3-Embedding-0.6B puts unrelated
# sentences around 0.4 to 0.8 apart and paraphrases below 0.1; 0.08 is inside
# the paraphrase band with room, so a pair under it is a pair a reader would
# call one claim. This is a probe threshold, not a merge rule: nothing in this
# file writes an edge, and the number that matters is how many such pairs the
# judge never marked.
NEAR_DUPLICATE_DISTANCE = 0.08

# How many claims the dedup probe draws. Each one costs an indexed kNN lookup,
# so this is the only metric whose cost grows with the number, and 200 is enough
# to separate "a few percent" from "a third" while staying under a second.
DEDUP_SAMPLE = 200

# The default seed for both samples. A fixed default is the point: two runs a
# month apart draw the same edges, so the second one measures the judge rather
# than the draw.
SEED = "alexandria"


# --------------------------------------------------------------- the bounds
#
# Each bound is a number with an argument behind it, and the argument is what
# makes the number changeable by the next person. None of these is a guess about
# what the graph currently does, because nobody has run this yet.

BOUNDS = {
    # A claim the interpreter has judged and drawn nothing from is not a
    # failure on its own: a genuinely novel claim has no older neighbor to
    # relate to, and `interpret` already counts those separately. But the whole
    # graph cannot be novel. Above a third, the judge is refusing rather than
    # discriminating, and the product ADR-8 promises (this week's finding
    # against what we already knew) has nothing to stand on.
    "isolated_share": 0.33,
    # The shortlist ceiling. If more than one claim in ten is linked to all five
    # of its candidates, the graph's density is set by NEIGHBORS and not by the
    # corpus, and raising that constant is a cheaper upgrade than any of the
    # ones in the ledger entry.
    "ceiling_share": 0.10,
    # A judge that writes the same confidence on most of its edges has produced
    # a label, not a score, and `deprecated_claims` depends on that score: its
    # gate is confidence >= 0.7. prompts/interpret.md defines the value as a
    # probability and warns about that gate, but anchors it to nothing, so there
    # is no worked pair anywhere saying what separates 0.7 from 0.9. Above 0.6
    # on one value, the gate is a coin the judge has already flipped.
    "modal_confidence_share": 0.60,
    # Two claims from one paper are near-neighbors in embedding space almost by
    # construction, so kNN hands the judge a paper's own siblings before it
    # hands it anything from another paper. Above 40 percent, the graph is
    # mostly papers agreeing with themselves, and the fix is a retrieval fix
    # (exclude same-paper candidates, widen the shortlist) rather than a
    # prompt fix.
    "same_paper_share": 0.40,
    # Near-duplicate pairs the judge did not mark. This is the entity-resolution
    # number: every unmarked pair is one claim counted twice in every total the
    # product prints. A tenth is generous for a first bar.
    "unmarked_duplicate_share": 0.10,
    # The daily cron writes edges every day. Two days with no new edge means it
    # has missed two runs, the same window `tools/delivery_health.py` uses on
    # the corpus tables and for the same reason: one day fires on a late start.
    "edge_stale_days": 2,
}


class Metric:
    """One measurement: a state, a headline a human can act on, its evidence."""

    def __init__(self, name: str, state: str, headline: str,
                 evidence: dict | None = None):
        self.name = name
        self.state = state
        self.headline = headline
        self.evidence = evidence or {}

    def as_dict(self) -> dict:
        return {"metric": self.name, "state": self.state,
                "headline": self.headline, "evidence": self.evidence}


# ---------------------------------------------------------------- the reads
#
# Every one of these is a SELECT. `%s` is psycopg's placeholder; the test suite
# rewrites it to `$1` and parses each statement with libpg_query, so a typo in
# here fails a pull request rather than a production run.

QUERIES = {
    "shape": """
        select
            (select count(*) from claims) as claims,
            (select count(*) from claims where interpreted_at is not null) as interpreted,
            (select count(*) from claims where embedding is null) as unembedded,
            (select count(*) from claim_links) as edges,
            (select count(*) from papers) as papers,
            (select max(created_at) from claim_links) as newest_edge,
            (select min(created_at) from claim_links) as oldest_edge
    """,
    # Out-degree is what the judge drew for a claim; in-degree is what later
    # claims drew about it. A claim with neither is isolated. The two laterals
    # are separate on purpose: one left join would multiply the rows and turn
    # every count below into a count of edges.
    "degrees": """
        select
            count(*)                                          as interpreted,
            count(*) filter (where o.edges = 0)               as no_out,
            count(*) filter (where o.edges = 0 and i.edges = 0) as isolated,
            count(*) filter (where o.neighbors >= %s)         as at_ceiling,
            percentile_disc(0.5) within group (order by o.edges) as median_out,
            percentile_disc(0.9) within group (order by o.edges) as p90_out,
            max(o.edges)                                      as max_out
        from claims c
        cross join lateral (
            select count(*) as edges, count(distinct l.to_claim) as neighbors
            from claim_links l where l.from_claim = c.id
        ) o
        cross join lateral (
            select count(*) as edges from claim_links l where l.to_claim = c.id
        ) i
        where c.interpreted_at is not null
    """,
    "relations": """
        select relation,
               count(*) as edges,
               count(*) filter (where confidence is null) as unscored,
               round(avg(confidence)::numeric, 3) as mean_confidence
        from claim_links
        group by relation
        order by count(*) desc
    """,
    # The histogram is the calibration evidence. A judge that scores gives a
    # spread; a judge that labels gives one tall bar.
    "confidence": """
        select coalesce(round(confidence::numeric, 2)::text, 'null') as value,
               count(*) as edges
        from claim_links
        group by 1
        order by count(*) desc
    """,
    # Every count here should be zero. ADR-10 says from_claim is always the
    # newer claim and ids are a bigserial, so a smaller from_claim is an edge
    # pointing backwards through time. `supports` and `contradicts` on one
    # ordered pair both fit the primary key and cannot both be true.
    "integrity": """
        select
            (select count(*) from claim_links where from_claim = to_claim) as self_edges,
            (select count(*) from claim_links where from_claim < to_claim) as backwards,
            (select count(*) from claim_links where method is null) as unattributed,
            (select count(*) from (
                select from_claim, to_claim from claim_links
                where relation in ('supports', 'contradicts')
                group by from_claim, to_claim
                having count(distinct relation) > 1
            ) both_ways) as self_contradictory
    """,
    # How much of the graph is one paper talking to itself.
    "provenance": """
        select count(*) as edges,
               count(*) filter (where a.paper_id = b.paper_id) as same_paper
        from claim_links l
        join claims a on a.id = l.from_claim
        join claims b on b.id = l.to_claim
    """,
    "contradiction": """
        select
            (select count(*) from claim_links where relation = 'contradicts') as edges,
            (select count(*) from claim_links
              where relation = 'contradicts' and coalesce(confidence, 0) >= 0.7) as confident,
            (select count(distinct to_claim) from claim_links
              where relation = 'contradicts') as claims_contradicted,
            (select count(*) from deprecated_claims) as deprecated
    """,
    # Which judge drew what. `method` is model@prompt_sha, so this is the table
    # you need before any claim that a new prompt draws better edges.
    "judges": """
        select coalesce(method, '(none)') as method,
               count(*) as edges,
               min(created_at) as first_edge,
               max(created_at) as last_edge
        from claim_links
        group by 1
        order by max(created_at) desc
    """,
    # The dedup probe. For a seeded sample of claims, find the single nearest
    # other claim and ask two things: is it close enough that a reader would
    # call them one claim, and did any judge ever say so.
    "dedup": """
        select count(*) as sampled,
               count(*) filter (where n.distance <= %s) as near_duplicates,
               count(*) filter (where n.distance <= %s and not n.marked) as unmarked
        from (
            select id, embedding from claims
            where embedding is not null and interpreted_at is not null
            order by md5(%s || id::text)
            limit %s
        ) s
        cross join lateral (
            select o.id as other,
                   s.embedding <=> o.embedding as distance,
                   exists (
                       select 1 from claim_links l
                       where l.relation = 'duplicates'
                         and ((l.from_claim = s.id and l.to_claim = o.id)
                           or (l.from_claim = o.id and l.to_claim = s.id))
                   ) as marked
            from claims o
            where o.id <> s.id and o.embedding is not null
            order by s.embedding <=> o.embedding
            limit 1
        ) n
    """,
    # The precision worksheet. Ordering by a hash of the seed and the edge's own
    # key makes the draw reproducible without a session setting, so the same
    # seed picks the same edges from a different machine a month later.
    "sample": """
        select l.from_claim, l.to_claim, l.relation, l.confidence, l.method,
               l.created_at, a.claim as from_text, b.claim as to_text,
               a.paper_id as from_paper, b.paper_id as to_paper
        from claim_links l
        join claims a on a.id = l.from_claim
        join claims b on b.id = l.to_claim
        order by md5(%s || l.from_claim::text || '-' || l.to_claim::text
                     || '-' || l.relation)
        limit %s
    """,
}


def _rows(conn, sql: str, params: tuple = ()) -> list[dict]:
    """Run one statement and hand back JSON-able dicts, never driver rows.

    Everything downstream of this function is pure, which is what lets the test
    suite exercise the real analysis on a handwritten snapshot.
    """
    cur = conn.execute(sql, params)
    names = [d[0] for d in cur.description]
    out = []
    for row in cur.fetchall():
        out.append({name: _plain(value) for name, value in zip(names, row)})
    return out


def _plain(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "quantize"):          # Decimal, from round() and avg()
        return float(value)
    return value


def collect(conn, seed: str = SEED) -> dict:
    """Every measurement query, as one JSON-able snapshot."""
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "shape": _rows(conn, QUERIES["shape"])[0],
        "degrees": _rows(conn, QUERIES["degrees"], (SHORTLIST,))[0],
        "relations": _rows(conn, QUERIES["relations"]),
        "confidence": _rows(conn, QUERIES["confidence"]),
        "integrity": _rows(conn, QUERIES["integrity"])[0],
        "provenance": _rows(conn, QUERIES["provenance"])[0],
        "contradiction": _rows(conn, QUERIES["contradiction"])[0],
        "judges": _rows(conn, QUERIES["judges"]),
        "dedup": _rows(conn, QUERIES["dedup"],
                       (NEAR_DUPLICATE_DISTANCE, NEAR_DUPLICATE_DISTANCE,
                        seed, DEDUP_SAMPLE))[0],
    }


# ------------------------------------------------------------- the analysis

def _share(part: int, whole: int) -> float | None:
    """None, never zero, when there is nothing to take a share of."""
    if not whole:
        return None
    return part / whole


def _pct(share: float | None) -> str:
    return "not applicable" if share is None else f"{share * 100:.1f} percent"


def _days_since(stamp: str | None, now: datetime) -> float | None:
    if not stamp:
        return None
    when = datetime.fromisoformat(stamp)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return (now - when).total_seconds() / 86400


def analyze(raw: dict, now: datetime | None = None) -> list[Metric]:
    """The snapshot, read against the bounds. Pure: no database, no clock read.

    `now` is a parameter so freshness is testable and so a snapshot captured
    yesterday can be read as of yesterday.
    """
    now = now or datetime.now(timezone.utc)
    shape, deg = raw["shape"], raw["degrees"]
    out: list[Metric] = []

    edges, claims = shape["edges"], shape["claims"]
    out.append(Metric(
        "size", OK,
        f"{claims} claims over {shape['papers']} papers, {edges} edges, "
        f"{shape['interpreted']} claims interpreted and "
        f"{claims - shape['interpreted']} still queued",
        {"claims": claims, "edges": edges, "papers": shape["papers"],
         "interpreted": shape["interpreted"], "unembedded": shape["unembedded"],
         "edges_per_interpreted_claim":
             round(edges / shape["interpreted"], 2) if shape["interpreted"] else None}))

    isolated = _share(deg["isolated"], deg["interpreted"])
    out.append(Metric(
        "isolation",
        _state(isolated, BOUNDS["isolated_share"]),
        f"{_pct(isolated)} of interpreted claims have no edge in either "
        f"direction, against a bound of {_pct(BOUNDS['isolated_share'])}; "
        f"median out-degree {deg['median_out']}, p90 {deg['p90_out']}, "
        f"max {deg['max_out']}",
        {"isolated": deg["isolated"], "no_outgoing": deg["no_out"],
         "interpreted": deg["interpreted"], "share": isolated,
         "bound": BOUNDS["isolated_share"]}))

    ceiling = _share(deg["at_ceiling"], deg["interpreted"])
    out.append(Metric(
        "shortlist ceiling",
        _state(ceiling, BOUNDS["ceiling_share"]),
        f"{_pct(ceiling)} of interpreted claims are linked to all {SHORTLIST} "
        f"of their candidates, so their edge count was set by "
        f"pipeline/interpret.py NEIGHBORS rather than by the corpus",
        {"at_ceiling": deg["at_ceiling"], "interpreted": deg["interpreted"],
         "shortlist": SHORTLIST, "share": ceiling,
         "bound": BOUNDS["ceiling_share"]}))

    mix = {r["relation"]: r["edges"] for r in raw["relations"]}
    out.append(Metric(
        "relation mix", OK,
        ", ".join(f"{rel} {n} ({_pct(_share(n, edges))})"
                  for rel, n in sorted(mix.items(), key=lambda kv: -kv[1]))
        or "no edges at all",
        {"counts": mix, "detail": raw["relations"]}))

    top = raw["confidence"][0] if raw["confidence"] else None
    modal = _share(top["edges"], edges) if top else None
    out.append(Metric(
        "confidence calibration",
        _state(modal, BOUNDS["modal_confidence_share"]),
        (f"{_pct(modal)} of edges carry the single value {top['value']}, "
         f"across {len(raw['confidence'])} distinct values; deprecated_claims "
         f"gates on confidence >= 0.7" if top else "no edges to score"),
        {"modal_value": top["value"] if top else None,
         "modal_share": modal, "distinct_values": len(raw["confidence"]),
         "histogram": raw["confidence"], "bound": BOUNDS["modal_confidence_share"]}))

    prov = raw["provenance"]
    same = _share(prov["same_paper"], prov["edges"])
    out.append(Metric(
        "same-paper edges",
        _state(same, BOUNDS["same_paper_share"]),
        f"{_pct(same)} of edges join two claims from the same paper, which is "
        f"a paper agreeing with itself and costs a shortlist slot",
        {"same_paper": prov["same_paper"], "edges": prov["edges"],
         "share": same, "bound": BOUNDS["same_paper_share"]}))

    ded = raw["dedup"]
    unmarked = _share(ded["unmarked"], ded["sampled"])
    out.append(Metric(
        "duplicate rate",
        _state(unmarked, BOUNDS["unmarked_duplicate_share"]),
        f"of {ded['sampled']} sampled claims, {ded['near_duplicates']} have a "
        f"nearest neighbor within {NEAR_DUPLICATE_DISTANCE} cosine and "
        f"{ded['unmarked']} of those were never marked `duplicates` by any "
        f"judge, so each is one claim counted twice",
        {"sampled": ded["sampled"], "near_duplicates": ded["near_duplicates"],
         "unmarked": ded["unmarked"], "share": unmarked,
         "distance": NEAR_DUPLICATE_DISTANCE,
         "bound": BOUNDS["unmarked_duplicate_share"]}))

    con = raw["contradiction"]
    out.append(Metric(
        "contradiction coverage", OK,
        f"{con['edges']} contradicts edges over {con['claims_contradicted']} "
        f"claims, {con['confident']} of them at the 0.7 confidence the "
        f"deprecated_claims view requires, which leaves "
        f"{con['deprecated']} claims on the Left-Behind Index",
        dict(con)))

    out.append(_integrity(raw["integrity"]))

    stale = _days_since(shape["newest_edge"], now)
    out.append(Metric(
        "freshness",
        UNKNOWN if stale is None else (
            FAILING if stale > BOUNDS["edge_stale_days"] else OK),
        ("no edge has ever been written" if stale is None else
         f"newest edge is {stale:.1f} days old, against a bound of "
         f"{BOUNDS['edge_stale_days']} days for a daily cron"),
        {"newest_edge": shape["newest_edge"], "oldest_edge": shape["oldest_edge"],
         "days": stale, "bound": BOUNDS["edge_stale_days"]}))

    out.append(Metric(
        "judges", OK,
        "; ".join(f"{j['method']}: {j['edges']} edges, last {j['last_edge']}"
                  for j in raw["judges"]) or "no edges at all",
        {"methods": raw["judges"]}))

    return out


def _state(share: float | None, bound: float) -> str:
    if share is None:
        return UNKNOWN
    return FAILING if share > bound else OK


def _integrity(row: dict) -> Metric:
    """Four counts that are defects at any value above zero."""
    broken = {k: v for k, v in row.items() if v}
    reasons = {
        "self_edges": "a claim related to itself",
        "backwards": "an edge from an older claim to a newer one, which ADR-10 forbids",
        "unattributed": "an edge with no method, so no judge owns it",
        "self_contradictory": "an ordered pair holding both supports and contradicts",
    }
    if not broken:
        return Metric("integrity", OK,
                      "no self-edges, nothing pointing backwards through time, "
                      "every edge attributed to a judge, no pair both supported "
                      "and contradicted", dict(row))
    return Metric("integrity", FAILING,
                  "; ".join(f"{v} {reasons[k]}" for k, v in broken.items()),
                  dict(row))


# ------------------------------------------------------- precision sampling

VERDICTS = ("correct", "wrong", "unsure")


def worksheet(rows: list[dict], seed: str, size: int) -> dict:
    """The sample, as a file a reader fills in.

    `verdict` is null on every edge and the instructions travel with the data,
    because a worksheet that needs a second document to be usable is a worksheet
    that comes back half filled.
    """
    return {
        "drawn_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "requested": size,
        "instructions": (
            "For each edge, read both claims and set `verdict` to one of "
            f"{', '.join(VERDICTS)}. The question is only whether the relation "
            "is true of this pair, never whether the pair is interesting. "
            "Re-run `python3 tools/graph_audit.py --sample N` with the same "
            "seed to draw the same edges under a later judge. Then "
            "`--labels <this file>` for precision."),
        "edges": [dict(row, verdict=None) for row in rows],
    }


def precision(sheet: dict) -> dict:
    """Precision from a filled worksheet: overall, per relation, per band.

    `unsure` is counted and excluded from every denominator. A reader who
    cannot tell is evidence about the claims, not about the edge, and folding
    that into either column would make the number say something it does not.
    """
    labelled = [e for e in sheet.get("edges", []) if e.get("verdict")]
    bad = sorted({e["verdict"] for e in labelled} - set(VERDICTS))
    if bad:
        raise ValueError(
            f"verdict must be one of {', '.join(VERDICTS)}, found: "
            f"{', '.join(bad)}")

    def score(group: list[dict]) -> dict:
        correct = sum(1 for e in group if e["verdict"] == "correct")
        wrong = sum(1 for e in group if e["verdict"] == "wrong")
        unsure = sum(1 for e in group if e["verdict"] == "unsure")
        judged = correct + wrong
        return {"correct": correct, "wrong": wrong, "unsure": unsure,
                "precision": round(correct / judged, 3) if judged else None}

    by_relation = {}
    for rel in sorted({e["relation"] for e in labelled}):
        by_relation[rel] = score([e for e in labelled if e["relation"] == rel])

    by_band = {}
    for band in sorted({_band(e.get("confidence")) for e in labelled}):
        by_band[band] = score([e for e in labelled
                               if _band(e.get("confidence")) == band])

    return {
        "seed": sheet.get("seed"),
        "drawn": len(sheet.get("edges", [])),
        "labelled": len(labelled),
        "overall": score(labelled),
        "by_relation": by_relation,
        # Calibration read straight off the sheet: of the edges the judge
        # called 0.9, how many were right. A band whose precision sits far from
        # its own number is the argument for recalibrating rather than
        # reprompting.
        "by_confidence": by_band,
    }


def _band(confidence) -> str:
    if confidence is None:
        return "unscored"
    low = int(float(confidence) * 10) / 10
    return f"{low:.1f}-{low + 0.1:.1f}"


# ------------------------------------------------------------------- driver

def connect():
    """A connection, or the reason there is not one. Never both."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return None, ("no DATABASE_URL in this environment, so the graph "
                      "cannot be read from here")
    try:
        import psycopg
    except ImportError:
        return None, "psycopg is not installed here (pip install 'psycopg[binary]')"
    try:
        return psycopg.connect(url, connect_timeout=15), None
    except Exception as exc:
        return None, f"DATABASE_URL is set but the connection failed: {exc}"


def exit_code(metrics: list[Metric]) -> int:
    if any(m.state == FAILING for m in metrics):
        return 1
    if any(m.state == UNKNOWN for m in metrics):
        return 2
    return 0


def render(metrics: list[Metric]) -> str:
    mark = {OK: "ok     ", FAILING: "FAILING", UNKNOWN: "unknown"}
    lines = ["Claim graph audit",
             "(docs/product/graph-quality.md holds the argument behind every bound)",
             ""]
    for m in metrics:
        lines.append(f"  {mark[m.state]}  {m.name}")
        lines.append(f"           {m.headline}")
    lines.append("")
    lines.append({
        0: "Every metric was measured and every one is inside its bound.",
        1: "At least one metric is outside its bound. The headline says which.",
        2: ("Nothing is outside a bound, and this is not a clean report: a "
            "metric above could not be measured at all."),
    }[exit_code(metrics)])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON instead of prose")
    parser.add_argument("--sample", type=int, metavar="N",
                        help="draw N edges as a labelling worksheet and stop")
    parser.add_argument("--labels", metavar="FILE",
                        help="read a filled worksheet and report precision")
    parser.add_argument("--seed", default=SEED,
                        help=f"the sampling seed, default {SEED!r}; the same "
                             "seed always draws the same edges")
    parser.add_argument("--snapshot", metavar="FILE",
                        help="read a snapshot written by --json --raw instead "
                             "of a database")
    parser.add_argument("--raw", action="store_true",
                        help="with --json, print the collected snapshot rather "
                             "than the reading of it")
    args = parser.parse_args(argv)

    if args.labels:
        with open(args.labels) as fh:
            print(json.dumps(precision(json.load(fh)), indent=2))
        return 0

    if args.snapshot:
        with open(args.snapshot) as fh:
            raw = json.load(fh)
    else:
        conn, why = connect()
        if conn is None:
            metric = Metric("graph", UNKNOWN, why)
            print(json.dumps(metric.as_dict(), indent=2) if args.json
                  else render([metric]))
            return 2
        with conn:
            if args.sample:
                rows = _rows(conn, QUERIES["sample"], (args.seed, args.sample))
                print(json.dumps(worksheet(rows, args.seed, args.sample),
                                 indent=2, ensure_ascii=False))
                return 0
            raw = collect(conn, args.seed)

    if args.sample:
        print("--sample draws from the database and cannot read a snapshot",
              file=sys.stderr)
        return 2

    metrics = analyze(raw)
    if args.json:
        print(json.dumps(raw if args.raw else
                         {"audited_at": datetime.now(timezone.utc).isoformat(),
                          "metrics": [m.as_dict() for m in metrics]},
                         indent=2, ensure_ascii=False))
    else:
        print(render(metrics))
    return exit_code(metrics)


if __name__ == "__main__":
    sys.exit(main())
