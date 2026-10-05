"""The deploy-drift guard: is the merged code the running code.

Sprint 2026-09-28 item 2. Two halves are under test here and they meet in the
middle. `pipeline/runtime_sha.py` rides into each job's Modal image and writes a
digest of the files that job is actually running from. `check_deploy` in
`tools/delivery_health.py` computes the same digest from a git checkout and
compares. The acceptance criterion the sprint names is the last test in this
file: an intentionally stale deploy trips the alarm, and a real deploy clears
it.

The interesting cases are the ones where this guard could cry wolf, and there
are three. A seat's own sandbox nearly always has uncommitted edits, a branch
carries commits that never merged, and a shallow clone cannot date anything.
All three answer `unknown`, and each has a test, because a health check that
goes red on a normal Tuesday is a health check nobody reads by Friday. That is
the argument `tools/delivery_health.py` already makes for its own third state.

No network, no database, no Modal. The git fixture is a real repository in a
temporary directory, because the dating and dirty-tree logic is `git log` and
`git status` and mocking those would test the mock.

Run with `python3 tests/test_deploy_drift.py` or under pytest.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import runtime_sha as rs  # noqa: E402
from tools import delivery_health as dh  # noqa: E402

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


# --------------------------------------------------------------- fake database

class FakeConn:
    """Enough psycopg for this guard: one table, one savepoint, no server."""

    def __init__(self, rows: list[tuple] | None = None, fail: str | None = None):
        self.rows = rows if rows is not None else []
        self.fail = fail
        self.statements: list[str] = []

    def execute(self, sql, params=None):
        self.statements.append(sql)
        if self.fail:
            raise RuntimeError(self.fail)
        return _Result(self.rows)

    def transaction(self):
        return _NullTransaction()


class _Result:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


class _NullTransaction:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


# ------------------------------------------------------------------ git fixture

MANIFEST_FILES = sorted({
    key
    for app in rs.APPS
    for key, _ in rs.local_entries(app, ROOT)
})


def fixture_repo(tmp: Path, days_ago: float) -> Path:
    """A real git repository holding the three jobs and everything they mount.

    One commit, dated `days_ago` days back, which is what `_last_commit_at`
    reads to decide whether a drift is old enough to be an alarm.
    """
    repo = tmp / "repo"
    for key in MANIFEST_FILES:
        dest = repo / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / key, dest)
    when = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    env = {**os.environ,
           "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when,
           "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@example.com"}
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "fixture"]):
        subprocess.run(["git", "-C", str(repo), *args], env=env, check=True,
                       capture_output=True)
    return repo


def row_for(app: str, repo: Path, sha: str | None = None, *,
            notified_at=None, ran_hours_ago: float = 1.0) -> tuple:
    """One `deploy_runtime` row, current for `app` unless `sha` overrides it."""
    now = datetime.now(timezone.utc)
    return (app, sha or rs.digest(rs.local_entries(app, repo)),
            now - timedelta(hours=ran_hours_ago),
            now - timedelta(hours=ran_hours_ago),
            notified_at)


# ------------------------------------------------------- the digest's own rules

def test_the_file_list_is_read_out_of_the_image_not_kept_beside_it():
    """Every file each image adds is in that app's digest, with nothing declared.

    This is the property that makes the guard maintainable: adding a file to an
    image adds it to the digest with nobody remembering to. So the test asserts
    the derivation rather than a fixed list, and separately that every derived
    path is a file that exists.
    """
    for app, module in rs.APPS.items():
        source = (ROOT / module).read_text()
        added = [repo for repo, _ in rs._ADD_FILE.findall(source)]
        keys = [key for key, _ in rs.local_entries(app, ROOT)]
        check(f"{app}: the module itself is hashed", keys[0] == module, str(keys[:1]))
        check(f"{app}: every add_local_file is hashed",
              set(added) <= set(keys), str(set(added) - set(keys)))
        missing = [k for k in keys if not (ROOT / k).is_file()]
        check(f"{app}: every hashed path exists", not missing, str(missing))


def test_the_guard_cannot_be_deployed_without_itself():
    """`runtime_sha.py` is in all three images, or a job cannot record anything.

    Worth its own assertion because the failure is silent in the worst way: the
    job runs, the import fails, the guard prints a line nobody reads, and the
    surface reports the app as never having run rather than as broken.
    """
    for app, module in rs.APPS.items():
        source = (ROOT / module).read_text()
        check(f"{app} mounts pipeline/runtime_sha.py",
              "pipeline/runtime_sha.py" in source)


def test_the_digest_answers_to_content_and_not_to_order_or_location():
    """Same bytes under the same keys, same digest, wherever the files sit."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "a.txt").write_text("alpha")
        (tmp / "b.txt").write_text("beta")
        forward = [("one", tmp / "a.txt"), ("two", tmp / "b.txt")]
        backward = list(reversed(forward))
        check("order does not change the digest",
              rs.digest(forward) == rs.digest(backward))

        moved = tmp / "elsewhere"
        moved.mkdir()
        shutil.copyfile(tmp / "a.txt", moved / "renamed")
        shutil.copyfile(tmp / "b.txt", moved / "also-renamed")
        relocated = [("one", moved / "renamed"), ("two", moved / "also-renamed")]
        check("the same bytes under the same keys hash the same anywhere",
              rs.digest(relocated) == rs.digest(forward),
              "this is what lets a Modal container be compared with a checkout")

        (tmp / "b.txt").write_text("beta!")
        check("one changed byte changes the digest",
              rs.digest(forward) != rs.digest(relocated))

        check("a key that is not there hashes as missing, not as absent",
              rs.digest([("one", tmp / "gone")]) != rs.digest([]))


def test_container_and_checkout_agree_on_the_same_deploy():
    """The two sides meet: a simulated image hashes to the checkout's digest.

    `/root/budget.py` in the image is `pipeline/budget.py` in the repository.
    If the two sides ever keyed on the location rather than on the repository
    path, every comparison would report drift forever and the guard would be
    worse than nothing.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for app, module in rs.APPS.items():
            source = (ROOT / module).read_text()
            box = tmp / app
            box.mkdir()
            # Lay the image out the way Modal does: the module at the root of
            # the image, every added file at the path the manifest names.
            module_file = box / Path(module).name
            shutil.copyfile(ROOT / module, module_file)
            for repo, dest, _is_dir in rs.manifest(source):
                target = box / dest.lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / repo, target)
            entries = [(key, box / str(path).lstrip("/"))
                       for key, path in rs.runtime_entries(app, module_file, source)]
            entries[0] = (module, module_file)
            check(f"{app}: the image and the checkout agree",
                  rs.digest(entries) == rs.digest(rs.local_entries(app, ROOT)))


# ---------------------------------------------------- recording cannot break a job

def test_recording_never_raises_and_never_kills_the_transaction():
    """A guard that can fail the run it guards is worse than no guard.

    Both failure modes are covered: a database that refuses the write, and a
    module path that cannot be read at all.
    """
    conn = FakeConn(fail='relation "deploy_runtime" does not exist')
    sha, line = rs.record_runtime(conn, "triage", str(ROOT / "pipeline/triage.py"))
    check("a refused write still returns a digest", len(sha) == rs.DIGEST_CHARS, sha)
    check("and says plainly that the guard is blind for this run",
          "NOT recorded" in line, line)

    sha, line = rs.record_runtime(FakeConn(), "triage", str(ROOT / "nope.py"))
    check("an unreadable module returns an empty sha", sha == "", sha)
    check("and does not raise", "could not be hashed" in line, line)

    conn = FakeConn()
    sha, line = rs.record_runtime(conn, "weekly", str(ROOT / "pipeline/weekly.py"))
    check("a good write reports the digest it recorded", sha in line, line)
    check("the write is an upsert on one row per app",
          "on conflict (app)" in conn.statements[0])


def test_a_new_deploy_clears_the_alarm_cooldown():
    """`notified_at` survives a re-run of the same code and dies with a new one.

    The reason is the alarm's honesty. A drift that lasts a week should cost one
    mail a day, and a fresh deploy that drifts again tomorrow should get its own
    first alarm rather than inheriting yesterday's silence.
    """
    sql = rs.UPSERT
    check("the same sha keeps the cooldown",
          "then deploy_runtime.notified_at else null end" in sql)
    check("the same sha keeps first_seen_at, so 'live since' means something",
          "then deploy_runtime.first_seen_at else now() end" in sql)


# ------------------------------------------------------------- the check's verdict

def test_a_current_deploy_is_green():
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        conn = FakeConn([row_for(app, repo) for app in rs.APPS])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("three jobs running this checkout reads ok",
              surface.state == dh.OK, f"{surface.state}: {surface.headline}")
        check("and the headline says so plainly",
              "running this checkout" in surface.headline, surface.headline)


def test_an_intentionally_stale_deploy_trips_the_alarm():
    """The sprint's acceptance criterion, first half.

    The repository moved nine days ago and the jobs are still reporting some
    older digest. That is PR #110's exact shape, and until today nothing in this
    repository could see it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        conn = FakeConn([row_for(app, repo, sha="0ldc0dec0de") for app in rs.APPS])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("a nine-day-old drift is failing",
              surface.state == dh.FAILING, f"{surface.state}: {surface.headline}")
        check("the headline names the jobs and how far behind they are",
              all(app in surface.headline for app in rs.APPS), surface.headline)
        check("the evidence carries both digests",
              surface.evidence["triage"]["recorded_sha"] == "0ldc0dec0de"
              and len(surface.evidence["triage"]["expected_sha"]) == rs.DIGEST_CHARS,
              str(surface.evidence.get("triage")))


def test_and_a_real_deploy_clears_it():
    """The sprint's acceptance criterion, second half.

    Same stale repository, same check, and the only thing that changes is that
    the jobs have since run on the current code. Nothing else has to be reset by
    hand, which matters: a guard that needs an acknowledgement is a guard that
    stays acknowledged.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        stale = dh.check_deploy(
            FakeConn([row_for(app, repo, sha="0ldc0dec0de") for app in rs.APPS]),
            repo, notify=False)
        deployed = dh.check_deploy(
            FakeConn([row_for(app, repo) for app in rs.APPS]), repo, notify=False)
        check("stale is red and the deploy turns it green",
              stale.state == dh.FAILING and deployed.state == dh.OK,
              f"{stale.state} then {deployed.state}")


def test_a_drift_younger_than_a_day_is_a_pending_deploy_not_an_alarm():
    """The org merges most days, and most mornings are not an incident."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=0.1)
        conn = FakeConn([row_for(app, repo, sha="0ldc0dec0de") for app in rs.APPS])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("a two-hour-old drift is not red",
              surface.state == dh.OK, f"{surface.state}: {surface.headline}")
        check("and the headline still names the pending deploy",
              "pending" in surface.headline, surface.headline)


def test_a_job_that_never_reported_is_treated_as_drift():
    """No row is not the same as a matching row, and must never read green."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        surface = dh.check_deploy(FakeConn([]), repo, notify=False)
        check("an empty table on a nine-day-old checkout is failing",
              surface.state == dh.FAILING, f"{surface.state}: {surface.headline}")
        check("and the evidence says nothing was recorded",
              surface.evidence["weekly"]["recorded_sha"] is None,
              str(surface.evidence.get("weekly")))


# ------------------------------------------------------- the three honest unknowns

def test_an_uncommitted_edit_is_unknown_and_never_red():
    """A seat's own sandbox is the normal case, and it is not a broken deploy."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        conn = FakeConn([row_for(app, repo) for app in rs.APPS])
        # The edit lands after the row is built, so the row is exactly what the
        # jobs would be running off main and the only thing that differs is the
        # seat's own unsaved work. That is the case this guard must not call red.
        (repo / "pipeline/triage.py").write_text(
            (repo / "pipeline/triage.py").read_text() + "\n# a seat is working here\n")
        surface = dh.check_deploy(conn, repo, notify=False)
        check("a dirty working tree reads unknown",
              surface.state == dh.UNKNOWN, f"{surface.state}: {surface.headline}")
        check("and the headline names the file it cannot account for",
              "pipeline/triage.py" in surface.headline, surface.headline)


def test_a_checkout_that_cannot_date_its_files_is_unknown():
    """A shallow clone cannot tell an hour of drift from a month of it."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        loose = tmp / "loose"
        for key in MANIFEST_FILES:
            (loose / key).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / key, loose / key)
        conn = FakeConn([row_for(app, loose, sha="0ldc0dec0de") for app in rs.APPS])
        surface = dh.check_deploy(conn, loose, notify=False)
        check("no git history means unknown, not failing",
              surface.state == dh.UNKNOWN, f"{surface.state}: {surface.headline}")


def test_a_missing_table_is_unknown_not_a_broken_deploy():
    """`deploy_runtime` lands in db/schema.sql and apply_schema is a hand step."""
    conn = FakeConn(fail='relation "deploy_runtime" does not exist')
    surface = dh.check_deploy(conn, ROOT, notify=False)
    check("a table that is not there yet reads unknown",
          surface.state == dh.UNKNOWN, f"{surface.state}: {surface.headline}")
    check("and the headline names the table",
          "deploy_runtime" in surface.headline, surface.headline)


def test_unknown_and_failing_keep_their_exit_codes_with_five_surfaces():
    """The fifth surface must not break the three-state contract."""
    check("deploy is in the default run order", "deploy" in dh.ORDER)
    check("one failing deploy exits 1",
          dh.exit_code([dh.Surface("deploy", dh.FAILING, "")]) == 1)
    check("one unknown deploy exits 2",
          dh.exit_code([dh.Surface("deploy", dh.UNKNOWN, "")]) == 2)
    check("a green deploy beside a green press exits 0",
          dh.exit_code([dh.Surface("deploy", dh.OK, ""),
                        dh.Surface("press", dh.OK, "")]) == 0)


# -------------------------------------------------------------------- the alarm

def test_the_alarm_is_mailed_once_a_day_and_says_what_to_run():
    """The owner's one action is a deploy command, so the mail leads with it.

    No mail leaves this test. `notify_owner` refuses without a Gmail secret and
    returns the refusal as a string, which is the path a sandbox always takes,
    so what is under test is the wiring and the cooldown rather than SMTP.
    """
    saved = {k: os.environ.pop(k, None)
             for k in ("GMAIL_ADDRESS", "GMAIL_APP_PASSWORD")}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixture_repo(Path(tmp), days_ago=9)
            conn = FakeConn([row_for(app, repo, sha="0ldc0dec0de") for app in rs.APPS])
            surface = dh.check_deploy(conn, repo, notify=True)
            check("the alarm reports back through the surface",
                  "NOT NOTIFIED" in surface.evidence.get("alarm", ""),
                  str(surface.evidence.get("alarm")))

            recent = datetime.now(timezone.utc) - timedelta(hours=2)
            conn = FakeConn([row_for(app, repo, sha="0ldc0dec0de", notified_at=recent)
                             for app in rs.APPS])
            surface = dh.check_deploy(conn, repo, notify=True)
            check("a drift mailed two hours ago is not mailed again",
                  "within the last day" in surface.evidence.get("alarm", ""),
                  str(surface.evidence.get("alarm")))
            check("and it is still reported as failing",
                  surface.state == dh.FAILING, surface.state)

            old = datetime.now(timezone.utc) - timedelta(hours=30)
            conn = FakeConn([row_for(app, repo, sha="0ldc0dec0de", notified_at=old)
                             for app in rs.APPS])
            surface = dh.check_deploy(conn, repo, notify=True)
            check("a drift last mailed 30 hours ago is mailed again",
                  "NOT NOTIFIED" in surface.evidence.get("alarm", ""),
                  str(surface.evidence.get("alarm")))
    finally:
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value


def test_no_notify_leaves_the_owner_alone():
    """A human running this by hand must not be able to mail the owner by accident."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        conn = FakeConn([row_for(app, repo, sha="0ldc0dec0de") for app in rs.APPS])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("--no-notify still reports the drift",
              surface.state == dh.FAILING, surface.state)
        check("and sends nothing",
              surface.evidence.get("alarm") == "not notified",
              str(surface.evidence.get("alarm")))


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print(name)
            fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) failed: {', '.join(FAILURES)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
