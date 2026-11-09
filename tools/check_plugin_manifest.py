#!/usr/bin/env python3
"""Does the install line a stranger pastes still describe this repository?

The library is distributed as a Claude Code plugin, served from a marketplace
manifest in this same repository. Two commands are the whole product surface
for a new reader:

    /plugin marketplace add alexandrapaiz/alexandria
    /plugin install alexandria-skills@alexandria

Both of those strings are facts about files on disk. The marketplace name
comes from `.claude-plugin/marketplace.json`, the plugin name comes from the
entry inside it, the repository slug comes from the plugin manifest's own
`repository` field, and the nine skills come from the directories under
`skills/`. Every one of those can change without the sentence that advertises
it changing with it, and a wrong install line is worse than no install line,
because the reader blames the product rather than the sentence.

`claude plugin validate . --strict` already checks the JSON: required fields,
unknown fields, component paths that do not resolve. It does not and cannot
check the prose. So this checker does the half the CLI leaves open, and it
deliberately does not reimplement the half the CLI already owns.

The count is the check that earns this file. `site/app/skills/page.jsx` has
been telling visitors the library holds two skills while nine sit on `main`,
and nothing failed, because no gate connects a number in a sentence to a
number of directories. Here the prose lives inside a marked block and every
count inside that block has to equal what ships.

    python3 tools/check_plugin_manifest.py
    python3 tools/check_plugin_manifest.py --json
    python3 tools/check_plugin_manifest.py --root /path/to/a/checkout
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLUGIN_MANIFEST = os.path.join(".claude-plugin", "plugin.json")
MARKETPLACE_MANIFEST = os.path.join(".claude-plugin", "marketplace.json")
SKILLS_DIR = "skills"

# Distribution manifests are discovered rather than listed, by the directory
# convention every plugin ecosystem uses: `<ecosystem>-plugin/`. The two names
# above stay, because the advertised install line is built out of that pair and
# out of no other, but a second ecosystem's manifest carries its own
# description, and a description is a count surface.
#
# This is the half the hand list cost. `.cursor-plugin/plugin.json` said the
# library ships nine skills while ten shipped, and this checker reported a
# clean pass over it, because the only manifests it could see were the two
# written into these constants. The skill seat put the defect in one sentence
# on 2026-11-09: what decided the number was the instrument's reach rather
# than the library's drift.
MANIFEST_DIR_SUFFIX = "-plugin"

# The prose the install line lives in. Each file carries the block markers
# below; nothing outside a marked block is read, because both of these files
# also carry historical sentences with their own, correctly stale, counts.
GUARDED_PROSE = ("README.md", os.path.join("docs", "product", "install.md"))

BLOCK_OPEN = "<!-- install-line:start -->"
BLOCK_CLOSE = "<!-- install-line:end -->"

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# Where a skill count can be read by somebody who is deciding whether to
# install, and how each file's counts are judged.
#
#   "live"      every undated count in the file describes today
#   "block"     only the install-line block is live, because the rest of the
#               file quotes rulings that are correct about the day they quote
#   "internal"  a comment to the next engineer rather than prose a reader
#               meets. Not checked, and named here anyway, because a reach
#               that is written down can be argued with and an implicit one
#               cannot.
#
# Every manifest found by `discovered_manifests` is "live" without being
# listed here: a manifest description has no room for a historical sentence.
COUNT_SURFACES = {
    "README.md": "block",
    os.path.join("docs", "product", "install.md"): "live",
    os.path.join(SKILLS_DIR, "README.md"): "live",
    os.path.join("site", "app", "llms.txt", "route.js"): "live",
    os.path.join("site", "lib", "skill-shelves.js"): "internal",
    os.path.join("site", "lib", "path.js"): "internal",
}

# The tree the census walks. Anything here that names a skill count and is
# absent from COUNT_SURFACES is the finding, because that is the shape the
# cursor manifest and `/llms.txt` both had: a live count nobody had classified.
#
# `docs/product/` is deliberately only its install page. The other files there
# are internal product notes whose counts are quotations of dated rulings, and
# deciding which of those describe today is a judgment per sentence rather than
# per file. Widening the census to them is a separate piece of work and it is
# filed in the ledger rather than guessed at here.
COUNT_ROOTS = (
    "README.md",
    os.path.join("docs", "product", "install.md"),
    os.path.join(SKILLS_DIR, "README.md"),
    os.path.join("site", "app"),
    os.path.join("site", "lib"),
)

COUNT_SUFFIXES = (".md", ".js", ".jsx", ".ts", ".tsx")

# A count with a date beside it is a measurement rather than a claim about
# today, so it is right when it is stale and editing it would be a lie. This
# is the exemption the marker block used to buy, moved from the file to the
# passage: `skills/README.md` says "Ten skills as of 2026-11-09" and needs no
# markers to be read correctly.
#
# Two scopes count as "beside it", and the second is narrow on purpose. The
# count's own sentence, and the sentence that OPENS its paragraph, because a
# writer dates a passage once at its head: "All eight completed the ADR-38
# retrofit on 2026-09-30, so every skill now carries ... seven of the eight
# skills have no section validated" is one dated reading and the second
# sentence inherits the date from the first.
#
# A count of a SUBSET needs no new rule, and the rule it already has is the
# better sentence. `docs/product/install.md` said a grade was "carried by two
# skills today", which the census reads as a claim about the library and
# cannot tell from one about a grade. Written with its denominator, "nine of
# the ten skills today", the phrase the census matches is "ten skills" and it
# passes, and the reader is told the share rather than left to work it out.
#
# What is deliberately not exempt is a date further down the same paragraph.
# `docs/product/install.md` had exactly that shape when this gate was
# written: a paragraph whose last sentence says "filed as of 2026-10-18" and
# whose middle sentence said "carried by two skills today". A paragraph-wide
# rule would have exempted a sentence that says "today", which is the one
# word that cannot be a record.
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")

# Component keys a plugin manifest may point at. A path here that does not
# resolve is a load failure at install time, which is the one class of defect
# this checker shares with `claude plugin validate --strict`: it is cheap to
# repeat and it is the difference between nine skills and none.
COMPONENT_KEYS = ("skills", "agents", "commands", "hooks")

NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

# The lookbehind is the one false positive the census found on its first run
# and it is worth excluding by hand rather than by a disposition: a markdown
# section number. `### 2.3 Skills compose` otherwise reads as "3 skills", so
# the gate's first act would have been to cry wolf on a heading.
#
# The noun is two phrasings rather than one because `/llms.txt` used both in
# four lines, "the nine skill files are in the public repository" and "that
# installs nine skills", and a census that read one of them would have found
# half of one surface. What is still outside the reach, and is written down
# here rather than left to be rediscovered, is a count with the noun elided:
# that route's "the repository carries a Cursor plugin manifest for the same
# nine" is a live stale count no pattern short of a parser can see.
COUNT_PHRASE = re.compile(
    r"(?<![.\d])\b(" + "|".join(list(NUMBER_WORDS) + [r"\d+"])
    + r")\s+(?:skills|skill\s+files)\b",
    re.IGNORECASE,
)


def _as_number(word: str) -> int:
    return int(word) if word.isdigit() else NUMBER_WORDS[word.lower()]


def discovered_manifests(root: str) -> list:
    """Every distribution manifest in the checkout, by directory convention.

    A plugin ecosystem puts its manifest in `<ecosystem>-plugin/`, so the
    directories are enumerable and the next ecosystem is covered on the day
    its manifest lands rather than on the day somebody remembers this file.
    """
    found = []
    for entry in sorted(os.listdir(root)):
        if not entry.endswith(MANIFEST_DIR_SUFFIX):
            continue
        directory = os.path.join(root, entry)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if name.endswith(".json"):
                found.append(os.path.join(entry, name))
    return found


def manifest_descriptions(data, where: str) -> list:
    """Every `description` in a manifest, at whatever depth it sits.

    Walked rather than addressed by key path, because the three manifests this
    repository ships put their descriptions in three different places: a
    plugin manifest at the top level, a marketplace manifest under `metadata`
    and again inside each entry of `plugins`, and the cursor manifest at the
    top level beside a `displayName` the others do not have. A walk needs no
    update when a fourth shape arrives.
    """
    found = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "description" and isinstance(value, str):
                found.append((where, value))
            else:
                found.extend(manifest_descriptions(value, f"{where} {key}"))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            found.extend(manifest_descriptions(value, f"{where}[{index}]"))
    return found


def _sentence_end(text: str, after: int) -> int:
    right = len(text)
    for mark in (". ", ".\n"):
        found = text.find(mark, after)
        if found != -1:
            right = min(right, found + 1)
    return right


def sentence_around(text: str, start: int, end: int) -> str:
    """The sentence a match sits in, so a date beside it can be seen.

    Prose here is hard-wrapped, so a sentence is not a line and the line a
    count lands on routinely carries neither end of it.
    """
    left = max(
        text.rfind(". ", 0, start),
        text.rfind(".\n", 0, start),
        text.rfind("\n\n", 0, start),
        -1,
    ) + 1
    return text[left:_sentence_end(text, end)]


def opening_sentence(text: str, start: int) -> str:
    """The first sentence of the paragraph a match sits in.

    This is what makes a dated passage readable as one reading rather than as
    a dated first line followed by undated claims.
    """
    paragraph = text.rfind("\n\n", 0, start) + 2
    return text[paragraph:_sentence_end(text, paragraph)]


def is_dated(text: str, start: int, end: int) -> bool:
    """Is this count a record of a measurement rather than a claim about today?"""
    return bool(
        DATE.search(sentence_around(text, start, end))
        or DATE.search(opening_sentence(text, start))
    )


def read_json(root: str, relative: str, problems: list) -> dict | None:
    path = os.path.join(root, relative)
    if not os.path.exists(path):
        problems.append(
            f"{relative} is missing. Without it `/plugin marketplace add` "
            "fails on this repository and the library cannot be installed."
        )
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        problems.append(f"{relative} is not valid JSON: {error}")
        return None


def frontmatter(text: str) -> dict:
    """The top-level scalar keys of a SKILL.md front matter block.

    Deliberately not a YAML parser. Only `name` and `description` matter here
    and both are single-line scalars in every skill in this library; a nested
    `provenance` block is skipped by the indentation test rather than parsed.
    There is no pyyaml in requirements-dev.txt and a checker is a poor reason
    to add one.
    """
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line[:1].isspace() or line.startswith("-"):
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"\'')
    return fields


def discovered_skills(root: str, problems: list) -> list:
    """The skills a stranger's install actually loads, by the same convention.

    Claude Code finds a plugin's skills at `<plugin root>/skills/*/SKILL.md`.
    The manifest may also declare paths explicitly, and this repository does
    not: a declared `./skills` is additive rather than authoritative (measured
    2026-10-18, a manifest naming a path that does not exist still loaded all
    nine from the conventional location), so the declaration buys nothing and
    can rot. Convention is the single source of truth, and that is exactly why
    it needs a test.
    """
    directory = os.path.join(root, SKILLS_DIR)
    if not os.path.isdir(directory):
        problems.append(f"{SKILLS_DIR}/ does not exist, so the plugin ships no skills.")
        return []

    names = []
    for entry in sorted(os.listdir(directory)):
        skill_file = os.path.join(directory, entry, "SKILL.md")
        if not os.path.isfile(skill_file):
            continue
        with open(skill_file, encoding="utf-8") as handle:
            fields = frontmatter(handle.read())
        if fields.get("name") != entry:
            problems.append(
                f"{SKILLS_DIR}/{entry}/SKILL.md declares name "
                f"{fields.get('name')!r}, which is not its directory name "
                f"{entry!r}. The loader addresses a skill by its declared "
                "name, so the two disagreeing makes it unaddressable."
            )
        if not fields.get("description"):
            problems.append(
                f"{SKILLS_DIR}/{entry}/SKILL.md has no description. A skill "
                "with no description never fires, because the description is "
                "the only thing the model sees before it loads the body."
            )
        names.append(entry)
    return names


def stranded_skills(root: str) -> list:
    """SKILL.md files outside the discovery root, which ship nothing.

    Dot directories are skipped rather than reported. `.agents/skills/` holds
    twenty vendored Clerk skills that this repository consumes in its own
    sessions and does not sell, and they are correctly invisible to the
    plugin: the first run of this checker reported all twenty, which is how a
    gate that cries wolf teaches people to ignore it. The convention being
    relied on is that a dot directory is tooling for the checkout rather than
    product in it, and `.claude/agents/` is in the same position.
    """
    stranded = []
    for current, directories, files in os.walk(root):
        directories[:] = [
            name for name in directories
            if not name.startswith(".")
            and name not in {"node_modules", "__pycache__"}
        ]
        if "SKILL.md" not in files:
            continue
        relative = os.path.relpath(current, root)
        parts = relative.split(os.sep)
        if len(parts) == 2 and parts[0] == SKILLS_DIR:
            continue
        stranded.append(os.path.join(relative, "SKILL.md"))
    return sorted(stranded)


def repo_slug(plugin: dict, problems: list) -> str | None:
    url = (plugin or {}).get("repository", "")
    match = re.search(r"github\.com[/:]([^/]+/[^/.]+)", url)
    if not match:
        problems.append(
            f"{PLUGIN_MANIFEST} has no GitHub `repository` url, so the "
            "`/plugin marketplace add <owner>/<repo>` line has nothing to be "
            "checked against."
        )
        return None
    return match.group(1)


def check_plugin(root: str, problems: list) -> dict | None:
    plugin = read_json(root, PLUGIN_MANIFEST, problems)
    if plugin is None:
        return None
    for field in ("name", "version", "description"):
        if not plugin.get(field):
            problems.append(f"{PLUGIN_MANIFEST} has no {field}.")
    name = plugin.get("name", "")
    if name and not NAME_PATTERN.match(name):
        problems.append(
            f"{PLUGIN_MANIFEST} name {name!r} is not an installable id: "
            "lowercase letters, digits and hyphens only."
        )
    for key in COMPONENT_KEYS:
        declared = plugin.get(key)
        if isinstance(declared, str):
            declared = [declared]
        for relative in declared or []:
            if not os.path.exists(os.path.join(root, relative)):
                problems.append(
                    f"{PLUGIN_MANIFEST} declares {key} path {relative!r}, "
                    "which does not exist. The runtime loader reports this as "
                    "a load failure."
                )
    return plugin


def check_marketplace(root: str, plugin: dict | None, problems: list) -> tuple:
    market = read_json(root, MARKETPLACE_MANIFEST, problems)
    if market is None:
        return None, None
    if not market.get("name"):
        problems.append(f"{MARKETPLACE_MANIFEST} has no name.")
    elif not NAME_PATTERN.match(market["name"]):
        problems.append(
            f"{MARKETPLACE_MANIFEST} name {market['name']!r} is not an "
            "installable id: lowercase letters, digits and hyphens only."
        )
    owner = market.get("owner") or {}
    if not (owner.get("name") if isinstance(owner, dict) else owner):
        problems.append(
            f"{MARKETPLACE_MANIFEST} names no owner. Trust in a plugin "
            "marketplace derives from its source, so an anonymous one asks a "
            "reader to install from nobody."
        )

    entries = market.get("plugins") or []
    if not entries:
        problems.append(
            f"{MARKETPLACE_MANIFEST} lists no plugins, so "
            "`/plugin marketplace add` succeeds and offers nothing."
        )
        return market, None

    entry = entries[0]
    for index, candidate in enumerate(entries):
        if not candidate.get("name"):
            problems.append(f"{MARKETPLACE_MANIFEST} plugins[{index}] has no name.")
        if not candidate.get("source"):
            problems.append(f"{MARKETPLACE_MANIFEST} plugins[{index}] has no source.")
            continue
        source = candidate["source"]
        if not isinstance(source, str) or "://" in source:
            continue
        target = os.path.normpath(os.path.join(root, source))
        if not os.path.isdir(target):
            problems.append(
                f"{MARKETPLACE_MANIFEST} plugins[{index}] source {source!r} "
                "is not a directory in this repository."
            )
            continue
        inner = os.path.join(target, PLUGIN_MANIFEST)
        if not os.path.isfile(inner):
            problems.append(
                f"{MARKETPLACE_MANIFEST} plugins[{index}] source {source!r} "
                f"holds no {PLUGIN_MANIFEST}, so the entry resolves to no plugin."
            )
            continue
        if os.path.samefile(target, root) and plugin is not None:
            if candidate.get("name") != plugin.get("name"):
                problems.append(
                    f"{MARKETPLACE_MANIFEST} plugins[{index}] is named "
                    f"{candidate.get('name')!r} and the plugin it points at is "
                    f"named {plugin.get('name')!r}. The install id is "
                    "`<plugin>@<marketplace>`, so the two disagreeing means "
                    "the advertised line installs nothing."
                )
    return market, entry


def check_prose(root: str, lines: dict, count: int, problems: list) -> dict:
    """Every guarded block carries the live install lines and the live count."""
    blocks = {}
    for relative in GUARDED_PROSE:
        path = os.path.join(root, relative)
        if not os.path.exists(path):
            problems.append(
                f"{relative} is missing, and it is where the install line is "
                "published. A reader has nowhere to copy it from."
            )
            continue
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        if BLOCK_OPEN not in text or BLOCK_CLOSE not in text:
            problems.append(
                f"{relative} has no {BLOCK_OPEN} / {BLOCK_CLOSE} block, so "
                "nothing in it is checked against the manifests. Mark the "
                "install block or move it to a file that does."
            )
            continue
        block = text.split(BLOCK_OPEN, 1)[1].split(BLOCK_CLOSE, 1)[0]
        blocks[relative] = block
        for label, expected in lines.items():
            if expected and expected not in block:
                problems.append(
                    f"{relative}'s install block does not contain the {label} "
                    f"the manifests describe: {expected!r}. The sentence and "
                    "the manifest have drifted, and the reader pastes the "
                    "sentence."
                )
        # The counts inside the block, but only for a file whose disposition
        # is "block". A "live" file's whole text is read by the census, and
        # its block is part of that text, so checking here too would report
        # one wrong number as two problems.
        if COUNT_SURFACES.get(relative) != "live":
            for match in COUNT_PHRASE.finditer(block):
                claimed = _as_number(match.group(1))
                if claimed != count:
                    problems.append(
                        f"{relative}'s install block says {match.group(0)!r} "
                        f"and {count} ship from skills/. A reader counts what "
                        "arrives."
                    )
    return blocks


def check_manifest_counts(root: str, count: int, problems: list) -> list:
    """A description is prose too, and it is the first prose a reader meets.

    Returns the surfaces it read, because the number of surfaces is the thing
    this check used to get wrong. It reported four problems over four
    manifests it had been told about, and a reader could not tell that from
    four problems over every manifest that ships.
    """
    surfaces = []
    for relative in discovered_manifests(root):
        path = os.path.join(root, relative)
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as error:
            problems.append(f"{relative} is not valid JSON: {error}")
            continue
        for where, description in manifest_descriptions(data, relative):
            surfaces.append(where)
            for match in COUNT_PHRASE.finditer(description):
                if _as_number(match.group(1)) != count:
                    problems.append(
                        f"{where} says {match.group(0)!r} and {count} ship "
                        "from skills/. The listing a reader reads before "
                        "installing is the one place the number has to hold."
                    )
    return surfaces


def census(root: str) -> list:
    """Every file under COUNT_ROOTS that names a skill count, with its counts.

    Derived, so a surface that appears tomorrow is in the census tomorrow.
    This is the half that turns the checker's own reach into something a
    reader can see and argue with. The gate over it is `check_count_census`
    below, which fails on a surface carrying no disposition.
    """
    paths = []
    for relative in COUNT_ROOTS:
        target = os.path.join(root, relative)
        if os.path.isfile(target):
            paths.append(relative)
            continue
        for current, directories, files in os.walk(target):
            directories[:] = [
                name for name in directories
                if not name.startswith(".")
                and name not in {"node_modules", "__pycache__"}
            ]
            for name in sorted(files):
                if name.endswith(COUNT_SUFFIXES):
                    paths.append(
                        os.path.relpath(os.path.join(current, name), root)
                    )

    found = []
    for relative in sorted(set(paths)):
        try:
            with open(os.path.join(root, relative), encoding="utf-8") as handle:
                text = handle.read()
        except (OSError, UnicodeDecodeError):
            continue
        counts = []
        for match in COUNT_PHRASE.finditer(text):
            counts.append(
                {
                    # Collapsed, because this prose is hard-wrapped and a
                    # count phrase lands across the break often enough that
                    # a raw match prints as 'nine\nskills' and a reader
                    # cannot grep for what the gate just told them.
                    "phrase": " ".join(match.group(0).split()),
                    "claimed": _as_number(match.group(1)),
                    "dated": is_dated(text, match.start(), match.end()),
                    "line": text.count("\n", 0, match.start()) + 1,
                }
            )
        if counts:
            found.append({"file": relative, "counts": counts})
    return found


def check_count_census(root: str, count: int, problems: list) -> dict:
    """The gate: a count surface nobody has classified is the finding.

    `INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`
    is this class one level up, and the remedy there was the same: enumerate
    the population, declare a judgment per member, and fail on the member
    nobody has judged. A checker that only reads the files it was handed
    cannot tell a clean library from an unread one.
    """
    surveyed = census(root)
    for entry in surveyed:
        relative = entry["file"]
        disposition = COUNT_SURFACES.get(relative)
        if disposition is None:
            phrases = ", ".join(sorted({c["phrase"] for c in entry["counts"]}))
            problems.append(
                f"{relative} names a skill count ({phrases}) and is not "
                "classified in COUNT_SURFACES, so nothing checks whether it "
                "describes today. Classify it live, block or internal; an "
                "unclassified surface is how a stale count survives a pass."
            )
            continue
        # "internal" is not read, and "block" is read by `check_prose`, which
        # owns the marker block and the install lines inside it as well.
        if disposition != "live":
            continue
        for item in entry["counts"]:
            if item["dated"] or item["claimed"] == count:
                continue
            problems.append(
                f"{relative}:{item['line']} says {item['phrase']!r} and "
                f"{count} ship from skills/. Give the sentence a date if it "
                "is a record of a measurement, or the live number if it is a "
                "claim about today."
            )
    return {entry["file"]: entry for entry in surveyed}


def check(root: str = REPO) -> dict:
    problems: list = []

    plugin = check_plugin(root, problems)
    market, entry = check_marketplace(root, plugin, problems)
    skills = discovered_skills(root, problems)

    for path in stranded_skills(root):
        problems.append(
            f"{path} is a skill outside {SKILLS_DIR}/<name>/SKILL.md, so the "
            "plugin loader never finds it. It ships to nobody and fails "
            "nothing."
        )

    slug = repo_slug(plugin, problems) if plugin else None
    marketplace_name = (market or {}).get("name")
    plugin_name = (entry or {}).get("name") or (plugin or {}).get("name")

    lines = {
        "marketplace line": f"marketplace add {slug}" if slug else None,
        "install id": (
            f"{plugin_name}@{marketplace_name}"
            if plugin_name and marketplace_name else None
        ),
    }
    blocks = check_prose(root, lines, len(skills), problems)
    manifest_surfaces = check_manifest_counts(root, len(skills), problems)
    surveyed = check_count_census(root, len(skills), problems)

    return {
        "ok": not problems,
        "problems": problems,
        "skills": skills,
        "manifests": discovered_manifests(root),
        # The denominator, printed and never asserted, the way
        # `tools/target_census.py` prints its own: a count of surfaces that is
        # asserted trains the next reader to raise the number rather than to
        # classify the surface.
        "surfaces": {
            "manifest descriptions": sorted(manifest_surfaces),
            "classified": {
                relative: COUNT_SURFACES[relative]
                for relative in sorted(surveyed)
                if relative in COUNT_SURFACES
            },
            "unclassified": sorted(
                relative for relative in surveyed
                if relative not in COUNT_SURFACES
            ),
            # The rot in the other direction: a disposition for a file that is
            # no longer there. Reported rather than failed, because `--root`
            # is routinely pointed at a checkout that holds a subset of these
            # on purpose, and a test over the real tree is the right place to
            # require it empty.
            "missing": sorted(
                relative for relative in COUNT_SURFACES
                if not os.path.exists(os.path.join(root, relative))
            ),
        },
        "marketplace": marketplace_name,
        "plugin": plugin_name,
        "repository": slug,
        "install": [
            f"/plugin marketplace add {slug}" if slug else None,
            f"/plugin install {plugin_name}@{marketplace_name}"
            if plugin_name and marketplace_name else None,
        ],
        "guarded": sorted(blocks),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=REPO, help="the checkout to read")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args(argv)

    report = check(args.root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"marketplace: {report['marketplace']}  plugin: {report['plugin']}")
        print(f"skills ({len(report['skills'])}): {', '.join(report['skills'])}")
        for line in report["install"]:
            if line:
                print(f"  {line}")
        if report["problems"]:
            print(f"\n{len(report['problems'])} problem(s):")
            for problem in report["problems"]:
                print(f"  - {problem}")
        else:
            print("\nThe install line and the manifests agree.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
