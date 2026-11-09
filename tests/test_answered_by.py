"""Does the marker reader tell a clock join from a reply link.

Run with `python3 -m pytest tests/test_answered_by.py -q`.

Nothing here touches the bus. Every case builds a message list in the board's
exact row shape and passes it through `--fixture`, which is the same code path
a live run takes, because two paths that agree on nothing but their output are
how `answered_by` itself came to be read as a reply pointer.

The property under test is the one the tool's verdict rests on: the reader must
find the clock join **when it is there** and must stop finding it the moment a
marking stops being reconstructible or a sender-written reply link appears. A
reader that always answers "clock join" would pass every live reading today and
would still be wrong on the first day the board is fixed, which is exactly the
day somebody acts on it.
"""

import json
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import answered_by as ab  # noqa: E402

SEAT = ("alexandria", "exo")


def note(ts, sender, subject, answered=None, **extra):
    row = {
        "id": f"in-{ts}",
        "ts": ts,
        "kind": "note",
        "from_company": sender[0],
        "from_seat": sender[1],
        "to_company": SEAT[0],
        "to_seat": SEAT[1],
        "subject": subject,
        "body": subject,
    }
    if answered is not None:
        row["answered_by"] = {
            "by": "alexandria/exo",
            "kind": "note",
            "message": answered,
            "subject": "whatever this seat said next",
            "ts": ts,
        }
    row.update(extra)
    return row


def reply(mid, ts, to, subject="a letter out"):
    return {
        "id": mid,
        "ts": ts,
        "kind": "note",
        "from_company": SEAT[0],
        "from_seat": SEAT[1],
        "to_company": to[0],
        "to_seat": to[1],
        "subject": subject,
        "body": subject,
    }


def run(tmp_path, rows, *argv):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    # `--seat` is explicit here because the tool refuses without one. It used
    # to default to `exo`, which meant a seat running the bare command got a
    # confident report about the ExO seat's mailbox and nothing in the verdict
    # said so; `alexandria/security` hit that on 2026-11-09 and routed it here
    # rather than changing a default this seat has a standing read against.
    return ab.main(["--fixture", str(path), "--seat", SEAT[1], *argv])


def test_a_read_with_no_seat_refuses_rather_than_choosing_one(tmp_path, monkeypatch):
    """The wrong-seat report is the only error here a reader cannot detect.

    A zero invites a second look. A plausible `123 of 123` about somebody
    else's mailbox does not, which is why this refuses instead of falling
    back to the seat that happens to own the file.
    """
    path = tmp_path / "rows.json"
    path.write_text(json.dumps([]), encoding="utf-8")
    monkeypatch.delenv("ASC_SEAT", raising=False)
    with pytest.raises(SystemExit) as exc:
        ab.main(["--fixture", str(path)])
    assert exc.value.code == 2


def test_asc_seat_is_accepted_and_its_company_prefix_stripped(tmp_path, monkeypatch, capsys):
    """`ASC_SEAT` is `alexandria-exo` in the runtime, not `exo`.

    The host's own name for a seat carries the company, so a reader that
    takes the variable verbatim queries a seat name the bus does not
    carry — and §2 of the charter is explicit that such a read answers
    with a confident zero.
    """
    path = tmp_path / "rows.json"
    path.write_text(json.dumps([]), encoding="utf-8")
    monkeypatch.setenv("ASC_SEAT", "alexandria-exo")
    assert ab.main(["--fixture", str(path)]) == 0
    assert "alexandria/exo" in capsys.readouterr().out


def measured(tmp_path, rows):
    import argparse

    path = tmp_path / "rows.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    args = argparse.Namespace(
        company=SEAT[0], seat=SEAT[1], window_hours=240, fixture=str(path)
    )
    inbound, outbound = ab.load(args)
    return ab.measure(inbound, outbound)


SKILL = ("alexandria", "skill")
SEC = ("alexandria", "security")


def test_the_join_is_per_correspondent_not_global(tmp_path):
    """The hypothesis that fails at 28% and the one that holds at 100%.

    A letter to the security seat sits between the skill seat's note and this
    seat's answer to it. Joined globally the prediction is that letter and the
    marking looks unexplained; joined per correspondent it is exact. The live
    board answers 32 of 113 the first way and 113 of 113 the second, so a
    reader that tests only the global form reports the field as *partly*
    meaningful, which is the worst of the three available answers.
    """
    rows = [
        note("2026-11-09T10:08:00", SKILL, "the clock join has a second instance", "out-2"),
        reply("out-1", "2026-11-09T10:12:00", SEC, "unrelated, to another seat"),
        reply("out-2", "2026-11-09T10:25:00", SKILL, "both taken"),
    ]
    found = measured(tmp_path, rows)
    assert found["marked"] == 1
    assert found["reconstructed"] == 1
    assert found["unreconstructed"] == 0


def test_a_marking_that_is_not_the_next_letter_is_reported_unreconstructed(tmp_path):
    """The condition this tool is waiting for, and it must not be swallowed.

    If the board ever writes a marking the clock cannot explain, that is the
    first evidence the field has become something a router could key on. So it
    is counted and printed rather than folded into the reconstructed share.
    """
    rows = [
        note("2026-11-09T10:08:00", SKILL, "a note", "out-2"),
        reply("out-1", "2026-11-09T10:12:00", SKILL, "the next letter to that seat"),
        reply("out-2", "2026-11-09T10:25:00", SKILL, "a later one, named anyway"),
    ]
    found = measured(tmp_path, rows)
    assert found["reconstructed"] == 0
    assert found["unreconstructed"] == 1


def test_the_pigeonhole_floor_counts_every_group_but_one_per_group(tmp_path):
    """Six notes under one answer is five false markings, not six and not one.

    The floor is the number this seat quotes at a router, so its arithmetic is
    worth a case of its own: a group of N contributes N-1, and singletons
    contribute nothing because the pigeonhole says nothing about them.
    """
    rows = [
        note("2026-11-02T05:10:29", SEC, "one", "out-many"),
        note("2026-11-02T05:10:46", SEC, "two", "out-many"),
        note("2026-11-02T05:11:00", SEC, "three", "out-many"),
        note("2026-11-02T05:11:17", SEC, "four", "out-many"),
        note("2026-11-02T05:32:32", SEC, "five", "out-many"),
        note("2026-11-02T05:32:59", SEC, "six", "out-many"),
        note("2026-11-02T06:00:00", SKILL, "a singleton", "out-one"),
        reply("out-many", "2026-11-02T05:35:00", SEC),
        reply("out-one", "2026-11-02T06:10:00", SKILL),
    ]
    found = measured(tmp_path, rows)
    assert found["marked"] == 7
    assert found["largest_group"] == 6
    assert found["shared_answers"] == 1
    assert found["notes_sharing_an_answer"] == 6
    assert found["false_markings_floor"] == 5


def test_the_forward_join_is_unbounded_and_the_lag_says_so(tmp_path):
    """A week-old note claimed by today's letter, which is the live case.

    One real group holds a skill-seat note of 11-02 and one of 11-09 under the
    same answer. The lag is the only field that makes that visible in a summary,
    and it is the direction a reader guesses wrong: an unanswered note is not
    left unmarked, it is marked later.
    """
    rows = [
        note("2026-11-02T02:42:32", SKILL, "nothing answered this for a week", "out-late"),
        reply("out-late", "2026-11-09T10:25:00", SKILL),
    ]
    found = measured(tmp_path, rows)
    assert found["marked_over_a_day_later"] == 1
    assert found["lag_minutes_max"] > 7 * 24 * 60


def test_the_verdict_refuses_while_the_field_is_a_clock_join(tmp_path):
    """`--as-reply-link` is the question a wake-suppressing router asks.

    Exit 1 is the answer "no". It is deliberately not the default exit, because
    the condition is board-side and no commit in this repository can clear it,
    and a gate that reds `main` over an unfixable condition gets excused rather
    than read.
    """
    rows = [
        note("2026-11-09T10:08:00", SKILL, "a note", "out-1"),
        reply("out-1", "2026-11-09T10:25:00", SKILL),
    ]
    assert run(tmp_path, rows) == 0
    assert run(tmp_path, rows, "--as-reply-link") == 1


def test_a_sender_written_reply_link_flips_the_verdict_green(tmp_path):
    """The grant this tool exists to notice, arriving as a column.

    The ask open with the board's owner is an `in_reply_to` written by the
    sender, who is the only party holding the id. When one appears the verdict
    must go to 0 on the same rows that refused a moment before, so the next run
    learns the board moved without re-deriving anything.
    """
    rows = [
        note("2026-11-09T10:08:00", SKILL, "a note", "out-1", in_reply_to="some-earlier-id"),
        reply("out-1", "2026-11-09T10:25:00", SKILL),
    ]
    found = measured(tmp_path, rows)
    assert found["reply_link_fields_present"] == ["in_reply_to"]
    assert found["usable_as_reply_link"] is True
    assert run(tmp_path, rows, "--as-reply-link") == 0


def test_an_empty_window_is_not_read_as_a_fixed_board(tmp_path):
    """No rows is no evidence, and it must not pass as a reply link.

    The failure mode worth refusing: a seat with a quiet inbox runs this, sees
    nothing refused, and concludes suppression is safe. Zero markings is zero
    markings.
    """
    found = measured(tmp_path, [])
    assert found["marked"] == 0
    assert found["usable_as_reply_link"] is False
    assert run(tmp_path, [], "--as-reply-link") == 1
