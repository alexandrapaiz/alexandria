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
why it now has a companion: the resolution must put the two appended blocks in
the order the register wants. Two checks, because the two defects are different
and the first one cannot see the second.

**One ordering rule, and both modes run it.** The companion used to compare the
two stamps on its own, which meant the check answered a narrower question than
the resolver asked: it read nothing at all when the two blocks tied, and the
tie is the ordinary case here rather than the rare one (46 stamped register
headings carry a clock and 1,692 carry a date only, counted 2026-11-09). So the
trunk fallback, which is the rule that decides the ordinary case, was the one
rule the auditor never verified. Both now call `order_blocks`, which is the only
place an order is decided, and `--check` reads the trunk from the merge's own
two parents rather than from a `MERGE_HEAD` it does not have (both findings:
ExO seat, 2026-11-09, on PR #921).

**And an ordering the check could not read is its own verdict, never a pass.**
`--check` used to print "the blocks' stamps do not decrease" on every balanced
register, including the ones where nothing read the order. That sentence is now
printed only when a block really was located in the resolution and compared,
and exit 3 says at least one ordering went unread (L-A21).

Expect exit 3 to be ordinary rather than alarming on a trunk merge. The
ordering half can only speak about a merge of two appends, and a week of other
seats' entries folded into the middle of a register is not an append, so the
honest answer there is that the arithmetic balanced and the order was not read.
Exit 1 is still the only answer that means something is wrong.

**Precedence against the parent's merger, which is a question this file has to
answer rather than hold.** HQ keeps an entry-keyed three-way merger,
`tools/merge-register.py`, and `docs/agents/exo-owed.md` row 17 asks to vendor
it here. The two tools disagree: HQ's orders a date-keyed register by theirs'
order verbatim and then the entries only ours has, so on the same three stages
it puts the trunk's newer entry above the branch's older one, and this file's
own `--check` refuses that output
(`INC-2026-11-09-the-parent-merger-this-seat-asked-to-vendor-and-the-gate-we-shipped-this-morning-order-the-same-two-appends-differently`,
reproduced by the ExO seat; the earlier claim from this seat that the two
converge was wrong and was never run).

The precedence is a precondition on the input and not a ranking of the tools,
because their domains barely overlap. HQ's handles a register that is inserted
into mid-file, where rebuilding from the base relocates everything the mainline
added, and that is the case this file refuses outright. Where both can speak,
which is a conflict that is a pure trailing append on both sides, the rule here
governs, for three reasons that are about this repository rather than about
taste:

1. **Confluence.** The same two appends must resolve to the same bytes however
   the merge was typed, because the auditor cannot know which way it was typed.
   The stamp and the trunk label are both facts about content and ancestry, so
   they are direction-independent, and that was measured: the same conflict
   merged both ways gives one blob. A rule keyed on the words "ours" and
   "theirs" is keyed on the direction, so it cannot have that property.
2. **The registers are ascending and none of them is newest-first.** Counted
   over all 16 registers on 2026-11-09 with this file's own `stamp()`: every one
   whose entries carry stamps is ascending-dominant, `docs/ideas.md` 81 ascents
   to 32 descents, `docs/agents/incidents.md` 63 to 24,
   `docs/agents/learning-log.md` 18 to 3, `docs/agents/hq-relay.md` 18 to 6,
   `docs/research/reading-queue.md` 12 to 1, and the descents are backdated
   entries rather than a file maintained in reverse. So "stamps ascend down the
   file" is the invariant these files already hold, and `fold` and `prior` sort
   on it.
3. **HQ's measured reason survives here anyway.** Their argument is diff churn
   from relocation. This file never rebuilds from the base: the base is kept
   byte-identical and only the two new blocks are placed, so the most it can
   relocate is one trailing block at the end of the file, never everything the
   mainline inserted.

`--check` reads a merge commit rather than an index, so it audits work that is
already committed and pushed. With no argument it reads `HEAD`, which is the
useful default in the turn after a merge.

Exit codes: 0 when everything asked for was resolved or verified, 1 when a file
was refused or an invariant failed, 2 when there was nothing to look at and the
run therefore says nothing about whether the registers are intact, 3 when the
arithmetic balanced everywhere and at least one register's ordering could not be
read (L-A21: a gate that saw nothing must not read as a quiet pass, and that
applies to the half of a gate that saw nothing as much as to the whole of one).
"""

import argparse
import collections
import importlib.util
import re
import subprocess
import sys
import typing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RESOLVED, REFUSED, NOTHING, UNREAD = "resolved", "refused", "nothing", "unread"

EXIT = {RESOLVED: 0, REFUSED: 1, NOTHING: 2, UNREAD: 3}


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


def stamp_decides(ours_key: tuple, theirs_key: tuple) -> str | None:
    """Which of two stamps is the earlier one, when they can be compared at all.

    Returns "ours", "theirs", or None for a tie this rule must not break.

    Two stamps on different days compare on the day. Two stamps on one day
    compare only when both carry a clock. A bare date is not midnight: it is a
    heading whose author did not record a time, so "the bare date sorts before
    any time on that day" is a guess wearing a rule's clothes, and guessing an
    order is the defect this tool was rebuilt to stop. The tie goes to the trunk
    fallback, which has a reason, instead.

    This matters because of how the registers are actually stamped. Of the
    stamped headings in the 16 registers, 46 carry a clock and 1,692 carry a
    date only, so a mixed pair on one day is the shape a same-day conflict here
    most often takes.
    """
    if ours_key[:3] != theirs_key[:3]:
        return "ours" if ours_key[:3] < theirs_key[:3] else "theirs"
    clocked = (ours_key[3] >= 0, theirs_key[3] >= 0)
    if not all(clocked) or ours_key == theirs_key:
        return None
    return "ours" if ours_key < theirs_key else "theirs"


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
    """Which of two merge parents is the trunk side, along the trunk's own spine.

    Containment is read along `--first-parent` rather than with
    `merge-base --is-ancestor`, and the difference is the whole of whether
    `--check` can answer this at all. Plain ancestry works mid-merge, when the
    branch is not on the trunk yet, and goes degenerate the moment the merge
    lands: both parents of a merged commit are ancestors of `main`, so the test
    answers "both" and the rule abstains on exactly the merges a seat asks it
    about after the fact.

    The trunk's spine does distinguish them, in both shapes this repository
    produces. A branch-local `git merge origin/main` puts the trunk second, and
    the trunk's spine holds that parent and not the branch head. A merged pull
    request puts the trunk first, and the trunk's spine holds the merge itself
    and so its first parent, never the branch. Returns None when the spine holds
    both or neither, which is the honest answer for two branches merged
    off-trunk and for a parent whose branch was force-pushed away.
    """
    trunk = next((r for r in TRUNK_REFS
                  if git("rev-parse", "--verify", "--quiet", r,
                         repo=repo, check=False).returncode == 0), None)
    if trunk is None:
        return None

    spine = set(git("rev-list", "--first-parent", trunk,
                    repo=repo, check=False).stdout.split())
    if not spine:
        return None

    def on_spine(ref: str) -> bool:
        full = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}",
                   repo=repo, check=False).stdout.strip()
        return bool(full) and full in spine

    ours, theirs = on_spine(ours_ref), on_spine(theirs_ref)
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
    decided = (stamp_decides(ours_stamp[0], theirs_stamp[0])
               if ours_stamp and theirs_stamp else None)
    if decided == "ours":
        return ours_tail, theirs_tail, "stamp order, ours is the earlier block"
    if decided == "theirs":
        return theirs_tail, ours_tail, "stamp order, theirs is the earlier block"

    if not ours_stamp or not theirs_stamp:
        why = "a block carries no stamp"
    elif ours_stamp[0] == theirs_stamp[0]:
        why = f"both blocks carry {_say(ours_stamp[0])}"
    else:
        why = (f"both blocks carry {_say(ours_stamp[0][:3] + (-1, -1))} and only "
               f"one of them carries a clock")
    trunk = trunk_side(repo=repo) if trunk is None else trunk
    if trunk == "ours":
        return ours_tail, theirs_tail, f"{why}, so trunk order, ours is the trunk"
    if trunk == "theirs":
        return theirs_tail, ours_tail, f"{why}, so trunk order, theirs is the trunk"
    return None, None, (f"{why} and neither side is reachable from the trunk, "
                        f"so no rule here can order them")


class OrderVerdict(typing.NamedTuple):
    """What the ordering check found, and whether it read anything at all.

    `read` is the field the caller must not drop. A `findings` list that is
    empty because the blocks are in the right order and one that is empty
    because nothing could be compared are the same value and opposite answers,
    and printing one sentence for both is how this check spent its first day
    asserting an order it had never looked at.
    """

    findings: list[str]
    said: str
    read: bool


def order_verdict(base: str, ours: str, theirs: str, resolved: str,
                  repo=ROOT, trunk=None) -> OrderVerdict:
    """The companion to the arithmetic: the blocks must sit in the register's order.

    The line-count audit is a multiset and a multiset is order-independent, so
    it reads balanced on a register written backwards. This reads the order, and
    it reads it against `order_blocks`, which is the one place in this tool that
    decides an order. That is deliberate: an auditor with a rule of its own
    verifies its own rule rather than the resolver's, and the two drifted apart
    on the commonest case here for exactly that reason.

    Abstains, rather than guessing, when no rule can order the two blocks or
    when a block is not in the resolution whole and once (L-A21).
    """
    lb = lines(base)
    ours_tail = trailing_block(lb, lines(ours))
    theirs_tail = trailing_block(lb, lines(theirs))
    body = lines(resolved)

    if ours_tail is None or theirs_tail is None:
        which = "ours" if ours_tail is None else "theirs"
        return OrderVerdict([], f"{which} changed something that is not the end "
                                f"of the file, so this is not two appends and "
                                f"the order was not read", False)

    # One side appended and the other did not, which is most merges. There is no
    # order between two blocks to read, and there is still something to read:
    # the one block has to be at the end, and the line arithmetic cannot see
    # where in the file a block landed.
    if not ours_tail or not theirs_tail:
        only = ours_tail or theirs_tail
        if not only:
            return OrderVerdict([], "neither side appended, so there is no "
                                    "order to read", False)
        at = _locate(body, only)
        if at is None:
            return OrderVerdict([], "the one appended block is not in the "
                                    "resolution whole and once, so the order "
                                    "was not read", False)
        if at + len(only) == len(body):
            return OrderVerdict([], "one side appended and its block is last in "
                                    "the resolution", True)
        return OrderVerdict(
            [f"out of order: the one appended block is not last in the "
             f"resolution, {len(body) - at - len(only)} lines follow it: "
             f"{only[0].strip()[:60] or only[min(1, len(only) - 1)].strip()[:60]}"],
            "one side appended and its block is not last", True)

    first, second, why = order_blocks(ours_tail, theirs_tail, repo=repo, trunk=trunk)
    if first is None:
        return OrderVerdict([], f"the order could not be decided, so it was "
                                f"not read: {why}", False)

    at_first, at_second = _locate(body, first), _locate(body, second)
    if at_first is None or at_second is None:
        return OrderVerdict([], "a block is not in the resolution whole and "
                                "once, so the order was not read", False)
    if at_first < at_second:
        return OrderVerdict([], f"the blocks are in order by {why}", True)

    # The resolution leads with the block that should have been second.
    led, followed = stamp(second), stamp(first)
    if led and followed and led[0] != followed[0]:
        detail = (f"{_say(led[0])} is above {_say(followed[0])}, so the newer "
                  f"block landed first: {led[1].strip()[:60]}")
    else:
        detail = (f"the block that leads by {why} is second instead: "
                  f"{first[0].strip()[:60]}")
    return OrderVerdict([f"out of order: {detail}"],
                        f"the blocks are in the other order than {why} gives",
                        True)


def _locate(body: list[str], block: list[str]) -> int | None:
    """Where a block sits in the resolution, when it sits there whole and once.

    `None` is "I could not find it", which is what the caller turns into an
    abstention. A block that appears twice is as unlocatable as one that appears
    never, because picking either copy would be a guess.
    """
    if not block:
        return None
    hits = [i for i in range(len(body) - len(block) + 1)
            if body[i:i + len(block)] == block]
    return hits[0] if len(hits) == 1 else None


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
        order_verdict(base, ours, theirs, text, repo=repo).findings
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
    # The trunk, from the merge's own two parents. `trunk_side` reads
    # `MERGE_HEAD`, which exists only mid-merge, so before this the ordering
    # rule that decides the ordinary case was the one `--check` never ran.
    trunk = _trunk_of(ours_ref, theirs_ref, repo=repo)

    report, state = [], NOTHING
    absent, unread = [], []
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
        state = RESOLVED if state in (NOTHING, UNREAD) else state
        order = order_verdict(base, ours, theirs, resolved, repo=repo, trunk=trunk)
        findings = audit(base, ours, theirs, resolved) + order.findings
        if findings:
            state = REFUSED
            report.append(f"{path}: the resolution in {ref[:9]} does not balance")
            report.extend(f"  {f}" for f in findings)
        else:
            report.append(f"{path}: balanced, every line of both sides is present "
                          f"once, and {order.said}")
        if not order.read:
            unread.append(path)
    if unread and state != REFUSED:
        state = UNREAD
    if unread:
        report.append(f"{len(unread)} of the audited registers had an ordering "
                      f"nothing could read, so this run is not a verdict on "
                      f"their order: {', '.join(unread)}")
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
