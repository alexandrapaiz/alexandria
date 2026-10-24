"""Canon law 13's grammar question, asserted on the shapes that collide with it.

`docs/voice/check_voice.py` holds `past_tense_you`, the one half of the
stands-alone gate the generator calls grammar rather than judgment: find every
sentence whose subject is "you" and whose verb is in any past tense. Until
2026-10-24 its only caller was `specimens`, which reads the two generator
prompts, so a detector for the one hard voice law with no pre-send gate had
never been run over an issue.

Pointing it at `site/content/issues` is what found the bug this file pins down.
The participle arm read `\\w+(?:ed|en|t|ne)\\b`, with no floor on the stem, so
every word ending in those two letters was a participle. `What to read if you
have one hour` is a standing heading in the archive and the old pattern fired
on it, because "one" is "o" plus "ne".

A gate whose first run on the real artifact reports a line the laws permit is a
gate nobody keeps, which is why the floor is asserted here and not just fixed.
The eight true shapes are the ones that have actually shipped or been struck;
the nine others are the collisions. Both halves matter: a pattern tuned only
against false positives stops catching the sentence the owner struck.
"""

import pathlib
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _voice():
    spec = importlib.util.spec_from_file_location(
        "check_voice", ROOT / "docs/voice/check_voice.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: Sentences that ARE a claim about what the reader has done. The first two are
#: the openings she struck and the one that shipped after her ruling was
#: already in the prompt.
CLAIMS = (
    "You spent last week watching agents get faster by doing less at test time.",
    "You have spent the week watching agents get faster by thinking less.",
    "you have written the same retry logic three times",
    "You have shipped a dozen agents.",
    "you had built the harness yourself",
    "you have done this before",
    "You were running agents overnight.",
    "you have not shipped a single one",
)

#: Sentences that are not. Every one of the first four was a false positive
#: under the pattern as it stood, and the first is a heading the archive prints.
PERMITTED = (
    "What to read if you have one hour",
    "you have it in production",
    "you have ten agents running",
    "you have none of these",
    "You keep a dozen agents running.",
    "if you have a minute",
    "you have two models to choose between",
    "The agent-building world has spent the week arguing about scaffolding.",
    "Accelerate every builder and agent to frontier speed.",
)


def test_the_struck_openings_are_caught():
    past_tense_you = _voice().past_tense_you
    missed = [s for s in CLAIMS if not past_tense_you(s)]
    assert not missed, f"the gate no longer catches: {missed}"


def test_the_permitted_lines_do_not_fire():
    past_tense_you = _voice().past_tense_you
    wrong = [s for s in PERMITTED if past_tense_you(s)]
    assert not wrong, f"the gate fires on lines the laws permit: {wrong}"


def test_the_standing_heading_in_the_archive_does_not_fire():
    """Named on its own, because this is the line that found the bug.

    It is printed by `prompts/digest.md`'s read-list section, so it appears in
    every issue that has one, and a gate that failed on it would have been
    turned off in its first week rather than fixed.
    """
    assert not _voice().past_tense_you("What to read if you have one hour")


def test_the_gate_reads_the_archive_and_returns_a_verdict():
    """`standalone` is a verdict and not a report.

    `stale` returns 0 unconditionally by design, and the test file beside this
    one explains why calling it would assert that a report printed. This gate
    is the other kind, so the test asserts the return code tracks the hits.
    """
    voice = _voice()
    issues = sorted((ROOT / "site/content/issues").glob("*.md"))
    assert issues, "no issues in the archive to read"
    hits = [(p, n) for p in issues
            for n, span, _ in voice.issue_sentences(p)
            if voice.past_tense_you(span) and not voice.hers(span)]
    rc = voice.standalone(issues)
    assert rc == (1 if hits else 0), (
        f"the gate returned {rc} with {len(hits)} hit(s)")
