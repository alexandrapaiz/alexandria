#!/usr/bin/env python3
"""The four things that make a skill stale, computed rather than noticed.

    python3 tools/skill_triggers.py                     # every trigger measurable offline
    python3 tools/skill_triggers.py --json              # the same, for a script
    python3 tools/skill_triggers.py --live              # NEON_RO_URL: all four
    python3 tools/skill_triggers.py --smoke             # the arithmetic, against fixtures
    python3 tools/skill_triggers.py --snapshot out.json # NEON_RO_URL: the claim-status file

ADR-37, accepted 2026-09-29: "i want skills to self-maintain." The decision
names four triggers and the owner's dispatch of the same day asked for all four
rather than the one that shipped in the first pass.

    1. deprecated   a claim the skill cites is the target of a confident
                    `contradicts` edge, which is what `skills_needing_revision`
                    returns.
    2. refines      a claim the skill cites has gained a `refines` neighbour at
                    confidence >= 0.7 since the skill's own version date, so the
                    procedure the skill teaches has a newer and narrower form.
    3. citations    a cited paper's citation count moved by more than 2x, or by
                    20 or more, between the last two checks of the slow loop, so
                    the skill's weight in the library is stale in either
                    direction.
    4. eval         the skill's last eval regressed on the current subject model,
                    or the subject model in the budget table has moved under it,
                    so the published number describes a model nobody runs.

Each one produces a record, each record renders one line for
`docs/research/reading-queue.md`, and every line carries a stable `key:` so a
skill that waits a week for its revision does not collect seven identical lines.
`pipeline/skill_revision.py` is the daily job that writes them and dispatches the
skill seat once a day with the list.

## Two of the four need no database, and that is deliberate

Triggers 1 to 3 read the corpus, so they run where the `neon` secret is, which
is Modal. Trigger 4 reads `skills/<slug>/evals/results.json` and the budget
table, both of which are files in this repository, so it runs anywhere including
CI. Splitting them means the half that a person can check from a checkout is
checkable from a checkout, and the run always says which half it measured.

## What a floor is for

Trigger 3 has two rules and a floor. The ratio rule ignores counts below
`RATIO_FLOOR` because 1 citation to 3 is a 3x move and means nothing; the
absolute rule has no floor because 20 citations is 20 citations at any size.
Both directions count: a paper the field stopped citing is as much a reason to
re-weigh a skill as one it started citing, and ADR-37 says "up or down".

## The one thing a queue line must never carry

`pipeline/reading_queue.py` treats any `arxiv:<id>` in a queue line as a paper
to fetch and puts it at the front of distill's drain. Trigger 3's evidence is
about a paper the corpus already holds, so these lines name papers by url and
title and never by `arxiv:` id. `tests/test_skill_triggers.py` asserts that
every line this module can produce parses as zero papers to fetch.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import skill_eval                          # noqa: E402
import skill_registrar as registrar        # noqa: E402

# ADR-37's own number, and the same one `deprecated_claims` uses for a
# contradiction. An edge the interpreter was not confident about is not evidence
# that a procedure has a newer form.
REFINES_MIN_CONFIDENCE = 0.7

# Trigger 3's two rules. `RATIO` is a multiple of the earlier count in either
# direction; `ABSOLUTE` is a difference in citations.
CITATION_RATIO = 2.0
CITATION_ABSOLUTE = 20
RATIO_FLOOR = 5

TRIGGERS = ("deprecated", "refines", "citations", "eval")

# What each trigger is called in a queue line and in a dispatch, in the words a
# reader who has not read this file would use.
LABELS = {
    "deprecated": "a cited claim is deprecated",
    "refines": "a cited claim has a newer, narrower form",
    "citations": "a cited paper's citation count moved sharply",
    "eval": "the eval no longer supports the published number",
}


# --------------------------------------------------------------- the records

def record(trigger: str, skill_path: str, key: str, evidence: str,
           detail: dict | None = None) -> dict:
    """One reason one skill needs a maintenance pass.

    `key` is the dedupe identity and it appears verbatim in the queue line, so
    idempotence is a substring test against the file rather than a second store
    that can disagree with it.
    """
    if trigger not in TRIGGERS:
        raise ValueError(f"{trigger!r} is not one of {', '.join(TRIGGERS)}")
    return {"trigger": trigger, "skill_path": skill_path,
            "skill": skill_path.rsplit("/", 1)[-1], "key": key,
            "evidence": " ".join(evidence.split()), "detail": detail or {}}


def truncate(text: str, limit: int = 240) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def deprecated_record(skill_path: str, claim_id: int, claim: str) -> dict:
    return record(
        "deprecated", skill_path, f"{skill_path}#claim-{claim_id}-deprecated",
        f"{skill_path} cites claim {claim_id}, which the graph now marks "
        f"deprecated. The claim says: “{truncate(claim)}”. Read what "
        "contradicts it, then either revise the skill or retire it with the "
        "reason",
        {"claim_id": claim_id})


def refines_record(skill_path: str, claim_id: int, edge: dict,
                   since: str, since_from: str) -> dict:
    return record(
        "refines", skill_path,
        f"{skill_path}#claim-{claim_id}-refined-by-{edge['refined_by']}",
        f"{skill_path} cites claim {claim_id}, and claim {edge['refined_by']} "
        f"now refines it at confidence {float(edge.get('confidence') or 0):.2f}, "
        f"recorded {edge.get('created_at', '')} and so after this version's "
        f"date of {since} ({since_from}). The newer claim says: "
        f"“{truncate(edge.get('claim') or '')}”, from "
        f"{truncate(edge.get('paper_title') or 'a paper the corpus holds', 120)}. "
        "Read it in full and decide whether the skill's procedure is the older "
        "form",
        {"claim_id": claim_id, "refined_by": edge["refined_by"],
         "confidence": edge.get("confidence")})


def paper_reference(row: dict) -> str:
    """How a paper is named in a queue line. Never as `arxiv:<id>`.

    `pipeline/reading_queue.py` would read that as a fetch request and front-load
    distill's drain with a paper the corpus already has.
    """
    url = (row.get("paper_url") or "").strip()
    title = truncate(row.get("paper_title") or "", 120)
    if url and title:
        return f"{title} ({url})"
    return title or url or (row.get("paper_id") or "").replace("arxiv:", "arXiv ")


def citations_record(skill_path: str, row: dict) -> dict:
    before, now = int(row["citations_before"]), int(row["citations_now"])
    checked = str(row.get("checked_at") or "")[:10]
    paper_key = (row.get("paper_id") or "").replace("arxiv:", "")
    direction = "up" if now > before else "down"
    return record(
        "citations", skill_path,
        f"{skill_path}#paper-{paper_key}-citations-{checked}",
        f"{skill_path} cites claim {row['claim_id']}, from "
        f"{paper_reference(row)}. Its citation count moved {direction} from "
        f"{before} to {now} between the slow loop's last two checks "
        f"({str(row.get('checked_before') or '')[:10]} to {checked}), which is "
        f"{movement_reason(before, now)}. Re-weigh what the skill leans on this "
        "paper for",
        {"claim_id": row["claim_id"], "paper_id": row.get("paper_id"),
         "citations_before": before, "citations_now": now})


def eval_record(skill_path: str, key: str, evidence: str,
                detail: dict) -> dict:
    return record("eval", skill_path, key, evidence, detail)


# --------------------------------------------------------------- trigger 1

def deprecated_records(rows: list[dict]) -> list[dict]:
    """`skills_needing_revision`'s rows, as records. One per (skill, claim)."""
    out, seen = [], set()
    for row in rows:
        rec = deprecated_record(row["skill_path"], row["deprecated_claim_id"],
                                row.get("deprecated_claim") or "")
        if rec["key"] in seen:
            continue
        seen.add(rec["key"])
        out.append(rec)
    return out


# --------------------------------------------------------------- trigger 2

def version_date(skill_dir: pathlib.Path, row) -> tuple[str, str]:
    """(date, where it came from) for the version now on main.

    ADR-37 asks for edges recorded "since the skill's version date", and a
    version has no date of its own in the frontmatter. Two places do carry one,
    in this order of preference:

    1. `evals/results.json`'s history entry for this version, which is the date
       the version was last measured. That is the strongest answer, because it
       is the date the published number was produced.
    2. `provenance.extracted`, the date the skill's claims were pulled out of
       the corpus. Every skill in the library has one.

    An empty answer is honest and it means this trigger cannot be computed for
    that skill, which the run says rather than defaulting to the epoch and
    firing on every edge the graph has ever held.
    """
    doc = read_results(skill_dir)
    version = str(getattr(row, "version", "") or "")
    for entry in reversed(history_entries(doc)):
        if str(entry.get("version") or "") == version and entry.get("date"):
            return str(entry["date"])[:10], "the date this version was measured"
    extracted = str(getattr(row, "extracted", "") or "")
    if extracted:
        return extracted[:10], "provenance.extracted"
    return "", ""


def refines_records(rows_by_path: dict, edges: list[dict],
                    dates: dict[str, tuple[str, str]]) -> list[dict]:
    """The refines edges that landed after the skill that cites their target.

    One query fetches every qualifying edge since the oldest version date in the
    library and this filters per skill, because a per-skill query would be one
    round trip per skill for a job that runs daily.
    """
    out, seen = [], set()
    for path, row in sorted(rows_by_path.items()):
        since, source = dates.get(path, ("", ""))
        if not since:
            continue
        cited = set(row.claim_ids)
        for edge in edges:
            if edge["claim_id"] not in cited:
                continue
            if float(edge.get("confidence") or 0) < REFINES_MIN_CONFIDENCE:
                continue
            when = str(edge.get("created_at") or "")[:10]
            if when and when < since:
                continue
            rec = refines_record(path, edge["claim_id"], edge, since, source)
            if rec["key"] in seen:
                continue
            seen.add(rec["key"])
            out.append(rec)
    return out


# --------------------------------------------------------------- trigger 3

def moved(before: int, now: int) -> bool:
    """Did this paper's citation count move enough to matter.

    Two rules, either sufficient, both directions. The ratio needs a floor
    because 1 to 3 is a 3x move on noise; MiniLM-class arithmetic is not the
    problem here, small integers are.
    """
    if abs(now - before) >= CITATION_ABSOLUTE:
        return True
    if max(before, now) < RATIO_FLOOR:
        return False
    if before == 0:
        return now >= RATIO_FLOOR
    return now / before >= CITATION_RATIO or before / max(now, 1) >= CITATION_RATIO


def movement_reason(before: int, now: int) -> str:
    """Which rule fired, in the words the queue line prints."""
    reasons = []
    if abs(now - before) >= CITATION_ABSOLUTE:
        reasons.append(f"a move of {abs(now - before)} citations, at or past "
                       f"the {CITATION_ABSOLUTE} the trigger names")
    if max(before, now) >= RATIO_FLOOR:
        ratio = (now / before) if before else float(now)
        inverse = (before / now) if now else float(before)
        if max(ratio, inverse) >= CITATION_RATIO:
            reasons.append(f"a {max(ratio, inverse):.1f}x move, past the "
                           f"{CITATION_RATIO:.0f}x the trigger names")
    return " and ".join(reasons) or "a move below both thresholds"


def citation_records(claims_by_skill: dict[str, set], rows: list[dict]
                     ) -> list[dict]:
    out, seen = [], set()
    for path in sorted(claims_by_skill):
        cited = claims_by_skill[path]
        for row in rows:
            if row["claim_id"] not in cited:
                continue
            if not moved(int(row["citations_before"]), int(row["citations_now"])):
                continue
            rec = citations_record(path, row)
            if rec["key"] in seen:
                continue
            seen.add(rec["key"])
            out.append(rec)
    return out


# --------------------------------------------------------------- trigger 4

def read_results(skill_dir: pathlib.Path) -> dict:
    """`evals/results.json`, or an empty dict. A corrupt file is not a crash."""
    path = skill_dir / "evals" / "results.json"
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return doc if isinstance(doc, dict) else {}


# The record's reader, and the shape of one entry, both defined where the
# record is written. `tools/skill_eval.py` is the only thing that writes
# `history`, the two aliases below are that file's own functions, and this seat
# has filed four incidents in a week about one format being read by two
# implementations that disagree. One more reason this direction and not the
# other: `pipeline/skill_revision.py`'s Modal image carries `skill_eval.py` and
# does not carry this file, so a reviewer inside that image can reach the reader
# only if it lives there.
history_entries = skill_eval.history_entries
summary_entry = skill_eval.summary_entry
ENTRY_FIELDS = skill_eval.ENTRY_FIELDS


def regression(history: list[dict], subject: str) -> str:
    """Why the last eval no longer supports the published number, or "".

    The same comparison `tools/skill_eval.py` gate uses, read from the history
    rather than from two files: a delta below the previous version's own lower
    bound, on the same subject model, is a regression. A verdict that is not a
    gain is also one, because the number on the page claims a gain.
    """
    if not history:
        return ""
    latest = history[-1]
    if str(latest.get("subject_model") or "") != subject:
        return ""
    verdict = str(latest.get("verdict") or "")
    if verdict and not verdict.startswith("gain"):
        return (f"its last eval, on {latest.get('date')}, returned "
                f"{verdict!r} on {subject}")
    if verdict == "gain too small to matter":
        return (f"its last eval, on {latest.get('date')}, found a gain too "
                f"small to matter on {subject}")
    same = [e for e in history
            if str(e.get("subject_model") or "") == subject]
    if len(same) < 2:
        return ""
    previous, latest = same[-2], same[-1]
    before = (previous.get("delta") or {}).get("mean")
    spread = (previous.get("delta") or {}).get("ci95") or [None, None]
    now = (latest.get("delta") or {}).get("mean")
    if before is None or now is None or spread[0] is None:
        return ""
    floor = min(float(spread[0]), float(before))
    if float(now) < floor:
        return (f"its delta fell from {float(before):+.2f} to {float(now):+.2f} "
                f"between versions {previous.get('version')} and "
                f"{latest.get('version')}, below the earlier result's own lower "
                f"bound of {floor:+.2f}, both on {subject}")
    return ""


def eval_records(skill_path: str, doc: dict, subject: str) -> list[dict]:
    """Trigger 4, from files only: a regression, or a subject that moved."""
    history = history_entries(doc)
    if not history:
        return []          # unmeasured is the eval harness's finding, not this one
    latest = history[-1]
    measured_on = str(latest.get("subject_model") or "")
    out = []
    if measured_on and measured_on != subject:
        out.append(eval_record(
            skill_path, f"{skill_path}#subject-{subject}",
            f"{skill_path}'s published result was measured on {measured_on} on "
            f"{latest.get('date')}, and the subject model for this skill is now "
            f"{subject}. Re-run the eval on the new subject: a delta measured "
            "on a model nobody runs is not a receipt",
            {"measured_on": measured_on, "subject": subject}))
        return out          # one dispatch asks for one re-run, not two
    why = regression(history, subject)
    if why:
        out.append(eval_record(
            skill_path, f"{skill_path}#eval-{latest.get('date')}",
            f"{skill_path} is a finding rather than a pass: {why}. ADR-36 says "
            "such a skill is revised or retired with the numbers",
            {"verdict": latest.get("verdict"), "subject": subject}))
    return out


def subject_for(slug: str) -> str:
    """The subject model this skill's eval is pre-registered on.

    The suite's own `policy.subject` wins, because ADR-36 pre-registers the
    policy in the file. `tools/skill_eval.py`'s default, which comes from
    `pipeline/budget.py`'s table, is the answer for a suite that names none.
    """

    try:
        spec, problems = skill_eval.load_tasks(slug)
    except Exception:
        return skill_eval.DEFAULT_SUBJECT
    if spec and not problems:
        named = (spec.get("policy") or {}).get("subject")
        if named:
            return str(named)
    return skill_eval.DEFAULT_SUBJECT


# --------------------------------------------------------------- the queue

def line(rec: dict, today: str) -> str:
    """One checklist line for `docs/research/reading-queue.md`.

    The format that file documents is `- [ ] <what> — why — asked by
    skills/<slug> — YYYY-MM-DD`, and the `key:` segment is this module's
    addition: it is the identity the dedupe reads back.
    """
    return (f"- [ ] Revision ({rec['trigger']}): {rec['evidence']} "
            f"— key: {rec['key']} — asked by {rec['skill_path']} "
            f"— {today}")


def block(records: list[dict], today: str) -> str:
    """The section appended to the queue, heading and all."""
    counts = {}
    for rec in records:
        counts[rec["trigger"]] = counts.get(rec["trigger"], 0) + 1
    named = ", ".join(f"{n} {LABELS[t]}" for t, n in
                      sorted(counts.items(), key=lambda kv: TRIGGERS.index(kv[0])))
    lines = [f"\n## Queued {today} by pipeline/skill_revision.py\n",
             "Every line below is a skill whose ground moved under it, found by "
             "the four triggers ADR-37 names: " + named + ". A revision is the "
             "skill seat's first job, ahead of new skills. The `key:` on each "
             "line is what stops the same finding being queued twice; leave it "
             "in place when you strike the line.\n"]
    for rec in records:
        lines.append(line(rec, today))
    return "\n".join(lines) + "\n"


def carried(queue_text: str, rec: dict) -> bool:
    """Is this finding already in the file, struck or not.

    A line struck with `[x]` still counts: the reading has been done. The match
    is on the key rather than the whole line, because the evidence text may have
    been edited by whoever struck it.
    """
    if rec["key"] in queue_text:
        return True
    # The first pass of this job, 2026-09-30, wrote deprecated lines with no key.
    # Nothing on main carries one today, and this costs one substring test.
    if rec["trigger"] == "deprecated":
        claim_id = rec["detail"].get("claim_id")
        legacy = f"{rec['skill_path']} cites claim {claim_id},"
        if claim_id is not None and legacy in queue_text:
            return True
    return False


def fresh(queue_text: str, records: list[dict]) -> list[dict]:
    """The records this file does not already carry, deduped against itself."""
    out, seen = [], set()
    for rec in records:
        if rec["key"] in seen or carried(queue_text, rec):
            continue
        seen.add(rec["key"])
        out.append(rec)
    return out


# --------------------------------------------------------------- the snapshot

def ranges(ids: list[int]) -> list[list[int]]:
    """Consecutive ids as [start, end] pairs.

    `claims.id` is a bigserial, so the live set is one range plus whatever has
    been deleted. Storing the ranges rather than the ids keeps the snapshot a
    few hundred bytes instead of a few hundred kilobytes, on a file that is
    rewritten daily.
    """
    out: list[list[int]] = []
    for value in sorted(set(int(i) for i in ids)):
        if out and value == out[-1][1] + 1:
            out[-1][1] = value
        else:
            out.append([value, value])
    return out


def in_ranges(claim_id: int, spans: list) -> bool:
    return any(int(lo) <= int(claim_id) <= int(hi) for lo, hi in spans)


def snapshot(claim_ranges: list, deprecated: list[int], today: str) -> dict:
    return {"contract": 1, "generated_at": today,
            "written_by": "pipeline/skill_revision.py",
            "claim_id_ranges": claim_ranges,
            "deprecated_claim_ids": sorted(set(int(i) for i in deprecated)),
            "what_this_is": (
                "Which claim ids exist in the corpus and which of them are "
                "deprecated, as of generated_at. tools/skill_gate.py reads it "
                "when it has no database credential, which is every run in "
                "GitHub Actions. A snapshot older than the gate's limit is a "
                "failing gate, never a passing one.")}


def snapshot_problems(doc: dict, today: str, max_age_days: int) -> list[str]:
    """Why this snapshot cannot be trusted to answer for the graph today."""
    if not doc:
        return ["there is no claim-status snapshot in the repository, so "
                "whether a cited claim exists and is live could not be "
                "measured here"]
    stamp = str(doc.get("generated_at") or "")[:10]
    if not stamp:
        return ["the claim-status snapshot carries no generated_at, so its age "
                "is unknown and its answer cannot be trusted"]
    try:
        age = (dt.date.fromisoformat(today) - dt.date.fromisoformat(stamp)).days
    except ValueError:
        return [f"the claim-status snapshot's generated_at ({stamp}) is not a "
                "date"]
    if age > max_age_days:
        return [f"the claim-status snapshot was written {stamp}, {age} days "
                f"ago, past the {max_age_days} this gate allows. The daily job "
                "that refreshes it has not run, so the graph may have moved "
                "since"]
    return []


def claim_problems(claim_ids: list[int], doc: dict) -> list[str]:
    """Which cited claims do not exist, and which are deprecated."""
    problems = []
    spans = doc.get("claim_id_ranges") or []
    deprecated = set(int(i) for i in (doc.get("deprecated_claim_ids") or []))
    for claim_id in claim_ids:
        if spans and not in_ranges(claim_id, spans):
            problems.append(
                f"claim {claim_id} is cited by the provenance block and does "
                "not exist in the corpus, so the skill's receipt points at "
                "nothing")
        if claim_id in deprecated:
            problems.append(
                f"claim {claim_id} is cited by the provenance block and the "
                "graph marks it deprecated, which is trigger 1 rather than a "
                "revision that may merge")
    return problems


# --------------------------------------------------------------- the database

QUERIES = {
    # Trigger 2. One query for the whole library, filtered per skill in Python:
    # a per-skill round trip would be one query per skill on a daily job.
    "refines_since": """
        select l.to_claim, l.from_claim, l.confidence, l.created_at,
               nc.claim, nc.paper_id, np.title, np.url
        from claim_links l
        join claims nc on nc.id = l.from_claim
        join papers np on np.id = nc.paper_id
        where l.relation = 'refines'
          and coalesce(l.confidence, 0) >= %s
          and l.created_at >= %s
        order by l.created_at
    """,
    # Trigger 3. The same two-row window weekly.py's movers section uses, which
    # is what "the slow loop's window" means: between the last two checks.
    "citation_moves": """
        with checks as (
            select paper_id, citations, checked_at,
                   row_number() over (partition by paper_id
                                      order by checked_at desc) as rn
            from citation_log
        )
        select c.id, c.paper_id, p.title, p.url,
               prev.citations, latest.citations,
               prev.checked_at, latest.checked_at
        from claims c
        join papers p on p.id = c.paper_id
        join checks latest on latest.paper_id = c.paper_id and latest.rn = 1
        join checks prev on prev.paper_id = c.paper_id and prev.rn = 2
    """,
    # The gate's snapshot. Ranges are computed in Python from the live ids
    # because a gap in a bigserial is not something SQL should have to explain.
    "claim_ids": "select id from claims order by id",
    "deprecated_ids": "select id from deprecated_claims order by id",
}


def refines_edges(conn, since: str,
                  min_confidence: float = REFINES_MIN_CONFIDENCE) -> list[dict]:
    rows = conn.execute(QUERIES["refines_since"], (min_confidence, since)).fetchall()
    return [{"claim_id": to_claim, "refined_by": from_claim,
             "confidence": confidence,
             "created_at": created_at.date().isoformat() if created_at else "",
             "claim": claim, "paper_id": paper_id, "paper_title": title,
             "paper_url": url}
            for (to_claim, from_claim, confidence, created_at, claim, paper_id,
                 title, url) in rows]


def citation_moves(conn) -> list[dict]:
    rows = conn.execute(QUERIES["citation_moves"]).fetchall()
    return [{"claim_id": claim_id, "paper_id": paper_id, "paper_title": title,
             "paper_url": url, "citations_before": before, "citations_now": now,
             "checked_before": before_at.date().isoformat() if before_at else "",
             "checked_at": at.date().isoformat() if at else ""}
            for (claim_id, paper_id, title, url, before, now, before_at, at)
            in rows]


def claim_status(conn, today: str) -> dict:
    ids = [r[0] for r in conn.execute(QUERIES["claim_ids"]).fetchall()]
    dep = [r[0] for r in conn.execute(QUERIES["deprecated_ids"]).fetchall()]
    return snapshot(ranges(ids), dep, today)


# --------------------------------------------------------------- the run

def offline(skills_dir: pathlib.Path | None = None,
            today: str = "") -> tuple[list[dict], list[str]]:
    """Trigger 4 for every skill, plus one line per thing that is unmeasurable.

    No database, no network, no model. This is the half of the loop a person can
    run from a checkout and the half CI can run on a pull request.
    """
    today = today or dt.date.today().isoformat()
    rows, problems = registrar.read_skills(skills_dir)
    records = []
    for row in rows:
        directory = (skills_dir or registrar.SKILLS_DIR) / row.slug
        doc = read_results(directory)
        if not doc:
            problems.append(
                f"{row.path} has no readable evals/results.json, so trigger 4 "
                "could not be computed for it. ADR-36 makes such a skill draft "
                "rather than active.")
            continue
        records += eval_records(row.path, doc, subject_for(row.slug))
    return records, problems


def live(conn, skills_dir: pathlib.Path | None = None, today: str = ""
         ) -> tuple[list[dict], list[str]]:
    """All four triggers. Needs a read-only connection to the corpus."""
    today = today or dt.date.today().isoformat()
    rows, problems = registrar.read_skills(skills_dir)
    by_path = {row.path: row for row in rows}
    dates = {row.path: version_date((skills_dir or registrar.SKILLS_DIR)
                                    / row.slug, row) for row in rows}
    for path, (since, _) in sorted(dates.items()):
        if not since:
            problems.append(
                f"{path} carries no version date that could be read from its "
                "results history or its provenance block, so trigger 2 was not "
                "computed for it.")

    records = deprecated_records(registrar.revisions(conn))

    known = [since for since, _ in dates.values() if since]
    if known:
        edges = refines_edges(conn, min(known))
        records += refines_records(by_path, edges, dates)

    cited = {row.path: set(row.claim_ids) for row in rows}
    records += citation_records(cited, citation_moves(conn))

    offline_records, offline_problems = offline(skills_dir, today)
    return records + offline_records, problems + offline_problems


def render(records: list[dict], problems: list[str], today: str) -> str:
    lines = []
    for trigger in TRIGGERS:
        hits = [r for r in records if r["trigger"] == trigger]
        lines.append(f"{trigger:12} {len(hits)}  ({LABELS[trigger]})")
        for rec in hits:
            lines.append(f"  {rec['skill_path']}: {rec['evidence'][:150]}")
    for problem in problems:
        lines.append(f"unmeasured: {problem}")
    lines.append(f"{len(records)} triggers on {today}")
    return "\n".join(lines)


SMOKE = {
    "edges": [{"claim_id": 199, "refined_by": 421, "confidence": 0.82,
               "created_at": "2026-09-28", "claim": "the narrower form",
               "paper_id": "arxiv:2609.09134", "paper_title": "A newer paper",
               "paper_url": "arxiv.org/abs/2609.09134"},
              {"claim_id": 199, "refined_by": 422, "confidence": 0.4,
               "created_at": "2026-09-28", "claim": "an unconfident edge",
               "paper_id": "arxiv:2609.09135", "paper_title": "Another",
               "paper_url": "arxiv.org/abs/2609.09135"},
              {"claim_id": 199, "refined_by": 423, "confidence": 0.9,
               "created_at": "2026-09-01", "claim": "older than the version",
               "paper_id": "arxiv:2609.09136", "paper_title": "An older one",
               "paper_url": "arxiv.org/abs/2609.09136"}],
    "moves": [{"claim_id": 200, "paper_id": "arxiv:2609.08572",
               "paper_title": "A paper the field found",
               "paper_url": "arxiv.org/abs/2609.08572",
               "citations_before": 4, "citations_now": 40,
               "checked_before": "2026-09-16", "checked_at": "2026-09-30"},
              {"claim_id": 201, "paper_id": "arxiv:2609.03254",
               "paper_title": "A paper that moved on noise",
               "paper_url": "arxiv.org/abs/2609.03254",
               "citations_before": 1, "citations_now": 3,
               "checked_before": "2026-09-16", "checked_at": "2026-09-30"}],
    "history": [{"version": "1", "date": "2026-09-20",
                 "subject_model": "kimi-k2.6", "verdict": "gain",
                 "delta": {"mean": 0.41, "ci95": [0.2, 0.6]}},
                {"version": "2", "date": "2026-09-29",
                 "subject_model": "kimi-k2.6", "verdict": "gain",
                 "delta": {"mean": 0.05, "ci95": [-0.1, 0.2]}}],
}


def smoke() -> int:
    """The arithmetic of all four triggers, against fixtures. No network."""
    class Row:
        path = "skills/harness-engineering"
        slug = "harness-engineering"
        claim_ids = [199, 200, 201]
        version = "2"

    row = Row()
    by_path = {row.path: row}
    dates = {row.path: ("2026-09-15", "provenance.extracted")}

    refines = refines_records(by_path, SMOKE["edges"], dates)
    citations = citation_records({row.path: set(row.claim_ids)}, SMOKE["moves"])
    evals = eval_records(row.path, {"history": SMOKE["history"]}, "kimi-k2.6")
    subject = eval_records(row.path, {"history": SMOKE["history"]}, "kimi-k3")
    records = deprecated_records([{"skill_path": row.path,
                                   "deprecated_claim_id": 85,
                                   "deprecated_claim": "the older result"}]) \
        + refines + citations + evals
    today = dt.date.today().isoformat()
    print(render(records, [], today))
    print()
    print(block(records, today))

    text = block(records, today)
    checks = {
        "one refines edge fires, the unconfident and the older one do not":
            [r["detail"]["refined_by"] for r in refines] == [421],
        "the 4-to-40 move fires and the 1-to-3 move does not":
            [r["detail"]["citations_now"] for r in citations] == [40],
        "a delta below the previous lower bound is a regression":
            len(evals) == 1 and "fell from" in evals[0]["evidence"],
        "a subject model that moved asks for a re-run, not a retirement":
            len(subject) == 1 and "kimi-k3" in subject[0]["evidence"],
        "every record is deduped by key on a second pass":
            fresh(text, records) == [],
        "a struck line still counts as carried":
            fresh(text.replace("- [ ]", "- [x]"), records) == [],
        "no line asks distill to fetch a paper the corpus already has":
            _no_fetch_requests(text),
    }
    for label, ok in checks.items():
        print(("ok:   " if ok else "FAIL: ") + label)
    return 0 if all(checks.values()) else 1


def _no_fetch_requests(text: str) -> bool:
    sys.path.insert(0, str(ROOT / "pipeline"))
    import reading_queue

    return reading_queue.parse(text) == []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--live", action="store_true",
                    help="all four triggers; needs NEON_RO_URL or DATABASE_URL")
    ap.add_argument("--snapshot", metavar="PATH",
                    help="write the claim-status snapshot the gate reads")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.smoke:
        return smoke()

    today = dt.date.today().isoformat()
    if args.live or args.snapshot:
        conn = registrar.connect(writable=False)
        if conn is None:
            return 2
        with conn:
            if args.snapshot:
                doc = claim_status(conn, today)
                pathlib.Path(args.snapshot).write_text(
                    json.dumps(doc, indent=2, sort_keys=True) + "\n")
                print(f"{len(doc['deprecated_claim_ids'])} deprecated of "
                      f"{sum(hi - lo + 1 for lo, hi in doc['claim_id_ranges'])} "
                      f"claims, written to {args.snapshot}")
                if not args.live:
                    return 0
            records, problems = live(conn, today=today)
    else:
        records, problems = offline(today=today)
        problems.append("triggers 1, 2 and 3 read the corpus and this run had "
                        "no database credential, so only trigger 4 was "
                        "measured. pipeline/skill_revision.py runs all four.")

    print(json.dumps({"date": today, "records": records,
                      "unmeasured": problems}, indent=2, sort_keys=True)
          if args.json else render(records, problems, today))
    # Same three states as the registrar and the graph audit: a trigger is a
    # finding, something unmeasurable is unknown, and neither is ok.
    if records:
        return 1
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
