#!/usr/bin/env python3
"""A comment is the part of a module that nothing tests, and this tests one thing about it.

    python3 tools/prose_symbols.py                        # every tracked Python file
    python3 tools/prose_symbols.py tools/ pipeline/       # only these paths
    python3 tools/prose_symbols.py --root /srv/asc/hq     # a tree this repo does not own
    python3 tools/prose_symbols.py --json                 # the verdict as a script reads it
    python3 tools/prose_symbols.py --max-unresolved 0     # opt in to a failing threshold

It answers one question per file: **does every function this file's prose names
in call form actually exist in the file?** Comments and docstrings are the only
part of a module that no test, no type checker and no linter reads, so a name
that is wrong there stays wrong, and the next reader to act on it acts on a
symbol that is not there.

Why the question is worth a tool rather than a rule. The rule already existed:
read a module's prose before you measure its fields. On 2026-11-08
`alexandria/security` obeyed that rule, read `runtime/board/runpr.py`, and sent
this seat an ask naming `runpr.annotate`. There is no `annotate` in that module
and there never has been. Its comments name one twice. The ask was built on the
prose, half of it named nothing, and the half that was left measured as a no-op
-- two seats' runs spent on a function that does not exist. The rule's missing
clause is this file: read the prose, then check the names in it against the
symbol table.

**And the defect was not drift, which is why a rename-discipline rule would not
have caught it.** `corrected_report` was committed 2026-10-24 in `45c50bf4`.
The comment naming `annotate()` was committed 2026-10-26 in `34a95642`, two
days later, in a 27-line pure addition that never touched the function it
mis-names. Nothing was renamed. The prose was wrong when it was written, so
"update the comments when you rename a function" has no event to fire on here.
Only a check that compares prose against the symbol table catches it.

What it looks for, and the narrowness is deliberate. Only **call form** counts:
`name()`, `` `name()` ``, `obj.name()`. A bare backticked word is not a
candidate, because prose uses backticks for paths, flags, column names, literal
strings and sentinels, and a checker that flags those is a checker a seat turns
off. Call form is the spelling a reader reads as "there is a function here",
which is the belief that cost the two runs.

Three verdicts per candidate, and the third is the honest one.

`resolved` -- the name is defined in the file, imported into it, a builtin, or a
method of a class in it.

`unresolved` -- the file's prose names it in call form and the file's symbol
table does not have it. This is the finding. It carries the closest defined name
by edit distance, because a near miss is a typo and a far miss is a function
that was never there: `annotate` against this module's symbols has no near
match at all, and that distance is the tell that it is the second kind.

`unverifiable` -- a dotted call on something this file cannot see, `obj` being a
stdlib module or an object rather than a local import. Counted and not reported
as a finding, because a checker that guesses here manufactures the false
positives that would discredit the two it got right.

Why it is report-only by default. `tools/incidents.py` states the rule: "a gate
that can turn `main` red for a bookkeeping step nobody promised to run is a
worse defect than the one being fixed." A stale comment is a cost paid by the
next reader, not an error, and this repo's prose has never once been checked, so
the first run of this tool measures a backlog rather than a regression. Exit is
0 unless a caller asks for a threshold with `--max-unresolved`, which is how a
sweep opts in without every pull request inheriting the backlog.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import difflib
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Call form, and only call form. Group 1 is an optional dotted qualifier, group
# 2 the name being called. A leading backtick is allowed and not required,
# because prose writes both `` `annotate()` `` and a bare `annotate()`.
CALL_FORM = re.compile(r"(?:(?<![\w.])|`)(?:([A-Za-z_][\w]*)\.)?([a-z_][\w]*)\(\s*\)")

# The prose that claims a symbol is *in this module*, which is the difference
# between a stale name and a fair mention.
#
# A comment is allowed to name things that are not functions of its own file:
# `gather()` is one of this pipeline's stages, `serve()` is an MCP subcommand,
# `gen_random_uuid()` is Postgres's, `hasSpine()` is not even Python. Fifty
# such mentions are in this repo and not one of them is a defect. What makes
# `runpr.py:95` a defect is one word: it writes the missing name in call form
# and then says **below**. The prose tells the reader where to look, the reader
# looks, and there is nothing there -- which is exactly the trip
# `alexandria/security` took on 2026-11-08.
#
# That sentence is deliberately not a verbatim quotation of the defect, and the
# reason is a limitation worth stating rather than hiding: a module documenting
# this class trips its own checker. Quoting the bad comment exactly made this
# file the only finding in its own repository, which is correct behaviour and a
# useless report. There is no clever exemption for quoted prose here -- a
# checker that learns to ignore examples learns to ignore the real thing -- so
# the convention is to name such a symbol without its parentheses.
#
# So locality is the discriminator, and it is reported as a tier rather than
# used as a filter, because the broader set is worth printing and is not worth
# failing a build over.
LOCALITY = re.compile(
    r"\b(below|above|further down|earlier in this file|in this (?:module|file)|"
    r"this (?:module|file)'s|defined here|right here)\b",
    re.IGNORECASE,
)

# Words that appear in call form in prose without ever being a symbol of the
# file that says them. Shell and SQL, mostly, plus the two spellings of a
# generic placeholder.
PROSE_NOT_SYMBOLS = {
    "count", "sum", "min", "max", "avg", "now", "coalesce", "json_extract",
    "echo", "cat", "true", "false", "null", "f", "fn", "foo", "bar", "baz",
}


def tracked_python(root: Path, paths: list[Path]) -> list[Path]:
    """The Python files to read: git's list where git knows, a walk where it does not.

    Asking git rather than walking keeps vendored trees and `__pycache__` out
    without a blocklist that goes stale, and the walk is the fallback for a
    tree that is not a checkout -- which is the case this tool is pointed at
    when it reads the host's runtime.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "*.py"],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout
        files = [root / p for p in out.split("\0") if p]
    except (subprocess.SubprocessError, FileNotFoundError):
        files = [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]
    if paths:
        wanted = [p if p.is_absolute() else (root / p) for p in paths]
        files = [f for f in files if any(
            f == w or w in f.parents for w in wanted)]
    return sorted(files)


def defined_names(tree: ast.AST) -> set[str]:
    """Every name this module binds, at any nesting depth.

    Deliberately generous. A checker reporting a name the module does bind is
    worse than one missing a name it does not, so a nested helper, a method, a
    module constant and an import alias all count as defined.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                names.add(a.asname or a.name)
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            names.add(node.attr)
    return names


def called_names(tree: ast.AST) -> set[str]:
    """Every callable this file's *code* invokes, bare or as an attribute.

    The second half of what a bare call in prose can mean, and the half that
    takes the noise out. `mkdtemp()` in a docstring is not a stale name when the
    body three lines down calls `tempfile.mkdtemp()`; neither is `mkdir()` when
    the file calls `path.mkdir()` on an object whose class this tool cannot see.
    Attribute calls are how a Python file reaches everything it does not define,
    so collecting them is what lets this checker stay narrow without a stdlib
    allowlist that would go stale on its own.

    What survives it is the finding worth having: prose naming a call that
    neither this file nor anything it imports nor anything it ever invokes can
    supply. `runpr.py` does not call `.annotate()` anywhere, which is why that
    one still reports.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def local_imports(tree: ast.AST) -> dict[str, str]:
    """Module aliases to dotted module names, for resolving a dotted call."""
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out[a.asname or a.name.split(".")[0]] = a.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                out[a.asname or a.name] = f"{node.module}.{a.name}"
    return out


def prose_of(path: Path, source: str, tree: ast.AST) -> list[tuple[int, str]]:
    """Every comment and docstring in the file, as (line, text).

    Both halves are needed and they come from different readers: comments only
    exist in the token stream, docstrings only in the tree.
    """
    chunks: list[tuple[int, str]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                chunks.append((tok.start[0], tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                line = getattr(node, "lineno", 1)
                if node.body and isinstance(node.body[0], ast.Expr):
                    line = node.body[0].lineno
                chunks.append((line, doc))
    return chunks


def module_file(path: Path, root: Path, dotted: str) -> Path | None:
    """The file a dotted import names, or None when this tool cannot place it.

    Three tries, narrowest first: the dotted path from the tree root
    (`tools.drift_watch` -> `tools/drift_watch.py`), a sibling of the importing
    file, and the root itself. Returning None is a real answer here -- a stdlib
    or site-packages import is unverifiable, not missing, and guessing at it is
    how a checker earns the false positives that get it switched off.
    """
    parts = dotted.split(".")
    for candidate in (
        root.joinpath(*parts).with_suffix(".py"),
        path.parent / f"{parts[-1]}.py",
        root / f"{parts[-1]}.py",
    ):
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def symbols_of(file: Path, cache: dict[Path, set[str]]) -> set[str]:
    """One module's symbol table, parsed once per run."""
    if file not in cache:
        try:
            cache[file] = defined_names(ast.parse(file.read_text(encoding="utf-8")))
        except (OSError, SyntaxError, UnicodeDecodeError):
            cache[file] = set()
    return cache[file]


def visible_names(path: Path, root: Path, tree: ast.AST,
                  imports: dict[str, str], cache: dict[Path, set[str]]) -> set[str]:
    """Every name a bare call in this file's prose could reasonably mean.

    This file's own symbols, plus the symbols of every module it imports that
    the tree can place. Generous on purpose, and the reason is how prose is
    written rather than how code is: a test that does `from tools import
    drift_watch as dw` and then says "the guard at the top of `watch()`" is
    naming a function that exists, spelled the way a reader says it out loud.
    Scoring that bare name against the test file alone reports 52 findings in
    this repo's `tests/` that are all of them wrong, which is the first thing
    this tool did and the reason it does not now.
    """
    names = defined_names(tree) | called_names(tree)
    placed: set[Path] = set()
    for dotted in set(imports.values()):
        file = module_file(path, root, dotted)
        if file and file != path and file not in placed:
            placed.add(file)
            names |= symbols_of(file, cache)
    return names


def check_file(path: Path, root: Path, cache: dict[Path, set[str]]) -> list[dict]:
    """Every call-form name in this file's prose, with its verdict."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []

    imports = local_imports(tree)
    defined = visible_names(path, root, tree, imports, cache)
    builtin = set(dir(builtins))
    findings: list[dict] = []
    seen: set[tuple[str, int]] = set()

    for line, text in prose_of(path, source, tree):
        for match in CALL_FORM.finditer(text):
            qualifier, name = match.group(1), match.group(2)
            whole = f"{qualifier}.{name}" if qualifier else name
            if (whole, line) in seen:
                continue
            seen.add((whole, line))
            if name in PROSE_NOT_SYMBOLS or name in builtin:
                continue

            if qualifier:
                file = module_file(path, root, imports[qualifier]) if qualifier in imports else None
                if file is None:
                    verdict, pool = "unverifiable", set()
                else:
                    pool = symbols_of(file, cache)
                    verdict = "resolved" if name in pool else "unresolved"
            else:
                pool = defined
                verdict = "resolved" if name in defined else "unresolved"

            if verdict == "resolved":
                continue
            near = difflib.get_close_matches(name, sorted(pool), n=1, cutoff=0.6)
            # Locality is read from the sentence around the mention, not the
            # whole chunk: a module docstring that says "below" once about
            # something else must not promote every name in it.
            # The cue has to attach to *this* name, so the window is tight:
            # a few words after it, a couple before. Both repo findings the
            # first wide version produced were innocent for the same reason --
            # the cue belonged to another symbol in the same sentence.
            # "`schedules()` in `pipeline/runtime_sha.py`" was promoted by a
            # "this file's own" forty characters later about something else,
            # and `schedules` is really there at line 93 of that module.
            window = text[max(0, match.start() - 15):match.end() + 25]
            findings.append({
                "file": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
                "line": line,
                "name": whole,
                "verdict": verdict,
                "nearest": near[0] if near else None,
                "claims_local": bool(LOCALITY.search(window)),
            })
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path, help="limit to these files or directories")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="tree to read")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--verbose", action="store_true",
                        help="also list the mentions that claim no locality")
    parser.add_argument(
        "--max-unresolved", type=int, default=None,
        help="exit 1 when more than this many stale local claims are found (default: report only)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    cache: dict[Path, set[str]] = {}
    files = tracked_python(root, args.paths)
    findings = [f for path in files for f in check_file(path, root, cache)]
    unresolved = [f for f in findings if f["verdict"] == "unresolved"]
    unverifiable = [f for f in findings if f["verdict"] == "unverifiable"]

    stale = [f for f in unresolved if f["claims_local"]]
    mentioned = [f for f in unresolved if not f["claims_local"]]

    report = {
        "root": str(root),
        "files_read": len(files),
        "stale_local_claims": stale,
        "mentioned_not_found": mentioned,
        "unverifiable_count": len(unverifiable),
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{len(files)} Python files read under {root}")
        print(f"{len(stale)} prose claims that a named function is in this module, where it is not")
        for f in stale:
            near = f" (nearest defined name: {f['nearest']})" if f["nearest"] else " (no near match)"
            print(f"  {f['file']}:{f['line']}  {f['name']}(){near}")
        print(f"{len(mentioned)} names mentioned in call form and not found, no claim of locality")
        if args.verbose:
            for f in mentioned:
                print(f"  {f['file']}:{f['line']}  {f['name']}()")
        print(f"{len(unverifiable)} dotted calls this tool cannot place, not counted as findings")

    if args.max_unresolved is not None and len(stale) > args.max_unresolved:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
