#!/usr/bin/env python3
"""Resolve a conflict between two register appends, and prove the resolution lost nothing.

    python3 tools/resolve_register_conflict.py            # resolve what this merge conflicted
    python3 tools/resolve_register_conflict.py --dry-run  # say what it would do, write nothing
    python3 tools/resolve_register_conflict.py --check    # audit a resolution already made

Every seat appends to the same handful of Markdown registers, so two runs a day
apart meet at the same anchor and the second one resolves a conflict it did not
plan for. The instruction in the charters is "keep both sides in arrival order",
which is correct and which has been followed correctly and incorrectly in
roughly equal measure: nine entries in `docs/agents/incidents.md` are conflict
markers that reached `main`, and
`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`
is the first one where the resolution left valid Markdown and deleted a third
seat's line instead. That one was caught by a counter kept for another purpose.

The ledger entry of 2026-10-09 ("Resolving a conflict between two register
appends is mechanical, so stop asking seats to guess it", writer seat, filed for
this seat) asked for this file and named its recipe. Two modes, because the
2026-10-24 damage happened inside a resolution that was already finished.

**Resolve.** For each conflicted register, read the three stages git already
holds: the merge base, ours, theirs. When ours is the base plus a trailing block
and theirs is the base plus a trailing block, the answer is the base plus both
blocks, ours first, because ours is the side that is already on the trunk. When
either side changed anything that is not the end of the file, this refuses the
file and leaves it for a hand. Concatenating a change that is not an append is
how a resolution damages a record.

**Check.** The arithmetic that makes the claim testable, which is the half a
recipe usually lacks. For an append-only file, every line's count in the
resolution is fixed by its count in the three inputs:

    count(resolved) == count(ours) + count(theirs) - count(base)

Fewer means the resolution deleted a line that one side had, which is the
2026-10-24 incident. More means it duplicated one, which is what `merge=union`
does on the shared trailing lines of two appended entries and the measured
reason L-A49 forbids that attribute. Both are findings and neither leaves a
marker, so both are counted here rather than looked for.

`--check` reads a merge commit rather than an index, so it audits work that is
already committed and pushed. With no argument it reads `HEAD`, which is the
useful default in the turn after a merge.

Exit codes: 0 when everything asked for was resolved or verified, 1 when a file
was refused or an invariant failed, 2 when there was nothing to look at and the
run therefore says nothing about whether the registers are intact (L-A21: a
gate that saw nothing must not read as a quiet pass).
"""

import argparse
import collections
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RESOLVED, REFUSED, NOTHING = "resolved", "refused", "nothing"

EXIT = {RESOLVED: 0, REFUSED: 1, NOTHING: 2}


def _registers() -> list[str]:
    """The append-only register list, read from the checker that already owns it.

    One list, one place. `tools/check_registers.py` grew from eight files to
    nineteen across three seats' runs, and a second copy here would be stale the
    first time it grew again.
    """
    spec = importlib.util.spec_from_file_location(
        "check_registers", Path(__file__).resolve().parent / "check_registers.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return list(module.REGISTERS)


def git(*args, repo=ROOT, check=True) -> subprocess.CompletedProcess:
    done = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)
    if check and done.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({done.returncode}): {done.stderr.strip()}")
    return done


def lines(text: str) -> list[str]:
    """A file as a list of lines, with the trailing newline's empty tail dropped.

    Every register is line-oriented Markdown and every operation here is about
    whole lines, so the comparison is done on this list and never on the string.
    """
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out


def blob(ref: str, path: str, repo=ROOT) -> str | None:
    done = git("show", f"{ref}:{path}", repo=repo, check=False)
    return done.stdout if done.returncode == 0 else None


def conflicted(repo=ROOT) -> list[str]:
    """The paths git has left in an unmerged state in the index."""
    return git("diff", "--name-only", "--diff-filter=U",
               repo=repo).stdout.split()


def trailing_block(base: list[str], side: list[str]) -> list[str] | None:
    """`side` as the base plus a trailing block, or None if it changed anything else.

    A register append adds at the end and touches nothing above it. Anything
    else — an edited status, a reordered entry, a deleted line — is a change
    this tool must not resolve, because keeping both sides of it is not the same
    operation as keeping both appends.
    """
    if side[:len(base)] != base:
        return None
    return side[len(base):]


def counts(text: str) -> collections.Counter:
    return collections.Counter(lines(text))


def audit(base: str, ours: str, theirs: str, resolved: str) -> list[str]:
    """The arithmetic. Returns one finding per line whose count is wrong."""
    cb, co, ct, cr = counts(base), counts(ours), counts(theirs), counts(resolved)
    findings = []
    for line in set(cb) | set(co) | set(ct) | set(cr):
        expected = co[line] + ct[line] - cb[line]
        if cr[line] != expected:
            verb = "dropped" if cr[line] < expected else "duplicated"
            findings.append(
                f"{verb}: {cr[line]} of an expected {expected} "
                f"(base {cb[line]}, ours {co[line]}, theirs {ct[line]}): "
                f"{line.strip()[:72] or '<blank line>'}")
    return sorted(findings)


def resolve_one(path: str, repo=ROOT, write=True) -> tuple[str, list[str]]:
    """Resolve one conflicted register from the index's three stages."""
    base, ours, theirs = (blob(f":{n}", path, repo=repo) for n in (1, 2, 3))
    if base is None or ours is None or theirs is None:
        return REFUSED, [f"{path}: refused, the index does not hold all three "
                         f"stages (a file added on both sides is not an append)"]

    lb = lines(base)
    ours_tail = trailing_block(lb, lines(ours))
    theirs_tail = trailing_block(lb, lines(theirs))
    if ours_tail is None or theirs_tail is None:
        which = "ours" if ours_tail is None else "theirs"
        return REFUSED, [f"{path}: refused, {which} changed something that is not "
                         f"the end of the file, so this is not two appends"]

    merged = lb + ours_tail + theirs_tail
    text = "\n".join(merged) + "\n"
    findings = audit(base, ours, theirs, text)
    if findings:
        return REFUSED, [f"{path}: refused, the resolution would not balance"] + \
            [f"  {f}" for f in findings]

    if write:
        (Path(repo) / path).write_text(text)
        git("add", "--", path, repo=repo)
    return RESOLVED, [f"{path}: kept both appends, ours first "
                      f"({len(ours_tail)} lines) then theirs ({len(theirs_tail)} lines)"]


def check_commit(ref: str, repo=ROOT, registers=None) -> tuple[str, list[str]]:
    """Audit a merge commit that already exists, which is the mode for a pushed branch."""
    registers = registers if registers is not None else _registers()
    parents = git("rev-list", "--parents", "-n", "1", ref, repo=repo).stdout.split()
    if len(parents) != 3:
        return NOTHING, [f"{ref} is not a two-parent merge, so there is no "
                         f"resolution here to audit"]
    _, ours_ref, theirs_ref = parents
    base_ref = git("merge-base", ours_ref, theirs_ref, repo=repo).stdout.strip()

    report, state = [], NOTHING
    for path in registers:
        base, ours, theirs, resolved = (blob(r, path, repo=repo) for r in
                                        (base_ref, ours_ref, theirs_ref, ref))
        if None in (base, ours, theirs, resolved):
            continue
        if ours == theirs == resolved:
            continue
        state = RESOLVED if state == NOTHING else state
        findings = audit(base, ours, theirs, resolved)
        if findings:
            state = REFUSED
            report.append(f"{path}: the resolution in {ref[:9]} does not balance")
            report.extend(f"  {f}" for f in findings)
        else:
            report.append(f"{path}: balanced, every line of both sides is present once")
    if state == NOTHING:
        report.append(f"{ref[:9]} merged no register, so this run is not a "
                      f"verdict on the registers")
    return state, report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", nargs="?", const="HEAD", metavar="REF",
                    help="audit an existing merge commit instead of the index "
                         "(default HEAD)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the resolution without writing or staging it")
    ap.add_argument("--repo", default=ROOT, type=Path,
                    help="the checkout to work in (default this repository)")
    args = ap.parse_args(argv)
    repo = args.repo

    if args.check:
        state, report = check_commit(args.check, repo=repo)
        for line in report:
            print(line)
        return EXIT[state]

    registers = set(_registers())
    paths = conflicted(repo=repo)
    if not paths:
        print("no conflicted file in the index, so nothing here is a verdict "
              "on the registers")
        return EXIT[NOTHING]

    state, report = NOTHING, []
    for path in sorted(paths):
        if path not in registers:
            state = REFUSED
            report.append(f"{path}: refused, not an append-only register "
                          f"(tools/check_registers.py keeps the list)")
            continue
        one, said = resolve_one(path, repo=repo, write=not args.dry_run)
        report.extend(said)
        state = REFUSED if REFUSED in (state, one) else RESOLVED

    for line in report:
        print(line)
    if state == RESOLVED and not args.dry_run:
        print("staged. Every other conflicted file is still yours.")
    return EXIT[state]


if __name__ == "__main__":
    sys.exit(main())
