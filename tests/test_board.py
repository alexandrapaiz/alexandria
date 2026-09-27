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


# --- Ids come from the board, and a collision fails instead of merging ----


def test_the_numbering_starts_at_one_and_steps_past_hand_named_items():
    assert board.next_id([]) == "ALX-1"
    assert board.next_id(["board-store", "board-ui"]) == "ALX-1"
    assert board.next_id(["ALX-1", "board-ui", "ALX-9"]) == "ALX-10"


def test_the_numbering_ignores_things_that_only_look_like_an_id():
    assert board.next_id(["ALX-7x", "xALX-7", "alx-12", "ALX-", "ALX7"]) == "ALX-1"


def test_two_patches_of_one_id_share_a_claim_but_not_an_event_path():
    """The reason the claim file exists at all, stated as a test.

    Every patch is its own event, so two seats picking one id write two paths
    and neither write fails. The claim's path is the id alone, so the second
    one meets a path that is already there."""
    doing = item_event(id="ALX-4", status="doing")
    review = item_event(id="ALX-4", status="review")
    assert board.event_path(doing) != board.event_path(review)
    assert board.claim_path("ALX-4") == board.claim_path("ALX-4")
    assert board.claim_path("ALX-4") != board.claim_path("ALX-5")
    assert board.claim_path("ALX-4") == "board/ids/ALX-4.json"


def test_issuing_an_id_writes_one_file_named_by_the_id(monkeypatch):
    seen = {}

    def fake_put(repo, path, payload):
        seen["path"], seen["payload"] = path, payload
        return types.SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(board, "_contents_put", fake_put)
    outcome, record = board.claim_id("o/r", "ALX-4", by="engineer", at="2026-09-27T12:00:00Z")
    assert outcome == "claimed"
    assert seen["path"] == "board/ids/ALX-4.json"
    assert seen["payload"]["branch"] == "board", "a claim must never reach main"
    assert json.loads(base64.b64decode(seen["payload"]["content"])) == {
        "id": "ALX-4",
        "by": "engineer",
        "at": "2026-09-27T12:00:00Z",
    }
    assert record["by"] == "engineer"


def test_an_id_that_is_taken_is_answered_not_retried(monkeypatch):
    puts = []
    held = {"id": "ALX-7", "by": "frontend", "at": "2026-09-26T09:00:00Z"}

    def fake_put(repo, path, payload):
        puts.append(path)
        return types.SimpleNamespace(returncode=1, stdout="", stderr='422 "sha" wasn\'t supplied')

    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(board, "_contents_put", fake_put)
    monkeypatch.setattr(
        board,
        "_blob",
        lambda repo, path: {"sha": "abc", "content": base64.b64encode(json.dumps(held).encode()).decode()},
    )
    outcome, found = board.claim_id("o/r", "ALX-7", by="engineer")
    assert outcome == "exists"
    assert found["by"] == "frontend", "the claim says which seat holds the id"
    assert len(puts) == 1, "a taken id is an answer, not a race to retry"


def test_a_claim_blob_nobody_can_read_still_names_its_id(monkeypatch):
    monkeypatch.setattr(board, "ensure_ref", lambda repo, **kw: False)
    monkeypatch.setattr(
        board, "_contents_put", lambda *a: types.SimpleNamespace(returncode=1, stdout="", stderr="422")
    )
    monkeypatch.setattr(board, "_blob", lambda repo, path: {"sha": "abc", "content": "not base64 json"})
    outcome, found = board.claim_id("o/r", "ALX-7")
    assert (outcome, found["id"]) == ("exists", "ALX-7")


def test_the_issued_ids_come_from_the_ref_not_from_the_fold(monkeypatch):
    listing = [{"name": "ALX-1.json"}, {"name": "ALX-2.json"}, {"name": "README.md"}]
    monkeypatch.setattr(board, "gh_api", lambda *a, **kw: listing)
    assert board.list_claimed_ids("o/r") == ["ALX-1", "ALX-2"]
    monkeypatch.setattr(board, "gh_api", lambda *a, **kw: None)
    assert board.list_claimed_ids("o/r") == [], "no ids directory yet is an empty board"


def test_the_allocator_starts_above_the_highest_id_the_ref_holds(monkeypatch):
    tried = []
    monkeypatch.setattr(board, "list_claimed_ids", lambda repo: ["ALX-2", "ALX-11", "board-ui"])
    monkeypatch.setattr(
        board,
        "claim_id",
        lambda repo, item_id, **kw: (tried.append(item_id), ("claimed", {"id": item_id}))[1],
    )
    assert board.allocate_id("o/r")[0] == "ALX-12"
    assert tried == ["ALX-12"], "one listing and one create, not a walk up from one"


def test_the_allocator_steps_past_an_id_another_writer_took_first(monkeypatch):
    taken = {"ALX-1", "ALX-2"}
    tried = []

    def fake_claim(repo, item_id, by="seat", **kw):
        tried.append(item_id)
        if item_id in taken:
            return "exists", {"id": item_id, "by": "frontend"}
        return "claimed", {"id": item_id, "by": by}

    monkeypatch.setattr(board, "list_claimed_ids", lambda repo: [])
    monkeypatch.setattr(board, "claim_id", fake_claim)
    item_id, record = board.allocate_id("o/r", by="engineer")
    assert item_id == "ALX-3"
    assert tried == ["ALX-1", "ALX-2", "ALX-3"]
    assert record["by"] == "engineer"


def test_the_allocator_gives_up_loudly_rather_than_reusing_an_id(monkeypatch):
    monkeypatch.setattr(board, "list_claimed_ids", lambda repo: [])
    monkeypatch.setattr(board, "claim_id", lambda repo, item_id, **kw: ("exists", {"id": item_id}))
    with pytest.raises(RuntimeError) as exc:
        board.allocate_id("o/r", attempts=3)
    assert "ALX-3" in str(exc.value) and "board/ids" in str(exc.value)


def test_an_id_that_would_escape_the_ids_directory_is_refused():
    for bad in ("../../etc/passwd", "a/b", "ALX 7", "-leading", "x" * 65):
        assert board.validate(item_event(id=bad), VIEWS), f"{bad!r} must be refused"
    assert "board/ids" in board.validate(item_event(id="a/b"), VIEWS)[0]
    assert board.validate(item_event(id="ALX-7"), VIEWS) == []
    assert board.validate(item_event(id="board-ui"), VIEWS) == [], "the hand-named items still work"


def test_an_item_with_no_id_gets_one_from_the_board(monkeypatch, capsys):
    written = {}
    monkeypatch.setattr(board, "load_views", lambda *a, **kw: VIEWS)
    monkeypatch.setattr(board, "repo_slug", lambda: "o/r")
    monkeypatch.setattr(board, "allocate_id", lambda repo, by="seat", **kw: ("ALX-9", {"id": "ALX-9"}))
    monkeypatch.setattr(board, "write_event", lambda event, views, **kw: written.update(event) or "written")
    monkeypatch.setattr(board, "refresh_snapshot", lambda *a, **kw: None)
    assert board.main(["item", "--title", "Read-only board view", "--status", "next"]) == 0
    assert written["id"] == "ALX-9"
    assert "issued ALX-9" in capsys.readouterr().out


def test_a_hand_typed_id_another_seat_issued_says_so(monkeypatch, capsys):
    monkeypatch.setattr(board, "load_views", lambda *a, **kw: VIEWS)
    monkeypatch.setattr(board, "repo_slug", lambda: "o/r")
    monkeypatch.setattr(
        board,
        "claim_id",
        lambda repo, item_id, by="seat", **kw: ("exists", {"id": item_id, "by": "frontend", "at": "2026-09-26T09:00:00Z"}),
    )
    monkeypatch.setattr(board, "write_event", lambda *a, **kw: "written")
    monkeypatch.setattr(board, "refresh_snapshot", lambda *a, **kw: None)
    assert board.main(["item", "--id", "ALX-4", "--status", "doing", "--by", "engineer"]) == 0
    err = capsys.readouterr().err
    assert "issued by frontend" in err and "patches that item" in err


def test_a_dry_run_cannot_issue_an_id(monkeypatch):
    monkeypatch.setattr(board, "load_views", lambda *a, **kw: VIEWS)
    with pytest.raises(SystemExit) as exc:
        board.main(["item", "--dry-run", "--title", "something"])
    assert "cannot issue an id" in str(exc.value)


# --- The snapshot the site reads, and the swap that keeps it honest -------


def test_the_snapshot_carries_the_count_it_was_folded_from():
    events = [run_event(run_id="1"), item_event(id="ALX-1", status="doing")]
    snap = board.snapshot(board.fold(events), len(events), at="2026-09-27T12:00:00Z")
    assert snap["events"] == 2
    assert snap["items"]["ALX-1"]["status"] == "doing"
    assert snap["latest_run"]["engineer"]["run_id"] == "1"
    assert snap["generated"] == "2026-09-27T12:00:00Z"
    assert "source of truth" in snap["source"], "the file says what it is"


def test_the_snapshot_keeps_the_newest_runs_and_counts_the_rest():
    events = [run_event(run_id=str(n), at=f"2026-09-26T02:00:0{n}Z") for n in range(1, 6)]
    snap = board.snapshot(board.fold(events), len(events), runs=2)
    assert [r["run_id"] for r in snap["runs"]] == ["4", "5"], "the newest, in the log's order"
    assert (snap["runs_kept"], snap["runs_total"]) == (2, 5)


def test_the_first_snapshot_is_written_without_a_sha(monkeypatch):
    seen = {}

    def fake_put(repo, path, payload):
        seen["path"], seen["payload"] = path, payload
        return types.SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(board, "read_events", lambda **kw: [run_event()])
    monkeypatch.setattr(board, "_blob", lambda repo, path: None)
    monkeypatch.setattr(board, "_contents_put", fake_put)
    assert board.write_snapshot(repo="o/r") == {"events": 1, "runs": 1, "folds": 1}
    assert seen["path"] == "board/state.json"
    assert "sha" not in seen["payload"], "nothing to compare against on the first write"
    assert seen["payload"]["branch"] == "board", "the snapshot must never reach main"


def test_a_stale_sha_forces_a_refold_instead_of_an_overwrite(monkeypatch):
    """The one property that makes a mutable file safe in an append-only store.

    A writer that read the log before another writer appended to it is refused
    by the sha it carried, and it answers the refusal by reading the log again.
    So the event that beat it is in the snapshot it finally writes, rather than
    being dropped by it."""
    log = [run_event(run_id="1")]
    shas = iter(["stale", "fresh"])
    reads, puts = [], []

    def fake_read_events(**kw):
        reads.append(1)
        return list(log)

    def fake_put(repo, path, payload):
        puts.append(payload)
        if len(puts) == 1:
            log.append(run_event(seat="frontend", run_id="2"))
            return types.SimpleNamespace(returncode=1, stdout="", stderr="409 sha does not match")
        return types.SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(board, "read_events", fake_read_events)
    monkeypatch.setattr(board, "_blob", lambda repo, path: {"sha": next(shas)})
    monkeypatch.setattr(board, "_contents_put", fake_put)
    result = board.write_snapshot(repo="o/r", sleep=lambda s: None)
    assert len(reads) == 2, "the retry folded the log again rather than resending its body"
    assert [p["sha"] for p in puts] == ["stale", "fresh"]
    first = json.loads(base64.b64decode(puts[0]["content"]))
    second = json.loads(base64.b64decode(puts[1]["content"]))
    assert (first["events"], second["events"]) == (1, 2)
    assert "frontend" in second["latest_run"], "the event that beat us survived our write"
    assert result == {"events": 2, "runs": 2, "folds": 2}


def test_a_snapshot_that_will_not_write_raises_after_its_attempts(monkeypatch):
    monkeypatch.setattr(board, "read_events", lambda **kw: [run_event()])
    monkeypatch.setattr(board, "_blob", lambda repo, path: {"sha": "abc"})
    monkeypatch.setattr(
        board, "_contents_put", lambda *a: types.SimpleNamespace(returncode=1, stdout="", stderr="409")
    )
    with pytest.raises(RuntimeError) as exc:
        board.write_snapshot(repo="o/r", attempts=2, sleep=lambda s: None)
    assert "board/state.json" in str(exc.value)


def test_a_snapshot_that_cannot_be_written_leaves_the_event_standing(monkeypatch, capsys):
    monkeypatch.setattr(
        board, "write_snapshot", lambda **kw: (_ for _ in ()).throw(RuntimeError("no network"))
    )
    assert board.refresh_snapshot() is None
    err = capsys.readouterr().err
    assert "not refreshed" in err and "source of truth" in err
    with pytest.raises(RuntimeError):
        board.refresh_snapshot(strict=True)


def test_report_refreshes_the_snapshot_and_no_snapshot_leaves_it(monkeypatch):
    calls = []
    monkeypatch.setattr(board, "load_views", lambda *a, **kw: VIEWS)
    monkeypatch.setattr(board, "env_report", lambda *a, **kw: run_event())
    monkeypatch.setattr(board, "write_event", lambda *a, **kw: "written")
    monkeypatch.setattr(board, "refresh_snapshot", lambda **kw: calls.append(kw))
    board.main(["report", "--status", "success"])
    assert len(calls) == 1, "a report that lands refreshes the file the site reads"
    board.main(["report", "--status", "success", "--no-snapshot"])
    assert len(calls) == 1, "--no-snapshot leaves the file to the next writer"
