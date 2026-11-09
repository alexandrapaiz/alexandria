#!/usr/bin/env python3
"""Are the private paths absent from this repository's history, and could this clone tell?

    python3 tools/history_boundary.py                 # the charter's boundary duty, measured
    python3 tools/history_boundary.py --json
    python3 tools/history_boundary.py --path digests/  # one path rather than the standing list
    python3 tools/history_boundary.py --repo /some/checkout
    python3 tools/history_boundary.py --self-check     # the properties, printed

Exit 0 when every private path is absent from history and this clone could see
the history. Exit 1 when a private path is reachable. **Exit 2 when the clone
cannot answer**, which is the reason this file exists.

## Why

The security charter's public-and-private boundary duty is three sentences and
one of them is "`digests/` and `site/content/digests/` must be gitignored and
absent from history." Nine audits have answered it and none of them answered it
with a tool. The command each used was a `git log --all --diff-filter=A` typed
into a shell, and its clean answer is **empty output**, which makes this the
second duty in this charter whose silence is a pass.

**The host clones this repository at `--depth 1`, and on that clone the command
prints nothing.** Reproduced on 2026-11-09 against a fresh `git clone --depth 1`
of the public remote: `git rev-list --all --count` answers **1**, and the
boundary command over both private paths prints nothing at all, where the same
command on the full 4,870-commit history prints `043767e5`. No pathspec form
explains it; all four spellings of `digests` find the commit once the history is
present. The clone depth is the whole mechanism.

**It has already reached a pushed public branch once.** Two runs of this seat on
2026-11-09 answered this duty differently, hours apart. `audit-2026-11-09.md`
has it right: the one historical digest is still reachable from `043767e5`, the
known finding, raised 2026-09-18, withdrawn 2026-09-19, restated low with no
action 2026-11-02. `audit-2026-11-09-bounds-verified.md` says the command
"prints nothing, so they are absent from history on every branch this clone can
see." That sentence is wrong, and its direction is the dangerous one: it reports
a boundary clean. The hedge at the end of it is the tell. A clone that can see
less is not a narrower answer to this question, it is a wrong one.

The charter does carry the remedy, `git fetch --unshallow` with the widened
refspec, in bold, with three incidents behind it. It carries it under the rule
about **comparing two branches**, and this duty is not a comparison of two
branches, so a run that obeys that rule exactly can still measure history on a
grafted clone. `tools/check_pr_green.py` already holds both halves of that guard,
`shallow_state` and `refspec_is_wide`, and this file calls them rather than
restating them, because the guard was never the missing part. Only its sentence
is written here, since that one is written for a comparison of two branches.

## What it does not do

It does not scan for secrets. The charter's other history-wide duty is a
credential scan over every blob reachable from every ref, which has the same
blindness on the same clone and is a larger instrument than this: the 2026-11-08
audit did it properly over 8,536 blobs in two passes and recorded that "the
history scan is reproducible from this description and the script is not." That
tool is a day of work and is in `docs/ideas.md` for the engineer seat. This file
covers the one duty whose answer was published wrong, and its preflight is the
half both duties share.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

# The standing list, from the charter's boundary duty and `.gitignore` lines 8
# and 11. A path is on this list because shipping it publicly would leak the
# private product, not because it happens to be ignored today.
PRIVATE_PATHS = ("digests/", "site/content/digests/")

ABSENT = 0
PRESENT = 1
CANNOT_LOOK = 2

_spec = importlib.util.spec_from_file_location(
    "check_pr_green", TOOLS / "check_pr_green.py"
)
_green = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("check_pr_green", _green)
_spec.loader.exec_module(_green)


class CannotLook(Exception):
    """This clone cannot answer. Never an answer of "absent"."""


def _git(*args: str, repo: Path = ROOT, timeout: int = 60) -> str:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        raise CannotLook(f"git did not answer within {timeout}s: git {' '.join(args)}") from None
    except OSError as exc:
        raise CannotLook(f"git could not be run: {exc}") from None
    if proc.returncode != 0:
        first = (proc.stderr or "").strip().splitlines()
        raise CannotLook(
            f"git exited {proc.returncode}: {first[0] if first else 'no message'}"
        )
    return proc.stdout


def denominator(repo: Path = ROOT) -> dict:
    """What this clone can actually see, so a clean answer carries its own scope."""
    return {
        "commits": int(_git("rev-list", "--all", "--count", repo=repo).strip() or 0),
        "refs": len(_git("for-each-ref", "--format=%(refname)", repo=repo).splitlines()),
    }


def ever_mentioned(path: str, repo: Path = ROOT) -> bool:
    """Did any commit on any ref ever touch this path at all, under any filter.

    The standing list is a constant, so its clean answer is the one being asked
    for. A value handed to `--path` is not: a path spelled wrong and a path that
    was never present produce the same empty, which is the class this file is
    about, inside this file. This is what lets the clean line say which of the
    two it is rather than leaving the caller to assume.
    """
    return bool(_git("log", "--all", "--format=%H", "-1", "--", path, repo=repo).strip())


def additions(path: str, repo: Path = ROOT) -> list[dict]:
    """Every commit that ever added a file under this path, on any ref."""
    out = _git(
        "log", "--all", "--diff-filter=A", "--format=%H%x09%ad%x09%s",
        "--date=short", "--", path, repo=repo,
    )
    rows = []
    for line in out.splitlines():
        sha, _, rest = line.partition("\t")
        date, _, subject = rest.partition("\t")
        rows.append({"commit": sha[:8], "date": date, "subject": subject})
    return rows


REMEDY = (
    "Run: git config --add remote.origin.fetch "
    "'+refs/heads/*:refs/remotes/origin/*' && git fetch --unshallow"
)


def preflight(repo: Path = ROOT) -> str | None:
    """The reason this clone cannot answer, or None.

    The two primitives are `tools/check_pr_green.py`'s, because the guard was
    never the missing part. Its own `preflight` is not called, only because its
    sentence is written for a comparison of two branches and this duty is not
    one, and a gate that explains itself in terms of the wrong question is how a
    reader talks themselves past it.
    """
    state = _green.shallow_state(repo)
    if state is not False:
        was = "is shallow" if state else "could not say whether it is shallow"
        return (
            f"this clone {was}, and on a shallow clone the history this duty asks "
            f"about is not here to be asked. {REMEDY}"
        )
    if not _green.refspec_is_wide(repo):
        return (
            "this clone's fetch refspec names only the trunk, so `--all` reaches "
            f"the trunk alone and a private path on any other ref is invisible. {REMEDY}"
        )
    return None


def check(paths=PRIVATE_PATHS, repo: Path = ROOT) -> dict:
    reason = preflight(repo)
    if reason:
        raise CannotLook(reason)
    scope = denominator(repo)
    if scope["commits"] <= 1:
        # The guard above reads git's own shallow flag. This reads the result,
        # because a clone can be grafted in ways that flag does not admit and a
        # history of one commit cannot answer a question about history.
        raise CannotLook(
            f"this clone holds {scope['commits']} commit(s), which cannot answer a "
            "question about history even though git does not call it shallow"
        )
    found = {p: additions(p, repo) for p in paths}
    unknown = sorted(
        p for p, rows in found.items() if not rows and not ever_mentioned(p, repo)
    )
    return {
        "scope": scope,
        "paths": found,
        "never_mentioned": unknown,
        "absent": all(not rows for rows in found.values()),
    }


def describe(result: dict) -> str:
    scope = result["scope"]
    head = (
        f"asked every one of {scope['refs']} refs over {scope['commits']} commits "
        f"for any commit that ever added these paths"
    )
    if result["absent"]:
        names = ", ".join(result["paths"])
        line = f"absent: {names} appear in no commit on any ref. {head}."
        unknown = [p for p in result.get("never_mentioned", []) if p not in PRIVATE_PATHS]
        if unknown:
            line += (
                "\n  note: " + ", ".join(unknown) + " was never touched by any commit "
                "under any filter, so a path spelled wrong and a path never present "
                "are the same answer here. Check the spelling before recording this."
            )
        return line
    lines = [f"PRESENT in history. {head}."]
    for path, rows in result["paths"].items():
        if not rows:
            lines.append(f"  {path}: absent")
            continue
        for row in rows:
            lines.append(f"  {path}: added at {row['commit']} ({row['date']}) {row['subject']}")
    lines.append(
        "This is a statement about reachability, not a disposition. The one "
        "standing instance is recorded and withdrawn; read docs/security/ before "
        "treating a row here as new."
    )
    return "\n".join(lines)


SELF_CHECK = """\
history_boundary.py, the four properties it is written to hold

1. A private path reachable from any ref exits 1 and names the commit, with no
   file content printed, because the charter forbids quoting private evidence
   and reachability is the whole question.
2. A clone that cannot see the history exits 2 and never 0. The host clones at
   --depth 1, and on that clone the typed command this replaces prints nothing,
   which the duty reads as a pass.
3. The clean answer carries its denominator, refs and commits, so a reader can
   tell a measurement from a silence. Nine audits answered this duty with an
   empty shell output and one of them published the wrong answer. A --path value
   no commit ever touched says so on the same line, because a path spelled wrong
   and a path never present are otherwise the same empty.
4. The preflight reuses tools/check_pr_green.py's shallow_state and
   refspec_is_wide, because the guard existed and only the branch-comparison
   duty was ever wired to it.
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Are the private paths absent from history, and could this clone tell?"
    )
    ap.add_argument("--path", action="append", help="measure this path instead of the standing list")
    ap.add_argument("--repo", type=Path, default=ROOT, help="the checkout to measure, defaulting to this one")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--self-check", action="store_true", dest="self_check")
    args = ap.parse_args(argv)

    if args.self_check:
        sys.stdout.write(SELF_CHECK)
        return ABSENT

    try:
        result = check(tuple(args.path) if args.path else PRIVATE_PATHS, args.repo)
    except CannotLook as exc:
        if args.as_json:
            print(json.dumps({"absent": None, "cannot_look": str(exc)}, indent=1))
        else:
            sys.stderr.write(
                f"COULD NOT LOOK: {exc}\n"
                "This is not an answer of 'absent from history'. Do not record a "
                "clean boundary on it.\n"
            )
        return CANNOT_LOOK

    if args.as_json:
        print(json.dumps(result, indent=1))
    else:
        print(describe(result))
    return ABSENT if result["absent"] else PRESENT


if __name__ == "__main__":
    sys.exit(main())
