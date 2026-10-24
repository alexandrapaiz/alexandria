"""The authority gate's verdicts, under test, because it is a gate.

`tools/check_authority.py` answers one question about a diff: is this change the
owner's to merge, under `docs/standards/pm.md` §21. It landed in #456 as 714
lines with no test behind it and nothing in the suite reading its exit status,
which is the exact shape L-A9's 2026-10-05 amendment was written about. That
amendment's test of whether a gate is real has two halves: name the command,
and say what its exit status means. The command's docstring names both. This
file is the half that proves the second one, so that the mapping is a fact
about the program rather than a sentence in its header.

Why the verdicts and not the regexes. Every assertion here goes through
`examine()` on a unified diff and reads the verdict and the exit code, because
those are what a caller acts on. A test that pinned `PERMISSION` or `SPEND`
line by line would go red on any rewording of a pattern that kept every verdict
identical, and it would still not say whether the gate decided correctly.

The four cases worth more than the rest, all of them regressions:

  - A charter line that rules the OWNER is not a change to the seat's own
    authority. That is the false positive the tool exists to avoid, and it is
    the one a path check cannot reach:
    `INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`
    is a twelve-charter edit, correctly identified as a charter, held anyway,
    that moved no seat's authority at all.
  - A secret NAME in prose is not a secret write. Every charter in this
    repository is allowed to name one, and the seats read secrets constantly.
  - A price in prose spends nothing. `docs/finance/` would be one long
    `reserved` otherwise.
  - A sentence that only reflowed across a hard wrap did not move. Charters are
    hard-wrapped, so this is the ordinary case, not the exotic one.

And the direction of error is itself asserted, in both the rank and the exit
code, because it is the design: a wrong `reserved` costs one merge of waiting
and a wrong `clear` costs an authority breach, so both non-zero verdicts fail
closed and `clear` is the only verdict the gate may not reach by accident.

This file runs in no workflow. It is pinned in `tests/test_ci_coverage.py`'s
`UNCOVERED` for the reason every other file there is pinned: adding a step to
`.github/workflows/checks.yml` needs a `workflow`-scoped hand, which no agent
seat has (`docs/agents/pending-workflow-changes.md`).

    python3 -m pytest tests/test_check_authority.py -q
"""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "check_authority.py"


def _module():
    """Load `tools/check_authority.py` by path, the way the rest of this suite does.

    With one addition the neighbouring loaders do not need: the module goes
    into `sys.modules` BEFORE it executes. `check_authority` defines
    `@dataclass` types, and `dataclasses` resolves a field's annotations by
    looking its own class's module up in `sys.modules`. For a module loaded by
    path and never registered, that lookup returns `None` and decorating raises
    `AttributeError: 'NoneType' object has no attribute '__dict__'` at import.
    `tools/merge_order.py` has no dataclasses, which is the only reason the
    shorter pattern works there.
    """
    spec = importlib.util.spec_from_file_location("check_authority", TOOL)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ca = _module()


# --------------------------------------------------------------- diff building

def diff(path, hunks, old_path=None, delete=False, binary=False):
    """A unified diff over one file, in the shape `git diff` emits.

    `hunks` is a list of (old_start, lines), where each line keeps its leading
    `+`, `-` or space. Old-side line numbers are what the tool anchors a
    section lookup on, so they are passed in rather than invented here.
    """
    out = [f"diff --git a/{old_path or path} b/{path}"]
    if binary:
        out.append(f"Binary files a/{old_path or path} and b/{path} differ")
        return "\n".join(out) + "\n"
    out.append(f"--- a/{old_path or path}")
    out.append("+++ /dev/null" if delete else f"+++ b/{path}")
    for old_start, lines in hunks:
        out.append(f"@@ -{old_start},{len(lines)} +{old_start},{len(lines)} @@")
        out += lines
    return "\n".join(out) + "\n"


def verdict(text, base=None):
    return ca.examine(text, base=base)["verdict"]


def questions(text, base=None):
    return {f["question"] for f in ca.examine(text, base=base)["findings"]}


def section_line(path, sid):
    """The line number of `## <sid>. ...` in a real file in this tree.

    Looked up rather than hard-coded: these tests anchor inside sections of
    live law files, and a hard-coded 604 would go red the next time somebody
    adds a paragraph to `docs/standards/pm.md` without any verdict changing.
    """
    for i, line in enumerate((ROOT / path).read_text().splitlines(), start=1):
        if re.match(rf"^##\s+{re.escape(sid)}\.\s", line):
            return i
    raise AssertionError(f"{path} has no section {sid}; this test's anchor is stale")


# ------------------------------------------------------- the exit-status contract

def test_the_exit_status_mapping_is_what_the_docstring_promises():
    """L-A9's test of a real gate: name the command, say what the status means."""
    assert ca.EXIT == {ca.CLEAR: 0, ca.ERROR: 1, ca.RESERVED: 2, ca.UNDECIDED: 3}


def test_every_verdict_carries_its_own_exit_code_in_the_result():
    for text, expected in (
        (diff("README.md", [(1, [" a line", "+another line"])]), ca.CLEAR),
        (diff("docs/x.png", [], binary=True), ca.UNDECIDED),
    ):
        result = ca.examine(text)
        assert result["verdict"] == expected
        assert result["exit"] == ca.EXIT[expected]


def run_cli(args, stdin=""):
    return subprocess.run([sys.executable, str(TOOL), *args], input=stdin,
                          capture_output=True, text=True, cwd=ROOT, check=False)


def test_the_process_really_exits_with_the_mapped_status():
    """The mapping is only a gate if the process honours it."""
    clear = run_cli(["--stdin"], diff("README.md", [(1, [" a line", "+another"])]))
    assert clear.returncode == 0, clear.stdout

    binary = run_cli(["--stdin"], diff("docs/x.png", [], binary=True))
    assert binary.returncode == 3, binary.stdout

    reserved = run_cli(["--stdin"], reserved_pm_section_diff())
    assert reserved.returncode == 2, reserved.stdout


def test_explain_prints_the_four_questions_and_exits_zero():
    result = run_cli(["--explain"])
    assert result.returncode == 0
    for word in ("authority", "secret", "spend", "account"):
        assert word in result.stdout
    assert "0  clear" in result.stdout and "3  undecided" in result.stdout


def test_a_command_that_could_not_run_is_not_a_verdict_about_the_diff():
    result = run_cli(["--range", "no-such-rev-exists-here...HEAD"])
    assert result.returncode == ca.EXIT[ca.ERROR] == 1
    assert "not a verdict" in result.stderr


def test_json_carries_the_verdict_and_the_exit_code_together():
    result = run_cli(["--stdin", "--json"], diff("README.md", [(1, [" a", "+b"])]))
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["verdict"] == ca.CLEAR and payload["exit"] == 0


def test_an_empty_diff_is_clear_and_says_it_read_nothing():
    result = ca.examine("")
    assert result["verdict"] == ca.CLEAR and result["files"] == []
    assert "no readable change" in ca.render(result)


# ------------------------------------------------------------------- authority

def reserved_pm_section_diff():
    """One changed line inside `docs/standards/pm.md` §21, which §21 reserves."""
    anchor = section_line("docs/standards/pm.md", "21")
    return diff("docs/standards/pm.md",
                [(anchor + 2, [" a context line inside the section",
                               "+one more sentence in this section"])])


def test_a_changed_line_inside_a_section_21_reserves_is_reserved():
    result = ca.examine(reserved_pm_section_diff())
    assert result["verdict"] == ca.RESERVED
    finding = result["findings"][0]
    assert finding["question"] == "authority"
    assert "§21 names as the owner's" in finding["because"]


def test_the_reserved_sections_are_the_ones_section_21_names():
    """§21's own words: that section, §10, §19, and the PM charter's grant."""
    assert ca.RESERVED_SECTIONS["docs/standards/pm.md"] == {"10", "19", "21"}
    assert ca.RESERVED_SECTIONS["prompts/pm-agent.md"] == {"5"}
    for sid in sorted(ca.RESERVED_SECTIONS["docs/standards/pm.md"]):
        anchor = section_line("docs/standards/pm.md", sid)
        text = diff("docs/standards/pm.md",
                    [(anchor + 2, [" context", "+a sentence"])])
        assert verdict(text) == ca.RESERVED, f"§{sid} should be reserved"


def test_a_mechanical_edit_inside_the_pm_charters_grant_is_still_reserved():
    """Reserved by section is categorical, and deliberately so.

    The line this is modelled on is a real one: #455 changed how the PM reads
    a dispatch flag, inside `prompts/pm-agent.md` §5. It moves no authority by
    any reading. It is reserved anyway, because §21 names the section and the
    cheap error is the one this tool is allowed to make.
    """
    anchor = section_line("prompts/pm-agent.md", "5")
    text = diff("prompts/pm-agent.md",
                [(anchor + 3, [" context", "+Read it from your environment."])])
    assert verdict(text) == ca.RESERVED


def test_a_heading_that_declares_itself_a_grant_is_reserved_without_a_table():
    """A seat that gains an authority section tomorrow is covered today."""
    for heading in ("## 9. The grant", "## 4. Dispatch authority",
                    "## 7. Permissions"):
        text = diff("prompts/engineer-agent.md",
                    [(10, [f" {heading}", "+You may merge your own pull request."])])
        assert verdict(text) == ca.RESERVED, heading


def test_a_charter_line_that_rules_the_owner_is_not_the_seats_own_authority():
    """The regression, and the whole reason this reads lines instead of paths.

    INC-2026-10-24: a twelve-charter edit, correctly identified as a charter,
    held under a repealed carve-out, and it moved no seat's authority at all.
    """
    text = diff("prompts/engineer-agent.md",
                [(30, [" ## 3. Act",
                       "+The owner must merge every charter change herself.",
                       "+The PM seat may never approve one on her behalf."])])
    assert verdict(text) == ca.CLEAR


def test_a_rule_about_the_seat_itself_with_no_citation_is_undecided():
    text = diff("prompts/engineer-agent.md",
                [(30, [" ## 3. Act",
                       "+You may merge your own pull request whenever CI is green."])])
    result = ca.examine(text)
    assert result["verdict"] == ca.UNDECIDED
    assert "may be granting rather than restating" in result["findings"][0]["because"]


def test_the_same_rule_is_clear_when_its_hunk_cites_a_rule_this_tree_carries():
    """Derivative: a line restating a rule reports an authority, it moves none."""
    text = diff("prompts/engineer-agent.md",
                [(30, [" ## 3. Act",
                       "+You may merge your own pull request whenever CI is green,",
                       "+which is docs/standards/pm.md §10's grant and not this file's."])])
    assert verdict(text) == ca.CLEAR


def test_a_citation_that_does_not_resolve_in_this_tree_does_not_exempt():
    """Presence is not enough: the exemption rests on the citation being real."""
    text = diff("prompts/engineer-agent.md",
                [(30, [" ## 3. Act",
                       "+You may merge your own pull request whenever CI is green,",
                       "+under docs/standards/no-such-standard.md and INC-1999-01-01-invented."])])
    assert verdict(text) == ca.UNDECIDED


def test_resolving_citations_reads_the_tree_rather_than_the_neighbourhood():
    real = ca.resolving_citations("see docs/standards/pm.md for this", "prompts/x.md")
    assert "docs/standards/pm.md" in real
    assert ca.resolving_citations("see docs/standards/invented.md", "prompts/x.md") == []


def test_a_sentence_that_only_reflowed_across_the_wrap_did_not_move():
    """Charters are hard-wrapped, so this is the ordinary case."""
    text = diff("prompts/engineer-agent.md", [(30, [
        " ## 3. Act",
        "-You may merge your own pull request whenever CI is",
        "-green.",
        "+You may merge your own pull request",
        "+whenever CI is green.",
    ])])
    assert verdict(text) == ca.CLEAR


def test_rules_that_moved_drops_the_sentences_that_only_changed_wrapping():
    hunks, _, _ = ca.parse_diff(diff("prompts/engineer-agent.md", [(30, [
        "-One rule, wrapped one way and",
        "-no other.",
        "+One rule, wrapped",
        "+one way and no other.",
        "+A rule that is genuinely new.",
    ])]))
    moved = ca.rules_that_moved(hunks[0])
    assert moved == ["A rule that is genuinely new."]


def test_only_a_law_file_can_move_authority_at_all():
    """The same sentence, in a file that is not law, decides nothing."""
    sentence = "+You may merge your own pull request whenever CI is green."
    for path in ("README.md", "docs/notes/scratch.md", "site/app/page.tsx"):
        text = diff(path, [(10, [" context", sentence])])
        assert verdict(text) == ca.CLEAR, path
    law = diff("prompts/engineer-agent.md", [(10, [" context", sentence])])
    assert verdict(law) == ca.UNDECIDED


def test_a_line_in_a_reserved_file_whose_section_cannot_be_placed_is_undecided():
    """`docs/standards/pm.md` has sections this tool must place a line inside.

    A change above the first heading cannot be placed, and an unplaceable line
    in a file that carries reserved sections is not a clear.
    """
    text = diff("docs/standards/pm.md", [(1, ["+a line above every heading"])])
    assert verdict(text) == ca.UNDECIDED


def test_a_deleted_law_file_is_undecided_because_removing_a_rule_moves_one():
    law = diff("prompts/engineer-agent.md", [(1, ["-a rule"])], delete=True)
    assert verdict(law) == ca.UNDECIDED
    prose = diff("docs/notes/scratch.md", [(1, ["-a note"])], delete=True)
    assert verdict(prose) == ca.CLEAR


def test_a_change_this_tool_cannot_read_is_never_a_clear():
    """Observed on #435, whose diff is screenshots."""
    result = ca.examine(diff("docs/design/reviews/after.png", [], binary=True))
    assert result["verdict"] == ca.UNDECIDED
    assert result["findings"][0]["section"] == "(unreadable)"


# ---------------------------------------------------------------------- secrets

def test_a_credential_shaped_literal_in_an_added_line_is_reserved():
    fake = "ghp_" + "A" * 25          # built here so no scanner matches the file
    text = diff("pipeline/weekly.py", [(10, [" import os", f'+TOKEN = "{fake}"'])])
    result = ca.examine(text)
    assert result["verdict"] == ca.RESERVED
    assert "secret" in questions(text)


def test_a_credential_shaped_value_assigned_to_a_secret_shaped_name_is_reserved():
    for value in ("AbCdEfGhIjKlMnOpQrStUvWx",                      # letters only
                  "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",      # forty hex
                  "sk-ant-api03-AAAAAAAAAAAAAAAAAAAA"):            # dashes
        text = diff("pipeline/weekly.py",
                    [(10, [" import os", f'+MY_API_KEY = "{value}"'])])
        assert verdict(text) == ca.RESERVED, value


def test_a_long_alphanumeric_credential_is_not_mistaken_for_a_setting():
    """Fixed in this run, and the regression is a false `clear`.

    `SETTING_VALUE` is case-insensitive and ends in `[A-Z][A-Z0-9_]{2,}`, so it
    fullmatches any single word of letters, digits and underscores at any
    length. Checked before the credential shape, it cleared a forty-character
    hex token assigned to `*_API_KEY`. The order is now the other way round,
    and the cost of that is a long constant reading reserved, which is one
    merge of waiting rather than an authority breach.
    """
    token = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
    assert ca.SETTING_VALUE.fullmatch(token), "the overlap this guards is still there"
    text = diff("pipeline/weekly.py", [(10, [" import os", f'+GH_TOKEN = "{token}"'])])
    assert verdict(text) == ca.RESERVED


def test_reading_a_secret_is_not_writing_one():
    """Every seat run reads secrets. If reads were reserved, nothing would ship."""
    for line in ('+    token = os.environ["GITHUB_TOKEN"]',
                 "+    key = os.getenv('GROQ_API_KEY')",
                 "+  token: ${{ secrets.ANTHROPIC_API_KEY }}",
                 "+    secret = modal.Secret.from_name('alexandria-tokens')"):
        text = diff("pipeline/weekly.py", [(10, [" import os", line])])
        assert verdict(text) == ca.CLEAR, line


def test_a_secret_name_in_prose_is_a_name_and_not_a_write():
    """Charters are allowed to name secrets, and they do."""
    text = diff("docs/agents/runtime-changes.md",
                [(10, [" context", "+ANTHROPIC_API_KEY: the name only, never the value"])])
    assert verdict(text) == ca.CLEAR


def test_a_permissions_setting_is_a_setting_even_when_its_name_says_token():
    text = diff("pipeline/weekly.py", [(10, [" permissions:", "+  id-token: write"])])
    assert verdict(text) == ca.CLEAR


def test_an_unreadable_assignment_in_a_file_that_can_act_is_undecided():
    text = diff("pipeline/weekly.py",
                [(10, [" context", '+MY_API_KEY = "a value with spaces in it"'])])
    result = ca.examine(text)
    assert result["verdict"] == ca.UNDECIDED
    assert "secret" in questions(text)


# ------------------------------------------------------------- spend and account

def test_a_price_in_prose_spends_nothing():
    """Otherwise `docs/finance/` would be one long reserved."""
    for line in ("+The lifetime tier is $200.00, bought once.",
                 "+Steady-state cost is $0 and the issue costs $0.1628 a run."):
        text = diff("docs/finance/model.md", [(10, [" context", line])])
        assert verdict(text) == ca.CLEAR, line


def test_a_price_in_a_file_that_can_act_is_undecided():
    text = diff("pipeline/checkout.py",
                [(10, [" context", '+monthly_price = "$20.00 a month"'])])
    result = ca.examine(text)
    assert result["verdict"] == ca.UNDECIDED
    assert "spend" in questions(text)


def test_a_bare_dollar_one_is_a_shell_positional_and_not_a_dollar():
    text = diff("pipeline/deploy.sh", [(10, [" context", '+echo "$1 deployed"'])])
    assert verdict(text) == ca.CLEAR


def test_opening_an_account_in_a_file_that_can_act_is_undecided():
    text = diff("pipeline/checkout.py",
                [(10, [" context", "+    customer = polar.customers.create(email=email)"])])
    result = ca.examine(text)
    assert result["verdict"] == ca.UNDECIDED
    assert "account" in questions(text)


def test_describing_an_account_in_prose_opens_none():
    text = diff("docs/decisions.md",
                [(10, [" context", "+The owner will create an account at Polar herself."])])
    assert verdict(text) == ca.CLEAR


# ------------------------------------------------------------ the fail-closed direction

def test_reserved_outranks_undecided_outranks_clear():
    assert ca.RANK[ca.RESERVED] > ca.RANK[ca.UNDECIDED] > ca.RANK[ca.CLEAR]


def test_one_reserved_line_decides_a_diff_that_is_otherwise_undecided():
    text = reserved_pm_section_diff() + diff("docs/x.png", [], binary=True)
    assert verdict(text) == ca.RESERVED


def test_one_undecided_line_decides_a_diff_that_is_otherwise_clear():
    text = (diff("README.md", [(1, [" a", "+b"])])
            + diff("docs/x.png", [], binary=True))
    assert verdict(text) == ca.UNDECIDED


def test_both_non_zero_verdicts_fail_closed():
    """The only verdict that opens the gate is the one with no finding behind it."""
    for name in (ca.RESERVED, ca.UNDECIDED, ca.ERROR):
        assert ca.EXIT[name] != 0
    assert ca.EXIT[ca.CLEAR] == 0


def test_the_route_a_non_zero_verdict_prints_names_who_reads_next():
    reserved = ca.render(ca.examine(reserved_pm_section_diff()))
    assert "§22" in reserved and "board" in reserved
    undecided = ca.render(ca.examine(diff("docs/x.png", [], binary=True)))
    assert "a reader reads the lines above" in undecided


# ------------------------------------------- the diff shapes this repository emits

def test_a_twelve_charter_mechanical_edit_reads_clear():
    """The whole case, end to end, in the shape #414 actually had.

    Twelve charter files, one mechanical change each, no authority moved. A
    path check calls this the owner's. Reading the lines does not.
    """
    seats = ("engineer", "pm", "exo", "writer", "frontend", "market",
             "okr", "research", "sales", "security", "skill", "finance")
    text = "".join(
        diff(f"prompts/{seat}-agent.md", [(40, [
            " ## 2. Observe",
            "-Read the board with `gh run list` for the fleet's last runs.",
            "+Read the board through `tools/board.py`, because `gh run list` has",
            "+been blind to every agent seat's run since 2026-10-17.",
        ])])
        for seat in seats
    )
    result = ca.examine(text)
    assert result["verdict"] == ca.CLEAR, result["findings"]
    assert len(result["files"]) == 12


def test_a_new_file_with_no_sections_is_read_rather_than_skipped():
    text = diff("tools/new_instrument.py", [(1, [
        "+#!/usr/bin/env python3",
        '+"""A new instrument."""',
    ])], old_path="dev/null")
    assert verdict(text) == ca.CLEAR


def test_this_file_is_pinned_or_covered_so_it_cannot_report_nothing_silently():
    """The defect `tools/ci_coverage.py` exists to catch, asserted here too.

    A test file no workflow runs and no pin names is a file that reports
    nothing on the pull request that breaks what it guards.
    """
    pinned = (ROOT / "tests" / "test_ci_coverage.py").read_text()
    assert "tests/test_check_authority.py" in pinned, (
        "add tests/test_check_authority.py to UNCOVERED in "
        "tests/test_ci_coverage.py, with the reason, or wire it into a workflow"
    )
