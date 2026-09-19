"""
Tests for Lab 79: Function Ordering
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import ordering


SIZES = {"main": 100, "hot": 100, "warm": 100, "cold": 100, "never": 100}
TRACE = ["hot"] * 50 + ["warm"] * 10 + ["main"] * 5 + ["cold"]
ORIGINAL = ["main", "cold", "never", "warm", "hot"]


class TestCallCounts:
    def test_counts(self):
        c = ordering.call_counts(TRACE)
        assert c is not None, "call_counts() returned None"
        assert c["hot"] == 50
        assert c["cold"] == 1

    def test_absent(self):
        assert "never" not in ordering.call_counts(TRACE)

    def test_empty(self):
        assert ordering.call_counts([]) == {}


class TestOrderByHeat:
    def test_hottest_first(self):
        o = ordering.order_by_heat(ordering.call_counts(TRACE), list(SIZES))
        assert o is not None, "order_by_heat() returned None"
        assert o[0] == "hot"

    def test_uncalled_last(self):
        o = ordering.order_by_heat(ordering.call_counts(TRACE), list(SIZES))
        assert o[-1] == "never"

    def test_includes_everything(self):
        o = ordering.order_by_heat(ordering.call_counts(TRACE), list(SIZES))
        assert sorted(o) == sorted(SIZES)

    def test_deterministic(self):
        counts = {"a": 5, "b": 5}
        a = ordering.order_by_heat(counts, ["a", "b"])
        b = ordering.order_by_heat(counts, ["b", "a"])
        assert a == b, "ties must break deterministically or every build differs"


class TestLayout:
    def test_addresses(self):
        lay = ordering.layout(["a", "b"], {"a": 10, "b": 20})
        assert lay is not None, "layout() returned None"
        assert lay["a"] == 0
        assert lay["b"] == 10

    def test_missing_size(self):
        import pytest
        with pytest.raises(KeyError):
            ordering.layout(["a"], {})


class TestCacheEstimate:
    def test_counts_lines(self):
        lay = {"a": 0}
        n = ordering.estimate_cache_misses(["a"], lay, {"a": 64}, line_size=64)
        assert n == 1

    def test_spanning_function(self):
        n = ordering.estimate_cache_misses(["a"], {"a": 0}, {"a": 128}, line_size=64)
        assert n == 2

    def test_distinct_only(self):
        n = ordering.estimate_cache_misses(["a", "a", "a"], {"a": 0},
                                           {"a": 64}, line_size=64)
        assert n == 1


class TestCompare:
    def test_ordering_helps(self):
        r = ordering.compare_layouts(TRACE, list(SIZES), SIZES, ORIGINAL)
        assert r is not None, "compare_layouts() returned None"
        assert r["ordered_lines"] <= r["original_lines"]

    def test_reports_order(self):
        r = ordering.compare_layouts(TRACE, list(SIZES), SIZES, ORIGINAL)
        assert r["order"][0] == "hot"

    def test_improvement_non_negative(self):
        r = ordering.compare_layouts(TRACE, list(SIZES), SIZES, ORIGINAL)
        assert r["improvement"] >= 0.0
