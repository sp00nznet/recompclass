"""
Tests for Lab 78: Prune and Trap
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import prune


GRAPH = {
    "main": ["init", "loop"],
    "init": ["load"],
    "loop": ["update", "draw"],
    "update": [],
    "draw": [],
    "load": [],
    "debug_dump": ["debug_print"],
    "debug_print": [],
    "vtable_only": [],
}
ALL = list(GRAPH)


class TestReachable:
    def test_from_entry(self):
        r = reach()
        assert "main" in r and "draw" in r

    def test_excludes_unreachable(self):
        assert "debug_dump" not in reach()

    def test_unknown_callee_included(self):
        r = prune.reachable("a", {"a": ["b"]})
        assert "b" in r


def reach():
    r = prune.reachable("main", GRAPH)
    assert r is not None, "reachable() returned None"
    return r


class TestObserved:
    def test_dedupes(self):
        o = prune.observed(["main", "loop", "loop", "draw"])
        assert o == {"main", "loop", "draw"}

    def test_empty(self):
        assert prune.observed([]) == set()


class TestLiveSet:
    def test_union(self):
        # vtable_only is unreachable statically but the trace saw it.
        live = prune.live_set("main", GRAPH, ["vtable_only"])
        assert "vtable_only" in live
        assert "draw" in live

    def test_still_excludes_dead(self):
        assert "debug_dump" not in prune.live_set("main", GRAPH, [])


class TestPlan:
    def test_partitions(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert p is not None, "plan() returned None"
        assert "main" in p["keep"]
        assert "debug_dump" in p["trap"]

    def test_counts(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert p["kept"] + p["trapped"] == len(ALL)

    def test_reduction(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert 0.0 < p["reduction"] < 1.0

    def test_sorted(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert p["keep"] == sorted(p["keep"])
        assert p["trap"] == sorted(p["trap"])

    def test_empty(self):
        p = prune.plan([], set())
        assert p["reduction"] == 0.0


class TestTrapRegistry:
    def test_clean_initially(self):
        assert prune.TrapRegistry(["a", "b"]).clean is True

    def test_records_a_bad_prune(self):
        r = prune.TrapRegistry(["debug_dump"])
        assert r.call("debug_dump") == 1
        assert r.clean is False

    def test_counts_repeats(self):
        r = prune.TrapRegistry(["x"])
        r.call("x")
        assert r.call("x") == 2

    def test_unknown_name_raises(self):
        import pytest
        with pytest.raises(KeyError):
            prune.TrapRegistry(["x"]).call("y")

    def test_report_sorted(self):
        r = prune.TrapRegistry(["a", "b"])
        r.call("a")
        r.call("b")
        r.call("b")
        assert r.report() == [("b", 2), ("a", 1)]
