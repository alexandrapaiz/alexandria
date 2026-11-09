"""The merge-preview instrument: does it answer, and does it stay read-only.

`tools/check_pr_green.py` is the instrument `docs/standards/lessons.md` L-P8
names and this repository never had. These tests build the thing it is supposed
to describe rather than mocking the answer: every fixture is a real git
repository with real divergent commits, and every verdict assertion is about
what the real three-way merge does.

Four groups.

1. **The verdicts.** Clean-and-passing is green, clean-and-failing is red, a
   conflict is its own exit code rather than red, and a suite that outran its
   timeout is unmeasured rather than either.
2. **The refusals.** A shallow clone and a narrow fetch refspec both make every
   branch comparison lie, and both are refused with the command that fixes
   them. This half is why the tool exists on a host that clones one deep.
3. **The promise of L-E12.** The caller's branch, HEAD, refs and working tree
   are the same after a run, and no worktree is left behind. The second half of
   that is not hypothetical: 2.6 GB of `/tmp/asc-green-*/merged` worktrees from
   a sibling instrument were sitting on the shared volume while this was
   written.
4. **The sentences.** A verdict that was not measured must not print the
   sentence for one that was, and a green must print the command and the exit
   code a merger can re-perform rather than an adjective.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "check_pr_green", ROOT / "tools" / "check_pr_green.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cpg = _module()


def run(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """A trunk with a register and a code file, both of which branches will touch."""
    path = tmp_path / "repo"
    path.mkdir()
    run(path, "init", "-q", "-b", "main")
    run(path, "config", "user.email", "seat@example.com")
    run(path, "config", "user.name", "seat")
    (path / "docs").mkdir()
    (path / "docs" / "ideas.md").write_text("# Ideas\n\n### one\n")
    (path / "app.py").write_text("def main():\n    return 1\n")
    run(path, "add", "-A")
    run(path, "commit", "-qm", "base")
    return path


def branch(repo, name, edits: dict[str, str]):
    """A branch off main that applies `edits`, leaving the checkout back on main."""
    run(repo, "checkout", "-q", "-b", name, "main")
    for rel, text in edits.items():
        (repo / rel).write_text(text)
    run(repo, "add", "-A")
    run(repo, "commit", "-qm", name)
    head = run(repo, "rev-parse", "HEAD")
    run(repo, "checkout", "-q", "main")
    return head


def commit_on_main(repo, rel, text):
    (repo / rel).write_text(text)
    run(repo, "add", "-A")
    run(repo, "commit", "-qm", f"main touches {rel}")


def passing(returncode=0):
    """A stand-in suite runner, so no test here pays for the real ten-minute suite."""
    def runner(worktree, command, timeout):
        # Asserting on the worktree is the point of injecting this: the suite
        # has to be handed the merged tree, not the caller's checkout.
        assert (Path(worktree) / "app.py").exists()
        return {"ran": True, "returncode": returncode, "seconds": 0.1,
                "tail": ["1 passed" if returncode == 0 else "1 failed"],
                "worktree": str(worktree)}
    return runner


# --------------------------------------------------------------------------
# 1. The verdicts


def test_a_clean_merge_with_a_passing_suite_is_green_and_exits_zero(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=passing())
    assert report["state"] == cpg.GREEN
    assert cpg.EXIT[report["state"]] == 0
    assert report["conflicts"] == []


def test_a_clean_merge_with_a_failing_suite_is_red_and_not_a_conflict(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("main", "a", ["false"], 60, repo=repo, runner=passing(1))
    assert report["state"] == cpg.RED
    assert cpg.EXIT[report["state"]] == 1
    # The merge was clean, so the finding is the suite and the report says so.
    assert report["conflicts"] == []
    assert report["suite"]["returncode"] == 1


def test_a_real_conflict_is_its_own_exit_code_rather_than_red(repo):
    """Exit 3 and exit 1 are different next steps: rebase, or fix your tests."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    commit_on_main(repo, "app.py", "def main():\n    return 3\n")
    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=passing())
    assert report["state"] == cpg.CONFLICT
    assert cpg.EXIT[report["state"]] == 3
    assert cpg.EXIT[cpg.CONFLICT] != cpg.EXIT[cpg.RED]
    assert "app.py" in report["conflicts"]
    # Nothing ran, and the report does not pretend otherwise.
    assert "suite" not in report


def test_a_suite_that_outran_its_timeout_is_unmeasured_rather_than_red(repo):
    """Slow and broken are different findings, and only one of them is the branch's."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})

    def times_out(worktree, command, timeout):
        return {"ran": False, "seconds": float(timeout),
                "reason": f"the suites outran --timeout {timeout}s"}

    report = cpg.preview("main", "a", ["true"], 7, repo=repo, runner=times_out)
    assert report["state"] == cpg.UNMEASURED
    assert cpg.EXIT[report["state"]] == 2
    assert "--timeout 7" in report["reason"]


def test_merge_only_answers_the_merge_and_claims_nothing_about_the_suites(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("main", "a", ["true"], 60, merge_only=True, repo=repo,
                         runner=passing())
    assert report["state"] == cpg.MERGE_CLEAN
    assert cpg.EXIT[report["state"]] == 0
    assert report["suite"] is None


def test_a_base_that_is_not_a_commit_is_unmeasured_and_names_itself(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("origin/nosuchtrunk", "a", ["true"], 60, repo=repo,
                         runner=passing())
    assert report["state"] == cpg.UNMEASURED
    assert "origin/nosuchtrunk" in report["reason"]


def test_unrelated_histories_are_unmeasured_and_never_a_quiet_pass(repo):
    """The shape a shallow clone produces, asserted on a complete one.

    `--depth 1` grafts the trunk with no parents, so a three-way merge between
    two close branches reads as unrelated histories. This builds that state
    honestly, with a real orphan branch, so the assertion is about the code path
    rather than about a clone the test would have to fake.
    """
    run(repo, "checkout", "-q", "--orphan", "elsewhere")
    run(repo, "rm", "-rqf", ".")
    (repo / "other.py").write_text("x = 1\n")
    run(repo, "add", "-A")
    run(repo, "commit", "-qm", "unrelated")
    run(repo, "checkout", "-q", "main")

    report = cpg.preview("main", "elsewhere", ["true"], 60, repo=repo,
                         runner=passing())
    assert report["state"] == cpg.UNMEASURED
    assert "merge base" in report["reason"]
    assert cpg.EXIT[report["state"]] != 0


def test_a_head_already_in_the_base_is_named_rather_than_reported_as_work(repo):
    """A branch whose work already landed merges clean and adds nothing."""
    oid = branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    run(repo, "merge", "-q", "--no-ff", "-m", "land a", oid)
    report = cpg.preview("main", "a", ["true"], 60, merge_only=True, repo=repo,
                         runner=passing())
    assert report["already_in_base"] is True


# --------------------------------------------------------------------------
# 2. The refusals, which are the half this host makes load-bearing


def test_a_shallow_clone_is_refused_with_both_halves_of_the_remedy(tmp_path, repo):
    """`--unshallow` alone is not the remedy, and three runs have paid for that."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    shallow = tmp_path / "shallow"
    done = subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        capture_output=True, text=True)
    assert done.returncode == 0, done.stderr

    assert cpg.shallow_state(shallow) is True
    reason = cpg.preflight(shallow)
    assert reason is not None
    assert "shallow" in reason
    assert "--unshallow" in reason
    assert "refs/heads/*" in reason


def test_a_narrow_refspec_is_refused_even_when_the_history_is_complete(tmp_path, repo):
    """The half the earlier remedy kept missing: deep history, still one branch."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    clone = tmp_path / "single"
    done = subprocess.run(
        ["git", "clone", "-q", "--single-branch", "--branch", "main",
         f"file://{repo}", str(clone)],
        capture_output=True, text=True)
    assert done.returncode == 0, done.stderr

    assert cpg.shallow_state(clone) is False
    assert cpg.refspec_is_wide(clone) is False
    reason = cpg.preflight(clone)
    assert reason is not None and "refs/heads/*" in reason

    # And the fix the message names actually widens it, so the message is not
    # advice nobody checked.
    run(clone, "config", "--add", "remote.origin.fetch",
        "+refs/heads/*:refs/remotes/origin/*")
    assert cpg.refspec_is_wide(clone) is True
    assert cpg.preflight(clone) is None


def test_a_complete_clone_with_a_wide_refspec_is_not_refused(repo):
    run(repo, "remote", "add", "origin", f"file://{repo}")
    run(repo, "config", "--add", "remote.origin.fetch",
        "+refs/heads/*:refs/remotes/origin/*")
    assert cpg.preflight(repo) is None


# --------------------------------------------------------------------------
# 3. The promise of L-E12: a measurement may only ask questions


def _state(repo):
    return {
        "branch": run(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "head": run(repo, "rev-parse", "HEAD"),
        "refs": run(repo, "for-each-ref", "--format=%(refname) %(objectname)"),
        "status": run(repo, "status", "--porcelain"),
        "worktrees": run(repo, "worktree", "list", "--porcelain"),
        "app": (repo / "app.py").read_text(),
    }


def test_the_measurement_leaves_the_callers_checkout_exactly_as_it_found_it(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n",
                       "docs/ideas.md": "# Ideas\n\n### one\n### two\n"})
    before = _state(repo)
    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=passing())
    assert report["state"] == cpg.GREEN
    assert _state(repo) == before


def test_no_worktree_is_left_behind_on_the_shared_volume(repo):
    """2.6 GB of a sibling instrument's abandoned worktrees is why this is a test."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    seen = {}

    def remember(worktree, command, timeout):
        seen["path"] = Path(worktree)
        assert seen["path"].exists()
        return {"ran": True, "returncode": 0, "seconds": 0.1, "tail": []}

    cpg.preview("main", "a", ["true"], 60, repo=repo, runner=remember)
    assert not seen["path"].exists()
    assert "check-pr-green" not in run(repo, "worktree", "list", "--porcelain")


def test_the_worktree_is_removed_even_when_the_suite_runner_raises(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    seen = {}

    def explode(worktree, command, timeout):
        seen["path"] = Path(worktree)
        raise RuntimeError("the suite runner died mid-run")

    with pytest.raises(RuntimeError):
        cpg.preview("main", "a", ["true"], 60, repo=repo, runner=explode)
    assert not seen["path"].exists()
    assert "check-pr-green" not in run(repo, "worktree", "list", "--porcelain")


def test_the_scratch_refs_are_gone_after_a_run(repo):
    oid = branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    run(repo, "update-ref", f"{cpg.REF_NS}/a", oid)
    assert cpg.REF_NS in run(repo, "for-each-ref", "--format=%(refname)")
    cpg.drop_refs(repo)
    assert cpg.REF_NS not in run(repo, "for-each-ref", "--format=%(refname)")


def test_this_runs_namespace_is_not_the_one_merge_order_deletes():
    """Two measurements in one clone must not be able to delete each other's refs."""
    import importlib.util as iu
    spec = iu.spec_from_file_location("merge_order", ROOT / "tools" / "merge_order.py")
    mo = iu.module_from_spec(spec)
    spec.loader.exec_module(mo)
    assert cpg.REF_NS != mo.REF_NS
    assert not cpg.REF_NS.startswith(mo.REF_NS)
    assert not mo.REF_NS.startswith(cpg.REF_NS)


# --------------------------------------------------------------------------
# 4. The sentences a merger reads


def test_merge_only_never_prints_the_sentence_for_a_suite_that_ran(repo):
    """The first live run of this tool printed exactly this sentence wrongly."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("main", "a", ["true"], 60, merge_only=True, repo=repo,
                         runner=passing())
    text = "\n".join(cpg.render(report, "#1", []))
    assert "suites pass" not in text
    assert "No suite was run" in text


def test_a_green_prints_the_command_and_the_exit_code_rather_than_an_adjective(repo):
    """L-P8's whole point: the merger re-performs a command, it does not believe a word."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("main", "a", ["python3", "-m", "pytest", "-q"], 60,
                         repo=repo, runner=passing())
    report["suite"]["command"] = "python3 -m pytest tests/ -q"
    text = "\n".join(cpg.render(report, "#1", []))
    assert "python3 -m pytest tests/ -q" in text
    assert "exit 0" in text
    assert report["merge_commit"][:8] in text


def test_a_conflict_report_names_the_file_a_merger_has_to_look_at(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    commit_on_main(repo, "app.py", "def main():\n    return 3\n")
    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=passing())
    text = "\n".join(cpg.render(report, "#1", []))
    assert "CONFLICT" in text
    assert "conflicts in app.py" in text


def test_uncommitted_work_is_named_as_not_measured(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=passing())
    text = "\n".join(cpg.render(report, "HEAD", ["pipeline/distill.py"]))
    assert "not measured" in text
    assert "uncommitted" in text


def test_every_state_has_a_headline_and_only_the_two_clean_ones_exit_zero():
    """A gate that saw nothing must not read as a quiet pass (L-A21)."""
    for state in (cpg.GREEN, cpg.MERGE_CLEAN, cpg.RED, cpg.UNMEASURED, cpg.CONFLICT):
        lines = cpg.render({"state": state}, "#1", [])
        assert lines and lines[0].startswith("#1: ")
    assert cpg.EXIT[cpg.GREEN] == 0
    assert cpg.EXIT[cpg.MERGE_CLEAN] == 0
    assert all(cpg.EXIT[s] != 0 for s in (cpg.RED, cpg.UNMEASURED, cpg.CONFLICT))


def test_the_json_verdict_carries_the_state_the_exit_code_came_from(repo):
    """A caller parsing the data must not have to re-derive the verdict from prose."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=passing())
    payload = json.loads(json.dumps({**report, "target": "#1", "uncommitted": []}))
    assert payload["state"] in cpg.EXIT
    assert payload["target"] == "#1"


def test_the_default_suite_names_the_tests_directory_the_conftest_lives_in():
    """A bare `pytest` collects `skills/` fixtures and misses the Modal stub."""
    assert "tests/" in cpg.DEFAULT_SUITE
    assert (ROOT / "tests" / "conftest.py").exists()


def test_the_timeout_default_is_longer_than_this_repositorys_own_suite():
    """Measured, not guessed: the full suite is over ten minutes on a seat host."""
    assert cpg.DEFAULT_TIMEOUT >= 1200


# --------------------------------------------------------------------------
# 5. A full shared volume is a fact about the host, never a verdict on the merge
#
# This half is load-bearing rather than defensive. The merged worktree is a
# second checkout of the whole repository, which here is roughly 430 MB, and the
# ExO seat measured this host's free space swinging between 4 MB and 3.6 GB on a
# sixty-second period. A run of this tool can be the write that fills the disk,
# and the run that wrote these tests lost a command's whole output to ENOSPC.
#
# Deliberately not a pre-flight `df`. That reading expires before it can be
# acted on, and it expires in the comfortable direction. The classification
# happens at the write, which is the only instrument that cannot go stale.


def test_every_word_the_kernel_uses_for_a_full_volume_is_recognised():
    for said in ("No space left on device",
                 "fatal: unable to write file: No space left on device",
                 "Disk quota exceeded",
                 "write error: ENOSPC"):
        assert cpg.out_of_space(said), said


def test_an_ordinary_test_failure_is_not_mistaken_for_a_full_volume():
    for said in ("1 failed, 2585 passed", "AssertionError: expected 4, got 2",
                 "", None):
        assert not cpg.out_of_space(said)


def test_a_suite_killed_by_a_full_volume_is_unmeasured_rather_than_red(repo):
    """Calling this red would bill the branch for the host."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})

    def disk_fills(worktree, command, timeout):
        return {"ran": False, "seconds": 1.0,
                "reason": "the shared volume filled while the suites ran",
                "tail": ["OSError: [Errno 28] No space left on device"]}

    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=disk_fills)
    assert report["state"] == cpg.UNMEASURED
    assert report["state"] != cpg.RED
    assert "volume" in report["reason"]


def test_run_suite_itself_classifies_the_full_volume_at_the_write(tmp_path):
    """Not the caller's job to notice. The function that ran the command does it."""
    script = tmp_path / "fills.py"
    script.write_text(
        "import sys\n"
        "sys.stderr.write('OSError: [Errno 28] No space left on device\\n')\n"
        "sys.exit(1)\n")
    out = cpg.run_suite(tmp_path, ["python3", str(script)], 60)
    assert out["ran"] is False
    assert "volume filled" in out["reason"]
    # The suite's own words are kept, because a merger re-performing the command
    # needs to see what it said.
    assert any("No space left" in line for line in out["tail"])


def test_an_ordinary_nonzero_suite_still_reports_its_exit_code(tmp_path):
    script = tmp_path / "fails.py"
    script.write_text("print('1 failed, 2585 passed')\nraise SystemExit(1)\n")
    out = cpg.run_suite(tmp_path, ["python3", str(script)], 60)
    assert out["ran"] is True
    assert out["returncode"] == 1


def test_nothing_in_this_tool_takes_a_pre_flight_disk_reading():
    """The reading expires before it can be used, and in the comfortable direction."""
    source = (ROOT / "tools" / "check_pr_green.py").read_text()
    for stale in ("shutil.disk_usage", "statvfs", '"df"', "'df'"):
        assert stale not in source, stale


# A suite killed by a signal is the third shape of one distinction this module
# already makes twice: a timeout is unmeasured because slow is not broken, a
# full volume is unmeasured because the host is not the branch, and a signal is
# unmeasured for the same reason. On this host twelve seats run as one unix
# user and some of them call `pkill`, so a seat's suite being killed by
# somebody else's cleanup is ordinary. Measured instance:
# this seat's own run on 2026-11-09 read `red` on a suite SIGTERMed at 494s.


def test_a_suite_killed_by_a_signal_is_unmeasured_rather_than_red(repo):
    """A merger handed red for this would hunt a failure that does not exist."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})

    def signalled(worktree, command, timeout):
        return {"ran": False, "seconds": 494.4,
                "reason": "the suites were killed by SIGTERM after 494.4s",
                "tail": ["........ [ 69%]"]}

    report = cpg.preview("main", "a", ["true"], 60, repo=repo, runner=signalled)
    assert report["state"] == cpg.UNMEASURED
    assert report["state"] != cpg.RED
    assert "SIGTERM" in report["reason"]


def test_run_suite_itself_classifies_a_signal_death_at_the_write(tmp_path):
    """Not the caller's job to notice, the same way the full volume is not."""
    script = tmp_path / "dies.py"
    script.write_text(
        "import os, signal, sys\n"
        "print('........ [ 69%]', flush=True)\n"
        "os.kill(os.getpid(), signal.SIGTERM)\n"
    )
    result = cpg.run_suite(tmp_path, [sys.executable, str(script)], 60)
    assert result["ran"] is False, result
    assert "SIGTERM" in result["reason"], result["reason"]
    assert "494" not in result["reason"], "the seconds should be this run's own"


def test_an_ordinary_nonzero_exit_is_still_red_and_not_unmeasured(tmp_path):
    """The repair must not launder a real failure into "could not look"."""
    script = tmp_path / "fails.py"
    script.write_text("print('1 failed, 2585 passed')\nraise SystemExit(1)\n")
    result = cpg.run_suite(tmp_path, [sys.executable, str(script)], 60)
    assert result["ran"] is True
    assert result["returncode"] == 1
