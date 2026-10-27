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

# The honest one-line issue for a quiet day used to be checked here, against
# `pipeline.weekly.empty_issue()`. That function belongs to the daily cadence,
# which this branch no longer carries, so the floor is asserted against the
# wording itself rather than against a function that is not in the pipeline:
# the gate must pass an honest short issue, or a quiet day would block the send
# instead of reporting itself.
HONEST_EMPTY = (
    "# Nothing worth your time today\n\n"
    "September 20, 2026: today's papers were routine, so there is no issue. "
    "The next one comes tomorrow, and Monday's weekly synthesis covers the "
    "whole week."
)


def test_the_honest_empty_issue_passes_the_gate():
    assert blocking(HONEST_EMPTY, kind="daily") == []


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


# ---------------- the gate inside the send path ----------------
#
# `hold_for_quality` is the policy: which draft is kept and whether it may be
# sent. It takes the second draft as a closure rather than calling the
# generator itself, because finishing a draft means the same title and masthead
# work the first one got and only `weekly()` holds the arguments for that.


def test_a_clean_issue_goes_out_without_a_second_call():
    from pipeline import weekly

    body, model, cleared = weekly.hold_for_quality(
        GOOD, "kimi", "2026-W37 issue", rewrite=_never_called)
    assert cleared is True
    assert body == GOOD
    assert model == "kimi"


def test_a_blocked_issue_is_regenerated_once_and_then_sent():
    from pipeline import weekly

    calls = []

    def rewrite(instructions):
        calls.append(instructions)
        return GOOD, "kimi-second"

    body, model, cleared = weekly.hold_for_quality(
        _blocked(), "kimi", "2026-W37 issue", rewrite=rewrite)
    assert len(calls) == 1
    assert "skeleton-heading" in calls[0]
    assert cleared is True
    assert body == GOOD
    assert model == "kimi-second", "the row has to name whoever actually wrote it"


def test_an_issue_that_fails_twice_is_held_and_still_returned():
    from pipeline import weekly

    blocked = _blocked()
    worse = blocked.replace("## Last week's", "## Left behind\n\n## Last week's")
    body, model, cleared = weekly.hold_for_quality(
        blocked, "kimi", "2026-W37 issue", rewrite=lambda _: (worse, "kimi-second"))
    assert cleared is False
    assert body == blocked, "the second draft was worse, so the first is kept"
    assert model == "kimi"


def test_a_better_but_still_blocked_rewrite_is_kept_and_still_held():
    """Fewer blocking findings is the better issue to store, and still not one
    to send. The owner reads the stored body, so it should be the best draft
    the run produced."""
    from pipeline import weekly

    blocked = _blocked().replace("## Last week's", "## Trailblazing\n\n## Last week's")
    better = _blocked()
    body, model, cleared = weekly.hold_for_quality(
        blocked, "kimi", "2026-W37 issue", rewrite=lambda _: (better, "kimi-second"))
    assert cleared is False
    assert body == better
    assert model == "kimi-second"


def test_an_issue_with_no_second_try_is_held_rather_than_sent():
    """The short edition reaches the gate with no rewrite: it is already the
    degraded print, and asking the same model list again costs the run."""
    from pipeline import weekly

    blocked = _blocked()
    body, model, cleared = weekly.hold_for_quality(
        blocked, "kimi", "2026-W37 issue", rewrite=None)
    assert cleared is False
    assert body == blocked


def test_a_rewrite_that_raises_keeps_the_first_draft_and_holds():
    from pipeline import weekly

    def explode(_instructions):
        raise RuntimeError("every model in the press's fallback list failed")

    blocked = _blocked()
    body, model, cleared = weekly.hold_for_quality(
        blocked, "kimi", "2026-W37 issue", rewrite=explode)
    assert cleared is False
    assert body == blocked


def test_a_broken_gate_never_costs_the_issue(monkeypatch):
    """An unwritten newsletter is worse than an unchecked one."""
    from pipeline import weekly

    def explode():
        raise RuntimeError("no module named check_digest_quality")

    monkeypatch.setattr(weekly, "quality", explode)
    body, model, cleared = weekly.hold_for_quality(
        "# anything\n", "kimi", "2026-W37 issue", rewrite=_never_called)
    assert cleared is True
    assert body == "# anything\n"


def test_the_gate_travels_with_the_job():
    """A checker that is not in the image is a checker the scheduled run cannot
    open, which is the whole failure docs/agents/registers.md describes."""
    source = (REPO / "pipeline" / "weekly.py").read_text(encoding="utf-8")
    assert 'add_local_file("tools/check_digest_quality.py"' in source


def test_the_corrections_are_counted_against_the_request():
    """They ride in the system prompt, so every size check in write_digest has
    to see them. Incident 22 is an unbudgeted prompt growing past the ceiling."""
    import inspect

    from pipeline import weekly

    source = inspect.getsource(weekly.write_digest)
    assert "system = prompt + corrections" in source
    assert "guard.check_request(system" in source
    assert "call_model(model, system" in source
    assert "fit_payload(copy.deepcopy(payload), system" in source


def _blocked():
    """A tier-four issue with one slot label put back into a heading, which is
    the gate's clearest blocking rule."""
    return GOOD.replace(
        "## Counting partial credit turns out to be the whole trick",
        "## Trailblazing")


def _never_called(*args, **kwargs):
    raise AssertionError("the generator was called when it should not have been")


# ---------------- the word-edge class ----------------

# Filed 2026-09-24 as item 3 of "The quality gate passes the issue the owner
# rejected", escalated at thirty days on 2026-10-24 after a later run
# rediscovered it and described it as new. Three gates in this repository had
# the same defect, a pattern matching inside a word instead of at its edge, so
# the tests below are written against the class rather than against the two
# lines of 2026-W39 that happened to expose it.

# Her close, mandated 2026-09-30 and required in every issue by canon law 10.
# The gate warned on it forever, because "every" contains "very", so the one
# finding an issue could never clear was the one the issue was required to
# carry.
MANDATED_CLOSE = "Accelerate every builder and agent to frontier speed."


def details(body, rule):
    return [f.detail for f in findings(body) if f.rule == rule]


def test_the_close_the_owner_mandated_raises_nothing():
    assert findings(f"# T\n\n{MANDATED_CLOSE}\n") == []


def test_the_issue_the_gate_has_actually_read_loses_both_false_warnings():
    """2026-W39 is the only issue this gate has ever been run against. It
    returned seven warnings and two of the seven were the substring bug."""
    body = (REPO / "site" / "content" / "issues" / "2026-W39.md").read_text(encoding="utf-8")
    found = findings(body)
    assert details(body, "empty-intensifier") == []
    assert {f.rule for f in found} == {"bare-number"}, "the rest of the gate is unchanged"


def test_no_listed_term_fires_from_inside_a_longer_word():
    """The class guard. Every literal in the four lists, buried behind one
    letter so its left edge is gone, must raise nothing.

    The right edge is deliberately left open, so this does not assert the
    mirror case: a listed word's inflections are the same defect as the word
    and have to keep matching.
    """
    lists = (gate.SLOP_ALWAYS, gate.SLOP_USUALLY, gate.HEDGES, gate.INTENSIFIERS)
    for terms in lists:
        for term in terms:
            buried = f"# T\n\nThe x{term} of it, measured against the baseline.\n"
            hits = [f for f in findings(buried) if term in f.detail]
            assert hits == [], f"x{term} matched {term!r} inside a word: {hits}"


def test_every_listed_term_still_fires_standing_on_its_own():
    """The other half, so the guard above cannot be satisfied by a gate that
    has stopped looking."""
    for terms in (gate.SLOP_ALWAYS, gate.SLOP_USUALLY, gate.HEDGES, gate.INTENSIFIERS):
        for term in terms:
            body = f"# T\n\nThe {term} of it, measured against the baseline.\n"
            hits = [f for f in findings(body) if term in f.detail]
            assert hits, f"{term!r} on its own raised nothing"


def test_the_always_slop_still_blocks_on_an_inflection():
    for inflected in ("delves", "delved", "revolutionized", "supercharged", "realms"):
        body = GOOD.replace("against the same benchmark", f"and it {inflected} the loss")
        assert "slop-lexicon" in rules(blocking(body)), inflected


def test_an_intensifier_at_the_end_of_a_line_is_caught_now():
    """The recall half of the same defect: the trailing space the terms used
    to carry was standing in for a word boundary, and a line that ends on the
    word has no space after it."""
    assert details("# T\n\nThe gain is very\nlarge.\n", "empty-intensifier") == ["'very'"]
