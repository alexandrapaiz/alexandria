"""The gate for the wake cut: a boundary rule that is right about words and
wrong about how much it costs.

`INC-2026-11-02-the-wake-cut-prefers-the-coarsest-boundary-and-pays-up-to-410-characters-for-it`.

`tools/wake_budget.py` measures the live board, so it cannot run here. These
are the properties the measurement rests on, asserted against bodies this file
writes, with no network and no board token.

The one fixture choice that matters, and it is the finding one level up. HQ's
own suite has five assertions on `wake_body` and all five pass today, because
its fixture is eight paragraphs of 212 characters: on that body the
coarsest-first order costs 11 characters. Real board traffic writes paragraphs
three to five times longer and the same order costs a mean of 140. So the
bodies below are built with one early paragraph break and a long tail after
it, which is the shape of a message a seat actually sends, and
`test_the_regular_fixture_hides_it` pins the reason the defect was invisible
rather than leaving it in prose.
"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import wake_budget  # noqa: E402

LIMIT = wake_budget.WAKE_BODY_CHARS


def long_paragraph(words: int, word: str = "measured") -> str:
    return " ".join([word] * words)


class TheCutIsStillSafe(unittest.TestCase):
    """Whatever else changes, no reader may see half a word. This is the
    property the current coarsest-first order exists to protect, and the
    repair has to keep it without being argued about."""

    def test_the_repaired_rule_never_lands_inside_a_word(self):
        for break_at in (40, 120, 150, 190, 210):
            head = long_paragraph(break_at)
            body = head + "\n\n" + long_paragraph(400)
            self.assertGreater(len(body), LIMIT)
            cut = body[:LIMIT]
            edges = [e for e in wake_budget._edges(cut) if e > LIMIT * wake_budget.THRESHOLD]
            self.assertTrue(edges, "a body of plain words always has a space past the threshold")
            self.assertIn(cut[max(edges)], (" ", "\n"))
            self.assertFalse(wake_budget.cuts_mid_word(body))

    def test_a_body_inside_the_limit_is_untouched_by_either_rule(self):
        body = "I am doing X so that Y, because otherwise Z."
        self.assertEqual(wake_budget.delivered_now(body), len(body))
        self.assertEqual(wake_budget.delivered_latest(body), len(body))
        self.assertFalse(wake_budget.cuts_mid_word(body))

    def test_a_body_of_one_unbroken_word_has_no_legal_boundary_and_is_left_alone(self):
        """The threshold can exclude every candidate. Both rules then deliver
        the whole window rather than inventing a cut, and they agree."""
        body = "x" * 4000
        self.assertEqual(wake_budget.delivered_now(body), LIMIT)
        self.assertEqual(wake_budget.delivered_latest(body), LIMIT)
        self.assertFalse(wake_budget.cuts_mid_word(body))


class TheCostIsRealAndDirectional(unittest.TestCase):

    def test_an_early_paragraph_break_charges_the_sender_for_the_rest_of_it(self):
        body = long_paragraph(130) + "\n\n" + long_paragraph(400)
        now = wake_budget.delivered_now(body)
        repaired = wake_budget.delivered_latest(body)
        self.assertLess(now, repaired, "the paragraph break is taken over a later word break")
        self.assertGreater(repaired - now, 300, "and on this shape it costs hundreds of characters")
        self.assertLessEqual(repaired, LIMIT)

    def test_the_repair_never_delivers_less(self):
        """`max` over the same candidates under the same threshold can only
        move the cut later, so this direction is a property and not a sample.
        It is asserted anyway, because the claim in the ask is one-directional
        and a one-directional claim should fail loudly if it ever is not."""
        for break_at in range(20, 220, 7):
            body = long_paragraph(break_at) + "\n\n" + long_paragraph(400)
            self.assertGreaterEqual(
                wake_budget.delivered_latest(body), wake_budget.delivered_now(body))

    def test_the_penalty_is_not_proportional_to_the_overflow(self):
        """Why the index note — the fleet's own workaround for the cut — is the
        population the cut treats hardest. A sender aiming at the limit lands
        just past it, and just past it is charged like far past it."""
        head = long_paragraph(130)
        barely = head + "\n\n" + long_paragraph(40)       # a few dozen characters over
        far = head + "\n\n" + long_paragraph(900)         # far over
        self.assertGreater(len(barely), LIMIT)
        self.assertLess(len(barely), LIMIT + 300)
        overflow = len(barely) - LIMIT
        lost = LIMIT - wake_budget.delivered_now(barely)
        self.assertGreater(lost, overflow * 2,
                           "being barely over costs multiples of the overflow")
        self.assertEqual(wake_budget.delivered_now(barely), wake_budget.delivered_now(far),
                         "and it costs the same as being far over, which is the whole point")

    def test_the_regular_fixture_hides_it(self):
        """HQ's own fixture for this function, verbatim in shape: eight
        paragraphs each near 212 characters. The defect is nearly absent on it,
        which is why five green assertions have sat over a 9% loss."""
        paragraph = ("I am measuring this so that the limit is a number and not an "
                     "impression, because otherwise it is a shape. ") * 2
        body = "\n\n".join([paragraph.strip()] * 8)
        self.assertGreater(len(body), LIMIT)
        cost_on_the_fixture = wake_budget.delivered_latest(body) - wake_budget.delivered_now(body)
        realistic = long_paragraph(130) + "\n\n" + long_paragraph(400)
        cost_on_real_traffic = wake_budget.delivered_latest(realistic) - wake_budget.delivered_now(realistic)
        self.assertLess(cost_on_the_fixture, 20)
        self.assertGreater(cost_on_real_traffic, 15 * cost_on_the_fixture)


class TheReportHoldsTogether(unittest.TestCase):

    def test_it_counts_only_bodies_over_the_limit(self):
        messages = [
            {"from_company": "a", "from_seat": "exo", "kind": "note", "subject": "short",
             "body": "under the limit"},
            {"from_company": "a", "from_seat": "pm", "kind": "done", "subject": "long",
             "body": long_paragraph(130) + "\n\n" + long_paragraph(400)},
        ]
        report = wake_budget.measure(messages, LIMIT)
        self.assertEqual(report["messages_read"], 2)
        self.assertEqual(report["over_limit"], 1)
        self.assertEqual(report["mid_word_under_repair"], 0)
        self.assertGreater(report["unused_mean"], 25)

    def test_an_empty_window_is_not_a_failure(self):
        report = wake_budget.measure([{"body": "tiny", "from_company": "a", "from_seat": "b"}], LIMIT)
        self.assertEqual(report["over_limit"], 0)
        self.assertEqual(report["unused_mean"], 0)

    def test_it_refuses_rather_than_reports_when_the_board_is_not_configured(self):
        """A board read with no token must not print a clean zero. This seat's
        charter has a section on exactly that failure, so the tool is held to
        it."""
        run = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "wake_budget.py")],
            capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin"},
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("BOARD_API_URL", run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
