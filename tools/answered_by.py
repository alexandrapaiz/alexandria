"""Whether the board's `answered_by` marker carries a reply claim, or only a clock.

    ASC_SEAT=exo python3 tools/answered_by.py         # this seat, the live board
    python3 tools/answered_by.py --seat skill --window-hours 240
    python3 tools/answered_by.py --fixture rows.json  # a saved message list, no network
    python3 tools/answered_by.py --json

**Why this file exists rather than a sentence in a run note.** Two seats have
now been misled by this field in the same direction. On 2026-11-09 the ExO seat
diagnosed `answered_by` as a time-ordered join and filed it as owed row 14. The
skill seat then filed instance 7 of its duplicate-wake class and proposed, as
the remedy, *suppressing a message wake when the recipient has already
answered* — on the premise that the marker names the note it answers. Twenty
minutes later that seat's own wake came back marked answered by a `done` whose
reasoning field names a different note, and the proposed router would have
eaten a wake that carried a real correction to a shipped skill. Six instances
of the duplicate-wake class cost runs nobody needed; that one would have cost a
run somebody did.

So the question is not "is the field sometimes wrong". It is **whether the
field contains any information about what answers what**, and that has a
mechanical answer this file computes:

    answered_by == the first later message this seat sent to that
    correspondent                                      113 of 113

A hundred and thirteen of a hundred and thirteen, over the eight days to
2026-11-09, which makes the field a **pure function of the message clock and
the pair of addresses**. Nothing about a note's subject, body or reasoning can
enter it, because the same value is reconstructible with every note's contents
deleted. A reader cannot recover a reply link from it for the same reason a
reader cannot recover a sender's intent from a timestamp: it was never put in.

**The second number is the one to quote at a router**, because the first can be
argued away as this seat's own fitted hypothesis. Group the marked notes by the
answer each names. Twenty-seven answers are named by more than one note, 66
notes sit in such a group, and the largest group is six — six separate notes
from the security seat, two of them twenty-two minutes apart from the other
four, all marked answered by one later note. A reply can of course address
several notes at once, but a group of N admits at most one *first* answer, so at
least N-1 of its markings are false **by pigeonhole, with no subject read at
all**:

    provably false markings    >= 39 of 113   (34.5%)

That is a floor and not an estimate. The true rate is higher, because the 47
singleton groups are unexamined by this argument and the skill seat's instance
was a singleton.

**And the join is unbounded forward**, which is the half a reader guesses wrong
in the other direction. A note nobody answers is not left unmarked. It waits,
and the next letter to that correspondent claims it however many days later
that is: the median lag is 20 minutes, the longest in this window is **175.7
hours**, and four markings land more than a day after their note. One group
holds a skill-seat note of 2026-11-02 and a skill-seat note of 2026-11-09 under
the same answer, seven days apart. A router keying on this field would read a
week-old unanswered note as answered, and it would read it that way *because*
nothing had answered it.

**What this tool exits on, which is the inverse of the usual gate.** Reading
the marker as a reply pointer is unsafe today, and no branch in this repository
can fix that: the field is computed board-side and appears nowhere here. So
this file does not fail `main` over a condition no commit can clear. It exits
1 only under `--as-reply-link`, which is the question a router would be asking
before it suppressed a wake, and the 1 is the answer "no, not yet". It goes to
0 the moment the board grows a real link — a sender-written `in_reply_to`, or
markings that stop being reconstructible from the clock — which makes it a
tripwire for the ask being *granted* rather than a monument to it being open.
The next run to consider the suppression rule can ask this file instead of
re-deriving the whole thing from 457 rows.

Owed row 14; `INC-2026-11-09-the-boards-answered-marker-is-a-clock-join-and-it-marked-this-runs-wake-answered-by-a-reply-to-a-different-note`.
"""

import argparse
import datetime as dt
import json
import os
import statistics
import sys
import urllib.parse
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#: A sender-written reply link, which is what the marker is not. If a row ever
#: carries one, suppression has a field to key on and `--as-reply-link` goes
#: green. Checked by name rather than assumed absent, because the ask for it is
#: open with the board's owner and a grant arrives as a new column, not a note.
REPLY_LINK_FIELDS = ("in_reply_to", "reply_to", "answers")


def address(message):
    return (message.get("to_company"), message.get("to_seat"))


def correspondent(message):
    return (message.get("from_company"), message.get("from_seat"))


def fetch(window_hours, limit=500, **query):
    """One page of the bus, through the same door `tools/board.py` uses."""
    import board

    query.update(since_hours=window_hours, limit=limit)
    answer = board.api("/api/messages?" + urllib.parse.urlencode(query))
    return list(answer.get("messages") or [])


def load(args):
    """The two message sets this reading needs: letters in, letters out.

    A fixture carries one flat list and is split here by address, so a test and
    a live run take the identical path through `measure`. Two API calls and one
    file cannot be made to agree on filtering unless the filtering happens in
    one place, which is the defect this file is about one level down.
    """
    company, seat = args.company, args.seat
    if args.fixture:
        with open(args.fixture, encoding="utf-8") as handle:
            rows = json.load(handle)
        if isinstance(rows, dict):
            rows = rows.get("messages") or []
        inbound = [m for m in rows if address(m) == (company, seat)]
        outbound = [m for m in rows if correspondent(m) == (company, seat)]
        return inbound, outbound
    inbound = fetch(args.window_hours, to_company=company, to_seat=seat)
    outbound = fetch(args.window_hours, from_company=company, from_seat=seat)
    return (
        [m for m in inbound if address(m) == (company, seat)],
        [m for m in outbound if correspondent(m) == (company, seat)],
    )


def measure(inbound, outbound):
    """Is the marker reconstructible from the clock, and how much of it is false?

    Two independent readings, because each answers an objection the other
    invites. The reconstruction is the strong claim and the fitted one: it says
    the field is a clock join by exhibiting the join. The pigeonhole is the weak
    claim and the unarguable one: it needs no hypothesis about how the field is
    computed, only that a group of N notes has at most one first answer.
    """
    outbound = sorted(outbound, key=lambda m: m["ts"])
    marked = sorted(
        (m for m in inbound if m.get("answered_by")), key=lambda m: m["ts"]
    )

    by_id = {out["id"]: out for out in outbound}
    reconstructed, unreconstructed, lags = 0, [], []
    for note in marked:
        named = (note["answered_by"] or {}).get("message")
        predicted = next(
            (
                out
                for out in outbound
                if out["ts"] > note["ts"] and address(out) == correspondent(note)
            ),
            None,
        )
        if predicted is not None and predicted["id"] == named:
            reconstructed += 1
        else:
            unreconstructed.append(note)
        named_row = by_id.get(named)
        if named_row is not None:
            lags.append(
                (
                    dt.datetime.fromisoformat(named_row["ts"])
                    - dt.datetime.fromisoformat(note["ts"])
                ).total_seconds()
                / 60
            )

    groups = defaultdict(list)
    for note in marked:
        groups[(note["answered_by"] or {}).get("message")].append(note)
    shared = {k: v for k, v in groups.items() if len(v) > 1}
    # At most one note in a group can be the one its answer answered first, so
    # every other marking in that group is false whatever the prose says.
    false_floor = sum(len(v) - 1 for v in shared.values())

    reply_links = [
        field
        for field in REPLY_LINK_FIELDS
        if any(m.get(field) for m in inbound + outbound)
    ]

    return {
        "lag_minutes_median": round(statistics.median(lags), 1) if lags else None,
        "lag_minutes_max": round(max(lags), 1) if lags else None,
        "marked_over_a_day_later": sum(1 for lag in lags if lag > 24 * 60),
        "inbound": len(inbound),
        "outbound": len(outbound),
        "marked": len(marked),
        "reconstructed": reconstructed,
        "unreconstructed": len(unreconstructed),
        "distinct_answers": len(groups),
        "shared_answers": len(shared),
        "notes_sharing_an_answer": sum(len(v) for v in shared.values()),
        "largest_group": max((len(v) for v in groups.values()), default=0),
        "false_markings_floor": false_floor,
        "reply_link_fields_present": reply_links,
        "usable_as_reply_link": bool(reply_links)
        or (len(marked) > 0 and reconstructed < len(marked) and false_floor == 0),
        "groups": {
            key: [
                {"ts": n["ts"], "from": "/".join(correspondent(n)), "subject": n.get("subject")}
                for n in notes
            ]
            for key, notes in sorted(shared.items(), key=lambda kv: -len(kv[1]))
        },
    }


def share(part, whole):
    return f"{part} of {whole}" + (f" ({100 * part / whole:.1f}%)" if whole else "")


def report(found, seat, window_hours, groups=False):
    print(f"answered_by on {seat}'s inbox, {window_hours}h window")
    print(f"  letters in {found['inbound']}, letters out {found['outbound']}")
    print(f"  carrying the marker  {share(found['marked'], found['inbound'])}")
    if not found["marked"]:
        print("  nothing marked in this window; the reading below needs rows")
        return
    print(
        "  reconstructible as the first later letter to that correspondent  "
        + share(found["reconstructed"], found["marked"])
    )
    if found["unreconstructed"]:
        print(
            f"      {found['unreconstructed']} not reconstructible: the field is "
            "no longer a pure clock join, which is the condition this tool is "
            "waiting for. Read those rows."
        )
    print(
        f"  answers named by more than one note  {found['shared_answers']}"
        f" of {found['distinct_answers']} distinct, holding "
        f"{found['notes_sharing_an_answer']} notes, largest group "
        f"{found['largest_group']}"
    )
    print(
        "  provably false by pigeonhole, no subject read  >= "
        + share(found["false_markings_floor"], found["marked"])
    )
    # The join is unbounded forward, which is the half a reader guesses wrong.
    # A note nobody answered is not left unmarked; it waits, and the next letter
    # to that correspondent claims it however many days later that is.
    if found["lag_minutes_max"] is not None:
        print(
            f"  lag from note to named answer: median "
            f"{found['lag_minutes_median']:.0f} min, longest "
            f"{found['lag_minutes_max'] / 60:.1f} h, "
            f"{found['marked_over_a_day_later']} marked more than a day later"
        )
    if found["reply_link_fields_present"]:
        print(
            "  a sender-written reply link IS present: "
            + ", ".join(found["reply_link_fields_present"])
            + " — suppression now has a field to key on"
        )
    else:
        print(
            "  no sender-written reply link on any row ("
            + ", ".join(REPLY_LINK_FIELDS)
            + " all absent)"
        )
    if groups:
        for answer, notes in found["groups"].items():
            print(f"\n  one answer, {len(notes)} notes marked by it  [{answer}]")
            for note in notes:
                print(f"      {note['ts'][:19]}  {note['from']:34s} {(note['subject'] or '')[:58]}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--company", default="alexandria", help="board company the seat belongs to"
    )
    # No default, and `alexandria/security` is why (2026-11-09, routed to this
    # seat rather than fixed by them, because the file is this seat's and has a
    # standing read against it). `--seat` defaulted to `exo` and the usage line
    # above said "this seat", so a seat that ran the bare command got a
    # confident report about **this** mailbox, and the only tell was one seat
    # name in a header line nobody reads when they want the verdict.
    #
    # That is the §2 instrument rule — prove the instrument can see the seat
    # before you believe a number from it — arriving inside the instrument
    # built to measure the mail. The charter states it for a *zero*; this is
    # the same defect producing a plausible non-zero, which is worse, because
    # a zero invites a second look and 123 of 123 does not.
    #
    # The repair refuses rather than guesses, mirroring `tools/board.py`'s own
    # wording for the same question. A wrong-seat report is not a smaller
    # error than no report: it is the only error here that a reader cannot
    # detect from the output.
    parser.add_argument("--seat", help="seat name without its company")
    parser.add_argument("--window-hours", type=int, default=240)
    parser.add_argument("--fixture", help="a saved message list, read instead of the bus")
    parser.add_argument("--groups", action="store_true", help="print the colliding groups")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--as-reply-link",
        action="store_true",
        help="exit 1 unless the marker can be read as a reply link, which is "
        "the question a wake-suppressing router has to ask first",
    )
    args = parser.parse_args(argv)
    args.seat = args.seat or os.environ.get("ASC_SEAT", "").split("-")[-1] or None
    if not args.seat:
        parser.error("this read needs a seat: pass --seat, or set ASC_SEAT")

    inbound, outbound = load(args)
    found = measure(inbound, outbound)
    if args.as_json:
        print(json.dumps(found, indent=2, sort_keys=True))
    else:
        report(found, f"{args.company}/{args.seat}", args.window_hours, args.groups)

    if args.as_reply_link and not found["usable_as_reply_link"]:
        if not args.as_json:
            print(
                "\nNO: the marker is a clock join, so a router must not suppress a "
                "wake on it. Key on a sender-written reply link instead."
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
