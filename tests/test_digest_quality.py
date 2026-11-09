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
    # `one-shape` is excluded because it is the only rule here that is about
    # the whole page rather than about the text in front of it, and this body
    # is a two-block fragment rather than an issue. Every real body the press
    # hands the gate carries its items, and the fragment carrying no list is a
    # fact about the fixture. Narrowed rather than dropped: the close itself
    # still has to raise nothing.
    assert [f for f in findings(f"# T\n\n{MANDATED_CLOSE}\n")
            if f.rule != "one-shape"] == []


def test_the_issue_the_gate_has_actually_read_loses_both_false_warnings():
    """2026-W39 is the only issue this gate has ever been run against. It
    returned seven warnings and two of the seven were the substring bug.

    `one-shape` joined that set on 2026-11-09 and it is a true finding rather
    than a loosened assertion: `docs/voice/check_voice.py devices` reaches the
    same verdict on this same file, "no list and no written turn". It is pinned
    here on purpose, because this is the issue the product is serving and the
    count is the evidence for promoting the rule from `warn` to `block`.
    """
    body = (REPO / "site" / "content" / "issues" / "2026-W39.md").read_text(encoding="utf-8")
    found = findings(body)
    assert details(body, "empty-intensifier") == []
    assert {f.rule for f in found} == {"bare-number", "one-shape"}, \
        "the rest of the gate is unchanged"


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


# ---------------- ban list 19, 20: the derived heading ban ----------------
#
# The writer seat measured on 2026-11-01 that this gate's heading ban and the
# voice canon's shared no phrase at all, and routed the repair here because
# `tools/` is pipeline code its charter may not write. The tests below are the
# half that keeps the repair true. The first one is the important one: it reads
# the canon's own asserted cases and requires this gate to agree with every one
# of them, so the two lists cannot drift apart again without a red test.

def _canon():
    """`docs/voice/check_voice.py`, loaded by path because `docs/` is not a package."""
    import importlib.util

    path = REPO / "docs" / "voice" / "check_voice.py"
    spec = importlib.util.spec_from_file_location("check_voice_for_gate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_pre_send_gate_agrees_with_the_canon_on_every_asserted_heading():
    """The anti-drift test, and the reason this repair is not a ninth hand entry.

    `SLOT_HEADING_CASES` in the canon is the writer seat's statement of what a
    framework heading is, maintained by the seat that owns the ban's wording.
    This asserts the gate that can stop a send reaches the same verdict on all
    of them. Widening the ban there turns this red until the send agrees, which
    is the whole point: two lists maintained by two seats against one rule is
    the drift the repair was filed about.
    """
    canon = _canon()
    disagreed = []
    for fires, heading in canon.SLOT_HEADING_CASES:
        caught = rules(blocking(f"# T\n\n{heading}\n\nsome body text here.\n"))
        hit = "slot-heading" in caught or "skeleton-heading" in caught
        if hit is not fires:
            disagreed.append(("missed" if fires else "fired on", heading))
    assert disagreed == [], f"the send and the canon disagree: {disagreed}"


def test_the_four_headings_that_were_serving_are_blocking_now():
    """The measurement in the ledger entry, as a test.

    Every one of these passed this gate while it was on the site. The first
    three are canon law 12 in its plainest form, the owner's ruling given twice
    and recorded as incident 20.
    """
    for heading in (
        "## What to read",
        "## What fell behind: the assumptions that let agents run unchecked",
        "## What is gaining ground: recursive self-improvement with fewer guardrails",
        "## What is genuinely new: where memory lives and who can pull the plug",
    ):
        assert "slot-heading" in rules(blocking(
            f"# T\n\n{heading}\n\nsome body text here.\n")), heading


def test_the_phrasings_are_read_out_of_the_generator_and_not_kept_here():
    """A derived list cannot drift, so this asserts it is derived.

    The phrasings must come out of `prompts/digest.md`'s own ban paragraph,
    which is the span `check_voice.py slotwords` reads. If a future run pastes
    them into a tuple instead, the intersection check below is what notices.
    """
    dress, complaint = gate.slot_dress()
    assert complaint == "", complaint
    assert dress, "the ban paragraph yielded no phrasings"
    generator = (REPO / "prompts" / "digest.md").read_text(encoding="utf-8")
    span = generator[generator.find(gate.SLOT_BAN_OPEN):
                     generator.find(gate.SLOT_BAN_CLOSE)]
    for phrase in dress:
        assert f'"{phrase}"' in span, f"{phrase!r} is not quoted in the ban itself"


def test_the_two_lists_are_still_disjoint_so_the_floor_is_doing_separate_work():
    """Not a style assertion. The empty intersection is the finding that
    produced this work, and it is why the hand floor is kept rather than
    replaced: the internal names are still worth blocking even though nothing
    prints them."""
    dress, _ = gate.slot_dress()
    assert set(dress).isdisjoint(set(gate.SKELETON_HEADINGS))
    for banned in gate.SKELETON_HEADINGS:
        assert "skeleton-heading" in rules(blocking(
            f"# T\n\n## {banned.title()}\n\nsome body text here.\n")), banned


def test_the_generators_own_worked_heading_for_the_read_slot_still_passes():
    """A gate nobody can satisfy does not raise quality, it stops the
    newsletter. These are the headings law 12 asks for and every one of them
    has to survive the ban."""
    for heading in (
        "## What to read if you have one hour",
        "## What to read when the week has been long",
        "## Three papers for anyone wiring memory or kill switches into production",
        "## Budget-constrained agents can now improve their own harnesses",
    ):
        caught = rules(blocking(f"# T\n\n{heading}\n\nsome body text here.\n"))
        assert "slot-heading" not in caught, heading


def test_a_good_issue_is_still_clean_under_the_new_reading():
    assert blocking(GOOD) == []


def test_one_heading_raises_one_finding_even_when_both_readings_could_fire():
    """The floor and the derived reading are separate rules, so a heading that
    matches both would otherwise be reported twice. An issue with one defect
    has one finding."""
    body = "# T\n\n## Read these yourself\n\nsome body text here.\n"
    assert len([f for f in blocking(body)
                if f.rule in ("skeleton-heading", "slot-heading")]) == 1


def test_a_generator_it_cannot_read_warns_rather_than_passing_in_silence():
    """The confident zero, refused. A gate reporting no defects because it
    could not read its own rule is the class this repository keeps filing, so
    the unreadable case is a finding and the hand floor still applies."""
    saved = gate.GENERATOR_PATHS
    gate.GENERATOR_PATHS = (REPO / "prompts" / "no-such-generator.md",)
    try:
        dress, complaint = gate.slot_dress()
        assert dress == ()
        assert "only the hand floor" in complaint
        findings_ = findings("# T\n\n## What to read\n\nsome body text here.\n")
        assert "slot-ban-unreadable" in [f.rule for f in findings_]
        assert [f for f in findings_ if f.rule == "slot-ban-unreadable"
                ][0].level == gate.WARN
        # and the floor is untouched by the derived half being blind
        assert "skeleton-heading" in rules(blocking(
            "# T\n\n## Trailblazing\n\nsome body text here.\n"))
    finally:
        gate.GENERATOR_PATHS = saved


def test_the_image_the_press_runs_carries_the_generator_this_rule_reads():
    """The ImportError-on-the-next-cron class, as a merge-time check.

    `pipeline/weekly.py` builds the press's image from a hand list of local
    files, and this rule now reads one of them at send time. The same list is
    why `tests/test_law8_url.py` exists. `/root/prompts/digest.md` is the
    container path in `GENERATOR_PATHS`; if that line ever leaves the image,
    the derived half of this ban degrades to a warning in a Modal log and this
    test is what says so first.
    """
    weekly = (REPO / "pipeline" / "weekly.py").read_text(encoding="utf-8")
    assert '.add_local_file("prompts/digest.md", "/root/prompts/digest.md")' in weekly
    assert pathlib.Path("/root/prompts/digest.md") in gate.GENERATOR_PATHS


# ---------------- canon law 14: the shape of the page ----------------
#
# The second rule the writer seat routed here on 2026-11-01, filed as "Law 14's
# one-shape failure cannot block a send, so the one thing she rejected twice
# ships green". The gate had eight blocking rules and none of them measured the
# shape of the page.

def test_a_page_of_one_shape_is_named_before_the_send():
    body = ("# A finding stated as a sentence\n\n*The latest in AI research.*\n\n"
            "## Counting partial credit turns out to be the trick\n\n"
            + ("One column of prose, stated at length and without a turn in it, "
               "which is the page she read and rejected. " * 8) + "\n")
    found = [f for f in findings(body) if f.rule == "one-shape"]
    assert len(found) == 1
    assert found[0].level == gate.BLOCK


def test_a_list_is_one_of_the_two_devices_that_answers_it():
    body = ("# A finding stated as a sentence\n\n"
            "## Counting partial credit turns out to be the trick\n\n"
            "- **The reward counts passing assertions.**\n"
            "- **The baseline never beats supervised training.**\n")
    assert [f for f in findings(body) if f.rule == "one-shape"] == []


def test_a_written_turn_inside_a_section_is_the_other_one():
    body = ("# A finding stated as a sentence\n\n"
            "## Counting partial credit turns out to be the trick\n\n"
            "One column of prose, stated at length.\n\n"
            "### Where this leaves a builder\n\n"
            "The turn, which is the second device law 14 names.\n")
    assert [f for f in findings(body) if f.rule == "one-shape"] == []


def test_a_heading_is_not_a_device_and_neither_is_a_standalone_line():
    """The two shapes every issue carries anyway. If either answered this rule,
    no artifact the press can produce could ever reach it, which is the
    blindness `check_voice.py` recorded one level up for the citation line."""
    body = ("# A finding stated as a sentence\n\n## A heading\n\n"
            "## Another heading\n\n*Short standalone line.*\n\n"
            + ("Prose at length, without a list and without a turn. " * 10) + "\n")
    assert [f for f in findings(body) if f.rule == "one-shape"] != []


def test_the_pre_send_gate_and_the_canon_agree_on_the_served_issue():
    """Two commands, one law, one verdict.

    `docs/voice/check_voice.py devices` prints "FAIL 2026-W39 no list and no
    written turn". A gate that could stop a send and reached the other answer
    on the same page would be the two-vocabularies defect this day's work was
    filed about, one law over.
    """
    canon = _canon()
    issue = REPO / "site" / "content" / "issues" / "2026-W39.md"
    body = issue.read_text(encoding="utf-8")
    kinds = canon.shapes([b for b in __import__("re").split(r"\n\s*\n", body)
                          if b.strip() and canon.written_here(b)])
    canon_fails = not [k for k in ("list", "turn") if kinds.get(k)]
    gate_fails = bool([f for f in findings(body) if f.rule == "one-shape"])
    assert canon_fails == gate_fails is True


def test_the_shape_rule_can_hold_a_send_and_says_what_to_do_about_it():
    """`block` rather than `warn`, which was a judgment and is pinned here.

    The generator states law 14 as "A hard gate" that "can fail an issue by
    itself", and `check_voice.py ungated` counts BLOCK rules only, so a warning
    would have left this row UNGATED while looking like a repair in the diff.

    The second assertion is the half that makes blocking defensible rather than
    merely strict: a blocking finding is handed to the generator as its one
    retry instruction, so the detail has to be the move to make and not a
    complaint about the page.
    """
    body = "# T\n\n## A heading\n\n" + ("Prose at length. " * 30) + "\n"
    one_shape = [f for f in blocking(body) if f.rule == "one-shape"]
    assert one_shape and all(f.level == gate.BLOCK for f in one_shape)
    instruction = gate.corrections(findings(body))
    assert "one-shape" in instruction
    assert "genuinely parallel" in instruction and "written turn" in instruction


def test_the_served_issue_is_held_by_this_rule_and_that_is_the_point():
    """Stated as a test because it is the cost of the change rather than a
    side effect of it.

    2026-W39 is the edition the archive treats as cleanest and it is the one
    this rule holds. The generator mandates the shape it lacks, "Bullets where
    the results are parallel", so this is a deviation from the instructions
    rather than a rule nothing can meet, and the body is written to the
    digests table whether or not the email goes (`hold_for_quality`).
    """
    body = (REPO / "site" / "content" / "issues" / "2026-W39.md").read_text(encoding="utf-8")
    assert [f.rule for f in blocking(body)] == ["one-shape"]


def test_the_tier_is_reachable_so_the_rule_is_not_unsatisfiable():
    """The counter-check every rule in this file owes: a gate nobody can
    satisfy does not raise quality, it stops the newsletter. GOOD is the
    worked tier-four issue and it carries a list."""
    assert [f for f in findings(GOOD) if f.rule == "one-shape"] == []


def test_the_daily_is_not_held_to_the_page_shape():
    """A 150-to-400-word dispatch is not the page law 14 is about, and the
    canon reads weekly issues only."""
    body = "# T\n\n" + ("A short dispatch, stated plainly. " * 12) + "\n"
    assert [f for f in findings(body, kind="daily") if f.rule == "one-shape"] == []


def test_a_wrapped_list_item_is_a_list_here_even_though_the_canon_scores_it_prose():
    """The one place this gate deliberately reads law 14 differently, pinned so
    the next run does not align it back.

    `check_voice.py shapes` asks whether EVERY row of a block is a bullet. The
    press's mandated item shape is a bold claim wrapped over two or three lines
    with prose and a citation under it, so no item the generator can write
    passes that reading, and the worked tier-four issue below scores `list: 0`
    against it. Markdown says those rows are the bullet's continuation, so this
    gate asks about the first row. The divergence is the canon's bug and it is
    filed for the writer seat; until it lands, aligning this gate to it would
    make the rule fire on correct issues, which is how a rule gets deleted.
    """
    canon = _canon()
    import re as _re
    blocks = [b for b in _re.split(r"\n\s*\n", GOOD)
              if b.strip() and canon.written_here(b)]
    assert canon.shapes(blocks).get("list", 0) == 0, \
        "the canon has been fixed; this gate can follow it again"
    assert [f for f in findings(GOOD) if f.rule == "one-shape"] == []


def test_the_served_archive_gets_the_verdict_it_has_earned():
    """Both files the repository serves, named rather than summarised, because
    this count is the evidence for the `warn` to `block` promotion."""
    verdicts = {}
    for issue in sorted((REPO / "site" / "content" / "issues").glob("*.md")):
        body = issue.read_text(encoding="utf-8")
        verdicts[issue.stem] = bool(
            [f for f in findings(body) if f.rule == "one-shape"])
    assert verdicts == {"2026-W37": False, "2026-W39": True}, verdicts


def test_the_shape_finding_cites_the_ban_list_entry_that_is_about_it():
    """Every rule in this file cites the entry it enforces, and this one has
    an entry rather than an `n/a`: ban list 49, "One shape for a whole issue",
    whose own specimen is 2026-W39, the file this rule holds."""
    body = "# T\n\n## A heading\n\n" + ("Prose at length. " * 30) + "\n"
    entry = [f.ban_list for f in blocking(body) if f.rule == "one-shape"]
    assert entry == ["49"]
    listed = (REPO / "docs" / "voice" / "ban-list.md").read_text(encoding="utf-8")
    assert "49. One shape for a whole issue" in listed


def test_the_short_edition_is_not_held_by_the_shape_rule():
    """`check_voice.py blockrules` found this one, which is the whole reason
    that command exists.

    It reports every BLOCK rule here against the prompt that writes the
    degraded edition and named this rule UNRULED with the consequence attached,
    "block on the short edition holds the issue". `prompts/digest-short.md`
    asks for no list and no written turn anywhere and says "No other sections",
    so blocking there would hold every degraded week, and that edition exists
    because 2026-10-12 was a week with no issue at all.
    """
    prose = ("# A finding stated as a sentence\n\n"
             + ("One column of prose, at length and without a turn. " * 12) + "\n")
    assert [f.rule for f in blocking(prose)] == ["one-shape"]
    short = prose.replace("\n\n", f"\n\n{gate.SHORT_EDITION_NOTE}\n\n", 1)
    assert [f for f in blocking(short) if f.rule == "one-shape"] == []


def test_the_short_edition_note_is_the_one_the_press_actually_writes():
    """A parity test rather than a parity comment. A comment between two files
    is the class `INC-2026-10-26-a-parity-comment-between-two-files-is-the-
    third-instance-in-two-days` is about: it tells a reader the two agree and
    cannot notice when they stop. The press is the writer of this line, so the
    press's copy is the authority and this gate's copy is the one that has to
    follow it.
    """
    weekly = (REPO / "pipeline" / "weekly.py").read_text(encoding="utf-8")
    assert f'SHORT_EDITION_NOTE = "{gate.SHORT_EDITION_NOTE}"' in weekly


def test_the_short_edition_is_still_held_by_the_rules_it_can_break():
    """The other half, so the scope above cannot be satisfied by a gate that
    stops reading the degraded edition. Only law 14's shape is scoped out."""
    short = ("# A finding stated as a sentence\n\n"
             f"{gate.SHORT_EDITION_NOTE}\n\n"
             "We delve into the tapestry of the realm.\n")
    assert "slop-lexicon" in rules(blocking(short))


def test_the_ban_reaches_the_h1_too_and_that_is_deliberate():
    """Scoped to match the canon exactly, which reads `^#{1,6} `.

    This is worth a test because it is the one way this rule can hold a send on
    something that is not a section heading. A title that opens on `What` and
    breaks to a colon is caught, and it should be: `prompts/digest.md` says the
    title is the week's strongest finding and "not a label for the issue", and
    this file already carries a `colon-title` warning saying the same thing
    about shape. Neither issue the repository serves has such a title, so the
    reading costs nothing live.
    """
    assert "slot-heading" in rules(blocking(
        "# What this week changed: three papers\n\nsome body text here.\n"))
    # And the titles that are actually serving stay clean of this rule.
    for issue in sorted((REPO / "site" / "content" / "issues").glob("*.md")):
        body = issue.read_text(encoding="utf-8")
        title = next(l for l in body.splitlines() if l.startswith("# "))
        assert [f for f in blocking(f"{title}\n\nsome body text here.\n")
                if f.rule == "slot-heading"] == [], title
