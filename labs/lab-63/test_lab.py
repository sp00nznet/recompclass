"""
Tests for Lab 63: Bisect Harness
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import bisect_lift


ADDRS = [0x1000, 0x1010, 0x1020, 0x1030, 0x1040, 0x1050, 0x1060, 0x1070]
BAD = 0x1040


def good_test(lo, hi):
    """Lifting is good as long as BAD is not in the range."""
    return not bisect_lift.in_range(BAD, lo, hi)


def always_good(lo, hi):
    return True


class TestInRange:
    def test_inside(self):
        assert bisect_lift.in_range(5, 0, 10) is True

    def test_boundaries_inclusive(self):
        assert bisect_lift.in_range(0, 0, 10) is True
        assert bisect_lift.in_range(10, 0, 10) is True

    def test_outside(self):
        assert bisect_lift.in_range(11, 0, 10) is False

    def test_empty_range(self):
        assert bisect_lift.in_range(5, 10, 0) is False


class TestRunWithRange:
    def test_all_original(self):
        out = bisect_lift.run_with_range(ADDRS, 1, 0, lambda a: "o", lambda a: "l")
        assert out is not None, "run_with_range() returned None"
        assert set(out) == {"o"}

    def test_all_lifted(self):
        out = bisect_lift.run_with_range(ADDRS, 0, 0xFFFF, lambda a: "o", lambda a: "l")
        assert set(out) == {"l"}

    def test_partial(self):
        out = bisect_lift.run_with_range(ADDRS, 0x1000, 0x1020,
                                         lambda a: "o", lambda a: "l")
        assert out[:3] == ["l", "l", "l"]
        assert out[3:] == ["o"] * 5

    def test_preserves_order(self):
        out = bisect_lift.run_with_range(ADDRS, 0, 0xFFFF, lambda a: a, lambda a: a)
        assert out == ADDRS


class TestBisect:
    def test_finds_the_bad_one(self):
        assert bisect_lift.bisect(ADDRS, good_test) == BAD

    def test_returns_none_when_clean(self):
        assert bisect_lift.bisect(ADDRS, always_good) is None

    def test_first_address_bad(self):
        def t(lo, hi):
            return not bisect_lift.in_range(ADDRS[0], lo, hi)
        assert bisect_lift.bisect(ADDRS, t) == ADDRS[0]

    def test_last_address_bad(self):
        def t(lo, hi):
            return not bisect_lift.in_range(ADDRS[-1], lo, hi)
        assert bisect_lift.bisect(ADDRS, t) == ADDRS[-1]


class TestBisectLog:
    def test_returns_pair(self):
        found, log = bisect_lift.bisect_log(ADDRS, good_test)
        assert found == BAD
        assert isinstance(log, list)

    def test_log_is_logarithmic(self):
        # 8 addresses should take far fewer than 8 runs.
        _, log = bisect_lift.bisect_log(ADDRS, good_test)
        assert len(log) <= 6, f"took {len(log)} runs, expected a binary search"

    def test_log_records_outcomes(self):
        _, log = bisect_lift.bisect_log(ADDRS, good_test)
        assert all(set(e) == {"lo", "hi", "good"} for e in log)
        assert any(e["good"] is False for e in log)

    def test_format(self):
        found, log = bisect_lift.bisect_log(ADDRS, good_test)
        text = bisect_lift.format_log(found, log)
        assert "0x1040" in text
