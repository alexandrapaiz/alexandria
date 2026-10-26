"""The drift alarm's new channel: does it fire, once per image, and say enough.

Run with `python3 -m pytest tests/test_drift_watch.py -q`.

`tools/drift_watch.py` exists because `tools/delivery_health.py`'s deploy
surface has been correct since 2026-10-08 and has raised an alarm to nobody:
its cooldown is `deploy_runtime.notified_at`, writing it needs `DATABASE_URL`,
and no agent seat holds one. The judgement is `judge_deploy`, which has its
own suite in `tests/test_deploy_drift.py`, so the tests here are about the
three things that are new: which apps the alarm is about, what the card says,
and the dedupe that makes a daily schedule post one card per stale image
instead of one a day.

Nothing here touches the network or the board. The deploy surface is built by
calling the real `judge_deploy` against the real git fixture
`tests/test_deploy_drift.py` already builds, because the dating is `git log`
and mocking it would test the mock. The board is a recording double. A test
that needed a credential would be a test nobody runs on a pull request.
"""

import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

import test_deploy_drift as drift  # noqa: E402  the fixture, not the tests

from tools import board  # noqa: E402
from tools import delivery_health as dh  # noqa: E402
from tools import drift_watch as dw  # noqa: E402

UTC = timezone.utc
NOW = datetime.now(UTC)

OTHER_COLUMN = "c-done"


# ---------------------------------------------------------------- the surface


def surface(stale: dict[str, str] | None = None, *, days_ago: float,
            repo: Path, ran_hours_ago: float = 2.0):
    """The deploy surface as the receipt reader hands it to the judgement.

    `stale` maps an app to the sha it last reported; every app not named runs
    the trunk. The fixture's one commit is `days_ago` old, which is what
    `_last_commit_at` reads, so `days_ago` is the drift the surface sees.
    """
    stale = stale or {}
    rows = {}
    for app in drift.rs.APPS:
        ran = NOW - timedelta(hours=ran_hours_ago)
        rows[app] = {"runtime_sha": stale.get(app) or drift.rs.digest(
                         drift.rs.local_entries(app, repo)),
                     "recorded_at": ran, "first_seen_at": ran,
                     "notified_at": None}
    return dh.judge_deploy(rows, repo, source=dh.RECEIPT_URL)


@pytest.fixture(scope="module")
def stale_repo():
    """A checkout whose one commit is nine days old: well past the window."""
    with tempfile.TemporaryDirectory() as tmp:
        yield drift.fixture_repo(Path(tmp), days_ago=9)


@pytest.fixture(scope="module")
def fresh_repo():
    """A checkout committed an hour ago: inside the 24 hour grace window."""
    with tempfile.TemporaryDirectory() as tmp:
        yield drift.fixture_repo(Path(tmp), days_ago=1 / 24)


# ------------------------------------------------- which apps it is about


def test_only_the_apps_past_the_window_get_a_card(stale_repo):
    """One app stale, four current, and the alarm is about the one.

    The headline joins every stale app into one sentence with semicolons, so
    a reader of the headline cannot tell four stale apps from one with a long
    name. The evidence still has the app names attached, which is why
    `behind` reads that and not the prose.
    """
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=stale_repo)
    assert deploy.state == dh.FAILING
    assert [r["app"] for r in dw.behind(deploy)] == ["weekly"]


def test_every_stale_app_gets_its_own_card(stale_repo):
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    assert [r["app"] for r in dw.behind(deploy)] == sorted(drift.rs.APPS)


def test_a_fully_deployed_fleet_posts_nothing(stale_repo):
    deploy = surface(days_ago=9, repo=stale_repo)
    assert deploy.state == dh.OK
    assert dw.behind(deploy) == []


def test_a_drift_still_inside_the_grace_window_posts_nothing(fresh_repo):
    """A merge at noon is not an alarm at one, which is the window's whole job.

    `judge_deploy` names the app as pending in the headline, so a guardrail
    that read the headline would alarm on it. This one reads the state.

    Two fixtures rather than one, because on 2026-10-23 they stopped giving
    the same answer and the difference is the point. `fresh_repo` records a
    digest that matches no commit, which is what a shallow clone looks like
    from inside, and that is now `unknown`: the drift could not be dated, so
    calling it fine was a claim the checkout could not support. The history
    fixture below records the digest of the commit before the edit, which is
    what a real deploy's row holds an hour after somebody merges, and that is
    still `ok`. Either way this guardrail posts nothing, which is what the
    test is really about.
    """
    deploy = surface({"weekly": "0000stale000"}, days_ago=1 / 24, repo=fresh_repo)
    assert deploy.state == dh.UNKNOWN
    assert dw.behind(deploy) == []

    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_history(Path(tmp), [
            ("pipeline/llm.py", "A change merged two hours ago"),
        ], base_days_ago=1.1)
        placeable = {app: dh._digest_at(repo, app, "HEAD~1", {})
                     for app in drift.rs.APPS}
        deploy = surface(placeable, days_ago=1.1, repo=repo)
        assert deploy.state == dh.OK
        assert "pending" in deploy.headline
        assert dw.behind(deploy) == []


def test_the_scalar_evidence_keys_are_not_mistaken_for_apps(stale_repo):
    """`read_via`, `ref` and `alarm` sit in the same mapping as the apps.

    A filter that walked the mapping without excluding them would post a card
    titled after a URL the first time one of those values became a dict.
    """
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=stale_repo)
    assert "read_via" in deploy.evidence and "alarm" in deploy.evidence
    assert all(r["app"] in drift.rs.APPS for r in dw.behind(deploy))


# -------------------------------------------------- what the card is keyed on


def test_the_card_is_keyed_on_the_running_image(stale_repo):
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=stale_repo)
    record = dw.behind(deploy)[0]
    assert record["key"] == "0000stale000"
    assert dw.card_title("weekly", record["key"]) == (
        "Deploy: weekly is not running main, still on 0000stale000")
    assert dw.card_title("weekly", record["key"]).startswith(dw.TITLE_PREFIX)


def test_a_second_stale_image_is_a_second_card_and_not_the_first_one_again():
    """A deploy that lands a different stale image is a new fact.

    The alternative, keying on the app alone, would hide the second drift
    behind the first card and the board would show a stale alarm as a current
    one.
    """
    first = dw.cooldown_key({"recorded_sha": "aaaa11112222"})
    second = dw.cooldown_key({"recorded_sha": "bbbb33334444"})
    assert first != second
    assert dw.card_title("weekly", first) != dw.card_title("weekly", second)


def test_an_app_that_never_recorded_is_keyed_on_the_commit_that_asked_it_to():
    """There is no sha to key on, and the day is the wrong thing to use.

    `INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see` is why this
    case exists at all. Keyed on the date it would post a card a day forever,
    and the commit that added the recorder changes only when the recorder
    does.
    """
    key = dw.cooldown_key({"recorded_sha": None, "asked_in": "a941a71"})
    assert "a941a71" in key
    assert dw.cooldown_key({"recorded_sha": None}) == "nothing recorded at all"


# ------------------------------------------------------------- what it says


def test_the_card_body_names_the_shas_the_age_and_the_one_command(stale_repo):
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=stale_repo)
    record = dw.behind(deploy)[0]
    body = dw.card_body(record, deploy, NOW)
    assert "0000stale000" in body, "the card did not say what production runs"
    assert record["evidence"]["expected_sha"] in body, "nor what it should run"
    assert "9.0 days" in body
    # The one action that closes it, named rather than described, and the
    # ladder it has to go behind.
    assert "modal deploy pipeline/weekly.py" in body
    assert "press-rehearsal.md" in body
    # Which reader answered, for the same reason every surface carries it.
    assert dh.RECEIPT_URL in body


def test_the_card_body_explains_why_it_is_a_card_and_not_the_email(stale_repo):
    """The reason is the finding, so a reader does not re-discover it.

    Somebody opening this card will ask why the check that was built to mail
    is posting instead. If the card does not answer that, the next engineer to
    read `_notify_drift` concludes the alarm works.
    """
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=stale_repo)
    body = dw.card_body(dw.behind(deploy)[0], deploy, NOW)
    assert "cooldown" in body and "database credential" in body


def test_every_block_of_the_card_fits_what_the_board_accepts(stale_repo):
    """The board refuses a block over 420 characters with a 400.

    One of these blocks quotes commit subjects this file does not control, so
    the arithmetic that holds today is not a property worth assuming at the
    moment the alarm matters. `board.scannable` is what makes it hold.
    """
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    for record in dw.behind(deploy):
        body = dw.card_body(record, deploy, NOW)
        longest = max(len(block) for block in body.split("\n\n"))
        assert longest <= board.BODY_BLOCK_LIMIT, (
            f"{record['app']}'s card has a {longest} character block and the "
            f"board refuses anything over {board.BODY_BLOCK_LIMIT}")


def test_the_card_names_the_deadline_the_deploy_has_to_beat(stale_repo):
    """The card used to say how old the image was and never when it mattered.

    So the owner was left to work the cron out of a decorator. The ExO seat
    did exactly that by hand on 2026-10-24, on the compute card, and wrote
    the answer in as a comment. One paragraph here is cheaper than that, and
    it is right every day rather than on the day somebody bothered.
    """
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    record = dw.behind(deploy)[0]
    body = dw.card_body(record, deploy, NOW)
    app = record["app"]
    assert f"The next run of {app} is" in body, body
    assert "away. That is the deadline on this card" in body, body
    assert record["evidence"]["cron"], record["evidence"]
    # The schedule itself, so a reader can check the arithmetic rather than
    # trust it.
    assert record["evidence"]["cron"] in body, body


def test_the_card_does_not_hand_over_a_deadline_while_nothing_is_firing(stale_repo):
    """A clock that has stopped is not a deadline, and 2026-10-24 was that day.

    The Modal workspace was disabled, so a card reading "weekly fires Monday
    09:00" would have told the owner to work to a schedule that was not
    running. The outage belongs inside the deadline sentence, because a reader
    who skips a footnote has been misled by the part they did read.
    """
    outage = "Modal's edge says workspace ac-1 is disabled."
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    deploy.evidence["compute_outage"] = outage
    body = dw.card_body(dw.behind(deploy)[0], deploy, NOW)
    assert outage in body, body
    assert "no cron in this pipeline is firing at all" in body, body
    assert "from the moment compute comes back" in body, body
    assert "That is the deadline on this card" not in body, body


def test_a_schedule_that_cannot_be_read_leaves_the_card_without_a_deadline(stale_repo):
    """And says so, rather than printing an age with an implied deadline.

    `deadline` is the only new sentence on this card and it is the one a
    reader acts on, so the failure mode that matters is a confident wrong
    time. There is no third option where it quietly says nothing: a card with
    the paragraph missing reads as a card whose deadline is not urgent.
    """
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    record = dw.behind(deploy)[0]
    record["evidence"] = {**record["evidence"], "next_run_at": None,
                          "next_run_why": "its module puts nothing on a cron"}
    body = dw.card_body(record, deploy, NOW)
    assert "I cannot say when this image next serves a run" in body, body
    assert "its module puts nothing on a cron" in body, body


def test_the_nudge_carries_the_deadline_too(stale_repo):
    """A nudge is read instead of the card, not alongside it.

    The card is written once per image and nudged once a day after that, so
    on day eight the sentence the owner sees is the nudge. A deadline only on
    the card is a deadline that expires from view on day two.
    """
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    record = dw.behind(deploy)[0]
    assert "Next run" in dw.nudge_body(record, NOW)
    bare = {**record, "evidence": {**record["evidence"], "next_run_at": None}}
    assert "Next run" not in dw.nudge_body(bare, NOW)


@pytest.mark.parametrize("hours,expected", [
    (24.5, "24.5 hours"),
    (47.9, "47.9 hours"),
    (48.0, "2.0 days"),
    (264.0, "11.0 days"),
])
def test_the_age_reads_in_the_unit_a_reader_would_use(hours, expected):
    assert dw.ageing(hours) == expected


def test_an_undatable_age_says_so_rather_than_printing_a_zero():
    assert dw.ageing(None) == "an unknown time"


def test_the_deploy_command_comes_from_the_app_table_not_from_a_string():
    """An entrypoint that moves must not leave the card naming a dead path."""
    from pipeline import runtime_sha
    for app, module in runtime_sha.APPS.items():
        assert dw.deploy_command(app) == f"modal deploy {module}"


# --------------------------------------------------------------- the dedupe


def board_payload(items):
    return {"columns": [{"id": "c-sprint", "name": "This sprint", "position": 2},
                        {"id": OTHER_COLUMN, "name": "Done", "position": 5}],
            "items": items}


def card(title, **kw):
    return {"id": "x", "title": title, "column_id": "c-sprint", **kw}


def test_find_card_matches_this_commands_own_card_for_this_image():
    one = card("Deploy: weekly is not running main, still on 0000stale000")
    assert dw.find_card(board_payload([one]), "weekly", "0000stale000") is one


def test_find_card_looks_in_every_column_including_done():
    """A drift somebody has already closed is not alarmed about again."""
    one = card("Deploy: weekly is not running main, still on 0000stale000",
               column_id=OTHER_COLUMN)
    assert dw.find_card(board_payload([one]), "weekly", "0000stale000") is one


def test_find_card_does_not_match_another_app():
    one = card("Deploy: ingest is not running main, still on 0000stale000")
    assert dw.find_card(board_payload([one]), "weekly", "0000stale000") is None


def test_find_card_does_not_match_another_image_of_the_same_app():
    one = card("Deploy: weekly is not running main, still on aaaa11112222")
    assert dw.find_card(board_payload([one]), "weekly", "0000stale000") is None


def test_find_card_does_not_match_a_card_somebody_else_wrote():
    """A human's own card about the same deploy is work, not this alarm.

    Treating it as this command's card would mean the guardrail reads somebody
    noticing late as itself having noticed, which is the mistake
    `press_watch` records against the PM's press-gap card.
    """
    one = card("Deploy the weekly job, it is behind again")
    assert dw.find_card(board_payload([one]), "weekly", "0000stale000") is None


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


def stale_one(repo):
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=repo)
    return deploy, dw.behind(deploy)[0]


def test_an_image_with_no_card_gets_one_in_the_working_column(recorder, stale_repo):
    rec = recorder(board_payload([]))
    deploy, record = stale_one(stale_repo)
    did = dw.post(record, deploy, NOW, company="alexandria")
    assert did["action"] == "created"
    (method, path, payload) = rec.calls[-1]
    assert (method, path) == ("POST", "/api/items")
    assert payload["title"] == (
        "Deploy: weekly is not running main, still on 0000stale000")
    assert payload["column_id"] == "c-sprint", "the card landed outside the working column"
    assert payload["seat"] == "engineer"
    assert payload["horizon"] == "now"


def test_an_image_that_already_has_a_fresh_card_is_not_posted_again(
        recorder, stale_repo):
    existing = card("Deploy: weekly is not running main, still on 0000stale000",
                    created_at=NOW.isoformat(), comments=[])
    rec = recorder(board_payload([existing]))
    deploy, record = stale_one(stale_repo)
    did = dw.post(record, deploy, NOW, company="alexandria")
    assert did["action"] == "already on the board"
    assert not [c for c in rec.calls if c[0] == "POST"], (
        "a second run on the same image wrote to the board, which is one "
        "card a day for as long as nobody deploys"
    )


def test_an_image_that_stays_undeployed_gets_one_nudge_a_day(recorder, stale_repo):
    existing = card("Deploy: weekly is not running main, still on 0000stale000",
                    created_at=NOW.isoformat(), comments=[])
    rec = recorder(board_payload([existing]))
    deploy, record = stale_one(stale_repo)
    later = NOW + timedelta(hours=25)
    did = dw.post(record, deploy, later, company="alexandria")
    assert did["action"] == "nudged"
    (method, path, payload) = rec.calls[-1]
    assert (method, path) == ("POST", "/api/items/x/comments")
    assert "0000stale000" in payload["body"]


def test_an_unresolvable_column_still_gets_the_card_posted(recorder, stale_repo, capsys):
    """The card matters and its column does not.

    A board whose working column has been renamed would otherwise swallow the
    one alarm this file exists to raise.
    """
    payload = board_payload([])
    payload["columns"] = [{"id": "c-other", "name": "Somewhere else", "position": 1}]
    rec = recorder(payload)
    deploy, record = stale_one(stale_repo)
    did = dw.post(record, deploy, NOW, company="alexandria")
    assert did["action"] == "created"
    assert "column_id" not in rec.calls[-1][2]
    assert "drift_watch" in capsys.readouterr().err


def test_a_run_alarming_about_every_app_reads_the_board_once(recorder, stale_repo,
                                                             monkeypatch):
    """Five cards is five writes and one read, not five reads.

    The board is an HTTP service and a guardrail that re-reads it per app
    makes its own cost proportional to how bad the day is.
    """
    rec = recorder(board_payload([]))
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: deploy)
    answer = dw.watch(company="alexandria")
    assert answer["exit"] == 1
    assert [a["action"] for a in answer["board"]] == ["created"] * len(drift.rs.APPS)
    assert len([c for c in rec.calls if c[0] == "read"]) == 1


# ---------------------------------------------------------------- the verdict


def test_a_surface_that_could_not_be_read_posts_nothing_and_exits_two(monkeypatch):
    """A gate that saw nothing must not read as a quiet pass.

    `INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see` and company
    standard L-A21 are the same shape, and this is the assertion that keeps
    this file out of it.
    """
    blind = dh.Surface("deploy", dh.UNKNOWN, "deploy_runtime could not be read", {})
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: blind)
    monkeypatch.setattr(board, "read_board",
                        lambda *a, **k: pytest.fail("a blind run touched the board"))
    answer = dw.watch(company="alexandria")
    assert answer["exit"] == 2
    assert answer["board"][0]["action"] == "nothing posted"


def test_a_green_fleet_exits_zero_and_touches_nothing(monkeypatch, stale_repo):
    deploy = surface(days_ago=9, repo=stale_repo)
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: deploy)
    monkeypatch.setattr(board, "read_board",
                        lambda *a, **k: pytest.fail("a green run touched the board"))
    answer = dw.watch(company="alexandria")
    assert answer["exit"] == 0
    assert answer["board"][0]["action"] == "nothing to post"


def test_a_board_that_refuses_the_write_still_exits_one(monkeypatch, stale_repo):
    """The drift is real whether or not the board took the card.

    A run that swallowed the exit code here would report a working guardrail
    on an app nobody was told about, which is the defect this file is about,
    one layer up.
    """
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=stale_repo)
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: deploy)

    def refuse(*a, **k):
        raise board.BoardError("401 from the board")
    monkeypatch.setattr(board, "read_board", refuse)
    answer = dw.watch(company="alexandria")
    assert answer["exit"] == 1
    assert answer["board"][0]["action"] == "not posted"
    assert "401" in answer["board"][0]["why"]


def test_a_dry_run_needs_no_board_credential(monkeypatch, stale_repo):
    deploy = surface({"weekly": "0000stale000"}, days_ago=9, repo=stale_repo)
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: deploy)
    monkeypatch.setattr(board, "read_board",
                        lambda *a, **k: pytest.fail("a dry run read the board"))
    monkeypatch.setattr(board, "api",
                        lambda *a, **k: pytest.fail("a dry run wrote to the board"))
    answer = dw.watch(dry_run=True, company="alexandria")
    assert answer["exit"] == 1
    assert answer["board"][0]["action"] == "would create"
    assert answer["board"][0]["body"]


def test_the_render_names_every_app_it_posted_about(monkeypatch, stale_repo):
    """The prose and the JSON read the same answer, not two.

    Incident 8's standing rule is to judge a run by its artifacts, so the
    human-readable output has to carry the same app names the JSON does.
    """
    deploy = surface({app: "0000stale000" for app in drift.rs.APPS},
                     days_ago=9, repo=stale_repo)
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: deploy)
    answer = dw.watch(dry_run=True, company="alexandria")
    text = dw.render(answer)
    for app in drift.rs.APPS:
        assert app in text


def test_the_judgement_is_called_and_not_copied():
    """No second implementation of the drift rule can drift from the first.

    The grace window, the app list and the staleness arithmetic all live in
    `delivery_health` and `runtime_sha`. A copy here would agree with them
    only by luck and only until one of them changed, which is the argument
    `press_watch` makes about the press's week label. So: this module may
    name the grace window, but only through `dh`, and it may not keep a list
    of apps at all.
    """
    import ast
    tree = ast.parse((ROOT / "tools" / "drift_watch.py").read_text())
    bare = [node.id for node in ast.walk(tree)
            if isinstance(node, ast.Name) and node.id == "DEPLOY_GRACE_HOURS"]
    assert not bare, "the grace window is re-declared here rather than read from dh"
    assigned = {target.id for node in ast.walk(tree)
                if isinstance(node, ast.Assign)
                for target in node.targets if isinstance(target, ast.Name)}
    assert "APPS" not in assigned and "DEPLOY_GRACE_HOURS" not in assigned, (
        "this file keeps its own copy of something the judgement owns")


# ------------------------------- the apps this run could not measure at all

def mixed_surface(repo: Path):
    """One app past the window, one app nothing in this checkout can place.

    `distill`'s module does not ask for a row in this fixture, so it has none
    and `recording_asked_at` finds nothing: `unknown`. `weekly` reports an
    image the checkout cannot place and the only commit is nine days old:
    `failing`. `judge_deploy` tests its alarm branch first, so the surface
    itself reads `failing` and the unknown app is not visible in its state.
    """
    rows = {app: {"runtime_sha": drift.rs.digest(
                      drift.rs.local_entries(app, repo)),
                  "recorded_at": NOW - timedelta(hours=2),
                  "first_seen_at": NOW - timedelta(hours=2),
                  "notified_at": None}
            for app in drift.rs.APPS if app != "distill"}
    rows["weekly"]["runtime_sha"] = "0ldc0dec0de"
    return dh.judge_deploy(rows, repo, source=dh.RECEIPT_URL)


@pytest.fixture(scope="module")
def mixed_repo():
    with tempfile.TemporaryDirectory() as tmp:
        yield drift.fixture_never_records(Path(tmp), "distill", days_ago=9)


def test_undated_reads_the_apps_the_surface_could_not_place(mixed_repo):
    found = dw.undated(mixed_surface(mixed_repo))
    assert [r["app"] for r in found] == ["distill"]
    assert found[0]["why"], "an unmeasured app with no reason is half an answer"


def test_the_scalar_shallow_flag_is_not_mistaken_for_an_app(mixed_repo):
    """`judge_deploy` puts `shallow_checkout` in the evidence beside the apps."""
    surface = mixed_surface(mixed_repo)
    assert "shallow_checkout" in surface.evidence
    assert "shallow_checkout" not in [r["app"] for r in dw.undated(surface)]
    assert "shallow_checkout" not in [r["app"] for r in dw.behind(surface)]


def test_an_app_that_could_not_be_measured_is_not_a_quiet_pass(
        monkeypatch, mixed_repo):
    """Exit 2, and the card for the app that did alarm is still posted.

    This is the narrow hole L-A21 names and this file used to fall into. The
    surface reads `failing`, so the `unknown` guard at the top of `watch()`
    never fired, `behind()` filtered the unmeasured app out, and the run
    exited 1: a claim that production is stale and the board carries it, made
    by a run that could not see one of the three jobs it was talking about.
    """
    surface = mixed_surface(mixed_repo)
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: surface)

    answer = dw.watch(today=NOW, dry_run=True)

    assert answer["exit"] == 2, "a run that measured two of three is not green"
    assert answer["undated"] == ["distill"]
    assert answer["behind"] == ["weekly"]
    posted = [a for a in answer["board"] if a.get("app") == "weekly"]
    assert posted and posted[0]["action"] == "would create", \
        "the drift that was found must not be lost to the exit code"

    printed = dw.render(answer)
    assert "distill" in printed and "unmeasured" in printed, printed
    assert "could not be placed against production" in printed, printed


def test_an_unmeasurable_app_alone_is_also_not_a_quiet_pass(monkeypatch):
    """No app behind, one app unplaceable, nothing inside the window either.

    The surface reads `unknown` here and the top of `watch()` already caught
    that. The case this adds is the one where `late` is empty for an innocent
    reason and `blind` is not, which used to return exit 0.
    """
    class Fake:
        state = dh.FAILING   # not `unknown`, so the early return is skipped
        evidence = {"read_via": dh.RECEIPT_URL, "ref": "origin/main",
                    "shallow_checkout": True,
                    "weekly": {"state": dh.UNKNOWN,
                               "why": "the drift cannot be dated"},
                    "ingest": {"state": dh.OK},
                    "distill": {"state": dh.OK}}

        def as_dict(self):
            return {"state": self.state, "headline": "mixed",
                    "evidence": self.evidence}

    monkeypatch.setattr(dw, "read_deploy", lambda today=None: Fake())
    answer = dw.watch(today=NOW, dry_run=True)

    assert answer["behind"] == []
    assert answer["undated"] == ["weekly"]
    assert answer["exit"] == 2, "nothing to post is not the same as nothing wrong"


def test_the_card_says_why_it_could_not_name_the_commits_rather_than_guessing(
        monkeypatch, mixed_repo):
    """"Usually a shallow clone" was a guess, and the flag is now a fact.

    Two readings share one sentence and they have different fixes. A shallow
    clone is closed by one command. An image matching no commit on the trunk
    is a deploy from somewhere that is not the trunk, which is a different
    problem entirely, and a card that called it "usually a shallow clone"
    would send its reader after the wrong one.
    """
    surface = mixed_surface(mixed_repo)
    record = dw.behind(surface)[0]
    assert record["app"] == "weekly"

    body = dw.card_body(record, surface, NOW)
    assert "is not shallow" in body, body
    assert dh.UNSHALLOW not in body, body

    surface.evidence["shallow_checkout"] = True
    shallow_body = dw.card_body(record, surface, NOW)
    assert dh.UNSHALLOW in shallow_body, shallow_body


def test_a_board_that_refuses_the_card_still_reports_the_unmeasured_app(
        monkeypatch, mixed_repo):
    """The exit-code rule holds on the path where the board itself fails.

    Three returns in `watch()` can be reached with an unmeasured app in hand,
    and a rule that is true of two of them is not a rule.
    """
    surface = mixed_surface(mixed_repo)
    monkeypatch.setattr(dw, "read_deploy", lambda today=None: surface)
    monkeypatch.setattr(board_alarm_module(), "company_here", lambda c: "x")
    monkeypatch.setattr(dw.board, "read_board",
                        lambda company: (_ for _ in ()).throw(
                            board.BoardError("no board here")))

    answer = dw.watch(today=NOW, dry_run=False)

    assert answer["undated"] == ["distill"]
    assert answer["exit"] == 2, "an unplaced app outranks a board that refused"
    assert all(a["action"] == "not posted" for a in answer["board"])


def board_alarm_module():
    from tools import board_alarm
    return board_alarm
