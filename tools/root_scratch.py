#!/usr/bin/env python3
"""Does this branch add a file to the checkout root that nothing imports?

    python3 tools/root_scratch.py                 # against origin/main
    python3 tools/root_scratch.py --base <ref>
    python3 tools/root_scratch.py --list          # what the root holds on the base

Exit 0 and print nothing when the root is unchanged, so this can sit in front of
an `&&`.

## Why this is a ratchet and not a list

`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`
has six instances as of 2026-11-02, every one of them a run writing scratch into
the repository root and reaching the index through a `git add -A`. The remedy
each time was another line in `.gitignore`: `/.inbox.json`, `/.prbody-*.md`,
`/.p*.txt`, `/.scratchdir`, `/.scratch*`. The fourth instance wrote down in
advance why that cannot work -- "an ignore rule written from the instances it has
seen cannot stop the next name, and the next name is the only thing it needs to
stop" -- and the fifth and sixth instances then arrived under names none of the
five lines matched (`.scratch_mech.py`, then `.dfseries.txt`).

So this does not enumerate scratch. It enumerates the root, which is 23 entries
and changes a few times a year, and reports anything a branch adds to it. A run
that genuinely means to add a root file says so with `--allow`, which is one
flag against five lines of ignore rules that each stop exactly one name.

The ignore rules are still worth having, because they stop the stray before it
reaches the index and this only catches it afterwards. Two of the six instances
are on `main` today -- `.prbody-exo.md` and `site-server.log` -- which is the
case for a gate rather than a list: an ignore rule added after a file is tracked
does nothing to the file, and nothing was ever looking at the root.
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "origin/main"


def root_entries(ref, root=ROOT):
    """The names at the top level of `ref`, or None when the ref is unreadable.

    None rather than an empty set, because a shallow clone that cannot name
    `origin/main` would otherwise report every root file as newly added. That
    distinction is `INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`
    in one return value.
    """
    done = subprocess.run(["git", "ls-tree", "--name-only", ref],
                          cwd=root, capture_output=True, text=True)
    if done.returncode != 0:
        return None
    return {line for line in done.stdout.split("\n") if line}


def added(base=BASE, root=ROOT, allow=()):
    """(findings, note). Findings are the root names this branch adds."""
    before = root_entries(base, root)
    if before is None:
        return [], f"{base} cannot be named here, so the root was not compared"
    now = root_entries("HEAD", root)
    if now is None:
        return [], "HEAD cannot be read, so the root was not compared"
    new = sorted(now - before - set(allow))
    return [f"{name}: added to the checkout root on this branch and not on "
            f"{base}. If it is scratch, it belongs under a directory outside "
            f"the checkout; if it is meant to be there, pass --allow {name}"
            for name in new], ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--allow", action="append", default=[],
                    help="a root name this branch adds on purpose")
    ap.add_argument("--list", action="store_true",
                    help="print the base's root entries and exit 0")
    args = ap.parse_args(argv)
    if args.list:
        entries = root_entries(args.base)
        if entries is None:
            print(f"{args.base} cannot be named here", file=sys.stderr)
            return 0
        for name in sorted(entries):
            print(name)
        return 0
    findings, note = added(args.base, allow=args.allow)
    if note:
        print(f"note: {note}", file=sys.stderr)
    for finding in findings:
        print(f"BLOCKING: {finding}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
