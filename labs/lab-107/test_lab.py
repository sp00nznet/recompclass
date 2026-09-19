"""
Tests for Lab 107: Equivalence Gate
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import eqgate


def ref_add(a, b):
    return (a + b) & 0xFF


def good(a, b):
    return (a + b) % 256


def overfit(a, b):
    # Correct only on the three cases the submitter was shown.
    table = {(1, 2): 3, (2, 3): 5, (3, 4): 7}
    return table.get((a, b), 0)


def raises(a, b):
    raise ValueError("boom")


VISIBLE = [(1, 2), (2, 3), (3, 4)]


class TestGate:
    def gate(self, probes=None):
        return eqgate.Gate(ref_add, VISIBLE, probes)

    def test_accepts_correct(self):
        r = self.gate().submit(good)
        assert r is not None, "submit() returned None"
        assert r["accepted"] is True
        assert r["reason"] == ""

    def test_rejects_wrong(self):
        r = self.gate().submit(lambda a, b: 0)
        assert r["accepted"] is False
        assert r["reason"] == "mismatch"

    def test_rejects_raising(self):
        r = self.gate().submit(raises)
        assert r["reason"] == "raised"
        assert "boom" in r["detail"]

    def test_reports_failing_case(self):
        r = self.gate().submit(lambda a, b: 0)
        assert r["case"] in VISIBLE

    def test_overfit_passes_without_probes(self):
        # The gate is only as strong as its cases.
        assert self.gate().submit(overfit)["accepted"] is True

    def test_probes_catch_overfitting(self):
        g = self.gate(probes=eqgate.make_boundary_probes())
        assert g.submit(overfit)["accepted"] is False

    def test_probes_pass_a_correct_candidate(self):
        g = self.gate(probes=eqgate.make_boundary_probes())
        assert g.submit(good)["accepted"] is True


class TestStats:
    def test_counts(self):
        g = eqgate.Gate(ref_add, VISIBLE)
        g.submit(good)
        g.submit(lambda a, b: 0)
        s = g.stats()
        assert s is not None, "stats() returned None"
        assert s["submitted"] == 2
        assert s["accepted"] == 1
        assert abs(s["rate"] - 0.5) < 1e-9

    def test_reasons_tallied(self):
        g = eqgate.Gate(ref_add, VISIBLE)
        g.submit(raises)
        g.submit(lambda a, b: 0)
        assert g.stats()["reasons"]["raised"] == 1
        assert g.stats()["reasons"]["mismatch"] == 1

    def test_no_submissions(self):
        assert eqgate.Gate(ref_add, VISIBLE).stats()["rate"] == 0.0


class TestProbes:
    def test_covers_boundaries(self):
        probes = eqgate.make_boundary_probes()
        flat = {a for a, _ in probes}
        for v in (0, 1, 0x0F, 0x10, 0x7F, 0x80, 0xFF):
            assert v in flat
