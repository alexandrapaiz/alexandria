"""Does the wake-route sweep tell a route that cannot exist from one nobody used.

Run with `python3 -m pytest tests/test_wake_routes.py -q`.

`tools/wake_routes.py` reads the host's roster and audit log, which live
outside the repository and are not present on a pull request checkout, so
every test here builds both in a temporary directory in the host's exact
shapes. Nothing reads `/srv/asc`, for the reason `test_cron_firing.py` gives:
a test that needs the host's disk is a test nobody runs on a pull request.

Four states and the polarity between them is the point. `deaf` is a defect;
`gated` is the same silence arrived at on purpose, after HQ's monthly finance
seat woke itself seven times in one morning; `open` is a question and never a
failure, because an unused route and an impossible one leave the same absence.
The two regressions worth naming are both from this file's own first draft:
reading the charter line by line reported two seats that do declare a prefix
as declaring none, and printing only the first segment of a type name printed
`pr=` twice for the one seat that subscribes to both `pr.merged` and
`pr.opened`.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import wake_routes as wr  # noqa: E402

MANIFEST = """
[agent]
name = "{company}-{seat}"

[trigger]
cron = "{cron}"
webhook = true
subscriptions = [{subs}]

[runtime]
model = "claude-opus-5"
entry = "prompts/{seat}-agent.md"
repo = "alexandrapaiz/{company}"
max_turns = 180
"""


def build(tmp_path, seats, charters, rows=(), cadences=""):
    """seats: {seat: (cron, [subscriptions])}. charters: {seat: charter text}."""
    roster = tmp_path / "roster" / "testco"
    for seat, (cron, subs) in seats.items():
        d = roster / seat
        d.mkdir(parents=True)
        (d / "agent.toml").write_text(MANIFEST.format(
            company="testco", seat=seat, cron=cron,
            subs=", ".join('"%s"' % s for s in subs)))
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    for seat, text in charters.items():
        (prompts / ("%s-agent.md" % seat)).write_text(text)
    audit = tmp_path / "audit.jsonl"
    audit.write_text("".join(json.dumps(r) + "\n" for r in rows))
    yaml = tmp_path / "company.yaml"
    yaml.write_text(cadences)
    return dict(company="testco", roster=str(tmp_path / "roster"),
                prompts=str(prompts), audit=str(audit), company_yaml=str(yaml))


def start(seat, trigger, ts="2026-10-26T12:00:00.000Z"):
    return {"ts": ts, "agent": "testco-" + seat, "action": "run.start", "trigger": trigger}


def one(rows, seat):
    return next(r for r in rows if r["seat"] == seat)


def test_a_prefix_naming_no_seat_is_deaf_on_both_prefix_routed_types(tmp_path):
    args = build(tmp_path,
                 {"security": ("0 13 1,15 * *", ["message.posted", "pr.merged", "check.failed"])},
                 {"security": "One PR per run on a branch named sec/YYYY-MM-DD: the fixes.\n"},
                 cadences="  - { name: security, cadence: semimonthly }\n")
    row = one(wr.verdict(**args), "security")
    assert row["prefix"] == "sec"
    assert row["prefix_resolves_to"] == "sec"
    assert row["prefix_ok"] is False
    assert row["types"]["pr.merged"][0] == "deaf"
    assert row["types"]["check.failed"][0] == "deaf"
    assert row["types"]["message.posted"][0] == "open"


def test_the_masked_second_defect_is_printed_beside_the_first(tmp_path):
    """A prefix that names no seat decides before the cadence gate, so the
    gate's answer is unobservable behind it. That masking hid `security`'s
    missing suppression word for as long as both defects existed."""
    args = build(tmp_path,
                 {"security": ("0 13 1,15 * *", ["pr.merged"])},
                 {"security": "a branch named sec/YYYY-MM-DD\n"},
                 cadences="  - { name: security, cadence: semimonthly }\n")
    detail = one(wr.verdict(**args), "security")["types"]["pr.merged"][2]
    assert "no such seat" in detail
    assert "cadence gate would allow the continue-wake" in detail
    assert "semimonthly" in detail


def test_a_charter_declaring_no_prefix_is_deaf_and_says_which_file(tmp_path):
    args = build(tmp_path,
                 {"research": ("30 16 * * 1", ["pr.merged", "item.moved"])},
                 {"research": "Before you create your branch, run gh pr list.\n"},
                 cadences="  - { name: research, cadence: weekly-mon }\n")
    row = one(wr.verdict(**args), "research")
    assert row["prefix"] is None
    assert row["types"]["pr.merged"] == ("deaf", "no-prefix", row["prefix_source"])
    assert "research-agent.md" in row["prefix_source"]


def test_the_instruction_is_found_across_a_line_break(tmp_path):
    """The first draft read the charter line by line and reported `exo` and
    `frontend`, which both wrap this sentence, as declaring no prefix at all.

    The fixture says `testco-frontend/` rather than `alexandria-frontend/`
    because `seat_of_branch` strips the *acting company's* name and nothing
    else, so the live `alexandria-frontend/` resolves only inside alexandria.
    The first version of this test used the real prefix under a fixture company
    and read as a defect in the tool."""
    args = build(tmp_path,
                 {"frontend": ("0 12 * * 3", ["pr.merged"])},
                 {"frontend": "Open ONE pull request on a branch named\n"
                              "   `testco-frontend/YYYY-MM-DD-slug`: what you saw.\n"},
                 cadences="  - { name: frontend, cadence: weekly-wed }\n")
    row = one(wr.verdict(**args), "frontend")
    assert row["prefix"] == "testco-frontend"
    assert row["prefix_resolves_to"] == "frontend"
    assert row["prefix_ok"] is True
    assert row["types"]["pr.merged"][0] == "open"


def test_a_cadence_slower_than_a_day_is_gated_and_never_deaf(tmp_path):
    args = build(tmp_path,
                 {"okr": ("0 10 1 * *", ["pr.merged", "check.failed"])},
                 {"okr": "Commit on a branch named okr/YYYY-MM.\n"},
                 cadences="  - { name: okr, cadence: monthly }\n")
    row = one(wr.verdict(**args), "okr")
    assert row["continues_on_own_merge"] is False
    assert row["types"]["pr.merged"][0] == "gated"
    assert row["types"]["check.failed"][0] == "open"   # a red check is never gated


def test_an_unknown_cadence_word_fails_open_like_the_bus(tmp_path):
    args = build(tmp_path,
                 {"skill": ("0 12 * * 2", ["pr.merged"])},
                 {"skill": "a branch named skill/YYYY-MM-DD-slug\n"},
                 cadences="  - { name: skill, cadence: fortnightly }\n")
    assert one(wr.verdict(**args), "skill")["continues_on_own_merge"] is True


def test_a_hand_opened_window_is_not_a_routed_wake(tmp_path):
    """Five seats in this company have only `window` rows, and reading those as
    wakes would have said every route was live."""
    args = build(tmp_path,
                 {"market": ("0 11 * * 5", ["message.posted", "pr.merged"])},
                 {"market": "a branch named market/YYYY-MM-DD\n"},
                 rows=[start("market", "window"), start("market", "window")],
                 cadences="  - { name: market, cadence: weekly-fri }\n")
    row = one(wr.verdict(**args), "market")
    assert row["ever_woken"] is False
    assert row["window_runs"] == 2
    assert row["types"]["message.posted"][0] == "open"


def test_a_routed_wake_of_any_trigger_makes_the_seat_live(tmp_path):
    args = build(tmp_path,
                 {"pm": ("5 11 * * *", ["message.posted", "pr.merged", "pr.opened",
                                        "run.failed", "run.reported"])},
                 {"pm": "a branch named pm/standup-YYYY-MM-DD\n"},
                 rows=[start("pm", "message"), start("pm", "cron"), start("pm", "hook")],
                 cadences="  - { name: pm, cadence: weekly-mon }\n")
    row = one(wr.verdict(**args), "pm")
    assert row["wakes"] == {"cron": 1, "hook": 1, "message": 1}
    assert all(row["types"][t][0] == "live" for t in row["subscriptions"])
    # the second regression: both `pr.*` types must survive as distinct keys
    assert "pr.merged" in row["types"] and "pr.opened" in row["types"]


def test_the_fixed_target_types_are_recognised_rather_than_unknown(tmp_path):
    args = build(tmp_path,
                 {"exo": ("0 1 * * 1", ["brief.sent", "week.started", "check.never_started"])},
                 {"exo": "Commit on a branch named\nexo/YYYY-MM-DD and open ONE pull request.\n"},
                 rows=[start("exo", "message")],
                 cadences="  - { name: exo, cadence: weekly-sun }\n")
    row = one(wr.verdict(**args), "exo")
    assert [row["types"][t][0] for t in ("brief.sent", "week.started")] == ["live", "live"]
    assert row["types"]["check.never_started"][0] == "live"


def test_a_type_outside_the_transcribed_rules_says_so_rather_than_passing(tmp_path):
    """The rules here are a transcription of another repository's file and it
    will go stale. A type this file has never heard of must not read as fine."""
    args = build(tmp_path,
                 {"engineer": ("6 11,23 * * *", ["ledger.appended"])},
                 {"engineer": "a branch named engineer/YYYY-MM-DD-slug\n"},
                 cadences="  - { name: engineer, cadence: daily }\n")
    assert one(wr.verdict(**args), "engineer")["types"]["ledger.appended"][0] == "unknown"


def test_exit_one_only_on_deaf(tmp_path, capsys):
    gated = build(tmp_path / "a",
                  {"finance": ("", ["pr.merged"])},
                  {"finance": "a branch named testco-finance/YYYY-MM\n"},
                  cadences="  - { name: finance, cadence: none }\n")
    assert wr.render(wr.verdict(**gated), "testco") == 0
    deaf = build(tmp_path / "b",
                 {"security": ("", ["pr.merged"])},
                 {"security": "a branch named sec/YYYY-MM-DD\n"},
                 cadences="  - { name: security, cadence: semimonthly }\n")
    assert wr.render(wr.verdict(**deaf), "testco") == 1


def test_a_wrong_roster_path_exits_two_rather_than_reporting_all_clear(tmp_path):
    """An empty seat list is the shape a wrong `--roster` takes, and reporting
    `no seat is deaf` for it would be this file's own version of the defect it
    was written to find."""
    assert wr.main(["--company", "nosuchco", "--roster", str(tmp_path),
                    "--prompts", str(tmp_path), "--audit", str(tmp_path / "none"),
                    "--company-yaml", str(tmp_path / "none.yaml")]) == 2


def test_the_prefix_column_says_which_world_it_describes():
    """Added 2026-10-26, after this file's own tool produced a false finding in
    the next run of the seat that shipped it.

    The prefix is read from the working checkout and the wake counts from the
    host's audit log, so on a branch the report mixes a charter that exists only
    here with routing that happened only out there. `alexandria-research` was
    read as a prefix fix taking effect on the bus; the fix was on an unmerged
    branch and the two wakes were a capacity re-fire and the message its pull
    request produced, neither of which needs a prefix to route."""
    note = wr.prefix_provenance('prompts')
    assert 'prompts' in note
    assert 'origin/main' in note


def test_an_undeterminable_comparison_says_so_rather_than_claiming_a_match():
    """The one wrong answer this helper could give is silence that reads as
    agreement. A path git cannot compare must not return "matches origin/main"."""
    note = wr.prefix_provenance('/nonexistent-path-outside-any-repo')
    assert 'could not be' in note or 'DIFFERS' in note
    assert 'which matches origin/main' not in note
