"""Does the incident register's inbox actually remove the collision?

The claim `tools/incidents.py` makes is narrow and worth testing exactly: two
seats filing an incident between merges touch different files, so there is
nothing to resolve. The tests that matter are therefore the ones that fail when
the tool would let a collision back in, plus the arithmetic that proves a fold
moved entries and changed nothing else.

The live register is read too. A tool whose tests all run on fixtures passes on
a repository that no longer exists, which is the shape
`INC-2026-10-24-three-instruments-in-one-day-tested-a-proxy-instead-of-the-mechanism`
names.
"""

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "incidents", ROOT / "tools" / "incidents.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


inc = _load()


REGISTER = """# Incident register

STANDING RULE: any issue that occurs MORE THAN ONCE is recorded here.

## INC-2026-10-01-the-first-thing — a subtitle (2026-10-01, engineer seat)

Body of the first.

### A subsection, which is not an entry

More body.

## Incident 7 — a legacy numbered entry (2026-09-20)

Body of the legacy one.
"""


def entry(inc_id, body="Body.\n"):
    return f"## {inc_id} — a title (2026-10-24, engineer seat)\n\n{body}"


# --- the parse, which everything else depends on ------------------------------


def test_only_level_two_headings_are_entries():
    """A `###` subsection inside an entry is not a second entry."""
    entries = inc.split_entries(REGISTER)
    assert [e.key for e in entries] == [
        "INC-2026-10-01-the-first-thing",
        "Incident 7",
    ]


def test_a_heading_inside_a_fenced_block_is_not_an_entry():
    """Entries quote shell and Markdown, and a quoted `## ` is not a filing.

    Without this the register's own worked examples would parse as entries and
    the duplicate-id check would fire on prose.
    """
    text = REGISTER + "\n## INC-2026-10-02-real\n\n```\n## INC-2026-10-02-real\n```\n"
    keys = [e.key for e in inc.split_entries(text)]
    assert keys.count("INC-2026-10-02-real") == 1
    assert not inc.check(text, [])


def test_the_id_stops_at_the_em_dash_rather_than_eating_the_subtitle():
    """Every real entry has `INC-id — subtitle`, so the id must end at the dash."""
    found = inc.split_entries("## INC-2026-10-24-a-slug — and a long subtitle here\n")
    assert found[0].key == "INC-2026-10-24-a-slug"
    assert found[0].date == "2026-10-24"


def test_a_legacy_number_keys_on_its_number():
    """`Incident 24` appears three times in the live file and that is the key."""
    assert inc.heading_key("Incident 24 — Monday's issue never existed (2026-09-20)") == (
        "Incident 24"
    )
    assert inc.heading_key("2026-09-18 — the first full week") == (
        "2026-09-18 — the first full week"
    )


# --- check, the gate ----------------------------------------------------------


def test_a_clean_register_and_an_empty_inbox_pass():
    assert inc.check(REGISTER, []) == []


def test_a_well_formed_inbox_entry_passes():
    name = "INC-2026-10-24-a-new-thing.md"
    assert inc.check(REGISTER, [(name, entry("INC-2026-10-24-a-new-thing"))]) == []


def test_a_conflict_marker_in_the_register_is_a_problem():
    """`tools/check_registers.py` found a bare `=======` on main once already."""
    problems = inc.check(REGISTER + "\n=======\n", [])
    assert any("conflict marker" in p for p in problems)


def test_a_conflict_marker_in_an_inbox_entry_is_a_problem():
    """An unresolved marker in the inbox would be folded into the register verbatim."""
    body = "Body.\n<<<<<<< HEAD\nmine\n=======\ntheirs\n>>>>>>> other\n"
    problems = inc.check(
        REGISTER, [("INC-2026-10-24-x.md", entry("INC-2026-10-24-x", body))]
    )
    assert any("conflict marker in an inbox entry" in p for p in problems)


def test_an_id_already_in_the_register_is_refused():
    """The one way the inbox could still file something twice."""
    name = "INC-2026-10-01-the-first-thing.md"
    problems = inc.check(REGISTER, [(name, entry("INC-2026-10-01-the-first-thing"))])
    assert any("already in the register" in p for p in problems)


def test_two_inbox_files_claiming_one_id_are_refused():
    """Two seats cannot collide on the anchor, so this is the residual collision."""
    problems = inc.check(
        REGISTER,
        [
            ("INC-2026-10-24-same.md", entry("INC-2026-10-24-same")),
            ("INC-2026-10-24-same.md ", entry("INC-2026-10-24-same")),
        ],
    )
    assert any("is also filed by" in p or "filename must be" in p for p in problems)


def test_a_filename_that_disagrees_with_its_heading_is_refused():
    """A reader greps the id. If the two disagree, one of the two greps fails."""
    problems = inc.check(
        REGISTER, [("INC-2026-10-24-filename.md", entry("INC-2026-10-24-heading"))]
    )
    assert any("the filename says" in p for p in problems)


def test_a_filename_outside_the_scheme_is_refused():
    problems = inc.check(REGISTER, [("notes.md", entry("INC-2026-10-24-x"))])
    assert any("must be INC-YYYY-MM-DD-slug.md" in p for p in problems)


def test_an_inbox_file_with_no_heading_is_refused():
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", "Just prose.\n")])
    assert any("no heading carries an INC id" in p for p in problems)


def test_two_entries_in_one_inbox_file_are_refused():
    """One file per entry is the mechanism. Two reintroduces the shared anchor."""
    two = entry("INC-2026-10-24-x") + "\n" + entry("INC-2026-10-24-y")
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", two)])
    assert any("INC ids in one file" in p for p in problems)
    assert any("INC-2026-10-24-y" in p for p in problems)


# --------------------------------------------------------------------------
# The three shapes this gate used to call a collision, and none of them is one
# --------------------------------------------------------------------------
#
# `check` counted level-two headings as its proxy for "one entry per file". On
# 2026-11-02 that proxy was wrong about three files on `main`, so
# `test_the_live_register_passes_its_own_gate` was red there and the four
# findings it reported were all false. Two of the three were a seat appending a
# new instance to the entry it repeats, which is exactly what this register's
# standing rule asks for, and the third titles itself at level one and sections
# itself at level two, which is ordinary Markdown.
#
# The mechanism is the id, not the heading count: two entries collide when two
# headings carry two different INC ids. A section heading and an appended
# instance heading carry none, so they cannot collide with anything.


def test_an_appended_instance_is_not_a_second_entry():
    """What the standing rule asks a seat to do must not read as a collision."""
    text = (entry("INC-2026-10-24-x")
            + "\n## Instance appended 2026-11-02, ExO seat, PR #759: it repeated\n\n"
            + "More body.\n")
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", text)])
    assert problems == []


def test_section_headings_inside_one_entry_are_not_a_second_entry():
    text = (entry("INC-2026-10-24-x")
            + "\n## What happened\n\nProse.\n"
            + "\n## The repair, which is one flag\n\nProse.\n")
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", text)])
    assert problems == []


def test_a_level_one_title_with_level_two_sections_is_accepted():
    """Three files on main are written this way and none of them is malformed."""
    text = ("# INC-2026-10-24-x - a title (2026-10-24, research seat)\n\n"
            "**Observed** 2026-10-24.\n\n## What happened\n\nProse.\n")
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", text)])
    assert problems == []


def test_the_id_is_still_checked_against_the_filename_wherever_the_heading_sits():
    """The level-one form must not be a way past the filename check."""
    text = "# INC-2026-10-24-y - a title (2026-10-24, research seat)\n\nProse.\n"
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", text)])
    assert any("the filename says" in p for p in problems)


def test_two_ids_collide_even_when_one_of_them_is_a_level_one_title():
    text = ("# INC-2026-10-24-x - a title (2026-10-24, research seat)\n\nProse.\n"
            + entry("INC-2026-10-24-y"))
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", text)])
    assert any("INC ids in one file" in p for p in problems)


def test_the_same_id_twice_in_one_file_is_not_counted_as_two_entries():
    """A repeated id is one entry written twice, which the register check catches."""
    text = entry("INC-2026-10-24-x") + "\n" + entry("INC-2026-10-24-x")
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", text)])
    assert not any("INC ids in one file" in p for p in problems)


def test_a_new_duplicate_inc_id_in_the_register_is_a_problem():
    problems = inc.check(REGISTER + entry("INC-2026-10-01-the-first-thing"), [])
    assert any("answering to one id" in p for p in problems)


def test_require_folded_is_off_by_default_and_loud_when_asked():
    """The flag exists; the default must not, because it could redden main."""
    inbox = [("INC-2026-10-24-x.md", entry("INC-2026-10-24-x"))]
    assert inc.check(REGISTER, inbox) == []
    problems = inc.check(REGISTER, inbox, require_folded=True)
    assert any("still holds 1 entries" in p for p in problems)


def test_a_new_legacy_collision_is_loud_and_the_existing_ones_are_not():
    """L-A18: ids already issued are permanent, so only a new one is a failure."""
    baseline = REGISTER + "\n## Incident 7 — a second entry on one number\n\nBody.\n"
    problems = inc.check(baseline, [])
    assert any("allocated again" in p for p in problems), problems


# --- fold, and the arithmetic that makes it checkable -------------------------


def test_fold_appends_and_keeps_the_register_as_a_prefix():
    inbox = [("INC-2026-10-24-x.md", entry("INC-2026-10-24-x"))]
    folded = inc.fold_text(REGISTER, inbox)
    assert folded.startswith(REGISTER.rstrip("\n"))
    assert "INC-2026-10-24-x" in folded
    assert inc.fold_invariant(REGISTER, inbox, folded) == []


def test_fold_orders_by_the_ids_own_date_not_by_directory_order():
    """The id's date is the day observed, so a backfilled entry sorts early."""
    inbox = [
        ("INC-2026-10-24-later.md", entry("INC-2026-10-24-later")),
        ("INC-2026-10-05-earlier.md", entry("INC-2026-10-05-earlier")),
    ]
    folded = inc.fold_text(REGISTER, inbox)
    assert folded.index("INC-2026-10-05-earlier") < folded.index("INC-2026-10-24-later")
    assert inc.fold_invariant(REGISTER, inbox, folded) == []


def test_the_invariant_catches_a_dropped_entry():
    """The 2026-10-24 hand resolution deleted a line and left no marker."""
    inbox = [
        ("INC-2026-10-24-x.md", entry("INC-2026-10-24-x")),
        ("INC-2026-10-24-y.md", entry("INC-2026-10-24-y")),
    ]
    damaged = inc.fold_text(REGISTER, inbox[:1])
    failures = inc.fold_invariant(REGISTER, inbox, damaged)
    assert any("not present verbatim" in f for f in failures)
    assert any("line arithmetic" in f for f in failures)


def test_the_invariant_catches_a_rewritten_prefix():
    """A fold that edits the register it started from is not an append."""
    inbox = [("INC-2026-10-24-x.md", entry("INC-2026-10-24-x"))]
    rewritten = inc.fold_text(REGISTER.replace("STANDING RULE", "standing rule"), inbox)
    failures = inc.fold_invariant(REGISTER, inbox, rewritten)
    assert any("prefix" in f for f in failures)


def test_the_invariant_catches_a_duplicated_entry():
    """More lines than the arithmetic allows is what `merge=union` produces."""
    inbox = [("INC-2026-10-24-x.md", entry("INC-2026-10-24-x"))]
    doubled = inc.fold_text(REGISTER, inbox + inbox)
    failures = inc.fold_invariant(REGISTER, inbox, doubled)
    assert any("line arithmetic" in f for f in failures)


def test_a_folded_register_still_passes_check():
    """The round trip: fold, then the gate must accept the result."""
    inbox = [("INC-2026-10-24-x.md", entry("INC-2026-10-24-x"))]
    folded = inc.fold_text(REGISTER, inbox)
    assert inc.check(folded, []) == []


# --- new ----------------------------------------------------------------------


def test_new_writes_a_skeleton_whose_filename_and_heading_agree(tmp_path):
    """The format is the enforcement, so the helper must satisfy its own gate."""
    path = inc.new_entry("a-thing-repeated", "2026-10-24", "engineer", "A title", tmp_path)
    assert path.name == "INC-2026-10-24-a-thing-repeated.md"
    assert inc.check(REGISTER, [(path.name, path.read_text())]) == []


def test_new_refuses_an_id_that_is_already_filed(tmp_path):
    inc.new_entry("a-thing", "2026-10-24", "engineer", "A title", tmp_path)
    with pytest.raises(FileExistsError):
        inc.new_entry("a-thing", "2026-10-24", "engineer", "A title", tmp_path)


# --- the live tree ------------------------------------------------------------


def test_the_live_register_passes_its_own_gate():
    """Run against the real file, not a fixture."""
    text = (ROOT / "docs" / "agents" / "incidents.md").read_text()
    assert inc.check(text, inc._read_inbox(inc.INBOX)) == []


def test_the_live_baselines_are_still_the_measured_truth():
    """A baseline nobody re-measures is a number that drifts into fiction.

    If a legacy duplicate is ever repaired, this fails and the constant comes
    down, which is the only way a baseline ratchets in the right direction.
    """
    text = (ROOT / "docs" / "agents" / "incidents.md").read_text()
    census = inc.legacy_census(inc.split_entries(text))
    assert census["detail"] == inc.BASELINE_DUPLICATE_LEGACY, census["detail"]
    assert census["excess"] == inc.BASELINE_EXCESS_LEGACY_ENTRIES, census["detail"]


def test_every_live_inbox_entry_would_fold_cleanly():
    """Whatever is waiting in the inbox right now must be foldable."""
    text = (ROOT / "docs" / "agents" / "incidents.md").read_text()
    inbox = inc._read_inbox(inc.INBOX)
    folded = inc.fold_text(text, inbox)
    assert inc.fold_invariant(text, inbox, folded) == []
    assert inc.check(folded, []) == []


def test_the_inbox_directory_and_its_readme_exist():
    """A convention with no landing place is a convention nobody follows."""
    assert inc.INBOX.is_dir()
    readme = (inc.INBOX / "README.md").read_text()
    assert "tools/incidents.py" in readme
    assert "L-A18" in readme


def test_a_colon_separated_heading_still_keys_on_its_id():
    """The register already held one, so the parser had to learn it.

    `INC-2026-11-02-the-dispatch-prompt-...-holds-back` separates its id from
    its summary with `: ` where the skeleton this tool writes uses ` - `. Before
    2026-11-02 that heading did not match `INC_ID`, so `heading_key` keyed the
    entry on its whole heading: the id a charter would cite found nothing, and a
    second filing of the same id would not have collided with the first, which
    is the only guarantee the `INC-YYYY-MM-DD-slug` scheme makes.
    """
    heading = ("INC-2026-11-02-a-slug: a summary after a colon "
               "(2026-11-02, engineer seat)")
    assert inc.heading_key(heading) == "INC-2026-11-02-a-slug"
    entry, = inc.split_entries(f"## {heading}\n\nBody.\n")
    assert entry.inc_id == "INC-2026-11-02-a-slug"
    assert entry.date == "2026-11-02"


def test_any_separator_keys_on_the_id_because_the_slug_names_its_own_end():
    """The delimiter list was extended once and the next separator broke it.

    `:` was added to `INC_ID`'s lookahead on 2026-11-02 for one heading that
    used it. On 2026-11-08 a heading used `, ` instead, the match failed the
    same way, and `test_the_live_register_ids_all_parse` went red on `main`.
    Extending the list again would have bought one more separator, so the
    boundary now comes from the slug's own alphabet.

    Every mark below is prose by construction, because a slug is `[a-z0-9-]`
    and cannot contain any of them. The comma is the one that was live; the
    rest are the ones a list would have gone red on next.
    """
    for separator in (", ", ": ", " - ", " \u2014 ", " \u2013 ", "; ", ". ", "! ", "? ",
                      " (", ", and ", " \u2192 "):
        heading = f"INC-2026-11-02-a-slug{separator}a summary (2026-11-02, engineer seat)"
        assert inc.heading_key(heading) == "INC-2026-11-02-a-slug", separator
        entry, = inc.split_entries(f"## {heading}\n\nBody.\n")
        assert entry.inc_id == "INC-2026-11-02-a-slug", separator
        assert entry.date == "2026-11-02", separator


def test_a_trailing_hyphen_is_not_part_of_the_id():
    """What the old lookahead bought that the alphabet rule has to keep.

    The slug must end alphanumeric, so greedily eating `[a-z0-9-]` cannot
    carry a dangling separator hyphen into the id a charter would cite.
    """
    assert inc.heading_key("INC-2026-11-02-a-slug-- a summary") == "INC-2026-11-02-a-slug"
    assert inc.heading_key("INC-2026-11-02-a-slug - a summary") == "INC-2026-11-02-a-slug"


def test_the_live_register_ids_all_parse():
    """Every INC heading in the register yields the id a charter would cite."""
    text = (ROOT / "docs" / "agents" / "incidents.md").read_text()
    for item in inc.split_entries(text):
        if item.heading.startswith("INC-"):
            assert item.inc_id, item.heading
            assert re.match(r"^\d{4}-\d{2}-\d{2}$", item.date or ""), item.heading


def test_a_substitution_among_legacy_numbers_is_still_loud():
    """Repair one legacy duplicate, collide a new number, and the total is unmoved.

    This is the case a counted baseline cannot see, and the first draft of
    `tools/incidents.py` used a counted baseline. It is incident 26's shape in
    this register: a gate written as a list catches only what already shipped.
    """
    live = (ROOT / "docs" / "agents" / "incidents.md").read_text()
    entries = inc.split_entries(live)
    assert inc.check(live, []) == []

    # "Incident 22" has two entries on the baseline. Drop one of them, so the
    # repaired register holds eight duplicated keys instead of nine.
    victim = [e for e in entries if e.key == "Incident 22"][-1]
    block = "\n".join(victim.body)
    repaired = live.replace("## " + victim.heading + "\n" + "\n".join(victim.body[1:]), "")
    assert repaired != live or block  # the replace found its target or the body is empty

    # Now collide a number that has never collided, and keep the total at nine.
    substituted = repaired + "\n## Incident 21 — a second entry on one number\n\nBody.\n"
    problems = inc.check(substituted, [])
    assert any("Incident 21" in p and "allocated again" in p for p in problems), problems


# --- the branch's own appends, which no predicate here could see --------------
#
# The predicate the ExO seat routed to this file, from
# `INC-2026-10-27-the-register-anchor-conflicted-seven-times-in-two-days-and-its-inbox-has-no-gate`.
# The register's append anchor needed a keep-both merge resolve seven times in
# the thirty-nine hours after the inbox landed, and one of those was handed back
# against a pull request that had already passed review clean.
#
# The reason nothing caught them is structural rather than careless: every other
# predicate in `check` inspects an entry that is already in the inbox or already
# in the register, so a seat that ignores the inbox entirely produces a clean
# read. The question none of them asks is what the branch did.
#
# These tests build a real repository, because the predicate's whole subject is
# a diff against a merge base and a fixture cannot have one.


def _run(repo, *args):
    import subprocess
    done = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


@pytest.fixture
def repo(tmp_path):
    """A repository with a register, an inbox and a `base` branch to diff against."""
    (tmp_path / "docs" / "agents" / "incidents" / "inbox").mkdir(parents=True)
    (tmp_path / "docs" / "agents" / "incidents.md").write_text(REGISTER)
    _run(tmp_path, "init", "-q", "-b", "base")
    _run(tmp_path, "config", "user.email", "t@example.com")
    _run(tmp_path, "config", "user.name", "t")
    _run(tmp_path, "add", "-A")
    _run(tmp_path, "commit", "-qm", "the register as it stands")
    _run(tmp_path, "checkout", "-q", "-b", "work")
    return tmp_path


def _register(repo):
    return repo / "docs" / "agents" / "incidents.md"


def _inbox(repo):
    return repo / "docs" / "agents" / "incidents" / "inbox"


def _commit(repo, message="the branch's work"):
    _run(repo, "add", "-A")
    _run(repo, "commit", "-qm", message)


def test_a_branch_that_appends_to_the_register_with_no_inbox_file_is_caught(repo):
    _register(repo).write_text(REGISTER + "\n" + entry("INC-2026-10-27-straight-in"))
    _commit(repo)
    problems, skipped = inc.branch_appends("base", [], root=repo)
    assert skipped == ""
    assert len(problems) == 1
    assert "INC-2026-10-27-straight-in" in problems[0]
    # The problem says what to do instead, because a gate that only refuses
    # teaches the next seat nothing.
    assert "tools/incidents.py new" in problems[0]


def test_a_branch_that_files_into_the_inbox_passes(repo):
    name = "INC-2026-10-27-filed-properly.md"
    (_inbox(repo) / name).write_text(entry("INC-2026-10-27-filed-properly"))
    _commit(repo)
    problems, skipped = inc.branch_appends("base", [name], root=repo)
    assert (problems, skipped) == ([], "")


def test_a_branch_that_touches_the_register_at_all_is_not_the_question(repo):
    # Editing an entry that is already there is ordinary work. The predicate is
    # about a new level-two heading, not about the file being modified.
    _register(repo).write_text(
        REGISTER.replace("Body of the first.", "Body of the first, corrected."))
    _commit(repo)
    assert inc.branch_appends("base", [], root=repo) == ([], "")


def test_the_fold_is_exempt_because_it_is_a_move_and_not_an_append(repo):
    inc_id = "INC-2026-10-27-folded"
    # Filed on `base`, which is the real shape: a seat files into the inbox, the
    # entry reaches the mainline, and the fold on the mainline moves it.
    _run(repo, "checkout", "-q", "base")
    (_inbox(repo) / f"{inc_id}.md").write_text(entry(inc_id))
    _commit(repo, "file it")
    _run(repo, "checkout", "-q", "work")
    _run(repo, "merge", "-q", "base")
    folded = inc.fold_text(_register(repo).read_text(), [(f"{inc_id}.md", entry(inc_id))])
    _register(repo).write_text(folded)
    (_inbox(repo) / f"{inc_id}.md").unlink()
    _commit(repo, "fold it")
    # The heading is now an addition against `base` and the inbox is empty, so
    # the naive reading of this predicate would make the one legitimate append
    # the loudest failure in the file.
    added, _ = inc.added_and_removed_ids(inc.register_diff("base", root=repo)[0])
    assert inc_id in added
    assert inc.branch_appends("base", [], root=repo) == ([], "")


def test_the_exemption_is_keyed_on_the_moved_file_and_not_on_a_branch_name(repo):
    # An append that deletes some *other* inbox file is not a fold of this id.
    other = "INC-2026-10-27-unrelated.md"
    (_inbox(repo) / other).write_text(entry("INC-2026-10-27-unrelated"))
    _commit(repo, "a file to delete later")
    (_inbox(repo) / other).unlink()
    _register(repo).write_text(REGISTER + "\n" + entry("INC-2026-10-27-smuggled"))
    _commit(repo, "delete one, append another")
    problems, _ = inc.branch_appends("base", [], root=repo)
    assert len(problems) == 1 and "INC-2026-10-27-smuggled" in problems[0]


def test_folding_on_a_branch_is_not_exempt_and_should_not_be(repo):
    # The boundary, found by the test above while this was being written. The
    # exemption is for an inbox file that reached the mainline and is being
    # moved there. A branch that files and folds in its own history shows git no
    # deletion against the merge base, because the file never existed in it, and
    # the net effect on the register is an append from a branch -- which is the
    # thing the inbox exists to stop. So it is reported, correctly.
    inc_id = "INC-2026-10-27-filed-and-folded-on-one-branch"
    (_inbox(repo) / f"{inc_id}.md").write_text(entry(inc_id))
    _commit(repo, "file it")
    _register(repo).write_text(
        inc.fold_text(_register(repo).read_text(), [(f"{inc_id}.md", entry(inc_id))]))
    (_inbox(repo) / f"{inc_id}.md").unlink()
    _commit(repo, "fold it on the branch")
    problems, _ = inc.branch_appends("base", [], root=repo)
    assert len(problems) == 1 and inc_id in problems[0]


def test_a_removed_heading_is_not_reported_as_an_append(repo):
    victim = [e for e in inc.split_entries(REGISTER) if e.inc_id][0]
    _register(repo).write_text(
        REGISTER.replace("## " + victim.heading + "\n", "")
    )
    _commit(repo)
    added, removed = inc.added_and_removed_ids(inc.register_diff("base", root=repo)[0])
    assert victim.inc_id in removed and victim.inc_id not in added
    assert inc.branch_appends("base", [], root=repo) == ([], "")


def test_a_base_that_does_not_resolve_says_so_rather_than_passing_quietly(repo):
    # L-A21, and this file's own closing paragraph: a gate that saw nothing must
    # not read as a quiet pass. The reason is returned to the caller, which
    # prints it, rather than being swallowed into an empty problem list.
    problems, skipped = inc.branch_appends("no-such-ref", [], root=repo)
    assert problems == []
    assert "no-such-ref" in skipped


def test_an_inbox_name_that_is_not_an_id_claims_nothing(repo):
    _register(repo).write_text(REGISTER + "\n" + entry("INC-2026-10-27-straight-in"))
    _commit(repo)
    problems, _ = inc.branch_appends("base", ["notes.md", "README.md"], root=repo)
    assert len(problems) == 1


def test_the_cli_reads_the_predicate_only_when_given_a_base(repo, monkeypatch, capsys):
    monkeypatch.setattr(inc, "ROOT", repo)
    monkeypatch.setattr(inc, "REGISTER", _register(repo))
    monkeypatch.setattr(inc, "INBOX", _inbox(repo))
    _register(repo).write_text(REGISTER + "\n" + entry("INC-2026-10-27-straight-in"))
    _commit(repo)
    assert inc.main(["check"]) == 0                      # shape only, as before
    assert inc.main(["check", "--base", "base"]) == 1    # and now the branch too
    assert "INC-2026-10-27-straight-in" in capsys.readouterr().out


def test_the_live_branch_files_every_incident_it_adds_through_the_inbox():
    # The gate pointed at this repository, which is the only reading that can
    # catch the next instance. Skipped rather than failed where the base cannot
    # be named: the host clones `--depth 1`, which implies `--single-branch`, so
    # `origin/main` is not always a ref that resolves
    # (`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`).
    code, _ = inc.git("rev-parse", "--verify", "--quiet", "origin/main")
    if code != 0:
        pytest.skip("origin/main does not resolve on this checkout")
    names = [p.name for p in inc.inbox_files()]
    problems, skipped = inc.branch_appends("origin/main", names)
    assert skipped == ""
    assert problems == [], problems


# ---------------------------------------------------------------------------
# The lookup half: `prior`.
#
# The claim under test is not "the ranking is good". It is narrower and it is
# checkable: a seat holding a failure gets back the entry that already filed it,
# and gets told whether that entry prescribed a remedy. The fixtures pin the
# mechanism and the live register pins the one case that produced the tool, per
# `INC-2026-10-24-three-instruments-in-one-day-tested-a-proxy-instead-of-the-mechanism`.

PRIOR_REGISTER = """# Incident register

STANDING RULE: any issue that occurs MORE THAN ONCE is recorded here.

## INC-2026-01-01-the-ranker-ties-on-a-bare-date two bundles one day (2026-01-01, skill seat)

**What happened.** `rank_bundles()` sorts on `generated`, which is a bare date,
so two bundles written the same day are equal on every key and the winner is
alphabetical.

**The fix, which is the one already proposed.** Give `generated` a time, or
tie-break on a recorded timestamp.

## INC-2026-01-02-a-wake-fired-for-a-fixed-red stale wake (2026-01-02, engineer seat)

**What happened.** A `checks` failure woke a run against a commit a later commit
of the same run had already repaired.

**The fix, or why there is not one yet.** None here, and the repair is not this
seat's. Routed to the exo seat, which owns the wake path.

## INC-2026-01-03-an-old-entry-with-no-fix-section narrative only (2026-01-03, pm seat)

**What happened.** Something happened and nobody wrote down what was done about
it, which several of the oldest entries in the live register look like.
"""


def _prior_entries():
    return inc.split_entries(PRIOR_REGISTER, "register")


def test_a_failure_in_hand_finds_the_entry_that_already_filed_it():
    """The whole point: the query is a failure, not an id."""
    found = inc.prior_art(
        "rank_bundles tie: two bundles generated the same day, alphabetical winner",
        _prior_entries(),
    )
    assert found["hits"], "a query quoting the entry's own subject found nothing"
    assert found["hits"][0]["id"] == "INC-2026-01-01-the-ranker-ties-on-a-bare-date"
    assert found["hits"][0]["remedy"] == "REMEDY"


def test_the_remedy_paragraph_comes_back_and_not_only_the_id():
    """An id a seat still has to go and open is the step that does not happen."""
    found = inc.prior_art("rank_bundles bare date tie-break", _prior_entries())
    body = "\n".join(found["hits"][0]["remedy_lines"])
    assert "recorded timestamp" in body
    # The section stops at the next bold lead-in rather than running to the end
    # of the entry, or every hit prints the whole entry and nothing is read.
    assert "What happened" not in body


def test_a_fix_section_that_says_the_fix_is_owed_is_not_a_remedy():
    """The skeleton invites "or why there is not one yet", so the heading lies."""
    found = inc.prior_art("checks failure woke a run for a red already repaired",
                          _prior_entries())
    row = next(h for h in found["hits"]
               if h["id"] == "INC-2026-01-02-a-wake-fired-for-a-fixed-red")
    assert row["remedy"] == "OPEN"


def test_an_entry_with_no_fix_section_says_so_rather_than_claiming_a_remedy():
    found = inc.prior_art("nobody wrote down what was done about it narrative",
                          _prior_entries())
    row = next(h for h in found["hits"]
               if h["id"] == "INC-2026-01-03-an-old-entry-with-no-fix-section")
    assert row["remedy"] == "NONE"
    assert row["remedy_lines"] == []


def test_a_rare_identifier_outranks_a_word_the_whole_register_uses():
    """IDF is the reason there is no stopword list to go stale."""
    found = inc.prior_art("rank_bundles register entry recorded happened",
                          _prior_entries())
    assert found["hits"][0]["id"] == "INC-2026-01-01-the-ranker-ties-on-a-bare-date"


def test_a_term_in_every_entry_scores_nothing_and_matches_nothing():
    """Otherwise the headline reads "632 of 632 entries match", which it did."""
    found = inc.prior_art("happened", _prior_entries())
    assert found["matched"] == 0, "a term with zero information produced matches"
    assert found["close"] == 0


def test_the_seat_of_an_entry_is_read_off_its_heading():
    found = inc.prior_art("rank_bundles bare date", _prior_entries())
    assert found["hits"][0]["seat"] == "skill"


def test_both_halves_of_the_register_are_searched(tmp_path):
    """41% of the live entries are inbox files, so skipping them reads 59%."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "INC-2026-01-04-only-in-the-inbox.md").write_text(
        "## INC-2026-01-04-only-in-the-inbox a quuxly defect (2026-01-04, writer seat)\n\n"
        "**What happened.** The quuxifier emitted a zorblat.\n\n"
        "**The fix.** The zorblat is now a frobnitz.\n"
    )
    entries = inc.all_entries(PRIOR_REGISTER, inbox)
    found = inc.prior_art("quuxifier emitted a zorblat", entries)
    assert found["inbox_entries"] == 1
    assert found["hits"][0]["id"] == "INC-2026-01-04-only-in-the-inbox"
    assert "frobnitz" in "\n".join(found["hits"][0]["remedy_lines"])


def test_nothing_matching_says_file_it_as_a_first_instance():
    """A lookup that hedges on an empty result teaches a seat to ignore it."""
    import io
    out = io.StringIO()
    found = inc.prior_art("zzqqx unrelated nonsense token", _prior_entries())
    assert found["hits"] == []
    inc.report_prior(found, stream=out)
    assert "first instance" in out.getvalue()


def test_remedies_only_drops_the_entries_that_cannot_answer_the_question():
    found = inc.prior_art("a run woke for a red already repaired by its own commit",
                          _prior_entries(), remedies_only=True)
    assert all(h["remedy"] == "REMEDY" for h in found["hits"])


def test_a_seats_own_prior_entry_is_called_out_as_its_own():
    import io
    out = io.StringIO()
    found = inc.prior_art("rank_bundles tie two bundles generated the same day",
                          _prior_entries())
    inc.report_prior(found, seat="skill", stream=out)
    assert "YOUR OWN SEAT" in out.getvalue()
    assert "your own seat" in out.getvalue()


def test_the_report_never_fails_a_run():
    """A lookup that can hold a pull request is a lookup a seat stops running."""
    assert inc.main(["prior", "rank_bundles", "tie"]) == 0
    assert inc.main(["prior", "zzqqx-nothing-matches-this"]) == 0


def test_an_empty_query_is_refused_rather_than_answered():
    assert inc.main(["prior"]) == 2


def test_a_pytest_log_can_be_the_query(tmp_path):
    """The shape a failure arrives in is not under the reader's control."""
    log = tmp_path / "pytest.log"
    log.write_text(
        "FAILED tests/test_skill_receipts.py::test_every_published_receipt_is_current\n"
        "E   AssertionError: rank_bundles picked the older of two bundles generated\n"
        "E   on the same date\n"
    )
    assert inc.main(["prior", "--file", str(log), "--limit", "2"]) == 0


# --- the live register, which is the case that produced the tool -------------

def test_the_live_register_answers_the_failure_that_was_missed_on_2026_11_09():
    """The regression this tool is.

    On 2026-11-09 a seat shipped red on the receipt gate having followed "check
    the register before you ship". The remedy was already written, twice, by
    that seat, in `INC-2026-10-26-the-library-shows-the-older-of-two-receipts-
    dated-the-same-day`. If this query stops returning that entry with a remedy,
    the instrument has stopped answering the only question it was built for.
    """
    found = inc.prior_art(
        "tests/test_skill_receipts.py failed: two bundles on the same date, a "
        "published receipt reads stale, rank_bundles tie",
        inc.all_entries(),
        limit=5,
    )
    ids = [h["id"] for h in found["hits"]]
    wanted = "INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day"
    assert wanted in ids, f"the missed remedy is not in the top five: {ids}"
    row = next(h for h in found["hits"] if h["id"] == wanted)
    assert row["remedy"] == "REMEDY"
    assert "timestamp" in "\n".join(row["remedy_lines"])


def test_the_live_inbox_holds_entries_the_register_file_does_not():
    """The measurement that makes grepping docs/agents/incidents.md insufficient.

    This is deliberately an inequality rather than a pinned count. The fold moves
    entries from one half to the other and both numbers move with it, so pinning
    either would go red on a bookkeeping step nobody promised to run.
    """
    entries = inc.all_entries()
    inbox_only = [e for e in entries if e.source != "register"]
    register = [e for e in entries if e.source == "register"]
    assert register, "the live register parsed to nothing"
    if inc.inbox_files():
        assert inbox_only, "the inbox has files and the lookup read none of them"


def test_every_live_entry_gets_one_of_three_remedy_verdicts():
    """No fourth state, and no exception thrown on a real entry's prose."""
    for entry in inc.all_entries():
        verdict, section = inc.remedy_of(entry)
        assert verdict in ("REMEDY", "OPEN", "NONE"), entry.key
        assert (verdict == "NONE") == (section == []), entry.key


def test_an_unreadable_query_file_is_refused_by_name_and_not_searched_empty(tmp_path, capsys):
    """The census row for `--file` asserts this, so it is pinned here.

    An empty search returns "nothing in the register matches this. File it as a
    first instance", which is the one wrong answer this tool must never give. So
    a `--file` that cannot be read has to stop the lookup rather than shrink it.
    """
    missing = tmp_path / "no-such.log"
    assert inc.main(["prior", "--file", str(missing)]) == 2
    out = capsys.readouterr().out
    assert str(missing) in out
    assert "first instance" not in out


def test_what_counts_as_close_scales_with_the_length_of_the_query():
    """A fixed floor means two different things at two query lengths.

    Measured on the live register before this was relative: a short query called
    32 of 632 entries close and a two-sentence one called 222, which is the case
    where a seat pastes a failure verbatim and most needs the number.
    """
    assert inc.strong_threshold(1.0) == pytest.approx(0.6)
    assert inc.strong_threshold(0.2) == inc.STRONG_FLOOR, "the floor stops holding"
    assert inc.strong_threshold(0.0) == inc.STRONG_FLOOR


def test_a_long_query_does_not_call_a_third_of_the_register_close():
    long_query = (
        "a seat measured main as red against a stale snapshot of the trunk; the "
        "fix had already merged into main twenty five minutes before the "
        "measurement was reported"
    )
    found = inc.prior_art(long_query, inc.all_entries(), limit=3)
    assert found["close"] < found["entries_searched"] / 10, (
        f"{found['close']} of {found['entries_searched']} called close"
    )
    assert found["close_threshold"] >= inc.STRONG_FLOOR


def test_filing_an_entry_does_not_rank_the_entry_it_just_wrote(tmp_path, capsys, monkeypatch):
    """Found by running `new` for real: the skeleton scored 1.000 on its own slug.

    A lookup at filing time that ranks the file it just created pushes the real
    precedent down a rank, which is the one thing it exists not to do.
    """
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "INC-2026-01-05-the-quuxifier-emitted-a-zorblat.md").write_text(
        "## INC-2026-01-05-the-quuxifier-emitted-a-zorblat first time (2026-01-05, pm seat)\n\n"
        "**What happened.** The quuxifier emitted a zorblat.\n\n"
        "**The fix.** The zorblat became a frobnitz.\n"
    )
    monkeypatch.setattr(inc, "INBOX", inbox)
    monkeypatch.setattr(inc, "REGISTER", tmp_path / "incidents.md")
    (tmp_path / "incidents.md").write_text(PRIOR_REGISTER)
    assert inc.main([
        "new", "--slug", "the-quuxifier-emitted-a-zorblat-again",
        "--date", "2026-01-06", "--seat", "engineer",
        "--title", "the quuxifier emitted a zorblat a second time",
    ]) == 0
    out = capsys.readouterr().out
    assert "INC-2026-01-05-the-quuxifier-emitted-a-zorblat\n" in out, (
        "the prior instance is not in the ranking"
    )
    assert "zorblat-again" not in out.split("The closest")[-1], (
        "the entry just written ranked itself"
    )


def test_a_single_close_match_is_reported_in_the_singular():
    import io
    out = io.StringIO()
    found = inc.prior_art("rank_bundles bare date tie-break alphabetical", _prior_entries())
    found["close"] = 1
    found["close_with_remedy"] = 1
    inc.report_prior(found, stream=out)
    assert "1 of them is a close match" in out.getvalue()


def test_the_report_writes_to_the_stdout_in_use_and_not_the_one_at_import(capsys):
    """A default of `sys.stdout` in the signature binds the object at import.

    This run shipped that twice in one file, here and in the inbox `new` writes
    to, and the second one wrote a test fixture into the real register's inbox
    before it was caught. `tools/target_census.py` already used
    `stream=None` with `or sys.stdout` in the body, so the convention existed
    and this code diverged from it inside the same family of tools.
    """
    found = inc.prior_art("rank_bundles bare date tie-break", _prior_entries())
    inc.report_prior(found)
    assert "INC-2026-01-01-the-ranker-ties-on-a-bare-date" in capsys.readouterr().out


def test_a_truncated_list_never_reports_that_nothing_was_filed(capsys):
    """Found by running `--limit 0`: it said nothing matched while 58 entries did.

    A confident zero off a list that was cut to a limit is the one wrong answer
    this tool must not give, and it is the same shape as every "a predicate that
    saw nothing read as a pass" entry in the register.
    """
    found = inc.prior_art("rank_bundles bare date tie", _prior_entries(), limit=0)
    assert found["matched"] > 0
    assert found["hits"] == []
    inc.report_prior(found)
    out = capsys.readouterr().out
    assert "first instance" not in out
    assert "Raise --limit" in out


def test_a_limit_below_one_is_a_usage_error():
    assert inc.main(["prior", "rank_bundles", "--limit", "0"]) == 2
    assert inc.main(["prior", "rank_bundles", "--limit", "-3"]) == 2


# --------------------------------------------------------------------------
# The tie-break in `prior_art` (engineer seat, 2026-11-09)
#
# Reported by the skill seat the hour the lookup shipped. An assertion name is
# the most distinctive term this corpus has, so every entry about one gate
# carries it and ties at confidence 1.000 are the common case rather than the
# edge one. Breaking that tie on the id is alphabetical order dressed as
# relevance: on the live register the entry that governed the failure was third
# behind one whose id happened to sort early.
# --------------------------------------------------------------------------

TIE_REGISTER = """# Incident register

## INC-2026-01-01-aaa-no-remedy - the widget gate went red (2026-01-01, a seat)

**What happened.** The widget gate went red and nobody read it.

## INC-2026-11-08-mmm-open - the widget gate went red (2026-11-08, a seat)

**What happened.** The widget gate went red and nobody read it.

**The fix, or why there is not one yet.** Not this seat's file.

## INC-2026-11-09-zzz-remedy - the widget gate went red (2026-11-09, a seat)

**What happened.** The widget gate went red and nobody read it.

**The fix shipped here.** One widget row in the census.

## INC-2026-03-03-an-unrelated-digest-failure - the digest did not send (2026-03-03, a seat)

**What happened.** The mailer refused the recipient list and the issue never went out.

## INC-2026-04-04-an-unrelated-clone-failure - the clone came back shallow (2026-04-04, a seat)

**What happened.** A merge base between two close branches read as unrelated histories.
"""

# Two entries above share none of the query's terms, on purpose. The scorer
# weights a term by how rare it is, so a fixture where every entry carries
# every term gives each one no discriminating power at all and the whole
# ranking comes back empty. That is how the first draft of these tests failed,
# and it is the same in-band shape as the rest of this run: a degenerate
# corpus returns a legal empty result rather than an error.


def _tie_entries():
    return inc.split_entries(TIE_REGISTER, "register")


def test_the_descending_date_key_puts_newer_first_and_dateless_last():
    """The helper on its own, because both of its directions were wrong once.

    The first draft raised on a dateless entry, which the live register has.
    The second returned the low codepoint for one, which an ascending sort puts
    on top, so "sorts last" had to mean "largest key".
    """
    assert inc._descending("2026-11-09") < inc._descending("2026-11-08")
    assert inc._descending("2026-01-01") < inc._descending("2025-12-31")
    assert inc._descending("2026-11-09") < inc._descending(None)
    assert inc._descending("2026-11-09") < inc._descending("")
    # A dated range is what some register entries carry, and it must not raise.
    assert inc._descending("2026-09-17/18") == inc._descending("2026-09-17/18")


def test_a_tie_is_broken_by_remedy_then_recency_and_not_by_the_id():
    """The ranking's contract on a tie.

    The ids are chosen so alphabetical order and the intended order disagree:
    `aaa-no-remedy` would win on the id alone and is the least useful hit.
    """
    found = inc.prior_art("the widget gate went red and nobody read it",
                          _tie_entries())
    order = [h["id"] for h in found["hits"]]
    widgets = [i for i in order if "unrelated" not in i]
    assert widgets == ["INC-2026-11-09-zzz-remedy",
                       "INC-2026-11-08-mmm-open",
                       "INC-2026-01-01-aaa-no-remedy"], order
    # The three tie on confidence, so the order above is the tie-break and not
    # the score. Asserted so a scoring change cannot make this pass for the
    # wrong reason. The two distractors score lower and are excluded.
    scores = {h["confidence"] for h in found["hits"] if h["id"] in widgets}
    assert len(scores) == 1, found["hits"]


def test_the_newest_of_two_equal_verdicts_comes_first():
    """The second key, isolated from the first: both of these are OPEN."""
    entries = [e for e in _tie_entries()
               if e.key != "INC-2026-11-09-zzz-remedy"]
    found = inc.prior_art("the widget gate went red and nobody read it", entries)
    assert [h["id"] for h in found["hits"]][0] == "INC-2026-11-08-mmm-open"


def test_the_ranking_is_stable_across_two_calls_on_the_live_register():
    """A lookup a seat quotes in a pull request has to be reproducible.

    The key is total, with the id last, so this holds whatever the corpus does.
    Asserted on the real register because a partial key only shows up there.
    """
    first = inc.prior_art("test_the_uncovered_set_has_not_grown")
    second = inc.prior_art("test_the_uncovered_set_has_not_grown")
    assert [h["id"] for h in first["hits"]] == [h["id"] for h in second["hits"]]
