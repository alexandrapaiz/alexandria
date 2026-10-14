#!/usr/bin/env python3
"""Blind prose benchmark: alexandria's digest against a comparison newsletter.

Sprint 2026-09-21 item 2, and the ledger's "Repeatable prose benchmark"
entry. The point of this file is that no human hand chooses the extract
or hides the branding. Both are rules, both run the same way on both
sides, and the tests pin them.

    build   cut both specimens, blind them, shuffle, write the packet
    reveal  print which specimen is whose, from the seed
    tally   read the returned scoring sheets and write the result

Graders receive the packet. They never receive the key, and the key is
not stored: `reveal` recomputes it from the seed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import sys
import unicodedata

# ---------------------------------------------------------------- blinding

# Every substitution below runs on BOTH specimens. Where only one side is
# affected, the file that documents this benchmark says so, because a rule
# that touches one publication and not the other is a thumb on the scale.
PUNCTUATION = {
    "‐": "-", "‑": "-", "‒": "-", "–": "-",
    "—": " - ",
    " ": " ", " ": " ", " ": " ", " ": " ",
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "…": "...", "×": "x", "‍": "",
}

MD_LINK = re.compile(r"\[([^\]]*)\]\((?:[^)]*)\)")
BARE_URL = re.compile(r"https?://\S+")
ANNOTATION = re.compile(r"\s*\((?:\d+\s*minute read|GitHub Repo|Sponsor)\)", re.I)
EMPHASIS = re.compile(r"(\*\*|__|\*|_|`)(.+?)\1", re.S)


def normalise_punctuation(text: str) -> str:
    """Typographic characters to ASCII, then the space before a percent sign.

    This is the substitution that matters most. 2026-W37 carries 16
    non-breaking hyphens and 2 narrow no-break spaces in the passage used
    here, and the comparison issue's prose carries none, so a grader could
    separate the two specimens by searching for a character rather than by
    reading either of them.
    """
    for bad, good in PUNCTUATION.items():
        text = text.replace(bad, good)
    text = re.sub(r"\s+%", "%", text)
    text = "".join(c for c in text if ord(c) < 128 or unicodedata.category(c)[0] != "S")
    text = "".join(c for c in text if ord(c) < 128)
    # Collapse runs of spaces inside a line, but never the indentation that
    # marks a sub-list, because that indentation is structure the grader is
    # meant to see.
    return "\n".join(
        re.match(r"[ \t]*", line).group(0) + re.sub(r"[ \t]+", " ", line.strip())
        for line in text.split("\n")
    )


def redact_links(text: str) -> str:
    text = MD_LINK.sub(lambda m: m.group(1).strip() or "[link]", text)
    return BARE_URL.sub("[link]", text)


def strip_emphasis(text: str) -> str:
    """Bold and italics go, on both sides.

    The comparison issue reaches us as rendered text with its markup
    already gone. Leaving alexandria's bold in place would hand the grader
    a typographic signature instead of a sentence, so both specimens are
    flattened and the benchmark measures prose.
    """
    for _ in range(3):
        text = EMPHASIS.sub(lambda m: m.group(2), text)
    return text


def blind(text: str, publishers: list[str]) -> str:
    text = normalise_punctuation(text)
    text = redact_links(text)
    text = ANNOTATION.sub("", text)
    text = strip_emphasis(text)
    for name in sorted(publishers, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(name)}\b", "[publication]", text, flags=re.I)
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


def words(text: str) -> int:
    return len(text.split())


# -------------------------------------------------------------- extraction


def extract_house(issue: str) -> tuple[str, str, list[str]]:
    """The issue's opening, then the first item of its first section.

    Returns (opening, section heading, item lines). The rule is positional
    and takes no view of which item reads best.
    """
    lines = issue.split("\n")
    try:
        first_section = next(i for i, l in enumerate(lines) if l.startswith("## "))
    except StopIteration:
        raise SystemExit("house issue has no '## ' section heading")
    opening = "\n".join(lines[1:first_section]).strip()
    body = lines[first_section:]
    starts = [i for i, l in enumerate(body) if l.startswith("- ")]
    if not starts:
        raise SystemExit("house issue's first section has no items")
    end = starts[1] if len(starts) > 1 else len(body)
    item = [l for l in body[starts[0]:end] if l.strip()]
    return opening, body[0][3:].strip(), item


def parse_comparison(source: str) -> tuple[dict, list[dict]]:
    head, _, rest = source.partition("\n---\n")
    meta = {}
    for line in head.split("\n"):
        key, _, value = line.partition(":")
        if value.strip():
            meta.setdefault(key.strip(), value.strip())
    sections: list[dict] = []
    for line in rest.split("\n"):
        if line.startswith("## "):
            sections.append({"name": line[3:].strip(), "items": []})
        elif not sections or not line.strip():
            continue
        elif line.startswith("(items not retained"):
            continue
        elif ANNOTATION.search(line) and line.strip().endswith(")"):
            sections[-1]["items"].append({"title": line.strip(), "body": []})
        elif sections[-1]["items"]:
            sections[-1]["items"][-1]["body"].append(line.strip())
    return meta, sections


def extract_comparison(sections: list[dict], target: int) -> tuple[str, list[dict]]:
    """The issue's SECOND section, items in publication order, until the
    running word count first reaches the house specimen's.

    Second, not first, and the reason is stated rather than chosen fresh
    each run: a TLDR-shaped issue leads on product news, alexandria
    publishes no product news, and comparing against that section would
    measure subject matter instead of prose. Sponsor items are skipped
    because they are advertising copy, not the newsletter's writing.
    """
    if len(sections) < 2:
        raise SystemExit("comparison issue has fewer than two sections")
    section = sections[1]
    if not section["items"]:
        raise SystemExit(f"comparison section {section['name']!r} retained no items")
    taken, total = [], 0
    for item in section["items"]:
        if "(sponsor)" in item["title"].lower():
            continue
        taken.append(item)
        total += words(item["title"]) + sum(words(b) for b in item["body"])
        if total >= target:
            break
    return section["name"], taken


# --------------------------------------------------------------- rendering


def render(heading: str, opening: str, items: list[str]) -> str:
    """Both specimens get the same container, so the container tells nothing."""
    out = []
    if opening:
        out += [opening, ""]
    out += [f"## {heading}", ""]
    out += items
    return "\n".join(out).strip() + "\n"


BOLD_LEAD = re.compile(r"^-\s+\*\*(.+?)\*\*\s*(.*)$", re.S)


def house_item_lines(item: list[str]) -> list[str]:
    """Title on its own line, then the body, matching the comparison's shape."""
    first = item[0].rstrip()
    lead = BOLD_LEAD.match(first)
    if lead:
        title, tail = lead.group(1).strip(), lead.group(2).strip()
    else:
        title, _, tail = first[2:].strip().partition(". ")
        title = title.rstrip(".") + "."
    lines = [title]
    if tail:
        lines.append(tail)
    for line in item[1:]:
        stripped = line.strip()
        # Sub-list items keep one level of indent; wrapped prose does not.
        lines.append("  " + stripped if stripped.startswith(("- ", "* ")) or
                     re.match(r"\d+\.\s", stripped) else stripped)
    return lines


def comparison_item_lines(items: list[dict]) -> list[str]:
    lines: list[str] = []
    for item in items:
        if lines:
            lines.append("")
        lines.append(item["title"])
        lines += item["body"]
    return lines


# ----------------------------------------------------------------- shuffle


def assignment(seed: int) -> dict[str, str]:
    """Which label each publication wears. Recomputed, never stored."""
    labels = ["A", "B"]
    random.Random(seed).shuffle(labels)
    return {"house": labels[0], "comparison": labels[1]}


# ------------------------------------------------------------------- sheet

CRITERIA = [
    ("clarity", "Clarity",
     "Could you say what this passage claims, in your own words, straight after reading it once?",
     "1 = I could not. 3 = I got the gist and would have to reread for the specifics. 5 = I could restate it."),
    ("human", "Written by a person",
     "Does this read as written by someone with a view, or as a form being filled in?",
     "1 = a template with the blanks filled. 3 = competent but anonymous. 5 = someone is clearly talking to me."),
    ("lands", "The point lands",
     "Did the point arrive without you going back over a sentence?",
     "1 = I reread more than once. 3 = I went back once. 5 = it landed first time."),
]


def scoring_sheet(specimens: list[str]) -> str:
    out = [
        "# Scoring sheet: two newsletter passages",
        "",
        "You are reading two passages from two AI newsletters, with the",
        "branding removed. We are not telling you which is which, and we",
        "would rather you did not guess. Read each one once, at the speed",
        "you would read your own email, then score it.",
        "",
        "Three questions per passage, each out of 5. There is no right",
        "answer and the one-line reason matters more to us than the number.",
        "",
        "Fill in the value after each colon and send the file back. Leave",
        "the field names alone, because a script reads them.",
        "",
        "```",
        "grader:",
        "",
    ]
    for label in specimens:
        out.append(f"# Passage {label}")
        for key, title, question, anchors in CRITERIA:
            out += [f"# {title}: {question}", f"# {anchors}",
                    f"{label}-{key}:", f"{label}-{key}-why:", ""]
    out += [
        "# Did either passage look familiar? An honest yes costs us nothing",
        "# and a quiet yes costs us the whole experiment. Letter, or 'no'.",
        "recognised:",
        "",
        "# One of these two passages is the one you would keep subscribing",
        "# to. Which letter, and in one line, why?",
        "preference:",
        "preference-why:",
        "```",
        "",
    ]
    return "\n".join(out)


SHEET_FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):[ \t]*(.*)$")


def parse_sheet(text: str) -> dict[str, str]:
    fields = {}
    for line in text.split("\n"):
        if line.startswith("#"):
            continue
        match = SHEET_FIELD.match(line.strip())
        if match and match.group(2).strip():
            fields[match.group(1)] = match.group(2).strip()
    return fields


# -------------------------------------------------------------- subcommands


def cmd_build(args: argparse.Namespace) -> int:
    issue_path = pathlib.Path(args.issue)
    source_path = pathlib.Path(args.comparison)
    out = pathlib.Path(args.out)

    opening, house_heading, house_item = extract_house(issue_path.read_text(encoding="utf-8"))
    house_lines = house_item_lines(house_item)
    house_raw = render(house_heading, opening, house_lines)
    target = words(house_raw)

    meta, sections = parse_comparison(source_path.read_text(encoding="utf-8"))
    comp_heading, comp_items = extract_comparison(sections, target)
    comp_raw = render(comp_heading, "", comparison_item_lines(comp_items))

    publishers = ["alexandria", meta.get("publisher", "")]
    publishers = [p for p in publishers if p]
    house = blind(house_raw, publishers) + "\n"
    comparison = blind(comp_raw, publishers) + "\n"

    where = assignment(args.seed)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"specimen-{where['house']}.md").write_text(house, encoding="utf-8")
    (out / f"specimen-{where['comparison']}.md").write_text(comparison, encoding="utf-8")
    (out / "scoring-sheet.md").write_text(scoring_sheet(sorted(where.values())), encoding="utf-8")

    print(f"seed {args.seed}")
    print(f"  specimen-{where['house']}.md       {words(house):>4} words   (house)")
    print(f"  specimen-{where['comparison']}.md       {words(comparison):>4} words   (comparison, "
          f"{len(comp_items)} items from {comp_heading!r})")
    print(f"  scoring-sheet.md")
    for label, text in ((where["house"], house), (where["comparison"], comparison)):
        leaked = [c for c in text if ord(c) > 127]
        if leaked:
            print(f"  WARNING specimen-{label} still carries non-ASCII: {set(leaked)}")
    return 0


def cmd_reveal(args: argparse.Namespace) -> int:
    where = assignment(args.seed)
    for role, label in where.items():
        print(f"specimen-{label} = {role}")
    return 0


def cmd_tally(args: argparse.Namespace) -> int:
    scores_dir = pathlib.Path(args.scores)
    sheets = sorted(scores_dir.glob("*.md")) if scores_dir.is_dir() else []
    if not sheets:
        print(f"no scoring sheets in {scores_dir}/. Nothing to tally yet.", file=sys.stderr)
        return 1

    where = assignment(args.seed)
    role_of = {label: role for role, label in where.items()}
    graders, per = [], {role: {key: [] for key, *_ in CRITERIA} for role in where}
    preference = {role: 0 for role in where}
    recognised = {role: 0 for role in where}

    for sheet in sheets:
        fields = parse_sheet(sheet.read_text(encoding="utf-8"))
        graders.append(fields.get("grader", sheet.stem))
        for label, role in role_of.items():
            for key, *_ in CRITERIA:
                raw = fields.get(f"{label}-{key}")
                if raw is None:
                    continue
                try:
                    value = float(raw)
                except ValueError:
                    print(f"{sheet.name}: {label}-{key} is not a number: {raw!r}", file=sys.stderr)
                    return 1
                if not 1 <= value <= 5:
                    print(f"{sheet.name}: {label}-{key} is outside 1-5: {value}", file=sys.stderr)
                    return 1
                per[role][key].append(value)
        choice = fields.get("preference", "").strip().upper()[:1]
        if choice in role_of:
            preference[role_of[choice]] += 1
        seen = fields.get("recognised", "").strip().upper()[:1]
        if seen in role_of:
            recognised[role_of[seen]] += 1

    def mean(values: list[float]) -> float | None:
        return round(sum(values) / len(values), 2) if values else None

    result = {
        "eval": "blind-prose-benchmark",
        "date": args.date,
        "seed": args.seed,
        "graders": graders,
        "method": f"see docs/evals/{args.date}-prose-benchmark.md",
        "scores": {role: {key: mean(v) for key, v in crit.items()} for role, crit in per.items()},
        "counts": {role: {key: len(v) for key, v in crit.items()} for role, crit in per.items()},
        "preference": preference,
        "recognised": recognised,
        "key": {f"specimen-{label}": role for label, role in role_of.items()},
    }
    output = json.dumps(result, indent=1) + "\n"
    if args.write:
        pathlib.Path(args.write).write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seed", type=int, default=20260921)
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build", help="write the grading packet")
    build.add_argument("--issue", default="site/content/issues/2026-W37.md")
    build.add_argument("--comparison",
                       default="docs/evals/2026-09-21-prose-benchmark/sources/comparison-2026-09-21.txt")
    build.add_argument("--out", default="docs/evals/2026-09-21-prose-benchmark/specimens")
    build.set_defaults(func=cmd_build)

    reveal = sub.add_parser("reveal", help="print the key")
    reveal.set_defaults(func=cmd_reveal)

    tally = sub.add_parser("tally", help="aggregate returned sheets")
    tally.add_argument("--scores", default="docs/evals/2026-09-21-prose-benchmark/scores")
    tally.add_argument("--date", default="2026-09-21")
    tally.add_argument("--write")
    tally.set_defaults(func=cmd_tally)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
