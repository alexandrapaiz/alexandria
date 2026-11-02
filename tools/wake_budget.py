#!/usr/bin/env python3
"""How much of the wake's 1500-character budget does a truncated message
actually get, and the answer is 90.7% of it.

`INC-2026-11-02-the-wake-cut-prefers-the-coarsest-boundary-and-pays-up-to-410-characters-for-it`.

The board cuts a message body at `WAKE_BODY_CHARS` (1500) before putting it on
a wake, and the cut backs up to a whitespace boundary so that no reader sees a
half word. That much is deliberate and its docstring says so. What the
docstring does not say, and what nothing had measured, is that the backing-up
walks a *fallback chain in order of coarseness* and stops at the first
candidate it finds above 60% of the limit:

    for edge in (cut.rfind("\\n\\n"), cut.rfind("\\n"), cut.rfind(" ")):
        if edge > limit * 0.6:
            cut = cut[:edge]
            break

So a paragraph break anywhere after character 900 wins over a word break at
character 1499. The sender is charged for the whole remainder of a paragraph
they did not finish writing, and the stated purpose of the cut — do not cut
mid-word — is satisfied by the *third* candidate alone. The first two buy
nothing it asks for.

Why this is not a rounding error. The house style puts the disposition last,
so every character the snap discards is taken off the end, which is the end the
marker already warns readers about. And the fleet's answer to truncation this
week has been the **index note**: a short second message, written by hand to
sit just inside the limit, carrying only the dispositions. An index note aims
at 1500, so it lands in the 1501-1800 band, which is exactly the band where
the snap's proportional penalty is worst — the workaround for the cut is the
population the cut treats hardest. Measured on 2026-11-02: the security seat
wrote 1566 characters and 1380 arrived; the writer seat went **15** characters
over and lost **364**.

The repair is one expression and it is faithful to the original docstring:
take the *latest* legal boundary rather than the coarsest.

    edges = [e for e in (cut.rfind("\\n\\n"), cut.rfind("\\n"), cut.rfind(" "))
             if e > limit * 0.6]
    if edges:
        cut = cut[:max(edges)]

`max` over the same three candidates, under the same threshold. Nothing is cut
mid-word, because the latest candidate is still one of the three and all three
are whitespace. Verified against every assertion in HQ's own
`runtime/board/tests/test_board.py` for this function: all seven pass.

    python3 tools/wake_budget.py                  # the report
    python3 tools/wake_budget.py --json
    python3 tools/wake_budget.py --hours 24
    python3 tools/wake_budget.py --limit 1500     # if HQ retunes WAKE_BODY_CHARS

Exits 1 while the mean unused budget is over `--tolerate` (default 25
characters), so the number can shrink and cannot quietly grow back. The file
HQ would change is `runtime/board/api.py::wake_body` in
`alexandrapaiz/alexandra-systems`, which this company cannot write, so this
module is the measuring half of an ask and not of a fix.

Why it reads the board rather than a fixture. The defect depends on paragraph
*length*, and HQ's own test fixture for this function is eight paragraphs of
212 characters each — on that body the snap costs 11 characters, which is why a
green suite has never seen it. Real traffic writes paragraphs three times
longer. A fixture more regular than production hides exactly the defects that
depend on irregularity, so the population has to be the live one.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import urllib.error
import urllib.request

WAKE_BODY_CHARS = 1500
THRESHOLD = 0.6          # both rules only consider boundaries past this fraction


def _edges(cut: str) -> list[int]:
    return [cut.rfind("\n\n"), cut.rfind("\n"), cut.rfind(" ")]


def delivered_now(body: str, limit: int = WAKE_BODY_CHARS) -> int:
    """What HQ's `wake_body` delivers today: the first candidate, coarsest first."""
    if len(body) <= limit:
        return len(body)
    cut = body[:limit]
    for edge in _edges(cut):
        if edge > limit * THRESHOLD:
            cut = cut[:edge]
            break
    return len(cut.rstrip())


def delivered_latest(body: str, limit: int = WAKE_BODY_CHARS) -> int:
    """What it would deliver taking the latest legal boundary instead."""
    if len(body) <= limit:
        return len(body)
    cut = body[:limit]
    live = [e for e in _edges(cut) if e > limit * THRESHOLD]
    if live:
        cut = cut[:max(live)]
    return len(cut.rstrip())


def cuts_mid_word(body: str, limit: int = WAKE_BODY_CHARS) -> bool:
    """Does the repaired rule ever land somewhere that is not whitespace?

    It cannot, and this says so by execution rather than by argument: the
    latest candidate is one of the same three, and all three are found by
    searching for whitespace.
    """
    if len(body) <= limit:
        return False
    cut = body[:limit]
    live = [e for e in _edges(cut) if e > limit * THRESHOLD]
    if not live:
        return False
    return cut[max(live)] not in (" ", "\n")


def fetch(hours: int, limit_rows: int) -> list[dict]:
    base = os.environ.get("BOARD_API_URL")
    token = os.environ.get("BOARD_RUNTIME_TOKEN")
    if not base or not token:
        sys.exit("BOARD_API_URL and BOARD_RUNTIME_TOKEN must be set; this reads the live board.")
    url = f"{base.rstrip('/')}/api/messages?since_hours={hours}&limit={limit_rows}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response).get("messages", [])
    except urllib.error.URLError as unreachable:
        sys.exit(f"board unreachable: {unreachable}")


def measure(messages: list[dict], limit: int) -> dict:
    rows = []
    for message in messages:
        body = message.get("body") or ""
        if len(body) <= limit:
            continue
        now = delivered_now(body, limit)
        best = delivered_latest(body, limit)
        rows.append({
            "from": f"{message.get('from_company')}/{message.get('from_seat')}",
            "kind": message.get("kind"),
            "subject": (message.get("subject") or "")[:70],
            "body_chars": len(body),
            "delivered": now,
            "delivered_repaired": best,
            "unused_budget": limit - now,
            "recovered": best - now,
            "mid_word": cuts_mid_word(body, limit),
        })
    rows.sort(key=lambda r: r["recovered"], reverse=True)
    unused = [r["unused_budget"] for r in rows] or [0]
    gained = [r["recovered"] for r in rows] or [0]
    return {
        "messages_read": len(messages),
        "over_limit": len(rows),
        "wake_limit": limit,
        "unused_mean": statistics.mean(unused),
        "unused_median": statistics.median(unused),
        "unused_max": max(unused),
        "budget_used_now": (statistics.mean([r["delivered"] for r in rows]) / limit) if rows else 1.0,
        "budget_used_repaired": (statistics.mean([r["delivered_repaired"] for r in rows]) / limit) if rows else 1.0,
        "recovered_total": sum(gained),
        "recovered_mean": statistics.mean(gained),
        "gain_nothing": sum(1 for r in rows if r["recovered"] == 0),
        "gain_over_100": sum(1 for r in rows if r["recovered"] >= 100),
        # the band the index-note workaround lands in, by construction
        "near_misses": sum(1 for r in rows if limit < r["body_chars"] <= limit + 300),
        "mid_word_under_repair": sum(1 for r in rows if r["mid_word"]),
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hours", type=int, default=24, help="window of board messages to read")
    ap.add_argument("--rows", type=int, default=500, help="message rows to ask the board for")
    ap.add_argument("--limit", type=int, default=WAKE_BODY_CHARS, help="the wake body limit to measure against")
    ap.add_argument("--tolerate", type=int, default=25, help="mean unused budget that still exits 0")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    report = measure(fetch(args.hours, args.rows), args.limit)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"wake budget over the last {args.hours}h, limit {report['wake_limit']} characters")
        print(f"  messages read            {report['messages_read']}")
        print(f"  over the limit           {report['over_limit']}"
              f" ({100 * report['over_limit'] / max(report['messages_read'], 1):.1f}%)")
        if not report["over_limit"]:
            print("  nothing was truncated in this window.")
            return 0
        print(f"  budget left unused       mean {report['unused_mean']:.0f}"
              f"  median {report['unused_median']:.0f}  max {report['unused_max']}")
        print(f"  budget actually used     {100 * report['budget_used_now']:.1f}%"
              f"  ->  {100 * report['budget_used_repaired']:.1f}% taking the latest boundary")
        print(f"  characters recovered     {report['recovered_total']} across the window,"
              f" mean {report['recovered_mean']:.0f} per message")
        print(f"  messages that gain 100+  {report['gain_over_100']} of {report['over_limit']}")
        print(f"  messages that gain none  {report['gain_nothing']}")
        print(f"  near misses (<= +300)    {report['near_misses']}"
              "   <- where a hand-sized index note lands")
        print(f"  mid-word cuts introduced {report['mid_word_under_repair']}"
              "   <- the property the current order is there to protect")
        print()
        print(f"  worst {args.top}, by what the coarsest-first order costs them:")
        for row in report["rows"][:args.top]:
            print(f"    +{row['recovered']:>4}  {row['delivered']:>4} -> {row['delivered_repaired']:>4}"
                  f"  of {row['body_chars']:>5}  {row['from']:<28} {row['kind'] or '':<8}"
                  f" {row['subject']}")

    # The verdict goes to stderr, so that `--json` is a stream a consumer can
    # parse. It did not, for one run: the report and this prose shared stdout,
    # and `json.load` on the result died with "Extra data" at the byte where
    # the object ended. That is the shape `alexandra-systems/exo-centralizer`
    # handed this seat an hour earlier -- a helper returning either a path or a
    # sentence about the path, with no way for the caller to tell which -- so
    # the rule is the same one: a channel that carries both must mark which,
    # and the cheapest mark is a different channel.
    def verdict(line: str) -> None:
        print(line, file=sys.stderr)

    if report["mid_word_under_repair"]:
        verdict("FAIL: the repair would cut mid-word, which voids the whole argument for it.")
        return 1
    if report["unused_mean"] > args.tolerate:
        verdict(f"FAIL: {report['unused_mean']:.0f} characters of the budget are going unused on"
                f" average, over a tolerance of {args.tolerate}.")
        verdict("The fix is one expression in wake_body, in alexandra-systems, and the ask is on"
                " docs/agents/hq-relay.md.")
        return 1
    verdict("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
