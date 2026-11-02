#!/usr/bin/env python3
"""A flag that names nothing must refuse, across the tools tree rather than once.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

The writer seat's note of 2026-11-02 carried the measurement this file acts on.
The tools tree declares 246 arguments, 242 of them carried by a flag, and the
two sweeps for this class passed a bad command name and a bad positional, so
between them they covered four. The class is a flag whose value NAMES something
and is handed a value nothing carries, answered with a confident zero and exit
0. Both recorded instances were in one tool and both were repaired there:

- `INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`
- `INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`

The 242 were classified on 2026-11-02 and the population is much smaller than
the headline: 102 boolean switches have no target, 7 carry `choices=` and are
refused by argparse already, 77 take a number or free text, and 56 name
something resolvable. Eight of those were probed by hand; four refused already
(`cron_firing.py --seat`, `wake_routes.py --seat` both exit 2, `skill_eval.py`
and `skill_scope.py --root` exit 1) and three answered a confident zero. Those
three are repaired here, and the probe is kept as a test so the fourth instance
is a red pull request rather than a fifth incident.

Nothing here reaches a network or a database.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import resolve_target as rt                                      # noqa: E402

#: The three tools measured answering a confident zero on 2026-11-02, with a
#: value nothing carries and the flag that carries it. Each one must refuse.
CONFIDENT_ZEROS = [
    ("ledger.py", ["--status", "no-such-status-xyz"]),
    ("corrections.py", ["--skill", "no-such-skill-xyz"]),
    ("panel_validator.py", ["--skill", "no-such-skill-xyz"]),
]


def run(tool, argv):
    return subprocess.run([sys.executable, str(ROOT / "tools" / tool), *argv],
                          capture_output=True, text=True, timeout=120)


def test_the_exit_code_is_the_one_board_already_uses():
    """4 means "the thing you named is not here", in one tool or in twenty.

    A reader who learns the number on `board.py inbox` and meets a different
    number on the next tool has learned nothing, so this asserts the two agree
    rather than trusting that they were written on the same day.
    """
    board = (ROOT / "tools" / "board.py").read_text()
    assert "EXIT_UNKNOWN_SEAT = 4" in board
    assert rt.EXIT_UNKNOWN_TARGET == 4


def test_each_measured_tool_refuses_a_name_nothing_carries():
    for tool, argv in CONFIDENT_ZEROS:
        done = run(tool, argv)
        said = done.stdout + done.stderr
        assert done.returncode == rt.EXIT_UNKNOWN_TARGET, f"{tool}: {said[:300]}"
        # The refusal has to name the value, or a caller reading a log cannot
        # tell which of its arguments was wrong.
        assert argv[1] in said, f"{tool} refused without naming the value"
        # And a zero must not be the headline of a refusal.
        assert "0 correction" not in said
        assert "0 skills reviewed" not in said
        assert "0 entries at status" not in said


def test_a_real_name_still_works():
    """The repair must not have turned a working filter into a refusal."""
    done = run("ledger.py", ["--status", "accepted"])
    assert done.returncode == 0
    assert "entries at status 'accepted'" in done.stdout + done.stderr


def test_no_filter_is_not_a_refusal():
    """An absent value means "no filter", which is every tool's default."""
    assert rt.check("seat", "", {"a"}) is None
    assert rt.check("seat", None, {"a"}) is None


def test_the_refusal_never_guesses():
    """A fuzzy fallback turns a typo into a read of the wrong subject.

    That is strictly worse than the confident zero it would replace, because a
    zero is at least visibly nothing.
    """
    said = rt.refuse("skill", "agent-contaiment", {"agent-containment"})
    source = (ROOT / "tools" / "resolve_target.py").read_text()
    assert "agent-containment" in said          # printed as the roster
    for guesser in ("difflib", "get_close_matches", "SequenceMatcher",
                    "levenshtein", "startswith("):
        assert guesser not in source


def test_skills_are_read_off_disk_rather_than_listed():
    """A hardcoded roster goes stale the day a skill is promoted."""
    on_disk = {d.name for d in (ROOT / "skills").iterdir()
               if d.is_dir() and d.name != "_validation"}
    assert rt.skill_slugs() == on_disk
    assert on_disk                                # the fixture is not empty


def test_the_resolver_carries_its_own_smoke():
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "resolve_target.py"),
                          "--smoke"], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "FAIL:" not in out.stdout


def test_the_ledger_vocabulary_is_the_charters_five():
    """The statuses belong to the ledger contract, so the refusal must print those.

    A sixth status invented here would make the refusal itself wrong.
    """
    charter = (ROOT / "prompts" / "engineer-agent.md").read_text()
    import ledger
    for status in ledger.VALID_STATUSES:
        assert f"`{status}`" in charter
    assert len(ledger.VALID_STATUSES) == 5
