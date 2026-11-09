"""The branch-name gate, tested against the four shapes that answered "free" wrongly.

Incident 32's rule, verbatim: every gate is tested against an artifact known to
fail it before the gate is trusted. The artifacts here are not synthetic. The
clause this gate replaces answered empty for `exo/2026-09-18`, a name carrying
#4, #18 and #30, and empty is the contract's word for proceed. Four more shapes
produce the same empty from the corrected clause without the name being free: a
wrong token, no `gh` on `PATH`, an unreachable host, and a call that hangs. Each
one has a test here, driven by a real `gh` on a real `PATH` rather than a mock,
because the thing under test is an exit code crossing a process boundary.

    python3 -m pytest tests/test_branch_name_free.py -q
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "branch_name_free.py"
spec = importlib.util.spec_from_file_location("branch_name_free", TOOL)
gate = importlib.util.module_from_spec(spec)
sys.modules["branch_name_free"] = gate
spec.loader.exec_module(gate)

# A name this repository genuinely reused, kept literal: three merged pull
# requests, all of them outside any recency window the old clause could see.
REUSED = "exo/2026-09-18"
REUSED_PRS = [4, 18, 30]


@pytest.fixture
def shim(tmp_path):
    """A PATH whose `gh` is a script this test wrote.

    Returns a callable that writes the `gh` body and yields the environment to
    run under. The real PATH stays behind the shim directory, because only the
    first question is being scripted and the second is a real `git ls-remote`.
    `with_gh=False` is the one case that needs `gh` genuinely absent, so there
    the PATH is the shim directory alone with `git` linked into it.
    """
    bindir = tmp_path / "bin"
    bindir.mkdir()

    def make(body, *, with_gh=True):
        env = dict(os.environ)
        if with_gh:
            ghp = bindir / "gh"
            ghp.write_text(body)
            ghp.chmod(0o755)
            env["PATH"] = f"{bindir}{os.pathsep}{env.get('PATH', '')}"
        else:
            (bindir / "git").symlink_to(shutil.which("git"))
            env["PATH"] = str(bindir)
        return env

    return make


def run_tool(env, *args, cwd=None):
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        capture_output=True, text=True, env=env, cwd=str(cwd or REPO),
    )


# ---------------- the shape the old clause got wrong ----------------


def test_a_reused_name_exits_1_and_names_the_pull_requests(shim):
    rows = json.dumps([{"number": n, "state": "MERGED", "url": f"u/{n}"} for n in REUSED_PRS])
    env = shim(f"#!/bin/sh\ncat <<'EOF'\n{rows}\nEOF\n")
    proc = run_tool(env, REUSED)
    assert proc.returncode == gate.TAKEN, proc.stderr
    assert "TAKEN" in proc.stdout
    for n in REUSED_PRS:
        assert f"#{n}" in proc.stdout


def test_the_three_numbers_are_the_ones_the_old_clause_could_not_see(shim):
    """The regression this file exists for, stated as the count rather than a word."""
    rows = json.dumps([{"number": n, "state": "MERGED", "url": ""} for n in REUSED_PRS])
    env = shim(f"#!/bin/sh\ncat <<'EOF'\n{rows}\nEOF\n")
    proc = run_tool(env, REUSED, "--json")
    assert proc.returncode == gate.TAKEN
    out = json.loads(proc.stdout)
    assert out["pull_request_count"] == 3
    assert out["free"] is False


# ---------------- the four false empties ----------------


def test_a_non_zero_exit_is_a_refusal_and_never_free(shim):
    """A wrong or expired token: exit 1, empty stdout. The contract read this as free."""
    env = shim("#!/bin/sh\necho 'HTTP 401: Bad credentials' >&2\nexit 1\n")
    proc = run_tool(env, REUSED)
    assert proc.returncode == gate.CANNOT_LOOK, proc.stdout
    assert "COULD NOT LOOK" in proc.stderr
    assert "not an answer of 'free'" in proc.stderr
    assert proc.stdout == ""


def test_gh_missing_from_path_is_a_refusal(shim):
    env = shim("", with_gh=False)
    proc = run_tool(env, REUSED)
    assert proc.returncode == gate.CANNOT_LOOK
    assert "not on PATH" in proc.stderr


def test_an_empty_stdout_with_a_zero_exit_is_a_refusal(shim):
    """A blank body where json was asked for is an absent answer, not an answer of none.

    This is the same defect as the one the file fixes, one level in, and the
    first version of this fix carried it: `json.loads(out or "[]")` turned a
    missing answer into a confident zero.
    """
    env = shim("#!/bin/sh\nexit 0\n")
    proc = run_tool(env, REUSED)
    assert proc.returncode == gate.CANNOT_LOOK, proc.stdout
    assert "printed nothing" in proc.stderr


def test_output_that_is_not_json_is_a_refusal(shim):
    env = shim("#!/bin/sh\necho 'not json at all'\n")
    proc = run_tool(env, REUSED)
    assert proc.returncode == gate.CANNOT_LOOK
    assert "not json" in proc.stderr


def test_json_that_is_not_a_list_is_a_refusal(shim):
    env = shim("#!/bin/sh\necho '{\"message\": \"Not Found\"}'\n")
    proc = run_tool(env, REUSED)
    assert proc.returncode == gate.CANNOT_LOOK


def test_a_hang_is_a_refusal_and_is_bounded(shim):
    """A gate that hangs stops a run without saying so. Exit 2, inside the budget."""
    env = shim("#!/bin/sh\nsleep 30\n")
    start = time.monotonic()
    proc = run_tool(env, REUSED, "--timeout", "2")
    elapsed = time.monotonic() - start
    assert proc.returncode == gate.CANNOT_LOOK, proc.stdout
    assert "did not answer within 2s" in proc.stderr
    assert elapsed < 20, f"the bound did not hold: {elapsed:.1f}s"


# ---------------- the clean path, which must not be silent ----------------


def test_a_free_name_exits_0_and_still_prints(shim):
    """The inversion this file is about: silence here is a permission, so no silence."""
    env = shim("#!/bin/sh\necho '[]'\n")
    proc = run_tool(env, "sec/a-name-nothing-has-ever-used-9f3c1a")
    assert proc.returncode == gate.FREE, proc.stderr
    assert proc.stdout.strip(), "a gate whose quiet means permission must not be quiet"
    assert "asked GitHub" in proc.stdout


def test_free_in_json_says_which_question_was_asked(shim):
    env = shim("#!/bin/sh\necho '[]'\n")
    proc = run_tool(env, "sec/a-name-nothing-has-ever-used-9f3c1a", "--json")
    out = json.loads(proc.stdout)
    assert out["free"] is True
    assert "--head" in out["asked"]
    assert out["pull_request_count"] == 0


# ---------------- the second question ----------------


def test_a_live_remote_ref_with_no_pull_request_is_taken(shim, tmp_path):
    """A branch pushed and never opened answers nothing to the first question."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)
    for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(work), "config", k, v], check=True)
    (work / "f").write_text("x\n")
    subprocess.run(["git", "-C", str(work), "add", "f"], check=True)
    subprocess.run(["git", "-C", str(work), "commit", "-q", "-m", "c"], check=True)
    subprocess.run(["git", "-C", str(work), "remote", "add", "origin", str(origin)], check=True)
    subprocess.run(["git", "-C", str(work), "push", "-q", "origin", "main:pushed-never-opened"], check=True)

    env = shim("#!/bin/sh\necho '[]'\n")
    proc = run_tool(env, "pushed-never-opened", cwd=work)
    assert proc.returncode == gate.TAKEN, proc.stdout + proc.stderr
    assert "live ref on origin" in proc.stdout

    clean = run_tool(env, "a-name-never-pushed", cwd=work)
    assert clean.returncode == gate.FREE, clean.stdout + clean.stderr


def test_a_broken_remote_is_a_refusal_rather_than_free(shim, tmp_path):
    """The control for the test above: git saying nothing must not read as no."""
    work = tmp_path / "w"
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)
    subprocess.run(
        ["git", "-C", str(work), "remote", "add", "origin", str(tmp_path / "does-not-exist.git")],
        check=True,
    )
    env = shim("#!/bin/sh\necho '[]'\n")
    proc = run_tool(env, "any-name", cwd=work)
    assert proc.returncode == gate.CANNOT_LOOK, proc.stdout
    assert "COULD NOT LOOK" in proc.stderr


# ---------------- the contract itself ----------------


def test_the_three_exit_codes_are_distinct():
    assert len({gate.FREE, gate.TAKEN, gate.CANNOT_LOOK}) == 3
    assert gate.FREE == 0


def test_self_check_prints_and_exits_zero():
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--self-check"], capture_output=True, text=True
    )
    assert proc.returncode == 0
    assert "silence is a permission" in proc.stdout


def test_a_zero_timeout_is_refused_rather_than_accepted():
    """Zero would be a gate that always exits 2, which is a gate nobody reads."""
    proc = subprocess.run(
        [sys.executable, str(TOOL), REUSED, "--timeout", "0"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "must be positive" in proc.stderr


def test_a_name_is_required():
    proc = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "required" in proc.stderr


def test_the_query_is_server_side_on_the_exact_ref(shim, tmp_path):
    """No recency window, which is the half the ExO seat corrected. Asserted on argv."""
    log = tmp_path / "argv.txt"
    env = shim(f"#!/bin/sh\nprintf '%s\\n' \"$@\" > {log}\necho '[]'\n")
    run_tool(env, REUSED)
    argv = log.read_text().split("\n")
    assert "--head" in argv, argv
    assert REUSED in argv
    assert "--state" in argv and "all" in argv
    # The old clause's shape, which must not come back.
    joined = " ".join(argv)
    assert "select(.headRefName" not in joined
