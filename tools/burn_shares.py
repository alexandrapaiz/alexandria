#!/usr/bin/env python3
"""Which lever is actually spending the week: the arrival rate, or the run.

    python3 tools/burn_shares.py                  the decomposition, in prose
    python3 tools/burn_shares.py --json
    python3 tools/burn_shares.py --root PATH      a different run-log root
    python3 tools/burn_shares.py --tolerate 0.5   the rate share that exits 0

Exit 0 when cost per run is the dominant term in the growth of the fleet's
burn rate; **1 when the arrival rate is**, because that is the term no
capacity surface has a column for and the only one this seat's charters can
move. 2 a usage error, 3 could not look.

WHY THIS FILE EXISTS. HQ's `tools/ration.py` (alexandra-systems, shipped
2026-11-09) is the gauge this seat asked for and it is right about the thing
it measures: the allowance did not shrink, each walled cycle bought
$2.0k-$3.3k of list-price inference, and the week is now being spent in ten
hours instead of a hundred and sixty. Its own docstring then explains the
change by the run: "median turns per completed run went 67, 70, 89, and the
Opus share of completed runs 41%, 43%, 55%, so the same ceiling bought 560
passes in October and 390 in November."

That explanation is true and it is the smaller half. Burn rate is a product
of two factors and the gauge reports only the one:

    $/hour  =  $/run  x  runs/hour

Read off HQ's own per-cycle fields on 2026-11-09, from the first walled cycle
to the live one:

    $/hour    12.42 -> 194.52    x15.66
    $/run      4.64 ->   8.18    x1.76     21% of the growth, in log shares
    runs/hour  2.68 ->  23.78    x8.88     79% of the growth

So four fifths of it is arrival rate. That matters because the two factors
have different owners and different remedies. Cost per run is a model
routing decision and a turn cap, which live in the host manifest and are
HQ's merge. Arrival rate is **how many runs the fleet wakes**, and on this
host 94% of the cycle's runs and 100% of the last six hours' runs were
`message`-triggered -- seats waking seats. That is the agent layer, which is
this seat's writable surface, and it is the lever nothing was pointed at.

What this tool does not claim. It does not say the arrival rate is too high,
or that any particular wake was waste; a busy fleet shipping is not a defect.
It says which factor moved, so that an hour spent on turn caps is not spent
against a fifth of the problem. And it says nothing about the ceiling: where
the wall is is HQ's gauge's question and this one takes no view.

THE DENOMINATOR IS THE ACTIVE WINDOW, NEVER THE WEEK. A cycle that spends
its allowance in ten hours and then stands dark for six days has a runs/hour
of 23.8 over the hours it ran and 1.4 over the calendar week, and only the
first is a rate the fleet chose. So the hours here are `last priced run
minus cycle start`, which is HQ's own `spent_hours`, and a cycle still in
progress is marked so.
"""

import argparse
import datetime as dt
import glob
import json
import math
import os
import re
import sys

DEFAULT_ROOT = "/srv/asc/state/.epito/logs"
CYCLE_DAYS = 7
CYCLE_HOURS = CYCLE_DAYS * 24

# Deliberately the same three expressions HQ's gauge reads, so that the spend
# and run counts here are comparable to its output rather than merely similar.
# `tools/tests/test_burn_shares.py` asserts the equality against the live tree
# when there is one; a number that only agrees by eye is not a check.
LOG_NAME = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})-(\d{3})Z-([a-z]+)\.log$")
TOTAL_COST = re.compile(r'"total_cost_usd":([0-9.]+)')
WEEKLY_ANY = re.compile(r"hit your weekly limit", re.I)
WEEKLY_DATED = re.compile(
    r"hit your weekly limit[^\"]{0,40}?resets ([A-Z][a-z]{2}) (\d{1,2}), "
    r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(UTC\)", re.I)
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"])}


class CouldNotLook(Exception):
    pass


def parse_reset(match, year):
    month = MONTHS[match.group(1).lower()]
    day = int(match.group(2))
    hour = int(match.group(3)) % 12
    minute = int(match.group(4) or 0)
    if match.group(5).lower() == "pm":
        hour += 12
    return dt.datetime(year, month, day, hour, minute, tzinfo=dt.timezone.utc)


def load(root):
    """Every run log under `root`: when it started, what it cost, how it woke."""
    runs = []
    for path in sorted(glob.glob(os.path.join(root, "*", "*.log"))):
        name = os.path.basename(path)
        match = LOG_NAME.match(name)
        if not match:
            continue
        started = dt.datetime(
            *(int(match.group(i)) for i in range(1, 7)),
            tzinfo=dt.timezone.utc)
        try:
            with open(path, errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        totals = TOTAL_COST.findall(text)
        reset = None
        walled = bool(WEEKLY_ANY.search(text))
        if walled:
            dated = WEEKLY_DATED.search(text)
            if dated:
                reset = parse_reset(dated, started.year)
        runs.append({
            "started": started,
            "trigger": match.group(8),
            "cost": float(totals[-1]) if totals else None,
            "walled": walled,
            "reset": reset,
        })
    if not runs:
        raise CouldNotLook(f"no run logs under {root}")
    runs.sort(key=lambda r: r["started"])
    return runs


def anchor(runs, now):
    """The instant this week's allowance reset, off the provider's sentence.

    Same derivation as HQ's gauge and for the same reason: the only surface
    that names the reset instant is the provider's own refusal text, and a day
    of the week is an assumption rather than a reading.
    """
    dated = [r["reset"] for r in runs if r["reset"]]
    if not dated:
        raise CouldNotLook(
            "no dated weekly-limit refusal in the run logs, so nothing here "
            "names the instant the allowance resets")
    start = max(dated)
    while start + dt.timedelta(days=CYCLE_DAYS) <= now:
        start += dt.timedelta(days=CYCLE_DAYS)
    while start > now:
        start -= dt.timedelta(days=CYCLE_DAYS)
    return start


def cycle(runs, start, now=None):
    """One cycle's spend, runs, active hours and wake mix."""
    end = start + dt.timedelta(days=CYCLE_DAYS)
    inside = [r for r in runs if start <= r["started"] < end]
    if now is not None:
        inside = [r for r in inside if r["started"] <= now]
    paid = [r for r in inside if r["cost"]]
    last = max((r["started"] for r in paid), default=None)
    hours = (last - start).total_seconds() / 3600 if last else 0.0
    triggers = {}
    for run in inside:
        triggers[run["trigger"]] = triggers.get(run["trigger"], 0) + 1
    return {
        "start": start,
        "end": end,
        "spend": sum(r["cost"] for r in paid),
        "runs_priced": len(paid),
        "runs_logged": len(inside),
        "refusals": sum(1 for r in inside if r["walled"]),
        "active_hours": hours,
        "triggers": triggers,
        "complete": end <= (now or dt.datetime.now(dt.timezone.utc)),
    }


def rates(row):
    """The two factors and their product, or None where the row cannot carry them."""
    if not row["runs_priced"] or row["active_hours"] <= 0:
        return None
    return {
        "per_hour": row["spend"] / row["active_hours"],
        "per_run": row["spend"] / row["runs_priced"],
        "runs_per_hour": row["runs_priced"] / row["active_hours"],
    }


def shares(first, last):
    """How much of the growth in $/hour each factor accounts for.

    In log shares, because the two factors multiply: ln(x*y) = ln x + ln y, so
    the shares of the log growth add to one and a factor that did not move
    takes none of it. An arithmetic share of a product does not have that
    property and would hand the same answer two different values depending on
    which factor you divided out first.
    """
    a, b = rates(first), rates(last)
    if not a or not b:
        return None
    total = b["per_hour"] / a["per_hour"]
    if total <= 0 or abs(math.log(total)) < 1e-9:
        return None
    cost = b["per_run"] / a["per_run"]
    rate = b["runs_per_hour"] / a["runs_per_hour"]
    span = math.log(total)
    return {
        "from": first["start"], "to": last["start"],
        "burn_growth": total, "cost_growth": cost, "rate_growth": rate,
        "cost_share": math.log(cost) / span,
        "rate_share": math.log(rate) / span,
    }


def read(root, now):
    runs = load(root)
    start = anchor(runs, now)
    live = cycle(runs, start, now)
    priors, edge = [], start
    while True:
        edge -= dt.timedelta(days=CYCLE_DAYS)
        prior = cycle(runs, edge, now)
        if not prior["runs_priced"]:
            break
        priors.append(prior)
        if len(priors) >= 8:
            break
    priors.reverse()
    # The baseline is the earliest cycle that ever met the wall. A ramp-up week
    # the fleet never filled is not a rate the fleet chose, so it is no more a
    # baseline for a rate than it is evidence about a ceiling -- which is the
    # same exclusion HQ's gauge makes for the ceiling, for the same reason.
    walled = [p for p in priors if p["refusals"]]
    baseline = walled[0] if walled else None
    return {
        "now": now, "cycle": live, "priors": priors,
        "baseline": baseline,
        "shares": shares(baseline, live) if baseline else None,
    }


def money(value):
    return f"${value:,.0f}"


def render(report):
    out = []
    add = out.append
    live = report["cycle"]
    add(f"The burn, split into its two factors, read at "
        f"{report['now']:%Y-%m-%d %H:%MZ}")
    add("")
    add("  $/hour = $/run x runs/hour. A capacity surface that reports the "
        "first two")
    add("  cannot say which of them moved, and they have different owners.")
    add("")
    add("    cycle         spend  priced   active   $/run  runs/h     $/h  "
        "wakes by message")
    for row in report["priors"] + [live]:
        rate = rates(row)
        mark = "" if row["complete"] else "  <- in progress"
        msg = row["triggers"].get("message", 0)
        pct = 100 * msg / row["runs_logged"] if row["runs_logged"] else 0
        if not rate:
            add(f"    {row['start']:%Y-%m-%d}  {money(row['spend']):>7}  "
                f"{row['runs_priced']:>6}       --      --      --      -- "
                f"{pct:>14.0f}%{mark}")
            continue
        add(f"    {row['start']:%Y-%m-%d}  {money(row['spend']):>7}  "
            f"{row['runs_priced']:>6}  {row['active_hours']:>6.1f}h  "
            f"{rate['per_run']:>6.2f}  {rate['runs_per_hour']:>6.2f}  "
            f"{rate['per_hour']:>6.1f}  {pct:>14.0f}%{mark}")
    add("")
    split = report["shares"]
    if not split:
        add("  no walled prior cycle with a priced run, so there is no "
            "baseline to split the growth against. The factors above stand on "
            "their own and the share below is not computed.")
        return "\n".join(out)
    add(f"  from {split['from']:%Y-%m-%d} (the first cycle that met the wall) "
        f"to this one:")
    add("")
    add(f"    $/hour     x{split['burn_growth']:.2f}")
    add(f"    $/run      x{split['cost_growth']:.2f}   "
        f"{100 * split['cost_share']:.0f}% of the growth")
    add(f"    runs/hour  x{split['rate_growth']:.2f}   "
        f"{100 * split['rate_share']:.0f}% of the growth")
    add("")
    if split["rate_share"] > split["cost_share"]:
        add("  The dominant term is the arrival rate. Turn caps and model "
            "routing address")
        add("  the other one, and they are the host's manifest and the "
            "owner's merge. How")
        add("  many runs the fleet wakes is the agent layer, which is a "
            "charter away.")
    else:
        add("  The dominant term is the cost of a run. That is a turn cap and "
            "a model")
        add("  choice, both of which live in the host manifest and neither of "
            "which a")
        add("  charter can move: it is an ask, not an edit.")
    add("")
    add("  This tool rations nothing and pauses no seat. It says which lever "
        "to pull.")
    return "\n".join(out)


def jsonable(value):
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--tolerate", type=float, default=0.5,
                        help="the rate share at or below which this exits 0")
    parser.add_argument("--now", default="",
                        help="pretend it is this instant; bounds the runs read "
                             "as well as the clock")
    args = parser.parse_args(argv)

    now = dt.datetime.now(dt.timezone.utc)
    if args.now:
        try:
            now = dt.datetime.fromisoformat(args.now.replace("Z", "+00:00"))
        except ValueError:
            print(f"burn_shares.py: --now is not an instant: {args.now}",
                  file=sys.stderr)
            return 2
        if now.tzinfo is None:
            now = now.replace(tzinfo=dt.timezone.utc)

    try:
        report = read(args.root, now)
    except CouldNotLook as why:
        print(f"burn_shares.py: could not look: {why}", file=sys.stderr)
        return 3

    print(json.dumps(jsonable(report), indent=2, sort_keys=True)
          if args.json else render(report))
    split = report["shares"]
    if split and split["rate_share"] > args.tolerate:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
