"""The triage planner's fairness properties, as tests.

These encode why the planner exists: a run that is cut short by a 429 must
still have read more than one tier. Run with `python3 tests/test_triage_planner.py`.
"""

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub modal so the planner's logic can be tested without the Modal SDK or any
# credentials. plan_batches is pure; only the decorators need modal to exist.
if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)
    modal.Image = types.SimpleNamespace(
        debian_slim=lambda *a, **k: types.SimpleNamespace(
            pip_install=lambda *a, **k: types.SimpleNamespace(
                add_local_file=lambda *a, **k: None
            )
        )
    )
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

import pipeline.triage as t


def rows(tier, n, start=0):
    return [(f"{tier}:{i}", f"title {i}", "abstract", tier) for i in range(start, start + n)]


def tiers_of(plan):
    return [chunk[0][3] for chunk in plan]


def test_truncated_run_is_still_fair():
    """The bug that mattered: 2 calls landed and only tier b was ever read."""
    plan = t.plan_batches(rows("b", 500) + rows("a", 500) + rows("a-low", 500), max_calls=2)
    assert len(set(tiers_of(plan))) == 2, tiers_of(plan)
    assert "a" in tiers_of(plan), "the firehose must be served in the first two calls"


def test_a_low_is_never_last():
    """'a-low' fell into the old CASE's else branch and sorted behind everything."""
    plan = t.plan_batches(rows("b", 100) + rows("a-low", 100), max_calls=2)
    assert set(tiers_of(plan)) == {"b", "a-low"}, tiers_of(plan)


def test_unknown_tier_still_drains():
    plan = t.plan_batches(rows("b", 100) + rows("brand-new", 100), max_calls=2)
    assert "brand-new" in tiers_of(plan), tiers_of(plan)


def test_weights_are_respected_over_a_full_run():
    plan = t.plan_batches(
        rows("b", 500) + rows("a", 500) + rows("a-low", 500) + rows("c", 500) + rows("d", 500),
        max_calls=10,
    )
    counts = {tier: tiers_of(plan).count(tier) for tier in set(tiers_of(plan))}
    assert counts == {"a": 3, "b": 3, "a-low": 2, "c": 1, "d": 1}, counts


def test_short_queue_spills_its_share():
    """A quiet hf-daily day donates its calls instead of wasting them."""
    plan = t.plan_batches(rows("b", 5) + rows("a", 500), max_calls=10)
    assert len(plan) == 10, len(plan)
    assert tiers_of(plan).count("a") == 9, tiers_of(plan)


def test_no_paper_is_sent_twice():
    plan = t.plan_batches(rows("a", 95) + rows("b", 30), max_calls=20)
    ids = [row[0] for chunk in plan for row in chunk]
    assert len(ids) == len(set(ids)), "a paper was planned into two calls"


def test_terminates_when_queue_is_smaller_than_budget():
    plan = t.plan_batches(rows("a", 3), max_calls=50)
    assert len(plan) == 1 and len(plan[0]) == 3


def test_empty_queue():
    assert t.plan_batches([], max_calls=25) == []


def test_zero_weight_tier_does_not_hang():
    t.TIER_WEIGHTS["muted"] = 0
    try:
        plan = t.plan_batches(rows("muted", 100), max_calls=5)
        assert plan == [], plan
    finally:
        del t.TIER_WEIGHTS["muted"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"{len(tests)} passed")
