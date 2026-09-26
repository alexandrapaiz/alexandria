#!/usr/bin/env python3
"""The run report: what a seat's workflow step posts to the owner's channel.

    python3 tools/run_report.py --status success --workflow engineer-agent
    python3 tools/run_report.py --status failure --workflow pm-agent --dry-run

Reads the pull request for the current branch, composes the five-bullet report
the owner asked for, and posts it to `SLACK_WEBHOOK_URL`. With no webhook set
it says so and exits 0, because the visibility window is the owner's to open.

## Why this is a file and not twelve copies of a shell heredoc

It was twelve copies of a shell heredoc until 2026-09-26, and it failed on the
first two runs that met it (INC-2026-09-26-run-report-dash-echo). The step
declared no `shell:`, so it ran under the container's `sh`, which is dash, and
dash's builtin `echo` expands backslash escapes. Every `\n` inside the pull
request body that `gh` had correctly escaped became a real newline before `jq`
read it, so `jq` refused the input as containing unescaped control characters
and the step exited 4. Both runs had already finished their work and opened
their pull requests. They were marked `failure` anyway, which is the part that
costs the org something: the PM's standup reads run health off those statuses.

Shell embedded in YAML cannot be tested, and a fleet-wide step that cannot be
tested is a fleet-wide step that ships broken. The logic that decides what the
report says now lives in `compose()`, which is pure, and
`tests/test_run_report.py` holds the case that broke it plus the ones that
would have broken it next. L-E0's "agents as first-class citizens" cuts the
same way: a seat can run this file, read its output, and diagnose it, which is
not true of a step body.

## What it never does

It never fails the run. A notification is not the work, and a red job for an
undelivered message is a lie to every reader of `gh run list`. Delivery
problems print as `::warning::` and the exit status stays 0. A composition bug
is different and raises, because that is this file's own contract and a test
should have caught it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

# The owner's two rulings of 2026-09-26, in the order she gave them.
# "communications are pretty dead on slack" -> the report is the pull
# request's own opening, not a log line. "make the slack prose be in
# bullets" -> bullets, not paragraphs, one line each.
MAX_BULLETS = 5
MAX_BULLET_CHARS = 180
BULLET = "•"

_BULLET_LINE = re.compile(r"^\s*[-*•]\s+(.*)$")
_BOLD = re.compile(r"\*\*")
_SKIP_LINE = re.compile(r"^\s*(#|\U0001F916|<!--)")


def _clean(text: str) -> str:
    """One bullet's worth of text: no bold markers, no control characters."""
    text = _BOLD.sub("", text).strip()
    # A control character is what broke the shell version. Strip them here so
    # no downstream JSON encoder has to survive them.
    text = "".join(ch for ch in text if ch == "\t" or ord(ch) >= 0x20)
    return text[:MAX_BULLET_CHARS].rstrip()


def summarize(body: str) -> list[str]:
    """The first five bullet lines of a pull request body, one line each.

    A body with no bullets yields its first two lines of real prose, so a
    description written as paragraphs still reports something.
    """
    bullets: list[str] = []
    for line in (body or "").splitlines():
        match = _BULLET_LINE.match(line)
        if not match:
            continue
        cleaned = _clean(match.group(1))
        if cleaned:
            bullets.append(f"{BULLET} {cleaned}")
        if len(bullets) == MAX_BULLETS:
            return bullets
    if bullets:
        return bullets
    for line in (body or "").splitlines():
        if _SKIP_LINE.match(line) or not line.strip():
            continue
        cleaned = _clean(line)
        if cleaned:
            bullets.append(f"{BULLET} {cleaned}")
        if len(bullets) == 2:
            break
    return bullets


def compose(pr: dict | None, workflow: str, status: str) -> dict:
    """The Slack payload. Pure: no network, no git, no environment."""
    pr = pr or {}
    title = _clean(pr.get("title") or "") or "no PR opened"
    url = (pr.get("url") or "").strip()
    parts = [f"*{workflow}* {BULLET} {status} {BULLET} {title}"]
    summary = summarize(pr.get("body") or "")
    if summary:
        parts.append("\n".join(summary))
    if url:
        parts.append(url)
    return {"text": "\n".join(parts)}


def current_branch() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=False,
    ).stdout.strip()


def fetch_pr(branch: str) -> dict | None:
    """The pull request for this branch, or None. Never raises."""
    if not branch:
        return None
    result = subprocess.run(
        ["gh", "pr", "list", "--head", branch, "--state", "all",
         "--json", "number,title,url,body"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print(f"::warning::gh pr list failed for {branch}: "
              f"{result.stderr.strip()[:300]}")
        return None
    try:
        rows = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        print(f"::warning::gh pr list returned unparseable JSON: {exc}")
        return None
    return rows[0] if rows else None


def post(webhook: str, payload: dict) -> bool:
    """Deliver the payload. Returns whether it landed; never raises."""
    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status >= 300:
                print(f"::warning::Slack returned HTTP {response.status}")
                return False
            return True
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        print(f"::warning::the run report did not reach Slack: {exc}")
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workflow", default=os.environ.get("GITHUB_WORKFLOW", "agent"))
    parser.add_argument("--status", default="unknown")
    parser.add_argument("--branch", default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the payload instead of posting it")
    args = parser.parse_args(argv)

    branch = args.branch or current_branch()
    payload = compose(fetch_pr(branch), args.workflow, args.status)

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook:
        print("No SLACK_WEBHOOK_URL configured; the visibility window is not open yet.")
        return 0

    # The report is printed as well as posted, so the run's own log carries it
    # even when the channel does not (incident 8: judge a run by its artifacts).
    print(payload["text"])
    post(webhook, payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
