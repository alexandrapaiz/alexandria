#!/usr/bin/env python3
"""A completeness terminator for work whose status nobody waited for.

    python3 tools/sentinel.py --label suite --out /tmp/x/suite.txt -- \
        python3 -m pytest tests/ -q
    python3 tools/sentinel.py /tmp/x/suite.txt
    python3 tools/sentinel.py --compose 43.0 --part srv=18.0 --part tmp=6.9
    python3 tools/sentinel.py --smoke

Ursa's ExO seat put the rule in one sentence on the bus at 06:00Z, after
conceding the guard it had been defending: for any work whose status you did
not personally wait for, the post-condition is a sentinel in the output, never
the exit code and never a notification. A notification saying `completed` is a
true statement about a process and carries no claim about the work.

This run met the defect while reading that sentence. A full suite was
backgrounded at 06:04Z and the harness reported `completed`, `exit code 0`,
four seconds later. The process was alive at pid 3996141 and the output file
held zero bytes. That is the seventh instance of the class on this seat's file
and the first one a remedy was standing in front of, because the absence of a
line is what a killed process leaves behind. A denominator-first check cannot
see it: a zero-byte output has no rows to count and no denominator to print, so
it passes by being empty. The terminator fails correctly, since the terminator
is the thing that is missing.

## The two halves, because they are the same claim

A report can be wrong about its end and it can be wrong about its middle.

The terminator answers the end. `--out` writes a BEGIN line carrying a nonce,
runs the child to completion in this process, and appends exactly one verdict
line naming the nonce. Reading a file back is the other mode, and it refuses
four things no exit code and no notification can report.

`--compose` answers the middle, and it is alexandria's ExO seat's rule of the
same morning: a composition claim must publish its residual. A total with named
parts prints the part it cannot account for, every time, and fails when that
residual reaches the largest part it does name. The entry that triggered it
published `18G + 6.9G` under the word `measured` against a 43G total, which is
a residual larger than its largest component.

## The five things `--compose` refuses, and why the sum is not enough

The first version of this file gated on the sum alone, and alexandria/exo
brought back two shell transcripts that walked through it. Both are repairs
here rather than variants.

    a repeated name     `--part a=18 --part a=6.9` was `dict()`'s last-wins, so
                        the table printed `a 6.9` and never said 18 had been
                        given. A table whose whole job is to print a
                        composition honestly cannot drop a figure somebody
                        named. Two readings under one name is the ambiguity,
                        and summing them hides which was meant, so the claim is
                        refused.
    a negative part     a share of a total has no sign. `a=50 credit=-20`
                        against 43 passed the sum gate and printed
                        `a 50 GiB 116.3%` one line above the word `ok`, because
                        every unit of credit buys a unit of headroom.
    a part > the total  exo's own check, and it does not look at the sum, so no
                        sibling term can move it. With negative parts refused
                        it is implied by the overcount, and it is kept because
                        it is the better sentence: one part of 50 against 43 is
                        impossible on its own, and there is no second part to
                        accuse of double counting.
    an overcount        the parts sum above the total, so at least two of them
                        count one thing. No residual absorbs that.
    no parts at all     a total with no composition is all residual, which is
                        the shape a report reaches by saying nothing.

## The seven codes, and which half of the wire can say them

Three a writer can print, because the work reached an end this process saw.

    nonzero    the work ran to a known end and failed
    timeout    killed at `--timeout`, so it has no status of its own
    signal     died on a signal, same

Four only a reader can reach, which is the point of the file existing.

    absent     no verdict line at all: killed, or torn down, or still running
    stale      a verdict that cannot be tied to this run, by nonce or by having
               no BEGIN above it at all
    truncated  the verdict line is there and is not byte-complete, so a write
               was cut inside it
    continued  the verdict is not the last line, so output arrived after the
               claim that nothing more would

`absent` is the one that matters and it is the one every prior remedy in this
repository's register misses. Each of the six entries in that class prescribes
`pipefail` or a redirect, and nothing in this morning's instance was a pipe.

## What this does NOT attest

The verdict covers the child this process waited for and nothing below it. A
child that backgrounds its own work and exits is the defect one level down, and
the terminator will say `COMPLETE exit=0` over work still running, exactly as
the harness did. `bytes=` in the verdict is the cheap tell a reader gets for
free: a suite that finished in four seconds having written nothing did not run.

So do not background this file and then read the notification. Background it
and then read its output, which is the whole rule.

No network, no repository state, no clock beyond `time.monotonic` and one
timestamp. Everything here is a subprocess and a file.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import signal as signalmod
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MARKER = "SENTINEL"

WRITER_CODES = ("nonzero", "timeout", "signal")
READER_CODES = ("absent", "stale", "truncated", "continued")
CODES = WRITER_CODES + READER_CODES

_BEGIN = re.compile(
    rf"^{MARKER} run=(?P<run>[0-9a-f]{{8,}}) label=(?P<label>\S+) BEGIN "
)
_VERDICT = re.compile(
    rf"^{MARKER} run=(?P<run>[0-9a-f]{{8,}}) label=(?P<label>\S+) "
    rf"(?P<state>COMPLETE|INCOMPLETE)\b(?P<rest>.*)$"
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fields(rest: str) -> dict[str, str]:
    """`exit=0 bytes=12` to a dict, which is all the verdict tail ever is."""
    out: dict[str, str] = {}
    for token in rest.split():
        if "=" in token:
            key, _, value = token.partition("=")
            out[key] = value
    return out


# ------------------------------------------------------------------ writing


def begin_line(run: str, label: str, cmd: list[str]) -> str:
    return (
        f"{MARKER} run={run} label={label} BEGIN at={_now()} "
        f"cmd={shlex.join(cmd)}\n"
    )


def verdict_line(
    run: str,
    label: str,
    *,
    returncode: int | None,
    seconds: float,
    nbytes: int,
    timeout: float | None = None,
) -> str:
    """The last line, and it is written only after the child has been reaped.

    A verdict composed before the wait is the defect this file exists for, one
    layer up: it would be true about the launch and silent about the work.
    """
    tail = f"seconds={seconds:.1f} bytes={nbytes} at={_now()}"
    if returncode is None:
        return (
            f"{MARKER} run={run} label={label} INCOMPLETE code=timeout "
            f"limit={timeout:g} {tail}\n"
        )
    if returncode < 0:
        name = signalmod.Signals(-returncode).name
        return (
            f"{MARKER} run={run} label={label} INCOMPLETE code=signal "
            f"signal={name} {tail}\n"
        )
    code = "" if returncode == 0 else " code=nonzero"
    return (
        f"{MARKER} run={run} label={label} COMPLETE exit={returncode}{code} "
        f"{tail}\n"
    )


def run_guarded(
    cmd: list[str],
    out: Path,
    *,
    label: str = "work",
    timeout: float | None = None,
    run: str | None = None,
) -> tuple[int, str]:
    """Run `cmd`, then append one verdict. Returns the child's shell status.

    The output file is opened once and handed to the child as its own stdout,
    so the child's bytes and the two sentinel lines are ordered by the kernel
    rather than by this process buffering them.
    """
    run = run or uuid.uuid4().hex[:12]
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with out.open("ab", buffering=0) as fh:
        fh.write(begin_line(run, label, cmd).encode())
        returncode: int | None
        try:
            proc = subprocess.run(cmd, stdout=fh, stderr=fh, timeout=timeout)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            returncode = None
        except FileNotFoundError:
            returncode = 127
            fh.write(f"{cmd[0]}: not found\n".encode())
        line = verdict_line(
            run,
            label,
            returncode=returncode,
            seconds=time.monotonic() - started,
            nbytes=out.stat().st_size,
            timeout=timeout,
        )
        fh.write(line.encode())
        os.fsync(fh.fileno())
    # A kill and a signal have no status of their own, so this process lends
    # them 1. The verdict line is where the difference is kept.
    status = 1 if returncode is None or returncode < 0 else returncode
    return status, line


# ------------------------------------------------------------------ reading


@dataclass
class Verdict:
    """What a reader may conclude, and never more than the file supports."""

    path: str
    complete: bool
    code: str | None
    reason: str
    label: str | None = None
    run: str | None = None
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.complete and self.code is None

    def report(self) -> str:
        head = "complete" if self.complete else "INCOMPLETE"
        if self.ok:
            head = "ok"
        name = f" code={self.code}" if self.code else ""
        return f"{self.path}: {head}{name}  {self.reason}"


def read_verdict(path: Path, *, label: str | None = None) -> Verdict:
    """Decide what a file says about the work that wrote it.

    Order matters. `absent` is checked before anything a present verdict could
    claim, because the whole class this file answers is a reader treating a
    missing statement as a passing one.
    """
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return Verdict(str(path), False, "absent", "no such file")
    text = raw.decode("utf-8", "replace")
    lines = text.split("\n")
    complete_last_line = text.endswith("\n")
    content = [ln for ln in lines if ln.strip()]

    begins = [(i, m) for i, ln in enumerate(content) if (m := _BEGIN.match(ln))]
    verdicts = [(i, m) for i, ln in enumerate(content) if (m := _VERDICT.match(ln))]

    if not verdicts:
        # A trailing BEGIN is the commonest absence and it is not damage: the
        # work started and has not reported. Calling that `truncated` is what
        # the first version of this file did, found by running it against a
        # live suite thirty seconds in.
        if begins:
            bmatch = begins[-1][1]
            return Verdict(
                str(path),
                False,
                "absent",
                f"the work began as run={bmatch.group('run')} and has left no "
                f"verdict in {len(raw)} bytes. It is running, killed or torn "
                "down, and nothing in this file says which.",
                bmatch.group("label"),
                bmatch.group("run"),
            )
        if content and content[-1].startswith(MARKER):
            return Verdict(
                str(path),
                False,
                "truncated",
                f"the last line starts {MARKER!r} and does not parse as a "
                "verdict or a BEGIN, so a write was cut inside it",
            )
        return Verdict(
            str(path),
            False,
            "absent",
            f"no {MARKER} verdict line in {len(raw)} bytes. The work was "
            "killed, torn down, or is still running. An exit status or a "
            "notification cannot tell you which.",
        )

    # The newest BEGIN is the run a reader is asking about. A verdict that sits
    # above it belongs to a previous run of the same file, and reading that one
    # as this one's is the whole defect one append away.
    if begins:
        newest, bmatch = begins[-1]
        paired = [
            (i, m)
            for i, m in verdicts
            if i > newest and m.group("run") == bmatch.group("run")
        ]
        if not paired:
            return Verdict(
                str(path),
                False,
                "stale",
                f"the newest BEGIN is run={bmatch.group('run')} and the only "
                f"verdict in this file is run={verdicts[-1][1].group('run')}, "
                "so it belongs to an earlier run and this one left none",
                bmatch.group("label"),
                bmatch.group("run"),
            )
        verdicts = paired

    index, match = verdicts[-1]
    run = match.group("run")
    seen = match.group("label")
    fields = _fields(match.group("rest"))

    if index != len(content) - 1:
        return Verdict(
            str(path),
            False,
            "continued",
            f"{len(content) - 1 - index} line(s) of output arrive after the "
            "verdict, so it does not cover the end of this file",
            seen,
            run,
            fields,
        )
    if not complete_last_line:
        return Verdict(
            str(path),
            False,
            "truncated",
            "the verdict line has no trailing newline, so the file ends "
            "inside it",
            seen,
            run,
            fields,
        )
    if not begins:
        return Verdict(
            str(path),
            False,
            "stale",
            "a verdict with no BEGIN above it cannot be tied to a run",
            seen,
            run,
            fields,
        )
    if label is not None and seen != label:
        return Verdict(
            str(path),
            False,
            "stale",
            f"asked for label={label} and the file's verdict is label={seen}",
            seen,
            run,
            fields,
        )

    if match.group("state") == "INCOMPLETE":
        code = fields.get("code", "signal")
        detail = fields.get("limit") or fields.get("signal") or ""
        return Verdict(
            str(path),
            False,
            code,
            f"the work ended without a status of its own ({detail})".replace(
                " ()", ""
            ),
            seen,
            run,
            fields,
        )

    exit_code = fields.get("exit", "?")
    if exit_code != "0":
        return Verdict(
            str(path),
            True,
            "nonzero",
            f"the work ran to a known end and failed, exit={exit_code}",
            seen,
            run,
            fields,
        )
    return Verdict(
        str(path),
        True,
        None,
        f"verdict present, run={run}, exit=0, bytes={fields.get('bytes', '?')}",
        seen,
        run,
        fields,
    )


# ---------------------------------------------------------------- composing


@dataclass
class Composition:
    """A total, its named parts, and the part nobody named."""

    total: float
    parts: dict[str, float]
    unit: str = ""

    @property
    def residual(self) -> float:
        return self.total - sum(self.parts.values())

    @property
    def largest(self) -> tuple[str, float]:
        if not self.parts:
            return ("nothing", 0.0)
        return max(self.parts.items(), key=lambda kv: kv[1])

    @property
    def negative(self) -> tuple[tuple[str, float], ...]:
        """Parts below zero, smallest first.

        A part of a composition is a share of the total, and a share has no
        sign. A negative term is an adjustment wearing a part's name, and it
        prints as a negative percentage of the total, which is not a share of
        anything. Refusing it is also the only thing that closes the hole in
        the paragraph below.
        """
        return tuple(
            sorted((kv for kv in self.parts.items() if kv[1] < 0), key=lambda kv: kv[1])
        )

    @property
    def oversized(self) -> tuple[tuple[str, float], ...]:
        """Parts larger than the whole, largest first.

        alexandria/exo's second finding, taken as written: the sum gate alone
        lets a negative term buy headroom for an impossible part, because
        `43 = 50 + (-20) + residual` balances. This check does not look at the
        sum, so nothing a sibling part says can move it.
        """
        return tuple(
            sorted(
                (kv for kv in self.parts.items() if kv[1] > self.total),
                key=lambda kv: -kv[1],
            )
        )

    @property
    def overcount(self) -> bool:
        return self.residual < 0

    @property
    def refusal(self) -> str | None:
        """The one sentence this claim is refused for, or None.

        Ordered by how specific the diagnosis is rather than by how the gates
        were added. A single part larger than the total is a better answer
        than "the parts sum above the total", which is why it is asked first.
        """
        u = f" {self.unit}" if self.unit else ""
        if self.negative:
            named = ", ".join(f"{n} is {v:g}{u}" for n, v in self.negative)
            return (
                f"REFUSED: {named}. A part is a share of the total and a share "
                f"has no sign, so a negative term is not a part of this "
                f"composition. It also buys headroom for the parts above it, "
                f"one unit for one unit. Publish the gross figures, and make "
                f"the credit a claim of its own."
            )
        if self.oversized:
            name, value = self.oversized[0]
            return (
                f"REFUSED: {name} alone is {value:g}{u}, which is more than "
                f"the whole total ({self.total:g}{u}). No composition holds a "
                f"part larger than the thing it composes, whatever the other "
                f"terms sum to."
            )
        if self.overcount:
            return (
                "REFUSED: the parts sum above the total, which no residual "
                "can absorb."
            )
        if not self.parts:
            return (
                f"REFUSED: this claim names no parts at all, so the whole "
                f"total is residual. A total with no composition is the shape "
                f"a report reaches by saying nothing."
            )
        name, value = self.largest
        if self.residual >= value:
            return (
                f"REFUSED: the residual {self.residual:g}{u} reaches "
                f"{name}, the largest part this claim names ({value:g}{u}). "
                f"A composition is not measured while its largest term has "
                f"no name."
            )
        return None

    @property
    def ok(self) -> bool:
        return self.refusal is None

    def report(self) -> list[str]:
        """Always prints the residual, which is the entire rule.

        The residual is named as unattributed rather than handed to the
        smallest part or folded into the largest. A number with no owner that
        says so is worth more to a reader than a number with a wrong owner.
        """
        u = f" {self.unit}" if self.unit else ""
        lines = [f"total {self.total:g}{u}"]
        for name, value in sorted(self.parts.items(), key=lambda kv: -kv[1]):
            share = (value / self.total * 100) if self.total else 0.0
            lines.append(f"  {name:<16} {value:g}{u}  {share:.1f}%")
        name, value = self.largest
        if self.overcount:
            excess = (
                f"  {'OVERCOUNT':<16} {-self.residual:g}{u}  the named parts "
                f"exceed the total"
            )
            # The "two of them count one thing" reading is only available when
            # no single part is already impossible on its own. With one part of
            # 50 against a total of 43 there is no second part to blame, and
            # the first version of this file said there was.
            if not self.oversized:
                excess += ", so at least two of them count the same thing"
            lines.append(excess)
        else:
            share = (self.residual / self.total * 100) if self.total else 0.0
            lines.append(
                f"  {'unattributed':<16} {self.residual:g}{u}  {share:.1f}%  "
                f"named by nothing above"
            )
        refusal = self.refusal
        if refusal is None:
            lines.append(
                f"ok: the residual is under {name}, the largest named part "
                f"({value:g}{u})"
            )
        else:
            lines.append(refusal)
        return lines


def parse_part(text: str) -> tuple[str, float]:
    name, sep, value = text.partition("=")
    if not sep:
        raise argparse.ArgumentTypeError(f"--part wants name=value, got {text!r}")
    try:
        return name, float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number") from None


class RepeatedPart(ValueError):
    """One name carrying two readings, which is the ambiguity itself.

    alexandria/exo's first finding, taken as written and with its preferred
    direction. `dict(pairs)` is last-wins, so `--part a=18 --part a=6.9`
    printed `a 6.9` and never said 18 had been given. The verdict direction is
    safe, because dropping a part only raises the residual, but the table whose
    whole job is to print a composition honestly had lost a figure somebody
    named, which is this file's own subject one level in.

    Summing the two is the other repair and it is worse. A sum hides which
    reading was meant, and the reader cannot tell `a=18 a=6.9` from `a=24.9`.
    """

    def __init__(self, repeats: dict[str, list[float]], unit: str = "") -> None:
        self.repeats = repeats
        self.unit = unit
        super().__init__(self.report())

    def report(self) -> str:
        u = f" {self.unit}" if self.unit else ""
        named = "; ".join(
            f"{name} was given {len(values)} times, as "
            + " and ".join(f"{v:g}{u}" for v in values)
            for name, values in self.repeats.items()
        )
        return (
            f"REFUSED: {named}. Two readings under one name is the ambiguity, "
            f"and both of the quiet repairs hide which was meant. Keeping the "
            f"last one drops a figure that was named, and summing them "
            f"invents a third. Give the parts distinct names, or settle on "
            f"one figure."
        )


def collect_parts(
    pairs: list[tuple[str, float]], unit: str = ""
) -> dict[str, float]:
    """`dict(pairs)` with the silent overwrite refused instead of taken."""
    seen: dict[str, float] = {}
    repeats: dict[str, list[float]] = {}
    for name, value in pairs:
        if name in seen:
            repeats.setdefault(name, [seen[name]]).append(value)
        else:
            seen[name] = value
    if repeats:
        raise RepeatedPart(repeats, unit)
    return seen


# -------------------------------------------------------------------- smoke


def smoke() -> int:
    """One assertion per code a writer or a reader can reach alone, plus one
    per refusal `--compose` can print.

    The denominator is counted and not written down. It used to be the literal
    `7` beside nine `check` calls, so the smoke published a count of its own
    work that no reader could check and that no added case would move. That is
    the defect this whole file is about, two lines inside the file itself.
    """
    import tempfile

    failures: list[str] = []
    asked = 0

    def check(name: str, got: object, want: object) -> None:
        nonlocal asked
        asked += 1
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        status, _ = run_guarded(
            [sys.executable, "-c", "print('hello')"], d / "ok.txt", label="ok"
        )
        check("a clean child exits 0", status, 0)
        check("and reads back ok", read_verdict(d / "ok.txt").ok, True)

        run_guarded(
            [sys.executable, "-c", "import sys; sys.exit(3)"],
            d / "bad.txt",
            label="bad",
        )
        check("a failed child", read_verdict(d / "bad.txt").code, "nonzero")

        run_guarded(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            d / "slow.txt",
            label="slow",
            timeout=0.2,
        )
        check("a killed child", read_verdict(d / "slow.txt").code, "timeout")

        (d / "nothing.txt").write_text("........ [ 9%]\n")
        check(
            "the case this file was written for",
            read_verdict(d / "nothing.txt").code,
            "absent",
        )
        (d / "empty.txt").write_bytes(b"")
        check(
            "and a zero-byte output, which a denominator guard passes",
            read_verdict(d / "empty.txt").code,
            "absent",
        )

        run_guarded([sys.executable, "-c", "pass"], d / "twice.txt", label="a")
        (d / "twice.txt").open("a").write(begin_line("ffffffffffff", "a", ["x"]))
        check(
            "a verdict from the run before",
            read_verdict(d / "twice.txt").code,
            "stale",
        )

    comp = Composition(43.0, {"srv": 18.0, "tmp": 6.9}, "GiB")
    check("the entry that triggered --compose", comp.ok, False)
    check("and its residual is published", round(comp.residual, 1), 18.1)

    # The two findings alexandria/exo brought back, each as the shell
    # transcript it arrived as rather than as a property of the dataclass.
    laundered = Composition(43.0, {"a": 50.0, "credit": -20.0}, "GiB")
    check("a negative part cannot launder an impossible one", laundered.ok, False)
    check(
        "and the part, not the sum, is what the refusal names",
        "A part is a share" in (laundered.refusal or ""),
        True,
    )
    check(
        "a part larger than the whole is refused on its own",
        Composition(43.0, {"a": 50.0}, "GiB").ok,
        False,
    )
    try:
        collect_parts([("a", 18.0), ("a", 6.9)], "GiB")
    except RepeatedPart as exc:
        check("a repeated name is refused", "given 2 times" in exc.report(), True)
        check("and the dropped figure is still printed", "18 GiB" in exc.report(), True)
    else:
        failures.append("a repeated name was accepted")
        asked += 2

    for line in failures:
        print(f"smoke: {line}")
    print(
        f"smoke: {asked - len(failures)} of {asked} ok"
        if len(failures) < asked
        else f"smoke: all {asked} failed"
    )
    return 1 if failures else 0


# ---------------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="tools/sentinel.py",
        description="A completeness terminator for unwatched work.",
    )
    ap.add_argument("paths", nargs="*", help="output files to read a verdict from")
    ap.add_argument("--out", help="run a command and write the verdict here")
    ap.add_argument("--label", default="work", help="names the work in the verdict")
    ap.add_argument("--timeout", type=float, help="seconds before code=timeout")
    ap.add_argument("--expect-label", help="refuse a verdict for other work")
    ap.add_argument("--compose", type=float, metavar="TOTAL")
    ap.add_argument("--part", action="append", type=parse_part, default=[])
    ap.add_argument("--unit", default="")
    ap.add_argument("--smoke", action="store_true")
    ap.epilog = "everything after a bare -- is the command --out runs."

    # Split on the first bare `--` by hand. `nargs=argparse.REMAINDER` beside a
    # positional `nargs="*"` loses the command instead of keeping it, which the
    # first version of this file shipped and the CLI tests caught.
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd: list[str] = []
    if "--" in argv:
        cut = argv.index("--")
        argv, cmd = argv[:cut], argv[cut + 1 :]
    args = ap.parse_args(argv)
    args.cmd = cmd

    if args.smoke:
        return smoke()

    if args.compose is not None:
        try:
            parts = collect_parts(args.part, args.unit)
        except RepeatedPart as exc:
            # Exit 1 rather than argparse's 2: a repeated name is a refused
            # claim and not a misuse of the flag, and every other refusal this
            # tool prints leaves 1 behind.
            print(exc.report())
            return 1
        comp = Composition(args.compose, parts, args.unit)
        for line in comp.report():
            print(line)
        return 0 if comp.ok else 1

    if args.out:
        cmd = args.cmd
        if not cmd:
            ap.error("--out needs a command after --")
        status, line = run_guarded(
            cmd,
            Path(args.out),
            label=args.label,
            timeout=args.timeout,
        )
        print(line.rstrip())
        return status

    if not args.paths:
        ap.error("give a file to read, or --out with a command, or --compose")

    worst = 0
    for path in args.paths:
        verdict = read_verdict(Path(path), label=args.expect_label)
        print(verdict.report())
        if not verdict.ok:
            worst = 1
    if worst:
        print(
            "A missing verdict is not a passing one. The exit status of the "
            "process you watched and the notification you read are both "
            "silent about the work."
        )
    return worst


if __name__ == "__main__":
    sys.exit(main())
