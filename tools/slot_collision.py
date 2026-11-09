#!/usr/bin/env python3
"""A cron slot that fires into a run already going is lost, so measure the slot.

    python3 tools/slot_collision.py                          # every declared slot on the roster
    python3 tools/slot_collision.py --seat alexandria-exo
    python3 tools/slot_collision.py --seat alexandria-exo --slot '0 14 * * 1'   # a candidate
    python3 tools/slot_collision.py --seat alexandria-exo --sweep              # rank all 168 hours
    python3 tools/slot_collision.py --json
    python3 tools/slot_collision.py --audit /path/to/audit.jsonl --roster /path/to/roster

Exit 0 when every declared slot this reader could observe landed in a minute
when its own seat was not already running. Exit 1 when one of them landed
inside a live run, or when a declared slot has no observable occurrence at all.

**Why this is a different question from `tools/cron_firing.py`.** That file is
retrospective and per-day: it reads the logs a firing left behind and says
whether the cycle produced anything. It learned to read `coalesced` on
2026-11-02. But a coalesced slot is only ever visible *after* the week is lost,
and the thing that decides whether it will be lost is the slot's own position
in the seat's traffic. That is a property of the clock, it is knowable in
advance, and nothing read it. This file reads it.

**The mechanism it is pointed at**, from the 2026-11-02 Ask 1 on
`docs/agents/hq-relay.md`: the host's pending holder is single-valued per seat,
so a cron slot that arrives while a run of that seat is live is held, and the
next message to that seat overwrites the held slot. Over all 17 coalesced cron
firings in the host's history the separation was perfect in both directions —
7 of 7 released when no message followed, 0 of 10 released when one did. So a
slot that lands inside a live run of a seat with inbox traffic is not at risk,
it is lost, and the only remedy available in a manifest is the slot's minute.

**Three states, and the third is the one this file exists to add.**

- `collided` — the seat was running at the slot's minute. An observation.
- `narrow` — the seat was not running, but the nearest run boundary is inside
  `--margin` minutes. A prediction, not an observation, so it does not fail
  the exit on its own. It is printed because a margin of two minutes read off
  a top-of-the-hour sample is how a slot gets chosen that looks clear and is
  not: on the three Sundays before this file was written, this seat's chain of
  released holds began at 23:02, 23:04 and 23:02Z, so `0 23 * * 0` is clear at
  the sampled minute on 6 of 6 Sundays with two minutes of margin behind it.
  Both readings are true of different questions. The answer that chooses a
  clock needs the second one.
- `unobserved` — the slot has no occurrence inside the seat's own record. This
  fails, deliberately. A zero over a denominator of zero is the reading this
  organization has now mistaken for health four times, and a clock that moved
  last night has exactly that shape.

**The window is the seat's own record and never the calendar.** The audit log
starts when the host started writing it and a seat's rows start when the seat
first ran, so occurrences are enumerated between that seat's first and last row
rather than over the whole file. A slot that came due before the seat existed is
not a clear slot.
"""

import argparse
import bisect
import json
import os
import re
import sys
from datetime import datetime, time, timedelta, timezone

HOST_AUDIT = "/srv/asc/state/.epito/audit.jsonl"
HOST_ROSTER = "/srv/asc/roster"
DEFAULT_MARGIN_MIN = 5


def parse_ts(s):
    """The host writes `2026-11-09T01:00:00.882Z`; some rows carry no millis."""
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


# ---------------------------------------------------------------- cron fields

class CronError(ValueError):
    pass


def _field(spec, lo, hi):
    """One cron field to the set of values it matches. `*`, `a`, `a-b`, `*/n`, lists."""
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise CronError("empty term in %r" % spec)
        step = 1
        if "/" in part:
            part, _, st = part.partition("/")
            if not st.isdigit() or int(st) < 1:
                raise CronError("bad step in %r" % spec)
            step = int(st)
        if part == "*":
            first, last = lo, hi
        elif "-" in part.lstrip("-"):
            a, _, b = part.partition("-")
            if not (a.isdigit() and b.isdigit()):
                raise CronError("bad range in %r" % spec)
            first, last = int(a), int(b)
        elif part.isdigit():
            first = last = int(part)
        else:
            raise CronError("unreadable term %r" % part)
        if first < lo or last > hi or first > last:
            raise CronError("%r is outside %d-%d" % (part, lo, hi))
        out.update(range(first, last + 1, step))
    return out


class Slot:
    """A five-field cron expression, matched the way cron matches it."""

    def __init__(self, expr):
        self.expr = expr.strip()
        fields = self.expr.split()
        if len(fields) != 5:
            raise CronError("a cron line has five fields, %r has %d" % (expr, len(fields)))
        self.minutes = _field(fields[0], 0, 59)
        self.hours = _field(fields[1], 0, 23)
        self.dom = _field(fields[2], 1, 31)
        self.month = _field(fields[3], 1, 12)
        dow = _field(fields[4], 0, 7)
        self.dow = set(0 if d == 7 else d for d in dow)
        # cron's own rule: when day-of-month and day-of-week are both
        # restricted, a day matching either one matches.
        self.dom_restricted = fields[2].strip() != "*"
        self.dow_restricted = fields[4].strip() != "*"

    def matches_day(self, d):
        if d.month not in self.month:
            return False
        dow = (d.weekday() + 1) % 7  # Monday=0 -> cron Sunday=0
        in_dom, in_dow = d.day in self.dom, dow in self.dow
        if self.dom_restricted and self.dow_restricted:
            return in_dom or in_dow
        return (in_dom if self.dom_restricted else True) and (in_dow if self.dow_restricted else True)

    def occurrences(self, start, end):
        """Every minute this slot fires in [start, end], in order."""
        out = []
        day = start.date()
        while day <= end.date():
            if self.matches_day(day):
                for h in sorted(self.hours):
                    for m in sorted(self.minutes):
                        t = datetime.combine(day, time(h, m), tzinfo=timezone.utc)
                        if start <= t <= end:
                            out.append(t)
            day += timedelta(days=1)
        return out


# ------------------------------------------------------------------ the record

def read_runs(audit_path, now):
    """Live intervals per agent, from the host's audit log.

    A `run.end` row carries `durationMs`, so the interval is end minus
    duration: that is the only pairing the log supports, because `run.start`
    rows carry no session id. A trailing `run.start` with no `run.end` after
    it is the run that is still going, and it is held open to `now` — leaving
    it out would report the asking run's own minute as free.
    """
    per_agent = {}
    first_row, last_row = {}, {}
    starts = {}
    with open(audit_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            agent, action = row.get("agent"), row.get("action")
            ts = parse_ts(row.get("ts", "")) if row.get("ts") else None
            if not agent or ts is None:
                continue
            if agent not in first_row or ts < first_row[agent]:
                first_row[agent] = ts
            if agent not in last_row or ts > last_row[agent]:
                last_row[agent] = ts
            if action == "run.end" and isinstance(row.get("durationMs"), (int, float)):
                per_agent.setdefault(agent, []).append(
                    (ts - timedelta(milliseconds=row["durationMs"]), ts, row.get("trigger")))
            elif action == "run.start":
                starts[agent] = (ts, row.get("trigger"))
    for agent, (ts, trigger) in starts.items():
        ends = per_agent.get(agent) or []
        if not ends or ts > max(e for _, e, _ in ends):
            per_agent.setdefault(agent, []).append((ts, max(ts, now), trigger))
    for agent in per_agent:
        per_agent[agent].sort()
    return per_agent, first_row, last_row


def classify(t, intervals, starts, margin, grace_sec=60):
    """`collided`, `narrow` or `clear` for one minute, with the margin in minutes.

    **The slot's own run is not a near miss, and reading it as one is how the
    first version of this file reported every uncollided slot on the roster as
    `narrow` with a sub-minute margin.** A cron slot that is received starts a
    run seconds later, so the nearest run boundary to a healthy slot is always
    the boundary that slot itself created. Twelve of twelve clear slots read
    `narrow` that way, which is a number that should be read as an artifact
    rather than as twelve coincidences. So a `cron`-triggered run beginning
    within `grace_sec` of the minute is the slot being delivered, and it is
    excluded from the margin.

    The grace is one minute, because every cron row the host has written
    started its run inside thirty seconds of the slot: 4.7s, 20.1s and 0.9s for
    the three firings of this seat. What remains is the margin that means
    something: how long before the slot a
    run of this seat ended, and how long after it an unrelated run began.
    """
    i = bisect.bisect_right(starts, t) - 1
    for j in (i, i + 1):
        if 0 <= j < len(intervals):
            s, e, _trigger = intervals[j]
            if s <= t <= e:
                return "collided", 0.0
    best = None
    for j in (i - 1, i, i + 1, i + 2):
        if not (0 <= j < len(intervals)):
            continue
        s, e, trigger = intervals[j]
        own = trigger == "cron" and timedelta(0) <= (s - t) <= timedelta(seconds=grace_sec)
        for b in (s, e):
            if own:
                continue
            d = abs((t - b).total_seconds()) / 60.0
            best = d if best is None else min(best, d)
    if best is None:
        return "clear", None
    return ("narrow" if best < margin else "clear"), best


def judge_slot(expr, agent, runs, window, margin):
    intervals = runs.get(agent) or []
    starts = [s for s, _e, _t in intervals]
    slot = Slot(expr)
    occ = slot.occurrences(*window)
    rows = []
    for t in occ:
        state, m = classify(t, intervals, starts, margin)
        rows.append({"at": t.isoformat().replace("+00:00", "Z"), "state": state, "margin_min": m})
    if not rows:
        verdict = "unobserved"
    elif any(r["state"] == "collided" for r in rows):
        verdict = "collided"
    elif any(r["state"] == "narrow" for r in rows):
        verdict = "narrow"
    else:
        verdict = "clear"
    # a collided occurrence has no margin to report: it has a loss. Mixing its
    # zero into the minimum makes every collided slot read as if its clear
    # occurrences were also on the edge, which is two findings wearing one number.
    margins = [r["margin_min"] for r in rows
               if r["margin_min"] is not None and r["state"] != "collided"]
    return {
        "seat": agent,
        "slot": slot.expr,
        "verdict": verdict,
        "occurrences": len(rows),
        "collided": sum(1 for r in rows if r["state"] == "collided"),
        "narrow": sum(1 for r in rows if r["state"] == "narrow"),
        "min_margin_min": min(margins) if margins else None,
        "window": [window[0].isoformat().replace("+00:00", "Z"),
                   window[1].isoformat().replace("+00:00", "Z")],
        "rows": rows,
    }


# ---------------------------------------------------------------- the manifest

CRON_RE = re.compile(r'^\s*cron\s*=\s*"([^"]*)"')
NAME_RE = re.compile(r'^\s*name\s*=\s*"([^"]*)"')


def declared_slots(roster):
    """Every `[trigger] cron` on the roster, with the agent name beside it.

    The host's directory name for a seat's logs is the manifest's `[agent]
    name`, so that is what is read rather than the path, which is how a seat
    whose directory and name disagree still gets measured.
    """
    out = []
    if not os.path.isdir(roster):
        return out
    for company in sorted(os.listdir(roster)):
        cdir = os.path.join(roster, company)
        if not os.path.isdir(cdir):
            continue
        for seat in sorted(os.listdir(cdir)):
            path = os.path.join(cdir, seat, "agent.toml")
            if not os.path.isfile(path):
                continue
            name, cron = None, None
            with open(path) as fh:
                for line in fh:
                    if name is None:
                        m = NAME_RE.match(line)
                        if m:
                            name = m.group(1)
                    if cron is None:
                        m = CRON_RE.match(line)
                        if m and m.group(1).strip():
                            cron = m.group(1).strip()
            if cron:
                out.append((name or "%s-%s" % (company, seat), cron, path))
    return out


# -------------------------------------------------------------------- printing

def fmt_margin(m):
    if m is None:
        return "no run in the record"
    if m >= 60:
        return "%.1fh" % (m / 60.0)
    if m < 1:
        return "under a minute"
    return "%dm" % round(m)


def print_report(results, margin, quiet_rows=False):
    for r in results:
        head = "%-26s %-14s %s" % (r["seat"], r["slot"], r["verdict"].upper())
        print(head)
        print("    occurrences in the seat's own record: %d  (%s .. %s)"
              % (r["occurrences"], r["window"][0][:16], r["window"][1][:16]))
        if r["occurrences"]:
            print("    collided %d, narrow %d, closest clear slot came within %s of a run"
                  % (r["collided"], r["narrow"],
                     fmt_margin(r["min_margin_min"]) if r["min_margin_min"] is not None
                     else "no boundary to measure"))
            if not quiet_rows:
                for row in r["rows"]:
                    detail = ("inside a live run of this seat" if row["state"] == "collided"
                              else fmt_margin(row["margin_min"]))
                    print("      %s  %-9s %s" % (row["at"][:16], row["state"], detail))
        else:
            print("    nothing to read: this slot has not come due inside the record,")
            print("    so a clear verdict here would be a zero over a denominator of zero")
        print()


def sweep(agent, runs, window, margin, top):
    """Every top-of-hour slot in the week, ranked by collisions then by margin."""
    intervals = runs.get(agent) or []
    starts = [s for s, _e, _t in intervals]
    names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    scored = []
    for dow in range(7):
        for hour in range(24):
            expr = "0 %d * * %d" % (hour, dow)
            occ = Slot(expr).occurrences(*window)
            states = [classify(t, intervals, starts, margin) for t in occ]
            coll = sum(1 for s, _ in states if s == "collided")
            margins = [m for _, m in states if m is not None]
            scored.append({
                "slot": expr, "label": "%s %02d:00Z" % (names[dow], hour),
                "occurrences": len(occ), "collided": coll,
                "min_margin_min": min(margins) if margins else None,
            })
    def key(s):
        if not s["occurrences"]:
            return (2, 0, 0)
        return (0 if not s["collided"] else 1,
                s["collided"] / s["occurrences"],
                -(s["min_margin_min"] if s["min_margin_min"] is not None else 1e9))
    scored.sort(key=key)
    return scored[:top] if top else scored


def main(argv=None):
    p = argparse.ArgumentParser(
        description="A cron slot that fires into a run already going is lost, so measure the slot.")
    p.add_argument("--audit", default=HOST_AUDIT, help="the host's audit log")
    p.add_argument("--roster", default=HOST_ROSTER, help="the deployed roster, which declares the slots")
    p.add_argument("--seat", help="one seat, by the manifest's agent name (`alexandria-exo`)")
    p.add_argument("--slot", help="a candidate cron line to measure instead of the declared one; needs --seat")
    p.add_argument("--sweep", action="store_true",
                   help="rank every top-of-hour slot in the week for --seat, best first")
    p.add_argument("--top", type=int, default=10, help="how many rows --sweep prints; 0 for all 168")
    p.add_argument("--margin", type=float, default=DEFAULT_MARGIN_MIN,
                   help="minutes of clearance under which a clear slot is reported `narrow`")
    p.add_argument("--now", help="pin the clock, so a reading can be reproduced")
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument("--quiet-rows", action="store_true", help="the verdicts without the per-occurrence lines")
    args = p.parse_args(argv)

    now = parse_ts(args.now) if args.now else datetime.now(timezone.utc)
    if now is None:
        print("--now is not a readable stamp: %r" % args.now, file=sys.stderr)
        return 2
    if not os.path.exists(args.audit):
        print("no audit log at %s, so there is nothing to read; this reader needs the "
              "host's own record and does not run on a pull request checkout" % args.audit,
              file=sys.stderr)
        return 2

    runs, first_row, last_row = read_runs(args.audit, now)

    def window_for(agent):
        return (first_row.get(agent, now), min(last_row.get(agent, now), now))

    if args.sweep:
        if not args.seat:
            print("--sweep measures one seat, so it needs --seat", file=sys.stderr)
            return 2
        rows = sweep(args.seat, runs, window_for(args.seat), args.margin, args.top)
        if args.as_json:
            print(json.dumps({"seat": args.seat, "sweep": rows}, indent=2))
            return 0
        print("every top-of-hour slot for %s, best first (%d occurrence%s of each in the record)"
              % (args.seat, rows[0]["occurrences"] if rows else 0,
                 "" if rows and rows[0]["occurrences"] == 1 else "s"))
        for s in rows:
            print("  %-12s collided %d of %-3d nearest boundary %s"
                  % (s["label"], s["collided"], s["occurrences"], fmt_margin(s["min_margin_min"])))
        return 0

    if args.slot:
        if not args.seat:
            print("--slot measures one seat's clock, so it needs --seat", file=sys.stderr)
            return 2
        targets = [(args.seat, args.slot, "--slot")]
    else:
        targets = [(n, c, p) for (n, c, p) in declared_slots(args.roster)
                   if not args.seat or n == args.seat]
        if not targets:
            where = "for %s " % args.seat if args.seat else ""
            print("no declared cron %son the roster at %s" % (where, args.roster), file=sys.stderr)
            return 2

    results, bad = [], []
    for name, expr, _src in targets:
        try:
            r = judge_slot(expr, name, runs, window_for(name), args.margin)
        except CronError as exc:
            bad.append({"seat": name, "slot": expr, "verdict": "unreadable", "why": str(exc)})
            continue
        results.append(r)

    findings = [r for r in results if r["verdict"] in ("collided", "unobserved")] + bad
    if args.as_json:
        print(json.dumps({"now": now.isoformat().replace("+00:00", "Z"),
                          "margin_min": args.margin,
                          "results": results + bad,
                          "findings": len(findings)}, indent=2))
        return 1 if findings else 0

    print_report(results, args.margin, quiet_rows=args.quiet_rows)
    for b in bad:
        print("%-26s %-14s UNREADABLE  %s" % (b["seat"], b["slot"], b["why"]))
    if findings:
        print("%d slot%s a seat cannot be relied on to receive: %s"
              % (len(findings), "" if len(findings) == 1 else "s",
                 ", ".join("%s %s (%s)" % (f["seat"], f["slot"], f["verdict"]) for f in findings)))
    else:
        print("every declared slot this reader could observe fell in a minute its own seat was idle")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
