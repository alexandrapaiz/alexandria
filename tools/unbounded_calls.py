#!/usr/bin/env python3
"""Every call that leaves the process and is not bounded in time.

    python3 tools/unbounded_calls.py                  # the whole tree
    python3 tools/unbounded_calls.py tools/           # one path
    python3 tools/unbounded_calls.py --network-only    # only calls that leave the machine
    python3 tools/unbounded_calls.py --json
    python3 tools/unbounded_calls.py --baseline docs/security/unbounded-calls.json

Exit 0 when nothing in scope is unbounded, or when everything unbounded is
already in the baseline. Exit 1 when an unbounded call is in scope and not in
the baseline. Exit 2 when the question could not be asked, which is a refusal
to answer rather than an answer of clean.

**The last line of that invocation list is the green one, and it was owed**
(written 2026-11-09 by the security seat, from the `alexandria/exo` seat's
reading of this file). The first version of this tool shipped deliberately
with no baseline, so that the count was the thing that went down. The
consequence was that no invocation of it reached exit 0 anywhere in this
repository: the bare run exited 1 at the live count, and the documented
`--baseline` path existed on no branch, so the flag raised `CannotLook` and
printed "refusing to answer, which is not an answer of clean". A gate with no
green state cannot go in a pipeline or a checklist, so it gets run once by its
author and never again. The ExO seat found that by running this file rather
than by reading its report, which is the only way it was ever going to be
found: the suite had 38 tests, every exit-0 assertion was against a tree the
test built, and the one test that ran the real command line accepted either
answer.

**What "accepted" means, and what it does not.** An accepted row silences one
unbounded call at one path and line. It is not a statement that the call is
safe. Every row in the shipped set today carries `status: "debt"`, which means
the call should get a clock and has not got one, and the word for a call that
genuinely wants no bound is `status: "wants-no-clock"`, of which there are
none here. That is why the clean path prints how many unbounded calls it read
beside how many this file accepted, rather than printing nothing: green here
reads "23 unbounded of which 23 accepted", which a reader can act on, and
never "clean".

**Accepted rows go stale, and a set nobody prunes stops being a ratchet.** The
set is keyed on path and line, so a call that gets its clock and a call that
merely moves both leave a row matching nothing. That is measured rather than
feared: `tools/board.py`'s two unbounded calls moved from lines 844 and 857 to
981 and 994 inside one evening of edits to that file, which on its own would
have left two stale rows beside two fresh findings for zero change in the
world. So stale rows are named on every path, with no effect on the exit
status, because a row going stale is usually somebody having paid the debt.

**Why this is a tool and not a grep** (written 2026-11-09 by the security
seat). On 2026-11-09 two seats of this company spent an evening on one defect
class: an external call with no timeout, no handler, and an exit status read
beside a discarded output so that "the tool could not answer" arrives as "the
tool answered no". Five sightings were reported, four were fixed, and the
`alexandria/exo` charter grew a rule telling a seat to run the class over the
artifacts it owns before reporting it outward.

That rule is right and it was satisfied three separate times by a grep over
the files the seat happened to have open. The tree held twenty-four instances
in `tools/` alone, eight of them crossing the network, at every moment of that
evening. Three bounds in one dimension -- who wrote it, which file is open,
which sighting is in hand -- and the dimension beside them is what is actually
there. The rule reproduced the class it was written to stop, which is the
sixth sighting and the first one inside a remedy rather than inside a tool.

So the predicate stops being a habit and becomes a thing you can run. A gate
is the half the registers rule says the org keeps forgetting: one gate decides
something gets written down, and a second decides something gets checked
before it ships.

**What counts as unbounded.** A `subprocess` call or a `urlopen` whose
`timeout` keyword is absent or is a literal `None`. That is deliberately
syntactic and deliberately shallow.

**And `httpx` is deliberately not scanned, which is a measurement rather than
an omission.** This repository's HTTP calls go through `httpx` in nine
modules, and `httpx` is bounded by default:
`httpx._config.DEFAULT_TIMEOUT_CONFIG` reads `Timeout(timeout=5.0)`, so
`httpx.get(url)` with no keyword already has a clock. `subprocess` has no
default at all, and `urlopen` inherits `socket.getdefaulttimeout()`, which is
`None` on this host and is never set anywhere in this tree. Those two are the
transports whose silence means forever, which is why they are the two scanned.
The one `httpx` spelling that would be unbounded is an explicit
`timeout=None`, and that appears nowhere in `tools/`, `pipeline/` or `mcp/`
today. If it ever does, this is the paragraph that says to widen the scan.
It cannot see a bound applied by a wrapper, so a wrapper that bounds its own
call is reported and belongs in the baseline with a one-line reason. It cannot
see a bound that arrives as a positional argument either, and `subprocess.run`
has no positional timeout, so for that call the keyword is the only spelling.

A false positive costs one baseline line. A false negative is a run that hangs
until the sixty-minute wall and prints nothing while it does, which is what
this file exists to make visible.
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Attribute names on `subprocess` that start a process.
SUBPROCESS_STARTERS = {"run", "Popen", "call", "check_call", "check_output"}

#: Binaries that always leave the machine, whatever their arguments.
NETWORK_BINARIES = {"gh", "curl", "wget", "npm", "npx", "pip", "pip3"}

#: Binaries that leave the machine for some subcommands and not others. `git
#: fetch` crosses the network and `git rev-parse` does not, so the reach is
#: read off the subcommand when the argv is a literal and is `unknown` when it
#: is not. A call whose reach cannot be read is reported as `unknown` rather
#: than as local, because "local" is the only wrong guess that hides a
#: finding.
SOMETIMES_NETWORK = {"git"}

#: `git` subcommands that talk to a remote. `remote` and `archive` are
#: deliberately absent: `git remote get-url` and `git archive <local-ref>` are
#: both local, and listing them would have called this repository's only two
#: uses of them network. Both are still unbounded and both are still reported,
#: under their real reach.
GIT_REMOTE_SUBCOMMANDS = {"fetch", "push", "pull", "clone", "ls-remote",
                          "submodule"}

#: Directories with no run of ours inside them.
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             ".next", "dist", "build", ".pytest_cache", ".mypy_cache"}


class CannotLook(Exception):
    """The question could not be asked. Never an answer of clean."""


def _is_bounded(call: ast.Call) -> bool:
    """Whether a `timeout` keyword is present *and* is not a literal None.

    The second half was missing until the gate's author ran this question at
    its own code. `subprocess.run(argv, timeout=None)` is unbounded and reads
    as bounded to anything that only asks whether the keyword is there, which
    is the same shape as every defect this file reports: the bound was a
    decision about whether an argument exists, and the dimension beside it is
    what the argument says.

    Nothing in this repository writes `timeout=None` today, measured, so this
    is a guard rather than a finding. It is here because the next person to
    silence this gate will reach for exactly that spelling.
    """
    for keyword in call.keywords:
        if keyword.arg != "timeout":
            continue
        value = keyword.value
        if isinstance(value, ast.Constant) and value.value is None:
            return False
        return True
    return False


def _argv_of(call: ast.Call) -> list[str] | None:
    """The literal head of a call's argv, as far as it is readable.

    None when the argv is a variable, a splat, or a join. This tool will not
    guess at those, and a caller treats an unreadable argv as `unknown` reach
    rather than as local.
    """
    if not call.args:
        return None
    first = call.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value.split() or None
    if isinstance(first, (ast.List, ast.Tuple)):
        words = []
        for element in first.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                words.append(element.value)
            else:
                break
        return words or None
    return None


def _reach(argv: list[str] | None) -> tuple[str, str]:
    """`(binary, reach)` where reach is `network`, `local` or `unknown`.

    Three values and not two, because the honest answer for an argv this tool
    cannot read is that it does not know, and collapsing that into either of
    the others is the conflation this whole class is about.
    """
    if not argv:
        return "unreadable", "unknown"
    binary = argv[0].rsplit("/", 1)[-1]
    if binary in NETWORK_BINARIES:
        return binary, "network"
    if binary in SOMETIMES_NETWORK:
        subcommands = [word for word in argv[1:] if not word.startswith("-")]
        # `git -C <path> fetch` puts the path in front of the subcommand, so
        # any readable word matching the set is enough to call it network.
        if any(word in GIT_REMOTE_SUBCOMMANDS for word in subcommands):
            return binary, "network"
        if not subcommands:
            # `["git", *args]` and `["git", "-C", path, ...]` both stop the
            # argv reader before any subcommand, so there is nothing to
            # classify on and `unknown` is the honest answer.
            return binary, "unknown"
        return binary, "local"
    return binary, "local"


def _handlers_covering(tree: ast.AST, lineno: int) -> list[str]:
    """The except clauses whose try block contains `lineno`.

    Reported rather than judged. A handler is not a bound: it is the other
    half, and a call with a handler and no timeout still hangs forever. The
    two are printed side by side so a reader can see which half is missing.
    """
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        start = min(x.lineno for x in node.body)
        end = max(getattr(x, "end_lineno", x.lineno) or x.lineno
                  for x in node.body)
        if start <= lineno <= end:
            for handler in node.handlers:
                found.append(ast.unparse(handler.type) if handler.type else "bare")
    return found


def scan_source(source: str, path: str) -> list[dict]:
    """Every external call in one file's text, bounded or not.

    **The bounded ones are returned too, and that was a correction** (made
    2026-11-09, by this file's own test suite before it shipped). The first
    version dropped them, so the clean path could only say "0 in scope", which
    reads identically whether the tool found twenty-three calls that all have
    clocks or found no calls because it never looked at the right directory. A
    reader cannot tell those apart, and the whole class this gate exists for is
    an instrument's silence read as a fact about the world. Sixth instance of
    this class inside its own repair in two evenings.

    Raises `CannotLook` on a file that does not parse, because a file this tool
    silently skipped is a file it reported clean without reading, and that is
    the single-route negative result the register already carries as a class.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise CannotLook(f"{path}: does not parse ({exc})") from exc

    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        module = getattr(func.value, "id", "")
        kind = None
        if module == "subprocess" and func.attr in SUBPROCESS_STARTERS:
            kind = f"subprocess.{func.attr}"
        elif func.attr == "urlopen":
            kind = "urlopen"
        if kind is None:
            continue
        bounded = _is_bounded(node)
        if kind == "urlopen":
            binary, reach = "http", "network"
        else:
            binary, reach = _reach(_argv_of(node))
        rows.append({
            "path": path,
            "line": node.lineno,
            "call": kind,
            "binary": binary,
            "reach": reach,
            "bounded": bounded,
            "handlers": _handlers_covering(tree, node.lineno),
        })
    return sorted(rows, key=lambda r: (r["path"], r["line"]))


def scan_paths(paths, root: pathlib.Path = ROOT) -> list[dict]:
    """Every external call under each path, bounded or not. Dirs recurse."""
    files: list[pathlib.Path] = []
    for raw in paths:
        target = (root / raw) if not pathlib.Path(raw).is_absolute() else pathlib.Path(raw)
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            for found in sorted(target.rglob("*.py")):
                if SKIP_DIRS & set(found.relative_to(root).parts):
                    continue
                files.append(found)
        else:
            raise CannotLook(f"{raw}: no such file or directory under {root}")

    rows = []
    for found in files:
        try:
            text = found.read_text(encoding="utf-8")
        except OSError as exc:
            raise CannotLook(f"{found}: could not read ({exc})") from exc
        rows.extend(scan_source(text, str(found.relative_to(root))))
    return rows


def load_baseline(path: pathlib.Path | None) -> set[tuple[str, int]]:
    """Accepted instances, as `path:line` pairs.

    A baseline is a decision someone wrote down, so it is read strictly: a
    malformed baseline is a `CannotLook` and never an empty set, because an
    empty set reads as "nothing is accepted" and would turn an unreadable file
    into a wall of findings nobody asked for.
    """
    if path is None:
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CannotLook(f"{path}: could not read the baseline ({exc})") from exc
    if not isinstance(data, dict) or not isinstance(data.get("accepted"), list):
        raise CannotLook(f"{path}: a baseline is an object with an 'accepted' list")
    out = set()
    for row in data["accepted"]:
        if not isinstance(row, dict) or "path" not in row or "line" not in row:
            raise CannotLook(f"{path}: every accepted row needs a path and a line")
        out.add((row["path"], int(row["line"])))
    return out


def stale_rows(rows: list[dict],
               accepted: set[tuple[str, int]]) -> list[tuple[str, int]]:
    """Accepted rows that match no unbounded call in the tree.

    Computed against every row rather than against `--network-only`'s scope,
    because a local accepted row matching nothing under that filter is the
    filter working and not a stale row.

    This is the half that makes the count able only to go down. The accepted
    set is keyed on path and line, so a call that gets its clock and a call
    that merely moves both leave a row matching nothing, and a set nobody
    prunes grows until it accepts lines that no longer exist. Naming them is
    not a finding and does not change the exit status: a row going stale is
    usually somebody having paid the debt.
    """
    unbounded_anywhere = {(r["path"], r["line"])
                          for r in rows if not r["bounded"]}
    return sorted(accepted - unbounded_anywhere)


def render(rows: list[dict], accepted: set[tuple[str, int]],
           network_only: bool) -> tuple[list[dict], str]:
    """The findings and the prose, from one pass over the rows."""
    # `--network-only` keeps `unknown` as well as `network`, because dropping
    # the calls this tool could not read would make the filter quieter than
    # the truth.
    scope = [r for r in rows
             if not network_only or r["reach"] in ("network", "unknown")]
    unbounded = [r for r in scope if not r["bounded"]]
    new = [r for r in unbounded if (r["path"], r["line"]) not in accepted]

    lines = []
    for row in new:
        where = {"network": "leaves the machine",
                 "local": "local",
                 "unknown": "reach unreadable"}[row["reach"]]
        half = ("no handler either" if not row["handlers"]
                else f"handled ({', '.join(row['handlers'])}) but not bounded")
        lines.append(f"{row['path']}:{row['line']}  {row['call']}"
                     f"({row['binary']}) -- {where}, {half}")
    if new:
        crossing = sum(1 for r in new if r["reach"] == "network")
        unknown = sum(1 for r in new if r["reach"] == "unknown")
        lines.append("")
        lines.append(f"{len(new)} unbounded external call"
                     f"{'' if len(new) == 1 else 's'}: {crossing} that leave "
                     f"the machine, {unknown} whose reach this tool could not "
                     f"read, {len(new) - crossing - unknown} local. A call "
                     f"with no bound hangs until the run's own wall and prints "
                     f"nothing while it does.")
    else:
        # A gate whose silence means permission must not be silent, and the
        # number it prints has to be the one a reader can check: how many
        # external calls it actually read, not how many findings it has.
        bounded = len(scope) - len(unbounded)
        accepted_here = len(unbounded) - len(new)
        lines.append(f"unbounded_calls: {len(scope)} external call"
                     f"{'' if len(scope) == 1 else 's'} read, {bounded} bounded"
                     f" in time, {len(unbounded)} unbounded of which "
                     f"{accepted_here} accepted by the baseline. Nothing "
                     f"unaccounted for.")

    stale = stale_rows(rows, accepted)
    if stale:
        where = ", ".join(f"{path}:{line}" for path, line in stale)
        lines.append("")
        lines.append(f"{len(stale)} accepted row"
                     f"{'' if len(stale) == 1 else 's'} matched no unbounded "
                     f"call and should be pruned: {where}. A row that matches "
                     f"nothing is either a call that got its clock or a call "
                     f"that moved, and both want an edit to the accepted set.")
    return new, "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", default=None,
                    help="files or directories; default is tools/ pipeline/ mcp/")
    ap.add_argument("--network-only", action="store_true",
                    help="only calls that leave the machine")
    ap.add_argument("--baseline", type=pathlib.Path, default=None)
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    paths = args.paths or ["tools", "pipeline", "mcp"]
    try:
        rows = scan_paths(paths, root=args.root)
        accepted = load_baseline(args.baseline)
    except CannotLook as exc:
        print(f"unbounded_calls: {exc}", file=sys.stderr)
        print("unbounded_calls: refusing to answer, which is not an answer "
              "of clean", file=sys.stderr)
        return 2

    new, prose = render(rows, accepted, args.network_only)
    if args.json:
        print(json.dumps({
            "scanned": paths,
            "findings": new,
            "calls_read": len(rows),
            "unbounded": sum(1 for r in rows if not r["bounded"]),
            "stale_accepted": [{"path": path, "line": line}
                               for path, line in stale_rows(rows, accepted)],
        }, indent=2))
    else:
        print(prose)
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
