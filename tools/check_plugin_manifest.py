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

# The prose the install line lives in. Each file carries the block markers
# below; nothing outside a marked block is read, because both of these files
# also carry historical sentences with their own, correctly stale, counts.
GUARDED_PROSE = ("README.md", os.path.join("docs", "product", "install.md"))

BLOCK_OPEN = "<!-- install-line:start -->"
BLOCK_CLOSE = "<!-- install-line:end -->"

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")

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

COUNT_PHRASE = re.compile(
    r"\b(" + "|".join(list(NUMBER_WORDS) + [r"\d+"]) + r")\s+skills\b",
    re.IGNORECASE,
)


def _as_number(word: str) -> int:
    return int(word) if word.isdigit() else NUMBER_WORDS[word.lower()]


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
        for match in COUNT_PHRASE.finditer(block):
            claimed = _as_number(match.group(1))
            if claimed != count:
                problems.append(
                    f"{relative}'s install block says {match.group(0)!r} and "
                    f"{count} ship from skills/. A reader counts what arrives."
                )
    return blocks


def check_manifest_counts(root: str, plugin, market, count: int, problems: list) -> None:
    """A description is prose too, and it is the first prose a reader meets."""
    descriptions = []
    if plugin:
        descriptions.append((PLUGIN_MANIFEST, plugin.get("description", "")))
    if market:
        descriptions.append((MARKETPLACE_MANIFEST, (market.get("metadata") or {}).get("description", "")))
        for index, entry in enumerate(market.get("plugins") or []):
            descriptions.append(
                (f"{MARKETPLACE_MANIFEST} plugins[{index}]", entry.get("description", ""))
            )
    for where, description in descriptions:
        for match in COUNT_PHRASE.finditer(description or ""):
            if _as_number(match.group(1)) != count:
                problems.append(
                    f"{where} description says {match.group(0)!r} and {count} "
                    "ship from skills/. The marketplace listing is what a "
                    "reader reads before installing."
                )


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
    check_manifest_counts(root, plugin, market, len(skills), problems)

    return {
        "ok": not problems,
        "problems": problems,
        "skills": skills,
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
