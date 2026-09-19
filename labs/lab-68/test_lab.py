"""
Tests for Lab 68: Frame Driver
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import framedrv


class TestCycleClock:
    def test_no_frame_below_budget(self):
        c = framedrv.CycleClock(100)
        fired = c.tick(50)
        assert fired is not None, "tick() returned None"
        assert fired == 0
        assert c.frames == 0

    def test_frame_at_budget(self):
        c = framedrv.CycleClock(100)
        assert c.tick(100) == 1
        assert c.frames == 1

    def test_accumulates_across_ticks(self):
        c = framedrv.CycleClock(100)
        c.tick(60)
        assert c.tick(60) == 1

    def test_large_tick_fires_several(self):
        c = framedrv.CycleClock(100)
        assert c.tick(350) == 3
        assert c.frames == 3

    def test_remainder_carries(self):
        c = framedrv.CycleClock(100)
        c.tick(150)
        assert c.tick(50) == 1

    def test_total_cycles(self):
        c = framedrv.CycleClock(100)
        c.tick(30)
        c.tick(40)
        assert c.cycles == 70

    def test_callback_fires(self):
        seen = []
        c = framedrv.CycleClock(100, on_frame=lambda: seen.append(1))
        c.tick(250)
        assert len(seen) == 2


class TestRunLoop:
    def test_the_mariopaint_bug(self):
        # A loop of 2048 iterations that the ROM expected to take seconds.
        # Without a clock it completes instantly and draws nothing.
        c = framedrv.CycleClock(cycles_per_frame=1000)
        r = framedrv.run_loop(2048, 100, c)
        assert r is not None, "run_loop() returned None"
        assert r["iterations"] == 2048
        assert r["frames"] > 200, "the loop must advance frames, not run blind"

    def test_body_runs(self):
        seen = []
        c = framedrv.CycleClock(1000)
        framedrv.run_loop(5, 10, c, body=lambda i: seen.append(i))
        assert seen == [0, 1, 2, 3, 4]

    def test_cycles_counted(self):
        c = framedrv.CycleClock(1000)
        framedrv.run_loop(10, 7, c)
        assert c.cycles == 70

    def test_zero_iterations(self):
        c = framedrv.CycleClock(1000)
        r = framedrv.run_loop(0, 10, c)
        assert r["frames"] == 0


class TestImpossibleSpeed:
    def test_plausible(self):
        assert framedrv.detect_impossible_speed(1000, 950) is None

    def test_far_too_fast(self):
        d = framedrv.detect_impossible_speed(1000, 3)
        assert d is not None
        assert "1000" in d and "3" in d

    def test_at_tolerance_boundary(self):
        assert framedrv.detect_impossible_speed(1000, 500, tolerance=0.5) is None

    def test_slower_is_fine(self):
        assert framedrv.detect_impossible_speed(1000, 5000) is None

    def test_zero_expected(self):
        assert framedrv.detect_impossible_speed(0, 0) is None
