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
            rows = [
                m for m in self.state["messages"]
                if (m["to_seat"] is None and m["to_company"] is None)
                or (seat and m["to_seat"] == seat)
                or (company and m["to_company"] == company)
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
            return self._send(201, {"id": row["id"]})
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
