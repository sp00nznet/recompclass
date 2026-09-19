"""
Tests for Lab 121: Harness Validation
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import harnessval


# The subject is a small "build": a dict describing a recompiled program.
def subject():
    return {"functions": 100, "checksum": 0xABCD, "fallbacks": 0, "comment": "ok"}


def strict_harness(s):
    """Healthy when the checksum matches and nothing fell back."""
    return s["checksum"] == 0xABCD and s["fallbacks"] == 0


def vacuous_harness(s):
    """The Module 35 bug: always passes."""
    return True


MUTATIONS = [
    harnessval.Mutation("corrupt_checksum",
                        lambda s: dict(s, checksum=0x1234)),
    harnessval.Mutation("silent_fallbacks",
                        lambda s: dict(s, fallbacks=37)),
    harnessval.Mutation("cosmetic_comment",
                        lambda s: dict(s, comment="changed"),
                        should_detect=False),
]


class TestValidateHarness:
    def test_baseline(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        assert r is not None, "validate_harness() returned None"
        assert r["baseline"] is True

    def test_catches_real_defects(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        assert r["caught"] == 2
        assert r["escaped"] == []

    def test_control_correctly_ignored(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        outcomes = {x["name"]: x["outcome"] for x in r["results"]}
        assert outcomes["cosmetic_comment"] == "correctly_ignored"

    def test_vacuous_harness_exposed(self):
        r = harnessval.validate_harness(vacuous_harness, subject(), MUTATIONS)
        assert r["caught"] == 0
        assert r["escaped"] == ["corrupt_checksum", "silent_fallbacks"]

    def test_false_alarm_detected(self):
        paranoid = lambda s: s["comment"] == "ok" and strict_harness(s)
        r = harnessval.validate_harness(paranoid, subject(), MUTATIONS)
        assert r["false_alarms"] == ["cosmetic_comment"]

    def test_broken_baseline_reported(self):
        r = harnessval.validate_harness(lambda s: False, subject(), MUTATIONS)
        assert r["baseline"] is False

    def test_results_have_all_fields(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        for x in r["results"]:
            assert set(x) == {"name", "detected", "should_detect", "outcome"}

    def test_subject_not_mutated_in_place(self):
        s = subject()
        harnessval.validate_harness(strict_harness, s, MUTATIONS)
        assert s["checksum"] == 0xABCD


class TestReport:
    def test_names_escapes(self):
        r = harnessval.validate_harness(vacuous_harness, subject(), MUTATIONS)
        text = harnessval.report(r)
        assert "ESCAPED" in text
        assert "corrupt_checksum" in text

    def test_flags_broken_baseline(self):
        r = harnessval.validate_harness(lambda s: False, subject(), MUTATIONS)
        assert "BASELINE FAILED" in harnessval.report(r)
