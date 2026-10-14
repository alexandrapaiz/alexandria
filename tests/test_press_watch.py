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
    assert "1 minutes ago" in body
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
    assert "none at all" in body


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
