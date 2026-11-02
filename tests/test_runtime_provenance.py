"""Does the runner-provenance check tell "I compared the wrong pair" from "nothing is wrong".

Run with `python3 -m pytest tests/test_runtime_provenance.py -q`.

`tools/runtime_provenance.py` reads a checkout and a global install that live
outside this repository, so every test here builds both in a temporary
directory, for the reason `test_cron_firing.py` and `test_wake_routes.py` both
give: a test that needs the host's disk is a test nobody runs on a pull
request. Nothing here touches `/srv/asc`.

The polarity is the point, and it is the opposite way round from most checks
here. `install == checkout` is the answer that proves nothing — the install is
a symlink, so that comparison cannot fail — and a check that printed it as a
pass is how the question went unanswered after somebody had looked. So the
pass condition is about the **repository**, not about the install, and an
install this host does not have is not a finding.

Two regressions are pinned from this file's own first run against the live
host. `git status --porcelain` begins an unstaged modification with a space, so
stripping stdout ate the first row's first path letter and dropped one of two
modified files from the executed path; and the default branch is read from the
remote's own HEAD rather than assumed to be `main`.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import runtime_provenance as rp  # noqa: E402


def run(cwd, *args):
    subprocess.run(args, cwd=str(cwd), check=True,
                   capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path):
    """An upstream with two commits and a clone of the first, in the shape the
    host's runtime checkout has: `cli/src/index.js` and `cli/src/lib/runner.js`
    under a `cli/` directory that the install points at."""
    up = tmp_path / "upstream"
    (up / "cli" / "src" / "lib").mkdir(parents=True)
    run(up, "git", "init", "--initial-branch=main", "-q")
    run(up, "git", "config", "user.email", "t@example.com")
    run(up, "git", "config", "user.name", "t")
    (up / "cli" / "src" / "index.js").write_text("one\n")
    (up / "cli" / "src" / "lib" / "runner.js").write_text("one\n")
    (up / "README.md").write_text("one\n")
    run(up, "git", "add", "-A")
    run(up, "git", "commit", "-qm", "first")
    first = subprocess.run(["git", "-C", str(up), "rev-parse", "HEAD"],
                           capture_output=True, text=True).stdout.strip()
    (up / "README.md").write_text("two\n")
    run(up, "git", "add", "-A")
    run(up, "git", "commit", "-qm", "second")

    co = tmp_path / "checkout"
    run(tmp_path, "git", "clone", "-q", str(up), str(co))
    run(co, "git", "config", "user.email", "t@example.com")
    run(co, "git", "config", "user.name", "t")
    return {"upstream": up, "checkout": co, "first": first,
            "install": tmp_path / "install"}


def test_clean_and_current_is_the_only_pass(repo):
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]))
    assert v["findings"] == []
    assert v["behind"] == 0
    assert v["detached"] is False
    assert rp.main(["--checkout", str(repo["checkout"]),
                    "--install", str(repo["install"])]) == 0


def test_a_missing_install_is_not_a_finding(repo):
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]))
    assert v["install_shape"]["shape"] == "missing"
    assert v["findings"] == []


def test_a_symlinked_install_says_the_comparison_proves_nothing(repo):
    link = repo["install"]
    os.symlink(str(repo["checkout"] / "cli"), str(link))
    v = rp.verdict(str(repo["checkout"]), str(link))
    assert v["install_shape"]["shape"] == "link"
    assert "proves nothing" in v["install_shape"]["note"]


def test_a_copied_install_can_drift_and_says_so(repo):
    copy = repo["install"]
    copy.mkdir()
    (copy / "index.js").write_text("one\n")
    v = rp.verdict(str(repo["checkout"]), str(copy))
    assert v["install_shape"]["shape"] == "copy"
    assert "drift" in v["install_shape"]["note"]


def test_detached_head_is_a_finding_naming_git_pull(repo):
    run(repo["checkout"], "git", "checkout", "-q", repo["first"])
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]))
    keys = [k for k, _ in v["findings"]]
    assert "detached" in keys
    assert "`git pull` cannot repair it" in dict(v["findings"])["detached"]


def test_behind_the_default_branch_is_a_finding_with_its_distance(repo):
    run(repo["checkout"], "git", "checkout", "-q", "-B", "main", repo["first"])
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]))
    assert v["behind"] == 1
    assert "behind" in [k for k, _ in v["findings"]]
    assert "1 commits behind origin/main" in dict(v["findings"])["behind"]


def test_every_modified_executed_file_is_reported_not_all_but_the_first(repo):
    """The pinned regression. Two unstaged modifications, and `git status
    --porcelain` starts each line with a space: the first reader stripped
    stdout, ate the first row's leading space, and the offset-3 path parse then
    dropped that row's first letter, so one of two files vanished from the
    executed-path list."""
    os.symlink(str(repo["checkout"] / "cli"), str(repo["install"]))
    (repo["checkout"] / "cli" / "src" / "index.js").write_text("hotfix\n")
    (repo["checkout"] / "cli" / "src" / "lib" / "runner.js").write_text("hotfix\n")
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]))
    paths = sorted(d["path"] for d in v["dirty_on_executed_path"])
    assert paths == ["cli/src/index.js", "cli/src/lib/runner.js"]
    assert "uncommitted" in [k for k, _ in v["findings"]]


def test_an_edit_outside_the_executed_directory_is_counted_but_not_a_finding(repo):
    os.symlink(str(repo["checkout"] / "cli"), str(repo["install"]))
    (repo["checkout"] / "README.md").write_text("edited\n")
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]))
    assert [d["path"] for d in v["dirty"]] == ["README.md"]
    assert v["dirty_on_executed_path"] == []
    assert v["findings"] == []


def test_the_default_branch_comes_from_the_remote_not_from_the_word_main(tmp_path):
    up = tmp_path / "up"
    up.mkdir()
    run(up, "git", "init", "--initial-branch=trunk", "-q")
    run(up, "git", "config", "user.email", "t@example.com")
    run(up, "git", "config", "user.name", "t")
    (up / "a").write_text("a\n")
    run(up, "git", "add", "-A")
    run(up, "git", "commit", "-qm", "first")
    co = tmp_path / "co"
    run(tmp_path, "git", "clone", "-q", str(up), str(co))
    v = rp.verdict(str(co), str(tmp_path / "nope"))
    assert v["default_branch"] == "trunk"
    assert v["findings"] == []


def test_an_unreadable_checkout_exits_two_and_never_zero(tmp_path):
    plain = tmp_path / "not-a-repo"
    plain.mkdir()
    v = rp.verdict(str(plain), str(tmp_path / "nope"))
    assert v["readable"] is False
    assert rp.main(["--checkout", str(plain), "--install", str(tmp_path / "nope")]) == 2


def test_the_live_host_reading_is_reproducible_when_the_host_is_there():
    """Not a unit test and skipped off the host: the one assertion is that the
    check does not crash on the real shape, which is a symlinked install over a
    detached, dirty, far-behind checkout."""
    if not os.path.isdir("/srv/asc/repos/epitome/.git"):
        pytest.skip("not on the company host")
    v = rp.verdict()
    assert v["readable"] is True
    assert isinstance(v["findings"], list)


def _staged(tmp_path, **files):
    d = tmp_path / "staged"
    d.mkdir(exist_ok=True)
    for name, body in files.items():
        (d / name).write_text(body)
    return d


def test_a_staged_copy_that_matches_is_not_called_unbacked(repo, tmp_path):
    """The pinned overclaim. The first draft of this check reported local edits
    as having 'no commit, no review and no backup', and said so in a message to
    two seats; the five edits it was reading are committed in another
    repository with an actuator beside them. A staged copy holding the same
    bytes is a backup, and the check has to say so."""
    os.symlink(str(repo["checkout"] / "cli"), str(repo["install"]))
    (repo["checkout"] / "cli" / "src" / "index.js").write_text("hotfix\n")
    staged = _staged(tmp_path, **{"index.js": "hotfix\n"})
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]), str(staged))
    assert v["staged"]["files"]["cli/src/index.js"] == "same"
    keys = [k for k, _ in v["findings"]]
    assert "staged-elsewhere" in keys
    assert "uncommitted" not in keys


def test_a_staged_copy_that_differs_leaves_the_edit_unaccounted(repo, tmp_path):
    os.symlink(str(repo["checkout"] / "cli"), str(repo["install"]))
    (repo["checkout"] / "cli" / "src" / "index.js").write_text("hotfix\n")
    staged = _staged(tmp_path, **{"index.js": "four clauses ahead\n"})
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]), str(staged))
    assert v["staged"]["files"]["cli/src/index.js"] == "differs"
    assert "uncommitted" in [k for k, _ in v["findings"]]


def test_one_file_held_and_one_loose_is_reported_as_both(repo, tmp_path):
    """The live host's own shape on 2026-11-02: `index.js` matched HQ's staged
    copy exactly and `runner.js` did not, because the staged copy is four
    prompt clauses ahead of what runs. A check that printed one verdict for the
    pair would have been wrong whichever verdict it chose."""
    os.symlink(str(repo["checkout"] / "cli"), str(repo["install"]))
    (repo["checkout"] / "cli" / "src" / "index.js").write_text("hotfix\n")
    (repo["checkout"] / "cli" / "src" / "lib" / "runner.js").write_text("hotfix\n")
    staged = _staged(tmp_path, **{"index.js": "hotfix\n", "runner.js": "ahead\n"})
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]), str(staged))
    keys = [k for k, _ in v["findings"]]
    assert "staged-elsewhere" in keys and "uncommitted" in keys
    assert "cli/src/lib/runner.js" in dict(v["findings"])["uncommitted"]
    assert "cli/src/index.js" in dict(v["findings"])["staged-elsewhere"]


def test_a_file_the_staged_copy_does_not_carry_reads_absent(repo, tmp_path):
    os.symlink(str(repo["checkout"] / "cli"), str(repo["install"]))
    (repo["checkout"] / "cli" / "src" / "index.js").write_text("hotfix\n")
    staged = _staged(tmp_path, **{"unrelated.js": "x\n"})
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]), str(staged))
    assert v["staged"]["files"]["cli/src/index.js"] == "absent"
    assert "uncommitted" in [k for k, _ in v["findings"]]


def test_a_missing_staged_path_is_an_error_on_the_argument_not_a_pass(repo, tmp_path):
    os.symlink(str(repo["checkout"] / "cli"), str(repo["install"]))
    (repo["checkout"] / "cli" / "src" / "index.js").write_text("hotfix\n")
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]),
                   str(tmp_path / "no-such-dir"))
    assert v["staged"]["error"]
    assert "uncommitted" in [k for k, _ in v["findings"]]


def test_a_clean_tree_with_a_staged_argument_still_passes(repo, tmp_path):
    staged = _staged(tmp_path, **{"index.js": "whatever\n"})
    v = rp.verdict(str(repo["checkout"]), str(repo["install"]), str(staged))
    assert v["findings"] == []
