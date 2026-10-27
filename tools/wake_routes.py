#!/usr/bin/env python3
"""A subscription that cannot route is a seat that will never be woken, and
nothing in any repository has ever checked one.

    python3 tools/wake_routes.py                     # this company, every seat
    python3 tools/wake_routes.py --seat security
    python3 tools/wake_routes.py --json              # the verdict as a script reads it
    python3 tools/wake_routes.py --company alexandria --roster /srv/asc/roster \
        --audit /srv/asc/state/.epito/audit.jsonl --prompts prompts

Exit 0 when every seat's subscribed event types can reach it. Exit 1 when a
seat is deaf on one, which is the thing this file exists to make visible.

## Why this exists

`docs/agents/hq-relay.md`, 2026-10-24, closing paragraph of the cadence entry:

> A prefix that names no seat produces no target, and that is correct
> behaviour with no signal attached. There is no log line, no bounced delivery
> and no counter: the event is simply not routed. Any company whose charters
> predate the `<company>-<seat>` convention has seats that are silently deaf
> on `pr.merged` and `check.failed`, and the only way to find them is to
> resolve every charter's declared prefix against the roster. That sweep is
> cheap and nothing in any repository runs it. It belongs beside the cron-slot
> instrument rather than in twelve separate charters.

This is that sweep, beside `tools/cron_firing.py` as that paragraph asked. It
was written on 2026-10-26, two days later, by the ExO seat whose own board
lane held the card the sweep serves.

## The three states, because two is what gets this wrong

`cron_firing.py` learned this the hard way and the reasoning transfers whole:
absence is weak evidence, so a check that answers reachable-or-not answers the
wrong question. A route can be impossible, possible, or demonstrated, and only
the first is a defect.

`deaf`
    The bus's own rules cannot produce this seat as a target for this type.
    The reason is carried with it. `prefix` is a charter that declares a
    branch prefix resolving to no seat in the roster, which is how
    `alexandria/security` has been deaf on `pr.merged` and `check.failed` for
    as long as both have existed. `no-prefix` is a charter that names no
    prefix at all, so each run of the seat invents one and the route depends
    on a habit rather than on an instruction. `cadence` is the continue-wake
    gate declining a seat the company declared slower than a day.

`open`
    The rules permit it and no wake of the seat has ever been observed. This
    is **not** reported as a failure. A route that is open and unused looks
    exactly like a route that is open and nobody has had occasion to use, and
    this file cannot tell them apart. It is reported as a question with the
    evidence that formed it: the seat's whole wake history, which is often
    empty.

`live`
    The rules permit it and the host's audit log shows this seat being woken.
    Per-type attribution is not available — `run.start` carries a trigger
    word (`message`, `hook`, `cron`, `window`) and never an event type, which
    is the same asymmetry the ExO charter's §0 records for the weekly
    doorbell — so `live` is a statement about the seat's reachability and not
    about this one type. A seat with wakes is reachable; a seat with none is
    the finding.

## What this does not do

It does not read the bus. The routing rules below are transcribed from
`runtime/board/api.py` in `alexandrapaiz/alexandra-systems` at the commit read
on 2026-10-26, and a transcription goes stale. `--rules` prints them with
their source so a reader can diff them against the parent by hand, and the
`ROUTING_READ_AT` constant is the date to distrust. That is a worse design
than importing the real thing and it is the only one available from here: the
bus is in another repository and this repository has no copy.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROUTING_READ_AT = "2026-10-26"
ROUTING_SOURCE = "alexandrapaiz/alexandra-systems:runtime/board/api.py Bus._targets"

# `seat_of_branch`, transcribed: the segment before the first slash, with the
# company prefix stripped when present. main, master and chair belong to nobody.
NOBODY = ("main", "master", "chair")

# NO_SELF_CONTINUE, transcribed. A cadence word nobody wrote down fails OPEN.
NO_SELF_CONTINUE = {"monthly", "quarterly", "dispatch-only", "none"}

# The types whose target is the branch prefix, so a prefix naming no seat is
# a route that cannot exist.
PREFIX_ROUTED = ("pr.merged", "check.failed")
# The types whose target is the addressee or the item's own seat: always
# routable in principle, because another party chooses the target.
ADDRESSED = ("message.posted", "item.moved")
# The types with a fixed target list rather than a computed one.
FIXED = {"brief.sent": "the learning loop's seats",
         "week.started": "the learning loop's seats"}
# The types whose target is always the company's PM seat, whoever acted.
PM_ROUTED = ("run.failed", "run.reported", "pr.opened")
# `check.never_started` is prefix-routed like a red check, and suppressed while
# the repository's runners are measurably dead (incident 16). Prefix-routed for
# this file's purposes: a prefix naming no seat still wakes nobody.
PREFIX_ROUTED_SUPPRESSIBLE = ("check.never_started",)


def seat_of_branch(ref: str, company: str) -> str:
    """Transcribed from the bus. Kept byte-faithful on purpose."""
    head = (ref or "").split("/")[0].lower()
    if not head or head in NOBODY:
        return ""
    low = company.lower() + "-"
    return head[len(low):] if head.startswith(low) else head


def roster_seats(roster: str, company: str) -> dict:
    """{seat: {name, cron, subscriptions, entry, max_turns}} from the host's own
    copy of the manifests, which is the copy the runtime enforces."""
    out = {}
    for path in sorted(glob.glob(os.path.join(roster, company, "*", "agent.toml"))):
        seat = os.path.basename(os.path.dirname(path))
        text = open(path).read()

        def one(key):
            m = re.search(r'^\s*%s\s*=\s*"([^"]*)"' % key, text, re.M)
            return m.group(1) if m else None

        subs = []
        m = re.search(r'^\s*subscriptions\s*=\s*\[(.*?)\]', text, re.M | re.S)
        if m:
            subs = re.findall(r'"([^"]+)"', m.group(1))
        out[seat] = {"name": one("name"), "cron": one("cron"),
                     "entry": one("entry"), "subscriptions": subs}
    return out


def charter_prefix(prompts: str, seat: str) -> tuple:
    """(prefix, evidence) for the branch prefix a seat's charter tells it to use.

    Returns (None, reason) when the charter names none. The pattern is the
    instruction every charter in this repository writes it with — "on a branch
    named X" — and it deliberately does not fall back to guessing from the
    seat's own branch history, because a prefix a run invented is the thing
    this file is looking for rather than an answer to it."""
    path = os.path.join(prompts, "%s-agent.md" % seat)
    if not os.path.exists(path):
        return None, "no charter at %s" % path
    text = open(path).read()
    # Whitespace-insensitive on purpose: `exo` and `frontend` both wrap this
    # instruction over a line break, and the first version of this function
    # read line by line and reported both as declaring no prefix. A false
    # `no-prefix` on two of twelve seats is exactly the kind of finding this
    # file exists to prevent, so it is recorded here rather than quietly fixed.
    m = re.search(r'branch\s+named\s+`?([A-Za-z][A-Za-z0-9-]*)/', text, re.S)
    if not m:
        return None, "%s declares no branch prefix" % path
    line_no = text[:m.start()].count("\n") + 1
    return m.group(1), "%s:%d" % (path, line_no)


def cadences(company_yaml: str) -> dict:
    """{seat: cadence} out of the company manifest, in the flow-mapping shape
    this company writes. A line this cannot read is a seat it does not name,
    which the bus reads as "wake" — so an absence here is never a defect."""
    out = {}
    if not os.path.exists(company_yaml):
        return out
    for line in open(company_yaml):
        name = re.search(r'name:\s*([A-Za-z0-9_-]+)', line)
        cad = re.search(r'cadence:\s*([A-Za-z0-9_-]+)', line)
        if name and cad:
            out[name.group(1)] = cad.group(1)
    return out


def wakes(audit: str, company: str) -> dict:
    """{seat: {trigger: [count, last_ts]}} from the host's audit log. Only
    `run.start` rows, because a run that started is a wake that landed."""
    out = {}
    if not os.path.exists(audit):
        return out
    pre = company + "-"
    for line in open(audit):
        try:
            d = json.loads(line)
        except Exception:                                 # noqa: BLE001
            continue
        agent = d.get("agent") or ""
        if not agent.startswith(pre) or d.get("action") != "run.start":
            continue
        seat = agent[len(pre):]
        t = d.get("trigger") or "?"
        row = out.setdefault(seat, {}).setdefault(t, [0, None])
        row[0] += 1
        row[1] = (d.get("ts") or "")[:19]
    return out


def verdict(company, roster, prompts, audit, company_yaml):
    seats = roster_seats(roster, company)
    cads = cadences(company_yaml)
    woke = wakes(audit, company)
    names = set(seats)
    rows = []
    for seat, man in sorted(seats.items()):
        prefix, where = charter_prefix(prompts, seat)
        resolved = seat_of_branch("%s/x" % prefix, company) if prefix else ""
        prefix_ok = bool(resolved) and resolved in names
        cad = (cads.get(seat) or "").strip().lower()
        continues = cad not in NO_SELF_CONTINUE
        w = woke.get(seat) or {}
        # `window` is a hand-opened session, not a routed event. A seat whose
        # only rows are windows has never been woken by the bus at all, and
        # that distinction is the whole point of this column.
        routed = {k: v for k, v in w.items() if k in ("message", "hook", "cron")}
        types = {}
        for t in man["subscriptions"]:
            if t in PREFIX_ROUTED:
                if not prefix:
                    types[t] = ("deaf", "no-prefix", where)
                elif not prefix_ok:
                    detail = "`%s/` resolves to `%s`, no such seat (%s)" % (prefix, resolved, where)
                    if t == "pr.merged":
                        # One type can have two defects and a prefix that names
                        # no seat decides first, so the cadence gate's answer is
                        # unobservable behind it. That masking is not
                        # hypothetical: it is what hid `security`'s missing
                        # `semimonthly` word for as long as both existed
                        # (docs/agents/hq-relay.md, 2026-10-24). Both reasons
                        # are printed rather than the first one.
                        detail += "; behind it the cadence gate would %s (cadence `%s`)" % (
                            "allow the continue-wake" if continues else "decline it", cad or "unset")
                    types[t] = ("deaf", "prefix", detail)
                elif t == "pr.merged" and not continues:
                    # By design, and the bus says so in its own comment: a seat
                    # slower than a day does not re-wake itself off its own
                    # merge, after HQ's monthly finance seat ran seven times in
                    # one morning on 2026-10-18. Reported, never a failure.
                    types[t] = ("gated", "cadence", "cadence `%s` is in the continue-wake "
                                                    "suppression set, by design" % cad)
                else:
                    types[t] = ("live" if routed else "open", "", "")
            elif t in PREFIX_ROUTED_SUPPRESSIBLE:
                if not prefix:
                    types[t] = ("deaf", "no-prefix", where)
                elif not prefix_ok:
                    types[t] = ("deaf", "prefix", "`%s/` resolves to `%s`, no such seat (%s)"
                                % (prefix, resolved, where))
                else:
                    types[t] = ("live" if routed else "open", "", "")
            elif t in ADDRESSED or t in FIXED or t in PM_ROUTED:
                types[t] = ("live" if routed else "open", "", "")
            else:
                types[t] = ("unknown", "type not in the transcribed rules", "")
        rows.append({"seat": seat, "cron": man["cron"], "cadence": cad or None,
                     "prefix": prefix, "prefix_source": where,
                     "prefix_resolves_to": resolved or None, "prefix_ok": prefix_ok,
                     "continues_on_own_merge": continues,
                     "subscriptions": man["subscriptions"],
                     "types": types,
                     "wakes": {k: v[0] for k, v in sorted(routed.items())},
                     "last_wake": max([v[1] for v in routed.values()], default=None),
                     "window_runs": (w.get("window") or [0, None])[0],
                     "ever_woken": bool(routed)})
    return rows


def render(rows, company, prompts=None):
    deaf = [(r["seat"], t, d[1], d[2]) for r in rows for t, d in sorted(r["types"].items())
            if d[0] == "deaf"]
    silent = [r for r in rows if not r["ever_woken"]]
    print("wake routes — %s, rules transcribed %s from %s"
          % (company, ROUTING_READ_AT, ROUTING_SOURCE))
    print(prefix_provenance(prompts))
    print()
    print("%-10s %-22s %-6s %s" % ("seat", "prefix", "wakes", "every subscribed type"))
    for r in rows:
        states = []
        for t, d in sorted(r["types"].items()):
            states.append("%s=%s%s" % (t, d[0], (":" + d[1]) if d[1] else ""))
        pre = r["prefix"] + "/" if r["prefix"] else "(none declared)"
        if not r["prefix_ok"] and r["prefix"]:
            pre += " !"
        print("%-10s %-22s %-6s %s"
              % (r["seat"], pre, sum(r["wakes"].values()), " ".join(states)))
    print()
    if silent:
        print("Never woken by the bus (%d of %d seats): %s"
              % (len(silent), len(rows), ", ".join(r["seat"] for r in silent)))
        for r in silent:
            print("  %-10s %d subscriptions, %d hand-opened window runs, no routed wake ever"
                  % (r["seat"], len(r["subscriptions"]), r["window_runs"]))
        print()
    gated = [(r["seat"], t, d[2]) for r in rows for t, d in sorted(r["types"].items())
             if d[0] == "gated"]
    if gated:
        print("GATED — declined on purpose, not a defect:")
        for seat, t, detail in gated:
            print("  %-10s %-14s %s" % (seat, t, detail))
        print()
    if deaf:
        print("DEAF — a subscribed type the rules cannot route to this seat:")
        for seat, t, why, detail in deaf:
            print("  %-10s %-14s %-10s %s" % (seat, t, why, detail))
    else:
        print("No seat is deaf on a subscribed type.")
    return 1 if deaf else 0


def prefix_provenance(prompts):
    """Which world the `prefix` column describes, which is not the world the
    `wakes` column describes (added 2026-10-26).

    The prefix is read out of the working checkout and the wake counts are read
    out of the host's audit log, so on a branch this report mixes a charter that
    only exists here with routing that only happened out there, and prints them
    side by side as though they were one world. It cost a false finding in the
    run after the one that shipped this file: `alexandria-research` appeared
    with a resolving prefix and two wakes, and was reported as a prefix fix
    taking effect on the bus. The prefix fix was on an unmerged branch. The two
    wakes were a capacity re-fire and the message its pull request produced,
    and neither needs a prefix to route at all.

    So the line below says which charters were read and whether they match the
    branch everything else here is about. Nothing is suppressed: a defect found
    on a branch is still a defect, it is just not yet a defect of `main`."""
    note = "prefixes read from %s" % (prompts or "prompts")
    try:
        import subprocess
        changed = subprocess.run(
            ["git", "diff", "--name-only", "origin/main", "--", prompts or "prompts"],
            capture_output=True, text=True, timeout=15)
        if changed.returncode == 0:
            names = [n for n in changed.stdout.split() if n]
            if names:
                return (note + " — WHICH DIFFERS FROM origin/main IN %d FILE(S). "
                        "The prefix column describes this checkout and the wakes "
                        "column describes the deployed world. A prefix that "
                        "resolves only here has not changed any routing yet."
                        % len(names))
            return note + ", which matches origin/main"
    except (OSError, subprocess.SubprocessError):
        pass
    return (note + " — and whether that matches origin/main could not be "
            "determined, so read the prefix column as a statement about this "
            "checkout only")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--company", default="alexandria")
    p.add_argument("--roster", default="/srv/asc/roster")
    p.add_argument("--prompts", default="prompts")
    p.add_argument("--audit", default="/srv/asc/state/.epito/audit.jsonl")
    p.add_argument("--company-yaml", default="company.yaml")
    p.add_argument("--seat")
    p.add_argument("--json", action="store_true")
    p.add_argument("--rules", action="store_true",
                   help="print the transcribed routing rules and their source, then exit")
    a = p.parse_args(argv)
    if a.rules:
        print("transcribed %s from %s" % (ROUTING_READ_AT, ROUTING_SOURCE))
        print("  seat_of_branch: first path segment, lowercased, `<company>-` stripped;")
        print("                  main, master and chair belong to nobody")
        print("  prefix-routed types: %s" % ", ".join(PREFIX_ROUTED))
        print("  addressed types:     %s" % ", ".join(ADDRESSED))
        print("  fixed-target types:  %s" % ", ".join(sorted(FIXED)))
        print("  NO_SELF_CONTINUE:    %s" % ", ".join(sorted(NO_SELF_CONTINUE)))
        return 0
    rows = verdict(a.company, a.roster, a.prompts, a.audit, a.company_yaml)
    if not rows:
        print("no seats found under %s/%s — wrong --roster, or a company with no manifests"
              % (a.roster, a.company), file=sys.stderr)
        return 2
    if a.seat:
        rows = [r for r in rows if r["seat"] == a.seat]
        if not rows:
            print("no seat named %s in %s" % (a.seat, a.company), file=sys.stderr)
            return 2
    if a.json:
        print(json.dumps({"company": a.company, "routing_read_at": ROUTING_READ_AT,
                          "routing_source": ROUTING_SOURCE, "seats": rows}, indent=2))
        return 1 if any(d[0] == "deaf" for r in rows for d in r["types"].values()) else 0
    return render(rows, a.company, a.prompts)


if __name__ == "__main__":
    sys.exit(main())
