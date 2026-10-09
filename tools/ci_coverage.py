#!/usr/bin/env python3
"""Which test files does CI actually run?

INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had: `checks.yml`
runs fourteen test files as fourteen named steps, and
`tests/test_markdown.py` is not one of them. That file holds the
2026-09-19 finding, the one where a crafted passage in an arXiv paper
reached the public archive as live HTML, and its own docstring says the
other half of it "is the half that runs in CI". Neither half runs
anywhere. `tests/test_accounts.py` is in the same position and it holds
the account and entitlement layer.

The defect is invisible by construction, which is the whole reason this
file exists. A test file that no workflow names does not fail. It passes
locally, it passes for the seat that wrote it, and it reports nothing at
all on the pull request that breaks what it guards. So the coverage
itself has to be the thing under test.

This module answers one question against the workflow files as they are
written, with no network and no GitHub API: for every test file in
`tests/`, is there a step in some workflow that executes it? It is the
measuring half. `tests/test_ci_coverage.py` is the gate, and it pins
today's uncovered set so that the set can shrink and cannot grow.

    python3 tools/ci_coverage.py            # the report
    python3 tools/ci_coverage.py --json     # the same thing, machine-readable
    python3 tools/ci_coverage.py --workflows .github/workflows-pending

Why this parses the YAML as text rather than with a parser. The
distinction that matters here is between a test file named in a `run:`
command and the same test file named in a `paths:` filter, and those are
two lines that look alike and mean opposite things: one executes the
file, the other only decides whether the job starts. A `paths` entry is
why this defect hid for so long, because the live `checks.yml` lists
`tests/test_press_resilience.py` in both places and a reader skimming for
the filename finds it either way. So the parser is block-aware about
`run:` specifically, and deliberately blind to everything else. It also
keeps this repository's dev dependencies as they are: there is no
`pyyaml` in `requirements-dev.txt` and a guard is a poor reason to add
one.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(".github", "workflows")
TESTS = "tests"

# A test file is one the harness will collect or a person can run: pytest's
# own `test_*.py` convention, and node's `*.test.mjs`. `conftest.py` and
# `sql_schema.py` are support code that other tests import, so they are
# covered whenever their importers are and are not files CI runs directly.
TEST_PATTERNS = ("test_*.py", "*.test.mjs")


def test_files(root: str = REPO) -> list[str]:
    """Every test file in `tests/`, as repo-relative paths, sorted."""
    found: set[str] = set()
    for pattern in TEST_PATTERNS:
        for path in glob.glob(os.path.join(root, TESTS, pattern)):
            found.add(os.path.relpath(path, root))
    return sorted(found)


def run_commands(text: str) -> list[str]:
    """Every shell command a workflow's steps execute, as strings.

    Block-aware about `run:` and nothing else, which is the point: a
    `paths:` entry naming a test file is not an execution of it.
    """
    commands: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^(\s*)-?\s*run:\s*(.*)$", line)
        if not match:
            i += 1
            continue
        indent, rest = len(match.group(1)), match.group(2).strip()
        if rest and rest not in ("|", ">", "|-", ">-", "|+", ">+"):
            # An inline command. YAML folds a plain scalar across
            # continuation lines, so take the indented remainder too.
            block = [rest]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    break
                if len(nxt) - len(nxt.lstrip()) <= indent:
                    break
                block.append(nxt.strip())
                i += 1
            commands.append(" ".join(block))
            continue
        # A literal or folded block: every line indented past the key.
        i += 1
        block = []
        while i < len(lines):
            nxt = lines[i]
            if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                break
            block.append(nxt.strip())
            i += 1
        commands.append("\n".join(block))
    return commands


def files_executed_by(command: str, universe: list[str], root: str = REPO) -> set[str]:
    """The test files one shell command runs.

    Three shapes appear in this repository and all three are handled:
    a bare script (`python3 tests/x.py`), pytest over named files
    (`python3 -m pytest tests/a.py tests/b.py -q`), and pytest or node
    over a directory or a glob (`python3 -m pytest tests/ -q`,
    `node --test tests/*.test.mjs`).
    """
    hit: set[str] = set()
    # A whole-directory pytest invocation: `pytest tests/` or `pytest tests`,
    # with no path under tests/ narrowing it.
    for part in re.split(r"[;&|\n]+", command):
        part = part.strip()
        if not part:
            continue
        tokens = part.split()
        named = [t for t in tokens if t.startswith(f"{TESTS}/") or t == TESTS]
        if not named:
            continue
        for token in named:
            token = token.strip("'\"")
            if token in (TESTS, f"{TESTS}/"):
                # The suite. pytest collects `test_*.py`; node does not run
                # here, so .mjs files are not covered by a pytest sweep.
                hit |= {f for f in universe if f.endswith(".py")}
                continue
            if any(ch in token for ch in "*?["):
                for path in glob.glob(os.path.join(root, token)):
                    rel = os.path.relpath(path, root)
                    if rel in universe:
                        hit.add(rel)
                continue
            if token in universe:
                hit.add(token)
    return hit


# A test file can also be run by another test file. `tests/test_markdown.py`
# runs `node --test tests/markdown.test.mjs` in a subprocess, which is how
# the node halves of this suite reach a Python harness at all, and
# `tests/test_skill_receipts.py` runs `tests/test_panel_provenance.py` the
# same way. That coverage is real: when the parent runs in CI, the child's
# assertions execute and a failure in the child fails the step. A report
# that called the child uncovered would be wrong, and it would push a seat
# to add a second step that runs it twice.
#
# So the scan is deliberately narrow. Only a quoted filename inside the
# argument list of a subprocess call counts, not a filename in a docstring
# or a skip message, because several of these files name each other in
# prose. Ten lines is the window: the longest of these calls in the
# repository today spans five.
SUBPROCESS = re.compile(r"subprocess\.(?:run|Popen|check_output|check_call)\(")
LITERAL = re.compile(r"""['"]([A-Za-z0-9_.-]+\.(?:py|mjs))['"]""")
WINDOW = 10


def children_of(path: str, universe: list[str], root: str = REPO) -> set[str]:
    """The test files this test file executes as subprocesses."""
    by_basename = {os.path.basename(f): f for f in universe}
    with open(os.path.join(root, path), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    found: set[str] = set()
    for n, line in enumerate(lines):
        if not SUBPROCESS.search(line):
            continue
        for candidate in LITERAL.findall("\n".join(lines[n : n + WINDOW])):
            child = by_basename.get(candidate)
            if child and child != path:
                found.add(child)
    return found


def indirect(direct: dict[str, list[str]], universe: list[str], root: str = REPO) -> None:
    """Spread coverage down the subprocess tree, in place, to a fixed point."""
    edges = {f: children_of(f, universe, root) for f in universe if f.endswith(".py")}
    changed = True
    while changed:
        changed = False
        for parent, kids in edges.items():
            if not direct[parent]:
                continue
            for kid in kids:
                for source in direct[parent]:
                    label = f"{source} (via {parent})" if "(via" not in source else source
                    if label not in direct[kid]:
                        direct[kid].append(label)
                        changed = True


def coverage(
    root: str = REPO,
    workflows: str = WORKFLOWS,
    only: list[str] | None = None,
) -> dict:
    """The report: which test files CI runs, which it does not, and where.

    `only` measures an explicit list of repo-relative workflow files instead
    of a directory. `tests/test_ci_coverage.py` uses it to ask what the
    staged replacement in `.github/workflows-pending/` would cover if it
    were the live `checks.yml`, which is a question about one file and not
    about the directory it is parked in.
    """
    universe = test_files(root)
    where: dict[str, list[str]] = {f: [] for f in universe}
    if only is None:
        workflow_paths = sorted(glob.glob(os.path.join(root, workflows, "*.yml")))
    else:
        workflow_paths = [os.path.join(root, rel) for rel in only]
    for path in workflow_paths:
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for command in run_commands(text):
            for name in files_executed_by(command, universe, root):
                if rel not in where[name]:
                    where[name].append(rel)
    direct = {f: list(v) for f, v in where.items()}
    indirect(where, universe, root)
    return {
        "direct": sorted(f for f in direct if direct[f]),
        "workflows": [os.path.relpath(p, root) for p in workflow_paths],
        "total": len(universe),
        "covered": sorted(f for f in universe if where[f]),
        "uncovered": sorted(f for f in universe if not where[f]),
        "where": where,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="print the report and exit 0 even when test files are uncovered",
    )
    parser.add_argument(
        "--only",
        action="append",
        metavar="FILE",
        help="measure these workflow files only, repo-relative; repeatable",
    )
    parser.add_argument(
        "--workflows",
        default=WORKFLOWS,
        help="directory of workflow files to measure (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    report = coverage(workflows=args.workflows, only=args.only)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    total, uncovered = report["total"], report["uncovered"]
    print(f"{len(report['covered'])} of {total} test files run in CI")
    print(f"  workflows read: {', '.join(report['workflows']) or '(none)'}")
    if not uncovered:
        print("  every test file in tests/ is executed by some workflow")
        return 0
    print(f"\n{len(uncovered)} test files run in no workflow:")
    for name in uncovered:
        print(f"  {name}")
    if args.report_only:
        return 0
    # Exit non-zero, and the reason is the defect this file was written for.
    # A step whose name claims every test file runs, and which exits 0 while
    # 33 of them do not, is another assertion nobody checks. So the report is
    # a gate by default and informational only when asked.
    print(
        "\nFAIL: a test file no workflow runs reports nothing on any pull "
        "request.\n      Pass --report-only for the report without the verdict."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
