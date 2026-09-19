"""
Tests for Lab 104: Matching Decomp as Oracle
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import decomporacle


def add(a, b):
    return (a + b) & 0xFF


def add_broken(a, b):
    return (a + b) & 0xFFFF      # forgot the mask width


def sub(a, b):
    return (a - b) & 0xFF


def explodes(a, b):
    raise ValueError("unimplemented")


CASES = [(1, 2), (0xFF, 1), (0x80, 0x80)]


class TestCompareFunction:
    def test_pass(self):
        r = decomporacle.compare_function("add", CASES, add, add)
        assert r is not None, "compare_function() returned None"
        assert r["status"] == "pass"
        assert r["cases"] == 3

    def test_fail(self):
        r = decomporacle.compare_function("add", CASES, add, add_broken)
        assert r["status"] == "fail"
        assert len(r["failures"]) >= 1

    def test_failure_detail(self):
        r = decomporacle.compare_function("add", [(0xFF, 1)], add, add_broken)
        f = r["failures"][0]
        assert f["expected"] == 0 and f["actual"] == 0x100

    def test_error(self):
        r = decomporacle.compare_function("add", CASES, add, explodes)
        assert r["status"] == "error"
        assert "unimplemented" in r["message"]


class TestRunSuite:
    def suite(self):
        return {"add": CASES, "sub": CASES}

    def test_all_pass(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": add, "sub": sub})
        assert r is not None, "run_suite() returned None"
        assert r["passed"] == 2 and r["failed"] == 0

    def test_counts_failures(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": add_broken, "sub": sub})
        assert r["failed"] == 1 and r["passed"] == 1

    def test_counts_errors(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": explodes, "sub": sub})
        assert r["errors"] == 1

    def test_missing_implementation(self):
        r = decomporacle.run_suite(self.suite(), {"add": add}, {"add": add})
        assert r["missing"] == ["sub"]

    def test_sorted(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": add, "sub": sub})
        assert [x["name"] for x in r["results"]] == ["add", "sub"]


class TestCoverage:
    def test_fraction(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add", "sub", "mul", "div"])
        assert c is not None, "coverage() returned None"
        assert c["tested"] == 1
        assert abs(c["fraction"] - 0.25) < 1e-9

    def test_untested_listed(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add", "sub"])
        assert c["untested"] == ["sub"]

    def test_empty(self):
        r = decomporacle.run_suite({}, {}, {})
        assert decomporacle.coverage(r, [])["fraction"] == 0.0


class TestHonestReport:
    def test_reports_divergence(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add_broken})
        c = decomporacle.coverage(r, ["add"])
        text = decomporacle.honest_report(r, c)
        assert text is not None, "honest_report() returned None"
        assert "diverge" in text

    def test_high_coverage_pass(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add"])
        assert "match the decomp" in decomporacle.honest_report(r, c)

    def test_low_coverage_is_not_validation(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add"] + [f"f{i}" for i in range(99)])
        text = decomporacle.honest_report(r, c)
        assert "not validation" in text
