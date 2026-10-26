#!/usr/bin/env python3
"""Which open pull requests actually merge, in which order, and what blocks the rest.

    python3 tools/merge_order.py                 # the open queue against origin/main
    python3 tools/merge_order.py --json          # the same numbers, for a standup
    python3 tools/merge_order.py --base main     # a different trunk

Every per-pull-request check in this repository asks one question: is this
branch mergeable against `main`. Every branch in a queue can answer yes to that
and still be mutually exclusive with its neighbours, because `mergeable` is
asked of one branch at a time and exclusivity is a property of a pair. The
owner merges by hand, one at a time, and the order she picks decides how much
of the day's work lands. Nothing in this repository told her the order.

`docs/standards/lessons.md` L-A48 names the shape and the instrument in the
same breath: "Measure it with the real merge, not with `mergeable`." Its
portfolio measurement of 2026-10-18 found 84 open pull requests of which 33
merged in sequence and 51 could not, and 44 of those 51 conflicted in nothing
but Markdown registers under `docs/`. The instrument it names,
`tools/merge-order.sh`, lives in another repository and has never existed in
this one, so the one number alexandria has ever had about its own queue is the
one that lesson's table carries for it.

Two passes, both with `git merge-tree`, which performs the real merge in the
object database and writes no ref, moves no HEAD and touches no working tree.

- **Sequential, oldest first.** Merge each pull request onto the accumulated
  result, skipping the ones that conflict and carrying on. This is the owner's
  morning in miniature: how many of today's open branches can actually land,
  and which ones need a rebase first.
- **Pairwise.** For every pair, merge their two heads. A pair that conflicts is
  a pair whose merge order cannot be chosen freely, and the tally of the files
  those conflicts land in names the anchor. One name at the top of that table
  is the whole finding.

Read-only in the flags, per L-E12. The heads it needs are fetched into a
`refs/merge-order/` namespace that is deleted on the way out, never with
`--depth`, and nothing here checks out, resets, or fetches into the caller's
branch. `tests/test_merge_order.py` holds that promise: a complete checkout is
still complete, on the same commit, with the same refs, after a run.

Exit codes, following `tools/drift_watch.py` so this can sit in front of an
`&&`: 0 when every open pull request merges in sequence, 1 when one cannot, and
2 when the queue could not be measured at all. A run that cannot reach the
pull requests says so and exits 2 rather than printing an empty clean queue,
because a gate that saw nothing must not read as a quiet pass (L-A21).
"""

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Where fetched pull-request heads are parked for the length of one run. Named
#: rather than anonymous so the cleanup can be exact, and under `refs/` rather
#: than in `FETCH_HEAD` so that two heads can be held at once without the
#: second fetch overwriting the first.
REF_NS = "refs/merge-order"

CLEAN, BLOCKED, UNMEASURED = "clean", "blocked", "unmeasured"

EXIT = {CLEAN: 0, BLOCKED: 1, UNMEASURED: 2}

#: A path whose conflicts are prose rather than product. L-A48's headline
#: finding was that 100 of 104 mutually exclusive pairs were exclusive over
#: nothing else, so the split is worth reporting rather than inferring.
PROSE_PREFIXES = ("docs/", "prompts/", "skills/")
PROSE_SUFFIXES = (".md", ".markdown")


def git(*args, repo=ROOT, check=True):
    """Run one git command in `repo` and return its stdout.

    `check=False` is for the commands whose non-zero exit is an answer rather
    than a failure, which is every `merge-tree`.
    """
    done = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True)
    if check and done.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({done.returncode}): {done.stderr.strip()}")
    return done


def is_prose(path: str) -> bool:
    """Is this path prose that seats append to, rather than code that runs?"""
    return path.startswith(PROSE_PREFIXES) and path.endswith(PROSE_SUFFIXES)


def open_prs(repo=ROOT) -> list[dict]:
    """The open pull requests, oldest first, as the queue the owner sees.

    `headRefOid` rather than `headRefName`, because the name is a pointer that
    can move between this call and the fetch, and the oid is the same object in
    every clone (the rule L-A47 states for `gh pr create`, applied to reading).
    """
    done = subprocess.run(
        ["gh", "pr", "list", "--state", "open", "--limit", "100",
         "--json", "number,title,headRefName,headRefOid,createdAt,isDraft"],
        capture_output=True, text=True, cwd=str(repo))
    if done.returncode != 0:
        raise RuntimeError(f"gh pr list failed: {done.stderr.strip()}")
    prs = json.loads(done.stdout or "[]")
    return sorted(prs, key=lambda p: p["createdAt"])


def fetch_heads(prs: list[dict], repo=ROOT) -> list[dict]:
    """Bring every head object into this repository, and drop the ones that will not come.

    One fetch, every refspec, so a queue of twenty costs one network round trip.
    A pull request whose head has been garbage collected on the remote is
    dropped from the measurement and named, rather than failing the run.

    The retry is the part that matters. `git fetch` with many refspecs fails as
    a unit, so one dead head takes every live head down with it, and the
    measurement that comes back is "nothing to merge" rather than "I could not
    look" — the quiet pass L-A21 exists to forbid. So the batch is the fast path
    and the per-head loop is the truth, and the loop runs whenever the batch
    does not bring back everything it asked for.
    """
    if not prs:
        return []
    spec = lambda pr: f"{pr['headRefOid']}:{REF_NS}/{pr['number']}"
    git("fetch", "--no-tags", "origin", *[spec(p) for p in prs], repo=repo, check=False)
    if len(_present(prs, repo)) < len(prs):
        for pr in prs:
            git("fetch", "--no-tags", "origin", spec(pr), repo=repo, check=False)
    return _present(prs, repo)


def _present(prs: list[dict], repo=ROOT) -> list[dict]:
    """The subset whose head is now an object in this repository."""
    return [pr for pr in prs
            if git("rev-parse", "--verify", "--quiet", f"{REF_NS}/{pr['number']}",
                   repo=repo, check=False).returncode == 0]


def drop_refs(repo=ROOT) -> None:
    """Remove every ref this run created. Called on the way out of every path."""
    listed = git("for-each-ref", "--format=%(refname)", REF_NS, repo=repo, check=False)
    for ref in listed.stdout.split():
        git("update-ref", "-d", ref, repo=repo, check=False)


def merge(ours: str, theirs: str, repo=ROOT) -> tuple[str | None, list[str]]:
    """The real merge of two commits. Returns (merged commit, conflicted paths).

    `git merge-tree --write-tree` finds the merge base itself and writes the
    result into the object database without a ref, a HEAD or a worktree. On
    success the tree is turned into a commit with both parents, so the next
    merge in a sequential pass can stand on it: that commit is reachable from
    nothing and is collected like any other loose object.
    """
    done = git("merge-tree", "--write-tree", "--name-only", ours, theirs,
               repo=repo, check=False)
    head, _, rest = done.stdout.partition("\n")
    tree = head.strip()
    if done.returncode == 0:
        commit = git("commit-tree", tree, "-p", ours, "-p", theirs,
                     "-m", "merge-order measurement", repo=repo).stdout.strip()
        return commit, []
    if not tree:
        # merge-tree refuses outright only when there is no merge base at all.
        return None, ["<no merge base>"]
    paths = [line for line in rest.split("\n\n")[0].split("\n") if line.strip()]
    return None, paths


def measure(prs: list[dict], base: str, repo=ROOT) -> dict:
    """Both passes over one queue. Pure measurement: no ref, no checkout, no network."""
    base_commit = git("rev-parse", base, repo=repo).stdout.strip()

    sequence, accumulated = [], base_commit
    for pr in prs:
        merged, paths = merge(accumulated, f"{REF_NS}/{pr['number']}", repo=repo)
        if merged:
            accumulated = merged
            sequence.append({"number": pr["number"], "merges": True, "conflicts": []})
        else:
            sequence.append({"number": pr["number"], "merges": False, "conflicts": paths})

    pairs, anchors = [], collections.Counter()
    for i, left in enumerate(prs):
        for right in prs[i + 1:]:
            _, paths = merge(f"{REF_NS}/{left['number']}",
                             f"{REF_NS}/{right['number']}", repo=repo)
            if paths:
                pairs.append({"left": left["number"], "right": right["number"],
                              "conflicts": paths})
                anchors.update(paths)

    prose_only = [p for p in pairs if p["conflicts"] and all(is_prose(f) for f in p["conflicts"])]
    return {
        "base": base,
        "base_commit": base_commit,
        "measured": len(prs),
        "sequence": sequence,
        "land": [s["number"] for s in sequence if s["merges"]],
        "blocked": [s["number"] for s in sequence if not s["merges"]],
        "pairs": pairs,
        "prose_only_pairs": len(prose_only),
        "anchors": anchors.most_common(),
    }


def verdict(report: dict) -> str:
    if report.get("measured") is None:
        return UNMEASURED
    return BLOCKED if report["blocked"] else CLEAN


def render(report: dict, titles: dict[int, str]) -> list[str]:
    """The report a reader can act on, which is the merge order and the anchor."""
    out = []
    n, landed = report["measured"], len(report["land"])
    if n == 0:
        out.append(f"merge order: no open pull requests against {report['base']}")
        return out

    out.append(f"merge order against {report['base']} ({report['base_commit'][:7]}): "
               f"{landed} of {n} merge in sequence, oldest first")
    for step in report["sequence"]:
        mark = "merges" if step["merges"] else "BLOCKED"
        title = titles.get(step["number"], "")
        out.append(f"  {mark:>7}  #{step['number']:<5} {title[:58]}")
        if not step["merges"]:
            for path in step["conflicts"][:6]:
                out.append(f"           conflicts in {path}")

    if n > 1:
        out.append("")
        out.append(f"mutually exclusive pairs: {len(report['pairs'])} of "
                   f"{n * (n - 1) // 2}, {report['prose_only_pairs']} of them "
                   f"over nothing but prose")
        if report["anchors"]:
            out.append("top anchors, by the pull requests they block:")
            for path, count in report["anchors"][:5]:
                out.append(f"  {count:>3}  {path}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="origin/main",
                    help="the trunk the queue is merging into (default origin/main)")
    ap.add_argument("--json", action="store_true", help="the report as data")
    args = ap.parse_args(argv)

    try:
        prs = open_prs()
    except (RuntimeError, json.JSONDecodeError) as exc:
        report = {"state": UNMEASURED, "measured": None, "reason": str(exc)}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"merge order: the open queue could not be read, so nothing "
                  f"here is a verdict on it ({exc})")
        return EXIT[UNMEASURED]

    titles = {p["number"]: p["title"] for p in prs}
    try:
        present = fetch_heads(prs)
        missing = [p["number"] for p in prs if p not in present]
        report = measure(present, args.base)
    finally:
        drop_refs()

    report["unreachable_heads"] = missing
    report["state"] = verdict(report)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for line in render(report, titles):
            print(line)
        if missing:
            print(f"heads unreachable on the remote, left out of the "
                  f"measurement: {', '.join(f'#{n}' for n in missing)}")
    return EXIT[report["state"]]


if __name__ == "__main__":
    sys.exit(main())
