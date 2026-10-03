#!/usr/bin/env python3
"""The vocabulary ADR-13's reviewers share, and nothing either of them judges.

ADR-13 asks for three independent reviewers, and independence is about context,
not about code: each reviewer reads the proposal with no shared context with
its author, which is what makes agreement evidence rather than an echo. What
they do have to share is the shape of a verdict, because `panel_consensus`
counts passes across reviewers and a panel whose members graded on different
scales would compute a consensus out of three different words.

So this file holds the three severities, the arithmetic that turns findings
into one verdict, the connection rule, and the insert. It holds no check and no
judgment about any skill. `tools/panel_provenance.py` and
`tools/panel_adversary.py` hold those, separately, and neither imports the
other.

The split was made on 2026-10-03 when the second reviewer was written. Before
that this vocabulary lived inside the provenance reviewer, which was correct
while there was one of them and would have meant two drifting copies the moment
there were two.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent


class Finding:
    """One thing a reviewer noticed, with the severity that drives the verdict.

    `fail` is a defect in the skill. `unknown` is a defect in what this
    reviewer can see. `note` is evidence: it is recorded in the verdict so the
    row says what was actually measured, and it never changes the verdict.
    """

    SEVERITIES = ("fail", "unknown", "note")

    def __init__(self, check: str, severity: str, detail: str):
        assert severity in self.SEVERITIES, severity
        self.check = check
        self.severity = severity
        self.detail = detail

    def as_dict(self) -> dict:
        return {"check": self.check, "severity": self.severity,
                "detail": self.detail}

    def __repr__(self) -> str:                      # pragma: no cover
        return f"Finding({self.check}, {self.severity})"


def verdict_of(findings: list[Finding]) -> str:
    """fail beats unknown beats pass. A note never decides anything.

    The order matters and it is the conservative one: a skill with a real
    defect and an unmeasurable check is a `fail`, because the defect is known.
    """
    severities = {f.severity for f in findings}
    if "fail" in severities:
        return "fail"
    if "unknown" in severities:
        return "unknown"
    return "pass"


def connect(writable: bool, cannot: str = ""):
    """A connection, or None with a printed reason. Never raises on absence.

    `cannot` is the one sentence that says what this particular reviewer could
    not measure without a database, because that sentence is the only part of
    this function that differs between the two of them.
    """
    try:
        import psycopg
    except ImportError:
        print("unknown: psycopg is not installed here, so nothing could be "
              "checked against the corpus. pip install 'psycopg[binary]'")
        return None
    names = ("DATABASE_URL",) if writable else ("NEON_RO_URL", "DATABASE_URL")
    for name in names:
        url = (os.environ.get(name) or "").strip()
        if url:
            return psycopg.connect(url)
    print(f"unknown: none of {', '.join(names)} is in this environment, so "
          f"{cannot or 'nothing could be measured'}. The live half of every "
          "reviewer runs in pipeline/skill_revision.py, which holds the neon "
          "secret.")
    return None


def reviewer_sha(relative_path: str) -> str | None:
    """The git blob sha of a reviewer's own file, so a verdict says who judged.

    Returns None rather than raising when there is no git here, which is the
    case inside the Modal image: the image carries the file and not the
    repository, so `reviewer_sha` is null on every row the daily job files and
    `target_sha` is the pin that matters.
    """
    try:
        out = subprocess.run(["git", "rev-parse", f"HEAD:{relative_path}"],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        return out.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def file_verdicts(conn, insert: str, verdicts: list[dict],
                  sha: str | None = None) -> list[int]:
    """One INSERT per verdict. The reviewer's name is inside its own `insert`.

    Written out in each reviewer's SQL rather than passed as a parameter, so
    `tests/test_every_relation_the_reviewer_names_exists` can read which
    reviewer a statement files as, and a reviewer cannot file under another
    reviewer's name by passing the wrong string.
    """
    ids = []
    for v in verdicts:
        row = conn.execute(insert, (
            v["target"], v["verdict"], json.dumps(v["findings"]),
            v["target_sha"], sha,
        )).fetchone()
        ids.append(int(row[0]))
    conn.commit()
    return ids


def render(verdicts: list[dict]) -> str:
    """The human form: the verdict, every finding that decided it, the evidence."""
    lines = []
    for v in verdicts:
        lines.append(f"{v['verdict']:>7}  {v['target']}")
        for finding in v["findings"]:
            if finding["severity"] == "note":
                continue
            lines.append(f"         {finding['severity']}: {finding['check']}: "
                         f"{finding['detail']}")
        notes = [f["detail"] for f in v["findings"] if f["severity"] == "note"]
        if notes:
            lines.append(f"         measured: {'; '.join(notes)}")
    fails = sum(1 for v in verdicts if v["verdict"] == "fail")
    unknowns = sum(1 for v in verdicts if v["verdict"] == "unknown")
    lines.append("")
    lines.append(f"{len(verdicts)} skills reviewed, {fails} failing, "
                 f"{unknowns} not fully measurable")
    return "\n".join(lines)
