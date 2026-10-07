"""The ban list's quoted enforcements, checked by the suite rather than by hand.

`docs/voice/check_voice.py` holds three editorial checks that were prose rules
until 2026-10-04, and its own docstring says what is still wrong with it:

    Not wired to anything yet, which is the honest half of L-A22: until a
    command that already runs calls this, these three are enforced at the
    reliability of someone choosing to type it. Filed in docs/ideas.md for the
    engineer, to move to tools/ and add to .github/workflows/checks.yml beside
    check_registers.py.

This file is the smaller half of that, taken by the engineer seat on
2026-10-07 because the larger half is a file move across a seat boundary and
this is not. The command that already runs is `python3 -m pytest tests/ -q`,
so the check runs there.

Only `enforcements` is wired. That is deliberate and the other two are not
oversights. `stale` and `measure` both return 0 by construction: the first
prints hits that "each is read by hand, because the tell cannot tell the two
apart", and the second prints a character census so a grade cannot carry a
figure between two artifacts. Neither has a verdict, so a test calling either
would assert that a report printed, which is the kind of green that teaches a
reader to trust a suite less. `enforcements` returns `1 if missing else 0` and
is a real assertion.

What it asserts: ban list 92 says an entry's second ending quotes the
generator text that now enforces it, on its own line, as
`LANDED prompts/digest.md: "..."`. Nine entries carry one. This checks that
all nine quotes are still present in `prompts/digest.md`, matched on
normalised whitespace because both files wrap their prose. An editorial merge
that rewrites the generator and leaves the register pointing at text that is
gone now turns red on the pull request that does it.

No network, no database. Both files are in the checkout.

Run with `python3 -m pytest tests/test_voice_enforcements.py -q`.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "docs" / "voice" / "check_voice.py"


def _load():
    """Import `docs/voice/check_voice.py`, which is not on any import path.

    It lives under `docs/` because it is the writer seat's register's own
    tool, and the ledger item that would move it to `tools/` is still open.
    Loading it by path rather than moving it keeps this test from being a
    cross-seat file change.
    """
    spec = importlib.util.spec_from_file_location("check_voice", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_voice"] = module
    spec.loader.exec_module(module)
    return module


def test_the_checker_is_where_this_test_thinks_it_is():
    assert CHECKER.exists(), (
        f"{CHECKER.relative_to(ROOT)} is gone. If it moved to tools/, which is "
        "the open ledger item for it, update this test's path rather than "
        "deleting the test: the check is the point, not the location."
    )


def test_every_quoted_enforcement_is_still_in_the_generator(capsys):
    check_voice = _load()
    rc = check_voice.enforcements()
    out = capsys.readouterr().out
    # The checker prints a failing entry as `  FAIL    entry  54  path: "..."`.
    # Reading its stdout rather than reaching into it keeps this test honest
    # about the one interface that file actually offers a caller: a return
    # code and a report.
    failed = [line for line in out.splitlines() if line.strip().startswith("FAIL")]
    assert rc == 0, (
        "a ban-list entry quotes generator text that is no longer in "
        "prompts/digest.md, so the register points at a rule the generator "
        "has stopped carrying:\n" + "\n".join(failed)
    )


def test_the_check_is_measuring_something(capsys):
    """A green check over zero entries is not a green check.

    The ratio in ban list 92 is meant to climb, so this asserts only a floor:
    the nine entries that carried a quoted ending on 2026-10-04 are still
    being verified. If the count drops, either entries lost their quotes or
    the parser stopped finding them, and both of those read as a pass.
    """
    check_voice = _load()
    check_voice.enforcements()
    out = capsys.readouterr().out
    verified = [line for line in out.splitlines() if line.strip().startswith("OK")]
    assert len(verified) >= 9, (
        f"only {len(verified)} quoted enforcements were verified, against 9 on "
        "2026-10-04. The ratio in ban list 92 is meant to climb, so a fall is "
        "either entries losing their quotes or the parser losing the entries."
    )
