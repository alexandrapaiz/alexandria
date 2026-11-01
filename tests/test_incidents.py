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
    assert any("no level-two heading" in p for p in problems)


def test_two_entries_in_one_inbox_file_are_refused():
    """One file per entry is the mechanism. Two reintroduces the shared anchor."""
    two = entry("INC-2026-10-24-x") + "\n" + entry("INC-2026-10-24-y")
    problems = inc.check(REGISTER, [("INC-2026-10-24-x.md", two)])
    assert any("level-two headings" in p for p in problems)


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
