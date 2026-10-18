"""The quiet-send guardrail: does it fire on the hour, and only once a week.

Run with `python3 -m pytest tests/test_press_watch.py -q`.

`tools/press_watch.py` is the scheduled reader sprint 2026-10-12 item 5 asks
for. The judgement it carries is `delivery_health.judge_press`, which already
has its own suite, so the tests here are about the three things that are new:
when the window has actually closed, what the card says, and the dedupe that
makes a daily schedule post one card a week instead of seven.

Nothing here touches the network or the board. The press surface is built by
calling the real `judge_press` with rows, which is the same shape both of its
readers hand it, and the board is a recording double. A test that needed a
credential would be a test nobody runs on a pull request.

The clock matters in every one of these, because the whole defect this guards
is a reader that ran at the wrong hour. `0 9 * * 1` plus a two hour grace
window puts the deadline at 11:00 UTC on a Monday, so 2026-10-12 10:00 and
2026-10-12 11:01 are the two sides of the only boundary this file has.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import board  # noqa: E402
from tools import delivery_health as dh  # noqa: E402
from tools import press_watch as pw  # noqa: E402

UTC = timezone.utc

#: The Monday the press went quiet, which is the week this guardrail was
#: written for. W41 ended on Sunday 2026-10-11, so its issue was due at 11:00
#: on 2026-10-12 and the newest row at the time was W40.
BEFORE = datetime(2026, 10, 12, 10, 0, tzinfo=UTC)
AFTER = datetime(2026, 10, 12, 11, 1, tzinfo=UTC)
W40 = {"week": "2026-W40", "created_at": datetime(2026, 10, 5, 9, 1, tzinfo=UTC),
       "model": "kimi-k2.6"}
W41 = {"week": "2026-W41", "created_at": datetime(2026, 10, 12, 9, 1, tzinfo=UTC),
       "model": "kimi-k2.6"}
#: The same week, printed by the second provider in `weekly.FALLBACK_MODELS`.
#: This is what the owner asked to be told about on 2026-10-16: the press
#: survived an outage and nothing said which account carried it.
W41_FALLBACK = {**W41, "model": "openai/gpt-oss-120b"}


def press(facts, when):
    """The press surface as either reader hands it to the judgement."""
    return dh.judge_press(facts, today=when, source=dh.RECEIPT_URL)


# ------------------------------------------------------- when the window closes


def test_the_window_has_not_closed_before_the_cron_plus_its_grace():
    """The nine hours every Monday that used to read as a missing issue.

    This is the one case that must stay quiet. A guardrail that posts a card
    at 00:05 every Monday about a week the press has not had its turn at yet
    teaches the board to ignore its cards, which costs more than the card is
    worth.
    """
    surface = press(W40, BEFORE)
    assert not pw.is_late(surface)
    assert surface.evidence["pending"] == "2026-W41"


def test_the_window_closes_an_hour_after_the_cron_and_the_guardrail_fires():
    surface = press(W40, AFTER)
    assert pw.is_late(surface)
    assert pw.due_week(surface) == "2026-W41"


def test_an_issue_written_on_time_is_not_late():
    assert not pw.is_late(press(W41, AFTER))


def test_an_empty_digests_table_is_late_whatever_the_clock_says():
    """`judge_press` has no grace for a press that has never printed."""
    surface = press(None, BEFORE)
    assert pw.is_late(surface)
    assert pw.due_week(surface) == "2026-W40"


def test_the_guardrail_fires_on_the_week_this_was_written_for():
    """2026-W41, 52.9 hours after its deadline, which is the live case."""
    surface = press(W40, datetime(2026, 10, 14, 15, 55, tzinfo=UTC))
    assert pw.is_late(surface)
    assert pw.due_week(surface) == "2026-W41"


# ------------------------------------------------------------- what it says


def test_the_deadline_is_the_cron_plus_the_grace_window():
    assert pw.due_deadline("2026-W41", AFTER) == datetime(2026, 10, 12, 11, 0, tzinfo=UTC)


def test_the_deadline_is_dated_from_the_week_the_card_names_not_from_today():
    """The pre-cron Monday, where dating from today prints a future deadline.

    At 10:00 on a Monday the week that owes an issue is the one before the one
    that has just ended. `last_sunday` answers the second question, so a card
    dated that way would tell its reader the overdue issue is due in an hour.
    """
    surface = press(None, BEFORE)
    week = pw.due_week(surface)
    deadline = pw.due_deadline(week, BEFORE)
    assert deadline < BEFORE, "an overdue card dated its deadline in the future"
    assert deadline == datetime(2026, 10, 5, 11, 0, tzinfo=UTC)


def test_the_card_names_the_week_in_its_title():
    assert pw.card_title("2026-W41") == "Press: no issue for 2026-W41"
    assert pw.card_title("2026-W41").startswith(pw.TITLE_PREFIX)


def test_the_card_body_carries_the_deadline_the_lateness_and_the_way_out():
    body = pw.card_body(press(W40, AFTER), AFTER)
    assert "2026-W41" in body
    assert "2026-10-12 11:00 UTC" in body
    assert "1 minutes late" in body
    # The command and the ladder it has to go behind, because the issue is
    # editorial and the rehearsal is not optional.
    assert "resend --week 2026-W41" in body
    assert "press-rehearsal.md" in body
    # Which reader answered, for the same reason every surface carries it.
    assert dh.RECEIPT_URL in body


@pytest.mark.parametrize("late_for,expected", [
    (timedelta(minutes=4), "4 minutes"),
    (timedelta(hours=1, minutes=30), "1.5 hours"),
    (timedelta(hours=52, minutes=54), "2.2 days"),
])
def test_lateness_reads_in_the_unit_a_reader_would_use(late_for, expected):
    assert pw.lateness(late_for) == expected


def test_the_card_body_does_not_claim_a_row_that_does_not_exist():
    body = pw.card_body(press(None, AFTER), AFTER)
    assert "no issue on record at all" in body
    assert "The newest issue on record" not in body, (
        "an empty table was described as having a row"
    )


#: The three connectives the board's own validator looks for. Its refusal
#: message names them, and the message is the only published statement of the
#: rule that exists: `400 item refused: the prose must carry its reason in
#: words (so that, because, otherwise): what you are doing and why, as a
#: conversation, not a list of labels`.
CONNECTIVES = ("so that", "because", "otherwise", " so ")


def test_the_card_reads_as_prose_the_board_will_accept():
    """The first draft of the card was refused by the board, correctly.

    It was four labelled lines, two of them `Field: value`, and the board
    answered 400. Asserting the shape here rather than finding out at the
    POST is the difference between a guardrail that fires and a guardrail
    whose own alarm bounces. See the note in `tools/board.py`.
    """
    body = pw.card_body(press(W40, AFTER), AFTER)
    assert any(word in body for word in CONNECTIVES), (
        "the card carries no reason in words, which the board refuses"
    )
    for line in body.splitlines():
        head = line.split(":")[0]
        assert not (line and ":" in line and len(head.split()) < 4
                    and not head.startswith("http")), (
            f"{line!r} reads as a label rather than a sentence"
        )


def test_the_nudge_reads_as_prose_too():
    body = pw.nudge_body(press(W40, AFTER + timedelta(hours=25)),
                         AFTER + timedelta(hours=25))
    assert any(word in body for word in CONNECTIVES)


# ------------------------------------------------- one card a week, not seven

OTHER_COLUMN = "c-done"


def board_payload(items):
    return {"columns": [{"id": "c-sprint", "name": "This sprint", "position": 2},
                        {"id": OTHER_COLUMN, "name": "Done", "position": 5}],
            "items": items}


def test_find_card_matches_this_commands_own_card_for_this_week():
    card = {"id": "x", "title": "Press: no issue for 2026-W41", "column_id": "c-sprint"}
    assert pw.find_card(board_payload([card]), "2026-W41") is card


def test_find_card_looks_in_every_column_including_done():
    """A week somebody has already closed is not alarmed about again."""
    card = {"id": "x", "title": "Press: no issue for 2026-W41", "column_id": OTHER_COLUMN}
    assert pw.find_card(board_payload([card]), "2026-W41") is card


def test_find_card_does_not_match_another_week():
    card = {"id": "x", "title": "Press: no issue for 2026-W40", "column_id": "c-sprint"}
    assert pw.find_card(board_payload([card]), "2026-W41") is None


def test_find_card_does_not_match_a_card_somebody_else_wrote():
    """The PM's own card for the same gap, which is work and not an alarm.

    `dee2d12f` on the live board is exactly this: "Diagnose and close today's
    press-send gap", created eleven hours after the send that did not happen.
    Treating it as this command's card would mean the guardrail reads a human
    noticing late as itself having noticed on time.
    """
    card = {"id": "x", "title": "Diagnose and close today's press-send gap",
            "column_id": "c-sprint"}
    assert pw.find_card(board_payload([card]), "2026-W41") is None


class Recorder:
    """The board, as far as `post` can tell, recording what it was asked."""

    def __init__(self, payload, created=None):
        self.payload, self.calls = payload, []
        self.created = created or {"id": "new-card"}

    def read_board(self, company, env=None, opener=None):
        self.calls.append(("read", company))
        return self.payload

    def api(self, path, method="GET", payload=None, env=None, opener=None):
        self.calls.append((method, path, payload))
        return self.created


@pytest.fixture
def recorder(monkeypatch):
    def install(payload, created=None):
        rec = Recorder(payload, created)
        monkeypatch.setattr(board, "read_board", rec.read_board)
        monkeypatch.setattr(board, "api", rec.api)
        return rec
    return install


def test_a_week_with_no_card_gets_one_in_the_working_column(recorder):
    rec = recorder(board_payload([]))
    did = pw.post(press(W40, AFTER), "2026-W41", AFTER, company="alexandria")
    assert did["action"] == "created"
    (method, path, payload) = rec.calls[-1]
    assert (method, path) == ("POST", "/api/items")
    assert payload["title"] == "Press: no issue for 2026-W41"
    assert payload["column_id"] == "c-sprint", "the card landed outside the working column"
    assert payload["seat"] == "engineer"
    assert payload["horizon"] == "now"


def test_a_week_that_already_has_a_fresh_card_is_not_posted_again(recorder):
    card = {"id": "x", "title": "Press: no issue for 2026-W41",
            "column_id": "c-sprint", "created_at": AFTER.isoformat(),
            "comments": []}
    rec = recorder(board_payload([card]))
    did = pw.post(press(W40, AFTER), "2026-W41", AFTER, company="alexandria")
    assert did["action"] == "already on the board"
    assert not [c for c in rec.calls if c[0] == "POST"], (
        "a second run on the same week wrote to the board, which is seven "
        "cards a week on a daily schedule"
    )


def test_a_week_that_stays_missing_gets_one_nudge_a_day(recorder):
    card = {"id": "x", "title": "Press: no issue for 2026-W41",
            "column_id": "c-sprint", "created_at": AFTER.isoformat(),
            "comments": []}
    rec = recorder(board_payload([card]))
    later = AFTER + timedelta(hours=25)
    did = pw.post(press(W40, later), "2026-W41", later, company="alexandria")
    assert did["action"] == "nudged"
    (method, path, payload) = rec.calls[-1]
    assert (method, path) == ("POST", "/api/items/x/comments")
    assert "Still missing" in payload["body"]
    assert "25.0 hours" in payload["body"]


def test_a_dry_run_reaches_no_board_at_all(monkeypatch):
    """`--dry-run` is how a seat sees the card without spending it."""
    def explode(*a, **k):
        raise AssertionError("a dry run called the board")
    monkeypatch.setattr(board, "read_board", explode)
    monkeypatch.setattr(board, "api", explode)
    did = pw.post(press(W40, AFTER), "2026-W41", AFTER, dry_run=True)
    assert did["action"] == "would create"
    assert did["title"] == "Press: no issue for 2026-W41"


def test_an_unresolvable_column_still_gets_the_card_posted(recorder, capsys):
    """The card matters and its column does not.

    A board that renamed its columns would otherwise turn this guardrail off,
    which is the failure mode where the alarm depends on the thing it watches.
    """
    rec = recorder({"columns": [{"id": "c-only", "name": "Inbox"}], "items": []})
    did = pw.post(press(W40, AFTER), "2026-W41", AFTER, company="alexandria")
    assert did["action"] == "created"
    (method, path, payload) = rec.calls[-1]
    assert "column_id" not in payload
    assert "no column named" in capsys.readouterr().err


# ---------------------------------------------------------------- the verdict


# ------------------------------------- the issue printed, on the wrong account


def test_an_issue_off_the_primarys_provider_is_a_fallback():
    assert pw.wrote_on_fallback(press(W41_FALLBACK, AFTER))


def test_an_issue_on_the_primary_is_not():
    assert not pw.wrote_on_fallback(press(W41, AFTER))


def test_a_missing_issue_is_not_also_a_fallback():
    """Two cards for one week is two alarms for one fact.

    The late card already says the week has no issue. Asking the fallback
    question of a week whose newest row is some older week would answer about
    that older week, which is a true sentence about the wrong subject.
    """
    assert not pw.wrote_on_fallback(press(W40, AFTER))


def test_the_fallback_card_names_the_week_the_model_and_the_primary():
    surface = press(W41_FALLBACK, AFTER)
    title = pw.fallback_title(surface)
    assert "2026-W41" in title
    assert "kimi-k2.6" in title, "the title says what it is not, so a reader can tell"
    body = pw.fallback_body(surface, AFTER)
    assert "openai/gpt-oss-120b" in body
    assert "groq" in body
    assert "short edition" in body, "the quality cost is arithmetic, so it is stated"


def test_the_fallback_card_reads_as_prose_the_board_will_accept():
    """The board refuses a labelled block and a block over 420 characters."""
    body = pw.fallback_body(press(W41_FALLBACK, AFTER), AFTER)
    for block in body.split("\n\n"):
        assert len(block) <= 420, block
    assert board.scannable(body) == body


def test_the_two_cards_for_one_week_do_not_dedupe_each_other():
    """`find_card` matched on a shared title prefix until there were two titles."""
    late = {"id": "late", "title": pw.card_title("2026-W41")}
    fell = {"id": "fell", "title": pw.fallback_title(press(W41_FALLBACK, AFTER))}
    payload = board_payload([late, fell])
    assert pw.find_card(payload, "2026-W41", pw.TITLE_PREFIX)["id"] == "late"
    assert pw.find_card(payload, "2026-W41", pw.FALLBACK_MARK)["id"] == "fell"


def test_a_fallback_week_gets_a_card_and_the_run_still_exits_zero(monkeypatch,
                                                                  recorder):
    """The press delivered, so the job is green and the board is told anyway.

    A red tick on a week the reader got an issue teaches everybody to stop
    reading the ticks, and the decision a fallback asks for belongs to a
    person looking at a card rather than at a job status.
    """
    rec = recorder(board_payload([]))
    fixed_press(press(W41_FALLBACK, AFTER), monkeypatch)
    answer = pw.watch(today=AFTER, company="alexandria")
    assert answer["exit"] == 0
    assert answer["on_fallback"] is True
    assert answer["board"]["action"] == "created"
    (method, path, payload) = rec.calls[-1]
    assert (method, path) == ("POST", "/api/items")
    assert pw.FALLBACK_MARK in payload["title"]


def test_a_fallback_card_is_said_once_and_never_nudged(recorder):
    """A statement is not an open problem, so it does not get a daily reminder."""
    surface = press(W41_FALLBACK, AFTER)
    stale = {"id": "fell", "title": pw.fallback_title(surface),
             "created_at": (AFTER - timedelta(days=9)).isoformat(),
             "comments": []}
    rec = recorder(board_payload([stale]))
    did = pw.post(surface, "2026-W41", AFTER, company="alexandria",
                  kind="fallback")
    assert did["action"] == "already on the board"
    assert not any(m == "POST" for (m, *_) in rec.calls)


def test_the_primary_path_still_says_nothing(monkeypatch):
    """The quiet case stays quiet, which is what makes the card worth reading."""
    fixed_press(press(W41, AFTER), monkeypatch)
    answer = pw.watch(today=AFTER)
    assert answer["exit"] == 0
    assert answer["on_fallback"] is False
    assert answer["board"]["action"] == "nothing to post"


def test_the_render_names_the_provider_on_every_verdict(monkeypatch):
    """"Which provider wrote it" is the owner's question, so it is always printed."""
    fixed_press(press(W41_FALLBACK, AFTER), monkeypatch)
    text = pw.render(pw.watch(today=AFTER, dry_run=True))
    assert "openai/gpt-oss-120b" in text
    assert "a fallback, not the primary" in text


def fixed_press(surface, monkeypatch):
    monkeypatch.setattr(pw, "read_press", lambda today=None: surface)


def test_watch_posts_nothing_and_exits_zero_when_the_press_is_current(monkeypatch):
    fixed_press(press(W41, AFTER), monkeypatch)
    answer = pw.watch(today=AFTER)
    assert answer["exit"] == 0
    assert answer["board"]["action"] == "nothing to post"


def test_watch_exits_two_and_posts_nothing_when_it_cannot_read_the_press(monkeypatch):
    """A gate that saw nothing is not a gate that saw a pass.

    `INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see` and company
    standard L-A21 are the same shape, one level up: the quiet answer read as
    the good answer. Here it is neither. No card, because the run cannot
    support the claim, and a non-zero exit so the job goes red.
    """
    fixed_press(dh.Surface("press", dh.UNKNOWN, "no reader answered"), monkeypatch)
    answer = pw.watch(today=AFTER)
    assert answer["exit"] == 2
    assert answer["board"]["action"] == "nothing posted"
    assert "cannot support" in answer["board"]["why"]


def test_watch_still_exits_one_when_the_board_refuses_the_card(monkeypatch):
    """The finding is real whether or not the board took it."""
    fixed_press(press(W40, AFTER), monkeypatch)

    def refuse(*a, **k):
        raise board.BoardError("board said 401 to GET /api/board/alexandria")
    monkeypatch.setattr(board, "read_board", refuse)
    answer = pw.watch(today=AFTER)
    assert answer["exit"] == 1
    assert answer["board"]["action"] == "not posted"
    assert "401" in answer["board"]["why"]


def test_watch_carries_the_surface_it_judged(monkeypatch):
    fixed_press(press(W40, AFTER), monkeypatch)
    answer = pw.watch(today=AFTER, dry_run=True)
    assert answer["press"]["state"] == dh.FAILING
    assert answer["due"] == "2026-W41"
    assert answer["late"] is True


@pytest.mark.parametrize("code", [0, 1, 2])
def test_every_verdict_renders(code, monkeypatch):
    """One render for three exit codes, and none of them may raise."""
    surfaces = {0: press(W41, AFTER), 1: press(W40, AFTER),
                2: dh.Surface("press", dh.UNKNOWN, "no reader answered")}
    fixed_press(surfaces[code], monkeypatch)
    answer = pw.watch(today=AFTER, dry_run=True)
    assert answer["exit"] == code
    text = pw.render(answer)
    assert "press" in text and answer["press"]["headline"] in text


# ------------------------------------------------------- the cooldown's memory


@pytest.mark.parametrize("comments,expected", [
    (None, False),
    ([], True),
    ([{"created_at": (AFTER + timedelta(hours=24)).isoformat()}], False),
    ([{"created_at": AFTER.isoformat()}], True),
    ([{"body": "no timestamp this reader knows"}], False),
    ([{"created_at": AFTER.isoformat()},
      {"created_at": (AFTER + timedelta(hours=24)).isoformat()}], False),
])
def test_the_newest_comment_is_the_cooldown(comments, expected):
    """Including the two shapes this reader refuses to guess about.

    A card with no `comments` key at all is the shape the board's list view
    returns, and a comment whose timestamp this does not recognise is a shape
    change. Both read as recently nudged, because a wrong quiet day costs
    nothing and a comment every run costs the card its reader.
    """
    card = {"id": "x", "created_at": AFTER.isoformat()}
    if comments is not None:
        card["comments"] = comments
    assert pw.needs_nudge(card, AFTER + timedelta(hours=25)) is expected


# -------------------------------------------- the schedule, which is the point

STAGED = ROOT / ".github" / "workflows-pending" / "press-watch.yml"


def staged_workflow() -> str:
    """The staged workflow with its commentary stripped.

    The prose in that file argues about `pull_request` at length, so a
    substring test against the whole text would read its own explanation as
    the trigger it rules out.
    """
    return "\n".join(line for line in STAGED.read_text().splitlines()
                     if not line.lstrip().startswith("#"))


def test_the_staged_workflow_exists():
    """A reader that is not scheduled anywhere is the defect, not the fix.

    This file's whole subject is a correct check that nothing ran at the hour
    it mattered. Shipping the tool without the schedule would be that again,
    so the schedule is asserted here and its remaining hand step is item 21 of
    docs/agents/pending-workflow-changes.md.
    """
    assert STAGED.exists(), f"{STAGED} is the schedule for tools/press_watch.py"


def test_the_staged_workflow_runs_two_hours_after_the_press_cron():
    text = staged_workflow()
    minute, hour = dh.PRESS_CRON.split()[:2]
    grace = int(dh.PRESS_GRACE.total_seconds() // 3600)
    expected = f'cron: "{minute} {int(hour) + grace} * * *"'
    assert expected in text, (
        f"the staged workflow does not run at {dh.PRESS_CRON} plus "
        f"{grace} hours, which is the deadline tools/delivery_health.py "
        f"judges by. It should contain {expected!r}."
    )


def test_the_staged_workflow_runs_daily_and_not_only_on_mondays():
    """The dedupe is what buys this, and the skipped Monday is what needs it."""
    text = staged_workflow()
    assert "* * 1" not in text, (
        "a Monday-only schedule has one firing opportunity a week, in the "
        "hour GitHub is most likely to skip under load"
    )


def test_the_staged_workflow_never_fires_from_a_branch():
    """A workflow that writes to the board must not run on a pull request."""
    text = staged_workflow()
    for trigger in ("pull_request:", "push:"):
        assert trigger not in text, (
            f"the staged workflow carries a {trigger} trigger, so every branch "
            "touching the tool would post a card to the company board"
        )
    assert "workflow_dispatch:" in text, "there is no way to run it by hand"


def test_the_staged_workflow_actually_runs_the_tool():
    text = staged_workflow()
    assert "python3 tools/press_watch.py" in text
    # Without a token the tool cannot post the card, which is the one thing
    # the schedule exists to do.
    assert "BOARD_RUNTIME_TOKEN" in text and "BOARD_API_URL" in text


def test_the_staged_workflow_needs_no_dependency_install():
    """Cheap is in the sprint item's own words, and this is what cheap means.

    The tool is standard library only. A `pip install` step would be thirty
    seconds a day for nothing, and a requirements file that drifts is one more
    way a guardrail stops running.
    """
    assert "pip install" not in staged_workflow()
    source = (ROOT / "tools" / "press_watch.py").read_text()
    for third_party in ("import requests", "import httpx", "import yaml",
                        "import psycopg", "import modal"):
        assert third_party not in source


def test_no_block_of_the_card_is_longer_than_the_board_accepts():
    """The board refuses a block over 420 characters, and refuses the alarm with it.

    This is not arithmetic that happens to hold today. One block quotes the
    press surface's headline, which this function does not control and which
    is over 500 characters on the pipeline surface already, so the card is
    formatted through `board.scannable` rather than measured once by hand.
    """
    body = pw.card_body(press(W40, AFTER), AFTER)
    assert all(len(block) <= board.BODY_BLOCK_LIMIT
               for block in body.split("\n\n")), (
        [len(b) for b in body.split("\n\n")]
    )


def test_a_long_headline_cannot_bounce_the_card():
    """The failure this guards: the week the press surface has most to say."""
    surface = dh.Surface("press", dh.FAILING,
                         "the newest issue is 2026-W40 and 2026-W41 has "
                         "ended, " + "and here is a great deal more "
                         "diagnosis of the same gap, " * 12,
                         {"due": "2026-W41", "newest_week": "2026-W40",
                          "read_via": dh.RECEIPT_URL, "model": "kimi-k2.6",
                          "created_at": "2026-10-05T09:01:04Z"})
    body = pw.card_body(surface, AFTER)
    assert all(len(block) <= board.BODY_BLOCK_LIMIT
               for block in body.split("\n\n"))
    assert "2026-W41" in body


def test_the_nudge_is_formatted_the_same_way():
    nudge = pw.nudge_body(press(W40, AFTER + timedelta(hours=25)),
                          AFTER + timedelta(hours=25))
    assert all(len(block) <= board.BODY_BLOCK_LIMIT
               for block in nudge.split("\n\n"))
