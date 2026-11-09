#!/usr/bin/env python3
"""How full is the volume, how much of it can this seat see, and what is the gap?

    python3 tools/host_headroom.py                    # the three numbers and the verdict
    python3 tools/host_headroom.py --path /tmp        # a different mount to ask about
    python3 tools/host_headroom.py --compose srv=/srv/asc tmp=/tmp
                                                      # a composition, with its residual
    python3 tools/host_headroom.py --json
    python3 tools/host_headroom.py --self-check       # the properties, printed

Exit 0 when the reading was taken, 1 when a `--compose` leaves a residual at
least as large as its own largest named component, or overcounts, or names one
path inside another, and 2 when the reading
cannot be taken at all, which is a refusal to answer rather than an answer of
"fine".

## Why a reporter prints three numbers and never one

`df` answers about a device. `du` answers about a directory. On this host they
are not two views of one quantity, because `/tmp` as a seat sees it is a bind
mount of a subdirectory of `/dev/sda1` and not the device's root:

    /tmp   /dev/sda1[/tmp/systemd-private-<id>-epitod.service-<id>/tmp]   ext4

`df` reports the whole device because that is what `df` does, and `du` reports
the subtree because that is all there is to walk. The bind source cannot be
reached by its own path from inside the namespace -- `ls -d /tmp/systemd-private-*`
is `No such file or directory`, and the visible `/tmp` has an inode that is not
2 -- so the difference is not merely unmeasured, it is unmeasurable from here.
Measured 2026-11-09: device 42.9 GiB used, visible 13.8 GiB, gap 29.1 GiB.

A reporter that prints only the `df` percentage therefore attributes a
host-level figure to a seat, and every seat-side reclaimer built to that
percentage has a ceiling near a third of the problem with a number that will
not move when it works perfectly. A reporter that prints only `du` understates
the wall every seat is about to hit. So this one prints both and the
subtraction, and it names the gap's disposition as outside the fleet rather
than as a gap in anybody's tool.

The register for the class is
`INC-2026-11-09-the-volume-is-99-percent-full-and-two-thirds-of-it-is-outside-every-seats-mount-namespace`
(engineer seat), and the four 2026-11-02 entries it supersedes on this point
all reason from the percentage to content a seat could enumerate.

## Why `--compose` exists, and it is this seat's own defect

The gap did not need tonight's `findmnt` to be visible. It had been printed
twice already, as addition that nobody performed:

- The 2026-11-02 register entry reads `44G used`, then `/srv/asc` at 18G and
  `/tmp` at 17G. 18 + 17 = 35. Nine gigabytes sat unnamed between two numbers
  in one sentence.
- This seat's own relay row for that day is worse, because it carried a
  claim word: "**Composition measured**: `/srv/asc` is 18G of fixed
  infrastructure holding no sandbox at all, `/tmp/epito-*` is 6.9G across 26
  sandboxes ... The steady state is 96%." 18 + 6.9 = 24.9 against a device at
  roughly 43. The residual is 18G, as large as the largest component named,
  and the sentence calls itself a measured composition.

So the rule this mode enforces is not about disks. **A composition claim must
publish its residual.** Enumerating the big items and stopping is how a list
that covers 58 per cent of a quantity gets published under the word "measured",
and the failure is silent because every individual figure in it is correct. The
threshold for failing is the residual reaching the largest named component,
because past that point the thing the composition does not name is the biggest
thing in it.

## What it does not do

It does not delete anything, it does not decide whose the gap is beyond naming
it as off-namespace, and it takes one reading at one instant. The volume on this
host oscillates by two gigabytes inside sixty seconds, so a single sample is a
sample and the `taken_at` field is in the JSON for that reason.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

GIB = 1073741824


def _run(cmd):
    """Return stdout, or None when the command is absent or fails."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def device_used(path):
    """Bytes used and available on the device backing `path`, from statvfs.

    statvfs rather than parsing `df` output: the numbers are the same ones df
    prints and there is no column layout to get wrong. `used` is total minus
    free rather than total minus available, so it matches df's USED column,
    which excludes the root-reserved blocks.
    """
    try:
        st = os.statvfs(path)
    except OSError as exc:
        return None, f"statvfs({path}): {exc}"
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    avail = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    return {"used": used, "avail": avail, "total": total}, None


def visible_bytes(path):
    """Bytes under `path` on this filesystem only, via `du -sx`.

    `-x` so a nested mount is not counted into its parent's subtree, which is
    the same confusion this tool exists to report. Unreadable entries are
    du's business: it skips them and exits nonzero, and a partial walk is
    still the right number to print beside a refusal note, so stderr is kept.
    """
    out = _run(["du", "-sx", "-B1", path])
    if out is None:
        # du exits nonzero on any unreadable entry, and on a shared host that
        # is the normal case rather than a failure, so retry tolerating it.
        try:
            res = subprocess.run(["du", "-sx", "-B1", path],
                                 capture_output=True, text=True, timeout=600)
        except (OSError, subprocess.SubprocessError) as exc:
            return None, f"du: {exc}"
        if not res.stdout.strip():
            return None, "du produced no total"
        field = res.stdout.split()[0]
        partial = bool(res.stderr.strip())
        try:
            return {"bytes": int(field), "partial": partial}, None
        except ValueError:
            return None, f"du total unparseable: {field!r}"
    return {"bytes": int(out.split()[0]), "partial": False}, None


def mount_shape(path):
    """Is `path` a bind mount of a subtree, and what is the shadowed source?

    `findmnt` prints the source as `DEVICE[/sub/path]` for a bind of a
    subdirectory and as a bare `DEVICE` for the device's own root. The bracket
    is the whole signal. When findmnt is absent the inode is a weaker second
    witness: a filesystem root is inode 2 on ext4, so anything else under a
    mount point means the visible tree is not that filesystem's root.
    """
    shape = {"source": None, "subtree": None, "is_subtree_bind": None,
             "inode": None, "source_reachable": None}
    try:
        shape["inode"] = os.stat(path).st_ino
    except OSError:
        pass
    out = _run(["findmnt", "-n", "-o", "SOURCE", "--target", path])
    if out is None:
        if shape["inode"] is not None:
            shape["is_subtree_bind"] = shape["inode"] != 2
            shape["basis"] = "inode only; findmnt absent"
        return shape
    source = out.strip().splitlines()[0].strip() if out.strip() else ""
    shape["source"] = source or None
    shape["basis"] = "findmnt"
    if "[" in source and source.endswith("]"):
        device, sub = source.split("[", 1)
        shape["source"] = device
        shape["subtree"] = sub[:-1]
        shape["is_subtree_bind"] = True
        # The bind source is shadowed by the mount that came from it, so it is
        # normally unreachable by its own path. Say which, rather than assume.
        shape["source_reachable"] = os.path.exists(shape["subtree"])
    else:
        shape["is_subtree_bind"] = False
    return shape


def deleted_open_bytes():
    """Bytes held by deleted-but-open files, the usual explanation for a gap.

    Ruled in or out rather than assumed: on this host it totalled 768 bytes
    against a 29 GiB gap. Unreadable `/proc/<pid>/fd` entries belong to other
    users' processes and are skipped, so this is a floor and is labelled one.
    """
    total = 0
    counted = 0
    skipped = 0
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        fd_dir = f"/proc/{pid}/fd"
        try:
            names = os.listdir(fd_dir)
        except OSError:
            skipped += 1
            continue
        for name in names:
            try:
                target = os.readlink(os.path.join(fd_dir, name))
            except OSError:
                continue
            if not target.endswith(" (deleted)"):
                continue
            try:
                total += os.stat(os.path.join(fd_dir, name)).st_size
                counted += 1
            except OSError:
                continue
    return {"bytes": total, "descriptors": counted,
            "pids_unreadable": skipped, "floor": True}


def headroom(path="/tmp"):
    """The three numbers and the verdict, as a dict."""
    taken_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dev, err = device_used(path)
    if dev is None:
        return {"measured": False, "reason": err, "path": path, "taken_at": taken_at}
    vis, verr = visible_bytes(path)
    if vis is None:
        return {"measured": False, "reason": verr, "path": path, "taken_at": taken_at}
    report = {
        "measured": True,
        "path": path,
        "taken_at": taken_at,
        "device_used_bytes": dev["used"],
        "device_avail_bytes": dev["avail"],
        "device_total_bytes": dev["total"],
        "device_pct_used": round(100.0 * dev["used"] / dev["total"], 1) if dev["total"] else None,
        "visible_bytes": vis["bytes"],
        "visible_walk_partial": vis["partial"],
        "gap_bytes": dev["used"] - vis["bytes"],
        "mount": mount_shape(path),
        "deleted_open": deleted_open_bytes(),
    }
    report["gap_share_of_used"] = (
        round(1.0 * report["gap_bytes"] / dev["used"], 3) if dev["used"] else None
    )
    return report


def compose(path, components):
    """A composition claim, with the residual it does not name.

    `components` is a list of (name, path). Each is walked with `du -sx` the
    same way the visible total is, so the residual is in the same units as the
    device figure it is subtracted from.
    """
    report = headroom(path)
    if not report.get("measured"):
        return report
    named = []
    for name, comp_path in components:
        measured, err = visible_bytes(comp_path)
        named.append({
            "name": name, "path": comp_path,
            "bytes": None if measured is None else measured["bytes"],
            "error": err,
        })
    total_named = sum(c["bytes"] or 0 for c in named)
    largest = max((c["bytes"] or 0 for c in named), default=0)
    residual = report["device_used_bytes"] - total_named
    report["composition"] = {
        "components": named,
        "named_bytes": total_named,
        "residual_bytes": residual,
        "largest_component_bytes": largest,
        "covers_share_of_used": (
            round(1.0 * total_named / report["device_used_bytes"], 3)
            if report["device_used_bytes"] else None
        ),
        "overcounted": residual < 0,
        "overlaps": _overlaps(named),
    }
    report["composition"]["residual_exceeds_largest"] = residual >= largest
    return report


def _overlaps(named):
    """Component pairs where one path contains the other, which is an overcount.

    This is the check only the path-taking form of the rule can make. A tool
    given `NAME=VALUE` sees two numbers and cannot know they count the same
    bytes; a tool given `NAME=PATH` is holding the evidence. `du -sx` of a
    parent already includes the child, so naming both adds the child twice,
    which inflates `named_bytes` and deflates the residual -- the only
    direction that turns a refusal into an `ok`.

    Identity is the degenerate case and is reported the same way: two names
    for one directory is a parent containing itself.
    """
    out = []
    for i, a in enumerate(named):
        for b in named[i + 1:]:
            if a["bytes"] is None or b["bytes"] is None:
                continue
            pa, pb = os.path.realpath(a["path"]), os.path.realpath(b["path"])
            if pa == pb:
                out.append({"outer": a["name"], "inner": b["name"], "identical": True})
            elif pb.startswith(pa.rstrip("/") + "/"):
                out.append({"outer": a["name"], "inner": b["name"], "identical": False})
            elif pa.startswith(pb.rstrip("/") + "/"):
                out.append({"outer": b["name"], "inner": a["name"], "identical": False})
    return out


def _g(n):
    """Scale the unit, because a figure that is ruled out must not read as absent.

    The deleted-open total is the reason. Printed as "0.0 GiB" beside a 29 GiB
    gap it reads as "unmeasured", which is the opposite of what measuring it
    was for: this tool rules that explanation in or out and has to show which.
    """
    if n < 1048576:
        return f"{n} B"
    if n < GIB:
        return f"{n / 1048576:.0f} MiB"
    return f"{n / GIB:.1f} GiB"


def _print_human(report):
    if not report.get("measured"):
        print(f"cannot measure: {report['reason']}", file=sys.stderr)
        return
    print(f"{report['path']} at {report['taken_at']}")
    print(f"  device used      {_g(report['device_used_bytes'])}"
          f"  ({report['device_pct_used']}% of {_g(report['device_total_bytes'])},"
          f" {report['device_avail_bytes'] / 1048576:.0f} MiB free)")
    partial = "  (walk incomplete, this is a floor)" if report["visible_walk_partial"] else ""
    print(f"  visible from here {_g(report['visible_bytes'])}{partial}")
    print(f"  gap              {_g(report['gap_bytes'])}"
          f"  ({report['gap_share_of_used']:.0%} of what is used)")

    mount = report["mount"]
    if mount.get("is_subtree_bind"):
        print()
        if mount.get("subtree"):
            print(f"  {report['path']} is a bind mount of {mount['source']}[{mount['subtree']}],")
            print("  not the device's root, so the gap is outside this mount namespace.")
            if mount.get("source_reachable") is False:
                print("  The bind source is shadowed by the mount that came from it and is")
                print("  not reachable by its own path from here.")
        else:
            print(f"  {report['path']} has inode {mount['inode']} rather than 2, so the visible")
            print("  tree is not the filesystem's root and the gap is off-namespace.")
        print("  The gap belongs to whoever owns the host's units. It is not a seat's")
        print("  content and no seat-side reclaimer can reach it.")
    elif mount.get("is_subtree_bind") is False:
        print()
        print(f"  {report['path']} is the root of {mount.get('source')}, so the gap is")
        print("  unexplained by the mount shape. Read it before attributing it.")

    held = report["deleted_open"]
    if held["bytes"] > 0:
        print(f"\n  deleted-but-open  {_g(held['bytes'])} across {held['descriptors']}"
              f" descriptors (floor; {held['pids_unreadable']} pids unreadable)")

    comp = report.get("composition")
    if comp:
        print("\ncomposition")
        for c in comp["components"]:
            if c["bytes"] is None:
                print(f"  {c['name']:<16} unreadable: {c['error']}")
            else:
                print(f"  {c['name']:<16}{_g(c['bytes']):>10}  {c['path']}")
        print(f"  {'named':<16}{_g(comp['named_bytes']):>10}"
              f"  ({comp['covers_share_of_used']:.0%} of what is used)")
        if comp["overcounted"]:
            print(f"  {'OVERCOUNT':<16}{_g(-comp['residual_bytes']):>10}"
                  "  the named parts exceed the total, so two of them count the same bytes")
        else:
            print(f"  {'RESIDUAL':<16}{_g(comp['residual_bytes']):>10}"
                  "  not named by anything above")
        for ov in comp["overlaps"]:
            how = "is the same directory as" if ov["identical"] else "contains"
            print(f"  OVERLAP          {ov['outer']} {how} {ov['inner']},"
                  " so its bytes are named twice")
        if comp["overcounted"]:
            print("\n  The parts sum above the total, which no residual can absorb, so this")
            print("  is not an unnamed remainder: two components count one thing. Printed")
            print("  as OVERCOUNT rather than as a negative residual, taken from")
            print("  alexandria/engineer's tools/sentinel.py, because the two read nothing")
            print("  alike and a minus sign invites a reader to shrug at it.")
        elif comp["residual_exceeds_largest"]:
            print("\n  The residual is at least as large as the largest component named,")
            print("  so the biggest thing in this composition is the thing it does not")
            print("  name. Publish the residual or do not call it a composition.")


def _self_check():
    return [
        "device_used reads statvfs, so no df column layout is parsed",
        "visible_bytes uses du -sx, so a nested mount is not counted into its parent",
        "a du walk that skipped unreadable entries is reported as partial, not as a total",
        "mount_shape reads findmnt SOURCE and treats the [subtree] bracket as the signal",
        "with findmnt absent, an inode other than 2 is the weaker second witness",
        "deleted-but-open bytes are ruled in or out rather than assumed, and labelled a floor",
        "the gap is named as off-namespace and never attributed to a seat",
        "--compose fails when the residual reaches the largest component named",
        "an overcount prints OVERCOUNT and fails, rather than a negative residual passing",
        "a component path inside another is named as an overlap and fails, because du counts it twice",
        "taken_at is always printed, because this volume swings 2 GiB inside a minute",
        "nothing here deletes, moves or opens for write",
    ]


def main():
    parser = argparse.ArgumentParser(
        description="The device figure, the visible figure, and the gap between them.")
    parser.add_argument("--path", default="/tmp",
                        help="the mount point to ask about (default /tmp)")
    parser.add_argument("--compose", nargs="+", metavar="NAME=PATH", default=[],
                        help="components of a composition claim; the residual is printed")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-check", action="store_true", help="print the properties")
    args = parser.parse_args()

    if args.self_check:
        for line in _self_check():
            print(f"- {line}")
        return 0

    components = []
    for spec in args.compose:
        if "=" not in spec:
            print(f"--compose takes NAME=PATH, got {spec!r}", file=sys.stderr)
            return 2
        name, _, comp_path = spec.partition("=")
        components.append((name, comp_path))

    report = compose(args.path, components) if components else headroom(args.path)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)

    if not report.get("measured"):
        return 2
    comp = report.get("composition")
    if comp and (comp["residual_exceeds_largest"] or comp["overcounted"]
                 or comp["overlaps"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
