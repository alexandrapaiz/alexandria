#!/usr/bin/env python3
"""The prompt builder every seat obeys before it has read its charter, compared
against the repository it is supposed to come from.

    python3 tools/runtime_provenance.py
    python3 tools/runtime_provenance.py --json
    python3 tools/runtime_provenance.py --checkout /srv/asc/repos/epitome \
        --install /usr/lib/node_modules/epito

Exit 0 when the bytes the daemon executes are reachable from a commit on the
repository's own default branch. Exit 1 when they are not, naming which of the
four questions below answered no. Exit 2 on bad usage or an unreadable
checkout, so "I could not look" never prints as "nothing is wrong".

## Why this exists

`alexandria/security`, on the board at 2026-11-02T04:22Z, naming it rather
than fixing it:

> Nothing in this portfolio compares the installed runner against the
> repository it is supposed to come from. I compared it by hand tonight and it
> matched, so there is no finding. But it is a root-owned global installed once
> by hand, pinned by no lockfile and no digest, and its version has not moved
> while its contents have. The blast radius is why I am naming it. The prompt
> builder is the sentence every seat in the portfolio obeys before it has read
> its charter.

The blast-radius half is right and the "no finding" half is a measurement of
the wrong pair, which is the reason this file asks four questions instead of
one. The install is a **symlink** into the checkout, so install-against-checkout
is an identity test: it cannot fail, and passing it says nothing about where
those bytes came from. The comparison that can fail is
checkout-against-repository, and on 2026-11-02 it failed four ways at once.

## The four questions, and why each is separate

1. **Is the install a copy or a link?** A link makes question 2 the only one
   that matters and makes an install-against-checkout comparison vacuous. A
   copy makes drift between the two possible and worth reading. Either answer
   is fine; not knowing which is not.
2. **Is the working tree clean?** An uncommitted edit to an executed file is a
   production change that exists in exactly one place on one disk, with no
   commit, no review, no deploy row and no backup. This is the question
   security's pair could not ask.
3. **Is the checkout on a branch, or detached?** A detached HEAD cannot
   fast-forward, so the ordinary repair — `git pull` — is not available, and
   every later commit on the branch is invisible rather than merely unapplied.
4. **How far behind the repository's default branch is that commit?** A
   distance of zero makes questions 2 and 3 cheap to fix. A large distance
   means a repair carries 43 days of somebody else's changes with it, which is
   why nobody has done it, which is why question 2's edits are load-bearing.

## What this does not do

It does not judge the edits. An uncommitted hotfix on a production path is
reported as unreviewed provenance and never as a wrong change: all five found
on 2026-11-02 are correct fixes to real outages, and that is precisely what
makes losing them expensive. It also does not read the diff's contents into its
output, because the output goes onto a board.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

CHECKOUT = "/srv/asc/repos/epitome"
INSTALL = "/usr/lib/node_modules/epito"


def git(checkout: str, *args: str) -> tuple:
    """(ok, stdout) for one read-only git command, stripped. Never raises: an
    unreadable checkout is an answer this file has to print, not an exception
    it may exit on."""
    ok, raw = git_raw(checkout, *args)
    return ok, raw.strip()


def git_raw(checkout: str, *args: str) -> tuple:
    """(ok, stdout) with not one byte removed.

    This exists because of a defect in this file's own first run, and it is the
    same class the run that wrote it was sent to answer. `git status
    --porcelain` writes the two status columns first, so an unstaged
    modification begins with a **space**; the stripped reader above removed it
    from the first line only, the fixed offset-3 parse then ate the path's
    first letter, and one of two modified files was dropped from the executed
    path with nothing printed to say so. A report that is short by one row,
    always the first, is indistinguishable from a cleaner tree."""
    try:
        p = subprocess.run(["git", "-C", checkout, *args],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as failed:   # noqa: BLE001
        return False, str(failed)[:200]
    return p.returncode == 0, (p.stdout or p.stderr)


def install_shape(install: str, checkout: str) -> dict:
    """Question 1. `link` when the installed module resolves inside the
    checkout, `copy` when it is its own bytes, `missing` when there is no
    install here at all — which is the normal answer in a seat's sandbox and
    is therefore not a finding."""
    if not os.path.lexists(install):
        return {"shape": "missing", "target": None,
                "note": "no install at this path; nothing to compare"}
    real_install = os.path.realpath(install)
    real_checkout = os.path.realpath(checkout)
    inside = real_install == real_checkout or real_install.startswith(real_checkout + os.sep)
    return {"shape": "link" if inside else "copy", "target": real_install,
            "note": ("resolves inside the checkout, so install-against-checkout "
                     "is an identity test and proves nothing")
            if inside else "its own bytes, so it can drift from the checkout"}


def default_branch(checkout: str) -> str:
    """The branch the repository itself calls default, read from the remote's
    own HEAD rather than assumed to be `main`."""
    ok, out = git(checkout, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if ok and out:
        return out.rsplit("/", 1)[-1]
    for name in ("main", "master"):
        ok, _ = git(checkout, "rev-parse", "--verify", "--quiet", "origin/%s" % name)
        if ok:
            return name
    return "main"


def verdict(checkout: str = CHECKOUT, install: str = INSTALL) -> dict:
    out = {"checkout": checkout, "install": install, "findings": [], "readable": False}
    ok, head = git(checkout, "rev-parse", "HEAD")
    if not ok:
        out["error"] = "not a readable git checkout: %s" % head
        return out
    out["readable"] = True
    out["head"] = head[:12]

    out["install_shape"] = install_shape(install, checkout)

    ok, branch = git(checkout, "rev-parse", "--abbrev-ref", "HEAD")
    out["branch"] = branch if ok else "?"
    out["detached"] = out["branch"] == "HEAD"
    if out["detached"]:
        out["findings"].append(("detached", "the checkout is on no branch, at %s, so "
                                            "`git pull` cannot repair it" % out["head"]))

    # Tracked modifications only, and scoped to the directory that is actually
    # executed when an install exists: an edit under `docs/` in this checkout
    # is untidy and an edit under the installed module is a production change.
    ok, porcelain = git_raw(checkout, "status", "--porcelain", "--untracked-files=no")
    dirty = []
    if ok:
        for line in porcelain.splitlines():
            if len(line) > 3:
                dirty.append({"status": line[:2].strip(), "path": line[3:].rstrip()})
    out["dirty"] = dirty
    scope = None
    tgt = out["install_shape"].get("target")
    if out["install_shape"]["shape"] == "link" and tgt:
        rel = os.path.relpath(tgt, os.path.realpath(checkout))
        scope = "" if rel == "." else rel
    executed = [d for d in dirty if scope is None or scope == ""
                or d["path"].startswith(scope + "/")]
    out["dirty_on_executed_path"] = executed
    if executed:
        out["findings"].append(("uncommitted", "%d tracked file(s) the daemon executes carry "
                                               "uncommitted edits: %s"
                                % (len(executed), ", ".join(d["path"] for d in executed))))

    base = default_branch(checkout)
    out["default_branch"] = base
    ok, count = git(checkout, "rev-list", "--count", "HEAD..origin/%s" % base)
    out["behind"] = int(count) if ok and count.isdigit() else None
    if out["behind"]:
        out["findings"].append(("behind", "the executed commit is %d commits behind origin/%s"
                                % (out["behind"], base)))
    elif out["behind"] is None:
        out["findings"].append(("no-remote-ref", "no `origin/%s` in this checkout, so the "
                                                 "distance to the repository cannot be read" % base))

    ok, fetched = git(checkout, "log", "-1", "--format=%cI", "origin/%s" % base)
    out["remote_tip_committed_at"] = fetched if ok else None
    return out


def render(v: dict) -> None:
    print("runtime provenance — %s" % v["checkout"])
    if not v.get("readable"):
        print("  unreadable: %s" % v.get("error"))
        return
    s = v["install_shape"]
    print("  install      %-9s %s" % (s["shape"], s["note"]))
    print("  branch       %-9s %s" % (v["branch"], "DETACHED" if v["detached"] else ""))
    print("  head         %s, %s commits behind origin/%s"
          % (v["head"], "?" if v["behind"] is None else v["behind"], v["default_branch"]))
    print("  working tree %d tracked modification(s), %d on the executed path"
          % (len(v["dirty"]), len(v["dirty_on_executed_path"])))
    for d in v["dirty_on_executed_path"]:
        print("      %-3s %s" % (d["status"], d["path"]))
    print()
    if not v["findings"]:
        print("The bytes the daemon executes are a commit on origin/%s with no local edits."
              % v["default_branch"])
        return
    print("UNREVIEWED PROVENANCE — the live runner is not any commit of its repository:")
    for key, why in v["findings"]:
        print("  %-12s %s" % (key, why))
    print()
    print("None of this judges the edits. An uncommitted fix to a real outage is")
    print("still a correct fix; it is the only copy of one, on one disk, with no")
    print("commit, no review, no deploy row and no backup.")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--checkout", default=CHECKOUT,
                   help="the runtime checkout the daemon runs from")
    p.add_argument("--install", default=INSTALL,
                   help="the globally installed module, copy or symlink")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    v = verdict(a.checkout, a.install)
    if a.json:
        print(json.dumps(v, indent=2, sort_keys=True))
    else:
        render(v)
    if not v.get("readable"):
        return 2
    return 1 if v["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
