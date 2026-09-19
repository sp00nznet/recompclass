"""
Tests for Lab 58: Variant Build
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import variant


def variants():
    return variant.load_variants([
        {"name": "rev-a",
         "functions": {"main": 0x1000, "init": 0x1100, "draw": 0x1200,
                       "only_a": 0x1300},
         "hints": [{"addr": 0x1150, "source": "runtime-harvested"}]},
        {"name": "rev-b",
         "functions": {"main": 0x1040, "init": 0x1140, "draw": 0x1240,
                       "only_b": 0x1340}},
    ])


class TestLoad:
    def test_returns_variants(self):
        v = variants()
        assert v is not None, "load_variants() returned None"
        assert len(v) == 2
        assert v[0].name == "rev-a"

    def test_carries_hints(self):
        assert len(variants()[0].hints) == 1

    def test_rejects_duplicate_names(self):
        import pytest
        with pytest.raises(ValueError):
            variant.load_variants([{"name": "x", "functions": {}},
                                   {"name": "x", "functions": {}}])


class TestCommon:
    def test_finds_shared(self):
        a, b = variants()
        c = variant.common_functions(a, b)
        assert c is not None, "common_functions() returned None"
        assert c == ["draw", "init", "main"]

    def test_excludes_unique(self):
        a, b = variants()
        c = variant.common_functions(a, b)
        assert "only_a" not in c and "only_b" not in c

    def test_no_overlap(self):
        a = variant.Variant("a", {"x": 1})
        b = variant.Variant("b", {"y": 2})
        assert variant.common_functions(a, b) == []


class TestDeltas:
    def test_computes_shift(self):
        a, b = variants()
        d = variant.compute_deltas(a, b)
        assert d is not None, "compute_deltas() returned None"
        assert d["main"] == 0x40

    def test_only_common(self):
        a, b = variants()
        d = variant.compute_deltas(a, b)
        assert set(d) == {"main", "init", "draw"}

    def test_negative_shift(self):
        a = variant.Variant("a", {"f": 0x2000})
        b = variant.Variant("b", {"f": 0x1F00})
        assert variant.compute_deltas(a, b)["f"] == -0x100


class TestDominant:
    def test_uniform(self):
        a, b = variants()
        dom = variant.dominant_shift(variant.compute_deltas(a, b))
        assert dom is not None, "dominant_shift() returned None"
        assert dom["shift"] == 0x40
        assert dom["count"] == 3
        assert dom["total"] == 3
        assert dom["coverage"] == 1.0

    def test_mixed(self):
        deltas = {"a": 0x40, "b": 0x40, "c": 0x40, "d": 0x80}
        dom = variant.dominant_shift(deltas)
        assert dom["shift"] == 0x40
        assert dom["count"] == 3
        assert abs(dom["coverage"] - 0.75) < 1e-9

    def test_empty(self):
        dom = variant.dominant_shift({})
        assert dom["shift"] is None
        assert dom["coverage"] == 0.0

    def test_tie_prefers_smaller_magnitude(self):
        dom = variant.dominant_shift({"a": 0x10, "b": -0x400})
        assert dom["shift"] == 0x10


class TestPortHints:
    def test_shifts_addresses(self):
        hints = [{"addr": 0x1150, "source": "runtime-harvested"}]
        ported = variant.port_hints(hints, 0x40)
        assert ported is not None, "port_hints() returned None"
        assert ported[0]["addr"] == 0x1190

    def test_records_the_port(self):
        hints = [{"addr": 0x1150, "source": "runtime-harvested"}]
        ported = variant.port_hints(hints, 0x40)
        assert "ported" in ported[0]["source"]
        assert "runtime-harvested" in ported[0]["source"]
        assert "0x40" in ported[0]["source"]

    def test_negative_shift_formatting(self):
        ported = variant.port_hints([{"addr": 0x200, "source": "scan"}], -0x20)
        assert ported[0]["addr"] == 0x1E0
        assert "-0x20" in ported[0]["source"]

    def test_does_not_mutate(self):
        hints = [{"addr": 0x1000, "source": "x"}]
        variant.port_hints(hints, 0x10)
        assert hints[0]["addr"] == 0x1000


class TestReport:
    def test_mentions_shift(self):
        a, b = variants()
        deltas = variant.compute_deltas(a, b)
        text = variant.format_delta_report(a, b, deltas,
                                           variant.dominant_shift(deltas))
        assert "0x40" in text

    def test_warns_on_divergence(self):
        a = variant.Variant("a", {"f": 0x100, "g": 0x200, "h": 0x300})
        b = variant.Variant("b", {"f": 0x110, "g": 0x260, "h": 0x390})
        deltas = variant.compute_deltas(a, b)
        text = variant.format_delta_report(a, b, deltas,
                                           variant.dominant_shift(deltas))
        assert "diverge" in text
