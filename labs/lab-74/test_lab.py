"""
Tests for Lab 74: Vector Lifter With a Reference
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import veclift


import math


class TestSaturate:
    def test_unsigned_in_range(self):
        assert veclift.saturate(100, 8, False) == 100

    def test_unsigned_clamps_high(self):
        assert veclift.saturate(300, 8, False) == 255

    def test_unsigned_clamps_low(self):
        assert veclift.saturate(-5, 8, False) == 0

    def test_signed_range(self):
        assert veclift.saturate(200, 8, True) == 127
        assert veclift.saturate(-200, 8, True) == -128

    def test_does_not_wrap(self):
        # The whole point: 256 must become 255, not 0.
        assert veclift.saturate(256, 8, False) == 255


class TestVaddSat:
    def test_elementwise(self):
        assert veclift.vadd_sat([1, 2], [3, 4]) == [4, 6]

    def test_saturates(self):
        assert veclift.vadd_sat([250], [10]) == [255]

    def test_signed(self):
        assert veclift.vadd_sat([120], [50], signed=True) == [127]

    def test_length_mismatch(self):
        import pytest
        with pytest.raises(ValueError):
            veclift.vadd_sat([1, 2], [3])


class TestFlushDenormals:
    def test_flushes(self):
        import sys
        out = veclift.flush_denormals([sys.float_info.min / 2])
        assert out is not None, "flush_denormals() returned None"
        assert out[0] == 0.0

    def test_preserves_sign(self):
        import sys
        out = veclift.flush_denormals([-sys.float_info.min / 2])
        assert math.copysign(1.0, out[0]) == -1.0

    def test_disabled(self):
        import sys
        d = sys.float_info.min / 2
        assert veclift.flush_denormals([d], enabled=False)[0] == d

    def test_normals_untouched(self):
        assert veclift.flush_denormals([1.5, -2.5]) == [1.5, -2.5]

    def test_inf_and_nan_untouched(self):
        out = veclift.flush_denormals([float("inf"), float("nan")])
        assert out[0] == float("inf")
        assert math.isnan(out[1])


class TestVmin:
    def test_basic(self):
        assert veclift.vmin([1.0, 5.0], [3.0, 2.0]) == [1.0, 2.0]

    def test_nan_loses_by_default(self):
        out = veclift.vmin([float("nan")], [2.0])
        assert out[0] == 2.0

    def test_nan_wins_when_asked(self):
        out = veclift.vmin([float("nan")], [2.0], nan_wins=True)
        assert math.isnan(out[0])

    def test_both_nan(self):
        out = veclift.vmin([float("nan")], [float("nan")])
        assert math.isnan(out[0])

    def test_length_mismatch(self):
        import pytest
        with pytest.raises(ValueError):
            veclift.vmin([1.0], [1.0, 2.0])


class TestDifferential:
    def test_agreement(self):
        r = veclift.differential(lambda a, b: a + b, lambda a, b: b + a,
                                 [(1, 2), (3, 4)])
        assert r is not None, "differential() returned None"
        assert r["diverged"] == 0
        assert r["total"] == 2

    def test_finds_divergence(self):
        r = veclift.differential(lambda a, b: a + b, lambda a, b: a - b, [(1, 2)])
        assert r["diverged"] == 1
        assert r["failures"][0]["case"] == (1, 2)

    def test_nan_equals_nan(self):
        nan = float("nan")
        r = veclift.differential(lambda a: nan, lambda a: nan, [(1.0,)])
        assert r["diverged"] == 0, "NaN != NaN would drown real findings in noise"

    def test_records_both_values(self):
        r = veclift.differential(lambda a: 1, lambda a: 2, [(0,)])
        assert r["failures"][0]["expected"] == 1
        assert r["failures"][0]["actual"] == 2
