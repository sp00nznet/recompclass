"""
Tests for Lab 73: Guest-Level Sampling Profiler
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import gprof


FUNCS = [(0x1000, 0x100, "main"), (0x1100, 0x080, "update"), (0x2000, 0x200, "render")]


class TestResolve:
    def test_start(self):
        assert gprof.resolve(0x1000, FUNCS) == "main"

    def test_middle(self):
        assert gprof.resolve(0x1050, FUNCS) == "main"

    def test_last_byte(self):
        assert gprof.resolve(0x10FF, FUNCS) == "main"

    def test_next_function(self):
        assert gprof.resolve(0x1100, FUNCS) == "update"

    def test_gap(self):
        assert gprof.resolve(0x1200, FUNCS) is None

    def test_before_everything(self):
        assert gprof.resolve(0x0100, FUNCS) is None


class TestSampler:
    def test_counts(self):
        s = gprof.Sampler(FUNCS)
        for a in (0x1000, 0x1010, 0x2000):
            s.sample(a)
        p = s.profile()
        assert p is not None, "profile() returned None"
        assert p[0]["name"] == "main"
        assert p[0]["samples"] == 2

    def test_unresolved(self):
        s = gprof.Sampler(FUNCS)
        s.sample(0x9999)
        assert s.unresolved == 1
        assert s.profile() == []

    def test_percent_includes_unresolved(self):
        s = gprof.Sampler(FUNCS)
        s.sample(0x1000)
        s.sample(0x9999)
        assert abs(s.profile()[0]["percent"] - 50.0) < 1e-9

    def test_sorted(self):
        s = gprof.Sampler(FUNCS)
        for a in [0x2000] * 3 + [0x1000] * 5:
            s.sample(a)
        names = [r["name"] for r in s.profile()]
        assert names == ["main", "render"]


class TestDetectSpin:
    def test_healthy(self):
        samples = [(0x1000 + i, "main") for i in range(100)]
        assert gprof.detect_spin(samples) is None

    def test_stuck(self):
        samples = [(0x1234, "update")] * 95 + [(0x1000, "main")] * 5
        d = gprof.detect_spin(samples)
        assert d is not None
        assert "1234" in d.upper() or "0X1234" in d.upper()
        assert "update" in d

    def test_empty(self):
        assert gprof.detect_spin([]) is None

    def test_threshold_respected(self):
        samples = [(0x1234, "u")] * 6 + [(0x1000, "m")] * 4
        assert gprof.detect_spin(samples, threshold=0.9) is None
        assert gprof.detect_spin(samples, threshold=0.5) is not None
