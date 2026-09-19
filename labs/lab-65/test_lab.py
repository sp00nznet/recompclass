"""
Tests for Lab 65: Instruction Fuzzer
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import insnfuzz


def add_ref(a, b):
    r = (a + b) & 0xFF
    return {"result": r, "carry": a + b > 0xFF,
            "half": (a & 0xF) + (b & 0xF) > 0xF, "zero": r == 0}


def add_bad_half(a, b):
    d = add_ref(a, b)
    d["half"] = (a & 0xF) + (b & 0xF) >= 0xF   # off by one
    return d


class TestInterestingValues:
    def test_includes_boundaries_8bit(self):
        v = insnfuzz.interesting_values(8)
        assert v is not None, "interesting_values() returned None"
        for expected in (0x00, 0x0F, 0x10, 0x7F, 0x80, 0xFF):
            assert expected in v, f"missing 0x{expected:02X}"

    def test_sorted_unique(self):
        v = insnfuzz.interesting_values(8)
        assert v == sorted(set(v))

    def test_within_range(self):
        assert all(0 <= x <= 0xFFFF for x in insnfuzz.interesting_values(16))

    def test_16bit_signed_boundary(self):
        v = insnfuzz.interesting_values(16)
        assert 0x8000 in v and 0x7FFF in v


class TestGenOperand:
    def test_in_range(self):
        rng = __import__("random").Random(1)
        for _ in range(200):
            assert 0 <= insnfuzz.gen_operand(rng, 8) <= 0xFF

    def test_pure_edges(self):
        rng = __import__("random").Random(1)
        edges = set(insnfuzz.interesting_values(8))
        for _ in range(50):
            assert insnfuzz.gen_operand(rng, 8, edge_bias=1.0) in edges

    def test_uniform_reaches_non_edges(self):
        rng = __import__("random").Random(7)
        edges = set(insnfuzz.interesting_values(8))
        drawn = {insnfuzz.gen_operand(rng, 8, edge_bias=0.0) for _ in range(200)}
        assert drawn - edges, "edge_bias=0.0 should produce non-edge values"


class TestFuzzInstruction:
    def test_no_divergence_when_same(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=200, seed=1)
        assert r is not None, "fuzz_instruction() returned None"
        assert r["failed"] is False
        assert r["trials"] == 200

    def test_finds_the_half_carry_bug(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half,
                                      trials=2000, seed=1, edge_bias=0.5)
        assert r["failed"] is True
        assert r["operands"] is not None

    def test_deterministic(self):
        a = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=42)
        b = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=42)
        assert a["operands"] == b["operands"]

    def test_different_seeds_differ(self):
        a = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=10, seed=1)
        b = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=10, seed=2)
        assert a["seed"] != b["seed"]

    def test_reports_both_results(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=3)
        assert r["expected"] != r["actual"]

    def test_arity_one(self):
        r = insnfuzz.fuzz_instruction("inc", lambda a: {"r": (a + 1) & 0xFF},
                                      lambda a: {"r": (a + 1) & 0xFF},
                                      trials=50, seed=1, arity=1)
        assert r["failed"] is False


class TestShrink:
    def test_shrinks_to_boundary(self):
        # Fails whenever the low nibbles sum to exactly 0x0F + 1.
        def fails(ops):
            a, b = ops
            return (a & 0xF) + (b & 0xF) == 0x10
        small = insnfuzz.shrink_case((0x3F, 0xA1), fails)
        assert small is not None, "shrink_case() returned None"
        assert fails(small)
        assert sum(small) <= 0x3F + 0xA1

    def test_returns_input_when_not_failing(self):
        assert insnfuzz.shrink_case((1, 2), lambda ops: False) == (1, 2)

    def test_terminates(self):
        def fails(ops):
            return True
        result = insnfuzz.shrink_case((0xAB, 0xCD), fails)
        assert result == (0x00, 0x00)


class TestFormat:
    def test_clean(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=10, seed=5)
        assert "no divergence" in insnfuzz.format_result(r)

    def test_failure_mentions_seed(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=9)
        assert "seed 9" in insnfuzz.format_result(r)
