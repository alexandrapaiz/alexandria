#!/usr/bin/env python3
"""The deploy ladder, as a command that refuses rather than as prose.

`docs/agents/runtime-changes.md` closes with the argument this file exists to
answer: **a rule enforced by a sentence in a charter is enforced at the
reliability of a model reading a file, and a rule enforced by a link in a
command is enforced at the reliability of a shell.** The press already has that
property, because the chair deploys it through an `&&` chain and an `&&` chain
is a gate. Four other apps do not, and the chain itself lives in three places
in `docs/decisions.md` where a reader has to find the right one.

So the chain moves here, once, derived rather than copied, and the chair runs

    python3 tools/deploy_gate.py --app triage

instead of remembering four commands in the right order. `--plan` prints the
chain and runs nothing, which is the form to read before trusting it.

## What this does not do, and why that is the design

It does not deploy on a push to `main`. The ledger entry that asked for this
work proposed exactly that, and the law forbids it in so many words: the
rehearsal is run by "the chair, by hand, before the deploy that installs the
schedule. Not cron, not CI, and not the seat that wrote the change." A workflow
that fires on merge is a cron by any honest reading, and the four production
failures of INC-2026-09-24-press-provider-migration are what the human in that
loop is there to catch.

What the gap actually was is narrower than "no deploy workflow". It was that
the chain was written down four times and enforced once, so the hand that runs
it has to carry the ladder in its head. This file is the hand's tool. The
accompanying `.github/workflows-pending/modal-deploy.yml` is the same tool
behind a dispatch button, for a chair who has no Modal CLI in front of them,
and it is `workflow_dispatch` only for the reason above.

## Two gates, and both of them refuse before anything is spent

**The ladder.** An app that calls a model gets `pipeline/budget.py`, then its
`preflight`, then its `rehearse`, and only then `modal deploy`. Which apps
those are is read off the modules themselves: an app whose module defines
`preflight` and `rehearse` is a model-calling app. Deriving it is the same
argument `pipeline/runtime_sha.py` makes about its file list, and it has the
same payoff. A new gate added to a module joins the ladder with nothing to
remember, and an app that loses one cannot quietly keep passing.

**The window.** Moonshot's organization concurrency is 1 at the account level,
so a rehearsal run inside a live job's hour takes that job's slot away. That is
INC-2026-09-24-kimi-org-concurrency, and `pipeline/llm.py`'s `KIMI_WINDOWS` is
the schedule in machine-readable form. A rehearsal is refused inside any of
those windows, before a single call, and the refusal names the job that owns
the hour and the next time the band is clear.

No model call, no database and no network happen in this file. It assembles a
chain and runs a subprocess, or prints it.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import runtime_sha  # noqa: E402

# `runtime_sha.APPS` holds the three apps whose deploy the drift guard watches.
# This file's job is the deploy itself, which covers every scheduled app, so
# ingest and distill are here too. ADR-12 and `pipeline/llm.py`'s window table
# are the two places that agree on what the five are.
# Ordered by the clock the pipeline runs on, 11:00 through Monday 09:00, and
# `--app all` follows that order rather than the alphabet. A paper has to be
# ingested before it can be triaged, so if a deploy of several apps is going to
# stop halfway it should stop with the upstream half already current.
APPS = {
    "ingest": "pipeline/ingest.py",
    "triage": "pipeline/triage.py",
    "interpret": "pipeline/interpret.py",
    "distill": "pipeline/distill.py",
    "weekly": "pipeline/weekly.py",
}

# The order the ladder runs in, and the reason each rung is where it is lives in
# docs/agents/runtime-changes.md's "ladder for a provider or model change".
# `drain` is not here on purpose: it is the dry run an owner's directive asked
# for on a specific day, it costs nothing and proves nothing about the deploy,
# and the ADR's own chains include it in two of the four. A rung that is
# sometimes in the chain cannot be a gate.
GATES = ("preflight", "rehearse")

# Every gate that spends a model call. The window check applies to these and to
# nothing else, because `pipeline/budget.py` is local arithmetic and
# `modal deploy` uploads an image.
SPENDING = ("rehearse",)


def module_source(app: str, repo_root: pathlib.Path | None = None) -> str:
    root = pathlib.Path(repo_root or ROOT)
    return (root / APPS[app]).read_text(encoding="utf-8")


def gates_for(app: str, repo_root: pathlib.Path | None = None) -> list[str]:
    """Which gates this app's module actually defines, in ladder order.

    Read off the source rather than declared beside it. `ingest` calls no model
    and defines neither, so its ladder is a bare deploy, which is what ADR-12's
    own chain says. A module that grows a `rehearse` gains the rung the day it
    does.
    """
    source = module_source(app, repo_root)
    return [gate for gate in GATES if f"\ndef {gate}(" in source]


def ladder(app: str, repo_root: pathlib.Path | None = None) -> list[list[str]]:
    """The commands to run for one app, in order, as argv lists.

    The budget guard comes first and only for an app with gates, because it
    asks whether a model request fits and an app that sends none has no request
    to size.
    """
    module = APPS[app]
    gates = gates_for(app, repo_root)
    steps: list[list[str]] = []
    if gates:
        steps.append(["python3", "pipeline/budget.py"])
    steps += [["modal", "run", f"{module}::{gate}"] for gate in gates]
    steps.append(["modal", "deploy", module])
    return steps


def spends_a_call(app: str, repo_root: pathlib.Path | None = None) -> bool:
    return any(gate in SPENDING for gate in gates_for(app, repo_root))


# ------------------------------------------------------------------ the window

def _windows() -> dict[str, tuple[int, int]]:
    """The reserved Kimi hours, in minutes from midnight UTC.

    Imported rather than copied. A second copy of this table is a copy that
    disagrees with the crons the day somebody moves one, and the crons are what
    `budget.check_kimi_windows()` already checks this table against.
    """
    from pipeline import llm

    return dict(llm.KIMI_WINDOWS)


def window_conflict(now: datetime | None = None) -> str | None:
    """Which scheduled job owns this minute, or None when the band is clear.

    The press's own 09:00-11:00 slot is reserved in `pipeline/llm.py` for the
    press *and* the chair's manual rehearsal, and it is still refused here. A
    rehearsal at 09:30 on a Monday lands on the live press; the comment reserves
    the band so that nothing else is scheduled into it, which is a different
    promise from the band being free.
    """
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    minute = now.hour * 60 + now.minute
    for job, (start, end) in sorted(_windows().items(), key=lambda kv: kv[1]):
        if start <= minute < end:
            clear = (now.replace(hour=end // 60, minute=end % 60,
                                 second=0, microsecond=0)
                     if end < 24 * 60 else
                     now.replace(hour=0, minute=0, second=0, microsecond=0)
                     + timedelta(days=1))
            return (f"{job} owns {start // 60:02d}:{start % 60:02d}-"
                    f"{end // 60:02d}:{end % 60:02d} UTC and it is now "
                    f"{now:%H:%M} UTC. Moonshot's organization concurrency is "
                    f"1, so a rehearsal here takes that run's slot "
                    f"(INC-2026-09-24-kimi-org-concurrency). The band is clear "
                    f"from {clear:%H:%M} UTC.")
    return None


# -------------------------------------------------------------------- the chain

def render(steps: list[list[str]]) -> str:
    """The chain as the shell would be given it, for a reader to check."""
    return " \\\n  && ".join(" ".join(step) for step in steps)


def run(app: str, repo_root: pathlib.Path | None = None,
        runner=None, out=print) -> int:
    """Run one app's ladder, stopping at the first rung that fails.

    `runner` takes an argv list and returns an exit status; it defaults to a
    real subprocess and exists so the tests can assert the chain stops without
    installing the Modal CLI.
    """
    root = pathlib.Path(repo_root or ROOT)

    def default(argv: list[str]) -> int:
        return subprocess.run(argv, cwd=str(root)).returncode

    runner = runner or default
    steps = ladder(app, root)
    for n, step in enumerate(steps, start=1):
        out(f"[{app} {n}/{len(steps)}] {' '.join(step)}")
        status = runner(step)
        if status != 0:
            out(f"[{app}] stopped: `{' '.join(step)}` exited {status}. "
                f"Nothing after it ran, which is the point of the chain.")
            return status
    out(f"[{app}] deployed, with every gate above it green.")
    return 0


def main(argv: list[str] | None = None, runner=None, out=print,
         now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run an app's deploy ladder, or print it.")
    parser.add_argument("--app", default="all",
                        choices=list(APPS) + ["all"],
                        help="which app, or every scheduled app in order")
    parser.add_argument("--plan", action="store_true",
                        help="print the chain and run nothing")
    parser.add_argument("--ignore-window", action="store_true",
                        help="deploy inside a reserved Kimi hour anyway; say "
                             "why in the pull request or the run that did it")
    args = parser.parse_args(argv)

    apps = list(APPS) if args.app == "all" else [args.app]

    if args.plan:
        for app in apps:
            out(f"# {app}")
            out(render(ladder(app)))
            out("")
        clash = window_conflict(now)
        out(f"# window: {clash}" if clash
            else "# window: clear, no scheduled Kimi job owns this minute")
        return 0

    spending = [app for app in apps if spends_a_call(app)]
    clash = window_conflict(now)
    if spending and clash:
        if not args.ignore_window:
            out(f"refusing to rehearse {', '.join(spending)}: {clash}")
            out("Pass --ignore-window only if you know the window's job is "
                "not running.")
            return 2
        out(f"WARNING: rehearsing inside a reserved window anyway. {clash}")

    for app in apps:
        status = run(app, runner=runner, out=out)
        if status != 0:
            return status
    return 0


if __name__ == "__main__":
    sys.exit(main())
