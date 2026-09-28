"""The board client, against a board that is not the company's.

Every test here runs a real HTTP server on localhost implementing the six
routes `docs/standards/pm.md` §14 documents, including the two places the live
board differs from that documentation (a move needs `seat`, and a move takes
only `column_id`). Nothing here touches the network or the company board: run
reports are append-only and undeletable, so a suite that posted to the real
board would leave a row behind on every green run.
"""

from __future__ import annotations

import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from tools import board


# --------------------------------------------------------------------------
# A board, in fifty lines
# --------------------------------------------------------------------------

COLUMNS = [
    {"id": "c-1", "name": "Backlog", "position": 1},
    {"id": "c-2", "name": "This sprint", "position": 2},
    {"id": "c-3", "name": "In progress", "position": 3},
    {"id": "c-4", "name": "Review", "position": 4},
    {"id": "c-5", "name": "Done", "position": 5},
]


def fresh_state():
    return {
        "company": {"id": "co-1", "name": "alexandria", "display_name": "Library of Alexandria"},
        "columns": [dict(c) for c in COLUMNS],
        "sprint": {"id": "s-1", "name": "sprint-2026-09-28", "starts_on": "2026-09-28",
                   "ends_on": "2026-10-04", "status": "open"},
        "items": [
            {"id": "i-1", "title": "Drain the reading queue", "body": "", "horizon": "now",
             "seat": "engineer", "column_id": "c-3", "column_name": "In progress", "comments": []},
            {"id": "i-2", "title": "Ship the pricing page", "body": "", "horizon": "next",
             "seat": "frontend", "column_id": "c-2", "column_name": "This sprint", "comments": []},
        ],
        "runs": [],
        "calls": [],
    }


class Handler(BaseHTTPRequestHandler):
    state: dict = {}

    def log_message(self, *a):  # keep pytest's output clean
        pass

    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        if self.headers.get("Authorization") != "Bearer test-token":
            self._send(401, {"error": "unauthorized"})
            return False
        return True

    def do_GET(self):
        if not self._authorized():
            return
        path, _, query = self.path.partition("?")
        args = urllib.parse.parse_qs(query)
        self.state["calls"].append(("GET", path, args))
        if path == "/api/board/alexandria":
            return self._send(200, {k: v for k, v in self.state.items() if k != "calls"})
        if path.startswith("/api/items/"):
            if "company" not in args:
                return self._send(400, {"error": "company is required (?company=<name>)"})
            for item in self.state["items"]:
                if item["id"] == path.rsplit("/", 1)[-1]:
                    return self._send(200, item)
            return self._send(404, {"error": "no such item"})
        return self._send(404, {"error": "no such route"})

    def do_POST(self):
        if not self._authorized():
            return
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length) or b"{}")
        path = self.path.partition("?")[0]
        self.state["calls"].append(("POST", path, payload))
        if not payload.get("company"):
            return self._send(400, {"error": "no company: the runtime sets ASC_COMPANY"})
        if path == "/api/runs":
            if not payload.get("seat"):
                return self._send(400, {"error": "a run report needs a seat"})
            row = dict(payload, id="r-%d" % (len(self.state["runs"]) + 1))
            self.state["runs"].insert(0, row)
            return self._send(201, {"id": row["id"], "company": payload["company"]})
        if not payload.get("seat"):
            return self._send(400, {"error": "company and seat are required"})
        if path == "/api/items":
            if not payload.get("title"):
                return self._send(400, {"error": "an item needs a title"})
            row = dict(payload, id="i-%d" % (len(self.state["items"]) + 1), comments=[])
            self.state["items"].append(row)
            return self._send(201, {"id": row["id"]})
        if path.endswith("/move"):
            item_id = path.split("/")[3]
            column = payload.get("column_id")
            if not isinstance(column, str) or not column.startswith("c-"):
                return self._send(400, {"error": f"column_id is not a uuid: {column}"})
            for item in self.state["items"]:
                if item["id"] == item_id:
                    item["column_id"] = column
                    return self._send(200, {"id": item_id, "column_id": column})
            return self._send(404, {"error": "no such item"})
        if path.endswith("/comments"):
            if not payload.get("body"):
                return self._send(400, {"error": "a comment needs a body"})
            for item in self.state["items"]:
                if item["id"] == path.split("/")[3]:
                    item["comments"].append(payload)
                    return self._send(201, {"id": "cm-1"})
            return self._send(404, {"error": "no such item"})
        return self._send(404, {"error": "no such route"})

    # The live board is a stdlib http.server, so it answers everything else 501.


@pytest.fixture
def live_board(monkeypatch):
    state = fresh_state()
    Handler.state = state
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("BOARD_API_URL", "http://127.0.0.1:%d" % server.server_port)
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "alexandrapaiz/alexandria")
    monkeypatch.setenv("GITHUB_WORKFLOW", "engineer-agent")
    monkeypatch.delenv("ASC_SEAT", raising=False)
    monkeypatch.delenv("ASC_COMPANY", raising=False)
    try:
        yield state
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture
def no_git(monkeypatch):
    """No branch, no `gh`. A report still has to be postable."""
    monkeypatch.setattr(board, "current_branch", lambda root=".": "")
    monkeypatch.setattr(board, "pr_for_branch", lambda branch: None)


# --------------------------------------------------------------------------
# The pure core
# --------------------------------------------------------------------------


def test_seat_comes_from_the_workflow_name():
    assert board.seat_from_workflow("engineer-agent") == "engineer"
    assert board.seat_from_workflow("pm-agent") == "pm"
    assert board.seat_from_workflow("") == ""


def test_company_comes_from_the_repository_name():
    assert board.company_from_repo("alexandrapaiz/alexandria") == "alexandria"
    assert board.company_from_repo("") == ""


def test_result_line_prefers_the_first_bullet():
    body = "# Heading\n\nSome prose.\n\n- **The first bullet** is the summary\n- the second\n"
    assert board.result_line(body, "the title") == "The first bullet is the summary"


def test_result_line_falls_back_to_the_title():
    assert board.result_line("just prose, no bullets", "the title") == "the title"


def test_result_line_is_bounded():
    assert len(board.result_line("- " + "x" * 500, "t", limit=40)) == 40


def test_resolve_column_is_case_insensitive():
    assert board.resolve_column({"columns": COLUMNS}, "in progress") == "c-3"
    assert board.resolve_column({"columns": COLUMNS}, "  Review ") == "c-4"


def test_resolve_column_names_the_columns_it_has():
    with pytest.raises(board.BoardError) as exc:
        board.resolve_column({"columns": COLUMNS}, "Doing")
    assert "'Doing'" in str(exc.value)
    assert "'In progress'" in str(exc.value)


def test_render_shows_every_column_including_the_empty_ones():
    out = board.render(fresh_state())
    for column in COLUMNS:
        assert column["name"] in out
    assert "sprint-2026-09-28" in out
    assert "Drain the reading queue" in out
    assert "2 items in 5 columns" in out


def test_render_filtered_by_seat_drops_the_other_seats_items():
    out = board.render(fresh_state(), seat="engineer")
    assert "Drain the reading queue" in out
    assert "Ship the pricing page" not in out


def test_render_says_when_an_item_is_in_no_column_it_declares():
    state = fresh_state()
    state["items"][0]["column_id"] = "c-99"
    out = board.render(state)
    assert "in no column this board declares  (1)" in out
    assert "Drain the reading queue" in out


def test_render_says_no_runs_rather_than_nothing():
    assert "0 runs on this board" in board.render(fresh_state())


# --------------------------------------------------------------------------
# The run report's payload
# --------------------------------------------------------------------------


class Args:
    def __init__(self, **kw):
        defaults = dict(status="success", seat=None, company=None, report=None, branch=None,
                        started_at=None, ended_at=None, turns=None, model=None, item=[],
                        dry_run=False, id=None, title=None, body="", horizon="now", column=None)
        defaults.update(kw)
        for key, value in defaults.items():
            setattr(self, key, value)


ENV = {
    "GITHUB_WORKFLOW": "engineer-agent",
    "GITHUB_REPOSITORY": "alexandrapaiz/alexandria",
    "GITHUB_RUN_ID": "36366360908",
    "GITHUB_EVENT_NAME": "schedule",
    "GITHUB_SERVER_URL": "https://github.com",
}


def test_run_payload_derives_everything_from_one_status():
    payload = board.run_payload(ENV, Args(), branch="engineer/2026-09-28-x",
                               pr={"url": "https://github.com/a/b/pull/127", "title": "t",
                                   "body": "- the one line\n"})
    assert payload["seat"] == "engineer"
    assert payload["company"] == "alexandria"
    assert payload["exit"] == "success"
    assert payload["trigger"] == "schedule"
    assert payload["repo"] == "alexandrapaiz/alexandria"
    assert payload["run_url"] == "https://github.com/alexandrapaiz/alexandria/actions/runs/36366360908"
    assert payload["pr_url"] == "https://github.com/a/b/pull/127"
    assert payload["report"] == "the one line"


def test_run_payload_names_the_branch_when_there_is_no_pull_request():
    payload = board.run_payload(ENV, Args(), branch="engineer/2026-09-28-x", pr=None)
    assert payload["report"] == "no pull request on engineer/2026-09-28-x"
    assert "pr_url" not in payload


def test_run_payload_carries_the_items_a_run_worked_on():
    payload = board.run_payload(ENV, Args(item=["i-1", "i-2"]), branch="", pr=None)
    assert payload["item_ids"] == ["i-1", "i-2"]


def test_run_payload_prefers_an_explicit_report_over_the_pull_request():
    payload = board.run_payload(ENV, Args(report="mine"), branch="b",
                                pr={"url": "u", "title": "t", "body": "- theirs"})
    assert payload["report"] == "mine"


def test_run_payload_refuses_a_report_with_no_seat():
    with pytest.raises(board.BoardError) as exc:
        board.run_payload({"GITHUB_REPOSITORY": "a/b"}, Args(), branch="", pr=None)
    assert "needs a seat" in str(exc.value)


def test_run_payload_omits_what_it_was_not_told():
    payload = board.run_payload(ENV, Args(), branch="", pr=None)
    for absent in ("turns", "model", "started_at", "ended_at", "item_ids"):
        assert absent not in payload


def test_run_payload_takes_a_seat_from_asc_seat_on_the_host():
    payload = board.run_payload(dict(ENV, ASC_SEAT="skill", GITHUB_WORKFLOW=""), Args(),
                                branch="", pr=None)
    assert payload["seat"] == "skill"


# --------------------------------------------------------------------------
# The wire
# --------------------------------------------------------------------------


def test_show_reads_the_live_board(live_board, capsys):
    assert board.main(["show"]) == 0
    out = capsys.readouterr().out
    assert "Library of Alexandria" in out
    assert "Drain the reading queue" in out


def test_show_json_is_the_board_as_the_api_returns_it(live_board, capsys):
    assert board.main(["show", "--json"]) == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["company"]["name"] == "alexandria"
    assert len(parsed["items"]) == 2


def test_get_sends_the_company_as_a_query_parameter(live_board, capsys):
    assert board.main(["get", "--id", "i-1"]) == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["title"] == "Drain the reading queue"
    method, path, args = live_board["calls"][-1]
    assert (method, path) == ("GET", "/api/items/i-1")
    assert args["company"] == ["alexandria"]


def test_item_creates_one_and_sends_company_and_seat(live_board, capsys):
    assert board.main(["item", "--title", "A new thing", "--horizon", "later"]) == 0
    assert "created i-3" in capsys.readouterr().out
    _, path, payload = live_board["calls"][-1]
    assert path == "/api/items"
    assert payload == {"company": "alexandria", "seat": "engineer",
                       "title": "A new thing", "horizon": "later"}


def test_item_resolves_a_column_name_when_given_one(live_board):
    assert board.main(["item", "--title", "x", "--column", "Review"]) == 0
    _, path, payload = live_board["calls"][-1]
    assert payload["column_id"] == "c-4"


def test_move_resolves_the_column_and_sends_the_seat_the_board_requires(live_board, capsys):
    assert board.main(["move", "--id", "i-1", "--column", "Done"]) == 0
    assert "moved i-1 to Done" in capsys.readouterr().out
    _, path, payload = live_board["calls"][-1]
    assert path == "/api/items/i-1/move"
    assert payload == {"company": "alexandria", "seat": "engineer", "column_id": "c-5"}
    assert [i for i in live_board["items"] if i["id"] == "i-1"][0]["column_id"] == "c-5"


def test_move_to_a_column_that_does_not_exist_never_reaches_the_board(live_board, capsys):
    assert board.main(["move", "--id", "i-1", "--column", "Doing"]) == 2
    assert "no column named 'Doing'" in capsys.readouterr().err
    assert not any(m == "POST" for m, _, _ in live_board["calls"])


def test_comment_posts_the_body(live_board, capsys):
    assert board.main(["comment", "--id", "i-1", "--body", "shipped in #127"]) == 0
    assert "commented on i-1" in capsys.readouterr().out
    assert live_board["items"][0]["comments"][0]["body"] == "shipped in #127"


def test_report_posts_one_run(live_board, no_git, capsys):
    assert board.main(["report", "--status", "success"]) == 0
    assert "reported r-1 for engineer" in capsys.readouterr().out
    assert live_board["runs"][0]["exit"] == "success"
    assert live_board["runs"][0]["seat"] == "engineer"


def test_report_dry_run_posts_nothing(live_board, no_git, capsys):
    assert board.main(["report", "--status", "failure", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "would POST /api/runs" in out
    assert json.loads(out.split("would POST")[0])["exit"] == "failure"
    assert live_board["runs"] == []


def test_report_never_fails_the_run_when_the_board_refuses(live_board, no_git, capsys, monkeypatch):
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "the-wrong-token")
    assert board.main(["report", "--status", "success"]) == 0
    assert "::warning::board:" in capsys.readouterr().out
    assert live_board["runs"] == []


def test_a_write_that_is_not_a_report_does_fail_loudly(live_board, capsys, monkeypatch):
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "the-wrong-token")
    assert board.main(["comment", "--id", "i-1", "--body", "x"]) == 2
    assert "board said 401" in capsys.readouterr().err


def test_the_token_never_appears_in_an_error(live_board, capsys, monkeypatch):
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "sk-not-in-the-log")
    board.main(["comment", "--id", "i-1", "--body", "x"])
    captured = capsys.readouterr()
    assert "sk-not-in-the-log" not in captured.out + captured.err


def test_the_board_quotes_its_own_refusal(live_board, capsys):
    assert board.main(["get", "--id", "nope"]) == 2
    assert "no such item" in capsys.readouterr().err


def test_no_board_url_says_which_variable_is_missing(monkeypatch, capsys):
    monkeypatch.delenv("BOARD_API_URL", raising=False)
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "t")
    assert board.main(["show"]) == 2
    assert "BOARD_API_URL is not set" in capsys.readouterr().err


def test_no_token_says_so_before_spending_a_request(monkeypatch, capsys):
    monkeypatch.setenv("BOARD_API_URL", "http://127.0.0.1:1")
    monkeypatch.delenv("BOARD_RUNTIME_TOKEN", raising=False)
    assert board.main(["show"]) == 2
    assert "BOARD_RUNTIME_TOKEN is not set" in capsys.readouterr().err


def test_an_unreachable_board_is_an_error_not_a_traceback(monkeypatch, capsys):
    monkeypatch.setenv("BOARD_API_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "t")
    assert board.main(["show"]) == 2
    assert "board unreachable" in capsys.readouterr().err


def test_a_dry_run_needs_no_board_at_all(monkeypatch, capsys):
    monkeypatch.setenv("BOARD_API_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "t")
    monkeypatch.setenv("GITHUB_REPOSITORY", "alexandrapaiz/alexandria")
    assert board.main(["--seat", "engineer", "move", "--id", "i-1",
                       "--column", "Done", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "would POST /api/items/i-1/move" in out
    assert "unresolved" in out


# --------------------------------------------------------------------------
# The permission line, enforced by absence
# --------------------------------------------------------------------------


@pytest.mark.parametrize("forbidden", ["company", "sprint", "column", "view"])
def test_there_is_no_command_that_creates_a_company_sprint_column_or_view(forbidden):
    with pytest.raises(SystemExit):
        board.build_parser().parse_args([forbidden, "--name", "x"])
