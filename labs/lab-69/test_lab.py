"""
Tests for Lab 69: Audio Clock Discipline
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import audioclock


class TestBuffer:
    def test_write_and_read(self):
        b = audioclock.Buffer(100)
        assert b.write(30) == 30
        assert b.read(10) == 10
        assert b.level == 20

    def test_overrun_drops(self):
        b = audioclock.Buffer(100)
        b.write(80)
        stored = b.write(50)
        assert stored == 20
        assert b.overruns == 1
        assert b.level == 100

    def test_underrun(self):
        b = audioclock.Buffer(100)
        b.write(10)
        got = b.read(50)
        assert got == 10
        assert b.underruns == 1
        assert b.level == 0

    def test_no_spurious_counts(self):
        b = audioclock.Buffer(100)
        b.write(50)
        b.read(50)
        assert b.overruns == 0 and b.underruns == 0

    def test_fill(self):
        b = audioclock.Buffer(100)
        b.write(25)
        assert abs(b.fill - 0.25) < 1e-9


class TestDiscipline:
    def test_at_target_is_neutral(self):
        d = audioclock.ClockDiscipline(target_fill=0.5)
        c = d.correction(0.5)
        assert c is not None, "correction() returned None"
        assert abs(c - 1.0) < 1e-9

    def test_too_full_speeds_up(self):
        d = audioclock.ClockDiscipline(target_fill=0.5)
        assert d.correction(0.9) > 1.0

    def test_too_empty_slows_down(self):
        d = audioclock.ClockDiscipline(target_fill=0.5)
        assert d.correction(0.1) < 1.0

    def test_clamped(self):
        d = audioclock.ClockDiscipline(target_fill=0.5, gain=10.0, max_correction=0.02)
        assert abs(d.correction(1.0) - 1.02) < 1e-9
        assert abs(d.correction(0.0) - 0.98) < 1e-9


class TestSimulate:
    def test_fixed_ratio_drifts_into_failure(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=None, drift=0.01)
        assert r is not None, "simulate() returned None"
        assert r["overruns"] > 0, "a 1% producer drift must eventually overrun"

    def test_discipline_survives_the_same_drift(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=audioclock.ClockDiscipline(),
                                drift=0.01)
        assert r["overruns"] == 0
        assert r["underruns"] == 0

    def test_discipline_holds_near_target(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=audioclock.ClockDiscipline(target_fill=0.5),
                                drift=0.005)
        assert 0.2 < r["final_fill"] < 0.8

    def test_records_one_fill_per_frame(self):
        r = audioclock.simulate(frames=50, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000)
        assert len(r["fills"]) == 50

    def test_negative_drift_underruns_without_discipline(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=None, drift=-0.01)
        assert r["underruns"] > 0
