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

**This docstring claimed all three answered `unknown` and that each had a test,
and the middle one had neither, from 2026-09-28 until 2026-10-09.** Nothing in
the surface ever looked at which branch it was standing on. The cost was not
a false alarm, it was the opposite: a branch commit dated the drift from
itself, so the guard read `ok` on every seat's run while the live `triage`
image was four days behind the trunk, and it told the truth only in a `main`
worktree somebody made by hand. The hazard was written down here, in the right
file, by the seat that owned it, and nothing between the sentence and the
artifact ever checked it. That is incident 20's shape and it is recorded as
`INC-2026-10-09-the-deploy-guard-judged-the-branch-it-ran-from`.

So the three cases now read: a dirty sandbox is reported and changes no
verdict, a branch is not the subject of the question at all, and a shallow
clone still answers `unknown`. Each has a test below, and this time the branch
one is `test_a_branch_commit_does_not_reset_the_drift_clock`.

No network, no database, no Modal. The git fixture is a real repository in a
temporary directory, because the dating and dirty-tree logic is `git log` and
`git status` and mocking those would test the mock. The fixtures name their
branch `main` explicitly rather than taking `git init`'s default, because the
default is `master` on some hosts and `main` on others and that would decide
which of two code paths the whole file exercises.

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

MANIFEST_TRIAGE = rs.local_entries("triage", ROOT)

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
    for args in (["init", "-q", "-b", "main"], ["add", "-A"],
                 ["commit", "-qm", "fixture"]):
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
        check("every job running the trunk reads ok",
              surface.state == dh.OK, f"{surface.state}: {surface.headline}")
        # Derived from APPS, not the literal "all 3 jobs" this carried until
        # 2026-10-09. The rows above already come from APPS, so a hardcoded
        # count here fails the day the guard starts watching one more job,
        # which is a test that blocks the fix it should be checking.
        check("and the headline names the ref it judged, not 'this checkout'",
              surface.headline == f"all {len(rs.APPS)} jobs are running main",
              surface.headline)


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
    """The org merges most days, and most mornings are not an incident.

    The row here holds the digest of the commit BEFORE the edit, which is what
    a real deploy's row holds: the image was built from the trunk as it stood,
    and then somebody merged. Until 2026-10-23 this fixture recorded a digest
    matching no commit at all, which is the shape of a shallow clone rather
    than of a recent merge. The two have to answer differently, because one is
    a pending deploy and the other is a question the checkout cannot answer,
    and `test_a_checkout_that_cannot_place_the_image_is_not_a_green_deploy` is
    the other half of that pair.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [
            ("pipeline/llm.py", "A change merged two hours ago"),
        ], base_days_ago=1.1)
        deployed = {app: dh._digest_at(repo, app, "HEAD~1", {}) for app in rs.APPS}
        conn = FakeConn([row_for(app, repo, sha=deployed[app]) for app in rs.APPS])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("a two-hour-old drift is not red",
              surface.state == dh.OK, f"{surface.state}: {surface.headline}")
        check("and the headline still names the pending deploy",
              "pending" in surface.headline, surface.headline)
        check("and it was dated from the undeployed commit, not from the file",
              surface.evidence["triage"]["drift_anchor"]
              == "the oldest undeployed commit",
              str(surface.evidence["triage"].get("drift_anchor")))


def test_a_checkout_that_cannot_place_the_image_is_not_a_green_deploy():
    """The shallow-clone hole, which was open to every seat for two weeks.

    Every agent seat runs from `git clone --depth 1`. One commit of history
    means the replay in `undeployed_commits` can never match the running
    digest, so `drift_began` falls back to the newest commit to the app's
    files, which in a shallow clone is that single commit and is hours old.
    The surface then reported a pending deploy inside its grace window.

    Measured on the live repository on 2026-10-23, same tree and same rows,
    with the only difference being the clone: shallow read `ok, a deploy is
    pending and still inside the 24h window: distill (0.1h), ingest (0.1h),
    weekly (0.1h)`, and the same checkout after `git fetch --unshallow` read
    three apps between 7.3 and 8.2 days behind. `weekly` is the press.

    So an undated drift inside the window is `unknown`. The one outside it
    still alarms, which is `test_an_undatable_drift_falls_back_to_the_old_anchor`
    and is unchanged: under-reporting the number is the old and correct
    behaviour, and reporting the state as green was never part of it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=0.1)
        conn = FakeConn([row_for(app, repo, sha="0ldc0dec0de") for app in rs.APPS])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("an image this checkout cannot place is not green",
              surface.state == dh.UNKNOWN, f"{surface.state}: {surface.headline}")
        check("and the headline says the comparison is what failed",
              "cannot be compared" in surface.headline, surface.headline)
        triage = surface.evidence["triage"]
        check("and the evidence says why, in the app's own row",
              "matches no commit this checkout can see" in triage.get("why", ""),
              str(triage.get("why")))
        check("while the number it could not trust is still on the page",
              "drift_hours" in triage, str(sorted(triage)))


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

def test_an_uncommitted_edit_changes_no_verdict_and_is_still_reported():
    """A seat's own sandbox is the normal case, and it is not a broken deploy.

    This used to read `unknown`, which was right while the surface hashed the
    disk: a dirty file made the comparison meaningless. The surface hashes a
    commit now, so the edit cannot reach either half of the comparison and the
    honest answer is the one the trunk gives. The edit is still named in the
    evidence, because a reader whose sandbox differs from the verdict is owed
    the reason it differs.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        conn = FakeConn([row_for(app, repo) for app in rs.APPS])
        # The edit lands after the row is built, so the row is exactly what the
        # jobs would be running off main and the only thing that differs is the
        # seat's own unsaved work. That is the case this guard must not call red.
        (repo / "pipeline/triage.py").write_text(
            (repo / "pipeline/triage.py").read_text() + "\n# a seat is working here\n")
        surface = dh.check_deploy(conn, repo, notify=False)
        check("a dirty working tree is green, because the trunk is current",
              surface.state == dh.OK, f"{surface.state}: {surface.headline}")
        check("and the evidence names the file the sandbox has changed",
              surface.evidence["triage"].get("uncommitted_here")
              == ["pipeline/triage.py"], str(surface.evidence["triage"]))
        check("and an app the sandbox did not touch carries no such note",
              "uncommitted_here" not in surface.evidence["weekly"],
              str(surface.evidence["weekly"]))


def test_a_branch_commit_does_not_reset_the_drift_clock():
    """The defect of 2026-10-09: the guard judged whatever branch ran it.

    Every agent seat runs on its own branch and commits within the hour, so
    "is this checkout deployed" had a fresh answer every single run. On
    2026-10-09 the same guard read `ok` on an engineer branch and `FAILING`
    ("triage is 3.9 days behind") in a clean `main` worktree, in the same
    minute, off the same row. This is that, in a fixture: `main` is four days
    ahead of the deployed image, a branch adds a commit a minute ago, and the
    verdict must not move.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp),
                               [("pipeline/triage.py", "A merged change")],
                               base_days_ago=5.0)
        deployed = _shas(repo)[0]
        rows = [row_for(app, repo, sha=_digest_at_commit(repo, app, deployed))
                for app in rs.APPS]

        on_main = dh.check_deploy(FakeConn(rows), repo, notify=False)
        check("on main, a four-day-old merge is an alarm",
              on_main.state == dh.FAILING, f"{on_main.state}: {on_main.headline}")

        # The seat's own branch, with a commit made right now. Before the fix
        # this reset `_last_commit_at` to minutes and the alarm went quiet.
        for args in (["checkout", "-q", "-b", "engineer/today"],):
            subprocess.run(["git", "-C", str(repo), *args], check=True,
                           capture_output=True)
        target = repo / "pipeline/triage.py"
        target.write_text(target.read_text(encoding="utf-8")
                          + "\n# the seat's own work, not merged\n",
                          encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                       capture_output=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.com",
                        "-c", "user.name=test", "commit", "-qm",
                        "Today's unmerged work"], check=True, capture_output=True)

        on_branch = dh.check_deploy(FakeConn(rows), repo, notify=False)
        check("on a branch, the same drift is still the same alarm",
              on_branch.state == dh.FAILING,
              f"{on_branch.state}: {on_branch.headline}")
        check("and the two runs agree on the headline",
              on_branch.headline == on_main.headline,
              f"branch: {on_branch.headline}\nmain:   {on_main.headline}")
        check("and the commit it names is the merged one, not the branch's",
              "A merged change" in on_branch.headline
              and "Today's unmerged work" not in on_branch.headline,
              on_branch.headline)
        check("and the evidence says which ref it judged",
              on_branch.evidence["ref"] == "main",
              str(on_branch.evidence.get("ref")))


def test_the_trunk_is_preferred_over_a_local_branch_of_the_same_name():
    """A seat's sandbox has `origin/main`, and that is the trunk, not `main`.

    The workflows check out a branch and fetch the remote, so a stale local
    `main` can exist beside a current `origin/main`. The remote-tracking ref is
    the one a hand deploys from, so it wins.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        check("with only main, main is the subject",
              dh._deployable_ref(repo) == "main", dh._deployable_ref(repo))
        subprocess.run(["git", "-C", str(repo), "update-ref",
                        "refs/remotes/origin/main", "HEAD"], check=True,
                       capture_output=True)
        check("with both, origin/main is the subject",
              dh._deployable_ref(repo) == "origin/main",
              dh._deployable_ref(repo))


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


# ------------------------------------------ which commits, not only how many days

# The ledger entry of 2026-10-08 that asked for this, in its own words: "2.9
# days behind" does not tell a reader whether the drift is a docstring or a
# provider change. These tests are about that sentence. The surface has no
# commit sha to read, because the container that writes the row was built from
# an image and cannot know which commit produced it, so the commit is recovered
# by replaying the digest over history until one matches.


def fixture_history(tmp: Path, edits: list[tuple[str, str]],
                    base_days_ago: float = 9.0,
                    extra: list[str] = ()) -> Path:
    """A repository with a first commit and then one commit per edit.

    The first commit is the deployed state: a caller takes its digest before
    applying the edits. Each later commit touches one file with one subject, so
    a test can assert on the names it gets back.
    """
    repo = tmp / "repo"
    for key in list(MANIFEST_FILES) + list(extra):
        dest = repo / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / key, dest)

    base = datetime.now(timezone.utc) - timedelta(days=base_days_ago)

    def git(*args, when):
        env = {**os.environ,
               "GIT_AUTHOR_DATE": when.isoformat(),
               "GIT_COMMITTER_DATE": when.isoformat(),
               "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@example.com",
               "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@example.com"}
        subprocess.run(["git", "-C", str(repo), *args], env=env, check=True,
                       capture_output=True)

    git("init", "-q", "-b", "main", when=base)
    git("add", "-A", when=base)
    git("commit", "-qm", "the deployed state", when=base)
    for n, (path, subject) in enumerate(edits, start=1):
        target = repo / path
        target.write_text(target.read_text(encoding="utf-8") + f"\n# edit {n}\n",
                          encoding="utf-8")
        git("add", "-A", when=base + timedelta(days=n))
        git("commit", "-qm", subject, when=base + timedelta(days=n))
    return repo


def _strip_recording(repo: Path, app: str) -> None:
    """Take the `record_runtime` call out of one app's module in a fixture.

    An app in `APPS` whose module does not call it is the state the real
    repository forbids (`test_every_watched_app_records_its_own_runtime`) and
    the state the guard still has to judge, because the two are a pair: the
    rule is what makes "no row" mean "no deploy", and the judgement has to
    hold when the rule is broken rather than guess.
    """
    module = repo / rs.APPS[app]
    marker = f'record_runtime(conn, "{app}"'
    kept = [line for line in module.read_text(encoding="utf-8").splitlines(True)
            if marker not in line]
    module.write_text("".join(kept), encoding="utf-8")


def _commit(repo: Path, message: str, when: datetime, init: bool = False) -> None:
    env = {**os.environ,
           "GIT_AUTHOR_DATE": when.isoformat(), "GIT_COMMITTER_DATE": when.isoformat(),
           "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@example.com"}
    steps = ([["init", "-q", "-b", "main"]] if init else []) + [["add", "-A"],
                                                               ["commit", "-qm", message]]
    for args in steps:
        subprocess.run(["git", "-C", str(repo), *args], env=env, check=True,
                       capture_output=True)


def _copy_manifest(repo: Path) -> None:
    for key in MANIFEST_FILES:
        dest = repo / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / key, dest)


def fixture_recording_added(tmp: Path, app: str, base_days_ago: float,
                            added_hours_ago: float,
                            subject: str = "The app records its runtime") -> Path:
    """A repository where one app learned to record in its second commit.

    This is the shape of 2026-10-09 in production: `ingest` and `distill` were
    added to the guard, and the deploy that would have let them record had not
    happened. The age that matters is the age of that second commit, not the
    age of the app's files, which is the whole of the distinction the guard
    draws now.
    """
    repo = tmp / "repo"
    _copy_manifest(repo)
    _strip_recording(repo, app)
    now = datetime.now(timezone.utc)
    _commit(repo, "the deployed state", now - timedelta(days=base_days_ago),
            init=True)
    shutil.copyfile(ROOT / rs.APPS[app], repo / rs.APPS[app])
    _commit(repo, subject, now - timedelta(hours=added_hours_ago))
    return repo


def fixture_never_records(tmp: Path, app: str, days_ago: float) -> Path:
    """One commit, and this app's module never asks for a row at all."""
    repo = tmp / "repo"
    _copy_manifest(repo)
    _strip_recording(repo, app)
    _commit(repo, "the deployed state",
            datetime.now(timezone.utc) - timedelta(days=days_ago), init=True)
    return repo


def _shas(repo: Path) -> list[str]:
    """Every commit in this fixture, oldest first."""
    status, out = dh._git(repo, "log", "--format=%h", "--reverse")
    assert status == 0, out
    return out.splitlines()


def test_the_deployed_commit_is_recovered_from_the_digest_alone():
    """The row carries no commit, so the commit comes from replaying the digest."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [
            ("pipeline/llm.py", "Swap the provider for triage"),
            ("prompts/triage.md", "Tighten the rubric"),
        ])
        head = _shas(repo)[-1]
        deployed = _shas(repo)[0]
        # The digest of the first commit, computed the way a container would.
        was = _digest_at_commit(repo, "triage", deployed)

        found = dh.undeployed_commits(repo, "triage", was)
        check("the first commit is named as the deployed one",
              found.get("deployed_commit") == deployed,
              f"{found.get('deployed_commit')} != {deployed}")
        check("and HEAD is not, because HEAD is the undeployed end",
              found.get("deployed_commit") != head)
        subjects = [c["subject"] for c in found.get("commits", [])]
        check("both later commits are named, newest first",
              subjects == ["Tighten the rubric", "Swap the provider for triage"],
              str(subjects))


def _digest_at_commit(repo: Path, app: str, commit: str) -> str:
    """What `pipeline/runtime_sha.py` would have hashed at one commit.

    Deliberately not `dh._digest_at`: a test that asks the thing under test
    what the answer is cannot fail. This checks out the commit into a worktree
    and runs the container's own code path over real files.
    """
    out = repo.parent / f"wt-{commit}"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach",
                    "-q", str(out), commit], check=True, capture_output=True)
    try:
        return rs.digest(rs.local_entries(app, out))
    finally:
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force",
                        str(out)], check=True, capture_output=True)


def test_another_app_s_commit_is_not_this_app_s_drift():
    """Each app's history is its own file set, or every drift names every commit."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [
            ("prompts/digest.md", "A press-only change"),
            ("prompts/triage.md", "A triage-only change"),
        ])
        deployed = _shas(repo)[0]
        found = dh.undeployed_commits(
            repo, "triage", _digest_at_commit(repo, "triage", deployed))
        subjects = [c["subject"] for c in found.get("commits", [])]
        check("triage names only the commit to its own files",
              subjects == ["A triage-only change"], str(subjects))


def test_the_file_list_is_read_at_the_commit_and_not_at_head():
    """A commit that added a file to the image also changed the file list.

    This is the property that decides whether the walk works at all. Reading
    today's manifest against an older tree reports every file added since as
    missing, so every historical digest mismatches and the surface silently
    falls back to "matches nothing". The manifest has to be parsed out of the
    module's source as it was at the commit being tested.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [], extra=["pipeline/evidence.py"])
        deployed = _shas(repo)[0]
        was = _digest_at_commit(repo, "triage", deployed)

        triage = repo / "pipeline" / "triage.py"
        triage.write_text(
            triage.read_text(encoding="utf-8")
            + '\nimage = image.add_local_file("pipeline/evidence.py",'
              ' "/root/evidence.py")\n',
            encoding="utf-8")
        env = {**os.environ,
               "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@example.com",
               "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@example.com"}
        for args in (["add", "-A"], ["commit", "-qm", "Mount the evidence helper"]):
            subprocess.run(["git", "-C", str(repo), *args], env=env, check=True,
                           capture_output=True)

        check("HEAD's manifest really is longer than the deployed one",
              len(rs.local_entries("triage", repo)) == len(MANIFEST_TRIAGE) + 1,
              str(len(rs.local_entries("triage", repo))))
        found = dh.undeployed_commits(repo, "triage", was)
        check("the deployed commit is still recovered across the change",
              found.get("deployed_commit") == deployed,
              found.get("why", str(found)))
        check("and the commit that moved the list is the undeployed one",
              [c["subject"] for c in found.get("commits", [])]
              == ["Mount the evidence helper"],
              str(found.get("commits")))


def test_a_digest_that_matches_no_commit_says_so_rather_than_guessing():
    """An image built from code that never merged is a real state, not a commit."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [("prompts/triage.md", "A change")])
        found = dh.undeployed_commits(repo, "triage", "0ldc0dec0de")
        check("it reports why instead of naming a commit",
              "commits" not in found and "matches none" in found.get("why", ""),
              str(found))
        check("and the headline clause is empty rather than wrong",
              dh.name_undeployed(found) == "", dh.name_undeployed(found))


def test_a_job_that_never_reported_has_nothing_to_diff():
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [("prompts/triage.md", "A change")])
        found = dh.undeployed_commits(repo, "triage", None)
        check("a missing row is explained, not replayed",
              "never reported" in found.get("why", ""), str(found))


def test_the_headline_names_the_commits_and_not_only_the_days():
    """The acceptance criterion for today's work, read off the surface."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [
            ("pipeline/llm.py", "Swap the provider for triage"),
        ])
        deployed = _shas(repo)[0]
        rows = [row_for(app, repo, sha=_digest_at_commit(repo, app, deployed))
                for app in rs.APPS]
        surface = dh.check_deploy(FakeConn(rows), repo, notify=False)

        check("the surface is failing, as it was before this change",
              surface.state == dh.FAILING, surface.state)
        check("the headline still carries the age",
              "days behind" in surface.headline, surface.headline)
        check("and now it carries the commit too",
              "Swap the provider for triage" in surface.headline,
              surface.headline)
        triage = surface.evidence["triage"]["undeployed"]
        check("the evidence names the deployed commit",
              triage.get("deployed_commit") == deployed, str(triage))
        check("and carries every commit, not only the named ones",
              len(triage.get("commits", [])) == 1, str(triage))


def test_the_alarm_mail_carries_the_commits():
    """The owner decides deploy-now or deploy-later, and the commits are the input."""
    saved = {k: os.environ.pop(k, None)
             for k in ("GMAIL_ADDRESS", "GMAIL_APP_PASSWORD")}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixture_history(Path(tmp), [
                ("pipeline/llm.py", "Swap the provider for triage"),
            ])
            deployed = _shas(repo)[0]
            rows = [row_for(app, repo, sha=_digest_at_commit(repo, app, deployed))
                    for app in rs.APPS]
            sent = []
            import pipeline.notify as notify
            real = notify.notify_owner

            def spy(subject, detail, steps, **kw):
                sent.append((subject, detail, steps))
                return "owner notified"

            notify.notify_owner = spy
            try:
                dh.check_deploy(FakeConn(rows), repo, notify=True)
            finally:
                notify.notify_owner = real
            check("the mail went out once", len(sent) == 1, str(len(sent)))
            body = sent[0][1] if sent else ""
            check("and its body names the undeployed commit",
                  "Swap the provider for triage" in body, body)
            check("while still naming the deploy command",
                  any("modal deploy" in s for s in (sent[0][2] if sent else [])),
                  str(sent[0][2] if sent else []))
    finally:
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value


def test_a_current_deploy_is_never_walked():
    """The walk costs git processes, so the green path must not pay for it."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [])
        conn = FakeConn([row_for(app, repo) for app in rs.APPS])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("a matching deploy is green", surface.state == dh.OK,
              surface.headline)
        check("and no app carries an undeployed block",
              all("undeployed" not in surface.evidence[app]
                  for app in rs.APPS), str(surface.evidence))


def test_a_pending_deploy_inside_the_grace_window_names_its_commits_too():
    """A reader inside the window has the same question as one outside it."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [("prompts/triage.md", "A fresh change")],
                               base_days_ago=0.4)
        deployed = _shas(repo)[0]
        rows = [row_for(app, repo, sha=_digest_at_commit(repo, app, deployed))
                for app in rs.APPS]
        surface = dh.check_deploy(FakeConn(rows), repo, notify=False)
        check("a change inside the window is still green",
              surface.state == dh.OK, surface.headline)
        check("and the pending deploy says what is in it",
              "A fresh change" in surface.headline, surface.headline)


def test_the_headline_counts_what_it_does_not_name():
    """Four commits on one line is not a headline, so three are named and the rest counted."""
    found = {"deployed_commit": "abc1234", "deployed_at": "x",
             "commits": [{"sha": f"c{n}", "subject": f"s{n}", "at": "x"}
                         for n in range(5)]}
    named = dh.name_undeployed(found)
    check("three are named", named.count("s0") == 1 and "s2" in named, named)
    check("the fourth and fifth are counted, not named",
          "s3" not in named and "and 2 more" in named, named)
    check("and the total is the first number a reader sees",
          named.startswith("5 undeployed commits"), named)




# ------------------------------------------------- the list cannot go short again

def scheduled_apps() -> dict[str, Path]:
    """Every module in `pipeline/` that installs a Modal schedule.

    Derived from the source rather than from a list, because a hand-kept list
    of what to watch is the defect this section exists for. `modal.Cron` and
    `modal.Period` are the two ways a schedule is installed, and a commented
    schedule does not count: `pipeline/skill_revision.py` carries the words
    `modal.Cron("0 16 * * *")` inside a comment explaining that it stopped
    being scheduled on 2026-10-05, and a text search that counted it would
    demand a guard on a job that no longer runs on its own.
    """
    import ast

    found = {}
    for path in sorted((ROOT / "pipeline").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (isinstance(func, ast.Attribute) and func.attr in ("Cron", "Period")
                    and isinstance(func.value, ast.Name) and func.value.id == "modal"):
                found[path.stem] = path
                break
    return found


def test_every_scheduled_app_is_watched_by_the_drift_guard():
    """A job on a schedule runs unattended, so a job on a schedule is watched.

    `runtime_sha.APPS` held three of five on 2026-10-09, and the two it omitted
    were `ingest` and `distill`: the stage that fills `papers` and the stage
    that fills `claims`, which are the two columns the pipeline surface judges.
    The cost was a diagnosis. The pipeline surface read FAILING with "claims
    has not moved in 2 days" while the deploy surface read `ok`, and both were
    telling the truth, because the guard was blind to the only job that could
    have answered.
    """
    watched = {Path(module).stem for module in rs.APPS.values()}
    scheduled = set(scheduled_apps())
    missing = sorted(scheduled - watched)
    assert not missing, (
        f"these scheduled jobs are not in runtime_sha.APPS: {missing}. A job "
        "nothing watches can stop firing without any surface noticing.")
    # And the other direction, so the guard cannot demand a deploy for a job
    # that no longer has a schedule to be behind on.
    stale = sorted(watched - scheduled)
    assert not stale, (
        f"runtime_sha.APPS watches {stale}, which install no schedule. An "
        "unscheduled app is deployed by hand when it is needed, so drift "
        "against the trunk is not a fault worth alarming on.")


def test_every_watched_app_records_its_own_runtime():
    """Being in the list is half of it. The row has to get written.

    Mounting the module is checked by
    `test_the_guard_cannot_be_deployed_without_itself`. This is the call: an
    app in `APPS` that never calls `record_runtime` has no row, and a missing
    row is now read as unmeasured rather than as drift, so the omission would
    be quiet in exactly the way it was quiet for distill.
    """
    for app, module in sorted(rs.APPS.items()):
        source = (ROOT / module).read_text(encoding="utf-8")
        assert f'record_runtime(conn, "{app}"' in source, (
            f"{module} is watched as {app!r} and never records a runtime, so "
            "the guard has nothing to compare and says so forever")


def test_an_app_that_has_never_recorded_since_its_code_asked_to_is_behind():
    """No row, while the code asks for one, is the oldest deploy there is.

    This test used to assert the opposite, and the opposite cost the press two
    issues. The reasoning behind it was that dating an app's drift from its
    last commit cries wolf, which is true, and the conclusion drawn was that
    one missing row among several is a coverage gap, which is false. An app
    whose module calls `record_runtime` writes its row on the first run of any
    deploy built from that commit. So no row does not mean nobody is watching.
    It means the image predates the line that asks for one, and that line has
    a date.

    `ingest` was the live case the old reasoning was written against, and it
    was not unmeasured: it was running an image from before 2026-10-09, and so
    was `distill`, the stage that fills `claims`. The three fixes to the
    fallback pacing that had stopped distill were all inside the gap. Seven
    days of no claims, two Mondays with no issue, and this surface read
    `unknown` through all of it.
    `INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_repo(Path(tmp), days_ago=9)
        reporting = [a for a in rs.APPS if a != "ingest"]
        conn = FakeConn([row_for(app, repo) for app in reporting])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("the surface is failing rather than unknown",
              surface.state == dh.FAILING, f"{surface.state}: {surface.headline}")
        check("and the headline says the app has never recorded",
              "ingest" in surface.headline
              and "never recorded a runtime" in surface.headline,
              surface.headline)
        check("and dates the image from the commit that asked for a row",
              surface.evidence["ingest"]["drift_hours"] > 24 * 8.5,
              str(surface.evidence["ingest"].get("drift_hours")))
        check("and the deploy command to fix it is in the evidence",
              "modal deploy pipeline/ingest.py" in surface.evidence["ingest"]["why"],
              str(surface.evidence["ingest"]))
        check("the mail is withheld, with its reason, because the cooldown is "
              "a column on the row this app does not have",
              "cooldown" in (surface.evidence.get("alarm") or "")
              and "not mailed" in (surface.evidence.get("alarm") or ""),
              str(surface.evidence.get("alarm")))
        for app in reporting:
            check(f"{app} is still judged on its own merits",
                  surface.evidence[app]["state"] == dh.OK,
                  str(surface.evidence[app]))


def test_an_app_added_to_the_guard_today_is_a_pending_deploy_not_an_alarm():
    """The cry-wolf case the old reasoning was right about, kept.

    Adding a job to the guard must not alarm on the day it is added, because
    nothing is wrong yet: the next deploy records, and the grace window is
    exactly the room for it. The number that decides it is the age of the
    commit that asked, so a module that is nine days old and learned to record
    ten hours ago is ten hours of drift rather than nine days of it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_recording_added(Path(tmp), "ingest", base_days_ago=9,
                                       added_hours_ago=10)
        reporting = [a for a in rs.APPS if a != "ingest"]
        conn = FakeConn([row_for(app, repo) for app in reporting])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("a deploy that is ten hours late is not an alarm",
              surface.state == dh.OK, f"{surface.state}: {surface.headline}")
        check("and the headline says a deploy is pending",
              "pending" in surface.headline and "ingest" in surface.headline,
              surface.headline)
        check("and the age is the age of the line, not of the module",
              surface.evidence["ingest"]["drift_hours"] < 24,
              str(surface.evidence["ingest"].get("drift_hours")))


def test_an_app_whose_code_never_asks_to_record_is_unmeasured():
    """And the third state is still a third state.

    An app in `APPS` whose module has no `record_runtime` call cannot write a
    row from any deploy, so the absence of one says nothing about the age of
    its image. `unknown` is the honest answer, and the headline has to name the
    app. The real repository cannot reach this state, because
    `test_every_watched_app_records_its_own_runtime` forbids it. The guard
    still has to be right when it is reached, since the day that rule breaks
    is the day this branch runs.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_never_records(Path(tmp), "ingest", days_ago=9)
        reporting = [a for a in rs.APPS if a != "ingest"]
        conn = FakeConn([row_for(app, repo) for app in reporting])
        surface = dh.check_deploy(conn, repo, notify=False)
        check("the surface is unknown rather than failing",
              surface.state == dh.UNKNOWN, f"{surface.state}: {surface.headline}")
        check("and it names the unmeasured app",
              "ingest" in surface.headline and "never recorded" in surface.headline,
              surface.headline)
        check("the unmeasured app carries no drift number",
              "drift_hours" not in surface.evidence["ingest"],
              str(surface.evidence["ingest"]))
        check("and the evidence says nothing in its code asks for a row",
              "nothing in its code asks it to" in surface.evidence["ingest"]["why"],
              str(surface.evidence["ingest"]))


def test_an_unrecorded_image_names_what_it_is_missing():
    """The commits inside the gap, not only the size of it.

    "distill is 4 days behind" is a number about the clock. Those four days
    held `66f7e87`, `c005e9e` and `e289242`, the three fixes to the exact
    thing that was broken, and the owner reading the alarm has one action
    available and needs to know what is in it. `undeployed_commits` cannot
    answer here, because there is no reported digest to replay the history
    against. The bound is every commit from the one that asked for a row
    forward, which is what `undeployed_since` returns.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_recording_added(
            Path(tmp), "ingest", base_days_ago=9, added_hours_ago=72,
            subject="The drift guard watched three of five scheduled jobs")
        reporting = [a for a in rs.APPS if a != "ingest"]
        surface = dh.check_deploy(
            FakeConn([row_for(app, repo) for app in reporting]), repo, notify=False)
        check("the headline names the commit inside the gap",
              "The drift guard watched three of five" in surface.headline,
              surface.headline)
        found = surface.evidence["ingest"]["undeployed"]
        check("and the evidence carries it as a list",
              [c["subject"] for c in found["commits"]]
              == ["The drift guard watched three of five scheduled jobs"],
              str(found))


def test_every_test_in_this_file_is_reached_by_the_runner():
    """The runner block goes last, or the tests under it do not run.

    `main()` walks `globals()`, so a test defined after the `__main__` block
    does not exist when the walk happens and `python3 tests/test_deploy_drift.py`
    prints "all checks passed" without it. Three tests sat under that block in
    this file, one of them the test that asserted the behaviour the fix above
    replaces, and the evidence line in a pull request said the file passed.
    This file is also in `test_ci_coverage.py`'s uncovered pin, so a direct run
    is the only run it gets.
    """
    import ast as _ast

    source = Path(__file__).read_text(encoding="utf-8")
    tree = _ast.parse(source)
    block = [n for n in tree.body
             if isinstance(n, _ast.If) and "__main__" in _ast.dump(n.test)]
    check("the file has a runner block", len(block) == 1, str(len(block)))
    if not block:
        return
    stranded = sorted(n.name for n in tree.body
                      if isinstance(n, _ast.FunctionDef)
                      and n.name.startswith("test_")
                      and n.lineno > block[0].lineno)
    check("and no test is stranded below it", not stranded, str(stranded))


def test_a_fresh_merge_does_not_reset_the_drift_clock():
    """The grace window is dated from when the drift began, not from today.

    `INC-2026-10-16-the-drift-clock-was-reset-by-every-merge`. The window
    exists so that a merge at noon is not an alarm at one, and it was measured
    from the newest commit to touch the app's files. That is the wrong end of
    the drift: every later merge pushed the number back under the ceiling, so
    an app nine days behind reported "a deploy is pending and still inside the
    24h window" on any day somebody touched its files.

    The fixture is the production shape in miniature. The deployed image is
    2.5 days old, one undeployed commit landed 1.5 days ago, and a second
    landed 12 hours ago. The old rule read 12 hours and passed. The drift is
    36 hours and the window is 24.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [
            ("pipeline/llm.py", "The press prints a short edition"),
            ("prompts/triage.md", "A docstring, merged this morning"),
        ], base_days_ago=2.5)
        deployed = _shas(repo)[0]
        rows = [row_for(app, repo, sha=_digest_at_commit(repo, app, deployed))
                for app in rs.APPS]
        surface = dh.check_deploy(FakeConn(rows), repo, notify=False)

        check("the surface is failing, which it was not before this fix",
              surface.state == dh.FAILING, f"{surface.state}: {surface.headline}")
        triage = surface.evidence["triage"]
        check("the drift is dated from the oldest undeployed commit",
              triage["drift_anchor"] == "the oldest undeployed commit",
              str(triage.get("drift_anchor")))
        check("so it reads a day and a half rather than half a day",
              35.0 < triage["drift_hours"] < 37.0, str(triage["drift_hours"]))
        check("while the newest commit is still reported, because a reader "
              "wants both dates",
              "merged_at" in triage and "drift_began" in triage, str(triage))
        check("and the headline names the undeployed work",
              "short edition" in surface.headline, surface.headline)
        # The old rule, computed here rather than asserted from memory: this
        # fixture is only a regression test if the anchor it replaces would
        # have passed it.
        newest = dh._parse_iso(triage["merged_at"])
        was = (datetime.now(timezone.utc) - newest).total_seconds() / 3600
        check("and the anchor this replaces would have called it fine",
              was < dh.DEPLOY_GRACE_HOURS, f"{was:.1f}h")


def test_an_undatable_drift_falls_back_to_the_old_anchor():
    """A guard that cannot recover the deployed commit under-reports, not invents.

    The replay needs the deployed digest to match a commit in range. A row
    whose digest matches nothing, which is a shallow clone or an image built
    from code that never merged, leaves `undeployed_commits` with a `why` and
    no commits. The anchor then goes back to the newest commit, exactly as it
    did before, and the evidence says which question the number answered.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = fixture_history(Path(tmp), [
            ("pipeline/llm.py", "Swap the provider for triage"),
        ], base_days_ago=9.0)
        rows = [row_for(app, repo, sha="ffffffffffff") for app in rs.APPS]
        surface = dh.check_deploy(FakeConn(rows), repo, notify=False)

        triage = surface.evidence["triage"]
        check("the replay could not place the image",
              "why" in triage["undeployed"], str(triage["undeployed"]))
        check("so the anchor is the one the guard has always had",
              triage["drift_anchor"] == "the newest commit to the app's files",
              str(triage.get("drift_anchor")))
        check("and the drift is still reported rather than withheld",
              triage["drift_hours"] > dh.DEPLOY_GRACE_HOURS, str(triage["drift_hours"]))


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
