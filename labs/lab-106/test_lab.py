"""
Tests for Lab 106: Propose and Check
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import proposecheck


CODE = (0x1000, 0x2000)
KNOWN = [(0x1000, 0x100), (0x1200, 0x80)]
TRACE = {0x1400, 0x1500}


def prop(addr, source="scan"):
    return {"addr": addr, "source": source}


class TestIndividualChecks:
    def test_alignment_ok(self):
        assert proposecheck.check_alignment(prop(0x1004), 4) is None

    def test_alignment_bad(self):
        assert proposecheck.check_alignment(prop(0x1002), 4) is not None

    def test_in_range(self):
        assert proposecheck.check_in_range(prop(0x1500), CODE) is None

    def test_out_of_range(self):
        assert proposecheck.check_in_range(prop(0x9000), CODE) is not None

    def test_mid_function_rejected(self):
        # 0x1050 is inside the function at 0x1000 of size 0x100.
        assert proposecheck.check_not_mid_function(prop(0x1050), KNOWN) is not None

    def test_function_start_is_fine(self):
        assert proposecheck.check_not_mid_function(prop(0x1000), KNOWN) is None

    def test_outside_known_is_fine(self):
        assert proposecheck.check_not_mid_function(prop(0x1400), KNOWN) is None

    def test_observed(self):
        assert proposecheck.check_observed(prop(0x1400), TRACE) is None

    def test_unobserved(self):
        assert proposecheck.check_observed(prop(0x1404), TRACE) is not None


class TestEvaluate:
    def proposals(self):
        return [
            prop(0x1400, "runtime"),      # good and observed
            prop(0x1404, "scan"),         # good, unobserved
            prop(0x1050, "scan"),         # mid-function: the civrev trap
            prop(0x9000, "scan"),         # out of range
            prop(0x1402, "scan"),         # misaligned
        ]

    def result(self):
        r = proposecheck.evaluate(self.proposals(), CODE, KNOWN, TRACE)
        assert r is not None, "evaluate() returned None"
        return r

    def test_accepts_the_good_ones(self):
        addrs = [p["addr"] for p in self.result()["accepted"]]
        assert addrs == [0x1400, 0x1404]

    def test_rejects_mid_function(self):
        rejected = {r["addr"] for r in self.result()["rejected"]}
        assert 0x1050 in rejected

    def test_rejection_gives_reasons(self):
        r = [x for x in self.result()["rejected"] if x["addr"] == 0x1050][0]
        assert any("function" in reason.lower() for reason in r["reasons"])

    def test_unobserved_is_not_rejected(self):
        addrs = [p["addr"] for p in self.result()["accepted"]]
        assert 0x1404 in addrs

    def test_observed_counted(self):
        assert self.result()["observed"] == 1

    def test_by_source(self):
        by = self.result()["by_source"]
        assert by["runtime"]["accepted"] == 1
        assert by["runtime"]["rejected"] == 0
        assert by["scan"]["rejected"] == 3

    def test_the_civrev_lesson(self):
        # Runtime-sourced proposals survive; scan-sourced ones mostly do not.
        by = self.result()["by_source"]
        assert by["runtime"]["rejected"] == 0
        assert by["scan"]["rejected"] > by["scan"]["accepted"]
