"""
Tests for Lab 99: Instrument a Hybrid
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import hybrid


def interp(addr):
    return 5      # the fallback runs five instructions


class TestDispatch:
    def test_native(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=20)
        assert h.dispatch(0x100) == 20
        assert h.native_calls == 1

    def test_fallback(self):
        h = hybrid.Interceptor(fallback=interp)
        assert h.dispatch(0x200) == 5
        assert h.fallback_calls == 1

    def test_crash_falls_back(self):
        def boom():
            raise ValueError("bad lift")
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, boom, instructions=20)
        assert h.dispatch(0x100) == 5
        assert h.crashes == 1
        assert h.fallback_calls == 1
        assert h.native_calls == 0

    def test_no_fallback_raises(self):
        import pytest
        with pytest.raises(RuntimeError):
            hybrid.Interceptor().dispatch(0x999)


class TestCrossover:
    def test_all_native(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=10)
        h.dispatch(0x100)
        assert h.crossover() == 1.0

    def test_all_fallback(self):
        h = hybrid.Interceptor(fallback=interp)
        h.dispatch(0x200)
        assert h.crossover() == 0.0

    def test_weighted_by_instructions(self):
        # One big native call outweighs many tiny fallbacks.
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=100)
        h.dispatch(0x100)
        for _ in range(10):
            h.dispatch(0x200)
        assert h.crossover() > 0.6

    def test_nothing_executed(self):
        assert hybrid.Interceptor().crossover() == 0.0


class TestHonestSummary:
    def test_nothing(self):
        s = hybrid.honest_summary(hybrid.Interceptor().stats())
        assert s is not None, "honest_summary() returned None"
        assert "Nothing has executed" in s

    def test_zero_crossover_is_called_out(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None)
        h.dispatch(0x200)
        s = hybrid.honest_summary(h.stats())
        assert "0%" in s
        assert "fallback is running this program" in s

    def test_full_crossover(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=10)
        h.dispatch(0x100)
        assert "All executed instructions ran native" in hybrid.honest_summary(h.stats())

    def test_partial(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=5)
        h.dispatch(0x100)
        h.dispatch(0x200)
        assert "50.0%" in hybrid.honest_summary(h.stats())

    def test_mentions_crashes(self):
        def boom():
            raise ValueError
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, boom, instructions=5)
        h.dispatch(0x100)
        assert "crashed and fell back" in hybrid.honest_summary(h.stats())
