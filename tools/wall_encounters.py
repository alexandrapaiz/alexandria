"""Which runs met a provider wall, and which only wrote about one.

Run with `python3 tools/wall_encounters.py` for the whole corpus, or
`--seat alexandria-exo`, or `--survivals` for the one question below.

**Why this file exists rather than a grep.** On 2026-11-09 two seats answered
the same question with two different numbers and both were right about their
own corpus: a file-wide grep for the provider's limit sentence found 1,162 log
files, and `cron_firing.classify_refusal` found 1,159 refused runs. The
difference was three runs, and the reconciliation was arithmetically exact —
session 2, weekly 1, spend 0, to the row.

The reading of those three was not. They were offered as "three runs that met a
wall mid-run and finished, each exit zero", and therefore as the evidence
nobody had that an in-run retry survives a wall. All three are exo seats whose
closing summary *quotes another run's refusal*, because reporting on refusals
is what the seat does. Every one has `api_error_status: None`,
`terminal_reason: completed`, `is_error: false`. Not one met a wall.

    alexandria-exo 2026-11-01T23-04-44-468Z-hook   77 turns  exit 0
    epitome-exo    2026-10-18T13-07-01-011Z-message 98 turns  exit 0
    epitome-exo    2026-10-26T09-02-46-416Z-hook   118 turns  exit 0

The 2026-10-18 run is the one to read twice. Its own summary names this exact
class — *"two runs that merely wrote the words, one of them the run that
published the 65"* — and corrected a capacity command for it three weeks
before it became an instance of it itself. A page about walls gets read by the
runs that write about walls, so the discipline has to live in a tool and not in
a run's attention.

So the measurement this file is built to make cheap, and it has one answer:

    genuine walls              1,159
    survived (exit 0, turns>1)     0

A wall has never been survived on this host. That number is the point. Every
remedy that assumes otherwise — a retry that rides out a refusal, a run that
can be expected to finish what it started — has no evidence behind it, and
three runs that merely described walls are not three that beat one.

Report-only, and exits 0 unless `--survivals` is asked a question it can
answer in the affirmative, per the `tools/incidents.py` rule about gates that
turn `main` red for bookkeeping.
"""

import argparse
import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import cron_firing as cf  # noqa: E402


#: The three classes a log can be in, which is the whole vocabulary here.
MET_A_WALL = "met-a-wall"
WROTE_ABOUT_ONE = "wrote-about-one"
NEITHER = "neither"


def classify(run):
    """Which of the three this run is.

    The order matters and is the inverse of a grep's: the error record is
    consulted first and the prose only where there is no error record, so a
    refused run whose prose also quotes some *other* wall is still counted
    once, under the wall that actually refused it.
    """
    if run.get("refusal"):
        return MET_A_WALL
    if run.get("wall_prose"):
        return WROTE_ABOUT_ONE
    return NEITHER


def survived(run):
    """Did this run meet a wall and still finish.

    Both halves are needed. `exit_code == 0` alone catches a refusal the host
    happened to exit cleanly on, and `turns > 1` alone catches nothing, since
    a wall met at turn one is a refusal with no work behind it. A run that is
    both is a run the provider stopped and that went on anyway, and no such
    run exists on this host.
    """
    return (classify(run) == MET_A_WALL
            and run.get("exit_code") == 0
            and (run.get("turns") or 0) > 1)


def survey(root=cf.LOG_ROOT, seat=None):
    """Every run under `root`, counted into the three classes.

    `seat` must already be a directory name the roster carries. `main` resolves
    it through `cron_firing.resolve_seat` before calling here, because an
    unresolvable seat has to raise rather than return an empty survey: a zero
    is the right answer to "this seat met no walls" and the wrong answer to
    "there is no such seat", and the two are indistinguishable in this output
    (`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
    and §2b's rule that an instrument must be shown able to see the seat before
    a zero from it is believed).
    """
    runs = cf.read_runs(root, seat=seat) if seat else cf.read_runs(root)
    counts = collections.Counter()
    scopes = collections.Counter()
    prose = []
    survivals = []
    for run in runs:
        kind = classify(run)
        counts[kind] += 1
        if kind == MET_A_WALL:
            scopes[run["refusal"]] += 1
        elif kind == WROTE_ABOUT_ONE:
            prose.append(run)
        if survived(run):
            survivals.append(run)
    return {
        "runs": len(runs),
        "counts": counts,
        "scopes": scopes,
        "prose": sorted(prose, key=lambda r: r["run_id"]),
        "survivals": sorted(survivals, key=lambda r: r["run_id"]),
    }


def _line(run):
    return (f"{run['seat']:24s} {run['run_id']:40s} "
            f"turns={run['turns']} exit={run['exit_code']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(cf.LOG_ROOT),
                        help="the log root to walk (default: the host's)")
    parser.add_argument("--seat", default=None, help="one seat rather than all")
    parser.add_argument("--survivals", action="store_true",
                        help="exit 1 if any run met a wall and still finished")
    args = parser.parse_args(argv)

    root = Path(args.root)
    # Before any reading, because every count below is about a seat and a count
    # about a seat that does not exist is worse than no count.
    try:
        seat = cf.resolve_seat(args.seat, root)
    except cf.SeatNotFound as exc:
        print(f"wall_encounters: {exc}", file=sys.stderr)
        return 2
    if seat != args.seat:
        print(f"note: reading {seat} for --seat {args.seat!r}", file=sys.stderr)

    found = survey(root, seat=seat)
    counts = found["counts"]
    print(f"{found['runs']} runs under {root}"
          + (f", seat {seat}" if seat else ""))
    print(f"  met a wall      {counts[MET_A_WALL]}")
    for scope, n in sorted(found["scopes"].items(), key=lambda kv: -kv[1]):
        print(f"      {scope:18s} {n}")
    print(f"  wrote about one {counts[WROTE_ABOUT_ONE]}")
    for run in found["prose"]:
        print("      " + _line(run))
    print(f"  neither         {counts[NEITHER]}")
    print(f"  survived a wall {len(found['survivals'])}")
    for run in found["survivals"]:
        print("      " + _line(run))

    # The two counts a grep and a classifier would each report, printed side by
    # side and labelled, because quoting either on its own is what cost two
    # seats a round trip.
    grep = counts[MET_A_WALL] + counts[WROTE_ABOUT_ONE]
    print(f"\n  a file-wide grep would say {grep}; "
          f"the refused-run count is {counts[MET_A_WALL]}; "
          f"the difference is {counts[WROTE_ABOUT_ONE]} run(s) of prose.")

    if args.survivals and found["survivals"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
