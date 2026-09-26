"""What the board promises, held by tests that touch no network.

    python3 -m pytest tests/test_board.py -q

The store's whole value is that a seat's report lands exactly once, that a
seat cannot invent a column or a view, and that a board outage never fails the
run that was reporting. Those three are the first three sections here.
"""

import base64
import importlib.util
import io
import json
import sys
import tarfile
import types
from pathlib import Path

import pytest

# Loaded by path, the way tests/test_check_registers.py loads its tool: nothing
# under tools/ is a package, and a stray __init__.py there would change how
# every other tool imports.
REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("board", REPO / "tools" / "board.py")
board = importlib.util.module_from_spec(_spec)
sys.modules["board"] = board
_spec.loader.exec_module(board)

VIEWS = {
    "columns": ["inbox", "next", "doing", "review", "done"],
    "views": {
        "board": {"title": "Board", "group_by": "status", "columns": ["inbox", "next", "doing"], "runs": 0},
        "seats": {"title": "By seat", "group_by": "assignee", "runs": 3},
    },
}


def run_event(seat="engineer", run_id="1", attempt=1, at="2026-09-26T02:00:00Z", **kw):
    return {
        "kind": "run",
        "at": at,
        "seat": seat,
        "run_id": run_id,
        "attempt": attempt,
        "status": "success",
        **kw,
    }


def item_event(id="board-ui", at="2026-09-26T02:00:00Z", **kw):
    return {"kind": "item", "at": at, "id": id, **kw}


# --- One report lands exactly once ---------------------------------------


def test_a_run_reports_to_the_same_path_every_time():
    """The path carries the run id and the attempt, so `if: always()` firing
    twice for one attempt cannot produce two rows."""
    first = board.event_path(run_event())
    assert first == board.event_path(run_event())
    assert first == "board/events/run/2026-09-26/engineer-1-1.json"


def test_two_seats_and_two_attempts_never_share_a_path():
    paths = {
        board.event_path(run_event(seat="engineer")),
        board.event_path(run_event(seat="frontend")),
        board.event_path(run_event(run_id="2")),
        board.event_path(run_event(attempt=2)),
    }
    assert len(paths) == 4


def test_two_different_item_patches_never_share_a_path():
    a = board.event_path(item_event(status="doing"))
    b = board.event_path(item_event(status="review"))
    assert a != b
    assert a == board.event_path(item_event(status="doing"))
    assert a.startswith("board/events/item/2026-09-26/")


def test_an_existing_path_is_a_success_not_a_retry(monkeypatch):
    calls = []

    def fake_run(argv, **kw):
        calls.append(argv)
        return types.SimpleNamespace(returncode=1, stdout="", stderr='422 "sha" wasn\'t supplied')

    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(board.subprocess, "run", fake_run)
    monkeypatch.setattr(board, "gh_api", lambda path, method="GET", payload=None, check=True: {"sha": "abc"})
    assert board.write_event(run_event(), VIEWS, repo="o/r") == "exists"
    assert len(calls) == 1, "an event already on the board is not retried"


def test_a_moved_ref_is_retried_then_succeeds(monkeypatch):
    attempts = []

    def fake_run(argv, **kw):
        attempts.append(argv)
        code = 0 if len(attempts) == 3 else 1
        return types.SimpleNamespace(returncode=code, stdout="{}", stderr="409 Conflict")

    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(board.subprocess, "run", fake_run)
    monkeypatch.setattr(board, "gh_api", lambda *a, **kw: None)
    assert board.write_event(run_event(), VIEWS, repo="o/r", sleep=lambda s: None) == "written"
    assert len(attempts) == 3


def test_the_write_is_a_contents_put_on_the_board_branch(monkeypatch):
    seen = {}

    def fake_run(argv, **kw):
        seen["argv"] = argv
        seen["payload"] = json.loads(kw["input"])
        return types.SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(board.subprocess, "run", fake_run)
    board.write_event(run_event(result="the board's own store"), VIEWS, repo="o/r")
    assert seen["argv"][:5] == ["gh", "api", "--method", "PUT", "repos/o/r/contents/board/events/run/2026-09-26/engineer-1-1.json"]
    assert seen["payload"]["branch"] == "board", "the write must never reach main"
    written = json.loads(base64.b64decode(seen["payload"]["content"]))
    assert written["result"] == "the board's own store"


# --- A seat cannot invent a column or a view -----------------------------


def test_an_item_status_outside_the_columns_is_refused():
    problems = board.validate(item_event(status="blocked"), VIEWS)
    assert problems and "not a column" in problems[0]
    assert "board/views.json" in problems[0], "the refusal names where columns are declared"


def test_every_declared_column_is_accepted():
    for column in VIEWS["columns"]:
        assert board.validate(item_event(status=column), VIEWS) == []


def test_a_view_that_does_not_exist_names_the_rule():
    with pytest.raises(SystemExit) as exc:
        board.resolve_view(VIEWS, "my-own-view")
    message = str(exc.value)
    assert "Seats do not create views" in message
    assert "board" in message and "seats" in message, "it lists the views that do exist"


def test_a_view_inherits_the_declared_columns_when_it_names_none():
    view = board.resolve_view(VIEWS, "seats")
    assert view["columns"] == VIEWS["columns"]
    assert view["group_by"] == "assignee"


def test_views_that_cannot_be_read_stop_the_write(tmp_path):
    with pytest.raises(SystemExit) as missing:
        board.load_views(root=tmp_path)
    assert "is missing" in str(missing.value)

    (tmp_path / "board").mkdir()
    (tmp_path / "board" / "views.json").write_text("{not json")
    with pytest.raises(SystemExit) as broken:
        board.load_views(root=tmp_path)
    assert "not valid JSON" in str(broken.value)

    (tmp_path / "board" / "views.json").write_text('{"views": {}}')
    with pytest.raises(SystemExit) as empty:
        board.load_views(root=tmp_path)
    assert "no columns" in str(empty.value)


def test_the_repository_ships_views_the_tool_can_read():
    views = board.load_views()
    assert views["columns"], "board/views.json on this branch declares columns"
    for name in views["views"]:
        assert board.resolve_view(views, name)["title"]


# --- A board outage never fails the run ----------------------------------


def test_report_swallows_a_broken_board_and_exits_zero(monkeypatch, capsys):
    monkeypatch.setattr(board, "load_views", lambda *a, **kw: VIEWS)
    monkeypatch.setattr(board, "env_report", lambda *a, **kw: run_event())
    monkeypatch.setattr(board, "write_event", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("no network")))
    assert board.main(["report", "--status", "success"]) == 0
    assert "not posted" in capsys.readouterr().err


def test_strict_report_fails_loudly(monkeypatch):
    monkeypatch.setattr(board, "load_views", lambda *a, **kw: VIEWS)
    monkeypatch.setattr(board, "env_report", lambda *a, **kw: run_event())
    monkeypatch.setattr(board, "write_event", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("no network")))
    with pytest.raises(RuntimeError):
        board.main(["report", "--status", "success", "--strict"])


def test_an_invalid_report_is_refused_before_it_is_written():
    with pytest.raises(SystemExit) as exc:
        board.write_event(run_event(status="green"), VIEWS, repo="o/r")
    assert "status must be one of" in str(exc.value)


def test_a_report_needs_a_seat_a_run_and_a_one_line_result():
    problems = board.validate({"kind": "run", "at": "2026-09-26T02:00:00Z", "status": "success",
                               "seat": "engineer", "run_id": "1", "result": "two\nlines"}, VIEWS)
    assert problems == ["result is one line"]
    missing = board.validate({"kind": "run", "at": "nope", "status": "success"}, VIEWS)
    assert any("ISO UTC" in p for p in missing)
    assert any("needs seat" in p for p in missing)
    assert any("needs run_id" in p for p in missing)


# --- The fold is the board's state --------------------------------------


def test_an_item_is_the_last_write_of_each_field():
    state = board.fold([
        item_event(at="2026-09-26T01:00:00Z", title="Read-only board view", status="inbox", assignee="frontend"),
        item_event(at="2026-09-26T03:00:00Z", status="doing"),
    ])
    item = state["items"]["board-ui"]
    assert item["status"] == "doing", "the later event wins"
    assert item["title"] == "Read-only board view", "a patch keeps what it did not mention"
    assert item["assignee"] == "frontend"
    assert item["events"] == 2 and item["updated"] == "2026-09-26T03:00:00Z"


def test_events_out_of_order_on_disk_still_fold_in_time_order():
    late = item_event(at="2026-09-26T09:00:00Z", status="done")
    early = item_event(at="2026-09-26T01:00:00Z", status="inbox")
    assert board.fold([late, early])["items"]["board-ui"]["status"] == "done"
    assert board.fold([early, late])["items"]["board-ui"]["status"] == "done"


def test_the_latest_run_per_seat_and_the_whole_fleet_log():
    state = board.fold([
        run_event(seat="engineer", run_id="1", at="2026-09-26T01:00:00Z", result="first"),
        run_event(seat="engineer", run_id="2", at="2026-09-26T05:00:00Z", result="second"),
        run_event(seat="frontend", run_id="3", at="2026-09-26T02:00:00Z"),
    ])
    assert state["latest_run"]["engineer"]["result"] == "second"
    assert len(state["runs"]) == 3, "the fleet log keeps every run, not just the latest"


# --- Rendering -----------------------------------------------------------


def test_the_board_prints_a_column_per_status_and_marks_the_empty_ones():
    state = board.fold([item_event(id="board-ui", title="Read-only board view",
                                   status="next", assignee="frontend")])
    text = board.render(state, board.resolve_view(VIEWS, "board"), VIEWS)
    assert "next  (1)" in text
    assert "inbox  (0)" in text
    assert "board-ui" in text and "frontend" in text
    assert "1 item in 5 columns, 0 runs" in text, "one item is not 1 items"


def test_an_item_no_column_holds_is_printed_rather_than_hidden():
    """A status dropped from views.json must not silently swallow its items."""
    state = board.fold([item_event(id="orphan", status="done", title="shipped")])
    text = board.render(state, board.resolve_view(VIEWS, "board"), VIEWS)
    assert "not in any column of this view  (1)" in text
    assert "orphan" in text


def test_the_runs_view_prints_the_newest_runs_first():
    state = board.fold([
        run_event(seat="engineer", run_id="1", at="2026-09-26T01:00:00Z", result="older"),
        run_event(seat="writer", run_id="2", at="2026-09-26T05:00:00Z", result="newer"),
    ])
    text = board.render(state, board.resolve_view(VIEWS, "seats"), VIEWS)
    assert text.index("newer") < text.index("older")
    assert "2 runs recorded" in text


def test_a_run_with_no_pull_request_says_so():
    state = board.fold([run_event(result="nothing worth shipping")])
    text = board.render(state, board.resolve_view(VIEWS, "seats"), VIEWS)
    assert "no PR" in text


# --- Filling a report in from the environment ---------------------------


def test_the_seat_the_run_and_the_url_come_from_the_actions_environment(monkeypatch):
    monkeypatch.setattr(board.subprocess, "run",
                        lambda argv, **kw: types.SimpleNamespace(returncode=1, stdout="", stderr=""))
    args = board.build_parser().parse_args(["report", "--status", "failure"])
    event = board.env_report({
        "GITHUB_WORKFLOW": "engineer-agent",
        "GITHUB_RUN_ID": "36207911573",
        "GITHUB_RUN_ATTEMPT": "2",
        "GITHUB_REPOSITORY": "alexandrapaiz/alexandria",
        "GITHUB_SERVER_URL": "https://github.com",
    }, args)
    assert event["seat"] == "engineer", "the workflow name minus the -agent suffix"
    assert event["run_id"] == "36207911573" and event["attempt"] == 2
    assert event["status"] == "failure"
    assert event["url"] == "https://github.com/alexandrapaiz/alexandria/actions/runs/36207911573"
    assert board.validate(event, VIEWS) == []


def test_the_branch_and_the_pull_request_are_derived_from_git(monkeypatch):
    def fake_run(argv, **kw):
        if "rev-parse" in argv:
            return types.SimpleNamespace(returncode=0, stdout="engineer/2026-09-26-board-store\n", stderr="")
        if argv[:3] == ["gh", "pr", "list"]:
            body = json.dumps({"number": 115, "title": "Engineer 2026-09-26", "url": "u",
                               "body": "Draft.\n\n- **Supersedes #110.** built on that branch\n- second\n"})
            return types.SimpleNamespace(returncode=0, stdout=body, stderr="")
        raise AssertionError(argv)

    monkeypatch.setattr(board.subprocess, "run", fake_run)
    args = board.build_parser().parse_args(["report", "--status", "success"])
    event = board.env_report({"GITHUB_WORKFLOW": "engineer-agent"}, args)
    assert event["branch"] == "engineer/2026-09-26-board-store"
    assert event["pr"] == 115
    assert event["result"] == "Supersedes #110. built on that branch"


def test_flags_beat_derivation(monkeypatch):
    monkeypatch.setattr(board.subprocess, "run",
                        lambda argv, **kw: (_ for _ in ()).throw(AssertionError("no subprocess needed")))
    args = board.build_parser().parse_args(
        ["report", "--status", "success", "--seat", "pm", "--run-id", "9", "--branch", "b",
         "--pr", "1", "--result", "said so on the command line"])
    event = board.env_report({}, args)
    assert (event["seat"], event["run_id"], event["pr"]) == ("pm", "9", 1)
    assert event["result"] == "said so on the command line"


def test_the_result_line_is_the_first_bullet_then_the_title():
    assert board.result_line("- **one** line here\n- two", "T") == "one line here"
    assert board.result_line("* bullet", "T") == "bullet"
    assert board.result_line("no bullets at all", "The title") == "The title"
    assert board.result_line("", "") == ""
    assert len(board.result_line("- " + "x" * 400, "T")) == 200


# --- Reading the ref -----------------------------------------------------


def _tar_of(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for name, text in files.items():
            raw = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
    return buf.getvalue()


def test_the_whole_board_is_read_in_one_git_call(monkeypatch):
    calls = []

    def fake_run(argv, **kw):
        calls.append(argv)
        if "archive" in argv:
            return types.SimpleNamespace(returncode=0, stderr=b"", stdout=_tar_of({
                "board/events/run/2026-09-26/engineer-1-1.json": json.dumps(run_event()),
                "board/events/item/2026-09-26/x-board-ui-ab.json": json.dumps(item_event(status="doing")),
                "board/events/run/2026-09-26/notes.txt": "ignored",
            }))
        return types.SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

    monkeypatch.setattr(board.subprocess, "run", fake_run)
    events = board.read_events()
    assert len(events) == 2
    assert sum(1 for c in calls if "archive" in c) == 1, "one subprocess for the whole log"


def test_a_board_ref_that_does_not_exist_yet_is_an_empty_board(monkeypatch):
    monkeypatch.setattr(board.subprocess, "run",
                        lambda argv, **kw: types.SimpleNamespace(returncode=128, stdout=b"", stderr=b"no such ref"))
    assert board.read_events() == []


def test_one_unreadable_file_does_not_take_the_board_down(monkeypatch, capsys):
    def fake_run(argv, **kw):
        if "archive" in argv:
            return types.SimpleNamespace(returncode=0, stderr=b"", stdout=_tar_of({
                "board/events/run/2026-09-26/good-1-1.json": json.dumps(run_event()),
                "board/events/run/2026-09-26/half-written.json": "{",
                "board/events/run/2026-09-26/wrong-shape.json": json.dumps({"kind": "note"}),
            }))
        return types.SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

    monkeypatch.setattr(board.subprocess, "run", fake_run)
    assert len(board.read_events()) == 1
    err = capsys.readouterr().err
    assert "half-written.json" in err and "wrong-shape.json" in err


# --- The ref itself ------------------------------------------------------


def test_the_board_ref_is_created_once_and_has_no_parent(monkeypatch):
    posts = []

    def fake_api(path, method="GET", payload=None, check=True):
        if method == "GET":
            return None  # the ref does not exist yet
        posts.append((path, payload))
        return {"sha": "deadbeef"}

    monkeypatch.setattr(board, "gh_api", fake_api)
    assert board.ensure_ref("o/r") is True
    paths = [p for p, _ in posts]
    assert paths == ["repos/o/r/git/trees", "repos/o/r/git/commits", "repos/o/r/git/refs"]
    commit = dict(posts[1][1])
    assert "parents" not in commit, "the board's history is orphan, so main never carries run reports"
    assert posts[2][1]["ref"] == "refs/heads/board"


def test_an_existing_ref_is_left_alone(monkeypatch):
    monkeypatch.setattr(board, "gh_api",
                        lambda path, method="GET", payload=None, check=True: {"ref": "refs/heads/board"})
    assert board.ensure_ref("o/r") is False


def test_a_long_result_stays_one_line_in_the_runs_view():
    state = board.fold([run_event(result="x" * 300)])
    text = board.render(state, board.resolve_view(VIEWS, "seats"), VIEWS)
    lines = [line for line in text.splitlines() if "success" in line]
    assert len(lines) == 1 and len(lines[0]) < 160


def test_update_replaces_a_stale_report_instead_of_leaving_it(monkeypatch):
    """A report posted before the PR description was final has to be fixable."""
    payloads = []

    def fake_run(argv, **kw):
        payload = json.loads(kw["input"])
        payloads.append(payload)
        # The API refuses a create against a path that exists, and accepts the
        # same call once it carries the blob's sha.
        code = 0 if "sha" in payload else 1
        return types.SimpleNamespace(returncode=code, stdout="{}", stderr="422 sha wasn't supplied")

    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(board.subprocess, "run", fake_run)
    monkeypatch.setattr(board, "gh_api", lambda *a, **kw: {"sha": "oldblob"})
    assert board.write_event(run_event(result="final"), VIEWS, repo="o/r", update=True) == "updated"
    assert payloads[-1]["sha"] == "oldblob"
    assert json.loads(base64.b64decode(payloads[-1]["content"]))["result"] == "final"


def test_without_update_the_first_report_stands(monkeypatch):
    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(board.subprocess, "run",
                        lambda argv, **kw: types.SimpleNamespace(returncode=1, stdout="", stderr="422"))
    monkeypatch.setattr(board, "gh_api", lambda *a, **kw: {"sha": "oldblob"})
    assert board.write_event(run_event(), VIEWS, repo="o/r", update=False) == "exists"


def test_plural():
    assert board.plural(0, "run") == "0 runs"
    assert board.plural(1, "run") == "1 run"
    assert board.plural(2, "item") == "2 items"


def test_every_agent_workflow_maps_to_a_declared_seat():
    """The step is `board.py report --status ...` in all twelve workflows, and
    the seat it records is the workflow's name minus `-agent`. If a thirteenth
    seat arrives, this fails until board/views.json knows the name, rather than
    that seat's runs landing under a name no view groups by."""
    import re

    workflows = sorted((REPO / ".github" / "workflows").glob("agent-*.yml"))
    assert len(workflows) == 12, "twelve seats, or this test's premise moved"
    derived = set()
    for path in workflows:
        name = re.search(r"^name:\s*(\S+)", path.read_text(), re.M).group(1)
        derived.add(re.sub(r"-agent$", "", name))
    assert derived == set(board.load_views()["seats"])
