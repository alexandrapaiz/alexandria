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
blocks. When either side changed anything that is not the end of the file, this
refuses the file and leaves it for a hand. Concatenating a change that is not an
append is how a resolution damages a record.

**Which block goes first is decided by the stamp the block carries, not by which
side git calls ours.** This tool's first version concatenated ours then theirs
unconditionally, on the premise that ours is already on the trunk. That premise
holds in one merge direction and the seats use the other: a seat clearing a
conflict runs `git merge origin/main` from its own branch, because that is how
you do it without rewriting pushed history, so ours is the branch and theirs is
the trunk. In a register ordered by time that put the newer entry above the
older one, measured on two real registers by the ExO seat on 2026-11-09 and
resolved by hand both times
(`INC-2026-11-09-the-register-resolver-orders-two-appends-backwards-in-the-only-merge-direction-we-use`).

So the order comes from the register's own content. Every register entry heading
carries a date, often a time with it, and the block with the earlier stamp goes
first. When both blocks carry the same stamp, or when one carries none, the
stamp cannot decide it and the tool falls back to putting the trunk side first,
labelling the trunk from ancestry against `origin/main` rather than from the
word "ours". When neither rule can speak, the file is refused. Guessing an order
is what the first version did.

**Check.** The arithmetic that makes the claim testable, which is the half a
recipe usually lacks. For an append-only file, every line's count in the
resolution is fixed by its count in the three inputs:

    count(resolved) == count(ours) + count(theirs) - count(base)

Fewer means the resolution deleted a line that one side had, which is the
2026-10-24 incident. More means it duplicated one, which is what `merge=union`
does on the shared trailing lines of two appended entries and the measured
reason L-A49 forbids that attribute. Both are findings and neither leaves a
marker, so both are counted here rather than looked for.

That arithmetic is a line multiset, and a multiset is order-independent, so it
read balanced on both registers the ExO seat found written backwards. It is
right about the deletion it was built for and blind to the ordering, which is
why it now has a companion: the stamps of the two appended blocks must be
non-decreasing in the resolution. Two checks, because the two defects are
different and the first one cannot see the second.

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
import re
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


class GitUnavailable(Exception):
    """git could not be asked, which is not an answer about the tree."""


def git(*args, repo=ROOT, check=True) -> subprocess.CompletedProcess:
    """One git command, with a hang kept apart from an answer.

    A non-zero exit is git answering, and `check` decides whether the caller
    reads it or this raises. A timeout or a missing git binary is git saying
    nothing at all, and that raises whatever `check` says, because `check=False`
    is a caller asking to read an exit code and not a caller asking to be lied
    to. The timeout was missing entirely until 2026-11-09.
    """
    try:
        done = subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, timeout=60)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise GitUnavailable(f"git {' '.join(args)}: {exc}") from exc
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


# The index stages, which are a ref this tool reads but `rev-parse` does not
# resolve as a tree. The index exists whenever git does, so for these three the
# only thing `show` can fail on is already the path.
_INDEX_STAGES = {":1", ":2", ":3"}


def blob(ref: str, path: str, repo=ROOT) -> str | None:
    """The file at a ref, or None when git resolved the tree and the path is not in it.

    None has to mean one thing, and until 2026-11-09 it meant two. `git show`
    exits non-zero both for a path absent from a tree and for a ref it cannot
    resolve at all, so a missing or mistyped ref came back as "the register is
    not there" and `check_commit` skipped that register in silence. That is this
    tool's own worst failure mode, because the reason it exists is that a hand
    resolution dropped three lines with nothing to notice, so an auditor that
    quietly audits fewer registers than it was asked about is the same defect
    wearing the instrument's name.

    The two are separated structurally rather than by reading git's prose. The
    ref is resolved on its own first, so the only question left for `show` is
    the path, and a ref that does not resolve raises instead of answering. A
    stderr allowlist was the first attempt here and it was the same mistake one
    layer down: matching English is a decision about a message, and git has more
    messages than any list will hold. This repository's own suite caught it.
    """
    if ref not in _INDEX_STAGES:
        probe = git("rev-parse", "--verify", "--quiet", f"{ref}^{{tree}}",
                    repo=repo, check=False)
        if probe.returncode != 0:
            raise RuntimeError(
                f"{ref} does not resolve to a tree in this checkout, so nothing "
                f"can be read at it and no register was audited there")
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


STAMP = re.compile(r"(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?")

TRUNK_REFS = ("refs/remotes/origin/main", "refs/heads/main")


def stamp(block: list[str]) -> tuple[tuple, str] | None:
    """The ordering key an appended block carries, and the line it was read from.

    Every shape a register entry heading takes in this repository leads with a
    date, and that is the only part of the heading the shapes agree on:

        ### 2026-11-09 - Idea name                      (docs/ideas.md)
        ## INC-2026-11-09-slug - what happened (...)    (docs/agents/incidents.md)
        ## 2026-11-09 09:12Z - message wake             (docs/agents/learning-log.md)
        ## Queued 2026-11-09 by the skill seat          (docs/research/reading-queue.md)

    So the key is the first date in the block, with the time beside it when
    there is one, and the line it came from is returned with it because the
    ordering check needs to find that line again in the resolution. A block with
    no date at all returns None, and a None is refused rather than guessed.
    """
    for line in block:
        found = STAMP.search(line)
        if found:
            year, month, day, hour, minute = found.groups()
            key = (int(year), int(month), int(day),
                   int(hour) if hour else -1, int(minute) if minute else -1)
            return key, line
    return None


def trunk_side(repo=ROOT) -> str | None:
    """Which of the two merge heads is the trunk, by ancestry rather than by name.

    `ours` and `theirs` are a fact about the direction somebody typed the merge
    in, not about the repository, which is the whole defect this answers. The
    trunk is a fact about the repository: it is the side already reachable from
    `main`. Returns "ours", "theirs", or None when neither side or both sides
    are reachable, which is the honest answer for two branches merged off-trunk.
    """
    head = git("rev-parse", "HEAD", repo=repo, check=False)
    other = git("rev-parse", "MERGE_HEAD", repo=repo, check=False)
    if head.returncode != 0 or other.returncode != 0:
        return None
    return _trunk_of(head.stdout.strip(), other.stdout.strip(), repo=repo)


def _trunk_of(ours_ref: str, theirs_ref: str, repo=ROOT) -> str | None:
    trunk = next((r for r in TRUNK_REFS
                  if git("rev-parse", "--verify", "--quiet", r,
                         repo=repo, check=False).returncode == 0), None)
    if trunk is None:
        return None

    def reachable(ref: str) -> bool:
        return git("merge-base", "--is-ancestor", ref, trunk,
                   repo=repo, check=False).returncode == 0

    ours, theirs = reachable(ours_ref), reachable(theirs_ref)
    if ours == theirs:
        return None
    return "ours" if ours else "theirs"


def order_blocks(ours_tail: list[str], theirs_tail: list[str],
                 repo=ROOT, trunk=None) -> tuple[list[str], list[str], str] | tuple[None, None, str]:
    """The two appended blocks in the order the register wants, and why.

    Returns `(first, second, reason)`, or `(None, None, refusal)` when no rule
    can decide it. An empty block is not an append and sorts before anything,
    since there is nothing of it to be out of order.
    """
    if not ours_tail or not theirs_tail:
        return ours_tail, theirs_tail, "one side appended nothing"

    ours_stamp, theirs_stamp = stamp(ours_tail), stamp(theirs_tail)
    if ours_stamp and theirs_stamp and ours_stamp[0] != theirs_stamp[0]:
        if ours_stamp[0] < theirs_stamp[0]:
            return ours_tail, theirs_tail, "stamp order, ours is the earlier block"
        return theirs_tail, ours_tail, "stamp order, theirs is the earlier block"

    why = ("both blocks carry the same stamp" if ours_stamp and theirs_stamp
           else "a block carries no stamp")
    trunk = trunk_side(repo=repo) if trunk is None else trunk
    if trunk == "ours":
        return ours_tail, theirs_tail, f"{why}, so trunk order, ours is the trunk"
    if trunk == "theirs":
        return theirs_tail, ours_tail, f"{why}, so trunk order, theirs is the trunk"
    return None, None, (f"{why} and neither side is reachable from the trunk, "
                        f"so no rule here can order them")


def order_findings(base: str, ours: str, theirs: str, resolved: str) -> list[str]:
    """The companion to the arithmetic: the two blocks' stamps must not decrease.

    The line-count audit is a multiset and a multiset is order-independent, so
    it reads balanced on a register written backwards. This reads the order.
    Silent when it cannot localise a block in the resolution, because a check
    that guesses is worse than one that abstains (L-A21).
    """
    lb = lines(base)
    ours_tail = trailing_block(lb, lines(ours))
    theirs_tail = trailing_block(lb, lines(theirs))
    if not ours_tail or not theirs_tail:
        return []

    ours_stamp, theirs_stamp = stamp(ours_tail), stamp(theirs_tail)
    if not ours_stamp or not theirs_stamp or ours_stamp[0] == theirs_stamp[0]:
        return []

    body = lines(resolved)
    places = {}
    for side, (key, probe) in (("ours", ours_stamp), ("theirs", theirs_stamp)):
        if body.count(probe) != 1:
            return []
        places[side] = (body.index(probe), key, probe)

    first, second = sorted(places.values())
    if first[1] <= second[1]:
        return []
    return [f"out of order: {_say(first[1])} is above {_say(second[1])}, "
            f"so the newer block landed first: {first[2].strip()[:60]}"]


def _say(key: tuple) -> str:
    year, month, day, hour, minute = key
    clock = f" {hour:02d}:{minute:02d}" if hour >= 0 else ""
    return f"{year:04d}-{month:02d}-{day:02d}{clock}"


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

    first, second, why = order_blocks(ours_tail, theirs_tail, repo=repo)
    if first is None:
        return REFUSED, [f"{path}: refused, {why}"]

    merged = lb + first + second
    text = "\n".join(merged) + "\n"
    findings = audit(base, ours, theirs, text) + \
        order_findings(base, ours, theirs, text)
    if findings:
        return REFUSED, [f"{path}: refused, the resolution would not balance"] + \
            [f"  {f}" for f in findings]

    lead = "ours" if first is ours_tail else "theirs"
    trail = "theirs" if first is ours_tail else "ours"
    if write:
        (Path(repo) / path).write_text(text)
        git("add", "--", path, repo=repo)
    return RESOLVED, [f"{path}: kept both appends, {lead} first "
                      f"({len(first)} lines) then {trail} "
                      f"({len(second)} lines), by {why}"]


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
    absent = []
    for path in registers:
        base, ours, theirs, resolved = (blob(r, path, repo=repo) for r in
                                        (base_ref, ours_ref, theirs_ref, ref))
        if None in (base, ours, theirs, resolved):
            # Git has said this register is not in all four trees, which is a
            # real answer and not a skip. It is named rather than passed over,
            # because coverage that is narrower than the question reads exactly
            # like a verdict on the whole question.
            absent.append(path)
            continue
        if ours == theirs == resolved:
            continue
        state = RESOLVED if state == NOTHING else state
        findings = audit(base, ours, theirs, resolved) + \
            order_findings(base, ours, theirs, resolved)
        if findings:
            state = REFUSED
            report.append(f"{path}: the resolution in {ref[:9]} does not balance")
            report.extend(f"  {f}" for f in findings)
        else:
            report.append(f"{path}: balanced, every line of both sides is present "
                          f"once and the blocks' stamps do not decrease")
    if absent:
        report.append(f"{len(absent)} of {len(registers)} registers are not in "
                      f"all four trees of this merge and were not audited: "
                      f"{', '.join(absent)}")
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

    try:
        return _run(args, repo)
    except GitUnavailable as exc:
        print(f"resolve_register_conflict: git could not be asked, so no "
              f"register was audited: {exc}", file=sys.stderr)
        return EXIT[NOTHING]
    except RuntimeError as exc:
        print(f"resolve_register_conflict: {exc}", file=sys.stderr)
        return EXIT[NOTHING]


def _run(args, repo) -> int:

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
