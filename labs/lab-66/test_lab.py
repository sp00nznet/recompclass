"""
Tests for Lab 66: Divergence Minimiser
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import minimise


# The bug reproduces whenever the sequence contains both "a" and "z".
def needs_a_and_z(seq):
    return "a" in seq and "z" in seq


LONG = list("qqqaqqqqqqzqqqqqq")


class TestTruncate:
    def test_cuts_after_index(self):
        out = minimise.truncate([1, 2, 3, 4, 5], 2)
        assert out is not None, "truncate() returned None"
        assert out == [1, 2, 3]

    def test_index_beyond_end(self):
        assert minimise.truncate([1, 2], 99) == [1, 2]

    def test_negative_index(self):
        assert minimise.truncate([1, 2], -1) == []

    def test_does_not_mutate(self):
        data = [1, 2, 3]
        minimise.truncate(data, 1)
        assert data == [1, 2, 3]


class TestShrinkPrefix:
    def test_drops_leading_noise(self):
        out = minimise.shrink_prefix(LONG, needs_a_and_z)
        assert out is not None, "shrink_prefix() returned None"
        assert needs_a_and_z(out)
        assert len(out) < len(LONG)

    def test_keeps_failing(self):
        out = minimise.shrink_prefix(LONG, needs_a_and_z)
        assert out[0] == "a"

    def test_cannot_drop_anything(self):
        seq = list("az")
        assert minimise.shrink_prefix(seq, needs_a_and_z) == seq


class TestShrinkElements:
    def test_removes_unneeded(self):
        out = minimise.shrink_elements(list("qazq"), needs_a_and_z)
        assert out is not None, "shrink_elements() returned None"
        assert out == list("az")

    def test_keeps_failing(self):
        out = minimise.shrink_elements(LONG, needs_a_and_z)
        assert needs_a_and_z(out)

    def test_minimal_already(self):
        assert minimise.shrink_elements(list("az"), needs_a_and_z) == list("az")

    def test_does_not_mutate(self):
        data = list("qazq")
        minimise.shrink_elements(data, needs_a_and_z)
        assert data == list("qazq")


class TestMinimise:
    def test_reduces_to_two(self):
        r = minimise.minimise(LONG, needs_a_and_z)
        assert r is not None, "minimise() returned None"
        assert r["minimal"] == list("az")

    def test_reports_lengths(self):
        r = minimise.minimise(LONG, needs_a_and_z)
        assert r["original"] == len(LONG)
        assert r["final"] == 2
        assert r["ratio"] < 0.2

    def test_log_has_all_stages(self):
        r = minimise.minimise(LONG, needs_a_and_z, failure_index=len(LONG) - 1)
        stages = [s for s, _ in r["log"]]
        assert len(stages) == 3

    def test_rejects_non_failing_input(self):
        import pytest
        with pytest.raises(ValueError):
            minimise.minimise(list("qqq"), needs_a_and_z)

    def test_truncation_applied(self):
        # Everything after the last needed element should go.
        seq = list("azqqqqqqqqqq")
        r = minimise.minimise(seq, needs_a_and_z, failure_index=1)
        assert r["final"] == 2

    def test_result_still_fails(self):
        r = minimise.minimise(LONG, needs_a_and_z)
        assert needs_a_and_z(r["minimal"])
