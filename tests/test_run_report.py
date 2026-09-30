#!/usr/bin/env python3
"""The run report's promises, including the one the shell version broke.

    python3 -m pytest tests/test_run_report.py -q

INC-2026-09-26-run-report-dash-echo is the reason this file exists. The report
step was twenty lines of shell inside twelve workflow files, so nothing could
test it, and it failed on the first two runs that met it. The first test below
is that failure, expressed against a real pull request body.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import run_report  # noqa: E402


# A body shaped like the ones the seats actually write: bullets, bold markers,
# headings, a table, and the attribution line the ban list puts at the bottom.
REAL_BODY = """- The board exists and it is ours: `python3 tools/board.py show` prints it.
- Owner priority 1 tonight, relayed live through the PM's sync session.
- The store is a dedicated ref, one JSON file per event, append only.
- The one-line workflow step is queued, because no seat can push workflows.
- Two incidents filed, one of them found from inside itself.

## Read this first

**This PR supersedes #110.** It is built on the other branch.

| Job | cap |
|---|---|
| Triage | $0.60 |

\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)
"""


def test_the_dash_echo_corruption_cannot_recur():
    """The failure itself: a body whose escaped newlines must survive transport.

    The shell version ran `echo "$pr" | jq`, and under dash `echo` expanded the
    `\\n` sequences inside the JSON string into real newlines, so jq rejected
    its own input with "control characters from U+0000 through U+001F must be
    escaped" and the step exited 4. This walks the same round trip: gh's JSON
    in, a Slack payload out, and the payload must be valid JSON.
    """
    gh_output = json.dumps([{  # exactly what `gh pr list --json` emits
        "number": 115,
        "title": "Engineer 2026-09-26 (run 2): the board's own store",
        "url": "https://github.com/alexandrapaiz/alexandria/pull/115",
        "body": REAL_BODY,
    }])
    pr = json.loads(gh_output)[0]
    payload = run_report.compose(pr, "engineer-agent", "success")
    # The payload survives a JSON round trip, which is what jq refused to do.
    assert json.loads(json.dumps(payload)) == payload
    assert "\\n" not in payload["text"]  # real newlines, not literal backslash-n
    assert payload["text"].count("\n") >= 5


def test_no_control_characters_reach_the_payload():
    """Any raw control character is stripped rather than carried."""
    pr = {"title": "a\x01title", "url": "", "body": "- first\x00bullet\x1f here"}
    text = run_report.compose(pr, "w", "success")["text"]
    assert not any(ord(ch) < 0x20 and ch != "\n" for ch in text)
    assert "atitle" in text


def test_five_bullets_one_line_each():
    """The owner's ruling: bullets, not paragraphs, capped at five."""
    bullets = run_report.summarize(REAL_BODY)
    assert len(bullets) == run_report.MAX_BULLETS
    assert all(b.startswith("• ") for b in bullets)
    assert all("\n" not in b for b in bullets)
    assert bullets[0].startswith("• The board exists")


def test_bold_markers_are_stripped():
    bullets = run_report.summarize("- **This PR supersedes #110.** Built on it.")
    assert bullets == ["• This PR supersedes #110. Built on it."]


def test_long_bullets_are_cut_to_one_line():
    bullets = run_report.summarize("- " + "x" * 400)
    assert len(bullets[0]) <= run_report.MAX_BULLET_CHARS + 2


def test_a_body_with_no_bullets_falls_back_to_prose():
    """The fallback the shell version had but could not prove it reached."""
    body = "# Heading\n\nThe corpus is not being read.\nSo this run fixed it.\nA third line.\n"
    bullets = run_report.summarize(body)
    assert bullets == [
        "• The corpus is not being read.",
        "• So this run fixed it.",
    ]


def test_attribution_and_headings_never_become_the_report():
    body = "# Title\n\n\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)\n"
    assert run_report.summarize(body) == []


def test_an_empty_body_composes_a_valid_payload():
    payload = run_report.compose({"title": "t", "url": "u", "body": ""}, "wf", "failure")
    assert payload == {"text": "*wf* • failure • t\nu"}


def test_no_pull_request_still_reports():
    """A run that shipped nothing still says so, rather than crashing."""
    payload = run_report.compose(None, "market-agent", "failure")
    assert payload == {"text": "*market-agent* • failure • no PR opened"}


def test_the_header_carries_workflow_and_status():
    text = run_report.compose({"title": "T", "url": "", "body": ""}, "pm-agent", "success")["text"]
    assert text.startswith("*pm-agent* • success • T")


@pytest.mark.parametrize("marker", ["-", "*", "•"])
def test_every_bullet_marker_the_seats_use(marker):
    assert run_report.summarize(f"{marker} a line") == ["• a line"]


def test_dry_run_prints_a_payload_and_exits_zero(monkeypatch, capsys):
    monkeypatch.setattr(run_report, "fetch_pr", lambda branch: {
        "title": "T", "url": "https://example.test/1", "body": REAL_BODY})
    monkeypatch.setattr(run_report, "current_branch", lambda: "engineer/x")
    assert run_report.main(["--status", "success", "--workflow", "engineer-agent",
                            "--dry-run"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["text"].startswith("*engineer-agent* • success • T")


def test_a_missing_webhook_is_not_a_failure(monkeypatch, capsys):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    monkeypatch.setattr(run_report, "fetch_pr", lambda branch: None)
    monkeypatch.setattr(run_report, "current_branch", lambda: "b")
    assert run_report.main(["--status", "success"]) == 0
    assert "visibility window is not open" in capsys.readouterr().out


def test_an_undelivered_report_never_fails_the_run(monkeypatch, capsys):
    """A notification is not the work. A red job for a dead webhook is a lie."""
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.invalid/nope")
    monkeypatch.setattr(run_report, "fetch_pr", lambda branch: None)
    monkeypatch.setattr(run_report, "current_branch", lambda: "b")

    monkeypatch.setattr(run_report, "post", lambda webhook, payload: False)
    assert run_report.main(["--status", "failure"]) == 0


def test_gh_failure_degrades_to_no_pull_request(monkeypatch, capsys):
    monkeypatch.setattr(run_report.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(
        a[0], 1, stdout="", stderr="gh: not authenticated"))
    assert run_report.fetch_pr("branch") is None
    assert "::warning::" in capsys.readouterr().out


def test_the_script_runs_under_the_container_shell():
    """The regression guard for the actual bug: no shell quoting in the path.

    The step now invokes one command with no pipes and no `echo`, so dash and
    bash agree. This runs it under `sh -e`, which is what the workflow gets
    when it declares no `shell:` key, and that is the exact condition that
    produced the failure.
    """
    script = (
        f"cd {ROOT} && python3 tools/run_report.py --status success "
        f"--workflow engineer-agent --branch does-not-exist-anywhere --dry-run"
    )
    result = subprocess.run(["sh", "-e", "-c", script],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["text"].startswith("*engineer-agent*")
