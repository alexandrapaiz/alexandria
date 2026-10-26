"""A cited result is not the paper's own result, as tests.

`INC-2026-10-26-a-papers-own-citation-was-wrong-and-the-corpus-carried-it-faithfully`:
`skills/context-window-engineering` rested a shipped delta on one paper's
sentence about two other papers, and the sentence was wrong about both. The
pipeline had no way to tell that row from a measured one, because the evidence
bar asks whether a finding is in a paper and a citation is a finding *about*
another paper.

So the first test here is that sentence, verbatim from the paper, and the four
after it are first-hand sentences that look relational on the surface. The
guard is useless if it cannot separate those two groups, and it is worse than
useless if it only separates them on examples written to be separated.

Run with `python3 -m pytest tests/test_relayed_claims.py -q`.
"""

import re
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))

# Stub modal so distill's non-Modal helpers import without the SDK, the same
# stub tests/test_evidence_grade.py carries and for the same reason.
if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)
    chain = types.SimpleNamespace()
    chain.pip_install = lambda *a, **k: chain
    chain.add_local_file = lambda *a, **k: chain
    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: chain)
    modal.Volume = types.SimpleNamespace(from_name=lambda *a, **k: None)
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

import evidence                                      # noqa: E402
import topics                                        # noqa: E402
import panel_adversary as adv                        # noqa: E402

DISTILL_SOURCE = (ROOT / "pipeline" / "distill.py").read_text()
BACKFILL_SOURCE = (ROOT / "pipeline" / "backfill_grades.py").read_text()
SCHEMA = (ROOT / "db" / "schema.sql").read_text()
PAPER_PROMPT = topics.render((ROOT / "prompts" / "distill.md").read_text())
PRACTICES_PROMPT = topics.render(
    (ROOT / "prompts" / "distill-practices.md").read_text())

PAPER = "arxiv:2609.03430"
POST = "blog:cloudflare-engineering:0f1e2d3c4b5a6978"

# Random Attention's section 5.1, the sentence the incident is about, as the
# evidence field would carry it.
THE_SENTENCE = (
    "Section 5.1 states that the same confound explains the large gaps others "
    "report between random retention and signal-based selection in previous "
    "works (Yuan et al., 2026; Liu et al., 2025): their random baselines "
    "perform poorly since the prompt is lost."
)

# First-hand evidence that reads relational. Every one of these is the source
# measuring something itself, and a guard that fires on them turns real
# results into verification targets.
FIRST_HAND = [
    "Raises SWE-bench Verified from 41.2% to 48.7% across three seeds.",
    "We compare against Zhang et al. and beat that method by 4.2 points on "
    "GSM8K at budget 128.",
    "Prior work used 8-bit quantization; this paper uses 4-bit and measures "
    "48.7% on MMLU.",
    "Trained on the RedPajama corpus of Together et al., reaching 61.8% on "
    "MMLU after 2 epochs.",
    "The authors measured 22.5 points of protection effect in their own "
    "bilateral ablation.",
]

# Second-hand evidence, in the five shapes the markers name.
SECOND_HAND = [
    THE_SENTENCE,
    "According to the Chroma context-rot report, accuracy degrades before the "
    "window is full.",
    "As shown in earlier work, positional bias costs 12 points at 32k.",
    "Prior work finds that random eviction trails scored selection by 4-10% "
    "across budgets.",
    "Yuan et al. report a 4-10% gap between attention-based selection and "
    "random eviction.",
]


# ------------------------------------- the sentence, and the ones like it not

def test_the_sentence_that_cost_a_shipped_skill_is_relayed():
    """The whole reason the grade exists, with the paper's own words in it."""
    assert evidence.grade(PAPER, THE_SENTENCE, True) == "relayed"


@pytest.mark.parametrize("text", FIRST_HAND)
def test_first_hand_evidence_that_reads_relational_is_not_relayed(text):
    """A paper measuring somebody else's method is still measuring it.

    These are the cases that decide whether the guard can ship at all. The
    pairing in `RELAY_MARKERS` is an attribution next to a reporting verb, so
    a bare citation, a bare name and a contrast across a clause boundary all
    stay first-hand.
    """
    assert evidence.relay_markers(text) == [], text
    assert evidence.grade(PAPER, text, True) == "controlled"


@pytest.mark.parametrize("text", SECOND_HAND)
def test_second_hand_evidence_is_relayed_whatever_its_venue(text):
    assert evidence.grade(PAPER, text, True) == "relayed"
    assert evidence.grade(POST, text, True) == "relayed"


def test_the_markers_say_which_phrase_fired():
    """A guard that returns only a boolean cannot be argued with."""
    assert evidence.relay_markers(THE_SENTENCE) == ["says-et-al", "others-say"]
    assert evidence.relay_markers("According to Anthropic's own benchmark") \
        == ["according-to"]
    assert evidence.relay_markers(None) == []
    assert set(evidence.relay_markers(THE_SENTENCE)) <= set(evidence.RELAY_MARKERS)


# ------------------------------------------------- the grade's own precedence

def test_relayed_outranks_every_other_signal():
    """Numbers and venue do not rescue a result the source only passed along.

    The numbers in a relayed row are real numbers from a paper nobody here
    read, so they are the reason to go and check rather than a reason to rank
    the row above one with no numbers at all.
    """
    numbers = "Reported at 48.7% on SWE-bench Verified, a 7.5 point delta."
    assert evidence.grade(PAPER, numbers, True) == "controlled"
    assert evidence.grade(PAPER, numbers, True, None, True) == "relayed"
    assert evidence.grade(POST, numbers, True, None, True) == "relayed"
    assert evidence.grade(PAPER, numbers, False, None, "true") == "relayed"
    assert evidence.grade(PAPER, None, False, None, True) == "relayed"


def test_the_relay_guard_never_clears_the_model_s_answer():
    """One-directional, the same way the measurement guard is.

    The model saw the whole paper and `reads_relayed` sees four sentences, so
    the text may add the mark and may never remove it.
    """
    clean = "Raises SWE-bench Verified from 41.2% to 48.7% across three seeds."
    assert evidence.reads_relayed(clean) is False
    assert evidence.grade(PAPER, clean, True, None, True) == "relayed"
    assert evidence.grade(PAPER, THE_SENTENCE, True, None, False) == "relayed"


def test_relayed_is_last_in_the_grade_order():
    """`GRADES` is strongest first and a relayed row is the weakest there is."""
    assert evidence.GRADES[-1] == evidence.RELAYED
    assert evidence.GRADES.index(evidence.RELAYED) > \
        evidence.GRADES.index(evidence.ANECDOTE)


# --------------------------------------------------- the database accepts it

def test_the_check_constraint_carries_the_fifth_grade():
    match = re.search(
        r"claims_evidence_grade_check\s.*?evidence_grade in\s*\(([^)]*)\)",
        SCHEMA, re.S)
    assert match, "the check constraint is gone from db/schema.sql"
    assert set(re.findall(r"'([a-z_]+)'", match.group(1))) == set(evidence.GRADES)


def test_the_widened_constraint_is_dropped_before_it_is_added():
    """An `if not exists` guard around a widening is a no-op on every live db.

    The four-value constraint is already on every database this schema has
    been applied to, so a guarded add would find it there and leave the old
    list in place. The insert would then fail on the first relayed claim and
    lose the run.
    """
    assert ("alter table claims drop constraint if exists "
            "claims_evidence_grade_check;") in SCHEMA
    drop = SCHEMA.index("drop constraint if exists claims_evidence_grade_check")
    add = SCHEMA.index("add constraint claims_evidence_grade_check")
    assert drop < add, "the constraint is added before the old one is dropped"


def test_the_address_has_a_column():
    assert ("alter table claims add column if not exists attributed_to text;"
            in SCHEMA)


# -------------------------------------------------------- distill carries it

def test_distill_asks_the_model_whose_result_it_is():
    """The grade is only as good as the field the prompt asks for."""
    for prompt, name in ((PAPER_PROMPT, "distill.md"),
                         (PRACTICES_PROMPT, "distill-practices.md")):
        assert "`relayed`" in prompt, f"{name} never asks for relayed"
        assert "`attributed_to`" in prompt, f"{name} never asks who"
        assert '"relayed"' in prompt, (
            f"{name}'s JSON envelope does not carry the field, so a model "
            "that reads only the envelope will never return it")
        assert '"attributed_to"' in prompt, f"{name}'s envelope omits the address"


def test_the_paper_prompt_says_a_paper_s_own_baseline_run_is_first_hand():
    """The distinction the guard's hardest cases turn on, in the prompt too."""
    low = PAPER_PROMPT.lower()
    assert "first-hand" in low
    assert "related-work" in low or "related work" in low


def test_distill_passes_the_model_s_answer_to_the_grader():
    assert 'c.get("relayed")' in DISTILL_SOURCE
    assert 'has_column(conn, "claims", "attributed_to")' in DISTILL_SOURCE
    assert 'cols.append("attributed_to")' in DISTILL_SOURCE


def test_distill_prints_which_phrase_made_a_claim_relayed():
    """A grade assigned against the model's answer is the arguable one."""
    assert "relayed by the guard" in DISTILL_SOURCE
    assert "relay_markers" in DISTILL_SOURCE


def test_distill_prints_the_count_even_when_it_is_zero():
    """Zero, run after run, means the field is not being answered."""
    assert "another work's result as this " in DISTILL_SOURCE


def test_the_backfill_can_only_answer_rows_that_had_no_answer():
    """Reading relay off the text alone is harsher than the live grader.

    That is the direction worth being wrong in, and it costs nothing on an
    existing grade because the backfill's where clause excludes every row that
    has one.
    """
    assert evidence.backfill_grade(PAPER, THE_SENTENCE) == "relayed"
    assert evidence.backfill_grade(PAPER, FIRST_HAND[0]) == "controlled"
    assert "where evidence_grade is null" in BACKFILL_SOURCE


# ------------------------------------------- the panel reviewer names the work

class Row:
    def __init__(self, claim_ids, slug="s"):
        self.claim_ids = claim_ids
        self.slug = slug
        self.path = f"skills/{slug}"
        self.sha = "0" * 64


def cited(**by_id):
    return {int(cid): dict(v) for cid, v in by_id.items()}


def test_the_adversary_names_the_work_a_relayed_claim_points_at():
    findings = adv.relayed(Row([78, 79, 80]), {
        78: {"evidence_grade": "relayed", "attributed_to": "Yuan et al., 2026"},
        79: {"evidence_grade": "relayed", "attributed_to": None},
        80: {"evidence_grade": "controlled", "attributed_to": None},
    })
    assert len(findings) == 1
    text = findings[0].detail
    assert findings[0].check == "evidence-relayed"
    assert findings[0].severity == "note"
    assert "78 (Yuan et al., 2026)" in text
    assert "79 (the source named no work)" in text
    assert "80" not in text.split(":")[-1]
    assert "reading-queue line" in text


def test_the_adversary_is_silent_when_nothing_is_relayed():
    """One more note saying nothing happened, on every skill, is noise."""
    assert adv.relayed(Row([10]), {
        10: {"evidence_grade": "controlled", "attributed_to": None}}) == []
    assert adv.relayed(Row([10]), {}) == []


def test_relayed_is_not_counted_as_a_grade_with_no_measurement():
    """`WEAK_GRADES` is about a missing number and relayed is not that.

    A relayed row usually arrives with numbers, so folding it into that
    sentence would describe it wrongly in both directions.
    """
    assert adv.RELAYED not in adv.WEAK_GRADES
    findings = adv.grades(Row([10]), {
        10: {"evidence_grade": "relayed", "attributed_to": "the Chroma report"}})
    shape = [f for f in findings if f.check == "evidence-grade"][0].detail
    assert "1 relayed" in shape
    assert "carry no measurement behind them" not in shape
    assert any(f.check == "evidence-relayed" for f in findings)


def test_the_relayed_finding_never_changes_a_verdict():
    """No register sets a bar for this, so the reviewer does not invent one."""
    findings = adv.grades(Row([10]), {
        10: {"evidence_grade": "relayed", "attributed_to": "Liu et al., 2025"}})
    assert adv.verdict_of(findings) != "fail"
    assert all(f.severity == "note" for f in findings)


def test_the_cited_query_reads_the_address():
    assert "attributed_to" in adv.QUERIES["cited"]


# --------------------------------- the rows the grade cannot reach by itself

def test_the_audit_finds_graded_rows_that_read_relayed_and_writes_nothing():
    """The grade is written at distill, so it reaches no row already written.

    Every relayed claim distilled before 2026-10-26 is still graded
    `controlled` or `asserted`, which is the state the incident is about. The
    audit is how that becomes a number, and it has no write path on purpose.
    """
    sys.path.insert(0, str(ROOT / "pipeline"))
    import backfill_grades as bg

    class Conn:
        def __init__(self, rows):
            self.rows = rows

        def execute(self, sql, params=()):
            assert "update" not in sql.lower()
            return types.SimpleNamespace(fetchall=lambda: self.rows)

    rows = [(78, PAPER, THE_SENTENCE, "controlled"),
            (79, PAPER, FIRST_HAND[0], "controlled"),
            (80, POST, SECOND_HAND[1], "anecdote")]
    found = bg.relay_candidates(Conn(rows), evidence)
    assert [r["id"] for r in found] == [78, 80]
    assert found[0]["markers"] == ["says-et-al", "others-say"]
    assert found[0]["graded_as"] == "controlled"
    source = (ROOT / "pipeline" / "backfill_grades.py").read_text()
    assert "def relay_audit" in source
    assert "relayed" in bg.GRADED_SQL, (
        "the audit must exclude rows that are already graded relayed, or it "
        "re-reports its own answers every run")
