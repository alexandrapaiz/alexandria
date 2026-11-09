"""Does the burn split read a cycle at an instant, and does it exclude a ramp-up week.

Run with `python3 -m pytest tests/test_burn_shares.py -q`.

Every test here builds its own log tree, because the thing under test is a
reader of `/srv/asc/state/.epito/logs` and a checkout has no such directory.

Three properties carry the file, and the first is the one that made the tool
worth writing. HQ's `tools/ration.py` has the same `--now` flag and bounds only
the clock with it, never the run set, so a read at hour 10 of a past cycle
divides that cycle's **whole** spend by ten hours. The first two tests below
are the assertion that flag was missing: a run after the instant is not in the
reading, and the rate at an instant is the rate at that instant.

The third is the baseline exclusion. A week the fleet never filled has a
runs/hour the fleet never chose, so it is no more a baseline for a rate than it
is evidence about a ceiling, and a decomposition anchored on one would report a
growth factor that is mostly the fleet switching on.

`shares` is checked for the property that justifies log shares over arithmetic
ones: the two must sum to one whatever the factors are, so that a factor which
did not move takes none of the growth.
"""

import datetime as dt
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import burn_shares  # noqa: E402

RESET = "You've hit your weekly limit · resets Nov 8, 11pm (UTC)"


def write(root, seat, stamp, cost=None, text=""):
    """One run log, named the way the daemon names them."""
    directory = root / seat
    directory.mkdir(parents=True, exist_ok=True)
    body = text
    if cost is not None:
        body += f' {{"total_cost_usd":{cost}}}'
    body += "\n---\n# exit=0 pr=- session=s turns=40\n"
    (directory / f"{stamp}-message.log").write_text(body)


@pytest.fixture
def tree(tmp_path):
    """Two walled prior cycles and a live one, so a ceiling and a baseline exist."""
    root = tmp_path / "logs"
    write(root, "seat", "2026-10-25T23-10-00-000Z", 1000,
          "You've hit your weekly limit · resets Nov 1, 11pm (UTC)")
    write(root, "seat", "2026-11-01T23-10-00-000Z", 1000, RESET)
    write(root, "seat", "2026-11-08T23-30-00-000Z", 100)
    write(root, "seat", "2026-11-09T03-30-00-000Z", 100)
    write(root, "seat", "2026-11-09T19-30-00-000Z", 9000)
    return root


def at(root, when):
    return burn_shares.read(str(root), dt.datetime.fromisoformat(when))


def test_now_bounds_the_runs_and_not_only_the_clock(tree):
    """The defect this tool exists beside: a later run must not be in the reading."""
    early = at(tree, "2026-11-09T09:00:00+00:00")
    assert early["cycle"]["runs_priced"] == 2
    assert early["cycle"]["spend"] == pytest.approx(200)
    late = at(tree, "2026-11-09T20:00:00+00:00")
    assert late["cycle"]["runs_priced"] == 3
    assert late["cycle"]["spend"] == pytest.approx(9200)


def test_the_rate_at_an_instant_is_that_instants_rate(tree):
    """$9,000 that has not been spent yet cannot be in a burn rate."""
    rate = burn_shares.rates(at(tree, "2026-11-09T09:00:00+00:00")["cycle"])
    # active hours run from the 23:00Z reset to the last priced run at 03:30Z
    assert rate["runs_per_hour"] == pytest.approx(2 / 4.5, rel=1e-6)
    assert rate["per_hour"] == pytest.approx(200 / 4.5, rel=1e-6)
    assert rate["per_run"] == pytest.approx(100)


def test_a_never_walled_cycle_is_not_the_baseline(tmp_path):
    """A ramp-up week is a rate the fleet never chose, so the split skips it."""
    root = tmp_path / "logs"
    write(root, "seat", "2026-10-18T23-10-00-000Z", 5)       # quiet, no refusal
    write(root, "seat", "2026-10-25T23-10-00-000Z", 1000,
          "You've hit your weekly limit · resets Nov 1, 11pm (UTC)")
    write(root, "seat", "2026-11-01T23-10-00-000Z", 1000, RESET)
    write(root, "seat", "2026-11-08T23-30-00-000Z", 400)
    report = at(root, "2026-11-09T09:00:00+00:00")
    assert report["baseline"]["refusals"] > 0
    assert report["baseline"]["start"].date() == dt.date(2026, 10, 25)
    assert report["shares"]["from"].date() == dt.date(2026, 10, 25)


def test_the_two_shares_sum_to_one(tree):
    split = at(tree, "2026-11-09T09:00:00+00:00")["shares"]
    assert split["cost_share"] + split["rate_share"] == pytest.approx(1.0)
    # and the factors multiply back to the growth they were split out of
    assert (split["cost_growth"] * split["rate_growth"]
            == pytest.approx(split["burn_growth"]))


def test_a_factor_that_did_not_move_takes_none_of_the_growth(tmp_path):
    """The property arithmetic shares do not have."""
    root = tmp_path / "logs"
    write(root, "seat", "2026-11-01T23-10-00-000Z", 100, RESET)
    write(root, "seat", "2026-11-01T23-40-00-000Z", 100, "")
    # live cycle: same $/run, twice the runs per hour
    for minute in ("10", "20", "30", "40"):
        write(root, "seat", f"2026-11-08T23-{minute}-00-000Z", 100)
    split = at(root, "2026-11-09T09:00:00+00:00")["shares"]
    assert split["cost_growth"] == pytest.approx(1.0)
    assert split["cost_share"] == pytest.approx(0.0)
    assert split["rate_share"] == pytest.approx(1.0)


def test_no_walled_prior_renders_without_a_share(tmp_path):
    """No baseline is a sentence, not a crash and not a zero."""
    root = tmp_path / "logs"
    write(root, "seat", "2026-11-01T23-10-00-000Z", 10, RESET)
    write(root, "seat", "2026-11-08T23-30-00-000Z", 500)
    report = at(root, "2026-11-09T09:00:00+00:00")
    # the 2026-11-01 cycle carries the dated reset, so it is walled; the
    # cycle before it has no priced run at all and the walk stops there
    assert report["shares"] is not None
    text = burn_shares.render(report)
    assert "$/hour" in text


def test_an_undated_refusal_cannot_anchor_a_cycle(tmp_path):
    """A day of the week is an assumption; only the provider's sentence is a reading."""
    root = tmp_path / "logs"
    write(root, "seat", "2026-11-08T23-30-00-000Z", 100,
          "You've hit your weekly limit")
    with pytest.raises(burn_shares.CouldNotLook):
        at(root, "2026-11-09T09:00:00+00:00")


def test_exit_one_only_while_the_rate_is_the_dominant_term(tree, capsys):
    assert burn_shares.main(["--root", str(tree),
                             "--now", "2026-11-09T09:00:00Z"]) == 1
    assert burn_shares.main(["--root", str(tree),
                             "--now", "2026-11-09T09:00:00Z",
                             "--tolerate", "1.0"]) == 0
    capsys.readouterr()


def test_a_missing_tree_is_could_not_look_and_not_a_zero(tmp_path, capsys):
    assert burn_shares.main(["--root", str(tmp_path / "nope")]) == 3
    assert "could not look" in capsys.readouterr().err


def test_log_shares_are_what_the_docstring_says(tree):
    """Guard the arithmetic itself, not only its output."""
    split = at(tree, "2026-11-09T09:00:00+00:00")["shares"]
    assert split["rate_share"] == pytest.approx(
        math.log(split["rate_growth"]) / math.log(split["burn_growth"]))
