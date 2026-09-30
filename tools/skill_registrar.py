#!/usr/bin/env python3
"""Register every skill on main, so `skills_needing_revision` has something to join.

    python3 tools/skill_registrar.py                  # the rows every skill would register as
    python3 tools/skill_registrar.py --files-only     # the CI gate: no database needed
    python3 tools/skill_registrar.py --check          # DATABASE_URL: which skills have no row
    python3 tools/skill_registrar.py --backfill       # DATABASE_URL: write the missing rows
    python3 tools/skill_registrar.py --revisions      # DATABASE_URL: read skills_needing_revision
    python3 tools/skill_registrar.py --deprecated 5,11,12,85,129,188   # offline cross-reference
    python3 tools/skill_registrar.py --json           # any of the above, for a script

ADR-36's finding, in the owner's words: skills are proven, not asserted, and
today they are neither revised nor proven. The mechanism of the first half is
this file. `db/schema.sql` has carried a `skills_needing_revision` view since
the founding: it joins a promoted skill's cited claims against
`deprecated_claims` and returns the skills whose evidence has moved under them.
It has never returned a row, and it never could, because it reads `promotions`
and the skill seat writes a `SKILL.md` into the repository with no `promotions`
row behind it. Seven claims are deprecated. No skill knows. The site says a
skill is revised when the research moves.

So a merged skill is registered. The row is derived rather than typed: every
field comes out of the skill's own provenance block, which is the same text the
library publishes on the skill's page, so the row cannot say something the page
does not. `kind` is `skill`, `status` is `approved`, `path` is the skill's
directory, and `claim_ids` is its `provenance.claims` list.

**Why `approved` and not `proposed`.** `promotions.status` is a three-way check
and the view reads only `approved`. A skill on main is there because the owner
merged it, and that merge is the approval ADR-13's panel exists to earn. A row
written for a skill that is not on main would be the wrong thing entirely, which
is why `--backfill` refuses to run against a dirty tree or a branch that is not
main unless it is told to (`--allow-branch`).

**The check is in two halves, and it has to be.** `checks.yml` runs in GitHub
Actions, where this organization has no database at all: the only Postgres that
matters is the production one and CI holds no credential for it. So the half
that CI can run is `--files-only`, which asks whether every skill on main can be
registered (its provenance parses, it names claims, its directory and its `name`
agree). The half that needs Neon, whether the row is actually there, runs in the
daily job that already holds the `neon` secret, `pipeline/skill_revision.py`.
Splitting it is not a weakening: the failure this guard exists to catch is a
skill merged without a registrable provenance block, and that one is visible in
the file.

## The three states

Same vocabulary as `tools/graph_audit.py` and `tools/delivery_health.py`, for
the same reason.

    ok        measured, and nothing wrong
    failing   measured, and something is wrong
    unknown   not measurable from here

    exit 0    nothing wrong
    exit 1    a finding: a skill that cannot be registered, or has no row
    exit 2    nothing wrong, and something could not be measured

## What it needs

`--files-only` needs nothing but the repository. Everything else needs
`DATABASE_URL` (or `NEON_RO_URL` for the read-only modes) and `psycopg`.
`--backfill` is the only mode here that writes, and it writes one statement:
an upsert into `promotions` keyed by the partial unique index on `path`.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

# Directories under skills/ that are not skills. `_validation` is the trigger
# test's own home and has no SKILL.md, so it would otherwise read as a skill
# that failed to parse.
NOT_A_SKILL = {"_validation"}

KIND = "skill"
STATUS = "approved"


# ----------------------------------------------------------- frontmatter

# The frontmatter this library writes is a two-level subset of YAML: scalars,
# one nested map under `provenance:`, inline arrays of numbers, and block lists
# of quoted strings. It is parsed structurally rather than by key regex, and the
# reason is worth keeping: `site/lib/content.js` matched keys anchored at column
# 0 against a file whose every provenance field is indented, so `validated` and
# every claim id read as the empty string on every skill for eleven days and the
# page rendered anyway (PR #133). A regex cannot tell `papers:` inside
# `provenance:` from a `papers:` at the top level. This is the Python side of
# `site/lib/skill-provenance.js`, and `tests/test_skill_registrar.py` holds the
# two against the same real files.
FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.S)


def split_frontmatter(raw: str) -> tuple[str, str]:
    match = FRONTMATTER.match(raw)
    if not match:
        return "", raw.strip()
    return match.group(1), raw[match.end():].strip()


def _unquote(value: str) -> str:
    v = value.strip()
    if len(v) > 1 and ((v[0] == '"' and v.endswith('"'))
                       or (v[0] == "'" and v.endswith("'"))):
        return v[1:-1]
    return v


def _inline_array(value: str) -> list[str]:
    return [x for x in (_unquote(p) for p in value[1:-1].split(",")) if x]


def parse_frontmatter(fm: str) -> dict:
    """The frontmatter as nested dicts and lists. Lookahead, never guesswork."""
    lines = []
    for raw in fm.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        lines.append((len(raw) - len(raw.lstrip()), raw.strip()))

    out: dict = {}
    stack: list[tuple[int, dict]] = [(-1, out)]
    current_list: list | None = None

    for i, (indent, text) in enumerate(lines):
        if text.startswith("- "):
            if current_list is not None:
                current_list.append(_unquote(text[2:]))
            continue

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        node = stack[-1][1]
        current_list = None

        key, _, rest = text.partition(":")
        key = key.strip()
        value = rest.strip()

        if value:
            if value.startswith("[") and value.endswith("]"):
                node[key] = _inline_array(value)
            else:
                node[key] = _unquote(value)
            continue

        # A key with no value on its own line. The next line decides what it is:
        # a `- ` opens a block list, a deeper indent opens a map, and anything
        # else leaves it an empty scalar.
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if nxt and nxt[0] > indent and nxt[1].startswith("- "):
            node[key] = []
            current_list = node[key]
        elif nxt and nxt[0] > indent:
            node[key] = {}
            stack.append((indent, node[key]))
        else:
            node[key] = ""

    return out


# ----------------------------------------------------------- the rows

class Row:
    """One `promotions` row, derived from one SKILL.md. Never typed by hand."""

    def __init__(self, slug: str, path: str, claim_ids: list[int],
                 name: str, version: str, status: str, sha: str):
        self.slug = slug
        self.path = path
        self.claim_ids = claim_ids
        self.name = name
        self.version = version
        self.skill_status = status      # the SKILL.md's own `status:` field
        self.sha = sha

    def as_dict(self) -> dict:
        return {
            "slug": self.slug, "path": self.path, "kind": KIND,
            "status": STATUS, "claim_ids": self.claim_ids,
            "name": self.name, "version": self.version,
            "skill_status": self.skill_status, "skill_md_sha256": self.sha,
        }


def read_skills(skills_dir: pathlib.Path | None = None) -> tuple[list[Row], list[str]]:
    """Every skill directory's derived row, plus one line per thing wrong.

    A directory with no SKILL.md is a finding rather than a skip, because the
    only way that happens is a half-merged skill.
    """
    import hashlib

    skills_dir = skills_dir or SKILLS_DIR
    rows: list[Row] = []
    problems: list[str] = []

    for entry in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        slug = entry.name
        if slug in NOT_A_SKILL:
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            problems.append(
                f"skills/{slug}/ has no SKILL.md, so no promotions row can be "
                "derived for it. Either it is a half-merged skill or it is "
                "infrastructure that belongs in skill_registrar.NOT_A_SKILL.")
            continue

        raw = skill_md.read_text()
        fm, _ = split_frontmatter(raw)
        if not fm:
            problems.append(
                f"skills/{slug}/SKILL.md has no `---` frontmatter block, so it "
                "carries no provenance and cannot be registered.")
            continue

        parsed = parse_frontmatter(fm)
        provenance = parsed.get("provenance")
        if not isinstance(provenance, dict):
            problems.append(
                f"skills/{slug}/SKILL.md has no `provenance:` map. ADR-36 "
                "derives the promotions row from that block, so a skill "
                "without one cannot be registered and cannot be revised when "
                "its evidence moves.")
            continue

        raw_claims = provenance.get("claims") or []
        if isinstance(raw_claims, str):
            raw_claims = [raw_claims] if raw_claims else []
        claim_ids: list[int] = []
        for value in raw_claims:
            try:
                claim_ids.append(int(str(value).strip()))
            except ValueError:
                problems.append(
                    f"skills/{slug}/SKILL.md cites {value!r} as a claim id, "
                    "which is not an integer. `promotions.claim_ids` is "
                    "bigint[] and the view joins on it.")
        if not claim_ids:
            problems.append(
                f"skills/{slug}/SKILL.md cites no claim ids. A skill with an "
                "empty provenance block can never appear in "
                "skills_needing_revision, so it is a skill that silently "
                "opts out of revision.")

        name = str(parsed.get("name") or "")
        if name and name != slug:
            problems.append(
                f"skills/{slug}/SKILL.md says `name: {name}`, which is not its "
                "directory. The page, the trigger test and this row all key on "
                "one or the other, so they have to agree.")

        rows.append(Row(
            slug=slug,
            path=f"skills/{slug}",
            claim_ids=claim_ids,
            name=name or slug,
            version=str(parsed.get("version") or ""),
            status=str(parsed.get("status") or ""),
            sha=hashlib.sha256(raw.encode()).hexdigest(),
        ))

    seen: dict[str, str] = {}
    for row in rows:
        if row.path in seen:
            problems.append(f"two skills claim the path {row.path}")
        seen[row.path] = row.slug

    return rows, problems


# ----------------------------------------------------------- the database

# Every statement this file sends, in one place, so `tests/test_skill_registrar.py`
# can parse them with libpg_query and resolve every relation and column against
# db/schema.sql. That test is the only thing standing between a renamed column
# and a daily job that silently stops finding skills, because no CI job in this
# organization can execute any of these against a real database.
QUERIES = {
    "registered": """
        select path, claim_ids
        from promotions
        where kind = 'skill' and status = 'approved'
    """,
    "revisions": """
        select promotion_id, skill_path, deprecated_claim_id, deprecated_claim
        from skills_needing_revision
        order by skill_path, deprecated_claim_id
    """,
    "upsert": """
        insert into promotions (claim_ids, kind, path, status, decided_at)
        values (%s, 'skill', %s, 'approved', now())
        on conflict (path) where kind = 'skill'
        do update set claim_ids = excluded.claim_ids,
                      status = 'approved',
                      decided_at = now()
        returning id
    """,
}


def connect(writable: bool):
    """A connection, or None with a printed reason. Never raises on absence."""
    try:
        import psycopg
    except ImportError:
        print("unknown: psycopg is not installed here, so nothing about the "
              "database could be measured. pip install 'psycopg[binary]'")
        return None
    names = ("DATABASE_URL",) if writable else ("NEON_RO_URL", "DATABASE_URL")
    for name in names:
        url = (os.environ.get(name) or "").strip()
        if url:
            return psycopg.connect(url)
    print(f"unknown: none of {', '.join(names)} is in this environment, so "
          "whether these skills are registered could not be measured. The "
          "engineer seat has no database credential (pending-workflow-changes "
          "item 6), which is why the live half of this check runs in "
          "pipeline/skill_revision.py.")
    return None


def registered_paths(conn) -> dict[str, list[int]]:
    return {path: list(claims or [])
            for path, claims in conn.execute(QUERIES["registered"]).fetchall()}


def unregistered(rows: list[Row], live: dict[str, list[int]]) -> list[Row]:
    return [r for r in rows if r.path not in live]


def stale(rows: list[Row], live: dict[str, list[int]]) -> list[Row]:
    """Registered, but the row's claim ids no longer match the file's.

    A revision that adds a paper adds claim ids, and a row left behind is a
    skill whose evidence is being watched at the wrong address.
    """
    return [r for r in rows
            if r.path in live and sorted(live[r.path]) != sorted(r.claim_ids)]


def backfill(conn, rows: list[Row]) -> list[str]:
    written = []
    for row in rows:
        conn.execute(QUERIES["upsert"], (row.claim_ids, row.path))
        written.append(f"{row.path}: {len(row.claim_ids)} claim ids")
    conn.commit()
    return written


def revisions(conn) -> list[dict]:
    out = []
    for pid, path, claim_id, claim in conn.execute(QUERIES["revisions"]).fetchall():
        out.append({"promotion_id": pid, "skill_path": path,
                    "deprecated_claim_id": claim_id,
                    "deprecated_claim": claim})
    return out


# ----------------------------------------------------------- offline answer

def touching(rows: list[Row], deprecated: list[int]) -> list[dict]:
    """Which skills cite which of `deprecated`. The view's answer, without Neon.

    The daily job asks Postgres. This exists so the question can be answered
    from a checkout with a list of ids from somewhere else, which is how it was
    answered on 2026-09-30: the engineer seat holds no database credential, and
    the deprecated ids were read out of the research seat's 2026-09-28 brief.
    A list read from a document is evidence with a date on it, not a live query,
    and anything printed from it says so.
    """
    want = set(deprecated)
    hits = []
    for row in rows:
        touched = sorted(want & set(row.claim_ids))
        if touched:
            hits.append({"skill_path": row.path, "claim_ids": touched,
                         "cites": len(row.claim_ids)})
    return hits


# ----------------------------------------------------------- git

def on_main() -> tuple[bool, str]:
    try:
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                cwd=ROOT, capture_output=True, text=True,
                                check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "skills"],
                               cwd=ROOT, capture_output=True, text=True,
                               check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return False, f"git could not be asked which branch this is ({exc})"
    if branch != "main":
        return False, f"this is branch {branch}, not main"
    if dirty:
        return False, "skills/ has uncommitted changes in this checkout"
    return True, "main, with a clean skills/"


# ----------------------------------------------------------- cli

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--files-only", action="store_true",
                    help="the CI gate: every skill can be registered. No database.")
    ap.add_argument("--check", action="store_true",
                    help="every skill on main has its promotions row")
    ap.add_argument("--backfill", action="store_true",
                    help="write the rows that are missing or stale")
    ap.add_argument("--revisions", action="store_true",
                    help="read skills_needing_revision and print it")
    ap.add_argument("--deprecated", default="",
                    help="comma-separated claim ids, cross-referenced offline")
    ap.add_argument("--allow-branch", action="store_true",
                    help="let --backfill run somewhere other than a clean main")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    rows, problems = read_skills()
    report: dict = {
        "skills": [r.as_dict() for r in rows],
        "problems": problems,
        "state": "failing" if problems else "ok",
    }

    if args.deprecated:
        ids = [int(x) for x in args.deprecated.replace(" ", "").split(",") if x]
        report["deprecated_given"] = ids
        report["touching"] = touching(rows, ids)

    needs_db = args.check or args.backfill or args.revisions
    unmeasured = False
    if needs_db:
        conn = connect(writable=args.backfill)
        if conn is None:
            unmeasured = True
        else:
            with conn:
                live = registered_paths(conn)
                missing = unregistered(rows, live)
                out_of_date = stale(rows, live)
                report["registered"] = sorted(live)
                report["unregistered"] = [r.path for r in missing]
                report["stale"] = [r.path for r in out_of_date]
                if args.backfill:
                    ok, why = on_main()
                    if not ok and not args.allow_branch:
                        print(f"refusing to backfill: {why}. A promotions row "
                              "says the owner merged this skill, so it is "
                              "written from main or with --allow-branch and a "
                              "reason.")
                        return 1
                    report["written"] = backfill(conn, missing + out_of_date)
                elif missing or out_of_date:
                    report["state"] = "failing"
                if args.revisions:
                    report["revisions"] = revisions(conn)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{len(rows)} skills on this checkout, "
              f"{sum(len(r.claim_ids) for r in rows)} claim ids in total")
        for row in rows:
            print(f"  {row.path}: {len(row.claim_ids)} claims, "
                  f"version {row.version or '?'}, status {row.skill_status or '?'}")
        for line in problems:
            print(f"failing: {line}")
        if "unregistered" in report:
            for path in report["unregistered"]:
                print(f"failing: {path} is on main with no promotions row, so "
                      "skills_needing_revision cannot see it and nothing will "
                      "notice when a claim it cites is deprecated")
            for path in report["stale"]:
                print(f"failing: {path}'s promotions row cites a different set "
                      "of claims than its SKILL.md does")
        for line in report.get("written", []):
            print(f"registered {line}")
        for hit in report.get("touching", []):
            print(f"touching: {hit['skill_path']} cites deprecated claim(s) "
                  f"{', '.join(str(c) for c in hit['claim_ids'])} out of "
                  f"{hit['cites']} it cites")
        for rev in report.get("revisions", []):
            print(f"revision: {rev['skill_path']} cites deprecated claim "
                  f"{rev['deprecated_claim_id']}")
        if report.get("touching") == [] and "touching" in report:
            print("touching: none of the given claim ids is cited by any skill")
        if not report.get("revisions") and args.revisions and not unmeasured:
            print("skills_needing_revision is empty: no registered skill cites "
                  "a deprecated claim")

    if report["state"] == "failing":
        return 1
    return 2 if unmeasured else 0


if __name__ == "__main__":
    sys.exit(main())
