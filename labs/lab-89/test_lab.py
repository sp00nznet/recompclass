"""
Tests for Lab 89: Independent Oracle
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import indoracle


def st(**kw):
    base = {"pc": 0, "a": 0, "b": 0, "x": 0, "y": 0, "sp": 0, "flags": 0}
    base.update(kw)
    return base


class TestValidateState:
    def test_ok(self):
        v = indoracle.validate_state(st(a=0xF, pc=0xFFF))
        assert v is not None, "validate_state() returned None"
        assert v == []

    def test_too_wide(self):
        v = indoracle.validate_state(st(a=0x10))
        assert len(v) == 1
        assert v[0][0] == "a"

    def test_the_real_giveaway(self):
        # A trace corrupted by CRLF translation injects a stray 0x0D,
        # pushing the value past what the register can hold.
        v = indoracle.validate_state(st(x=0x1A0D))
        assert any(f == "x" for f, _, _ in v)

    def test_unknown_field_ignored(self):
        assert indoracle.validate_state(st(cycles=999999)) == []

    def test_sorted(self):
        v = indoracle.validate_state(st(a=0x10, b=0x10))
        assert [f for f, _, _ in v] == ["a", "b"]


class TestCompareStep:
    def test_agree(self):
        r = indoracle.compare_step(st(), st())
        assert r is not None, "compare_step() returned None"
        assert r["agree"] is True
        assert r["kind"] is None

    def test_target_bug(self):
        r = indoracle.compare_step(st(flags=0x1), st(flags=0x2))
        assert r["kind"] == "target_bug"
        assert r["fields"] == ["flags"]

    def test_impossible_value_wins(self):
        # Even though flags also differ, the impossible X dominates.
        r = indoracle.compare_step(st(), st(x=0x1A0D, flags=1))
        assert r["kind"] == "impossible_value"

    def test_timing_only(self):
        a = dict(st(), cycles=100)
        b = dict(st(), cycles=101)
        r = indoracle.compare_step(a, b)
        assert r["kind"] == "timing"

    def test_timing_plus_register_is_a_bug(self):
        a = dict(st(a=1), cycles=100)
        b = dict(st(a=2), cycles=101)
        assert indoracle.compare_step(a, b)["kind"] == "target_bug"


class TestRunValidation:
    def test_clean(self):
        f = lambda s, i: st(pc=i)
        r = indoracle.run_validation(None, f, f, limit=100)
        assert r is not None, "run_validation() returned None"
        assert r["diverged"] is False
        assert r["steps_run"] == 100

    def test_finds_bug_at_step(self):
        def oracle(s, i):
            return st(pc=i, flags=0)

        def target(s, i):
            return st(pc=i, flags=1 if i == 42 else 0)

        r = indoracle.run_validation(None, oracle, target, limit=100)
        assert r["step"] == 42
        assert r["kind"] == "target_bug"

    def test_stops_at_end(self):
        def f(s, i):
            if i >= 10:
                raise StopIteration
            return st(pc=i)
        r = indoracle.run_validation(None, f, f, limit=100)
        assert r["steps_run"] == 10

    def test_format_gives_advice(self):
        def oracle(s, i):
            return st()

        def target(s, i):
            return st(x=0x1A0D)
        r = indoracle.run_validation(None, oracle, target, limit=5)
        assert "binary mode" in indoracle.format_validation(r)
