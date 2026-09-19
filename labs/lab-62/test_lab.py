"""
Tests for Lab 62: Interpreter Oracle
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import oracle


def make_impl(behaviour):
    """behaviour(step, state) -> dict of field updates, or raises StopIteration."""
    def impl(program, step, state):
        new = oracle.State(**state.as_dict())
        for k, v in behaviour(step, state).items():
            setattr(new, k, v)
        return new
    return impl


def counting(step, state):
    return {"pc": state.pc + 1, "a": (state.a + 1) & 0xFF}


def counting_wrong_at(n):
    def b(step, state):
        d = counting(step, state)
        if step == n:
            d["a"] = (d["a"] + 1) & 0xFF
        return d
    return b


def stops_after(n):
    def b(step, state):
        if step >= n:
            raise StopIteration
        return counting(step, state)
    return b


class TestDiffStates:
    def test_identical(self):
        s = oracle.State(pc=1, a=2)
        d = oracle.diff_states(s, oracle.State(pc=1, a=2))
        assert d is not None, "diff_states() returned None"
        assert d == []

    def test_one_field(self):
        assert oracle.diff_states(oracle.State(a=1), oracle.State(a=2)) == ["a"]

    def test_several_in_field_order(self):
        d = oracle.diff_states(oracle.State(pc=1, flags=1), oracle.State(pc=2, flags=2))
        assert d == ["pc", "flags"]


class TestRunDifferential:
    def test_no_divergence(self):
        r = oracle.run_differential(None, make_impl(counting), make_impl(counting), limit=50)
        assert r is not None, "run_differential() returned None"
        assert r["diverged"] is False
        assert r["steps_run"] == 50

    def test_finds_first_divergence(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(7)), limit=50)
        assert r["diverged"] is True
        assert r["step"] == 7

    def test_reports_fields(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(3)), limit=50)
        assert r["fields"] == ["a"]

    def test_reports_states(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(2)), limit=50)
        assert r["expected"].a != r["actual"].a

    def test_stops_at_end_of_program(self):
        r = oracle.run_differential(None, make_impl(stops_after(5)),
                                    make_impl(stops_after(5)), limit=100)
        assert r["diverged"] is False
        assert r["steps_run"] == 5

    def test_implementations_do_not_share_state(self):
        # If both advanced the same object, a divergence could never be seen.
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(1)), limit=10)
        assert r["diverged"] is True


class TestFormat:
    def test_clean_run_is_not_overstated(self):
        r = oracle.run_differential(None, make_impl(counting), make_impl(counting), limit=5)
        text = oracle.format_divergence(r)
        assert "No divergence" in text
        assert "not that either is" in text

    def test_names_step_and_field(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(4)), limit=20)
        text = oracle.format_divergence(r)
        assert "step 4" in text
        assert "a " in text
