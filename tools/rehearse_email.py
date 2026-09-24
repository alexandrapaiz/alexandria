#!/usr/bin/env python3
"""Print the email the press would send. Send nothing.

The owner's ruling of 2026-09-24 was that the emails had no UI, and the
reason nobody had noticed is that there was no way to look at one. The
press's only rendering path ran inside a Modal container, at the moment of
sending, to real subscribers. A render you can only see by mailing it to
somebody is a render nobody checks.

So this is the email half of the rehearsal law
(docs/agents/press-rehearsal.md). It is narrower than the `rehearse()`
function that document specifies: it makes no model call, touches no
provider, writes no row, and therefore costs nothing and can be run as
often as you like. What it shares with that specification is the rule that
matters most: it renders through the press's own code path, not a copy of
it. It calls `weekly.build_messages()`, the same function
`send_newsletter()` calls, so what it prints is what would be sent.

    python3 tools/rehearse_email.py                     # newest local issue
    python3 tools/rehearse_email.py 2026-W39            # a given issue key
    python3 tools/rehearse_email.py 2026-09-19          # a daily key
    python3 tools/rehearse_email.py --out /tmp/mail.html
    python3 tools/rehearse_email.py --from-db 2026-W39  # the real digests row

Exit status is 1 if the render leaves any slot unfilled or any template
region marker behind, so this is usable as a check and not only as a
viewer.
"""

import argparse
import os
import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub modal exactly the way tests/test_press_resilience.py does, so the press
# module imports without the SDK or any credentials. Nothing under test here
# needs Modal: the decorators are the only thing that touches it.
if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)

    class _Image:
        def __getattr__(self, name):
            return lambda *a, **k: self

    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Image())
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

from pipeline import weekly  # noqa: E402

ISSUES = ROOT / "site" / "content" / "issues"


def body_from_repo(key: str | None) -> tuple[str, str]:
    files = sorted(ISSUES.glob("*.md"))
    if not files:
        raise SystemExit(f"no issues in {ISSUES}")
    if key:
        path = ISSUES / f"{key}.md"
        if not path.exists():
            have = ", ".join(f.stem for f in files)
            raise SystemExit(f"no issue {key} in the repo. Have: {have}")
    else:
        path = files[-1]
    return path.stem, path.read_text()


def body_from_db(key: str | None) -> tuple[str, str]:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise SystemExit("--from-db needs DATABASE_URL in the environment")
    import psycopg

    with psycopg.connect(url) as conn:
        if key:
            row = conn.execute(
                "select week, body from digests where week = %s", (key,)
            ).fetchone()
        else:
            row = conn.execute(
                "select week, body from digests order by created_at desc limit 1"
            ).fetchone()
    if not row:
        raise SystemExit(f"no digests row for {key or 'the newest issue'}")
    return row[0], row[1]


def audit(html: str) -> list[str]:
    """What a filled template must not still contain."""
    problems = []
    slots = sorted(set(re.findall(r"{{(\w+)}}", html)))
    if slots:
        problems.append(f"unfilled slots: {', '.join(slots)}")
    markers = sorted(set(re.findall(r"<!-- (?:BEGIN|END):(\w+) -->", html)))
    if markers:
        problems.append(f"template regions left in place: {', '.join(markers)}")
    if "{{" in html or "}}" in html:
        problems.append("stray braces in the output")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("key", nargs="?", help="issue key, e.g. 2026-W39 or 2026-09-19")
    ap.add_argument("--from-db", action="store_true",
                    help="read the body from the digests table instead of the repo")
    ap.add_argument("--to", default="reader@example.com",
                    help="the recipient the footer names")
    ap.add_argument("--out", help="also write the HTML here")
    ap.add_argument("--quiet", action="store_true",
                    help="print the summary and the audit, not the HTML")
    args = ap.parse_args()

    key, body = (body_from_db if args.from_db else body_from_repo)(args.key)

    # The press's own path. Note what is not here: no SMTP connection, no
    # credentials, no subscriber query. build_messages() renders and returns.
    sender = os.environ.get("GMAIL_ADDRESS", "").strip() or "hello@alexandr.ia"
    messages = weekly.build_messages(key, body, [(args.to, None)], sender)
    email, subject, text, html = messages[0]

    render = weekly.email_render()
    issue = render.parse_issue(body)
    edition, edition_short = render.edition_for(key)

    print(f"rehearsal: {key}, nothing sent")
    print(f"  subject:       {subject}")
    print(f"  preheader:     {render.preheader_for(issue)}")
    print(f"  edition:       {edition}")
    print(f"  footer reads:  You are receiving {edition_short} of alexandria "
          f"at {email}.")
    print(f"  sections:      "
          f"{', '.join(s['title'] for s in issue['sections']) or 'none'}")
    print(f"  items:         {sum(len(s['items']) for s in issue['sections'])}")
    print(f"  html:          {len(html)} bytes")
    print(f"  plain text:    {len(text)} bytes (the markdown body, unchanged)")

    if args.out:
        Path(args.out).write_text(html)
        print(f"  written to:    {args.out}")

    problems = audit(html)
    if problems:
        print("\nFAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("  slots:         every slot filled, no regions left behind")

    if not args.quiet:
        print("\n" + "-" * 70)
        print(html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
