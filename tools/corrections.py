#!/usr/bin/env python3
"""Cluster the corrections before any of them becomes an edit.

    python3 tools/corrections.py --skill harness-engineering
    python3 tools/corrections.py --skill harness-engineering --json
    python3 tools/corrections.py --smoke          # the clustering, on fixtures

ADR-40's refinement item 3, in its own words: "Consumer reports, Ursa's survival
signal and failed-task notes are embedded and clustered; each cluster becomes one
generalized edit; the raw pile is never applied." The claim behind it is C244,
and the failure it names is the one a maintenance loop falls into by default.
Eleven reports each asking for one sentence produce eleven edits, each of which
is individually reasonable, and the skill grows past the point where anything
measurable is attributable to any of it. One cluster is one edit, and the number
of reports behind a cluster is how a reviewer judges whether it is worth making.

## Lexical, not embedded, and that is a stated limitation

The ADR says embedded. This clusters on word overlap instead, for a reason that
is about money rather than taste: this organization funds no embedding endpoint,
and an embedding call per correction on every maintenance run is a recurring cost
the engineer seat may not create (the charter's $0 rule). Jaccard overlap on
content words, single-link agglomerative, is deterministic, costs nothing, needs
no key, and is testable on a laptop.

What it is worse at is the thing embeddings are for: two corrections that say the
same thing in different words land in different clusters. So the output always
names the cluster count beside the correction count, and a run where those two
numbers are equal is the signal that the clustering found nothing and the pile
is being passed through. That reads as a finding rather than as success, and
upgrading to embeddings when a provider is funded is a ledger proposal, not a
silent change.

## What a correction is

Three sources, all already written by somebody else:

- **A consumer report** under `skills/<slug>/reviews/`. ADR-38's format ends in
  "What alexandria should improve", numbered, written as things a seat can do.
  Each numbered item is one correction, and the report's `sections_exercised`
  tells us which part of the skill it is about.
- **A failed task** in `skills/<slug>/evals/results.json`. A task whose with-arm
  did not beat its without-arm is the skill failing to do its job on a question
  the skill seat wrote, which is a correction nobody had to file.
- **Ursa's survival signal** (ADR-39), per section, when it arrives. A section
  no consumer ever acted on is a retirement candidate even when its eval holds,
  and that is a correction of a different kind: remove rather than add.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# How much word overlap makes two corrections the same correction. Jaccard on
# content words, so 0.34 is roughly "a third of the meaningful words are
# shared". Tuned on the one real consumer report in the library and the smoke
# fixtures below; it is a number to revisit with evidence, which is why it is a
# named constant and not a literal in the loop.
SAME_CORRECTION = 0.34

# Words that carry no signal about what a correction is about. Deliberately
# short: a stop list long enough to be clever is a stop list that silently
# merges two unrelated corrections because the only words they did not share
# were on it.
STOPWORDS = frozenset("""
a an the and or but if then than that this these those is are was were be been
being to of in on for with without from by as at it its into about over under
should would could can cannot may might must will shall do does did not no nor
so such when while where which who whom what how why there here more most less
own same too very just also only one two three any each both all some
skill section add says say said make makes making use used using
""".split())

HEADING = re.compile(r"^---\n(.*?)\n---\n", re.S)
NUMBERED = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")
IMPROVE_HEADING = re.compile(r"^#+\s*.*(improve|proposal)", re.I)
OTHER_HEADING = re.compile(r"^#+\s")

SOURCES = ("consumer report", "failed task", "survival")


def words(text: str) -> set[str]:
    """The content words of one correction, lowercased and de-stopped."""
    return {w for w in re.findall(r"[a-z0-9][a-z0-9'-]+", text.lower())
            if w not in STOPWORDS and len(w) > 2}


def overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def frontmatter(text: str) -> dict:
    """The report's frontmatter as flat strings. No YAML dependency.

    Only the three fields this file reads, because a hand-rolled parser that
    claims to read YAML is a bug waiting for a multi-line value. A list is read
    as its bracketed text and split on commas, which is how every report in the
    library writes `sections_exercised`.
    """
    match = HEADING.match(text)
    if not match:
        return {}
    out = {}
    for line in match.group(1).split("\n"):
        if ":" not in line or line.startswith(" "):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def listed(value: str) -> list[str]:
    inner = value.strip().strip("[]")
    return [part.strip().strip("'\"") for part in inner.split(",")
            if part.strip().strip("'\"")]


def proposals(text: str) -> list[str]:
    """The numbered items under the report's "what to improve" heading.

    ADR-38's format puts them last and numbers them, and says to write them as
    things a seat can do. Numbered items anywhere else in the report are the
    body's own structure and are not proposals, so the scan stops at the next
    heading.
    """
    out: list[str] = []
    inside = False
    buffer = ""
    for line in text.split("\n"):
        if IMPROVE_HEADING.match(line):
            inside = True
            continue
        if inside and OTHER_HEADING.match(line):
            break
        if not inside:
            continue
        found = NUMBERED.match(line)
        if found:
            if buffer:
                out.append(" ".join(buffer.split()))
            buffer = found.group(2)
        elif buffer and line.strip():
            buffer += " " + line.strip()
        elif buffer and not line.strip():
            out.append(" ".join(buffer.split()))
            buffer = ""
    if buffer:
        out.append(" ".join(buffer.split()))
    return [item for item in out if item]


def from_reports(directory: pathlib.Path) -> list[dict]:
    """One correction per numbered proposal in every consumer report."""
    out = []
    if not directory.is_dir():
        return out
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text()
        meta = frontmatter(text)
        sections = listed(meta.get("sections_exercised", ""))
        for index, item in enumerate(proposals(text), start=1):
            out.append({"source": "consumer report",
                        "where": f"{path.name}#{index}",
                        "sections": sections,
                        "consumer": meta.get("consumer", "unnamed"),
                        "text": item})
    return out


def from_results(doc: dict) -> list[dict]:
    """One correction per task the skill did not help on.

    A task whose with-arm did not beat its without-arm is the skill failing on a
    question the skill seat wrote for it. Nobody has to file that, and before
    ADR-40 nothing read it: a negative per-task delta sat in results.json and
    the only number anything looked at was the mean over all of them.
    """
    out = []
    for row in doc.get("per_task") or []:
        if row.get("control") or row.get("indicator"):
            continue
        delta = row.get("delta")
        if delta is None or delta > 0:
            continue
        sections = [str(s) for s in (row.get("sections") or [])]
        out.append({"source": "failed task", "where": row.get("id", "?"),
                    "sections": sections,
                    "consumer": "the eval harness",
                    "text": f"task {row.get('id')} did not improve with the "
                            f"skill loaded: with {row.get('with_mean')}, "
                            f"without {row.get('without_mean')}, scored by "
                            f"{row.get('scored_by', 'an unnamed instrument')}"
                            + (f", about {', '.join(sections)}"
                               if sections else "")})
    return out


def from_survival(doc: dict) -> list[dict]:
    """One correction per section Ursa's signal says nobody acted on.

    ADR-40's refinement item 5. Absent today, and the shape is fixed now so the
    day it arrives is a data change rather than a code change: each section in
    `section_deltas` carries `survival`, and a section whose survival says it was
    never acted on is a retirement candidate even when its eval holds.
    """
    out = []
    for name, row in (doc.get("section_deltas") or {}).items():
        survival = row.get("survival")
        if not isinstance(survival, dict):
            continue
        acted = survival.get("acted_on")
        if acted is None or acted:
            continue
        out.append({"source": "survival", "where": name, "sections": [name],
                    "consumer": "Ursa (ADR-39)",
                    "text": f"no consumer has acted on section {name!r} across "
                            f"{survival.get('loads', 'an unreported number of')} "
                            "loads, so it is a retirement candidate even though "
                            "its eval holds"})
    return out


def cluster(corrections: list[dict], threshold: float = SAME_CORRECTION
            ) -> list[dict]:
    """Single-link agglomerative clustering on word overlap. Deterministic.

    Single-link because the question is "does this correction say the same thing
    as anything already in the cluster", and that is what single-link asks. The
    order is the input's order, so two runs over the same pile produce the same
    clusters, which matters: a maintenance loop that proposes a different edit
    every morning from the same evidence is not a loop.
    """
    tokens = [words(c["text"] + " " + " ".join(c.get("sections") or []))
              for c in corrections]
    clusters: list[dict] = []
    for index, correction in enumerate(corrections):
        for group in clusters:
            if any(overlap(tokens[index], tokens[member]) >= threshold
                   for member in group["members"]):
                group["members"].append(index)
                group["tokens"] |= tokens[index]
                break
        else:
            clusters.append({"members": [index], "tokens": set(tokens[index])})
    out = []
    for group in clusters:
        rows = [corrections[i] for i in group["members"]]
        sections = []
        for row in rows:
            for name in row.get("sections") or []:
                if name not in sections:
                    sections.append(name)
        out.append({
            "size": len(rows),
            "sections": sections,
            "sources": sorted({row["source"] for row in rows}),
            "consumers": sorted({row["consumer"] for row in rows}),
            "evidence": [f"{row['source']}: {row['where']}" for row in rows],
            "corrections": [row["text"] for row in rows],
            "edit": generalized_edit(rows, sections),
        })
    # Largest first: a cluster of four reports asking for the same thing is a
    # stronger case for an edit than four clusters of one, and the ordering is
    # what puts that in front of whoever reads the dispatch.
    out.sort(key=lambda g: (-g["size"], g["edit"]))
    return out


def generalized_edit(rows: list[dict], sections: list[str]) -> str:
    """One edit for one cluster, written so a seat can act on it.

    It does not write the prose. It names the section, the number of independent
    corrections behind it, and who filed them, and it leaves the sentence to the
    seat that edits the skill. A generator that drafted the sentence here would
    be this file proposing skill content, which is the skill seat's call and
    ADR-13's.
    """
    where = ", ".join(sections) if sections else "no section named"
    who = sorted({row["consumer"] for row in rows})
    lead = rows[0]["text"]
    if len(lead) > 220:
        lead = lead[:217].rstrip() + "..."
    return (f"[{where}] {len(rows)} correction(s) from {len(who)} source(s) "
            f"({', '.join(who)}): {lead}")


def gather(slug: str, root: pathlib.Path | None = None) -> list[dict]:
    """Every correction on record for one skill, from all three sources."""
    base = (root or ROOT) / "skills" / slug
    doc = {}
    results = base / "evals" / "results.json"
    if results.exists():
        try:
            doc = json.loads(results.read_text())
        except json.JSONDecodeError:
            doc = {}
    return (from_reports(base / "reviews") + from_results(doc)
            + from_survival(doc))


def report(slug: str, root: pathlib.Path | None = None) -> dict:
    corrections = gather(slug, root)
    groups = cluster(corrections)
    passthrough = bool(groups) and len(groups) == len(corrections)
    return {
        "skill": slug,
        "corrections": len(corrections),
        "clusters": len(groups),
        "by_source": {name: sum(1 for c in corrections if c["source"] == name)
                      for name in SOURCES},
        "groups": groups,
        "threshold": SAME_CORRECTION,
        "passthrough": passthrough,
        "reads": (f"{len(corrections)} correction(s) on record became "
                  f"{len(groups)} cluster(s)")
                 + (". Every cluster holds exactly one correction, so the "
                    "clustering found nothing and this is the raw pile with a "
                    "label on it. ADR-40 refinement item 3 says the raw pile is "
                    "never applied, and lexical overlap is a worse instrument "
                    "than the embedding the ADR asks for"
                    if passthrough else ""),
    }


def render(doc: dict) -> str:
    lines = [f"{doc['skill']}: {doc['reads']}"]
    counts = ", ".join(f"{n} {name}" for name, n in doc["by_source"].items() if n)
    if counts:
        lines.append(f"  sources: {counts}")
    for group in doc["groups"]:
        lines.append(f"  - {group['edit']}")
        for line in group["evidence"]:
            lines.append(f"      {line}")
    if not doc["groups"]:
        lines.append("  nothing is on record, so no edit is proposed. ADR-40's "
                     "trap (C965): refinement proposals come from the subject "
                     "or from consumers, never from the cheap model's own idea "
                     "of what it could already reach")
    return "\n".join(lines)


# ------------------------------------------------------------------- the smoke

SMOKE_REPORT = """---
skill: fixture
skill_version: 2
consumer: a seat on real work
sections_exercised: [Order of operations, Debugging a harness]
decisions_changed: 1
---

# Bottom line

It was worth the context.

## Section by section

1. This numbered item is the body's own structure and is not a proposal.

## What alexandria should improve

1. The section on order of operations needs a worked number for the regression,
   because the claim is unquantified as written.
2. Order of operations should quantify the regression it mentions; a reader
   cannot act on an unquantified claim.
3. The debugging section should say what to do when two agents fail together.
"""


def smoke() -> int:
    checks = {}

    found = proposals(SMOKE_REPORT)
    checks["only the numbered items under the improve heading are proposals"] = (
        len(found) == 3 and found[0].startswith("The section on order")
        and "body's own structure" not in " ".join(found))
    checks["a multi-line proposal is read as one correction"] = (
        "because the claim is unquantified as written" in found[0])

    meta = frontmatter(SMOKE_REPORT)
    checks["the frontmatter's exercised sections are read"] = (
        listed(meta["sections_exercised"])
        == ["Order of operations", "Debugging a harness"])

    corrections = [{"source": "consumer report", "where": f"r#{i}",
                    "consumer": "c", "sections": [], "text": t}
                   for i, t in enumerate(found, start=1)]
    groups = cluster(corrections)
    checks["two reports asking for the same thing become one edit"] = (
        len(groups) == 2 and groups[0]["size"] == 2
        and groups[0]["evidence"] == ["consumer report: r#1",
                                      "consumer report: r#2"])
    checks["the edit names the count and leaves the prose to the skill seat"] = (
        "2 correction(s)" in groups[0]["edit"])
    checks["the clusters are ordered by how much evidence is behind them"] = (
        [g["size"] for g in groups] == [2, 1])

    again = cluster(corrections)
    checks["clustering the same pile twice gives the same clusters"] = (
        [g["edit"] for g in again] == [g["edit"] for g in groups])

    failed = from_results({"per_task": [
        {"id": "helped", "delta": 0.5, "with_mean": 1.0, "without_mean": 0.5},
        {"id": "flat", "delta": 0.0, "with_mean": 0.5, "without_mean": 0.5,
         "sections": ["Order of operations"]},
        {"id": "worse", "delta": -0.3, "with_mean": 0.2, "without_mean": 0.5},
        {"id": "ctl", "delta": -0.9, "control": True},
    ]})
    checks["a task the skill did not help on is a correction nobody filed"] = (
        [c["where"] for c in failed] == ["flat", "worse"])

    survival = from_survival({"section_deltas": {
        "Dead section": {"survival": {"acted_on": False, "loads": 9}},
        "Live section": {"survival": {"acted_on": True, "loads": 9}},
        "Unmeasured": {"survival": None},
    }})
    checks["a section nobody acted on is a retirement candidate"] = (
        [c["where"] for c in survival] == ["Dead section"])
    checks["a section with no survival signal is not called dead"] = (
        all(c["where"] != "Unmeasured" for c in survival))

    one_each = cluster([
        {"source": "consumer report", "where": "a", "consumer": "c",
         "sections": [], "text": "quantify the regression in section one"},
        {"source": "consumer report", "where": "b", "consumer": "c",
         "sections": [], "text": "the container needs a memory limit"},
    ])
    doc = {"skill": "x", "corrections": 2, "clusters": len(one_each),
           "by_source": {}, "groups": one_each, "threshold": SAME_CORRECTION,
           "passthrough": len(one_each) == 2, "reads": ""}
    checks["a pile that would not cluster is reported as a pass-through"] = (
        doc["passthrough"] is True)

    for label, ok in checks.items():
        print(("ok:   " if ok else "FAIL: ") + label)
    return 0 if all(checks.values()) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skill")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)

    if args.smoke:
        return smoke()
    if not args.skill:
        ap.error("--skill or --smoke")
    doc = report(args.skill)
    print(json.dumps(doc, indent=2, sort_keys=True) if args.json
          else render(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
