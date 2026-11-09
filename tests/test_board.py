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
        # The bus. Three directed messages and one broadcast, which is the
        # shape this seat's real inbox had on 2026-10-24: one that is ours,
        # one that names our seat in another company, and one that names our
        # seat and no company at all and so could be either.
        "messages": [
            {"id": "m-1", "ts": "2026-10-24T13:15:05+00:00", "kind": "handoff",
             "from_company": "alexandria", "from_seat": "pm",
             "to_company": "alexandria", "to_seat": "engineer",
             "subject": "Build the detector", "body": "yours", "ref": None},
            {"id": "m-2", "ts": "2026-10-24T17:55:41+00:00", "kind": "done",
             "from_company": "alexandra-systems", "from_seat": "pm",
             "to_company": None, "to_seat": "engineer",
             "subject": "Both defects are merged", "body": "whose?", "ref": None},
            {"id": "m-3", "ts": "2026-10-24T12:00:00+00:00", "kind": "note",
             "from_company": "Ursa", "from_seat": "exo",
             "to_company": "Ursa", "to_seat": "engineer",
             "subject": "Another company's engineer", "body": "theirs", "ref": None},
            {"id": "m-4", "ts": "2026-10-24T11:00:00+00:00", "kind": "note",
             "from_company": "alexandra-systems", "from_seat": "chair:asc-host",
             "to_company": None, "to_seat": None,
             "subject": "Deployed HQ main", "body": "the room", "ref": None},
        ],
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
        if path == "/api/messages":
            # The live board filters by seat and company and returns the
            # broadcasts alongside, so the fake does the same. It deliberately
            # does NOT drop a message whose to_company is null, because that
            # is exactly the row the client has to judge for itself.
            seat = (args.get("to_seat") or [None])[0]
            company = (args.get("to_company") or [None])[0]
            if not seat and not company:
                # Unfiltered means the whole bus, which is how the live board
                # answers it: the skill seat found its lost message on
                # 2026-11-02 with exactly this query. The fake returned only
                # the broadcasts here until that run, so a reader of this fake
                # could not have written the roster check that needs it.
                rows = list(self.state["messages"])
            else:
                # Measured against the live board on 2026-11-02: a read with
                # both filters returns the broadcasts, the rows naming the
                # seat in ANY company, and the rows naming the company and no
                # seat. It does NOT return another seat's company mail. The
                # fake ORed on company until that run, which is wider than the
                # server and is why a wrong seat name still produced a
                # non-empty `theirs` here and an empty one in production.
                rows = [
                    m for m in self.state["messages"]
                    if (m["to_seat"] is None and m["to_company"] is None)
                    or (seat and m["to_seat"] == seat)
                    or (company and m["to_company"] == company and m["to_seat"] is None)
                ]
            limit = int((args.get("limit") or ["500"])[0])
            return self._send(200, {"messages": rows[:limit]})
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
        if path == "/api/messages":
            if payload.get("kind") not in board.MESSAGE_KINDS:
                return self._send(400, {"error": "kind must be one of %r" % (board.MESSAGE_KINDS,)})
            if not payload.get("subject"):
                return self._send(400, {"error": "a message needs a subject"})
            # The live board accepts to_seat with no to_company. That is the
            # whole reason the client refuses it, so the fake must accept it
            # too or the test would be proving the server's rule, not ours.
            row = dict(payload, id="m-%d" % (len(self.state["messages"]) + 1))
            self.state["messages"].append(row)
            # The live board answers a send with its own delivery receipt, and
            # the wake carries only the first `wake_limit` characters. The fake
            # computes the same three fields because a sender that cannot read
            # them cannot know what its reader did not get.
            body = payload.get("body") or ""
            wake_limit = 1500
            delivered = min(len(body), wake_limit)
            return self._send(201, {
                "id": row["id"], "body_chars": len(body),
                "body_delivered": delivered,
                "body_truncated": len(body) > wake_limit,
                "wake_limit": wake_limit,
            })
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
    assert payload["exit"] == 0
    assert payload["trigger"] == "schedule"
    assert payload["repo"] == "alexandrapaiz/alexandria"
    assert payload["run_url"] == "https://github.com/alexandrapaiz/alexandria/actions/runs/36366360908"
    assert payload["pr_url"] == "https://github.com/a/b/pull/127"
    assert payload["report"] == "the one line"


def test_every_status_the_parser_accepts_becomes_a_number_or_nothing():
    """The gate for the fault that made every run report fail.

    `INC-2026-10-16-every-run-report-fails-on-a-string-where-the-board-wants-a-
    number-and-the-error-blames-the-database`. The board stores `exit` as a
    number and this file sent GitHub's word, so the one field the workflow
    step exists to pass was the field the insert rejected, for every seat,
    silently, inside a green job. This test is cheap, it runs on every pull
    request, and it needs no board: a workflow vocabulary and a database
    column drifting apart is exactly the class that no live probe will catch
    until it is already in production.
    """
    for status in board.RUN_STATUSES:
        payload = board.run_payload(ENV, Args(status=status), branch="b", pr=None)
        assert isinstance(payload.get("exit", 0), int), (
            f"--status {status} puts {payload.get('exit')!r} in the exit field, "
            "and the board's column is a number"
        )


def test_a_skipped_job_files_no_exit_code_rather_than_a_zero():
    """A job that never ran has no exit code, and 0 would read as a success."""
    payload = board.run_payload(ENV, Args(status="skipped"), branch="b", pr=None)
    assert "exit" not in payload


def test_a_cancelled_job_is_not_filed_as_a_success():
    payload = board.run_payload(ENV, Args(status="cancelled"), branch="b", pr=None)
    assert payload["exit"] == 130


def test_every_status_the_cli_accepts_is_one_the_map_knows():
    """Adding a fifth word to one tuple and not the other is the same bug again."""
    assert set(board.RUN_STATUSES) == set(board.EXIT_FOR_STATUS)


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
    assert live_board["runs"][0]["exit"] == 0
    assert live_board["runs"][0]["seat"] == "engineer"


def test_report_dry_run_posts_nothing(live_board, no_git, capsys):
    assert board.main(["report", "--status", "failure", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "would POST /api/runs" in out
    assert json.loads(out.split("would POST")[0])["exit"] == 1
    assert live_board["runs"] == []


def test_a_report_carries_the_time_it_was_filed_even_with_no_clock_given(
        live_board, no_git, capsys):
    """Otherwise the run list prints `no time` against it.

    Measured on the live board 2026-10-18: ordering there is by `started_at`,
    which this command cannot observe, so this is about the row being legible
    and not about where it sorts. The sort half needs `--started-at` from the
    workflow and is filed in docs/ideas.md.
    """
    assert board.main(["report", "--status", "success"]) == 0
    assert live_board["runs"][0]["ended_at"], "a report with no time sorts last"
    assert "started_at" not in live_board["runs"][0], (
        "a start time this command never observed would be a claim about "
        "how long the run took"
    )


def test_an_explicit_end_time_wins_over_the_filing_time(live_board, no_git, capsys):
    assert board.main(["report", "--status", "success",
                       "--ended-at", "2026-10-18T01:02:03+00:00"]) == 0
    assert live_board["runs"][0]["ended_at"] == "2026-10-18T01:02:03+00:00"


def test_report_never_fails_the_run_when_the_board_refuses(live_board, no_git, capsys, monkeypatch):
    monkeypatch.setenv("BOARD_RUNTIME_TOKEN", "the-wrong-token")
    assert board.main(["report", "--status", "success"]) == 0
    assert "::warning::board:" in capsys.readouterr().out
    assert live_board["runs"] == []


def test_a_rejected_body_is_an_error_annotation_and_still_exits_zero(
        live_board, no_git, capsys, monkeypatch):
    """Loud about this file's own bug, quiet about the board's bad minute.

    The exit code stays 0 either way, because a red job for an unposted
    report is the lie INC-2026-09-26-run-report-dash-echo told six times.
    """
    def refuse(*a, **kw):
        raise board.BoardError("board said 422 to POST /api/runs: exit is a number",
                               code=422)

    monkeypatch.setattr(board, "api", refuse)
    assert board.main(["report", "--status", "success"]) == 0
    assert "::error::board:" in capsys.readouterr().out


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
    assert board.main(["move", "--seat", "engineer", "--id", "i-1",
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


def test_the_options_go_after_the_subcommand_the_way_the_docs_show(live_board, capsys):
    """`board.py show --seat engineer`, which is how docs/board.md writes it."""
    assert board.main(["show", "--seat", "engineer"]) == 0
    out = capsys.readouterr().out
    assert "Drain the reading queue" in out
    assert "Ship the pricing page" not in out


# --------------------------------------------------------------------------
# The shape rule the board enforces on its own side
# --------------------------------------------------------------------------


def blocks(text):
    return text.split("\n\n")


def test_prose_already_short_enough_passes_through_unchanged():
    """A seat that wrote short paragraphs must not have them rearranged."""
    written = "The press is late.\n\nI am saying so because nobody else did."
    assert board.scannable(written) == written


def test_a_block_over_the_limit_is_split_at_a_sentence():
    one = "The press owes an issue and no row exists for it. " * 20
    out = board.scannable(one)
    assert len(blocks(out)) > 1
    assert all(len(b) <= board.BODY_BLOCK_LIMIT for b in blocks(out))
    # Split at the sentence, so no block starts mid-thought.
    assert all(b.startswith("The press") for b in blocks(out))


def test_a_sentence_over_the_limit_is_split_at_a_clause():
    clauses = ", ".join(["the press owes an issue for this week"] * 20) + "."
    out = board.scannable(clauses)
    assert all(len(b) <= board.BODY_BLOCK_LIMIT for b in blocks(out))
    assert all(b.startswith("the press") for b in blocks(out))


def test_prose_with_no_boundary_at_all_is_still_brought_under_the_limit():
    """The last resort, and the reason it exists.

    A refused alarm says nothing at all, so a block with no sentence and no
    clause to cut at is wrapped at a space rather than left to bounce.
    """
    out = board.scannable("word " * 200)
    assert all(len(b) <= board.BODY_BLOCK_LIMIT for b in blocks(out))
    assert "word word" in out


def test_a_measurement_survives_the_splitting():
    """The one thing on an alarm a reader actually acts on is the number.

    The sentence pass took every full stop as a boundary until 2026-10-24, so
    a block over the limit printed `8.5 days` as `8. 5 days`. It had been live
    since this function shipped and only short blocks hid it: `drift_watch`
    already feeds it `ageing()` output, and every alarm this org posts is
    about a measurement.
    """
    one = ("The weekly job has been behind for 8.5 days and nothing has "
           "deployed it. ") * 7
    out = board.scannable(one)
    assert len(out) > board.BODY_BLOCK_LIMIT, "the fixture must exercise the split"
    assert "8.5 days" in out
    assert "8. 5" not in out, out
    assert all(len(b) <= board.BODY_BLOCK_LIMIT for b in blocks(out))
    assert out.split() == one.split()


def test_a_version_number_is_not_three_sentences():
    """The same rule, where the decimals come in a row rather than singly."""
    one = "Pinned at 1.2.3 and the deploy is behind by 0.5 of a day. " * 10
    out = board.scannable(one)
    assert "1.2.3" in out and "0.5 of a day" in out, out
    assert all(len(b) <= board.BODY_BLOCK_LIMIT for b in blocks(out))


def test_nothing_is_lost_in_the_splitting():
    one = "The press owes an issue and no row exists for it. " * 20
    assert board.scannable(one).split() == one.split()


def test_empty_prose_stays_empty():
    assert board.scannable("") == ""
    assert board.scannable(None) == ""


# --------------------------------------------------------------------------
# The inbox, and the one field that decides who is woken
# --------------------------------------------------------------------------


def message(**over):
    base = {"id": "m-x", "ts": "2026-10-24T12:00:00+00:00", "kind": "note",
            "from_company": "alexandra-systems", "from_seat": "pm",
            "to_company": None, "to_seat": None, "subject": "s", "body": "b"}
    return {**base, **over}


def test_a_message_naming_this_seat_in_this_company_is_ours():
    m = message(to_company="alexandria", to_seat="engineer")
    assert board.address_of(m, "engineer", "alexandria") == "yours"


def test_a_message_naming_this_seat_in_another_company_is_not_ours():
    m = message(to_company="Ursa", to_seat="engineer")
    assert board.address_of(m, "engineer", "alexandria") == "theirs"


def test_a_message_naming_this_seat_and_no_company_is_ambiguous_not_ours():
    """The finding this command was built for. `engineer` is a seat in at
    least five companies, so a message that names the seat and not the
    company is delivered to all five and belongs to one."""
    m = message(to_company=None, to_seat="engineer")
    assert board.address_of(m, "engineer", "alexandria") == "ambiguous"


def test_a_message_naming_neither_is_a_broadcast():
    assert board.address_of(message(), "engineer", "alexandria") == "broadcast"


def test_a_message_naming_only_a_company_is_that_companys_room():
    m = message(to_company="alexandria", to_seat=None)
    assert board.address_of(m, "engineer", "alexandria") == "broadcast"
    other = message(to_company="Ursa", to_seat=None)
    assert board.address_of(other, "engineer", "alexandria") == "theirs"


def test_the_seat_and_company_match_is_case_insensitive():
    """`Ursa` is capitalised on the bus and lowercase in half the prose."""
    m = message(to_company="ALEXANDRIA", to_seat="Engineer")
    assert board.address_of(m, "engineer", "alexandria") == "yours"


def test_sorting_buckets_every_message_and_loses_none():
    rows = [
        message(id="a", to_company="alexandria", to_seat="engineer"),
        message(id="b", to_seat="engineer"),
        message(id="c", to_company="Ursa", to_seat="engineer"),
        message(id="d"),
    ]
    buckets = board.sort_inbox(rows, "engineer", "alexandria")
    assert [m["id"] for m in buckets["yours"]] == ["a"]
    assert [m["id"] for m in buckets["ambiguous"]] == ["b"]
    assert [m["id"] for m in buckets["theirs"]] == ["c"]
    assert [m["id"] for m in buckets["broadcast"]] == ["d"]
    assert sum(len(g) for g in buckets.values()) == len(rows)


def test_each_bucket_is_newest_first():
    rows = [
        message(id="old", ts="2026-10-24T01:00:00+00:00", to_company="alexandria", to_seat="engineer"),
        message(id="new", ts="2026-10-24T17:00:00+00:00", to_company="alexandria", to_seat="engineer"),
    ]
    buckets = board.sort_inbox(rows, "engineer", "alexandria")
    assert [m["id"] for m in buckets["yours"]] == ["new", "old"]


def test_the_ambiguous_block_prints_first_and_says_why():
    buckets = board.sort_inbox(
        [message(id="b", to_seat="engineer", subject="whose is this")],
        "engineer", "alexandria",
    )
    out = board.render_inbox(buckets, "engineer", "alexandria")
    ambiguous = out.index("addressed to this seat but to no company")
    yours = out.index("addressed to this seat in this company")
    assert ambiguous < yours
    assert "may belong to another company's seat of this name" in out


def test_the_render_counts_the_broadcasts_it_did_not_print():
    buckets = board.sort_inbox([message(), message(id="two")], "engineer", "alexandria")
    assert "2 broadcasts not printed" in board.render_inbox(buckets, "engineer", "alexandria")


def test_a_cut_window_says_so_rather_than_reading_as_empty():
    buckets = board.sort_inbox([], "engineer", "alexandria")
    assert "row ceiling" not in board.render_inbox(buckets, "engineer", "alexandria")
    cut = board.render_inbox(buckets, "engineer", "alexandria", truncated=True)
    assert "row ceiling" in cut and "--since-hours" in cut


def test_inbox_exits_three_on_an_ambiguous_message(live_board, capsys):
    assert board.main(["inbox", "--company", "alexandria", "--seat", "engineer"]) == 3
    out = capsys.readouterr().out
    assert "Both defects are merged" in out        # the ambiguous one, printed
    assert "Build the detector" in out             # ours, printed
    assert "Another company's engineer" not in out  # theirs, dropped
    assert "1 message in the window addressed to someone else" in out


def test_inbox_exits_zero_when_nothing_is_ambiguous(live_board, capsys):
    live_board["messages"] = [m for m in live_board["messages"] if m["id"] != "m-2"]
    assert board.main(["inbox", "--company", "alexandria", "--seat", "engineer"]) == 0


def test_inbox_does_not_print_broadcasts_unless_asked(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer"])
    assert "Deployed HQ main" not in capsys.readouterr().out
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer", "--broadcast"])
    assert "Deployed HQ main" in capsys.readouterr().out


def test_inbox_json_carries_the_buckets_and_the_truncation_flag(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["truncated"] is False
    assert [m["id"] for m in payload["ambiguous"]] == ["m-2"]
    assert [m["id"] for m in payload["yours"]] == ["m-1"]


def test_a_full_page_is_reported_as_truncated(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer",
                "--limit", "1", "--json"])
    assert json.loads(capsys.readouterr().out)["truncated"] is True


# --------------------------------------------------------------------------
# `send`, which cannot commit the defect `inbox` reports
# --------------------------------------------------------------------------


class Sent:
    """The arguments `send` takes, as argparse would hand them over."""

    def __init__(self, **over):
        self.kind = "done"
        self.subject = "s"
        self.body = "b"
        self.to_seat = None
        self.to_company = None
        self.ref = None
        self.reasoning = ""
        self.data = None
        self.__dict__.update(over)


def test_a_seat_target_without_a_company_is_refused_before_the_network():
    with pytest.raises(board.BoardError) as caught:
        board.message_payload(Sent(to_seat="engineer"), "engineer", "alexandria")
    assert "needs --to-company" in str(caught.value)


def test_the_owner_and_the_room_need_no_company():
    for seat in board.COMPANYLESS_SEATS:
        payload = board.message_payload(Sent(to_seat=seat), "engineer", "alexandria")
        assert payload["to_seat"] == seat
        assert "to_company" not in payload


def test_a_fully_addressed_message_passes():
    payload = board.message_payload(
        Sent(to_seat="pm", to_company="alexandria"), "engineer", "alexandria"
    )
    assert payload["to_seat"] == "pm" and payload["to_company"] == "alexandria"
    assert payload["seat"] == "engineer" and payload["company"] == "alexandria"


def test_a_message_with_no_target_at_all_is_a_broadcast_and_is_allowed():
    payload = board.message_payload(Sent(), "engineer", "alexandria")
    assert "to_seat" not in payload and "to_company" not in payload


def test_a_kind_outside_the_buss_vocabulary_is_refused_here():
    with pytest.raises(board.BoardError) as caught:
        board.message_payload(Sent(kind="shout"), "engineer", "alexandria")
    assert "kind must be one of" in str(caught.value)


def test_the_body_is_brought_under_the_boards_block_limit():
    long_body = " ".join(["word"] * 300)
    payload = board.message_payload(Sent(body=long_body), "engineer", "alexandria")
    blocks = payload["body"].split("\n\n")
    assert len(blocks) > 1
    assert all(len(b) <= board.BODY_BLOCK_LIMIT for b in blocks)


def test_data_that_is_not_json_is_refused_with_the_parser_error():
    with pytest.raises(board.BoardError) as caught:
        board.message_payload(Sent(data="{not json"), "engineer", "alexandria")
    assert "--data is not JSON" in str(caught.value)


def test_send_posts_the_message_and_names_where_it_went(live_board, capsys):
    code = board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "done", "--subject", "Done", "--body", "It is built.",
        "--to-company", "alexandria", "--to-seat", "pm",
    ])
    assert code == 0
    assert "alexandria/pm" in capsys.readouterr().out
    posted = live_board["messages"][-1]
    assert posted["to_seat"] == "pm" and posted["to_company"] == "alexandria"


def test_send_prints_the_delivery_receipt_the_wake_limit_makes_necessary(
    live_board, capsys
):
    """The notice goes to the sender alone, so a print is the only way to read it."""
    code = board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "done", "--subject", "Done", "--body", "It is built.",
        "--to-company", "alexandria", "--to-seat", "pm",
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert "body whole" in out
    assert "characters delivered" in out
    assert "TRUNCATED" not in out


def test_a_body_over_the_wake_limit_says_so_rather_than_reading_as_delivered(
    live_board, capsys
):
    """A send that was cut and reads as clean is how one thought is sent twice.

    The receipt is still the thing under test here, so this passes the flag that
    waives the gate below it. Without the flag the send never reaches the board,
    which is the point of the gate and is asserted separately.
    """
    code = board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "note", "--subject", "Long", "--body", " ".join(["word"] * 500),
        "--to-company", "alexandria", "--to-seat", "pm", "--allow-truncation",
    ])
    assert code == 0
    assert "body TRUNCATED" in capsys.readouterr().out


# --------------------------------------------------------------------------
# The gate in front of the receipt
# --------------------------------------------------------------------------
#
# The receipt above shipped on 2026-11-02 and it reports after the POST, which
# is after the reader has been woken with a note whose disposition is missing.
# On the same day six sends across three seats were cut and every one of them
# cost a second send to deliver its own tail, including two by this seat written
# in the two notes agreeing that the ceiling is 1500. Recording is not
# enforcing. The receipt is the gate that writes something down; this is the
# gate that checks it before it ships.


LONG = ("A sentence that carries a measurement of 8.5 days and a reason. " * 24)


def test_a_body_over_the_limit_is_refused_before_the_board_is_asked(live_board, capsys):
    before = len(live_board["messages"])
    over = board.would_truncate(board.scannable(LONG))
    assert over > 0, "the fixture has to be over the limit for this to test anything"
    code = board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "note", "--subject", "Long", "--body", LONG,
        "--to-company", "alexandria", "--to-seat", "pm",
    ])
    assert code == board.EXIT_WOULD_TRUNCATE
    # A refusal is an exit code, and nothing was posted, so no reader was woken.
    assert len(live_board["messages"]) == before
    out = capsys.readouterr().out
    assert "REFUSED" in out
    assert f"{over} characters over" in out
    assert "--allow-truncation" in out


def test_the_gate_measures_the_body_as_posted_and_not_as_typed():
    """`scannable` reflows the body, and it can make it longer.

    Measured: 1,500 unbroken characters leave `scannable` as 1,506, because the
    block pass splits anything over 420. So a sender's own `wc -c` on a draft is
    not this gate, and a gate that measured the typed string would pass bodies
    the board then cuts. This is also the likeliest reason the research seat
    could fit no formula to its five samples: the number the server counts is
    not the number the sender typed.
    """
    typed = "x" * board.WAKE_LIMIT
    assert len(board.scannable(typed)) > len(typed)
    assert board.would_truncate(typed) == 0
    assert board.would_truncate(board.scannable(typed)) > 0


def test_the_refusal_exit_code_is_none_of_the_ones_already_taken():
    assert board.EXIT_WOULD_TRUNCATE not in (0, 1, 2, board.EXIT_AMBIGUOUS,
                                             board.EXIT_UNKNOWN_SEAT)


def test_a_body_at_exactly_the_limit_is_sent_rather_than_refused(live_board, capsys):
    """The limit is a ceiling, not a target: at or under it goes whole."""
    # Built through `scannable`, because that is the string the gate measures
    # and the board stores. A raw 1,500 characters is 1,506 after the reflow.
    body = "Short block.\n\n" * 50
    while board.would_truncate(board.scannable(body)) == 0:
        body += "One more short block.\n\n"
    while board.would_truncate(board.scannable(body)) > 0:
        body = body[: -len("One more short block.\n\n")]
    assert len(board.scannable(body)) <= board.WAKE_LIMIT
    code = board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "note", "--subject", "Exact", "--body", body,
        "--to-company", "alexandria", "--to-seat", "pm",
    ])
    assert code == 0
    assert "body whole" in capsys.readouterr().out


def test_would_truncate_measures_the_overflow_and_nothing_else():
    assert board.would_truncate("x" * (board.WAKE_LIMIT - 1)) == 0
    assert board.would_truncate("x" * board.WAKE_LIMIT) == 0
    assert board.would_truncate("x" * (board.WAKE_LIMIT + 7)) == 7


def test_the_refusal_names_the_further_loss_beyond_the_overflow():
    """69 characters over cost 180, so the arithmetic understates the damage."""
    text = " ".join(board.render_would_truncate(69))
    assert "69 characters over" in text
    assert "80 to 190" in text
    assert "tail" in text


def test_the_flag_waives_the_gate_rather_than_silencing_the_receipt(live_board, capsys):
    code = board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "note", "--subject", "Long", "--body", LONG,
        "--to-company", "alexandria", "--to-seat", "pm", "--allow-truncation",
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert "REFUSED" not in out
    assert "body TRUNCATED" in out


def test_a_dry_run_is_not_blocked_by_the_gate_because_it_wakes_nobody(live_board, capsys):
    """A sender measuring its own draft must be able to, over the limit or not."""
    code = board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "note", "--subject", "Long", "--body", LONG, "--dry-run",
    ])
    assert code == 0
    assert "would POST" in capsys.readouterr().out


# The client's limit is a cache of a number only the server knows, and no route
# answers it before a POST (`/api/limits`, `/api/meta` and `/api/config` all 404,
# probed 2026-11-02). A cache with no refresh route goes stale silently, and a
# gate on a stale cache either refuses sends that would have arrived or passes
# sends that will be cut. The receipt is the one place that learns the truth.


def test_a_server_limit_that_disagrees_with_the_gate_is_said_out_loud():
    said = " ".join(board.render_limit_drift(900))
    assert "900" in said and str(board.WAKE_LIMIT) in said
    assert "stale" in said


def test_an_agreeing_server_limit_prints_nothing():
    assert board.render_limit_drift(board.WAKE_LIMIT) == []
    assert board.render_limit_drift(None) == []


def test_the_cached_limit_is_the_one_the_live_board_reports(live_board, capsys):
    """If the fake and the gate ever drift apart, this is where it shows."""
    board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "note", "--subject", "s", "--body", "b",
        "--to-company", "alexandria", "--to-seat", "pm",
    ])
    assert f"wake limit {board.WAKE_LIMIT}" in capsys.readouterr().out


def test_a_dry_run_send_posts_nothing(live_board, capsys):
    before = len(live_board["messages"])
    board.main([
        "send", "--company", "alexandria", "--seat", "engineer",
        "--kind", "note", "--subject", "s", "--body", "b", "--dry-run",
    ])
    assert len(live_board["messages"]) == before
    assert "would POST /api/messages" in capsys.readouterr().out


def test_a_limit_above_the_servers_ceiling_is_clamped_so_truncation_stays_honest(
    live_board, capsys
):
    """The server answers 500 to a request for 1000, so an unclamped
    `len(messages) >= limit` would read a cut window as a whole one."""
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer",
                "--limit", "100000", "--json"])
    assert json.loads(capsys.readouterr().out)["truncated"] is False
    sent = [c for c in live_board["calls"] if c[1] == "/api/messages"][-1]
    assert sent[2]["limit"] == [str(board.INBOX_LIMIT)]


# --------------------------------------------------------------------------
# The seat argument, which was answered instead of resolved
# --------------------------------------------------------------------------
#
# `INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`.
# Every message `render_inbox` prints names its sender and its recipient in the
# qualified form, `alexandria/research -> alexandria/engineer`. Typing that form
# back produced `to_seat=alexandria/engineer`, which matches no row on the bus,
# so `yours` was empty; and because the narrowing is done by the server, the
# `theirs` bucket that exists to say what was filtered never saw a row either.
# Zero in every bucket, exit 0, against a true count of 22.
#
# These assert the resolution rather than the message counts, because the counts
# live on the live board and the resolution is the defect.


def test_the_qualified_form_the_inbox_prints_resolves_to_the_bare_seat():
    assert board.seat_of(Args(seat="alexandria/engineer"), env={}) == "engineer"
    assert board.seat_of(Args(seat="alexandria/engineer"), env={},
                         company="alexandria") == "engineer"


def test_the_bare_form_is_untouched():
    assert board.seat_of(Args(seat="engineer"), env={}) == "engineer"
    assert board.seat_of(Args(seat="engineer"), env={}, company="alexandria") == "engineer"


def test_a_company_half_that_disagrees_is_refused_rather_than_read():
    # The case worth refusing loudest: two different questions in one call.
    with pytest.raises(board.BoardError) as exc:
        board.seat_of(Args(seat="Ursa/engineer"), env={}, company="alexandria")
    assert "Ursa" in str(exc.value) and "alexandria" in str(exc.value)


def test_the_company_half_is_matched_without_regard_to_case():
    assert board.seat_of(Args(seat="Alexandria/engineer"), env={},
                         company="alexandria") == "engineer"


def test_a_seat_value_the_reader_cannot_resolve_raises_rather_than_querying():
    # The rule the incident asks for, in one line: no unresolvable seat is
    # allowed to reach a query that will answer empty.
    for bad in ("alexandria/", "/", "   ", "alexandria/Ursa/engineer", "/engineer"):
        with pytest.raises(board.BoardError):
            board.seat_of(Args(seat=bad), env={}, company="alexandria")


def test_a_trailing_slash_is_not_trimmed_into_a_seat_named_after_a_company():
    # Caught by the test above while this fix was being written. Trimming the
    # slash made `alexandria/` resolve to the seat `alexandria`, which no row
    # on the bus is addressed to, which answers empty with a clean zero. The
    # defect being repaired, reintroduced one layer in.
    with pytest.raises(board.BoardError) as exc:
        board.seat_of(Args(seat="alexandria/"), env={}, company="alexandria")
    assert "no seat after the slash" in str(exc.value)


def test_the_qualified_form_is_accepted_from_the_environment_too():
    # `ASC_SEAT` is how the host supplies this on every scheduled run, so a
    # host that ever sets the qualified form must not read an empty inbox.
    assert board.seat_of(Args(seat=None), env={"ASC_SEAT": "alexandria/pm"},
                         company="alexandria") == "pm"


def test_the_header_no_longer_doubles_the_company(live_board, capsys):
    # The doubled header was the only tell the defect left. It is also the
    # proof that the seat reached the query in the wrong form.
    board.main(["inbox", "--company", "alexandria", "--seat", "alexandria/engineer"])
    out = capsys.readouterr().out
    assert "inbox for alexandria/engineer" in out
    assert "alexandria/alexandria" not in out


def test_the_qualified_form_asks_the_bus_the_same_question_as_the_bare_one(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer", "--json"])
    bare = json.loads(capsys.readouterr().out)
    board.main(["inbox", "--company", "alexandria", "--seat", "alexandria/engineer", "--json"])
    qualified = json.loads(capsys.readouterr().out)
    assert bare == qualified
    assert [m["id"] for m in qualified["yours"]] == ["m-1"]


def test_a_disagreeing_company_half_never_reaches_the_board(live_board, capsys):
    before = len(live_board["calls"])
    assert board.main(["inbox", "--company", "alexandria", "--seat", "Ursa/engineer"]) == 2
    assert len(live_board["calls"]) == before


def test_a_write_takes_the_qualified_form_too(live_board, capsys):
    # `send` reports its own target in the qualified form, so this is the same
    # round trip: the form the tool prints is a form the tool accepts.
    board.main(["comment", "--company", "alexandria", "--seat", "alexandria/engineer",
                "--id", "i-1", "--body", "read"])
    sent = [c for c in live_board["calls"] if "/comment" in c[1]][-1]
    assert sent[-1]["seat"] == "engineer"


# --------------------------------------------------------------------------
# The other delimiter, and the zero that stopped being trusted
# --------------------------------------------------------------------------
#
# `INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`.
# The repair above taught `seat_of` the form this file PRINTS,
# `alexandria/skill`. The host hands every seat the form it does not print,
# `alexandria-skill`, which has no slash and so fell through untouched into a
# query no row on the bus answers. The skill seat ran it at 24, 48, 72 and 168
# hours, got zero in every directed bucket and exit 0 each time, and lost the
# opening of a run.
#
# The first block asserts the spelling. The second asserts the thing a spelling
# rule cannot give you, which is that a zero this command cannot stand behind
# no longer reads like an empty inbox.


def test_the_hyphenated_form_the_host_hands_the_seat_resolves_to_the_bare_seat():
    assert board.seat_of(Args(seat="alexandria-skill"), env={}) == "skill"
    assert board.seat_of(Args(seat="alexandria-engineer"), env={},
                         company="alexandria") == "engineer"


def test_a_bare_seat_name_with_a_hyphen_in_it_is_left_whole():
    # `exo-centralizer` is a real seat on this bus. Splitting on the first
    # hyphen would make it the seat `centralizer` in a company `exo` that does
    # not exist, which is the same confident zero facing the other way.
    assert board.seat_of(Args(seat="exo-centralizer"), env={}) == "exo-centralizer"
    assert board.seat_of(Args(seat="exo-centralizer"), env={},
                         company="alexandria") == "exo-centralizer"


def test_the_longest_company_name_wins_when_one_company_prefixes_another(monkeypatch):
    # Rehearsed against a shortest-first sort and it stayed green, because no
    # two companies on the real list prefix each other: `alexandra-systems` and
    # `alexandria` diverge at the eighth character. So the ordering rule is
    # unreachable through `KNOWN_COMPANIES` as it stands today, and a gate that
    # asserts it through the real list measures nothing.
    #
    # The list is the thing that changes. `docs/standards/pm.md` §14 says a
    # company is a repository name, and the day somebody adds a repository whose
    # name extends an existing one, this rule is what keeps that company's
    # seats readable. So the gate supplies the collision instead of waiting for
    # it.
    monkeypatch.setattr(board, "KNOWN_COMPANIES", ("acme", "acme-labs"))
    assert board.seat_of(Args(seat="acme-labs-pm"), env={}) == "pm"
    assert board.seat_of(Args(seat="acme-pm"), env={}) == "pm"
    # And the company half it reports is the long one, so a disagreement is
    # caught against the right name rather than against `acme`.
    with pytest.raises(board.BoardError) as exc:
        board.seat_of(Args(seat="acme-labs-pm"), env={}, company="acme")
    assert "acme-labs" in str(exc.value)


def test_the_real_company_list_resolves_its_own_hyphenated_name():
    # The live instance of the rule above, asserted separately so the two
    # cannot be confused: this one passes under either sort order.
    assert board.seat_of(Args(seat="alexandra-systems-pm"), env={}) == "pm"


def test_a_disagreeing_company_half_is_refused_in_the_hyphenated_form_too():
    with pytest.raises(board.BoardError) as exc:
        board.seat_of(Args(seat="Ursa-engineer"), env={}, company="alexandria")
    assert "Ursa" in str(exc.value) and "alexandria" in str(exc.value)


def test_the_hyphenated_company_half_is_matched_without_regard_to_case():
    assert board.seat_of(Args(seat="Alexandria-pm"), env={},
                         company="alexandria") == "pm"


def test_a_company_name_and_a_bare_hyphen_is_not_split_into_an_empty_seat():
    # The trailing-slash lesson, in the other delimiter: stripping the prefix
    # here would leave an empty seat name.
    assert board.seat_of(Args(seat="alexandria-"), env={}) == "alexandria-"


def test_the_hyphenated_form_is_accepted_from_the_environment_too():
    # This is the path that actually failed. `ASC_SEAT` is the host's own name
    # for the seat and the host spells it with a hyphen.
    assert board.seat_of(Args(seat=None), env={"ASC_SEAT": "alexandria-skill"},
                         company="alexandria") == "skill"


def test_the_hyphenated_form_asks_the_bus_the_same_question_as_the_bare_one(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer", "--json"])
    bare = json.loads(capsys.readouterr().out)
    board.main(["inbox", "--company", "alexandria", "--seat", "alexandria-engineer", "--json"])
    hyphenated = json.loads(capsys.readouterr().out)
    assert bare == hyphenated
    assert [m["id"] for m in hyphenated["yours"]] == ["m-1"]


def test_the_hyphenated_header_no_longer_doubles_the_company(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "alexandria-engineer"])
    out = capsys.readouterr().out
    assert "inbox for alexandria/engineer" in out
    assert "alexandria/alexandria" not in out


# -- the roster check, which is right about delimiters nobody has typed yet --


def test_a_seat_name_nothing_on_the_bus_carries_does_not_read_as_an_empty_inbox(
        live_board, capsys):
    code = board.main(["inbox", "--company", "alexandria", "--seat", "enginer"])
    out = capsys.readouterr().out
    assert code == board.EXIT_UNKNOWN_SEAT
    assert "this zero is not trustworthy" in out


def test_an_unrecognized_spelling_is_told_how_the_bus_spells_it(live_board, capsys):
    # No rule in this file knows about underscores. The roster check does not
    # need one, which is the whole reason it is here and not another delimiter.
    code = board.main(["inbox", "--company", "alexandria", "--seat", "alexandria_engineer"])
    out = capsys.readouterr().out
    assert code == board.EXIT_UNKNOWN_SEAT
    assert "the bus spells it 'engineer'" in out
    assert "--seat engineer" in out


def test_a_name_resembling_nothing_says_so_rather_than_guessing(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "enginer"])
    out = capsys.readouterr().out
    assert "no name on the bus resembles it" in out
    assert "the bus spells it" not in out


def test_a_real_seat_with_a_genuinely_empty_inbox_is_still_a_clean_zero(
        live_board, capsys):
    # The false alarm that would make this check worse than the defect. The
    # bus carries nothing directed at anybody; `frontend` is a real seat
    # because it holds a card, so the zero is real and says nothing extra.
    live_board["messages"] = [m for m in live_board["messages"] if m["to_seat"] is None]
    code = board.main(["inbox", "--company", "alexandria", "--seat", "frontend"])
    out = capsys.readouterr().out
    assert code == 0
    assert "not trustworthy" not in out


def test_the_check_does_not_run_at_all_when_there_is_mail(live_board, capsys):
    before = len(live_board["calls"])
    assert board.main(["inbox", "--company", "alexandria", "--seat", "engineer"]) == 3
    # One request, not three: the roster costs nothing on the path that was
    # never wrong.
    assert len(live_board["calls"]) - before == 1
    assert "not trustworthy" not in capsys.readouterr().out


def test_the_json_form_carries_the_verdict_so_a_script_can_read_it(live_board, capsys):
    board.main(["inbox", "--company", "alexandria", "--seat", "enginer", "--json"])
    answer = json.loads(capsys.readouterr().out)
    assert answer["seat"] == "enginer"
    assert answer["seat_on_bus"] is False
    board.main(["inbox", "--company", "alexandria", "--seat", "engineer", "--json"])
    assert json.loads(capsys.readouterr().out)["seat_on_bus"] is True


def refuse_the_unfiltered_read(monkeypatch):
    """The board up for a filtered read and down for the roster probe."""
    real = board.api

    def refusing(path, *a, **kw):
        if path.startswith("/api/messages?") and "to_seat" not in path:
            raise board.BoardError("board unreachable", code=None)
        return real(path, *a, **kw)

    monkeypatch.setattr(board, "api", refusing)


def test_the_manifest_answers_the_roster_question_when_the_board_cannot(
        live_board, capsys, monkeypatch):
    """The writer seat's correction, and the behaviour change worth naming.

    Until 2026-11-02 both roster sources were network reads, so a board that
    could not answer the unfiltered probe left the confident zero unverified:
    the command printed "could not check" and exited 0, which is the same exit a
    good read of an empty inbox gives. That is the honest answer only while
    there is nothing else to ask. `company.yaml` is in the checkout, so there
    was.
    """
    refuse_the_unfiltered_read(monkeypatch)
    code = board.main(["inbox", "--company", "alexandria", "--seat", "enginer"])
    captured = capsys.readouterr()
    assert code == board.EXIT_UNKNOWN_SEAT, captured.err
    assert "not trustworthy" in captured.out
    assert "could not check" not in captured.err
    # And the suggestion still works off the manifest alone, which is the half
    # that proves the manifest is a usable roster and not just a yes/no oracle.
    # `enginer` above is not suggestible: it drops a letter, so it neither
    # normalises to a real name nor ends with one. `alexandria_engineer` is the
    # case layer two exists for, a delimiter nobody taught the resolver.
    board.main(["inbox", "--company", "alexandria", "--seat", "alexandria_engineer"])
    suggested = capsys.readouterr().out
    assert "the bus spells it 'engineer'" in suggested, suggested
    assert "--seat engineer" in suggested


def test_a_roster_that_cannot_be_read_at_all_is_still_reported_as_unasked(
        live_board, capsys, monkeypatch):
    # The honest third state, now reachable only when the manifest is gone too.
    # The command does not know, so it says it does not know and leaves the exit
    # status alone rather than failing a run on a board hiccup.
    refuse_the_unfiltered_read(monkeypatch)
    monkeypatch.setattr(board, "MANIFEST_PATH", "/nonexistent/company.yaml")
    code = board.main(["inbox", "--company", "alexandria", "--seat", "enginer"])
    captured = capsys.readouterr()
    assert code == 0
    assert "could not check" in captured.err
    assert "unverified" in captured.err
    assert "not trustworthy" not in captured.out


def test_the_manifest_parse_agrees_with_pyyaml_on_the_live_file():
    """A regex standing in for a YAML parser, checked against the YAML parser.

    `board.py` is standard library only and that is deliberate, so the manifest
    is read with a regex. The shortcut is only honest if something compares it
    to the real thing on the real file, and this gate earned its place twice
    while the function was being written: the first pattern matched `company:`
    where the board's company name is the `product:` key, and the second read
    only the block form `- name: x` where this manifest writes inline mappings
    `- { name: x, ... }`. Both returned an empty set for every real call, which
    is a roster that is never consulted and reads exactly like a roster that
    agrees.
    """
    yaml = pytest.importorskip("yaml")
    with open(board.MANIFEST_PATH, encoding="utf-8") as handle:
        declared = yaml.safe_load(handle)
    truth = {seat["name"] for seat in declared["seats"]}
    assert board.manifest_seats("alexandria") == truth
    assert len(truth) == 12, sorted(truth)


def test_the_manifest_is_authoritative_only_about_its_own_company():
    """Another company's inbox must not be checked against this one's seats.

    The failure would be confident and wrong in the expensive direction: a real
    seat of another company reported as a name nothing carries, with a
    suggestion drawn from this repository's twelve.
    """
    assert board.manifest_seats("Ursa") == set()
    # The parent name resolves too, because `company:` is `alexandra-systems`
    # and the board may be asked for either.
    assert board.manifest_seats("alexandra-systems") == board.manifest_seats("alexandria")


def test_an_unreadable_manifest_contributes_nothing_and_refuses_nothing(tmp_path):
    """This is a source of roster names, never a source of refusals.

    A manifest that is absent, truncated mid-write, or reshaped by a later
    convention must leave the two live reads doing exactly what they did
    before. Returning a refusal from here would make a file edit able to break
    every seat's inbox.
    """
    assert board.manifest_seats("alexandria", path=str(tmp_path / "gone.yaml")) == set()
    empty = tmp_path / "empty.yaml"
    empty.write_text("company: alexandria\n")
    assert board.manifest_seats("alexandria", path=str(empty)) == set()
    reshaped = tmp_path / "reshaped.yaml"
    reshaped.write_text("product: alexandria\nseats:\n  engineer: {}\n")
    assert board.manifest_seats("alexandria", path=str(reshaped)) == set()


def test_the_seat_block_does_not_leak_another_blocks_names(tmp_path):
    """The scan stops at the next top-level key, so a sibling list cannot leak.

    `company.yaml` carries `surfaces:` and `standards:` beside `seats:`, and a
    roster that quietly absorbed another block's names would accept a surface
    path as a seat name.
    """
    path = tmp_path / "c.yaml"
    path.write_text(
        "product: alexandria\n"
        "seats:\n"
        "  - { name: engineer, cadence: daily }\n"
        "  - name: pm\n"
        "surfaces:\n"
        "  - { name: not-a-seat }\n"
    )
    assert board.manifest_seats("alexandria", path=str(path)) == {"engineer", "pm"}


def test_the_roster_reads_both_surfaces_because_each_has_a_blind_spot(live_board):
    roster = board.seat_roster("alexandria", 24)
    # From the bus, and specifically from a DIRECTED row. `chair:asc-host`
    # would prove less than it looks: it sends the broadcast, and the fake
    # returned the broadcasts even when it was answering an unfiltered read
    # with nothing else. `pm` appears only as the sender of a directed message
    # and holds no card, so it is reachable only if the unfiltered read really
    # returns the whole bus.
    assert "pm" in roster
    assert "chair:asc-host" in roster
    # From the board: a seat holding a card that has sent and received nothing.
    live_board["messages"] = []
    assert "frontend" in board.seat_roster("alexandria", 24)


def test_normalize_seat_only_ever_suggests_and_never_resolves():
    assert board.normalize_seat("alexandria-skill") == "alexandriaskill"
    assert board.normalize_seat("Alexandria/Skill") == "alexandriaskill"
    assert board.normalize_seat("") == ""
    # The suggestion runs "the typed name ends with a real seat name", because
    # the extra characters are always on the side the reader typed.
    assert "exo-centralizer" in board.render_unknown_seat(
        "alexandria.exo-centralizer", "alexandria", {"exo", "exo-centralizer"})


# -- the same defect one function over, found by running the repaired command --


def test_a_run_report_resolves_the_hosts_name_for_the_seat():
    # `run_payload` derived its seat from the same three sources as `seat_of`
    # and resolved none of them. On this host `ASC_SEAT` is `alexandria-engineer`
    # and every card, message and inbox read on the board uses `engineer`, so an
    # unresolved report lands under a seat name nothing else on the board shares.
    # The board accepts it, which is why nothing would have refused it.
    payload = board.run_payload(
        {"ASC_COMPANY": "alexandria"},
        Args(seat="alexandria-engineer", status="success"),
    )
    assert payload["seat"] == "engineer"
    assert payload["company"] == "alexandria"


def test_a_run_report_takes_the_slashed_form_too():
    payload = board.run_payload({}, Args(seat="alexandria/pm", status="success"))
    assert payload["seat"] == "pm"


def test_a_run_report_leaves_a_bare_seat_alone():
    # The path twelve workflows took, which must not move.
    payload = board.run_payload({"GITHUB_WORKFLOW": "engineer-agent"},
                                Args(seat=None, status="success"))
    assert payload["seat"] == "engineer"
    payload = board.run_payload({}, Args(seat="exo-centralizer", status="success"))
    assert payload["seat"] == "exo-centralizer"


def test_a_run_report_refuses_a_company_half_that_disagrees():
    # Filing another company's run under this one's name is worse than
    # refusing, and the refusal is free because the company is already known
    # here.
    with pytest.raises(board.BoardError) as exc:
        board.run_payload({"ASC_COMPANY": "alexandria"},
                          Args(seat="Ursa-engineer", status="success"))
    assert "Ursa" in str(exc.value)


# --- the server's answered_by, reported rather than trusted ----------------
#
# Added 2026-11-09 by the security seat. The board sets this field itself by
# pairing a message with a later reply from its addressee, and this reader was
# silent about it, so a seat reading the raw API saw a bare claim and a seat
# reading this tool saw nothing. One reply was marked as the answer to two
# different messages inside half an hour on 2026-11-09, which is the shape.


def test_a_message_with_no_answered_by_gets_no_note():
    assert board.answered_note({"id": "a"}) is None
    assert board.answered_note({"id": "a", "answered_by": None}) is None


def test_a_reply_that_names_this_message_is_said_to_name_it():
    message = {"id": "aaa", "answered_by": {"by": "x/pm", "message": "bbb"}}
    replies = {"bbb": {"id": "bbb", "data": {"answering": "aaa"}}}
    note = board.answered_note(message, replies)
    assert "names this message" in note
    assert "PER THE SERVER" not in note


def test_a_reply_that_names_a_different_message_contradicts_the_server():
    """The two real cases of 2026-11-09, in both directions between seats."""
    message = {"id": "aaa", "answered_by": {"by": "x/exo", "message": "bbb"}}
    replies = {"bbb": {"id": "bbb", "data": {"answering": "ccc"}}}
    note = board.answered_note(message, replies)
    assert "PER THE SERVER" in note
    assert "names ccc" in note
    assert "read it before you skip this" in note


def test_a_reply_that_says_nothing_is_called_unverified_and_not_answered():
    """229 of the 235 marked messages in the window are this case.

    The distinction that matters to a reader is between a claim that was
    checked and a claim that could not be, and the old reader printed neither.
    """
    message = {"id": "aaa", "answered_by": {"by": "x/pm", "message": "bbb"}}
    for replies in [{}, {"bbb": {"id": "bbb"}}, {"bbb": {"id": "bbb", "data": {}}}]:
        note = board.answered_note(message, replies)
        assert "unverified" in note
        assert "does not say which message it answers" in note


def test_the_note_survives_a_reply_that_was_never_read():
    """The claim still prints, because hiding it is the bug this closes.

    What it prints is "not checked" rather than "unverified", and the three
    states are pinned by
    `test_a_reply_that_was_not_checked_is_not_checked_rather_than_unverified`
    below.
    """
    message = {"id": "aaa", "answered_by": {"by": "x/pm", "message": "bbb"}}
    note = board.answered_note(message, None)
    assert "PER THE SERVER" in note
    assert "not checked" in note


def test_the_rendered_inbox_carries_the_note_and_is_silent_without_the_field():
    marked = {"id": "aaa", "kind": "done", "ts": "2026-11-09T03:07:11Z",
              "from_company": "alexandria", "from_seat": "exo",
              "to_company": "alexandria", "to_seat": "security",
              "subject": "s", "answered_by": {"by": "alexandria/security",
                                              "message": "bbb"}}
    plain = dict(marked, id="ccc", answered_by=None)
    buckets = {"yours": [marked, plain], "ambiguous": [], "broadcast": [],
               "theirs": []}
    out = board.render_inbox(buckets, "security", "alexandria",
                             by_id={"bbb": {"id": "bbb",
                                            "data": {"answering": "ccc"}}})
    assert "PER THE SERVER" in out
    assert out.count("answered by") == 1, "the unmarked message grew a note"


# --- the second read, because the reply is never in the inbox ---------------
#
# The first version of answered_note was handed the inbox's own buckets, and
# its verification branch was dead on every real message: read_messages sends
# to_seat, so the bus never returns a letter addressed to anybody else, and an
# answering reply is addressed to the sender of the message being marked. Every
# claim read "unverified" and nothing could ever be contradicted. Caught by
# running the tool against the live board rather than by this suite.


def test_a_reply_that_was_not_read_is_not_checked_rather_than_unverified():
    """Three states and not two, which is this whole class in one function.

    `None` means the replies were not read. An empty mapping means they were
    read and this one was not among them. Those are the same bytes and they are
    not the same answer.
    """
    message = {"id": "aaa", "answered_by": {"by": "x/pm", "message": "bbb"}}
    assert "not checked" in board.answered_note(message, None)
    assert "unverified" in board.answered_note(message, {})


def test_nothing_marked_means_no_second_call_at_all(monkeypatch):
    """A clean inbox must not pay for a read it has no question for."""
    def refuse(*a, **k):
        raise AssertionError("the bus was read with nothing to check")
    monkeypatch.setattr(board, "api", refuse)
    assert board.answering_replies([{"id": "a"}], 6) == {}


def test_the_second_read_returns_only_the_replies_that_were_named(monkeypatch):
    messages = [{"id": "a", "answered_by": {"message": "r1"}},
                {"id": "b", "answered_by": {"message": "r2"}},
                {"id": "c"}]
    rows = [{"id": "r1"}, {"id": "r2"}, {"id": "unrelated"}]
    seen = []

    def api(path, **kwargs):
        seen.append(path)
        return {"messages": rows}

    monkeypatch.setattr(board, "api", api)
    found = board.answering_replies(messages, 6)
    assert sorted(found) == ["r1", "r2"]
    # Unfiltered by addressee on purpose: the thing being checked is never in
    # the caller's own inbox.
    assert "to_seat" not in seen[0]


def test_a_failed_second_read_is_not_checked_and_says_so(monkeypatch, capsys):
    """A failed call must not arrive as an answer, which is the class itself."""
    def refusing(path, **kwargs):
        raise board.BoardError("the board's database is unreachable")

    monkeypatch.setattr(board, "api", refusing)
    assert board.answering_replies(
        [{"id": "a", "answered_by": {"message": "r1"}}], 6) is None
    assert "could not read the answering replies" in capsys.readouterr().err


# --- the json render, which is the one an agent reads -----------------------
#
# The run that found this defect read `answered_by` out of a raw API response
# and was one step from skipping a live ask. A label only the prose render
# carries is a label on the wrong reader.


def test_an_unmarked_message_is_returned_unchanged_by_the_annotator():
    message = {"id": "aaa", "subject": "s"}
    assert board.annotate_answered(message, {}) is message


@pytest.mark.parametrize("by_id,verdict", [
    (None, "not-checked"),
    ({}, "reply-says-nothing"),
    ({"bbb": {"id": "bbb"}}, "reply-says-nothing"),
    ({"bbb": {"id": "bbb", "data": {"answering": "aaa"}}}, "names-this-message"),
    ({"bbb": {"id": "bbb", "data": {"answering": "zzz"}}}, "names-another-message"),
])
def test_the_json_verdict_has_one_value_per_state(by_id, verdict):
    """Four values, so a consumer can filter without parsing the sentence."""
    message = {"id": "aaa", "answered_by": {"by": "x/pm", "message": "bbb"}}
    out = board.annotate_answered(message, by_id)
    assert out["answered_check"] == verdict
    assert out["answered_note"]
    # The server's claim stays beside the verdict rather than being replaced:
    # its timestamp and sender are correct and only its message is a guess.
    assert out["answered_by"] == message["answered_by"]


def test_the_json_verdict_and_the_prose_note_never_disagree():
    message = {"id": "aaa", "answered_by": {"by": "x/pm", "message": "bbb"}}
    for by_id, expect in [
        ({"bbb": {"id": "bbb", "data": {"answering": "aaa"}}}, "names this message"),
        ({"bbb": {"id": "bbb", "data": {"answering": "zzz"}}}, "names zzz"),
        ({}, "does not say which message"),
        (None, "not checked"),
    ]:
        out = board.annotate_answered(message, by_id)
        assert expect in out["answered_note"]
        assert out["answered_note"] == board.answered_note(message, by_id)
