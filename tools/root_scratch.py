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

## The second bound, and why a list of names could not be the only one

`BELONGS` is a decision about a name. So is `_is_root`, and so is `--allow`.
Three bounds in one dimension leave the dimension beside it unasked, which is
**what a root entry is** rather than what it is called. Reproduced on
2026-11-09: a symlink at the root named `skills`, pointing at `/etc`, passed
this gate at exit 0 and printed nothing, while the identical link named
`notlisted` was caught on the same tree. `git ls-tree` writes the kind down in
the mode and `--name-only` was throwing it away.

`ROOT_MODES` is that second bound. The root of this repository has carried
exactly two modes across all twenty-three of its tracked entries, a directory
and a regular non-executable file, so a cited name arriving as a symlink, a
submodule or an executable is a stray however legitimate its spelling.

The class came to this seat from the ExO seat, which had just taken the same
finding from this seat about `tools/prose_symbols.py`, where all three bounds
were decisions about a directory and the missing one was the kind of an entry.
The general form is worth more than either instance: **name the dimension every
bound you have is a decision about, then go looking for the step that is not in
it.**

## Why this is a gate and not a habit

The sixth entry's remedy was a habit: stage explicit paths rather than
`git add -A`. It was written on 2026-11-02 and the class repeated on the
next run of this seat, inside the pull request filing that entry. Incident 20's
rule is the general form, and it names exactly this failure: recording is not
enforcing, and every register needs a second gate that reads it before
something ships. This file is that gate for this class. The habit stays
correct and is still the cheaper way to never trip the gate.

## What it does not do

It does not look at content or size, so a stray whose *contents* imitate a real
file reads the same to it as any other stray, which is fine because the name is
what it judges. It does ask the entry's kind, and the sentence here used to say
it could not be fooled by a stray spelled like a real file, which was false in
exactly the case the kind bound now covers.

It says nothing about files below the root, because `docs/` holds real
artifacts and a seat writing into its own lane is the normal case. It never
deletes anything. And it always measures the clone it is installed in rather
than the current directory, because `ROOT` is derived from this file's own
path, so pointing a shell at another tree and running this copy reports on
this tree.

Exit 2 means nothing was measured, and every way of failing to ask git reaches
it: a non-zero exit, a thirty-second timeout, and no git binary at all. A tool
whose output is the absence of a finding must never answer a question it could
not ask.
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


class GitUnavailable(Exception):
    """git could not be asked, which is not an answer about the tree."""


# The only two modes the root of this repository has ever carried, measured on
# `main` over all twenty-three tracked root entries on 2026-11-09: a directory
# and a regular, non-executable file.
#
# This is the bound that asks what a root entry *is* rather than what it is
# called, and it exists because none of the other three can ask. `BELONGS` is a
# decision about a name, `_is_root` is a decision about a name, and `--allow`
# is a decision about a name, so a root entry carrying one of the twenty-one
# cited names while being a different kind of thing passes all three.
#
# Reproduced 2026-11-09, in this seat's own gate: a symlink named `skills`
# pointing at `/etc` passed at exit 0 and in silence, while the identical link
# named `notlisted` was caught. The class was handed to this seat by the ExO
# seat, who had just taken the same finding from it about `tools/prose_symbols.py`.
ROOT_MODES = {
    "040000": "a directory",
    "100644": "a regular file",
}

# What the modes this gate refuses actually are, so the refusal says the thing
# a reader needs rather than six digits.
ROOT_KINDS = {
    "120000": "a symlink",
    "160000": "a gitlink, which is a submodule pointing at another repository",
    "100755": "an executable file",
}


def _git(*args, cwd=None):
    """Run one git command. A non-zero exit is an answer, and a hang is not.

    The two are kept apart here deliberately, and the reason is this seat's own
    finding against another seat's tool on 2026-11-09: catching every failure of
    a git call into one return value moves the conflation up a call rather than
    removing it, because the caller then reads "git could not be asked" as "git
    said no". So a non-zero exit is returned and the caller reads it, while a
    timeout or a missing git binary raises, and `main` turns that into an
    explicit could-not-look with exit 2.

    The timeout is the half of that which was missing here until 2026-11-09,
    and this file had none at all while the tool it was reported against had
    thirty seconds. This gate is written to sit in front of an `&&` in a seat's
    ready command, so an unbounded call here stalls a whole run and prints
    nothing at all while it does.
    """
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd or ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise GitUnavailable(f"git {' '.join(args)}: {exc}") from exc
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


def _is_root(path):
    return "/" not in path.strip()


def _parse_raw_z(out):
    """`git diff --raw -z` as (path, new mode) pairs.

    `--raw` is used in place of `--name-only` for exactly one reason: the mode
    is the only place an entry's kind is written down, and `--name-only` throws
    it away. The format is a NUL-separated stream of alternating records, a
    metadata field beginning with a colon that holds the old and new modes,
    then the path. `--diff-filter=A` is always passed with it, so the
    two-path rename and copy records cannot appear.
    """
    fields = [f for f in out.split("\0") if f]
    pairs = []
    i = 0
    while i < len(fields):
        meta = fields[i]
        if not meta.startswith(":"):
            i += 1
            continue
        parts = meta[1:].split()
        new_mode = parts[1] if len(parts) > 1 else ""
        if i + 1 < len(fields):
            pairs.append((fields[i + 1], new_mode))
        i += 2
    return pairs


def _parse_ls_tree_z(out):
    """`git ls-tree -z` as (path, mode) pairs, one per entry of one tree level."""
    pairs = []
    for record in out.split("\0"):
        if not record.strip():
            continue
        head, _, path = record.partition("\t")
        parts = head.split()
        if path and parts:
            pairs.append((path, parts[0]))
    return pairs


def _kind_problem(mode):
    """Why this mode does not belong at the root, or None if it does."""
    if mode in ROOT_MODES:
        return None
    named = ROOT_KINDS.get(mode, f"mode {mode}")
    return f"the name is cited, but the entry is {named} rather than a directory or a regular file"


def _staged_root_adds(cwd=None):
    """Root paths the index adds, with each one's mode."""
    code, out, err = _git("diff", "--cached", "--raw", "--diff-filter=A", "-z", cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or "cannot read the index")
    return [(path, mode) for path, mode in _parse_raw_z(out) if _is_root(path)]


def _branch_root_adds(ref, cwd=None):
    """Root files this branch's commits add relative to the baseline's tree.

    Two dots and not three. A three-dot comparison needs a merge base, and a
    merge base is the one thing a shallow clone lies about
    (INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register).
    Asking what this tree has that the baseline tree does not have needs no
    ancestry at all, and a root file that main already carries is reported by
    `--tracked` rather than here.
    """
    code, out, err = _git("diff", "--raw", "--diff-filter=A", "-z", ref, "HEAD", cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or f"cannot diff against {ref}")
    return [(path, mode) for path, mode in _parse_raw_z(out) if _is_root(path)]


def _tracked_strays(cwd=None):
    """Root entries on HEAD that nothing cites, or that are the wrong kind.

    The second half was added 2026-11-09 with the fourth bound. A cited name
    carrying an uncited kind is the case this reported as clean, and it is the
    one worth reporting here rather than failing on, like every other landed
    instance.
    """
    code, out, err = _git("ls-tree", "-z", "HEAD", cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or "cannot read HEAD")
    strays = []
    for path, mode in _parse_ls_tree_z(out):
        if path not in BELONGS:
            strays.append((path, "nothing at the root cites this name"))
        else:
            problem = _kind_problem(mode)
            if problem:
                strays.append((path, problem))
    return sorted(strays)


def scan(staged=True, branch=True, allow=(), cwd=None):
    """The report, as a dict. `strays` empty means there is nothing to say."""
    # `--allow` and `BELONGS` are deliberately not the same permission, and the
    # difference only appeared once there were two bounds. `BELONGS` says a name
    # is cited, which is a claim about the name and nothing else, so an entry
    # under a cited name still has to be the kind of thing that name means.
    # `--allow` is a person at a terminal saying "this exact path, this run,"
    # which is the escape hatch, and it has to cover both bounds or there is no
    # escape hatch for the second one at all.
    waived = set(allow)
    cited = set(BELONGS) | waived
    ref = _baseline_ref(cwd=cwd)
    if ref is None:
        return {"measured": False, "reason": "no main or origin/main in this clone"}

    sources = []
    if staged:
        sources.append(("staged", _staged_root_adds(cwd=cwd)))
    if branch:
        sources.append(("committed on this branch", _branch_root_adds(ref, cwd=cwd)))

    found = {}
    root_adds = set()
    for where, adds in sources:
        for path, mode in adds:
            root_adds.add(path)
            if path in waived:
                continue
            # Two bounds, asked in this order, because the name is the cheaper
            # question and a name nobody cites needs no second one.
            if path not in cited:
                why = "nothing at the root cites this name"
            else:
                why = _kind_problem(mode)
                if why is None:
                    continue
            found.setdefault(path, {"why": why, "where": []})["where"].append(where)

    return {
        "measured": True,
        "baseline": ref,
        "strays": [
            {"path": path, "where": f["where"], "why": f["why"]}
            for path, f in sorted(found.items())
        ],
        # Which `--allow` values actually suppressed something, so the caller
        # can be told about one that did not.
        "allowed_seen": sorted(set(allow) & root_adds),
    }


def _self_check():
    return [
        "A root entry not named in BELONGS is a stray, so a name nobody has",
        "used yet is caught the first time rather than the second.",
        "Only the root is read. docs/ artifacts are a seat's normal output.",
        "A cited name of a kind the root has never carried is a stray too,",
        "because the other three bounds are all decisions about a name.",
        "Two-dot diffs only, so a shallow clone cannot make this lie.",
        "Exit 1 on a stray, 0 on clean with no output, 2 when unmeasurable,",
        "and a git call that cannot be made is unmeasurable and never clean.",
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

    # Every path below asks git something, and every one of those questions can
    # fail to be asked. Until 2026-11-09 none of them was caught, so a git call
    # that broke left an uncaught traceback and Python's own exit 1 -- which is
    # this gate's "a stray was found" code, so an unmeasurable tree reported as
    # a failed gate and the docstring's promise of exit 2 was reachable from one
    # branch only. Both are refusals and both exit 2.
    try:
        return _run(args)
    except GitUnavailable as exc:
        print(f"root_scratch: git could not be asked, so nothing was measured: {exc}",
              file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"root_scratch: cannot measure this tree: {exc}", file=sys.stderr)
        return 2


def _run(args):
    if args.tracked:
        strays = _tracked_strays()
        if args.json:
            print(json.dumps({"tracked_strays": [
                {"path": p, "why": why, "known": KNOWN_LANDED.get(p)}
                for p, why in strays
            ]}, indent=2))
            return 0
        if not strays:
            print("no root entry on HEAD that BELONGS does not name, and none of the wrong kind")
            return 0
        print(f"{len(strays)} root entries on HEAD that do not belong:")
        for path, why in strays:
            note = KNOWN_LANDED.get(path, "not a known instance, read it before removing it")
            print(f"  {path}  -- {why}; {note}")
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
            print(f"    {stray['why']}")
        print("Move them under a mktemp -d and drop them from the branch, or add")
        print("the name to BELONGS with its citation.")
        print("A cited name of the wrong kind is the second case, and BELONGS")
        print("will not clear it, because BELONGS is a claim about the name. Pass")
        print("--allow for one run, or widen ROOT_MODES if the root genuinely")
        print("needs to carry that kind from now on. No entry at this root is a")
        print("symlink or a submodule today, so either is a deliberate act.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
