"""The `check()` harness is enforced under pytest, proved by running pytest.

Two files in this suite report failures by appending to a module-level
`FAILURES` list rather than by asserting: `test_press_resilience.py` and
`test_press_rehearsal.py`. Both are older than pytest's presence here and both
are run as scripts by `.github/workflows/checks.yml`, where their `__main__`
block exits 1 and CI reads the exit code.

Under `python3 -m pytest tests/ -q`, the command `requirements-dev.txt`
prescribes, that block never runs. Until the hook in `tests/conftest.py` was
written, nothing else read `FAILURES` either, so every `check()` failure in
those two files printed `FAIL` to a stdout `-q` swallows and the suite reported
green. `test_call_model_walks_and_backs_off` is what that cost: it asserted a
contract the press had stopped honouring on 2026-09-24 and was only ever caught
because checks.yml happens to run its file as a script.

A hook that silently stops working looks exactly like a hook that is working,
so this file does not read the hook. It runs pytest in a subprocess against
throwaway modules that use the pattern, and checks the exit code and the
attribution. The subprocess gets a copy of the real `tests/conftest.py`, so if
someone deletes the hook, these tests go red rather than passing vacuously.
"""

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

CONFTEST = Path(__file__).resolve().parent / "conftest.py"

PATTERN = '''
FAILURES = []


def check(name, condition, detail=""):
    if condition:
        print(f"  ok   {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL {name}: {detail}")
'''


def run_pytest_on(tmp_path, body):
    """pytest, in a subprocess, on one module that uses the `check()` pattern."""
    shutil.copy(CONFTEST, tmp_path / "conftest.py")
    (tmp_path / "test_subject.py").write_text(PATTERN + textwrap.dedent(body))
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, check=False,
    )


def test_a_failed_check_fails_the_test(tmp_path):
    """The whole point. Before the hook this exited 0."""
    result = run_pytest_on(tmp_path, """
        def test_the_subject():
            check("this one holds", True)
            check("this one does not", False, "1 is not 2")
    """)
    assert result.returncode != 0, f"pytest exited 0:\n{result.stdout}"
    assert "1 failed" in result.stdout, result.stdout
    # the detail reaches the report, not just the swallowed stdout
    assert "1 is not 2" in result.stdout, result.stdout


def test_a_clean_module_still_passes(tmp_path):
    """A gate that fails everything is not a gate."""
    result = run_pytest_on(tmp_path, """
        def test_the_subject():
            check("all well", True)
    """)
    assert result.returncode == 0, result.stdout
    assert "1 passed" in result.stdout, result.stdout


def test_each_test_answers_only_for_its_own_failures(tmp_path):
    """The snapshot is per test, so a later clean test is not blamed.

    `FAILURES` is module state that accumulates across the whole module. Reading
    its length rather than the slice appended during this test would fail every
    test after the first failing one, which is how a useful signal turns into
    noise nobody reads.
    """
    result = run_pytest_on(tmp_path, """
        def test_a_broken_one():
            check("broken", False, "the only real failure")

        def test_a_clean_one_after_it():
            check("clean", True)
    """)
    assert "1 failed, 1 passed" in result.stdout, result.stdout
    assert "test_a_broken_one" in result.stdout, result.stdout


def test_a_raising_test_keeps_its_own_traceback(tmp_path):
    """A real exception outranks a list of strings.

    A test that appends and then raises has a verdict already, and the
    traceback is the more useful one. Reporting the appended line instead would
    bury the cause.
    """
    result = run_pytest_on(tmp_path, """
        def test_the_subject():
            check("appended before the raise", False, "must not bury the cause")
            raise ValueError("the real cause")
    """)
    assert result.returncode != 0, result.stdout
    assert "ValueError: the real cause" in result.stdout, result.stdout
    assert "check() failure" not in result.stdout, result.stdout


def test_a_module_without_the_pattern_is_untouched(tmp_path):
    """Most of this suite asserts normally. The hook must not notice them."""
    shutil.copy(CONFTEST, tmp_path / "conftest.py")
    (tmp_path / "test_subject.py").write_text(
        "def test_plain():\n    assert 1 + 1 == 2\n")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "1 passed" in result.stdout, result.stdout


def test_both_real_files_still_carry_the_pattern_this_hook_exists_for():
    """If they stop, this file and the hook are dead weight and should go.

    Cheap, and it is the only thing that keeps the hook honest about its own
    reason for existing. A conftest hook guarding a pattern no file uses any
    more is worse than no hook: it reads as coverage.
    """
    tests = Path(__file__).resolve().parent
    for name in ("test_press_resilience.py", "test_press_rehearsal.py"):
        source = (tests / name).read_text()
        assert "\nFAILURES = []" in source, f"{name} no longer owns a FAILURES list"
        assert "def check(" in source, f"{name} no longer defines check()"
