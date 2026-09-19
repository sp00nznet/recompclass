"""
Tests for Lab 119: Verified Lifting Rules
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import verifylift


def ref_add(a, b, flag=False):
    total = a + b + (1 if flag else 0)
    return {"result": total & 0xFF, "carry": total > 0xFF,
            "half": (a & 0xF) + (b & 0xF) + (1 if flag else 0) > 0xF}


def good_add(a, b, flag=False):
    carry_in = 1 if flag else 0
    total = a + b + carry_in
    return {"result": total % 256, "carry": total >= 256,
            "half": ((a & 0xF) + (b & 0xF) + carry_in) >= 16}


def one_bad_input(a, b, flag=False):
    # Wrong for exactly one pair out of 65,536.
    d = ref_add(a, b, flag)
    if a == 0x7F and b == 0x01:
        d = dict(d, half=not d["half"])
    return d


class TestExhaustive:
    def test_verifies_correct(self):
        r = verifylift.exhaustive_verify(ref_add, good_add, width=4)
        assert r is not None, "exhaustive_verify() returned None"
        assert r["verified"] is True
        assert r["checked"] == 256

    def test_finds_the_single_bad_input(self):
        r = verifylift.exhaustive_verify(ref_add, one_bad_input, width=8)
        assert r["verified"] is False
        assert r["first_bad"][:2] == (0x7F, 0x01)

    def test_reports_values(self):
        r = verifylift.exhaustive_verify(ref_add, one_bad_input, width=8)
        assert r["expected"] != r["actual"]

    def test_flag_states(self):
        r = verifylift.exhaustive_verify(ref_add, good_add, width=4,
                                         flag_states=(False, True))
        assert r["checked"] == 512

    def test_arity_one(self):
        inc = lambda a, flag=False: {"result": (a + 1) & 0xFF}
        r = verifylift.exhaustive_verify(inc, inc, width=8, arity=1)
        assert r["verified"] is True
        assert r["checked"] == 256


class TestSampled:
    def test_passes_correct(self):
        r = verifylift.sampled_verify(ref_add, good_add, trials=1000, seed=1)
        assert r is not None, "sampled_verify() returned None"
        assert r["verified"] is True

    def test_deterministic(self):
        a = verifylift.sampled_verify(ref_add, one_bad_input, trials=500, seed=7)
        b = verifylift.sampled_verify(ref_add, one_bad_input, trials=500, seed=7)
        assert a["first_bad"] == b["first_bad"]

    def test_records_seed(self):
        assert verifylift.sampled_verify(ref_add, good_add, trials=10, seed=3)["seed"] == 3


class TestCompare:
    def test_sampling_misses_the_needle(self):
        r = verifylift.compare_approaches(ref_add, one_bad_input,
                                          trials=1000, seed=1)
        assert r is not None, "compare_approaches() returned None"
        assert r["exhaustive"]["verified"] is False
        assert r["missed"] is True

    def test_space_size(self):
        r = verifylift.compare_approaches(ref_add, good_add, trials=10, seed=1)
        assert r["space_size"] == 65536

    def test_sampled_fraction(self):
        r = verifylift.compare_approaches(ref_add, good_add, trials=6554, seed=1)
        assert abs(r["sampled_fraction"] - 0.1) < 0.01

    def test_no_miss_when_both_pass(self):
        r = verifylift.compare_approaches(ref_add, good_add, trials=100, seed=1)
        assert r["missed"] is False
