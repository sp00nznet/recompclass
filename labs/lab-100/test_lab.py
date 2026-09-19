"""
Tests for Lab 100: Migration Ladder
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import migration


PROFILE = {"render": 5000, "update": 3000, "input": 1500, "audio": 400, "menu": 100}
ALL = set(PROFILE)


class TestPlan:
    def test_hottest_first(self):
        o = migration.plan_migration(PROFILE)
        assert o is not None, "plan_migration() returned None"
        assert o[0] == "render"
        assert o[-1] == "menu"

    def test_includes_everything(self):
        assert sorted(migration.plan_migration(PROFILE)) == sorted(PROFILE)

    def test_stable_on_ties(self):
        tied = {"b": 10, "a": 10}
        assert migration.plan_migration(tied) == ["a", "b"]


class TestSimulate:
    def test_starts_at_zero(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert c is not None, "simulate_migration() returned None"
        assert c[0] == 0.0

    def test_ends_at_one(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert abs(c[-1] - 1.0) < 1e-9

    def test_monotonic(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert all(b >= a for a, b in zip(c, c[1:]))

    def test_length(self):
        order = migration.plan_migration(PROFILE)
        assert len(migration.simulate_migration(PROFILE, order)) == len(order) + 1

    def test_first_port_is_the_biggest_jump(self):
        order = migration.plan_migration(PROFILE)
        c = migration.simulate_migration(PROFILE, order)
        jumps = [b - a for a, b in zip(c, c[1:])]
        assert jumps[0] == max(jumps)


class TestStepsToReach:
    def test_half(self):
        order = migration.plan_migration(PROFILE)
        c = migration.simulate_migration(PROFILE, order)
        # render alone is 5000 of 10000.
        assert migration.steps_to_reach(c, 0.5) == 1

    def test_ninety_percent(self):
        order = migration.plan_migration(PROFILE)
        c = migration.simulate_migration(PROFILE, order)
        assert migration.steps_to_reach(c, 0.9) == 3

    def test_zero_needs_nothing(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert migration.steps_to_reach(c, 0.0) == 0

    def test_unreachable(self):
        assert migration.steps_to_reach([0.0, 0.5], 0.9) is None


class TestVerifyRunnable:
    def test_all_emulated_is_runnable(self):
        v = migration.verify_runnable(ALL, set(), ALL)
        assert v is not None, "verify_runnable() returned None"
        assert v == []

    def test_partially_ported_still_runnable(self):
        assert migration.verify_runnable(ALL, {"render"}, ALL) == []

    def test_all_ported_runnable(self):
        assert migration.verify_runnable(ALL, ALL, set()) == []

    def test_gap_detected(self):
        v = migration.verify_runnable(ALL, {"render"}, ALL - {"menu"})
        assert v == ["menu"]

    def test_sorted(self):
        v = migration.verify_runnable(ALL, set(), set())
        assert v == sorted(ALL)
