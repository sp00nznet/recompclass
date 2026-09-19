"""
Tests for Lab 67: Triage Tool
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import triage


def rep(func, insn, kind="divergence", seed=0):
    return {"func": func, "insn": insn, "kind": kind, "seed": seed}


REPORTS = [
    rep(0x1000, "add.w", seed=1),
    rep(0x1000, "add.w", seed=2),
    rep(0x1000, "add.w", seed=3),
    rep(0x2000, "ld.b", kind="crash", seed=4),
    rep(0x3000, "mul", seed=5),
]

TRACE = {0x1000: 10, 0x2000: 5000, 0x3000: 0}


class TestFingerprint:
    def test_tuple(self):
        f = triage.fingerprint(rep(0x1000, "add.w"))
        assert f is not None, "fingerprint() returned None"
        assert f == (0x1000, "add.w", "divergence")

    def test_same_bug_same_key(self):
        assert triage.fingerprint(rep(0x1000, "add.w", seed=1)) == \
               triage.fingerprint(rep(0x1000, "add.w", seed=9))

    def test_kind_matters(self):
        assert triage.fingerprint(rep(0x1000, "add.w", "crash")) != \
               triage.fingerprint(rep(0x1000, "add.w", "divergence"))

    def test_bad_kind(self):
        import pytest
        with pytest.raises(ValueError):
            triage.fingerprint(rep(0x1000, "add.w", "weird"))


class TestDeduplicate:
    def test_collapses(self):
        groups = triage.deduplicate(REPORTS)
        assert groups is not None, "deduplicate() returned None"
        assert len(groups) == 3

    def test_counts(self):
        groups = triage.deduplicate(REPORTS)
        by_func = {g["func"]: g for g in groups}
        assert by_func[0x1000]["count"] == 3
        assert by_func[0x2000]["count"] == 1

    def test_keeps_examples(self):
        groups = triage.deduplicate(REPORTS)
        by_func = {g["func"]: g for g in groups}
        assert len(by_func[0x1000]["examples"]) == 3
        assert by_func[0x1000]["examples"][0]["seed"] == 1

    def test_first_seen_order(self):
        groups = triage.deduplicate(REPORTS)
        assert [g["func"] for g in groups] == [0x1000, 0x2000, 0x3000]

    def test_empty(self):
        assert triage.deduplicate([]) == []


class TestRank:
    def test_reach_dominates(self):
        ranked = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert ranked is not None, "rank() returned None"
        assert ranked[0]["func"] == 0x2000      # reach 5000

    def test_unreached_last(self):
        ranked = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert ranked[-1]["func"] == 0x3000     # reach 0

    def test_adds_reach(self):
        ranked = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert ranked[0]["reach"] == 5000

    def test_missing_from_trace_is_zero(self):
        ranked = triage.rank(triage.deduplicate([rep(0x9999, "x")]), {})
        assert ranked[0]["reach"] == 0

    def test_divergence_beats_crash_at_equal_reach(self):
        reports = [rep(0x100, "a", "crash"), rep(0x200, "b", "divergence")]
        ranked = triage.rank(triage.deduplicate(reports), {0x100: 7, 0x200: 7})
        assert ranked[0]["kind"] == "divergence"

    def test_deterministic(self):
        a = triage.rank(triage.deduplicate(REPORTS), TRACE)
        b = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert [g["func"] for g in a] == [g["func"] for g in b]


class TestTriage:
    def test_counts(self):
        r = triage.triage(REPORTS, TRACE)
        assert r is not None, "triage() returned None"
        assert r["total"] == 5
        assert r["unique"] == 3

    def test_groups_ranked(self):
        r = triage.triage(REPORTS, TRACE)
        assert r["groups"][0]["func"] == 0x2000

    def test_format(self):
        text = triage.format_triage(triage.triage(REPORTS, TRACE))
        assert "3 distinct" in text
        assert "reach=5000" in text
