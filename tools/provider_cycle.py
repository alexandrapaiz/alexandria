#!/usr/bin/env python3
"""The provider's weekly pool has a size, and the record of what emptied it says what.

    python3 tools/provider_cycle.py                     # the live cycle, against the measured pool
    python3 tools/provider_cycle.py --history           # every cycle the archive can date
    python3 tools/provider_cycle.py --json              # the verdict as a script reads it
    python3 tools/provider_cycle.py --root /path/to/logs --now 2026-11-03T06:00:00Z

Exit 0 when the live cycle is inside its pool and projected to stay there.
Exit 1 when it is already exhausted, or burning fast enough to empty before
the reset, or being refused by a cap this file cannot project at all.

## Why this exists

Twice running, the portfolio spent its whole provider week in about a day and
then sat dark for six.
`INC-2026-11-01-the-portfolio-spent-its-provider-week-in-thirty-hours-and-ran-dark-for-the-other-hundred-thirty-eight`
measured the first instance by hand after the reset. This seat's own re-fired
cron slot of 2026-11-08 was the second. Both were measured the same way, by a
seat reading the host's logs once the week was already lost, and written into a
register. Nothing read the burn while the pool still held anything.

That incident's close says the repair is not available here: "no seat able to
see the pool's level and no component rationing it," handed to HQ as the ask to
expose the remaining budget somewhere a seat can read before it spends. That is
true of the provider's own counter and it is the wrong conclusion about the
pool's *size*, which is the part this file supplies. A cycle that ends in a
weekly refusal has measured the pool by spending it, and the host's archive
records what it spent. The level is unreadable; the capacity is not; and
capacity against elapsed time is what a projection needs.

## Three limits, and only one of them is the pool

The refusals all arrive as `429` and `tools/cron_firing.py` tells them apart by
their sentence. There are three, which matters here more than anywhere else,
because only `weekly-limit` says anything about the pool:

`weekly-limit`
    The pool. Resets at the instant its own sentence announces.

`session-limit`
    A few hours wide. Costs a run, never a week, and bounds nothing here.

`monthly-spend`
    The org's spend cap. **This file cannot project it and does not try.** It
    is not a function of elapsed time or burn rate against a weekly ceiling,
    its remedy is the owner raising a limit in the org's admin settings, and
    no amount of rescheduling touches it. When it is live the report says so
    and stops projecting, because a projection against the weekly pool would
    be answering a question nobody asked. Until 2026-11-08 all 257 of its
    refusals were classified as `weekly-limit`, which is
    `INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days-because-its-sentence-ends-by-naming-the-weekly-reset`.

## What bounds the pool, and what only looks like it does

Only a cycle that **hit the weekly wall** bounds the pool, and the measurement
is the turns spent *before the first weekly refusal* rather than the cycle's
whole total. Everything after the wall is runs being turned away at turn 1,
which is noise added to the number that is supposed to be the wall's height.

A cycle that ran its week out without a weekly refusal spent less than the pool
holds and says nothing about how much less, so it is a floor and never a
ceiling. Reading those two the same way is how the pool gets understated.

**And the archive is a rolling window, so the oldest cycle in it is clipped.**
The host prunes: this file was written while the count under the log root fell
from 3,385 to 3,209 in twenty minutes, and the cycle of 2026-10-18 went from
holding its whole week to starting on 2026-10-23. A clipped cycle's turns are a
floor for the same reason a never-refused cycle's are, so `clipped` is its own
verdict and it is excluded from the ceiling. A cycle ages out of being evidence
before it ages out of the report.

Two things are read rather than assumed.

**The reset instant comes from the provider.** Every weekly refusal carries its
own announcement, `resets Nov 8, 11pm (UTC)`, so the boundary is parsed from
the sentence that announced it. The Sunday 23:00Z rule is the fallback for a
window holding no refusal, and the report says which of the two it used.

**A run with no turn count is unread, not zero.** The host writes `turns=-`
beside `exit=timeout`, and that was 60 of the 84 surviving runs in the oldest
cycle here. A reader cannot tell a cheap week from an unmeasured one unless the
tool says, so every total carries the number of runs behind it that had no
price on them.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import cron_firing as cf  # noqa: E402  the log reader and the refusal classifier

UTC = dt.timezone.utc

#: The cycle is seven days long, which is what "weekly limit" means.
CYCLE = dt.timedelta(days=7)

#: The fallback boundary, used only when no refusal in range announced one.
#: Sunday is `weekday() == 6`, and 23:00Z is the hour every announcement in
#: this archive names.
FALLBACK_WEEKDAY = 6
FALLBACK_HOUR = 23

#: `resets Nov 8, 11pm (UTC)`, and `resets 11pm (UTC)` which is the same
#: sentence on the day of the reset itself. The month name is the provider's,
#: the year is never in it, and the hour is 12-hour with a meridiem.
RESET = re.compile(
    r"resets\s+(?:(?P<month>[A-Za-z]{3})[a-z]*\.?\s+(?P<day>\d{1,2}),\s*)?"
    r"(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<meridiem>am|pm)\s*\(UTC\)",
    re.IGNORECASE,
)

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}

#: A cycle needs at least this many priced runs before its total is allowed to
#: bound the pool. One refused run in an otherwise empty window is a refusal,
#: not a measurement, and a ceiling drawn from it would be absurd.
MIN_RUNS_TO_BOUND = 50

#: How much of a cycle has to have elapsed before its burn rate is allowed to
#: project. The first minutes of a cycle are the worst possible sample: every
#: seat the old cycle refused re-fires at once, so the rate is a thundering
#: herd and not a week's pace. Measured here at 0.4 hours into the cycle of
#: 2026-11-08, the average read 496 turns an hour and projected the pool gone
#: 107 hours early, which was false. An alarm that is red at the top of every
#: week is an alarm nobody reads by Wednesday, which is the week this one
#: exists to save.
MIN_ELAPSED_HOURS = 2.0


def parse_reset(text, observed):
    """The reset instant the provider announced, read in the refusal's own year.

    The announcement carries a month and a day but never a year, so the year
    comes from the run that was refused. A refusal observed in late December
    naming January is next year's reset, which is the one wrap this has to get
    right and the reason it is not a bare `replace`.

    **The undated form carries an hour and not a date, so it establishes no
    boundary.** `resets 11pm (UTC)` appears 141 times in this archive, and
    eleven of those were observed on a *Saturday*, where the reset it names is
    25 hours out rather than one. Reading it as "11pm on the day it was
    observed" invented a Saturday cycle edge in two of the five weeks here,
    which split one real cycle in two: the halves came out at 266 and 68
    weekly refusals, and the second half had a pool height of zero turns
    because it began already refused. A number that wrong is worse than no
    number, and the weekday rule covers these windows correctly anyway.

    The dated form is what governs, and the two in this archive — `Nov 1` and
    `Nov 8` — are both Sundays, which is independent evidence that the
    fallback rule has the right weekday.
    """
    match = RESET.search(text or "")
    if not match:
        return None
    if match["month"] is None:
        return None
    hour = int(match["hour"]) % 12
    if match["meridiem"].lower() == "pm":
        hour += 12
    minute = int(match["minute"] or 0)

    month = MONTHS.get(match["month"].lower()[:3])
    if month is None:
        return None
    for year in (observed.year, observed.year + 1):
        try:
            when = dt.datetime(year, month, int(match["day"]), hour, minute,
                               tzinfo=UTC)
        except ValueError:
            return None
        # A reset is announced before it happens, so the first candidate at or
        # after the refusal is the right year. The day of grace absorbs a
        # refusal logged either side of midnight from the reset it names.
        if when >= observed - dt.timedelta(days=1):
            return when
    return None


def announced_resets(runs):
    """Every distinct weekly reset instant the archive's refusals announced.

    `monthly-spend` sentences name the weekly reset too, in their closing
    clause, and that clause is just as authoritative about where the boundary
    falls as a weekly refusal's is. So both are read, which is a second use
    for the sentence `classify_refusal` now keeps.
    """
    found = set()
    for run in runs:
        if run.get("refusal") not in ("weekly-limit", "monthly-spend"):
            continue
        when = parse_reset(run.get("refusal_text") or "", run["started"])
        if when is not None:
            found.add(when)
    return sorted(found)


def fallback_reset(when):
    """The cycle end at or after `when`, on the Sunday 23:00Z rule."""
    edge = when.replace(hour=FALLBACK_HOUR, minute=0, second=0, microsecond=0)
    while edge.weekday() != FALLBACK_WEEKDAY:
        edge += dt.timedelta(days=1)
    if edge <= when:
        edge += CYCLE
    return edge


def cycle_end_for(when, resets):
    """The end of the cycle containing `when`, and where that boundary came from.

    An announced reset governs the cycle it ends and the seven days before it.
    Anything outside every announcement falls back to the weekday rule, and
    the caller is told which, because a boundary that was read and one that
    was assumed do not deserve equal confidence in a report.
    """
    for reset in resets:
        if reset - CYCLE <= when < reset:
            return reset, "announced"
    return fallback_reset(when), "weekday rule"


class Cycle:
    """One provider week, and what the portfolio spent inside it."""

    def __init__(self, start, end, source):
        self.start = start
        self.end = end
        self.source = source
        self.runs = []
        self.clipped = False

    # -- what was spent ---------------------------------------------------
    @property
    def turns(self):
        return sum(r["turns"] or 0 for r in self.runs)

    @property
    def unpriced(self):
        """Runs the host gave no turn count for, so every total is a floor."""
        return sum(1 for r in self.runs if r.get("turns") is None)

    @property
    def priced(self):
        return len(self.runs) - self.unpriced

    @property
    def live_runs(self):
        return [r for r in self.runs if (r.get("turns") or 0) > 1]

    @property
    def last_live(self):
        return max((r["started"] for r in self.live_runs), default=None)

    # -- what refused it --------------------------------------------------
    def refusals(self, kind):
        return [r for r in self.runs if r.get("refusal") == kind]

    @property
    def first_weekly_refusal(self):
        return min((r["started"] for r in self.refusals("weekly-limit")),
                   default=None)

    @property
    def turns_before_the_wall(self):
        """The pool's height: what was spent before the first weekly refusal.

        Everything after the wall is runs being turned away at turn 1, which
        is noise added to the number that is meant to be the wall's height.
        """
        wall = self.first_weekly_refusal
        if wall is None:
            return None
        return sum(r["turns"] or 0 for r in self.runs if r["started"] < wall)

    @property
    def hours_to_the_wall(self):
        wall = self.first_weekly_refusal
        if wall is None:
            return None
        return (wall - self.start).total_seconds() / 3600

    def refused_seats(self, kind):
        return sorted({r["seat"] for r in self.refusals(kind)})

    def refused_crons(self, kind):
        return [r for r in self.refusals(kind) if r["trigger"] == "cron"]

    # -- the shape of the week -------------------------------------------
    def dark_hours(self, now=None):
        """Hours from the last run past turn 1 to the cycle's end, or to `now`."""
        last = self.last_live
        if last is None:
            return None
        edge = min(self.end, now) if now is not None else self.end
        return max(0.0, (edge - last).total_seconds() / 3600)

    def is_live(self, now):
        return now is not None and self.start <= now < self.end

    def verdict(self, now=None):
        """What this cycle is evidence of.

        `weekly-exhausted` is the only one that bounds the pool. `clipped` and
        `complete` are floors, for the same reason in two different ways: one
        did not spend the pool, the other may have and the archive no longer
        holds the proof.
        """
        if self.is_live(now):
            if self.refusals("monthly-spend"):
                return "monthly-capped"
            return "weekly-exhausted" if self.refusals("weekly-limit") else "live"
        if not self.runs:
            return "empty"
        if self.clipped:
            return "clipped"
        if self.priced < MIN_RUNS_TO_BOUND:
            return "thin"
        if self.refusals("weekly-limit"):
            return "weekly-exhausted"
        return "complete"

    def bounds_the_pool(self, now=None):
        """A cycle bounds the pool only if it spent some of it before refusing.

        The `> 0` is not defensive. A cycle that opens already refused has a
        pool height of zero turns, which is a statement about the window's
        edges and not about the provider, and a ceiling of zero would make
        every projection fail.
        """
        return (self.verdict(now) == "weekly-exhausted"
                and not self.is_live(now)
                and (self.turns_before_the_wall or 0) > 0)

    def as_dict(self, now=None):
        last = self.last_live
        return {
            "start": self.start.isoformat().replace("+00:00", "Z"),
            "end": self.end.isoformat().replace("+00:00", "Z"),
            "boundary": self.source,
            "verdict": self.verdict(now),
            "clipped": self.clipped,
            "runs": len(self.runs),
            "runs_past_turn_1": len(self.live_runs),
            "runs_unpriced": self.unpriced,
            "turns": self.turns,
            "turns_before_the_wall": self.turns_before_the_wall,
            "hours_to_the_wall": self.hours_to_the_wall,
            "last_live_at": last.isoformat().replace("+00:00", "Z") if last else None,
            "dark_hours": self.dark_hours(now),
            "weekly_refusals": len(self.refusals("weekly-limit")),
            "monthly_refusals": len(self.refusals("monthly-spend")),
            "session_refusals": len(self.refusals("session-limit")),
            "weekly_refused_cron_slots": len(self.refused_crons("weekly-limit")),
            "monthly_refused_cron_slots": len(self.refused_crons("monthly-spend")),
            "monthly_refused_seats": self.refused_seats("monthly-spend"),
        }


def build_cycles(runs, now=None):
    """Every cycle the runs fall into, oldest first, boundaries read where read.

    The oldest cycle is marked `clipped` when the archive's earliest run starts
    after the cycle does, because the host prunes and a cycle whose opening
    hours are gone cannot say what was spent in them.
    """
    resets = announced_resets(runs)
    cycles = {}
    for run in runs:
        end, source = cycle_end_for(run["started"], resets)
        cycle = cycles.get(end)
        if cycle is None:
            cycle = cycles[end] = Cycle(end - CYCLE, end, source)
        cycle.runs.append(run)
    if now is not None:
        end, source = cycle_end_for(now, resets)
        if end not in cycles:
            cycles[end] = Cycle(end - CYCLE, end, source)

    ordered = [cycles[end] for end in sorted(cycles)]
    if runs:
        archive_start = min(r["started"] for r in runs)
        for cycle in ordered:
            # A tolerance would be guesswork. The question is whether the
            # archive holds anything from before this cycle; if it does not,
            # the cycle's own opening is the archive's opening and the hours
            # before it are unreadable rather than quiet.
            cycle.clipped = archive_start > cycle.start and not cycle.is_live(now)
    return ordered


def measure_pool(cycles, now=None):
    """The pool's size, from the cycles that proved it by spending it.

    Returns the spread rather than one number, because three cycles agreeing
    to within five percent and one cycle on its own are different evidence and
    a single figure cannot tell them apart.
    """
    bounding = [c for c in cycles if c.bounds_the_pool(now)]
    floors = [c for c in cycles if c.verdict(now) in ("complete", "clipped")]
    values = sorted(c.turns_before_the_wall for c in bounding)
    pool = {
        "cycles": len(values),
        "turns": values,
        # The spread is carried rather than collapsed. Four cycles measured
        # the pool at 29,955 to 40,856 turns, a 36% span, and a single figure
        # cannot say whether the burn is certainly going to empty it or only
        # possibly. The projection below answers both ends, and the gate fires
        # on the optimistic one, so that being red means trouble rather than
        # meaning the estimate was conservative.
        "low": values[0] if values else None,
        "high": values[-1] if values else None,
        "estimate": values[0] if values else None,
        "floor_from_unbounding_cycles": max((c.turns for c in floors), default=None),
        "excluded": {
            "clipped": sum(1 for c in cycles if c.verdict(now) == "clipped"),
            "complete": sum(1 for c in cycles if c.verdict(now) == "complete"),
            "thin": sum(1 for c in cycles if c.verdict(now) == "thin"),
        },
    }
    hours = CYCLE.total_seconds() / 3600
    pool["sustainable_turns_per_hour"] = (
        pool["estimate"] / hours if pool["estimate"] else None)
    return pool


def project(cycle, pool, now):
    """Where the live cycle's burn rate lands it, against the pool and the reset.

    The rate is turns per hour since the cycle opened, not an instantaneous
    one. A cycle that spent everything in its first day and has been dark
    since still reads as a high average, which is correct: the pool is gone
    either way, and the verdict is what says so.
    """
    elapsed = (now - cycle.start).total_seconds() / 3600
    out = {
        "elapsed_hours": elapsed,
        "remaining_hours": (cycle.end - now).total_seconds() / 3600,
        "turns_spent": cycle.turns,
        "burn_turns_per_hour": cycle.turns / elapsed if elapsed > 0 else None,
        "pool_low": pool["low"],
        "pool_high": pool["high"],
        "share_of_pool_low": None,
        "share_of_pool_high": None,
        "empties_at_soonest": None,
        "empties_at_latest": None,
        "hours_short_soonest": None,
        "hours_short_latest": None,
        "certain": False,
        "projectable": True,
        "why_not_projectable": None,
    }
    if cycle.refusals("monthly-spend"):
        out["projectable"] = False
        out["why_not_projectable"] = (
            "the org's monthly spend cap is refusing runs in this cycle, and it "
            "is not a function of the weekly pool or of elapsed time")
        return out
    if not pool["low"]:
        out["projectable"] = False
        out["why_not_projectable"] = (
            "no cycle in this archive both hit the weekly wall and kept its "
            "opening hours, so the pool is unmeasured here")
        return out
    # How much of the pool is gone is true at any point in the cycle, so it is
    # answered before the gate below. Only the *projection* needs a sample.
    out["share_of_pool_low"] = cycle.turns / pool["low"]
    out["share_of_pool_high"] = cycle.turns / pool["high"]

    if elapsed < MIN_ELAPSED_HOURS:
        out["projectable"] = False
        out["why_not_projectable"] = (
            f"only {elapsed:.1f}h of the cycle has elapsed, and every seat the "
            f"last cycle refused re-fires in the first of them, so the average "
            f"rate is a herd rather than a pace (needs {MIN_ELAPSED_HOURS:.0f}h)")
        return out

    rate = out["burn_turns_per_hour"]
    if rate and rate > 0:
        soonest = cycle.start + dt.timedelta(hours=pool["low"] / rate)
        latest = cycle.start + dt.timedelta(hours=pool["high"] / rate)
        out["empties_at_soonest"] = soonest.isoformat().replace("+00:00", "Z")
        out["empties_at_latest"] = latest.isoformat().replace("+00:00", "Z")
        out["hours_short_soonest"] = (cycle.end - soonest).total_seconds() / 3600
        out["hours_short_latest"] = (cycle.end - latest).total_seconds() / 3600
        # Certain means even the largest pool this archive has measured runs
        # out before the reset. That is the condition worth waking somebody
        # for; the low end alone is a watch, not an alarm.
        out["certain"] = out["hours_short_latest"] > 0
    return out


def assess(runs, now):
    """The state of the cycles as of `now`, from what was knowable by then.

    The filter is the whole reason `--now` is trustworthy. Without it this
    read the entire archive and attributed it to the given instant, so asked
    about 2026-11-02T02:00Z it reported 39,775 turns spent and 257 monthly
    refusals that had not happened yet, and printed `dark for 0.0h` against a
    last-live stamp in its own future. A replay that can see the future
    cannot answer whether an alarm would have fired in time, which is the one
    question a new alarm has to answer.
    """
    runs = [r for r in runs if r["started"] <= now]
    cycles = build_cycles(runs, now)
    pool = measure_pool(cycles, now)
    live = next((c for c in cycles if c.is_live(now)), None)
    result = {
        "now": now.isoformat().replace("+00:00", "Z"),
        "pool": pool,
        "cycles": [c.as_dict(now) for c in cycles],
        "live": live.as_dict(now) if live else None,
        "projection": project(live, pool, now) if live else None,
    }
    result["exit"] = 1 if failing(result) else 0
    return result


def failing(result):
    """The three ways a live cycle is not going to survive its week."""
    live, proj = result["live"], result["projection"]
    if live is None or proj is None:
        return False
    if live["verdict"] in ("weekly-exhausted", "monthly-capped"):
        return True
    return bool(proj.get("certain"))


def _hours(value):
    return "-" if value is None else f"{value:.1f}h"


def render(result, root):
    out = ["The provider's weekly pool, measured from the cycles that spent it",
           f"(read from {root}, at {result['now']})",
           ""]
    pool = result["pool"]
    if pool["cycles"]:
        spread = (f"{pool['low']:,} to {pool['high']:,}" if pool["cycles"] > 1
                  else f"{pool['low']:,}")
        out.append(f"  pool      {spread} turns a week, from {pool['cycles']} "
                   f"cycle(s) that hit the weekly wall")
        out.append(f"            a rate that lasts the week is "
                   f"{pool['sustainable_turns_per_hour']:,.0f} turns an hour "
                   f"on the low end")
    else:
        out.append("  pool      unmeasured here: no cycle in this archive both hit "
                   "the weekly wall and kept its opening hours")
        if pool["floor_from_unbounding_cycles"]:
            out.append(f"            it holds at least "
                       f"{pool['floor_from_unbounding_cycles']:,} turns, which is "
                       f"the most a cycle spent without being refused")
    excluded = pool["excluded"]
    if any(excluded.values()):
        out.append(f"            excluded from that: "
                   f"{excluded['clipped']} clipped by the archive's own start, "
                   f"{excluded['complete']} never refused, {excluded['thin']} too thin")
    out.append("")

    live, proj = result["live"], result["projection"]
    if live is None:
        out.append("  live      no cycle contains the given instant")
    else:
        out.append(f"  cycle     {live['start']} to {live['end']} "
                   f"(boundary: {live['boundary']})")
        out.append(f"  spent     {live['turns']:,} turns over "
                   f"{_hours(proj['elapsed_hours'])} of 168h, "
                   f"{live['runs_past_turn_1']} run(s) past turn 1")
        if live["runs_unpriced"]:
            out.append(f"            {live['runs_unpriced']} run(s) carry no turn "
                       f"count, so that total is a floor")
        if proj["burn_turns_per_hour"] is not None:
            burn = f"  burn      {proj['burn_turns_per_hour']:,.0f} turns an hour"
            if proj["share_of_pool_low"] is not None:
                burn += (f", {proj['share_of_pool_high'] * 100:.0f}% to "
                         f"{proj['share_of_pool_low'] * 100:.0f}% of the pool spent")
            out.append(burn)

        if live["verdict"] == "monthly-capped":
            out.append(f"  FAILING   the org's monthly spend cap is refusing runs: "
                       f"{live['monthly_refusals']} refusal(s) across "
                       f"{len(live['monthly_refused_seats'])} seat(s), of which "
                       f"{live['monthly_refused_cron_slots']} were cron slots")
            out.append( "            this is not the weekly pool and rescheduling does "
                        "not touch it. The provider's own")
            out.append( "            sentence names the remedy: raise the limit at "
                        "claude.ai/admin-settings/usage,")
            out.append( "            which is the owner's hand and no seat's")
            out.append(f"            dark for {_hours(live['dark_hours'])} since "
                       f"{live['last_live_at']}")
        elif live["verdict"] == "weekly-exhausted":
            out.append(f"  FAILING   the weekly pool is gone: {live['weekly_refusals']} "
                       f"refusal(s), of which "
                       f"{live['weekly_refused_cron_slots']} were cron slots")
            out.append(f"            it emptied {_hours(live['hours_to_the_wall'])} into "
                       f"the cycle, with {_hours(proj['remaining_hours'])} still to run")
            out.append(f"            dark for {_hours(live['dark_hours'])} since "
                       f"{live['last_live_at']}")
        elif not proj["projectable"]:
            out.append(f"  unknown   no projection: {proj['why_not_projectable']}")
        elif proj["certain"]:
            out.append(f"  FAILING   at this rate even the largest pool measured here "
                       f"empties {proj['empties_at_latest']},")
            out.append(f"            {_hours(proj['hours_short_latest'])} before the "
                       f"reset, and the smallest "
                       f"{_hours(proj['hours_short_soonest'])} before it")
            out.append( "            every cron slot after that is refused at turn 1")
        elif proj["hours_short_soonest"] is not None and proj["hours_short_soonest"] > 0:
            out.append(f"  watch     the smallest pool measured here empties "
                       f"{proj['empties_at_soonest']}, "
                       f"{_hours(proj['hours_short_soonest'])} early,")
            out.append( "            and the largest reaches the reset. Not an alarm "
                        "while the spread straddles it")
        else:
            out.append("  ok        this rate reaches the reset with the pool intact")
    out.append("")
    out.append("This cycle is not surviving its week." if result["exit"]
               else "The live cycle is inside its pool.")
    return "\n".join(out)


def render_history(result):
    out = ["", "  every cycle the archive can date",
           f"  {'cycle start':18s} {'verdict':17s} {'pool':>8s} {'turns':>8s} "
           f"{'to wall':>8s} {'dark':>7s} {'wk':>4s} {'mth':>4s}"]
    for c in result["cycles"]:
        wall = c["turns_before_the_wall"]
        out.append(f"  {c['start'][:16]:18s} {c['verdict']:17s} "
                   f"{(f'{wall:,}' if wall is not None else '-'):>8} "
                   f"{c['turns']:>8,} {_hours(c['hours_to_the_wall']):>8} "
                   f"{_hours(c['dark_hours']):>7} {c['weekly_refusals']:>4} "
                   f"{c['monthly_refusals']:>4}")
    out.append("")
    out.append("  `pool` is the turns spent before the first weekly refusal, which is")
    out.append("  the only column that bounds anything. A `clipped` or `complete` cycle")
    out.append("  is a floor: one lost its opening hours to the host's pruning, the")
    out.append("  other was never refused. `mth` is the monthly spend cap, which is a")
    out.append("  different limit with a different remedy.")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(cf.LOG_ROOT),
                        help="the host's per-run log directory")
    parser.add_argument("--now", help="ISO instant to judge from, for tests")
    parser.add_argument("--history", action="store_true",
                        help="print every cycle, not only the live one")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    now = (dt.datetime.fromisoformat(args.now.replace("Z", "+00:00"))
           if args.now else dt.datetime.now(UTC))
    runs = cf.read_runs(root=args.root)
    if not runs:
        print(f"No run logs under {args.root}, so the provider cycle is "
              f"unmeasured here, and that is not a failure.")
        return 0

    result = assess(runs, now)
    if args.json:
        print(json.dumps(result, indent=2))
        return result["exit"]
    print(render(result, args.root))
    if args.history:
        print(render_history(result))
    return result["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
