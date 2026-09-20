"""The pre-send gate, tested against the one issue that actually shipped.

Two halves. The first proves the gate catches what the owner and the ban list
caught by hand in 2026-W37, so a repeat of that issue cannot leave the
pipeline. The second proves an issue written to the tier passes clean, which
matters more than it looks: a gate nobody can satisfy does not raise quality,
it stops the newsletter.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "tools"))

import check_digest_quality as gate  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
SHIPPED_ISSUE = REPO / "site" / "content" / "issues" / "2026-W37.md"

# What a tier-four issue looks like: a title that is the finding, a first
# screen that says what is inside, headings written from the day's news, one
# link per item, and every item ending on the judgment rather than the source.
GOOD = """# Dense rewards beat binary ones by fifteen points

*The latest in AI research, read in full.*

Today: a reward signal that counts what a program got right instead of
whether it passed, and a retraction of last week's ceiling on agent
planning.

## Counting partial credit turns out to be the whole trick

- **A reward that counts passing assertions lifts task resolution from 49.4
  percent to 64.0 percent, while a pass-fail reward never beats the
  supervised baseline at all.**
  The verifier emits one outcome per assertion and the sum becomes the
  reward, so a run that got four of five checks right is no longer scored
  the same as one that got none.
  *Terminal Agent Reinforcement Learning* - https://arxiv.org/abs/2609.11042
  If you are training an agent against a test suite, the cheapest
  improvement available to you this week is to stop throwing away the
  partial credit you already compute.

## Last week's planning ceiling was an artifact of the harness

- The 23.9 percent figure we reported on agent planning came from a
  scaffold, not from the model. An expert-written reference implementation
  of the same task reaches 82.2 percent, against the same benchmark.
  *Reference implementations for agent planning* -
  https://arxiv.org/abs/2609.08404
  Treat last week's number as retired. If you quoted it in a design
  document, the ceiling you were planning against does not exist.
"""


def findings(body, kind="weekly"):
    return gate.check(body, kind)


def blocking(body, kind="weekly"):
    return [f for f in findings(body, kind) if f.level == gate.BLOCK]


def rules(found):
    return {f.rule for f in found}


# ---------------- the shipped issue ----------------

def test_the_one_issue_that_shipped_would_not_send_today():
    """2026-W37 broke the ban list in ways the owner had to report herself.
    Every one of those defects is a blocking finding now."""
    body = SHIPPED_ISSUE.read_text(encoding="utf-8")
    caught = rules(blocking(body))
    assert "skeleton-heading" in caught      # ban list 20, reported twice
    assert "typesetter-punctuation" in caught  # ban list 13, 87 of them
    assert "internal-vocabulary" in caught   # ban list 14, "three supports"
    assert "ends-on-citation" in caught      # ban list 25, every item


def test_the_shipped_issue_also_raises_the_judgment_warnings():
    body = SHIPPED_ISSUE.read_text(encoding="utf-8")
    warned = rules([f for f in findings(body) if f.level == gate.WARN])
    assert "uniform-length" in warned        # ten bullets cut to one shape
    assert "no-contents" in warned           # ban list 23
    assert "citation-per-item" in warned     # the traction section has no links


# ---------------- an issue written to the tier ----------------

def test_an_issue_written_to_the_tier_passes_clean():
    """The gate must be satisfiable. If this test ever fails, the gate is
    about to stop the newsletter rather than improve it."""
    assert blocking(GOOD) == []


def test_the_tier_issue_raises_no_citation_or_contents_warnings():
    warned = rules([f for f in findings(GOOD) if f.level == gate.WARN])
    assert "citation-per-item" not in warned
    assert "no-contents" not in warned
    assert "ends-on-citation" not in warned


# ---------------- rule by rule ----------------

def test_a_slot_label_as_a_heading_blocks():
    caught = rules(blocking(GOOD.replace(
        "## Counting partial credit turns out to be the whole trick",
        "## Trailblazing")))
    assert "skeleton-heading" in caught


def test_a_date_in_the_headline_blocks():
    caught = rules(blocking(GOOD.replace(
        "# Dense rewards beat binary ones by fifteen points",
        "# Dense rewards beat binary ones [September 14-20, 2026]")))
    assert "date-in-title" in caught


def test_the_typesetters_hyphen_blocks_even_though_it_looks_identical():
    caught = rules(blocking(GOOD.replace("pass-fail", "pass‑fail")))
    assert "typesetter-punctuation" in caught


def test_a_supports_count_blocks_in_words_as_well_as_digits():
    for phrasing in ("gaining three independent supports",
                     "with 2 supports", "supported by three citations"):
        body = GOOD.replace("against the same benchmark", phrasing)
        assert "internal-vocabulary" in rules(blocking(body)), phrasing


def test_the_week_code_is_internal_vocabulary_too():
    caught = rules(blocking(GOOD.replace("Today:", "This is 2026-W38. Today:")))
    assert "internal-vocabulary" in caught


def test_an_item_that_ends_on_its_link_blocks():
    body = GOOD.replace(
        """  If you are training an agent against a test suite, the cheapest
  improvement available to you this week is to stop throwing away the
  partial credit you already compute.
""", "")
    assert "ends-on-citation" in rules(blocking(body))


def test_the_always_slop_blocks_and_the_maybe_slop_only_warns():
    assert "slop-lexicon" in rules(blocking(GOOD.replace("trick", "paradigm shift")))
    warned = [f for f in findings(GOOD.replace("cheapest", "most robust"))
              if f.rule == "slop-lexicon"]
    assert warned and all(f.level == gate.WARN for f in warned)


def test_a_number_with_nothing_beside_it_warns():
    body = GOOD.replace(
        "from 49.4\n  percent to 64.0 percent, while a pass-fail reward never beats the\n"
        "  supervised baseline at all.",
        "to 64.0 percent.")
    assert "bare-number" in {f.rule for f in findings(body)}


# ---------------- the daily's own floor ----------------

def test_the_honest_empty_issue_passes_the_gate():
    """pipeline.weekly.empty_issue() has to survive its own gate, or a quiet
    day would block the send instead of reporting itself."""
    from pipeline.weekly import empty_issue

    assert blocking(empty_issue("September 20, 2026"), kind="daily") == []


def test_a_daily_that_is_neither_an_issue_nor_the_empty_line_blocks():
    caught = rules(blocking("# Something happened\n\nA sentence.\n", kind="daily"))
    assert "daily-too-short" in caught


def test_a_daily_the_length_of_a_weekly_warns():
    body = GOOD + ("\n- Another finding entirely, at length. " * 60)
    assert "daily-too-long" in {f.rule for f in findings(body, kind="daily")}


# ---------------- plumbing ----------------

def test_indented_lines_belong_to_the_item_above_them():
    items = gate.parse_items(GOOD)
    assert len(items) == 2
    assert "partial credit you already compute" in "\n".join(items[0].lines)


def test_corrections_speak_to_the_generator_not_to_the_log():
    body = GOOD.replace("## Counting partial credit turns out to be the whole trick",
                        "## Trailblazing")
    text = gate.corrections(gate.check(body))
    assert "rejected by the pre-send quality gate" in text
    assert "skeleton-heading" in text
    assert gate.corrections([]) == ""


def test_corrections_never_carry_warnings_into_the_retry():
    """A retry that chases warnings burns the one extra call on judgment
    calls the regex cannot make."""
    body = GOOD.replace("cheapest", "most robust")   # a warning, not a block
    assert gate.corrections(gate.check(body)) == ""


def test_the_report_groups_by_rule_rather_than_printing_every_hit():
    body = SHIPPED_ISSUE.read_text(encoding="utf-8")
    text = gate.report(gate.check(body), "2026-W37")
    assert "typesetter-punctuation (49x" in text
    assert text.count("non-breaking hyphen") <= gate.EXAMPLES_PER_RULE
