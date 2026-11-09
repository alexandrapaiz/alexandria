"""Does the backlog reader tell an unlooked-at queue from a drained one.

Run with `python3 -m pytest tests/test_pr_backlog.py -q`.

`tools/pr_backlog.py --fetch` calls `gh`, which a pull-request checkout cannot
rely on, so every test here passes saved rows through `--prs` / `--merged` and
pins the clock with `--now`. Nothing here touches the network.

The behaviour worth asserting is the one the tool exists for and the one it
refuses to do. It exists to fail when a non-empty backlog is losing to new
intake, which is the 2026-11-09 instance it was built on. It refuses to call a
queue newest-first on the strength of the backlog alone: with no `--since` there
is no observation of the queue *moving*, and a count of old rows is not evidence
about how they are being served. That refusal is the same shape as
`cron_firing.py`'s `unseen` and as the register's "a date is not an
observation" — an instrument that cannot tell "not yet" from "never" publishes
its worst verdict at the moment its subject is freshest.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import pr_backlog  # noqa: E402

NOW = "2026-11-09T02:00:00Z"


def pr(number, created, merged=None, draft=False, labels=(), title="a row",
       author="alexandrapaiz"):
    row = {
        "number": number,
        "title": title,
        "author": {"login": author},
        "createdAt": created,
        "isDraft": draft,
        "labels": [{"name": n} for n in labels],
        "headRefName": "branch/%d" % number,
    }
    if merged:
        row["mergedAt"] = merged
    return row


def run(tmp_path, open_rows, merged_rows=None, extra=()):
    op = tmp_path / "open.json"
    op.write_text(json.dumps(open_rows))
    argv = ["--prs", str(op), "--now", NOW]
    if merged_rows is not None:
        mp = tmp_path / "merged.json"
        mp.write_text(json.dumps(merged_rows))
        argv += ["--merged", str(mp)]
    argv += list(extra)
    return pr_backlog.main(argv)


def measured(tmp_path, capsys, *args, **kw):
    code = run(tmp_path, *args, extra=list(kw.pop("extra", ())) + ["--json"], **kw)
    return code, json.loads(capsys.readouterr().out)


def test_an_empty_queue_passes(tmp_path, capsys):
    code, m = measured(tmp_path, capsys, [])
    assert code == 0
    assert m["backlog"] == []


def test_rows_newer_than_the_age_cut_are_not_backlog(tmp_path, capsys):
    code, m = measured(tmp_path, capsys, [pr(1, "2026-11-09T01:00:00Z")])
    assert code == 0
    assert m["fresh_count"] == 1 and m["backlog"] == []


def test_the_age_cut_is_the_boundary_and_it_is_exclusive(tmp_path, capsys):
    # exactly 24 h old is not yet older than 24 h, so it is fresh
    code, m = measured(tmp_path, capsys, [pr(1, "2026-11-08T02:00:00Z")])
    assert m["backlog"] == [] and m["fresh_count"] == 1
    code, m = measured(tmp_path, capsys, [pr(1, "2026-11-08T01:59:59Z")])
    assert len(m["backlog"]) == 1


def test_a_backlog_with_no_since_is_unjudged_rather_than_failing(tmp_path, capsys):
    """The refusal this file is really about: old is not the same as neglected."""
    code, m = measured(tmp_path, capsys, [pr(1, "2026-11-02T02:00:00Z")])
    assert code == 0
    assert m["merged_from_backlog"] is None
    assert "drain unmeasured" in m["verdict"]


def test_a_backlog_losing_to_new_intake_fails(tmp_path, capsys):
    """The 2026-11-09 instance: the recovery drained from the newest end."""
    open_rows = [pr(n, "2026-11-02T02:00:00Z") for n in range(1, 33)]
    merged_rows = (
        [pr(100, "2026-11-02T02:00:00Z", merged="2026-11-09T01:00:00Z")] * 1
        + [pr(200 + i, "2026-11-09T00:30:00Z", merged="2026-11-09T01:00:00Z")
           for i in range(11)]
    )
    code, m = measured(tmp_path, capsys, open_rows, merged_rows,
                       extra=["--since", "2026-11-08T23:00:00Z"])
    assert code == 1
    assert m["merged_from_backlog"] == 1 and m["merged_new"] == 11
    assert "newest-first" in m["verdict"]


def test_a_backlog_being_drained_passes(tmp_path, capsys):
    open_rows = [pr(1, "2026-11-02T02:00:00Z")]
    merged_rows = [
        pr(100, "2026-11-02T02:00:00Z", merged="2026-11-09T01:00:00Z"),
        pr(101, "2026-11-02T03:00:00Z", merged="2026-11-09T01:30:00Z"),
        pr(200, "2026-11-09T00:30:00Z", merged="2026-11-09T01:00:00Z"),
    ]
    code, m = measured(tmp_path, capsys, open_rows, merged_rows,
                       extra=["--since", "2026-11-08T23:00:00Z"])
    assert code == 0
    assert m["merged_from_backlog"] == 2 and m["merged_new"] == 1
    assert "draining" in m["verdict"]


def test_a_tie_counts_as_draining(tmp_path, capsys):
    """One-for-one is holding the line, and this tool does not fail a tie."""
    open_rows = [pr(1, "2026-11-02T02:00:00Z")]
    merged_rows = [
        pr(100, "2026-11-02T02:00:00Z", merged="2026-11-09T01:00:00Z"),
        pr(200, "2026-11-09T00:30:00Z", merged="2026-11-09T01:00:00Z"),
    ]
    code, m = measured(tmp_path, capsys, open_rows, merged_rows,
                       extra=["--since", "2026-11-08T23:00:00Z"])
    assert code == 0 and "draining" in m["verdict"]


def test_merges_before_since_are_outside_the_window(tmp_path, capsys):
    open_rows = [pr(1, "2026-11-02T02:00:00Z")]
    merged_rows = [pr(100, "2026-11-01T02:00:00Z", merged="2026-11-02T04:00:00Z")]
    code, m = measured(tmp_path, capsys, open_rows, merged_rows,
                       extra=["--since", "2026-11-08T23:00:00Z"])
    assert m["merged_from_backlog"] == 0 and m["merged_new"] == 0
    # Nothing moved inside the window, so there is nothing to judge. A frozen
    # queue is not a queue served newest-first, and this tool will not say it
    # is: that is the same refusal as the no---since case above.
    assert code == 0
    assert "unjudged" in m["verdict"]


def test_a_hold_is_reported_per_row_and_never_subtracted(tmp_path, capsys):
    """The tool's one honest limit, asserted so a later change has to argue."""
    open_rows = [
        pr(1, "2026-11-02T02:00:00Z", draft=True),
        pr(2, "2026-11-02T03:00:00Z", labels=["hold: owner"]),
        pr(3, "2026-11-02T04:00:00Z"),
    ]
    code, m = measured(tmp_path, capsys, open_rows)
    assert len(m["backlog"]) == 3
    assert m["backlog"][0]["held"] == "draft"
    assert m["backlog"][1]["held"] == "label:hold: owner"
    assert m["backlog"][2]["held"] == ""


def test_the_oldest_row_is_first_so_the_output_can_be_pasted(tmp_path, capsys):
    open_rows = [
        pr(9, "2026-11-05T02:00:00Z"),
        pr(7, "2026-11-02T02:00:00Z"),
        pr(8, "2026-11-03T02:00:00Z"),
    ]
    code, m = measured(tmp_path, capsys, open_rows)
    assert [r["number"] for r in m["backlog"]] == [7, 8, 9]


def test_the_human_output_names_the_oldest_rows_by_number(tmp_path, capsys):
    code = run(tmp_path, [pr(707, "2026-11-02T02:00:00Z", title="the units row")])
    out = capsys.readouterr().out
    assert "#707" in out and "the units row" in out
    assert "because a message is an event" in out


def test_a_missing_author_does_not_crash_the_reader(tmp_path, capsys):
    row = pr(1, "2026-11-02T02:00:00Z")
    del row["author"]
    code, m = measured(tmp_path, capsys, [row])
    assert m["backlog"][0]["author"] == "?"


def test_the_seat_is_the_branch_prefix_and_never_the_author(tmp_path, capsys):
    """The defect this tool shipped with, found by running it on the live queue.

    Every seat in this company pushes with the same GitHub credential, so all
    40 backlog rows reported one author and the grouping said nothing. The
    branch prefix is the discriminator, and it is the one the bus already uses
    to route `pr.merged`.
    """
    rows = [
        pr(1, "2026-11-02T02:00:00Z", author="alexandrapaiz"),
        pr(2, "2026-11-02T03:00:00Z", author="alexandrapaiz"),
        pr(3, "2026-11-02T04:00:00Z", author="alexandrapaiz"),
    ]
    rows[0]["headRefName"] = "alexandria-pm/2026-11-02-a"
    rows[1]["headRefName"] = "alexandria-pm/2026-11-02-b"
    rows[2]["headRefName"] = "alexandria-exo/2026-11-02-c"
    code, m = measured(tmp_path, capsys, rows)
    assert {r["author"] for r in m["backlog"]} == {"alexandrapaiz"}
    assert m["backlog_by_seat"]["alexandria-pm"]["count"] == 2
    assert m["backlog_by_seat"]["alexandria-exo"]["count"] == 1


def test_the_seat_buckets_are_ordered_by_how_many_are_stalled(tmp_path, capsys):
    rows = []
    for i in range(3):
        row = pr(10 + i, "2026-11-02T02:00:00Z")
        row["headRefName"] = "alexandria-pm/r%d" % i
        rows.append(row)
    row = pr(20, "2026-11-01T02:00:00Z")
    row["headRefName"] = "alexandria-exo/old"
    rows.append(row)
    code, m = measured(tmp_path, capsys, rows)
    assert list(m["backlog_by_seat"]) == ["alexandria-pm", "alexandria-exo"]
    # the oldest-row age is per seat, not global
    assert m["backlog_by_seat"]["alexandria-exo"]["oldest_hours"] > \
        m["backlog_by_seat"]["alexandria-pm"]["oldest_hours"]


def test_a_branchless_row_does_not_crash_the_seat_grouping(tmp_path, capsys):
    row = pr(1, "2026-11-02T02:00:00Z")
    row["headRefName"] = ""
    code, m = measured(tmp_path, capsys, [row])
    assert m["backlog"][0]["seat"] == "?"
