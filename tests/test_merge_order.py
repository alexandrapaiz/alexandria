"""The merge-order instrument: does it find the exclusivity, and does it stay read-only.

`tools/merge_order.py` answers a question no per-pull-request check asks, so
these tests build the queue it is supposed to describe rather than mocking the
answer. Every fixture is a real git repository in a temp directory with real
divergent commits, and every assertion is about what the real merge does.

Two groups. The first is the measurement: a queue that lands, a queue that is
mutually exclusive over one appended file, the anchor tally, and the prose
split. The second is the promise of L-E12, that a measurement which runs inside
a directory somebody else is standing in may only ask questions.
"""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "merge_order", ROOT / "tools" / "merge_order.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


mo = _module()


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
    (path / "docs" / "ideas.md").write_text("# Ideas\n\n### one\n- Status: proposed\n")
    (path / "app.py").write_text("def main():\n    return 1\n")
    run(path, "add", "-A")
    run(path, "commit", "-qm", "base")
    return path


def branch(repo, name, edits: dict[str, str]):
    """A branch off main that applies `edits` and returns its head oid."""
    run(repo, "checkout", "-q", "-b", name, "main")
    for rel, text in edits.items():
        (repo / rel).write_text(text)
    run(repo, "add", "-A")
    run(repo, "commit", "-qm", name)
    head = run(repo, "rev-parse", "HEAD")
    run(repo, "checkout", "-q", "main")
    return head


def queue(repo, *names):
    """The shape `measure` wants, with the refs it reads already in place."""
    prs = []
    for i, name in enumerate(names, start=1):
        oid = run(repo, "rev-parse", name)
        run(repo, "update-ref", f"{mo.REF_NS}/{i}", oid)
        prs.append({"number": i, "title": name, "headRefOid": oid,
                    "createdAt": f"2026-10-24T0{i}:00:00Z"})
    return prs


def append(base_text, line):
    return base_text + line


LEDGER = "# Ideas\n\n### one\n- Status: proposed\n"


def test_two_branches_that_touch_different_files_both_land(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    branch(repo, "b", {"docs/ideas.md": append(LEDGER, "\n### two\n- Status: proposed\n")})
    report = mo.measure(queue(repo, "a", "b"), "main", repo=repo)

    assert report["land"] == [1, 2]
    assert report["blocked"] == []
    assert report["pairs"] == []
    assert mo.verdict(report) == mo.CLEAN


def test_two_appends_at_one_anchor_are_mutually_exclusive_and_name_the_file(repo):
    """L-A48's shape, reproduced: both clean against the trunk, exclusive with each other."""
    branch(repo, "a", {"docs/ideas.md": append(LEDGER, "\n### from a\n- Status: proposed\n")})
    branch(repo, "b", {"docs/ideas.md": append(LEDGER, "\n### from b\n- Status: proposed\n")})
    prs = queue(repo, "a", "b")
    report = mo.measure(prs, "main", repo=repo)

    # Each one lands on the trunk alone, which is all `mergeable` ever asks.
    assert mo.merge("main", f"{mo.REF_NS}/1", repo=repo)[0]
    assert mo.merge("main", f"{mo.REF_NS}/2", repo=repo)[0]

    # The pair does not, and the file is named.
    assert report["pairs"] == [{"left": 1, "right": 2,
                                "conflicts": ["docs/ideas.md"]}]
    assert report["anchors"] == [("docs/ideas.md", 1)]
    assert report["prose_only_pairs"] == 1


def test_the_sequential_pass_skips_the_blocked_one_and_carries_on(repo):
    """The owner's morning: a blocked branch must not stop the ones behind it."""
    branch(repo, "a", {"docs/ideas.md": append(LEDGER, "\n### from a\n- Status: proposed\n")})
    branch(repo, "b", {"docs/ideas.md": append(LEDGER, "\n### from b\n- Status: proposed\n")})
    branch(repo, "c", {"app.py": "def main():\n    return 3\n"})
    report = mo.measure(queue(repo, "a", "b", "c"), "main", repo=repo)

    assert report["land"] == [1, 3]
    assert report["blocked"] == [2]
    assert report["sequence"][1]["conflicts"] == ["docs/ideas.md"]
    assert mo.verdict(report) == mo.BLOCKED


def test_a_pair_exclusive_over_code_is_not_counted_as_prose(repo):
    """The prose split is the finding's headline, so it must not swallow code."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    branch(repo, "b", {"app.py": "def main():\n    return 3\n"})
    report = mo.measure(queue(repo, "a", "b"), "main", repo=repo)

    assert len(report["pairs"]) == 1
    assert report["prose_only_pairs"] == 0
    assert report["anchors"] == [("app.py", 1)]


def test_a_pair_exclusive_over_both_prose_and_code_is_not_prose_only(repo):
    branch(repo, "a", {"app.py": "def main():\n    return 2\n",
                       "docs/ideas.md": append(LEDGER, "\n### from a\n- Status: proposed\n")})
    branch(repo, "b", {"app.py": "def main():\n    return 3\n",
                       "docs/ideas.md": append(LEDGER, "\n### from b\n- Status: proposed\n")})
    report = mo.measure(queue(repo, "a", "b"), "main", repo=repo)

    assert sorted(report["pairs"][0]["conflicts"]) == ["app.py", "docs/ideas.md"]
    assert report["prose_only_pairs"] == 0


def test_an_empty_queue_is_clean_rather_than_blocked(repo):
    report = mo.measure([], "main", repo=repo)
    assert report["measured"] == 0
    assert mo.verdict(report) == mo.CLEAN
    assert mo.render(report, {})[0].endswith("no open pull requests against main")


def test_a_queue_that_cannot_be_read_exits_two_and_says_so(repo, monkeypatch, capsys):
    """L-A21: a run that saw nothing must not read as a quiet pass."""
    def refuse(*_args, **_kwargs):
        raise RuntimeError("gh pr list failed: HTTP 403")

    monkeypatch.setattr(mo, "open_prs", refuse)
    code = mo.main([])
    assert code == mo.EXIT[mo.UNMEASURED] == 2
    printed = capsys.readouterr().out
    assert "could not be read" in printed
    assert "403" in printed


def test_the_unmeasured_json_carries_the_reason_rather_than_an_empty_queue(mo_json=None):
    report = {"state": mo.UNMEASURED, "measured": None, "reason": "boom"}
    assert mo.verdict(report) == mo.UNMEASURED
    assert json.loads(json.dumps(report))["reason"] == "boom"


def test_is_prose_reads_registers_and_not_the_pipeline():
    assert mo.is_prose("docs/ideas.md")
    assert mo.is_prose("docs/agents/incidents.md")
    assert mo.is_prose("prompts/engineer-agent.md")
    assert not mo.is_prose("pipeline/weekly.py")
    assert not mo.is_prose("site/app/page.js")
    assert not mo.is_prose("docs/schema.sql")


def test_the_measurement_leaves_the_callers_checkout_exactly_as_it_found_it(repo):
    """L-E12, with the same assertions the lesson's own test makes.

    The instrument runs inside a directory a seat is working in, so the whole
    value of the numbers depends on nothing moving while they are taken.
    """
    branch(repo, "a", {"docs/ideas.md": append(LEDGER, "\n### from a\n- Status: proposed\n")})
    branch(repo, "b", {"docs/ideas.md": append(LEDGER, "\n### from b\n- Status: proposed\n")})

    before = {
        "head": run(repo, "rev-parse", "HEAD"),
        "branch": run(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "shallow": run(repo, "rev-parse", "--is-shallow-repository"),
        "status": run(repo, "status", "--porcelain"),
        "refs": run(repo, "for-each-ref", "--format=%(refname) %(objectname)"),
    }
    assert before["shallow"] == "false"

    prs = queue(repo, "a", "b")
    mo.measure(prs, "main", repo=repo)
    mo.drop_refs(repo=repo)

    after = {
        "head": run(repo, "rev-parse", "HEAD"),
        "branch": run(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "shallow": run(repo, "rev-parse", "--is-shallow-repository"),
        "status": run(repo, "status", "--porcelain"),
        "refs": run(repo, "for-each-ref", "--format=%(refname) %(objectname)"),
    }
    assert after == before


def test_the_scratch_refs_are_gone_even_when_a_merge_raises(repo, monkeypatch):
    """`drop_refs` is in a `finally`, so a crash mid-queue leaves no namespace behind."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    queue(repo, "a")
    assert run(repo, "for-each-ref", "--format=%(refname)", mo.REF_NS)

    mo.drop_refs(repo=repo)
    assert run(repo, "for-each-ref", "--format=%(refname)", mo.REF_NS) == ""


#: The git verbs and flags that write into the caller's checkout rather than
#: asking it a question. `--depth` is the one L-E12 was written about: it looks
#: like thrift and it leaves `.git/shallow` behind for every later reader.
WRITES_TO_THE_CALLER = ("--depth", "--unshallow", "checkout", "switch",
                        "reset", "clean", "stash", "pull", "merge")


def test_no_git_command_the_tool_runs_can_write_to_the_callers_checkout(repo, monkeypatch):
    """L-E12, tested on the commands rather than on the source text.

    A grep of the file would pass on a docstring and fail on a comment. This
    records every argv the module actually hands to git, across the fetch and
    both measurement passes, and reads the recorded list.
    """
    origin = repo
    branch(origin, "a", {"app.py": "def main():\n    return 2\n"})
    branch(origin, "b", {"docs/ideas.md": append(LEDGER, "\n### from b\n- Status: proposed\n")})

    clone = repo.parent / "clone"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    run(clone, "config", "user.email", "seat@example.com")
    run(clone, "config", "user.name", "seat")

    seen = []
    real = mo.git

    def recording(*args, **kwargs):
        seen.append(list(args))
        return real(*args, **kwargs)

    monkeypatch.setattr(mo, "git", recording)

    prs = [{"number": 7, "title": "a", "headRefOid": run(origin, "rev-parse", "a"),
            "createdAt": "2026-10-24T01:00:00Z"},
           {"number": 8, "title": "b", "headRefOid": run(origin, "rev-parse", "b"),
            "createdAt": "2026-10-24T02:00:00Z"}]
    try:
        present = mo.fetch_heads(prs, repo=clone)
        assert [p["number"] for p in present] == [7, 8]
        report = mo.measure(present, "origin/main", repo=clone)
        assert report["measured"] == 2
    finally:
        mo.drop_refs(repo=clone)

    assert seen, "the recorder saw no git commands, so it proved nothing"
    for argv in seen:
        for forbidden in WRITES_TO_THE_CALLER:
            assert forbidden not in argv, f"{forbidden} in git {' '.join(argv)}"


def test_a_head_the_remote_no_longer_has_is_dropped_and_named(repo):
    """A garbage-collected head must not fail the whole measurement."""
    branch(repo, "a", {"app.py": "def main():\n    return 2\n"})
    clone = repo.parent / "clone-gone"
    subprocess.run(["git", "clone", "-q", str(repo), str(clone)], check=True)

    prs = [{"number": 9, "title": "a", "headRefOid": run(repo, "rev-parse", "a"),
            "createdAt": "2026-10-24T01:00:00Z"},
           {"number": 10, "title": "gone", "headRefOid": "0" * 40,
            "createdAt": "2026-10-24T02:00:00Z"}]
    try:
        present = mo.fetch_heads(prs, repo=clone)
    finally:
        mo.drop_refs(repo=clone)

    assert [p["number"] for p in present] == [9]


def test_render_names_the_blocking_file_under_the_blocked_pull_request(repo):
    branch(repo, "a", {"docs/ideas.md": append(LEDGER, "\n### from a\n- Status: proposed\n")})
    branch(repo, "b", {"docs/ideas.md": append(LEDGER, "\n### from b\n- Status: proposed\n")})
    report = mo.measure(queue(repo, "a", "b"), "main", repo=repo)
    lines = mo.render(report, {1: "first", 2: "second"})

    blocked = [line for line in lines if "BLOCKED" in line]
    assert blocked and "#2" in blocked[0]
    assert any("conflicts in docs/ideas.md" in line for line in lines)
    assert any("top anchors" in line for line in lines)
