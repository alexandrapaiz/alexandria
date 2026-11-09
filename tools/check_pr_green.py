#!/usr/bin/env python3
"""Build the real three-way merge of a branch into the trunk and run the suites against it.

    python3 tools/check_pr_green.py                  # this branch's HEAD against origin/main
    python3 tools/check_pr_green.py 765              # one pull request by number
    python3 tools/check_pr_green.py --branch some/br # one branch by name, tracking ref or not
    python3 tools/check_pr_green.py --merge-only     # the conflict question alone, in seconds
    python3 tools/check_pr_green.py --suite 'python3 -m pytest tests/test_x.py -q'  # one file
    python3 tools/check_pr_green.py --json           # the same verdict as data

`docs/standards/lessons.md` L-P8 tells a merger that evidence it can re-perform
beats evidence it must believe, and it names the form: the command and its exit
code, not the adjective. The command it names is
`python3 tools/check-pr-green.py <pr>`, which "builds the real three-way merge
and runs this repository's own suites against it, which is better evidence than
a forge check on a branch tip that the merge will not ship." L-A66 is the same
rule from the held seat's side: a seat whose work is held supplies the evidence
the gate asks for rather than re-arguing the reading in its own favour.

That instrument lives at HQ and has never existed here, so the rule has been
live in this repository with its instrument absent, and the strongest thing any
seat could post was a local invocation it composed itself. This is the
instrument. The handoff that asked for it (alexandria/research, 2026-11-02)
checked for a local equivalent first, and the two near misses are real near
misses: `tools/merge_order.py` answers which pull requests merge in which order
and `tools/ci_coverage.py` answers which test files a workflow runs. Neither
builds the merge and runs anything against it.

Why the merge rather than the branch tip. A forge check runs on the head
commit, and the head commit is not what lands. Worse here than in general:
`checks.yml` is path-triggered over a pinned list, and `tools/ci_coverage.py`
reports that 14 of 84 test files run in any workflow at all. So for 70 of this
repository's test files there is no forge check to prefer, and a branch that
reverted the files that put it inside a path filter cannot follow a red with a
green no matter what it does. Against the merge, every one of the 84 runs.

What this does not do. It does not merge, push, check out, reset, or move the
caller's HEAD. The merge is built with `git merge-tree --write-tree`, which
writes an unreferenced tree into the object database, and it is read in a linked
worktree that is removed on the way out. The one thing it writes is loose
objects reachable from no ref, which git collects. L-E12 says a measurement may
only ask questions, and `tests/test_check_pr_green.py` holds that promise: the
caller's branch, HEAD, refs and working tree are the same after a run.

**One honest limit on that, measured on this tool's own first day.** The cleanup
is a `finally`, so it survives an exception and a failing suite, and it does not
survive the process being killed. A run stopped with a signal leaves one
worktree of roughly 430 MB on the shared volume and one registration in
`.git/worktrees`, and the manual cleanup is `git worktree prune` plus removing
the directory. This matters more than it looks: six directories under a sibling
instrument's prefix were holding 2.6 GB on this host while this was written, and
the first reading was almost reported as a leak before a second reading twenty
minutes later showed one directory at 400 MB. Live concurrent runs and killed
runs look identical from outside, so the number worth quoting about a tool like
this is its peak concurrent footprint rather than a leak count.

Exit codes, following `tools/merge_order.py` so this can sit in front of an
`&&`, with one addition:

- **0 green.** The real merge is clean and the suites pass against it.
- **0 merge-clean.** `--merge-only`, so the merge question is answered yes and
  the suites were never run. A separate verdict rather than `green` with a
  footnote, because the first live run of this tool printed "the suites pass
  against it" under `--merge-only` and that is the exact class of defect this
  seat spent two runs filing against other people's checks.
- **1 red.** The merge is clean and the suites fail. The failure is in what
  would land, which is the answer the merger wanted.
- **2 unmeasured.** It could not look: a shallow clone, no merge base, a head
  the remote will not serve, a suite run that outran its timeout. A gate that
  saw nothing must not read as a quiet pass (L-A21), so this is never 0.
- **3 conflict.** The real merge conflicts, so there is nothing to run the
  suites against. Distinct from 1 on purpose: "rebase your branch" and "fix
  your tests" are different next steps, and a merger should not have to parse
  prose to tell them apart.
"""

import argparse
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "tools"))

# The real merge has one implementation in this repository and this is not a
# second one. `merge_order.merge` is `git merge-tree --write-tree` plus
# `commit-tree`, already tested, already read-only, and already the thing L-A48
# meant by "measure it with the real merge, not with `mergeable`".
from merge_order import git, merge  # noqa: E402

GREEN, RED, UNMEASURED, CONFLICT = "green", "red", "unmeasured", "conflict"

#: The merge is clean and nobody asked for the suites. Exits 0 like `GREEN`,
#: because the question `--merge-only` asks was answered yes, and says a
#: different sentence, because the question `GREEN` answers was not asked.
MERGE_CLEAN = "merge-clean"

EXIT = {GREEN: 0, MERGE_CLEAN: 0, RED: 1, UNMEASURED: 2, CONFLICT: 3}

#: Where this run parks a fetched head, for the length of one run. Its own
#: namespace rather than `merge_order`'s, because that tool deletes every ref
#: under its namespace on the way out and two measurements in one clone must not
#: be able to delete each other's working state.
REF_NS = "refs/check-pr-green"

#: The suite command. `tests/` explicitly rather than bare `pytest`, because
#: `tests/conftest.py` installs the Modal stub the whole suite needs and a
#: rootdir-wide collection picks up `skills/` fixtures that are not tests.
DEFAULT_SUITE = ["python3", "-m", "pytest", "tests/", "-q"]

#: How long the suites may take. Measured rather than guessed: the full suite is
#: 2,586 tests and takes over ten minutes on a seat host, most of it in
#: collection, so a one-minute default would have reported `unmeasured` for
#: every honest run. A run that outruns this is `unmeasured`, never `red`,
#: because "slow" and "broken" are different findings.
DEFAULT_TIMEOUT = 2400

#: How many lines of the suite's own output to carry into the report. Enough to
#: hold pytest's failure summary, which is what a merger reads.
TAIL_LINES = 40

#: What a full shared volume says, in the words the kernel and git use for it.
#: This matters here more than in most tools: the merged worktree is a second
#: checkout of the whole repository, which on this repository is roughly 430 MB,
#: and the host's measured free space swings between 4 MB and 3.6 GB on a
#: sixty-second period (ExO measurement, 2026-11-02, 26 samples). So a run of
#: this tool can be the write that fills the disk.
#:
#: A pre-flight `df` is not the remedy and this does not do one. That reading
#: expires before it can be used, and it expires in the comfortable direction.
#: The only instrument that cannot go stale is the write's own exit status at
#: the write, so this classifies the failure after it happens and reports it as
#: `unmeasured` with the disk named, rather than letting a full volume reach a
#: merger as a red suite or an inscrutable checkout error.
ENOSPC_MARKERS = ("no space left on device", "disk quota exceeded",
                  "write error", "enospc")


def shallow_state(repo=ROOT) -> bool | None:
    """True shallow, False complete, None when git could not answer.

    Three-valued on purpose, the way `delivery_health._shallow_state` is. Every
    comparison below this line is a comparison of two branches, and the charter
    says in bold that on a shallow clone every one of them lies: `--depth 1`
    implies `--single-branch`, the trunk is grafted with no parents, and a
    three-way merge between two close branches reads as unrelated histories. A
    git that cannot answer is not evidence that the history is here.
    """
    done = git("rev-parse", "--is-shallow-repository", repo=repo, check=False)
    if done.returncode != 0:
        return None
    return done.stdout.strip() == "true"


def refspec_is_wide(repo=ROOT) -> bool:
    """Can this clone name a remote branch other than the trunk.

    The other half of the same trap, and the half the remedy kept missing:
    `--unshallow` deepens history without widening the fetch refspec, so a
    clone can hold every commit and still be unable to resolve
    `origin/<any branch but main>`. Three runs of this company have paid for
    that (INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again).
    """
    done = git("config", "--get-all", "remote.origin.fetch", repo=repo, check=False)
    return any("refs/heads/*" in line for line in done.stdout.splitlines())


def preflight(repo=ROOT) -> str | None:
    """The reason this clone cannot answer the question, or None."""
    state = shallow_state(repo)
    if state is not False:
        was = "is shallow" if state else "could not say whether it is shallow"
        return (f"this clone {was}, so every branch comparison below would lie. "
                "Run: git config --add remote.origin.fetch "
                "'+refs/heads/*:refs/remotes/origin/*' && git fetch --unshallow")
    if not refspec_is_wide(repo):
        return ("this clone's fetch refspec names only the trunk, so no other "
                "branch can be resolved by name. Run: git config --add "
                "remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*' "
                "&& git fetch")
    return None


def pr_target(number: int, repo=ROOT) -> dict:
    """What a pull request number resolves to, straight from the forge.

    `headRefOid` as well as the name, because the name is a pointer that can
    move between this call and the fetch and the oid is the same object in every
    clone. `baseRefName` too: a pull request that targets something other than
    the trunk must be measured against what it targets, not against what this
    tool's default assumes.
    """
    done = subprocess.run(
        ["gh", "pr", "view", str(number), "--json",
         "number,title,headRefName,headRefOid,baseRefName,state,isDraft"],
        capture_output=True, text=True, cwd=str(repo))
    if done.returncode != 0:
        raise RuntimeError(f"gh pr view {number} failed: {done.stderr.strip()}")
    return json.loads(done.stdout)


def remote_oid(branch: str, repo=ROOT) -> str | None:
    """The oid a remote branch points at, asked without needing a tracking ref.

    `git ls-remote` is the command the charter names for exactly this: the
    answer without the ref, for the case where `git push -u` set upstream
    config and created no remote-tracking ref.
    """
    done = git("ls-remote", "origin", f"refs/heads/{branch}", repo=repo, check=False)
    line = done.stdout.strip().split("\n")[0]
    return line.split()[0] if line.strip() else None


def park_head(oid: str, slug: str, repo=ROOT) -> str:
    """Bring one head object into this repository under this run's own namespace.

    Returns the ref. A head that is already an object here needs no network, so
    the common case of measuring the branch you are standing on costs nothing.
    """
    ref = f"{REF_NS}/{slug}"
    if git("rev-parse", "--verify", "--quiet", f"{oid}^{{commit}}",
           repo=repo, check=False).returncode != 0:
        git("fetch", "--no-tags", "origin", f"{oid}:{ref}", repo=repo, check=False)
    else:
        git("update-ref", ref, oid, repo=repo, check=False)
    if git("rev-parse", "--verify", "--quiet", ref, repo=repo, check=False).returncode != 0:
        raise RuntimeError(
            f"the remote would not serve {oid[:12]}, so the merge cannot be built")
    return ref


def drop_refs(repo=ROOT) -> None:
    """Remove every ref this run created. Called on the way out of every path."""
    listed = git("for-each-ref", "--format=%(refname)", REF_NS, repo=repo, check=False)
    for ref in listed.stdout.split():
        git("update-ref", "-d", ref, repo=repo, check=False)


def dirty_paths(repo=ROOT) -> list[str]:
    """What the caller has uncommitted, which this measurement does not see.

    Named rather than ignored. The default target is HEAD, and a seat with
    uncommitted work would otherwise read a green verdict as being about the
    tree in front of it.
    """
    done = git("status", "--porcelain", repo=repo, check=False)
    return sorted({line[3:].strip() for line in done.stdout.splitlines() if line[3:].strip()})


def out_of_space(text: str) -> bool:
    """Does this output say the volume filled, in any of the words used for it."""
    low = (text or "").lower()
    return any(marker in low for marker in ENOSPC_MARKERS)


def run_suite(worktree: Path, command: list[str], timeout: int) -> dict:
    """Run one command in the merged worktree and report what it did.

    The environment is inherited, because the packages the suite imports are the
    ones installed for the caller and a fresh environment would measure the
    install rather than the merge. `cwd` is the worktree, so every test that
    resolves the repository root off its own `__file__` resolves it to the
    merged tree.
    """
    started = time.monotonic()
    try:
        done = subprocess.run(command, capture_output=True, text=True,
                              cwd=str(worktree), timeout=timeout,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        return {"ran": False, "seconds": round(time.monotonic() - started, 1),
                "reason": f"the suites outran --timeout {timeout}s"}
    output = (done.stdout or "") + (done.stderr or "")
    lines = [line for line in output.splitlines() if line.strip()]
    if done.returncode != 0 and out_of_space(output):
        # A suite that died because the volume filled has said nothing about the
        # merge, and calling it red would bill the branch for the host.
        return {"ran": False, "seconds": round(time.monotonic() - started, 1),
                "reason": ("the shared volume filled while the suites ran, so "
                           "this is a fact about the host and not about the "
                           "merge. Re-run when there is room"),
                "tail": lines[-TAIL_LINES:]}
    if done.returncode < 0:
        # Killed by a signal, which `subprocess` reports as the negated signal
        # number. The suite said nothing about the merge, so this is the third
        # shape of the distinction this file already makes twice above: a
        # timeout is `unmeasured` because slow is not broken, a full volume is
        # `unmeasured` because the host is not the branch, and a signal is
        # `unmeasured` for exactly the same reason.
        #
        # Not hypothetical. On 2026-11-09 this seat's own run read `red` on a
        # suite SIGTERMed at 494 seconds, and on this host twelve seats run as
        # one unix user and some of them call `pkill`, so a seat's suite being
        # killed by somebody else's cleanup is an ordinary event rather than an
        # edge case. A merger handed `red` for it would send a branch to look
        # for a failure that does not exist.
        name = signal.Signals(-done.returncode).name if -done.returncode in \
            {s.value for s in signal.Signals} else f"signal {-done.returncode}"
        return {"ran": False, "seconds": round(time.monotonic() - started, 1),
                "reason": (f"the suites were killed by {name} after "
                           f"{round(time.monotonic() - started, 1)}s, so they said "
                           f"nothing about the merge. Re-run"),
                "tail": lines[-TAIL_LINES:]}
    return {"ran": True, "returncode": done.returncode,
            "seconds": round(time.monotonic() - started, 1),
            "tail": lines[-TAIL_LINES:]}


def preview(base: str, head_ref: str, command: list[str], timeout: int,
            merge_only: bool = False, repo=ROOT, runner=run_suite) -> dict:
    """The whole measurement: build the merge, then run `command` against it.

    `runner` is injected so the tests can assert on every branch of this
    function without running a ten-minute suite four times.
    """
    base_oid = git("rev-parse", "--verify", f"{base}^{{commit}}", repo=repo, check=False)
    if base_oid.returncode != 0:
        return {"state": UNMEASURED,
                "reason": f"the base {base!r} is not a commit in this clone"}
    base_oid = base_oid.stdout.strip()
    head_oid = git("rev-parse", "--verify", f"{head_ref}^{{commit}}",
                   repo=repo, check=False).stdout.strip()

    report = {"base": base, "base_oid": base_oid, "head_oid": head_oid}

    merge_base = git("merge-base", base_oid, head_oid, repo=repo, check=False)
    if merge_base.returncode != 0 or not merge_base.stdout.strip():
        return {**report, "state": UNMEASURED,
                "reason": ("these two commits have no merge base, which on a "
                           "complete clone means unrelated histories and on an "
                           "incomplete one means the history is still missing")}
    report["merge_base"] = merge_base.stdout.strip()

    if head_oid == report["merge_base"]:
        report["already_in_base"] = True

    merged, conflicts = merge(base_oid, head_oid, repo=repo)
    if merged is None:
        return {**report, "state": CONFLICT, "conflicts": conflicts}
    report["merge_commit"] = merged
    report["conflicts"] = []

    if merge_only:
        return {**report, "state": MERGE_CLEAN, "suite": None}

    worktree = Path(tempfile.mkdtemp(prefix="check-pr-green-"))
    try:
        added = git("worktree", "add", "--detach", str(worktree), merged,
                    repo=repo, check=False)
        if added.returncode != 0:
            why = added.stderr.strip()
            if out_of_space(why):
                why = ("the shared volume had no room for a second checkout of "
                       f"this repository: {why}")
            return {**report, "state": UNMEASURED,
                    "reason": f"the merged tree would not check out: {why}"}
        suite = runner(worktree, command, timeout)
    finally:
        git("worktree", "remove", "--force", str(worktree), repo=repo, check=False)
        shutil.rmtree(worktree, ignore_errors=True)
        git("worktree", "prune", repo=repo, check=False)

    report["suite"] = {**suite, "command": " ".join(command)}
    if not suite["ran"]:
        return {**report, "state": UNMEASURED, "reason": suite["reason"]}
    return {**report, "state": GREEN if suite["returncode"] == 0 else RED}


def render(report: dict, label: str, dirty: list[str]) -> list[str]:
    """The report a merger reads, which is one verdict and one re-performable command."""
    out = []
    state = report["state"]
    headline = {
        GREEN: "GREEN: the real merge is clean and the suites pass against it",
        RED: "RED: the real merge is clean and the suites fail against it",
        MERGE_CLEAN: ("MERGE CLEAN: the real merge is clean. No suite was run, "
                      "so this is not a verdict on the suites"),
        CONFLICT: "CONFLICT: the real merge conflicts, so no suite was run",
        UNMEASURED: "UNMEASURED: this could not be measured, so it is not a pass",
    }[state]
    out.append(f"{label}: {headline}")

    if "base_oid" in report:
        out.append(f"  base {report['base']} at {report['base_oid'][:8]}, "
                   f"head at {report.get('head_oid', '?')[:8]}, "
                   f"merge base {report.get('merge_base', '?')[:8]}")
    if report.get("already_in_base"):
        out.append("  this head is already an ancestor of the base, so the merge "
                   "is a fast-forward and adds nothing")
    if report.get("reason"):
        out.append(f"  reason: {report['reason']}")
    for path in report.get("conflicts", [])[:12]:
        out.append(f"  conflicts in {path}")
    if len(report.get("conflicts", [])) > 12:
        out.append(f"  and {len(report['conflicts']) - 12} more conflicted paths")

    # `.get` on `merge_commit` throughout, not `[...]`. A renderer that raises
    # on one of its own states turns a measured verdict into a traceback, which
    # is the one failure mode a tool whose whole job is reporting cannot have.
    merged = report.get("merge_commit", "")
    suite = report.get("suite")
    if suite and suite.get("ran"):
        out.append(f"  {suite.get('command', '?')} -> exit {suite['returncode']} "
                   f"in {suite['seconds']}s, against merge commit "
                   f"{merged[:8] or '?'}")
        for line in suite.get("tail", [])[-12:]:
            out.append(f"    {line}")
    elif state == MERGE_CLEAN:
        out.append("  --merge-only: drop the flag to run "
                   f"{shlex.join(DEFAULT_SUITE)} against merge commit "
                   f"{merged[:8] or '?'}")

    if dirty:
        out.append(f"  not measured: {len(dirty)} uncommitted path(s) in your "
                   "working tree, which no merge of your branch would carry")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pr", nargs="?", type=int,
                    help="a pull request number; its own base is used unless --base says otherwise")
    ap.add_argument("--branch", help="a branch name instead of a pull request number")
    ap.add_argument("--base", help="the trunk to merge into (default origin/main)")
    ap.add_argument("--merge-only", action="store_true",
                    help="answer the conflict question alone and run no suite")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                    help=f"seconds the suites may take before this is unmeasured (default {DEFAULT_TIMEOUT})")
    ap.add_argument("--json", action="store_true", help="the verdict as data")
    # One string, split with `shlex`, rather than a trailing positional. A
    # trailing `nargs="*"` next to an optional positional pull-request number is
    # ambiguous to argparse and it resolves the ambiguity by trying to parse
    # `python3` as an integer, which is how the first draft of this flag failed.
    ap.add_argument("--suite", default=None,
                    help="the suite command as one string, defaulting to "
                         f"{shlex.join(DEFAULT_SUITE)!r}")
    args = ap.parse_args(argv)

    blocked = preflight()
    if blocked:
        report = {"state": UNMEASURED, "reason": blocked}
        _emit(report, "check-pr-green", [], args.json)
        return EXIT[UNMEASURED]

    base = args.base
    label, slug, head_ref = "check-pr-green", None, None
    try:
        if args.pr:
            target = pr_target(args.pr)
            base = base or f"origin/{target['baseRefName']}"
            slug = str(target["number"])
            head_ref = park_head(target["headRefOid"], slug)
            label = f"#{target['number']} ({target['headRefName']})"
        elif args.branch:
            oid = remote_oid(args.branch)
            if oid is None:
                oid = git("rev-parse", "--verify", "--quiet", args.branch,
                          check=False).stdout.strip()
            if not oid:
                raise RuntimeError(
                    f"no branch named {args.branch!r} on origin or in this clone")
            slug = args.branch.replace("/", "-")
            head_ref = park_head(oid, slug)
            label = args.branch
        else:
            head_ref = "HEAD"
            label = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "HEAD"
    except (RuntimeError, json.JSONDecodeError) as exc:
        drop_refs()
        report = {"state": UNMEASURED, "reason": str(exc)}
        _emit(report, label, [], args.json)
        return EXIT[UNMEASURED]

    command = shlex.split(args.suite) if args.suite else list(DEFAULT_SUITE)
    dirty = dirty_paths() if head_ref == "HEAD" else []
    try:
        report = preview(base or "origin/main", head_ref, command,
                         args.timeout, merge_only=args.merge_only)
    finally:
        drop_refs()

    _emit(report, label, dirty, args.json)
    return EXIT[report["state"]]


def _emit(report: dict, label: str, dirty: list[str], as_json: bool) -> None:
    if as_json:
        print(json.dumps({**report, "target": label, "uncommitted": dirty}, indent=2))
    else:
        for line in render(report, label, dirty):
            print(line)


if __name__ == "__main__":
    sys.exit(main())
