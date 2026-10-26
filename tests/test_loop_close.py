"""Does the self-improvement loop close on the deploy, and never on the merge.

Run with `python3 -m pytest tests/test_loop_close.py -q`.

`tools/loop_close.py` is sprint-2026-10-26 item 4. The only self-improvement
proposal this product has ever merged changed `prompts/triage.md` on
2026-10-05 and the triage job went on reading the prompt of 2026-09-29 for
twelve days, with 8,861 rows judged against the old one
(`INC-2026-10-12-meta-review-proposal-merged-never-deployed`). The merge was
the loop's ending and the merge bought nothing, so the ending moved.

Everything here runs against a real git repository in a temporary directory,
built by `tests/test_deploy_drift.py`'s own fixture, because the question this
file asks is an ancestry question and a mocked `git merge-base` would test the
mock. No network, no database, no board: the board is a recording double and
the pull request facts arrive as data the way `--proposals` passes them.
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

import test_deploy_drift as drift  # noqa: E402  the fixture, not the tests

from pipeline import runtime_sha as rs  # noqa: E402
from tools import delivery_health as dh  # noqa: E402
from tools import loop_close as lc  # noqa: E402

UTC = timezone.utc
NOW = datetime.now(UTC)


def _sha(repo: Path, rev: str) -> str:
    status, out = dh._git(repo, "rev-parse", rev)
    assert status == 0, out
    return out


def _deploy(repo: Path, app: str, commit: str, first_seen: datetime) -> dict:
    """A `deploy_runtime` entry for the image built from one commit."""
    cache: dict[str, str] = {}
    sha = dh._digest_at(repo, app, _sha(repo, commit), cache)
    assert sha, f"the fixture could not be digested at {commit}"
    return {app: {"runtime_sha": sha, "recorded_at": NOW,
                  "first_seen_at": first_seen, "notified_at": None}}


def _proposal(merge_commit: str, files: list[str], merged_at: datetime,
              pid: int = 1) -> dict:
    return {"id": pid, "pr_url": f"https://example.invalid/pull/{pid}",
            "merged": True, "merge_commit": merge_commit,
            "merged_at": merged_at.isoformat(), "files": files}


# ------------------------------------------------------- the three live states


def test_a_merge_the_running_image_contains_is_live():
    """The deploy happened after the merge, so the loop has actually closed."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal"),
            ("pipeline/triage.py", "a later, unrelated commit"),
        ], base_days_ago=20)
        merge = _sha(repo, "HEAD~1")
        deploy = _deploy(repo, "triage", "HEAD", NOW - timedelta(days=2))

        out = lc.judge([_proposal(merge, ["prompts/triage.md"],
                                  NOW - timedelta(days=19))], deploy, repo)

        assert out["verdict"] == "ok"
        assert out["proposals"][0]["state"] == lc.LIVE


def test_a_merge_the_running_image_does_not_contain_is_dark():
    """The state that used to be called done, and the only one worth a card."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal"),
        ], base_days_ago=20)
        deploy = _deploy(repo, "triage", "HEAD~1", NOW - timedelta(days=20))

        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"],
                                  NOW - timedelta(days=19))], deploy, repo)

        assert out["verdict"] == "failing"
        item = out["proposals"][0]
        assert item["state"] == lc.DARK
        assert "triage has not deployed it" in item["why"]


def test_an_unmerged_proposal_is_open_and_not_a_finding():
    """A loop still running is not a loop that failed to close."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3)
        out = lc.judge([{"id": 7, "pr_url": "https://example.invalid/pull/7",
                         "merged": False}],
                       _deploy(repo, "triage", "HEAD", NOW), repo)
        assert out["proposals"][0]["state"] == lc.OPEN
        assert out["verdict"] == "ok"


# ------------------------------------------------- what it refuses to decide


def test_an_app_that_never_reported_is_unknown_and_not_dark():
    """No running digest is no evidence, and no evidence is not a failure."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=9)
        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW)],
                       {}, repo)
        assert out["proposals"][0]["state"] == lc.UNKNOWN
        assert out["verdict"] == lc.UNKNOWN


def test_a_digest_matching_nothing_in_history_is_unknown():
    """A deploy built from code this checkout does not hold cannot be placed."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=9)
        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW)],
                       {"triage": {"runtime_sha": "ffffffffffff",
                                   "recorded_at": NOW, "first_seen_at": NOW,
                                   "notified_at": None}}, repo)
        assert out["proposals"][0]["state"] == lc.UNKNOWN


def test_a_merged_proposal_with_no_merge_commit_is_unknown():
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3)
        out = lc.judge([{"id": 1, "pr_url": "u", "merged": True,
                         "files": ["prompts/triage.md"]}],
                       _deploy(repo, "triage", "HEAD", NOW), repo)
        assert out["proposals"][0]["state"] == lc.UNKNOWN


def test_an_unplaceable_app_outranks_a_dark_one():
    """Order of safety: a close cannot be taken back, so one unknown stops it.

    The mixed case, because a verdict that aggregates per-item states and is
    only ever tested with one state at a time is the defect the ledger entry
    of 2026-10-24 names.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "one proposal"),
            ("prompts/interpret.md", "another proposal"),
        ], base_days_ago=20)
        deploy = {**_deploy(repo, "triage", "HEAD~2", NOW - timedelta(days=20))}

        out = lc.judge([
            _proposal(_sha(repo, "HEAD~1"), ["prompts/triage.md"], NOW, pid=1),
            _proposal(_sha(repo, "HEAD"), ["prompts/interpret.md"], NOW, pid=2),
        ], deploy, repo)

        assert [p["state"] for p in out["proposals"]] == [lc.DARK, lc.UNKNOWN]
        assert out["verdict"] == lc.UNKNOWN, "an unknown anywhere stops the close"


def test_one_dark_reader_makes_the_whole_proposal_dark():
    """Two files, one deployed and one not, is not half done."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal, part one"),
            ("prompts/interpret.md", "the proposal, part two"),
        ], base_days_ago=20)
        deploy = {**_deploy(repo, "triage", "HEAD", NOW),
                  **_deploy(repo, "interpret", "HEAD~2", NOW)}

        out = lc.judge([_proposal(_sha(repo, "HEAD"),
                                  ["prompts/triage.md", "prompts/interpret.md"],
                                  NOW)], deploy, repo)

        item = out["proposals"][0]
        assert item["state"] == lc.DARK
        assert {p["app"] for p in item["pairs"]} == {"triage", "interpret"}


def test_a_file_no_image_adds_has_no_deploy_to_confirm():
    """`prompts/pm-agent.md` is a charter, not a prompt any job reads."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3,
                                     extra=["prompts/pm-agent.md"])
        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["prompts/pm-agent.md"], NOW)],
                       _deploy(repo, "triage", "HEAD", NOW), repo)
        assert out["proposals"][0]["state"] == lc.NO_READER


def test_a_pull_request_that_changed_no_targetable_file_is_no_reader():
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3)
        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["pipeline/triage.py"], NOW)],
                       _deploy(repo, "triage", "HEAD", NOW), repo)
        assert out["proposals"][0]["state"] == lc.NO_READER


def test_a_proposal_that_smuggled_code_past_the_regex_says_so():
    """Off-target files are reported rather than averaged into the verdict."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=9)
        out = lc.judge([_proposal(_sha(repo, "HEAD"),
                                  ["prompts/triage.md", "pipeline/llm.py"], NOW)],
                       _deploy(repo, "triage", "HEAD", NOW), repo)
        assert out["proposals"][0]["off_target"] == ["pipeline/llm.py"]


# ----------------------------------------------------------- the dark window


def test_the_dark_window_is_measured_to_the_image_that_is_running():
    """Merged on day 0, the running image first seen on day 10, so ten days."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=30)
        merged = NOW - timedelta(days=20)
        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], merged)],
                       _deploy(repo, "triage", "HEAD", merged + timedelta(days=10)),
                       repo)
        item = out["proposals"][0]
        assert item["state"] == lc.LIVE
        assert item["dark_days"] == pytest.approx(10.0, abs=0.1)
        assert "at most 10.0 days" in item["why"]


def test_the_window_is_a_bound_and_not_a_measurement():
    """`live_no_later_than` is the name, because an earlier image may have had it."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=9)
        seen = NOW - timedelta(days=1)
        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"],
                                  NOW - timedelta(days=5))],
                       _deploy(repo, "triage", "HEAD", seen), repo)
        assert out["proposals"][0]["live_no_later_than"].startswith(
            seen.isoformat()[:16])


# ------------------------------------------- which app reads what, and nothing hand-kept


def test_every_file_propose_change_can_target_has_a_reader_or_is_named():
    """The real repository: each targetable prompt maps to exactly one image.

    Derived rather than asserted as a table, so the day a prompt moves between
    images this test reads the new truth instead of the old one. What it pins
    is the invariant that matters: no prompt a job reads is read by two jobs,
    because a proposal with two readers is only live when both have deployed
    and that is a rule nobody has needed yet.
    """
    seen: dict[str, list[str]] = {}
    for app in rs.APPS:
        for key, _ in rs.local_entries(app, ROOT):
            if key.startswith("prompts/") or key == "sources.yaml":
                seen.setdefault(key, []).append(app)
    assert seen, "no app mounts a prompt, which cannot be right"
    for path, apps in seen.items():
        assert len(apps) == 1, f"{path} is read by {apps}, which judge() allows " \
                               f"and nothing has ever exercised"


def test_apps_reading_comes_from_the_manifest_and_not_from_a_list():
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3)
        assert lc.apps_reading("prompts/triage.md", repo, "HEAD") == ["triage"]
        assert lc.apps_reading("sources.yaml", repo, "HEAD") == ["ingest"]
        assert lc.apps_reading("docs/vision.md", repo, "HEAD") == []


def test_the_targetable_set_agrees_with_the_regex_in_propose_change():
    """A second copy of a rule drifts, so this is the check that it has not."""
    source = (ROOT / "mcp" / "server.py").read_text(encoding="utf-8")
    assert r"^(prompts/[a-z0-9_-]+\.md|sources\.yaml)$" in source
    inside, outside = lc.targets(["prompts/triage.md", "sources.yaml",
                                  "pipeline/llm.py", "skills/x/SKILL.md"])
    assert inside == ["prompts/triage.md", "sources.yaml"]
    assert outside == ["pipeline/llm.py", "skills/x/SKILL.md"]


# ----------------------------------------------------------------- the card


def test_the_card_names_the_app_the_commit_and_the_command_that_closes_it():
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        out = lc.judge([{**_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW),
                         "pr_url": "https://github.com/x/y/pull/451"}],
                       _deploy(repo, "triage", "HEAD~1", NOW), repo)
        title, body = lc.card_text(out["proposals"][0])
        assert title == "Self-improvement: #451 merged and is not running"
        assert "prompts/triage.md" in body
        assert "modal deploy pipeline/triage.py" in body
        assert "`triage` is on `" in body


class RecordingBoard:
    """The board, as a double that remembers what was asked of it."""

    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def api(self, path, method="GET", payload=None, env=None, opener=None):
        self.calls.append((method, path, payload))
        if method == "GET":
            return self.payload
        return {"id": "card-1"}

    @staticmethod
    def resolve_column(board, name):
        return "col-1"


def _dark(repo: Path) -> list[dict]:
    out = lc.judge([{**_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW),
                     "pr_url": "https://github.com/x/y/pull/451"}],
                   _deploy(repo, "triage", "HEAD~1", NOW), repo)
    return out["proposals"]


def test_a_dark_proposal_earns_one_card(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        double = RecordingBoard({"items": [], "columns": [
            {"id": "col-1", "name": "This sprint"}]})
        monkeypatch.setattr("tools.board.api", double.api)
        monkeypatch.setattr("tools.board.resolve_column", double.resolve_column)

        done = lc.post(_dark(repo), NOW)

        assert [d["action"] for d in done] == ["created"]
        posts = [c for c in double.calls if c[0] == "POST"]
        assert len(posts) == 1 and posts[0][1] == "/api/items"


def test_the_same_card_is_not_posted_twice(monkeypatch):
    """A daily schedule on an eleven-day drift costs the board one card."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        existing = {"id": "c1", "created_at": NOW.isoformat(),
                    "title": "Self-improvement: #451 merged and is not running",
                    "comments": []}
        double = RecordingBoard({"items": [existing], "columns": []})
        monkeypatch.setattr("tools.board.api", double.api)

        done = lc.post(_dark(repo), NOW)

        assert done[0]["action"] == "already on the board"
        assert not [c for c in double.calls if c[0] == "POST"]


def test_a_card_left_standing_is_nudged_the_next_day(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        existing = {"id": "c1",
                    "created_at": (NOW - timedelta(days=2)).isoformat(),
                    "title": "Self-improvement: #451 merged and is not running",
                    "comments": []}
        double = RecordingBoard({"items": [existing], "columns": []})
        monkeypatch.setattr("tools.board.api", double.api)

        done = lc.post(_dark(repo), NOW)

        assert done[0]["action"] == "nudged"
        assert any("comments" in c[1] for c in double.calls if c[0] == "POST")


def test_a_live_proposal_puts_nothing_on_the_board(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        double = RecordingBoard({"items": [], "columns": []})
        monkeypatch.setattr("tools.board.api", double.api)
        out = lc.judge([_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW)],
                       _deploy(repo, "triage", "HEAD", NOW), repo)
        assert lc.post(out["proposals"], NOW) == []
        assert double.calls == []


# ---------------------------------------------------------------- the write


class RecordingConn:
    def __init__(self):
        self.statements = []
        self.commits = 0

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

    def commit(self):
        self.commits += 1


def test_only_a_live_proposal_is_closed():
    conn = RecordingConn()
    wrote = lc.close_live(conn, [
        {"id": 1, "state": lc.LIVE, "live_no_later_than": "2026-10-17T12:00:00+00:00"},
        {"id": 2, "state": lc.DARK},
        {"id": 3, "state": lc.UNKNOWN},
        {"id": 4, "state": lc.OPEN},
    ])
    assert [w["id"] for w in wrote] == [1]
    assert len(conn.statements) == 1 and conn.commits == 1
    assert conn.statements[0][1] == ("2026-10-17T12:00:00+00:00", 1)


def test_the_close_writes_live_at_and_never_at_the_merge():
    """The whole point, asserted on the SQL: `live_at` is what closes it."""
    assert "live_at = coalesce(%s, now())" in lc.CLOSE_SQL
    assert "live_at is null" in lc.CLOSE_SQL
    assert "live_at is null" in lc.PROPOSAL_SQL


def test_a_proposal_with_no_row_of_its_own_is_not_written():
    """`--proposals` and the `gh` fallback both produce rows with no id."""
    conn = RecordingConn()
    assert lc.close_live(conn, [{"id": None, "state": lc.LIVE}]) == []
    assert conn.statements == []


def test_the_schema_carries_the_column_the_close_writes():
    schema = (ROOT / "db" / "schema.sql").read_text(encoding="utf-8")
    assert "alter table promotions add column if not exists live_at timestamptz;" in schema


# ------------------------------------------------------------------ the CLI


def test_the_exit_code_says_which_of_the_three_answers_it_is(tmp_path, capsys):
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        receipt = tmp_path / "receipt.json"
        proposals = tmp_path / "proposals.json"
        proposals.write_text(json.dumps(
            [_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW)]))

        for commit, expected in (("HEAD", 0), ("HEAD~1", 1)):
            rows = _deploy(repo, "triage", commit, NOW)
            receipt.write_text(json.dumps({
                "receipt": "alexandria-delivery", "version": 6,
                "deploy": [{"app": "triage",
                            "runtime_sha": rows["triage"]["runtime_sha"],
                            "entrypoint": "pipeline/triage.py", "file_count": 1,
                            "recorded_at": NOW.isoformat(),
                            "first_seen_at": NOW.isoformat(),
                            "notified_at": None}]}))
            code = lc.main(["--proposals", str(proposals),
                            "--receipt", str(receipt), "--repo-root", str(repo)])
            assert code == expected, capsys.readouterr().out


def test_write_without_a_credential_closes_nothing_and_says_so(tmp_path, capsys,
                                                               monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3)
        proposals = tmp_path / "p.json"
        proposals.write_text(json.dumps([{"id": 1, "pr_url": "u", "merged": False}]))
        receipt = tmp_path / "r.json"
        receipt.write_text(json.dumps({"receipt": "alexandria-delivery",
                                       "version": 6, "deploy": []}))
        lc.main(["--proposals", str(proposals), "--receipt", str(receipt),
                 "--repo-root", str(repo), "--write"])
        assert "needs DATABASE_URL" in capsys.readouterr().err


def test_the_render_names_every_proposal_it_judged():
    out = lc.render({"verdict": "failing", "why": "one dark", "ref": "main",
                     "proposals": [{"state": lc.DARK, "pr_url": "u", "why": "w",
                                    "pairs": [{"app": "triage",
                                               "path": "prompts/triage.md",
                                               "state": lc.DARK}]}]})
    assert "FAILING" in out and "triage" in out and "prompts/triage.md" in out


def test_a_pull_request_url_yields_its_number():
    assert lc.pr_number("https://github.com/a/b/pull/451") == 451
    assert lc.pr_number("https://github.com/a/b/pull/451/") == 451
    assert lc.pr_number("not a url") is None


def test_an_unknown_commit_is_not_a_no():
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3)
        assert lc.contains(repo, "0" * 40, _sha(repo, "HEAD")) is None


def test_the_guard_declares_what_it_needs_from_the_runtime():
    """Ancestry over a grafted clone is wrong rather than unavailable."""
    assert lc.NEEDS["git_history"] == "full"


def test_no_proposals_at_all_is_ok_and_not_unknown():
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [], base_days_ago=3)
        out = lc.judge([], {}, repo)
        assert out["verdict"] == "ok"
        assert "no system_diff proposal is open" in out["why"]


def test_a_deploy_surface_that_could_not_be_read_is_unknown():
    out = lc.judge([{"id": 1, "merged": True}],
                   "deploy_runtime could not be read: no such table")
    assert out["verdict"] == lc.UNKNOWN
    assert "no such table" in out["why"]


# --------------------------------------------- the surface in the daily report


def test_loop_is_a_surface_of_the_daily_report_and_sits_after_deploy():
    """Every seat reads this report daily, which is why the finding goes in it."""
    assert "loop" in dh.ORDER
    assert dh.ORDER.index("loop") == dh.ORDER.index("deploy") + 1


def test_the_surface_reports_a_dark_proposal_as_failing(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        proposals = [{**_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW),
                      "pr_url": "https://github.com/x/y/pull/451"}]
        deploy = _deploy(repo, "triage", "HEAD~1", NOW)
        monkeypatch.setattr(lc, "gather", lambda *a, **k: (proposals, deploy))

        surface = dh.check_loop(repo)

        assert surface.name == "loop" and surface.state == dh.FAILING
        assert "pull/451" in surface.headline
        assert "bought nothing" in surface.headline


def test_the_surface_reports_a_live_proposal_as_ok(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("prompts/triage.md", "the proposal")], base_days_ago=20)
        monkeypatch.setattr(lc, "gather", lambda *a, **k: (
            [_proposal(_sha(repo, "HEAD"), ["prompts/triage.md"], NOW)],
            _deploy(repo, "triage", "HEAD", NOW)))
        assert dh.check_loop(repo).state == dh.OK


def test_the_surface_answers_unknown_rather_than_raising(monkeypatch):
    """A guard that can fail the report it lives in is worse than no guard."""
    def boom(*a, **k):
        raise RuntimeError("gh is not installed here")

    monkeypatch.setattr(lc, "gather", boom)
    surface = dh.check_loop(ROOT)
    assert surface.state == dh.UNKNOWN
    assert "gh is not installed here" in surface.headline


# ----------------------------------------------- how the pull request is read


def test_a_token_holder_reads_the_api_and_not_the_cli(monkeypatch):
    """The Modal job has `GITHUB_TOKEN` and no `gh` binary, so both doors exist."""
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    monkeypatch.setenv("GITHUB_REPO", "a/b")
    asked = []

    def fake(number, token, repo):
        asked.append((number, token, repo))
        return {"merged": True, "merge_commit": "abc", "merged_at": "x",
                "files": ["prompts/triage.md"]}

    monkeypatch.setattr(lc, "pr_facts_api", fake)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k:
                        pytest.fail("gh was run with a token in the environment"))

    got = lc.pr_facts("https://github.com/a/b/pull/451", ROOT)

    assert asked == [(451, "t", "a/b")]
    assert got["files"] == ["prompts/triage.md"]


def test_the_api_reader_asks_for_the_pull_request_and_its_files(monkeypatch):
    seen = []

    class Answer:
        def __init__(self, body):
            self.body = body

        def read(self):
            return self.body

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(request, timeout=None):
        seen.append(request.full_url)
        if request.full_url.endswith("/files?per_page=100"):
            return Answer(json.dumps([{"filename": "prompts/triage.md"}]).encode())
        return Answer(json.dumps({"merged_at": "2026-10-05T04:33:28Z",
                                  "merge_commit_sha": "fa029bf"}).encode())

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    got = lc.pr_facts_api(451, "t", "a/b")

    assert got == {"merged": True, "merge_commit": "fa029bf",
                   "merged_at": "2026-10-05T04:33:28Z",
                   "files": ["prompts/triage.md"]}
    assert seen == ["https://api.github.com/repos/a/b/pulls/451",
                    "https://api.github.com/repos/a/b/pulls/451/files?per_page=100"]


def test_an_unreachable_api_is_a_why_and_never_a_merge(monkeypatch):
    import urllib.error
    import urllib.request

    def boom(request, timeout=None):
        raise urllib.error.URLError("no route")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    got = lc.pr_facts_api(451, "t", "a/b")
    assert got["merged"] is False and "no route" in got["why"]


def test_a_seat_with_no_token_falls_back_to_gh(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_REPO", raising=False)

    class Done:
        returncode = 0
        stdout = json.dumps({"state": "MERGED", "mergedAt": "2026-10-05T00:00:00Z",
                             "mergeCommit": {"oid": "fa029bf"},
                             "files": [{"path": "prompts/triage.md"}]})
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Done())
    got = lc.pr_facts("https://github.com/a/b/pull/451", ROOT)
    assert got["merged"] is True and got["merge_commit"] == "fa029bf"


def test_the_write_cannot_happen_where_the_judgement_does_and_the_file_says_so():
    """The constraint is load-bearing, so it is pinned rather than left in prose."""
    doc = lc.__doc__
    assert "No runtime in this organization holds all" in doc
    assert "promotions.live_at" in doc
