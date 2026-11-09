#!/usr/bin/env python3
"""Is this branch about to commit a file at the checkout root that nothing cites?

    python3 tools/root_scratch.py                 # the index and this branch, vs main
    python3 tools/root_scratch.py --staged        # the index only, before a commit
    python3 tools/root_scratch.py --branch        # this branch's commits only
    python3 tools/root_scratch.py --tracked       # what is already tracked and does not belong
    python3 tools/root_scratch.py --allow NAME    # this root path is legitimate, this once
    python3 tools/root_scratch.py --self-check    # the properties, printed
    python3 tools/root_scratch.py --json

Exit 1 when a stray root file is staged or committed on this branch, and print
nothing at all when there is none, so this can sit in front of an `&&` in a
seat's ready command without being noticed. Exit 2 when the baseline cannot be
read, which is a refusal to answer rather than an answer of "clean".

## Why an allowlist, when every earlier instance shipped a denylist

Seven runs of this company have committed scratch to the checkout root. The
register for the class is
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`
and its five successors, and the sixth entry
(`INC-2026-11-02-the-sixth-root-scratch-reached-a-pushed-public-branch-and-the-staging-command-is-the-surface-the-five-before-it-did-not-name`)
says in writing what the fourth and fifth both said before it: a list of names
cannot stop the next name, because a name an earlier run already committed is
a name that was already caught.

`.gitignore` on main carries five of those entries and they are all correct.
They did not stop the seventh instance, which was `.board.json`, a name none of
them carries. That is not a gap in the list. It is the list's own ceiling.

So this file enumerates the other side. The root of this repository holds
twenty-one entries and every one of them is cited by something: a workflow, a
manifest, an import, a charter. That set is small, it is stable, and it changes
only when somebody deliberately adds a top-level surface. A stray is then
defined without predicting anything: **a root entry that is not on the list.**
A legitimately new one costs a one-line edit here plus a reviewer's glance,
which is the correct price for adding a top-level file to a public repository.

## Why this is a gate and not a habit

The sixth entry's remedy was a habit: stage explicit paths rather than
`git add -A`. It was written on 2026-11-02 and the class repeated on the
next run of this seat, inside the pull request filing that entry. Incident 20's
rule is the general form, and it names exactly this failure: recording is not
enforcing, and every register needs a second gate that reads it before
something ships. This file is that gate for this class. The habit stays
correct and is still the cheaper way to never trip the gate.

## What it does not do

It does not look at content, size or shape, so it cannot be fooled by a stray
that is spelled like a real file. It says nothing about files below the root,
because `docs/` holds real artifacts and a seat writing into its own lane is
the normal case. And it never deletes anything.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Every entry at the repository root, and what cites it. A reviewer adding a
# line here is being asked to name the citation, which is the whole point.
BELONGS = {
    ".agents": "the agent manifests the host reads",
    ".claude": "Claude Code settings and skills for this checkout",
    ".claude-plugin": "the plugin manifest tools/check_plugin_manifest.py reads",
    ".cursor-plugin": "the Cursor plugin manifest",
    ".github": "the workflows",
    ".gitignore": "git",
    "README.md": "the repository's own front page",
    "company.yaml": "the seat roster the bus and tools/wake_routes.py parse",
    "db": "the schema tests/sql_schema.py loads",
    "docs": "every register and audit in this repository",
    "mcp": "the MCP server",
    "pipeline": "the digest pipeline",
    "prompts": "the twelve charters",
    "pytest.ini": "pytest, which reads the suite's tmp_path retention policy from it",
    "requirements-dev.txt": "the dev image",
    "requirements.txt": "the pipeline image",
    "site": "the Next.js site",
    "skills": "the skills library",
    "skills-lock.json": "tools/skill_registrar.py",
    "sources.yaml": "pipeline/ingest.py",
    "tests": "the suite",
    "tools": "the seat tools",
}

# Root entries that are tracked on main and are not cited by anything. They are
# this class's own landed instances, kept here by name so `--tracked` reports
# them as known rather than as news, and so removing one is a deliberate act by
# the seat that owns it. Neither is a secret and neither is loaded by any code.
KNOWN_LANDED = {
    ".prbody-exo.md": "ExO seat's pull request body, committed 2026-10-26 in 80f5e3e6",
    "site-server.log": "a Next.js dev-server log, committed 2026-10-26 in adb9cf1a",
}


def _git(*args, cwd=None):
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _baseline_ref(cwd=None):
    """The ref this branch's additions are measured against.

    `origin/main` when the clone has it, `main` otherwise. A shallow clone whose
    default branch is grafted still answers both, and the comparison here is
    name-only against one tree rather than a three-way merge, so the shallow
    trap that governs `git merge-base` does not apply.
    """
    for ref in ("origin/main", "main"):
        code, _, _ = _git("rev-parse", "--verify", "--quiet", f"{ref}^{{tree}}", cwd=cwd)
        if code == 0:
            return ref
    return None


def _root_entries(ref, cwd=None):
    code, out, err = _git("ls-tree", "--name-only", ref, cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or f"cannot read {ref}")
    return {line.strip() for line in out.splitlines() if line.strip()}


def _is_root(path):
    return "/" not in path.strip()


def _staged_root_adds(cwd=None):
    code, out, err = _git("diff", "--cached", "--name-only", "--diff-filter=A", cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or "cannot read the index")
    return [p for p in (line.strip() for line in out.splitlines()) if p and _is_root(p)]


def _branch_root_adds(ref, cwd=None):
    """Root files this branch's commits add relative to the baseline's tree.

    Two dots and not three. A three-dot comparison needs a merge base, and a
    merge base is the one thing a shallow clone lies about
    (INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register).
    Asking what this tree has that the baseline tree does not have needs no
    ancestry at all, and a root file that main already carries is reported by
    `--tracked` rather than here.
    """
    code, out, err = _git("diff", "--name-only", "--diff-filter=A", ref, "HEAD", cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or f"cannot diff against {ref}")
    return [p for p in (line.strip() for line in out.splitlines()) if p and _is_root(p)]


def _tracked_strays(cwd=None):
    code, out, err = _git("ls-tree", "--name-only", "HEAD", cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or "cannot read HEAD")
    entries = {line.strip() for line in out.splitlines() if line.strip()}
    return sorted(e for e in entries if e not in BELONGS)


def scan(staged=True, branch=True, allow=(), cwd=None):
    """The report, as a dict. `strays` empty means there is nothing to say."""
    allowed = set(BELONGS) | set(allow)
    ref = _baseline_ref(cwd=cwd)
    if ref is None:
        return {"measured": False, "reason": "no main or origin/main in this clone"}

    found = {}
    root_adds = set()
    if staged:
        for path in _staged_root_adds(cwd=cwd):
            root_adds.add(path)
            if path not in allowed:
                found.setdefault(path, []).append("staged")
    if branch:
        for path in _branch_root_adds(ref, cwd=cwd):
            root_adds.add(path)
            if path not in allowed:
                found.setdefault(path, []).append("committed on this branch")

    return {
        "measured": True,
        "baseline": ref,
        "strays": [{"path": p, "where": w} for p, w in sorted(found.items())],
        # Which `--allow` values actually suppressed something, so the caller
        # can be told about one that did not.
        "allowed_seen": sorted(set(allow) & root_adds),
    }


def _self_check():
    return [
        "A root entry not named in BELONGS is a stray, so a name nobody has",
        "used yet is caught the first time rather than the second.",
        "Only the root is read. docs/ artifacts are a seat's normal output.",
        "Two-dot diffs only, so a shallow clone cannot make this lie.",
        "Exit 1 on a stray, 0 on clean with no output, 2 when unmeasurable.",
        "It never deletes, moves or stages anything.",
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--staged", action="store_true", help="the index only")
    parser.add_argument("--branch", action="store_true", help="this branch's commits only")
    parser.add_argument("--tracked", action="store_true",
                        help="report root entries already tracked on HEAD that nothing cites")
    parser.add_argument("--allow", action="append", default=[], metavar="NAME",
                        help="treat this root path as legitimate for this run")
    parser.add_argument("--self-check", action="store_true", help="print the properties")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)

    if args.self_check:
        for line in _self_check():
            print(line)
        return 0

    if args.tracked:
        strays = _tracked_strays()
        if args.json:
            print(json.dumps({"tracked_strays": [
                {"path": p, "known": KNOWN_LANDED.get(p)} for p in strays
            ]}, indent=2))
            return 0
        if not strays:
            print("no root entry on HEAD that BELONGS does not name")
            return 0
        print(f"{len(strays)} root entries on HEAD that nothing cites:")
        for path in strays:
            note = KNOWN_LANDED.get(path, "not a known instance, read it before removing it")
            print(f"  {path}  -- {note}")
        print("Reported and not failed: removing a landed file belongs to the seat that put it there.")
        return 0

    staged = args.staged or not args.branch
    branch = args.branch or not args.staged
    report = scan(staged=staged, branch=branch, allow=args.allow)

    # An `--allow` that matched nothing is a typo or a stale invocation, and
    # silence would read as a pass. The value is a name and not a file this
    # tool opens, so nothing else here would ever raise on it.
    if report.get("measured"):
        unused = [a for a in args.allow if a not in report.get("allowed_seen", [])]
        for name in unused:
            print(f"note: --allow {name} matched no addition at the root",
                  file=sys.stderr)

    if args.json:
        print(json.dumps(report, indent=2))
    if not report.get("measured"):
        if not args.json:
            print(f"cannot measure: {report['reason']}", file=sys.stderr)
        return 2
    if not report["strays"]:
        return 0
    if not args.json:
        print(f"{len(report['strays'])} stray file(s) at the checkout root:")
        for stray in report["strays"]:
            print(f"  {stray['path']}  ({', '.join(stray['where'])})")
        print("Nothing at the root cites these. Move them under a mktemp -d and")
        print("drop them from the branch, or add the name to BELONGS with its citation.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
