"""
Tests for Lab 61: Attribution Harness
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import attribution


def a():
    return attribution.Attribution()


class TestRecording:
    def test_draw_counts(self):
        t = a()
        t.record_draw(attribution.GUEST, 3)
        t.record_draw(attribution.HARNESS)
        s = t.session_summary()
        assert s is not None, "session_summary() returned None"
        assert s["draws"][attribution.GUEST] == 3
        assert s["draws"][attribution.HARNESS] == 1

    def test_bad_source_rejected(self):
        import pytest
        with pytest.raises(ValueError):
            a().record_draw("somewhere")

    def test_dispatch_counts(self):
        t = a()
        t.record_dispatch(True)
        t.record_dispatch(False)
        t.record_dispatch(True)
        s = t.session_summary()
        assert s["dispatch"]["native"] == 2
        assert s["dispatch"]["fallback"] == 1


class TestFrames:
    def test_frame_summary_isolated(self):
        t = a()
        t.record_draw(attribution.GUEST, 2)
        f1 = t.end_frame()
        assert f1 is not None, "end_frame() returned None"
        assert f1["draws"][attribution.GUEST] == 2
        t.record_draw(attribution.GUEST, 5)
        f2 = t.end_frame()
        assert f2["draws"][attribution.GUEST] == 5

    def test_session_accumulates(self):
        t = a()
        t.record_draw(attribution.GUEST)
        t.end_frame()
        t.record_draw(attribution.GUEST)
        t.end_frame()
        s = t.session_summary()
        assert s["draws"][attribution.GUEST] == 2
        assert s["frames"] == 2


class TestRatios:
    def test_guest_ratio(self):
        t = a()
        t.record_draw(attribution.GUEST, 3)
        t.record_draw(attribution.HARNESS, 1)
        assert abs(t.session_summary()["guest_draw_ratio"] - 0.75) < 1e-9

    def test_no_draws_is_zero_not_error(self):
        assert a().session_summary()["guest_draw_ratio"] == 0.0

    def test_native_ratio(self):
        t = a()
        t.record_dispatch(True)
        t.record_dispatch(True)
        t.record_dispatch(False)
        assert abs(t.session_summary()["native_ratio"] - (2 / 3)) < 1e-9


class TestHonestClaim:
    def claim(self, guest=0, harness=0, native=0, fallback=0):
        t = a()
        if guest:
            t.record_draw(attribution.GUEST, guest)
        if harness:
            t.record_draw(attribution.HARNESS, harness)
        for _ in range(native):
            t.record_dispatch(True)
        for _ in range(fallback):
            t.record_dispatch(False)
        c = attribution.honest_claim(t.session_summary())
        assert c is not None, "honest_claim() returned None"
        return c

    def test_nothing_drawn(self):
        assert "Nothing has been drawn" in self.claim()

    def test_all_harness_says_so(self):
        c = self.claim(harness=10)
        assert "harness" in c
        assert "has not drawn" in c

    def test_all_guest(self):
        c = self.claim(guest=10)
        assert "All 10 draws came from guest code" in c

    def test_mixed_reports_both(self):
        c = self.claim(guest=3, harness=1)
        assert "3 of 4" in c
        assert "75" in c

    def test_mentions_clean_dispatch(self):
        c = self.claim(guest=1, native=5)
        assert "5 dispatches ran native" in c

    def test_mentions_fallbacks(self):
        c = self.claim(guest=1, native=5, fallback=2)
        assert "2 of 7 dispatches fell back" in c

    def test_no_dispatch_sentence_when_none(self):
        c = self.claim(guest=1)
        assert "dispatch" not in c.lower()
