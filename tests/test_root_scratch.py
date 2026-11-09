"""The root-scratch gate, tested against the commit that made it necessary.

Incident 32's rule, verbatim: every gate is tested against an artifact known to
fail it before the gate is trusted. The artifact here is not synthetic. Commit
`078c5727` on `sec/2026-11-08-message` is the seventh instance of this class, a
`.board.json` dump committed to the checkout root through a broad `git add`, and
one of these tests points the gate at that commit in a worktree and asserts it
is found. The synthetic repositories cover the shapes that commit does not: a
stray in the index before any commit, a legitimate new root file, a clone with
no baseline, and the whole sub-root tree that must stay quiet.

    python3 -m pytest tests/test_root_scratch.py -q
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("root_scratch", REPO / "tools" / "root_scratch.py")
gate = importlib.util.module_from_spec(spec)
sys.modules["root_scratch"] = gate
spec.loader.exec_module(gate)

# The commit this class's seventh instance was found on, kept by hash so the
# test still points at it after the branch is merged or deleted.
SEVENTH_INSTANCE = "078c5727"
SEVENTH_INSTANCE_FILE = ".board.json"


def git(repo, *args):
    proc = subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


@pytest.fixture
def repo(tmp_path):
    """A repository with a `main` holding one entry the allowlist names."""
    root = tmp_path / "r"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    (root / "README.md").write_text("# r\n")
    git(root, "add", "README.md")
    git(root, "commit", "-q", "-m", "first")
    git(root, "checkout", "-q", "-b", "work")
    return root


# ---------------- the shapes that must fail ----------------


def test_a_staged_stray_is_found_before_any_commit(repo):
    (repo / ".board.json").write_text('{"columns": []}\n')
    git(repo, "add", "-A")
    report = gate.scan(cwd=repo)
    assert [s["path"] for s in report["strays"]] == [".board.json"]
    assert "staged" in report["strays"][0]["where"]


def test_a_committed_stray_is_found_after_the_commit(repo):
    (repo / ".msgs.json").write_text("[]\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "measuring")
    report = gate.scan(cwd=repo)
    assert [s["path"] for s in report["strays"]] == [".msgs.json"]
    assert "committed on this branch" in report["strays"][0]["where"]


def test_a_name_no_run_has_ever_used_is_found_the_first_time(repo):
    """The property the five denylist instances could not have.

    `.quarterly-rollup.ndjson` appears in no register, no ignore rule and no
    earlier instance of this class. The gate does not know it and does not
    need to.
    """
    (repo / ".quarterly-rollup.ndjson").write_text("{}\n")
    git(repo, "add", "-A")
    report = gate.scan(cwd=repo)
    assert [s["path"] for s in report["strays"]] == [".quarterly-rollup.ndjson"]


def test_the_real_seventh_instance_is_found_at_its_own_commit(tmp_path):
    have = subprocess.run(
        ["git", "cat-file", "-e", f"{SEVENTH_INSTANCE}^{{commit}}"],
        cwd=str(REPO), capture_output=True,
    )
    if have.returncode != 0:
        pytest.skip(f"{SEVENTH_INSTANCE} is not in this clone")
    work = tmp_path / "w"
    git(REPO, "worktree", "add", "-q", "--detach", str(work), SEVENTH_INSTANCE)
    try:
        report = gate.scan(cwd=work)
        assert SEVENTH_INSTANCE_FILE in [s["path"] for s in report["strays"]]
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(work)],
                       cwd=str(REPO), capture_output=True)


# ---------------- the shapes that must stay quiet ----------------


def test_work_under_the_root_is_never_reported(repo):
    for rel in ("docs/security/audit-2026-11-09.md", "tools/root_scratch.py",
                "docs/agents/incidents/inbox/INC-2026-11-09-x.md"):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")
    git(repo, "add", "-A")
    assert gate.scan(cwd=repo)["strays"] == []


def test_an_allowed_new_root_file_is_not_a_stray(repo):
    (repo / "pyproject.toml").write_text("[tool]\n")
    git(repo, "add", "-A")
    assert gate.scan(cwd=repo)["strays"] != []
    assert gate.scan(cwd=repo, allow=["pyproject.toml"])["strays"] == []


def test_an_allow_that_matched_nothing_is_reported(repo, capsys, monkeypatch):
    """Silence on a typo would read as a pass.

    `--allow` takes a name rather than a file this tool opens, so nothing in
    the ordinary path would ever raise on a value that names nothing. The note
    is the only thing standing between a misspelled allow and a stray that
    shipped because the gate was told to ignore a different name.
    """
    monkeypatch.chdir(repo)
    monkeypatch.setattr(gate, "ROOT", repo)
    (repo / ".board.json").write_text("{}\n")
    git(repo, "add", "-A")
    assert gate.main(["--allow", ".bord.json"]) == 1
    captured = capsys.readouterr()
    assert ".board.json" in captured.out
    assert "--allow .bord.json matched no addition" in captured.err
    assert gate.main(["--allow", ".board.json"]) == 0
    assert "matched no addition" not in capsys.readouterr().err


def test_a_root_file_main_already_carries_is_not_an_addition(repo):
    """The two landed instances are `--tracked`'s business, not the gate's.

    A branch that merely keeps `site-server.log` must not fail, or every branch
    in this repository fails until somebody deletes another seat's file.
    """
    (repo / "site-server.log").write_text("> start\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "landed")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "work")
    git(repo, "checkout", "-q", "-b", "later")
    (repo / "docs").mkdir()
    (repo / "docs" / "a.md").write_text("a\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "ordinary work")
    assert gate.scan(cwd=repo)["strays"] == []


def test_this_repository_is_clean_at_the_root():
    report = gate.scan()
    assert report["measured"] is True
    assert report["strays"] == [], report["strays"]


# ---------------- refusing to answer ----------------


def test_no_baseline_refuses_rather_than_passing(tmp_path):
    """A gate that cannot measure must not report clean.

    This is the failure mode incident 20's rule is about: the silent pass is
    indistinguishable from the real one, and only the loud refusal is.
    """
    root = tmp_path / "lonely"
    root.mkdir()
    git(root, "init", "-q", "-b", "trunk")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    (root / "README.md").write_text("# r\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "first")
    report = gate.scan(cwd=root)
    assert report["measured"] is False
    assert "main" in report["reason"]


# ---------------- the allowlist's own contract ----------------


def test_every_allowlist_entry_names_a_citation_and_still_exists():
    for name, citation in gate.BELONGS.items():
        assert citation and citation.strip(), name
        assert (REPO / name).exists(), f"{name} is on the allowlist and not in the tree"


def test_the_allowlist_covers_every_cited_root_entry_on_head():
    """No entry of `main`'s root is missing from the list except the two landed
    strays, so `--tracked` reports exactly those two and not a backlog."""
    tracked = {path for path, _why in gate._tracked_strays()}
    assert tracked == set(gate.KNOWN_LANDED), tracked


def test_no_cited_root_entry_on_head_is_the_wrong_kind():
    """Every name BELONGS cites is a directory or a regular file on HEAD.

    This is the premise ROOT_MODES rests on, asserted rather than assumed. If a
    legitimate root entry ever has to be a symlink or a submodule, this fails
    first and the bound gets widened deliberately.
    """
    wrong = [
        (path, why) for path, why in gate._tracked_strays()
        if path in gate.BELONGS
    ]
    assert wrong == [], wrong


def test_exit_codes(repo, capsys, monkeypatch):
    monkeypatch.chdir(repo)
    monkeypatch.setattr(gate, "ROOT", repo)
    assert gate.main([]) == 0
    assert capsys.readouterr().out == ""
    (repo / ".reply.md").write_text("hi\n")
    git(repo, "add", "-A")
    assert gate.main([]) == 1
    assert ".reply.md" in capsys.readouterr().out


# ---------------- the fourth bound: what an entry is, not what it is called ----------------


def test_a_root_symlink_wearing_a_cited_name_is_a_stray(repo):
    """The handed-back class, at the shape that reproduced it.

    A symlink at the root named `skills`, which BELONGS cites as the skills
    library, pointing at a directory outside the tree. Three of this gate's
    bounds are decisions about a name and this one is not, which is the only
    reason it is caught.
    """
    (repo / "skills").symlink_to("/etc")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a root symlink named skills")
    report = gate.scan(cwd=repo)
    assert [s["path"] for s in report["strays"]] == ["skills"]
    assert "symlink" in report["strays"][0]["why"]


def test_the_identical_link_under_an_uncited_name_is_caught_by_the_first_bound(repo):
    """The control. Without it the test above proves nothing about the kind,
    because an uncited name is caught whatever kind it is."""
    (repo / "notcited").symlink_to("/etc")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "an uncited root symlink")
    report = gate.scan(cwd=repo)
    assert [s["path"] for s in report["strays"]] == ["notcited"]
    assert "cites this name" in report["strays"][0]["why"]


def test_a_root_submodule_wearing_a_cited_name_is_a_stray(repo, tmp_path):
    """A gitlink at the root named `site`, which is a whole other repository
    entering this one under a name a reviewer reads as the Next.js app."""
    other = tmp_path / "other"
    other.mkdir()
    git(other, "init", "-q", "-b", "main")
    git(other, "config", "user.email", "t@example.com")
    git(other, "config", "user.name", "t")
    (other / "f").write_text("x\n")
    git(other, "add", "-A")
    git(other, "commit", "-q", "-m", "first")
    git(repo, "-c", "protocol.file.allow=always", "submodule", "add", "-q",
        "--name", "site", str(other), "site")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a submodule named site")
    report = gate.scan(cwd=repo)
    strays = {s["path"]: s["why"] for s in report["strays"]}
    assert "site" in strays, strays
    assert "submodule" in strays["site"]
    # `.gitmodules` is caught too, by the name bound, and that is the only
    # reason the submodule case was not entirely silent before this bound.
    assert ".gitmodules" in strays


def test_a_cited_name_of_the_right_kind_stays_quiet(repo):
    """The bound refuses a kind and not a name, so an ordinary legitimate
    addition under a cited name is still silent."""
    (repo / "sources.yaml").write_text("sources: []\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a real root file on the list")
    report = gate.scan(cwd=repo)
    assert report["strays"] == []


# ---------------- a question that cannot be asked is not an answer ----------------


def test_no_git_binary_refuses_rather_than_passing(repo, monkeypatch, capsys):
    """Exit 2 and not 1, because 1 is this gate's "a stray was found" code and
    a caller cannot tell a crash from a finding when they share an exit."""
    monkeypatch.chdir(repo)
    monkeypatch.setattr(gate, "ROOT", repo)
    monkeypatch.setenv("PATH", str(repo / "no-such-dir"))
    assert gate.main([]) == 2
    assert "could not be asked" in capsys.readouterr().err


def test_a_git_timeout_refuses_rather_than_passing(repo, monkeypatch, capsys):
    """A timeout is git saying nothing at all. Patched at `subprocess.run`
    rather than by sleeping, so the suite does not pay thirty seconds."""
    def timing_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=30)

    monkeypatch.chdir(repo)
    monkeypatch.setattr(gate, "ROOT", repo)
    monkeypatch.setattr(gate.subprocess, "run", timing_out)
    assert gate.main([]) == 2
    assert "could not be asked" in capsys.readouterr().err


def test_every_git_call_carries_a_timeout(repo, monkeypatch):
    """The bound itself, rather than one call's behaviour. Until 2026-11-09 this
    file's single git helper had no timeout at all, while the tool this seat had
    just reported the class against had thirty seconds."""
    seen = []
    real = subprocess.run

    def recording(*args, **kwargs):
        seen.append(kwargs.get("timeout"))
        return real(*args, **kwargs)

    monkeypatch.setattr(gate.subprocess, "run", recording)
    gate.scan(cwd=repo)
    gate._tracked_strays(cwd=repo)
    assert seen, "no git call was made, so this test proves nothing"
    assert all(t is not None for t in seen), seen


def test_a_failing_git_call_refuses_rather_than_reporting_a_stray(repo, monkeypatch, capsys):
    """A non-zero exit from a git call used to raise an uncaught RuntimeError,
    which Python turns into exit 1, which is indistinguishable from a finding."""
    def refusing(*args, **kwargs):
        argv = args[0]
        if "diff" in argv:
            return subprocess.CompletedProcess(argv, 128, "", "fatal: nope")
        return real(*args, **kwargs)

    real = subprocess.run
    monkeypatch.chdir(repo)
    monkeypatch.setattr(gate, "ROOT", repo)
    monkeypatch.setattr(gate.subprocess, "run", refusing)
    assert gate.main([]) == 2
    assert "cannot measure" in capsys.readouterr().err


def test_allow_is_the_escape_hatch_for_both_bounds(repo):
    """`--allow` is a person naming one exact path for one run, so it has to
    clear the kind bound too. Without this there is no escape hatch for the
    second bound at all, and a seat with a legitimate need has to edit the tool."""
    (repo / "skills").symlink_to("/etc")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a root symlink named skills")
    assert gate.scan(cwd=repo)["strays"] != []
    waived = gate.scan(cwd=repo, allow=["skills"])
    assert waived["strays"] == []
    assert waived["allowed_seen"] == ["skills"]


def test_belongs_alone_does_not_clear_the_kind_bound(repo):
    """The other half, and the reason the two permissions are not one set.
    `BELONGS` is a claim that a name is cited, which says nothing about what the
    entry under it is, so being on the list must not waive the kind."""
    (repo / "skills").symlink_to("/etc")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a root symlink named skills")
    assert "skills" in gate.BELONGS
    report = gate.scan(cwd=repo)
    assert [s["path"] for s in report["strays"]] == ["skills"]
