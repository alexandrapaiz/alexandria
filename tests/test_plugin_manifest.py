"""The install-line checker, tested against install lines known to be wrong.

Incident 32's rule, verbatim: every gate is tested against an artifact known
to fail it before the gate is trusted. So each test below builds a checkout on
disk that carries one specific defect, asserts the checker names it, and then
the last group points the checker at this repository and asserts it finds
nothing.

The defect class this exists for is already live elsewhere in the product.
`site/app/skills/page.jsx` tells visitors the library holds two skills while
nine sit on `main`, and no test fails, because a number in a sentence and a
number of directories were never connected to each other. A checker written
only against the manifests would have passed that page too.

    python3 -m pytest tests/test_plugin_manifest.py -q
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "check_plugin_manifest", REPO / "tools" / "check_plugin_manifest.py"
)
checker = importlib.util.module_from_spec(spec)
sys.modules["check_plugin_manifest"] = checker
spec.loader.exec_module(checker)

OPEN = checker.BLOCK_OPEN
CLOSE = checker.BLOCK_CLOSE

SKILLS = ("alpha-skill", "beta-skill")

INSTALL_BLOCK = f"""\
{OPEN}

```
/plugin marketplace add owner/repo
/plugin install demo-skills@demo
```

That installs two skills.

{CLOSE}
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    """A checkout shaped like this one, with a correct install line."""
    write(
        tmp_path / ".claude-plugin" / "plugin.json",
        json.dumps(
            {
                "name": "demo-skills",
                "version": "0.1.0",
                "description": "Two skills for a test.",
                "repository": "https://github.com/owner/repo",
            }
        ),
    )
    write(
        tmp_path / ".claude-plugin" / "marketplace.json",
        json.dumps(
            {
                "name": "demo",
                "owner": {"name": "An Owner"},
                "plugins": [
                    {
                        "name": "demo-skills",
                        "source": "./",
                        "description": "Two skills for a test.",
                    }
                ],
            }
        ),
    )
    for name in SKILLS:
        write(
            tmp_path / "skills" / name / "SKILL.md",
            f"---\nname: {name}\ndescription: Use when testing the checker.\n---\n\nBody.\n",
        )
    write(tmp_path / "README.md", INSTALL_BLOCK)
    write(tmp_path / "docs" / "product" / "install.md", INSTALL_BLOCK)
    return tmp_path


def problems(root) -> str:
    return "\n".join(checker.check(str(root))["problems"])


def edit_json(root, relative, mutate):
    path = root / relative
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data))


# ------------------------------- the clean fixture is actually clean


def test_the_fixture_passes_before_anything_is_broken(repo):
    report = checker.check(str(repo))
    assert report["ok"], report["problems"]
    assert report["skills"] == list(SKILLS)
    assert report["install"] == [
        "/plugin marketplace add owner/repo",
        "/plugin install demo-skills@demo",
    ]


# ------------------------------- the count, which is why this file exists


def test_a_count_in_the_block_that_does_not_match_what_ships(repo):
    write(repo / "skills" / "gamma-skill" / "SKILL.md",
          "---\nname: gamma-skill\ndescription: Use when counting.\n---\n\nBody.\n")
    found = problems(repo)
    assert "'two skills'" in found and "3 ship" in found
    assert "README.md" in found and "install.md" in found


def test_a_digit_counts_the_same_as_a_word(repo):
    readme = repo / "README.md"
    readme.write_text(readme.read_text().replace("two skills", "12 skills"))
    assert "'12 skills'" in problems(repo)


def test_a_count_outside_the_block_is_not_the_checkers_business(repo):
    """Both guarded files carry historical sentences with their own counts.

    README.md says "fails all six skills on main today" inside a 2026-09-29
    quotation, and `docs/product/skill-validation.md` says the library holds
    two. Those sentences are correct about the day they describe. A checker
    that read the whole file would force them to be edited or would be
    switched off, and a gate people switch off is the defect it was meant to
    catch.
    """
    readme = repo / "README.md"
    readme.write_text(
        "Back in April the library held four skills.\n\n" + readme.read_text()
    )
    assert checker.check(str(repo))["ok"], problems(repo)


def test_a_manifest_description_counts_too(repo):
    edit_json(repo, ".claude-plugin/plugin.json",
              lambda d: d.update(description="Nine skills for a test."))
    found = problems(repo)
    assert "'Nine skills'" in found and "2 ship" in found


# ------------------------------- the names a reader pastes


def test_a_renamed_marketplace_breaks_the_install_id(repo):
    edit_json(repo, ".claude-plugin/marketplace.json",
              lambda d: d.update(name="renamed"))
    found = problems(repo)
    assert "demo-skills@renamed" in found
    assert "the reader pastes the sentence" in found


def test_a_renamed_plugin_disagrees_with_the_entry_that_points_at_it(repo):
    """The prose stays silent here on purpose, and the manifests do not.

    `/plugin install <id>@<marketplace>` resolves the id through the
    marketplace entry, so a published line that matches the entry still reads
    as correct while the plugin it lands on calls itself something else. The
    checker reports the disagreement itself rather than guessing which of the
    two names the author meant, because either one could be the typo.
    """
    edit_json(repo, ".claude-plugin/plugin.json",
              lambda d: d.update(name="other-skills"))
    found = problems(repo)
    assert "installs nothing" in found
    assert "'demo-skills'" in found and "'other-skills'" in found


def test_a_moved_repository_breaks_the_marketplace_line(repo):
    edit_json(repo, ".claude-plugin/plugin.json",
              lambda d: d.update(repository="https://github.com/elsewhere/repo"))
    assert "marketplace add elsewhere/repo" in problems(repo)


def test_an_uppercase_plugin_name_is_not_installable(repo):
    edit_json(repo, ".claude-plugin/plugin.json",
              lambda d: d.update(name="Demo_Skills"))
    assert "is not an installable id" in problems(repo)


# ------------------------------- the manifests themselves


def test_a_missing_marketplace_manifest_is_named_as_uninstallable(repo):
    (repo / ".claude-plugin" / "marketplace.json").unlink()
    found = problems(repo)
    assert "marketplace.json is missing" in found
    assert "cannot be installed" in found


def test_invalid_json_is_reported_rather_than_raised(repo):
    (repo / ".claude-plugin" / "plugin.json").write_text("{ not json")
    assert "is not valid JSON" in problems(repo)


def test_an_empty_plugins_list_offers_nothing(repo):
    edit_json(repo, ".claude-plugin/marketplace.json", lambda d: d.update(plugins=[]))
    assert "lists no plugins" in problems(repo)


def test_an_anonymous_marketplace_is_a_problem(repo):
    edit_json(repo, ".claude-plugin/marketplace.json", lambda d: d.pop("owner"))
    assert "names no owner" in problems(repo)


def test_a_declared_component_path_that_does_not_exist(repo):
    """The one defect `claude plugin validate --strict` also catches.

    Measured 2026-10-18: a plugin manifest declaring `skills: ["./nope"]`
    still loads every skill from the conventional `skills/` location, so the
    runtime hides this and only the validator sees it. That is the reason the
    live manifest declares no paths at all.
    """
    edit_json(repo, ".claude-plugin/plugin.json", lambda d: d.update(skills=["./nope"]))
    assert "which does not exist" in problems(repo)


def test_a_source_that_points_at_no_plugin(repo):
    (repo / "elsewhere").mkdir()
    edit_json(repo, ".claude-plugin/marketplace.json",
              lambda d: d["plugins"][0].update(source="./elsewhere"))
    assert "resolves to no plugin" in problems(repo)


# ------------------------------- the skills, as the loader sees them


def test_a_skill_whose_name_is_not_its_directory(repo):
    path = repo / "skills" / "alpha-skill" / "SKILL.md"
    path.write_text(path.read_text().replace("name: alpha-skill", "name: alpha"))
    assert "unaddressable" in problems(repo)


def test_a_skill_with_no_description_never_fires(repo):
    path = repo / "skills" / "beta-skill" / "SKILL.md"
    path.write_text("---\nname: beta-skill\n---\n\nBody.\n")
    assert "has no description" in problems(repo)


def test_a_skill_in_the_wrong_place_ships_to_nobody(repo):
    write(repo / "gold" / "stray-skill" / "SKILL.md",
          "---\nname: stray-skill\ndescription: Use when stranded.\n---\n\nBody.\n")
    assert "ships to nobody" in problems(repo)


def test_a_vendored_skill_under_a_dot_directory_is_left_alone(repo):
    """The false positive the first run of this checker produced, pinned.

    Twenty vendored Clerk skills live under `.agents/skills/` in the real
    checkout. They are consumed by sessions in this repository and are not
    part of the product, and the checker reporting all twenty was noise that
    would have taught a reader to skip its output.
    """
    write(repo / ".agents" / "skills" / "vendored" / "SKILL.md",
          "---\nname: vendored\ndescription: Use when vendored.\n---\n\nBody.\n")
    assert checker.check(str(repo))["ok"], problems(repo)


def test_a_nested_directory_under_skills_is_not_a_skill(repo):
    """`skills/_validation/` holds the harness, not a skill, and has no SKILL.md.

    Its `evals/` and `reviews/` subdirectories are two levels down, so the
    stranded-skill walk has to accept a SKILL.md at exactly
    `skills/<name>/SKILL.md` and reject one deeper, rather than accepting
    anything under `skills/`.
    """
    write(repo / "skills" / "_validation" / "evals" / "SKILL.md",
          "---\nname: evals\ndescription: Use when nested too deep.\n---\n\nBody.\n")
    assert "ships to nobody" in problems(repo)


# ------------------------------- the prose has to be marked at all


def test_prose_with_no_marked_block_is_a_problem(repo):
    (repo / "README.md").write_text("No install line here at all.\n")
    found = problems(repo)
    assert "has no" in found and "install-line:start" in found


def test_a_missing_guarded_file_is_a_problem(repo):
    (repo / "docs" / "product" / "install.md").unlink()
    assert "nowhere to copy it from" in problems(repo)


# ------------------------------- and now the real repository


def test_this_repository_passes():
    report = checker.check(str(REPO))
    assert report["ok"], "\n".join(report["problems"])


def test_the_real_install_line_is_the_one_the_readme_publishes():
    report = checker.check(str(REPO))
    readme = (REPO / "README.md").read_text()
    block = readme.split(OPEN, 1)[1].split(CLOSE, 1)[0]
    for line in report["install"]:
        assert line in block, f"{line!r} is not in the README's install block"


def test_the_checker_exits_non_zero_on_a_broken_checkout(repo):
    """The exit code is the contract, because that is what a workflow reads."""
    edit_json(repo, ".claude-plugin/marketplace.json", lambda d: d.update(name="renamed"))
    assert checker.main(["--root", str(repo)]) == 1
    assert checker.main(["--root", str(REPO)]) == 0


@pytest.mark.skipif(
    shutil.which("claude") is None, reason="the claude CLI is not on this machine"
)
def test_the_cli_validates_the_manifests_strictly():
    """The half this checker deliberately does not reimplement.

    `claude plugin validate . --strict` walks the marketplace entry into the
    plugin manifest, so one command covers both files. It is skipped rather
    than required, because CI has no claude binary and a test that cannot run
    there is better honest about it than deleted.
    """
    result = subprocess.run(
        ["claude", "plugin", "validate", ".", "--strict", "--json"],
        cwd=str(REPO), capture_output=True, text=True, timeout=180,
    )
    report = json.loads(result.stdout)
    assert report["success"], report
    assert report["manifest"]["errors"] == []
    assert report["manifest"]["warnings"] == []


# ------------------------------- the reach, which is what the four was


def test_a_second_ecosystems_manifest_is_found_without_being_listed(repo):
    """The cursor case: a manifest nobody added to a constant.

    `.cursor-plugin/plugin.json` landed 2026-10-26 and said the library ships
    nine skills. This checker read the two paths written into it and reported
    a clean pass for three weeks, so the number it printed was its own reach.
    """
    write(
        repo / ".cursor-plugin" / "plugin.json",
        json.dumps({"name": "demo-skills", "description": "Nine skills for a test."}),
    )
    found = problems(repo)
    assert ".cursor-plugin/plugin.json" in found
    assert "'Nine skills'" in found and "2 ship" in found


def test_a_discovered_manifest_is_in_the_report_even_when_it_is_clean(repo):
    write(
        repo / ".cursor-plugin" / "plugin.json",
        json.dumps({"name": "demo-skills", "description": "Two skills for a test."}),
    )
    report = checker.check(str(repo))
    assert report["ok"], report["problems"]
    assert ".cursor-plugin/plugin.json" in report["manifests"]
    assert ".cursor-plugin/plugin.json" in report["surfaces"]["manifest descriptions"]


def test_a_description_nested_inside_a_manifest_is_read_at_any_depth(repo):
    edit_json(
        repo,
        ".claude-plugin/marketplace.json",
        lambda d: d["metadata"].update(description="Seven skills for a test.")
        if d.get("metadata") else d.update(metadata={"description": "Seven skills for a test."}),
    )
    assert "'Seven skills'" in problems(repo)


def test_a_manifest_that_is_not_json_is_named_rather_than_crashing(repo):
    write(repo / ".cursor-plugin" / "plugin.json", "{not json")
    assert "is not valid JSON" in problems(repo)


# ------------------------------- the census gate


def test_a_count_surface_nobody_classified_is_the_finding(repo):
    """The gate that turns the checker's reach into something a reader sees.

    A file under the census roots that names a count and carries no
    disposition is red on the day it lands, rather than being the seventh
    unread surface in a tree somebody already called clean.
    """
    write(
        repo / "site" / "app" / "pricing" / "page.jsx",
        "export default function Page() {\n  return <p>Nine skills, one price.</p>;\n}\n",
    )
    found = problems(repo)
    assert "site/app/pricing/page.jsx" in found
    assert "not classified in COUNT_SURFACES" in found


def test_a_classified_live_surface_with_a_stale_count_fails(repo):
    """`/llms.txt` had this exact shape, and it is served to the public."""
    write(
        repo / "site" / "app" / "llms.txt" / "route.js",
        "export const body = `\nThat installs nine skills, and none of them loads.\n`;\n",
    )
    found = problems(repo)
    assert "site/app/llms.txt/route.js:2" in found
    assert "'nine skills'" in found


def test_the_other_phrasing_of_the_noun_counts_too(repo):
    """`/llms.txt` used both phrasings four lines apart."""
    write(
        repo / "site" / "app" / "llms.txt" / "route.js",
        "export const body = `\nThe nine skill files are in the repository.\n`;\n",
    )
    assert "'nine skill files'" in problems(repo)


def test_a_file_classified_internal_is_not_checked(repo):
    """A comment to the next engineer is not prose a reader meets.

    It is still named in COUNT_SURFACES, because a reach that is written
    down can be argued with and an implicit one cannot.
    """
    write(
        repo / "site" / "lib" / "path.js",
        "// a catalogue of nine skills has a short answer\nexport const n = 1;\n",
    )
    assert checker.check(str(repo))["ok"], problems(repo)
    assert "site/lib/path.js" in checker.check(str(repo))["surfaces"]["classified"]


# ------------------------------- dates, which make a stale count correct


def test_a_count_with_a_date_in_its_own_sentence_is_a_record(repo):
    write(
        repo / "site" / "app" / "llms.txt" / "route.js",
        "// Nine skills as of 2026-10-26, when this was measured.\n",
    )
    assert checker.check(str(repo))["ok"], problems(repo)


def test_a_date_in_the_paragraphs_opening_sentence_covers_the_passage(repo):
    """A writer dates a passage once, at its head, and means all of it."""
    write(
        repo / "site" / "app" / "llms.txt" / "route.js",
        "// All eight completed the retrofit on 2026-09-30.\n"
        "// Seven of the eight skills have no section validated by anything.\n",
    )
    assert checker.check(str(repo))["ok"], problems(repo)


def test_a_date_further_down_the_paragraph_does_not_cover_a_claim_about_today(repo):
    """The loophole a paragraph-wide rule would have opened.

    `docs/product/install.md` carried this shape: a paragraph whose last
    sentence says "as of 2026-10-18" around a middle sentence saying "two
    skills today". "Today" is the one word that cannot be a record.
    """
    write(
        repo / "site" / "app" / "llms.txt" / "route.js",
        "// ADR-36 defines two of those grades.\n"
        "// The third is carried by nine skills today and nothing defines it.\n"
        "// It is filed in docs/ideas.md as of 2026-10-18.\n",
    )
    assert "'nine skills'" in problems(repo)


def test_a_subset_that_names_its_denominator_passes(repo):
    """And it is the better sentence, which is why there is no new rule."""
    write(
        repo / "site" / "app" / "llms.txt" / "route.js",
        "// The grade is carried by one of the two skills today.\n",
    )
    assert checker.check(str(repo))["ok"], problems(repo)


def test_a_markdown_section_number_is_not_a_count(repo):
    """The census's one false positive on its first run over this repository.

    `### 2.3 Skills compose; nothing today says how` otherwise reads as
    "3 skills", so the gate's first act would have been to cry wolf on a
    heading.
    """
    install = repo / "docs" / "product" / "install.md"
    install.write_text("### 2.3 Skills compose; nothing says how\n\n" + install.read_text())
    assert checker.check(str(repo))["ok"], problems(repo)


# ------------------------------- the denominator, printed and not asserted


def test_the_report_names_the_surfaces_it_read(repo):
    report = checker.check(str(repo))
    assert report["surfaces"]["unclassified"] == []
    assert report["surfaces"]["classified"]["docs/product/install.md"] == "live"
    assert report["surfaces"]["classified"]["README.md"] == "block"
    assert ".claude-plugin/plugin.json" in report["surfaces"]["manifest descriptions"]


def test_this_repository_has_no_unclassified_count_surface():
    """The real tree, which is the one the four was measured over."""
    report = checker.check(str(REPO))
    assert report["surfaces"]["unclassified"] == [], report["problems"]
    assert ".cursor-plugin/plugin.json" in report["manifests"]


def test_one_wrong_count_in_a_guarded_live_file_is_one_problem(repo):
    """`docs/product/install.md` is both guarded and `live`, and its block is
    inside its text, so the two readers would otherwise report it twice."""
    write(repo / "skills" / "gamma-skill" / "SKILL.md",
          "---\nname: gamma-skill\ndescription: Use when counting.\n---\n\nBody.\n")
    found = [p for p in checker.check(str(repo))["problems"] if "install.md" in p]
    assert len(found) == 1, found


def test_every_guarded_prose_file_carries_a_disposition(repo):
    """An invariant rather than an artifact: a file the install line is
    published in, with no classification, is the gap this census closes."""
    for relative in checker.GUARDED_PROSE:
        assert relative in checker.COUNT_SURFACES, relative


def test_no_disposition_names_a_file_this_repository_does_not_have():
    """The rot in the other direction from the census gate.

    A `COUNT_SURFACES` entry for a deleted file is a judgment about nothing,
    and it reads as coverage. Required empty against the real tree only,
    because a fixture holds a deliberate subset.
    """
    assert checker.check(str(REPO))["surfaces"]["missing"] == []
