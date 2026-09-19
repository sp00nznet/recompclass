"""
Tests for Lab 70: Timing Regression Test
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import timingtest


REFERENCE = timingtest.Timeline([
    (0, "boot"), (60, "logo"), (180, "title"), (300, "menu"),
])

# Same states, far too early -- the mariopaint bug.
TOO_FAST = timingtest.Timeline([
    (0, "boot"), (1, "logo"), (4, "title"), (6, "menu"),
])

CLOSE_ENOUGH = timingtest.Timeline([
    (0, "boot"), (62, "logo"), (178, "title"), (301, "menu"),
])

MISSING_ONE = timingtest.Timeline([
    (0, "boot"), (60, "logo"), (300, "menu"),
])


class TestTimeline:
    def test_states(self):
        assert REFERENCE.states() == {"boot", "logo", "title", "menu"}

    def test_frame_of(self):
        assert REFERENCE.frame_of("title") == 180

    def test_frame_of_missing(self):
        assert REFERENCE.frame_of("credits") is None

    def test_record(self):
        t = timingtest.Timeline()
        t.record(5, "x")
        assert t.frame_of("x") == 5


class TestCompareContent:
    def test_identical(self):
        r = timingtest.compare_content(REFERENCE, REFERENCE)
        assert r is not None, "compare_content() returned None"
        assert r["match"] is True

    def test_the_weak_check_passes_the_bug(self):
        # This is the point: content comparison cannot see a pacing bug.
        assert timingtest.compare_content(REFERENCE, TOO_FAST)["match"] is True

    def test_detects_missing(self):
        r = timingtest.compare_content(REFERENCE, MISSING_ONE)
        assert r["match"] is False
        assert r["missing"] == ["title"]

    def test_detects_extra(self):
        extra = timingtest.Timeline(REFERENCE.observations + [(400, "credits")])
        r = timingtest.compare_content(REFERENCE, extra)
        assert r["extra"] == ["credits"]


class TestCompareTimeline:
    def test_identical(self):
        assert timingtest.compare_timeline(REFERENCE, REFERENCE)["match"] is True

    def test_catches_what_content_missed(self):
        r = timingtest.compare_timeline(REFERENCE, TOO_FAST)
        assert r is not None, "compare_timeline() returned None"
        assert r["match"] is False
        assert len(r["mistimed"]) >= 3

    def test_tolerance(self):
        assert timingtest.compare_timeline(REFERENCE, CLOSE_ENOUGH,
                                           tolerance=5)["match"] is True

    def test_outside_tolerance(self):
        assert timingtest.compare_timeline(REFERENCE, CLOSE_ENOUGH,
                                           tolerance=1)["match"] is False

    def test_reports_delta(self):
        r = timingtest.compare_timeline(REFERENCE, TOO_FAST)
        title = [m for m in r["mistimed"] if m["state"] == "title"][0]
        assert title["expected"] == 180
        assert title["actual"] == 4
        assert title["delta"] == -176

    def test_missing_state(self):
        r = timingtest.compare_timeline(REFERENCE, MISSING_ONE)
        assert "title" in r["missing"]

    def test_mistimed_sorted_by_expected(self):
        r = timingtest.compare_timeline(REFERENCE, TOO_FAST)
        frames = [m["expected"] for m in r["mistimed"]]
        assert frames == sorted(frames)


class TestAssertReaches:
    def test_exact(self):
        assert timingtest.assert_reaches(REFERENCE, "title", 180) is None

    def test_within_tolerance(self):
        assert timingtest.assert_reaches(REFERENCE, "title", 178, tolerance=5) is None

    def test_too_early(self):
        d = timingtest.assert_reaches(TOO_FAST, "title", 180, tolerance=5)
        assert d is not None
        assert "180" in d and "4" in d

    def test_never_reached(self):
        d = timingtest.assert_reaches(MISSING_ONE, "title", 180)
        assert d is not None
