"""
Tests for Lab 55: Synthetic Fixture Suite
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import fixtures


def toy_lifter(data):
    """A deterministic reference lifter for testing the harness itself."""
    out = []
    i = 0
    names = {v[0]: (k, v[1]) for k, v in fixtures.OPCODES.items()}
    while i < len(data):
        mnemonic, nops = names[data[i]]
        if nops == 0:
            out.append(f"{i:04X}: {mnemonic}")
        elif nops == 1:
            out.append(f"{i:04X}: {mnemonic} 0x{data[i+1]:02X}")
        else:
            val = data[i + 1] | (data[i + 2] << 8)
            out.append(f"{i:04X}: {mnemonic} 0x{val:04X}")
        i += 1 + nops
    return "\n".join(out)


class TestAssemble:
    def test_no_operand(self):
        assert fixtures.assemble(["nop"]) == bytes([0x00])

    def test_byte_operand(self):
        assert fixtures.assemble(["ld_a 0x42"]) == bytes([0x3E, 0x42])

    def test_word_operand_little_endian(self):
        assert fixtures.assemble(["jp 0x1234"]) == bytes([0xC3, 0x34, 0x12])

    def test_multiple(self):
        data = fixtures.assemble(["nop", "ret"])
        assert data == bytes([0x00, 0xC9])

    def test_skips_blanks_and_comments(self):
        data = fixtures.assemble(["", "; a comment", "nop"])
        assert data == bytes([0x00])

    def test_unknown_mnemonic(self):
        import pytest
        with pytest.raises(ValueError):
            fixtures.assemble(["frobnicate"])

    def test_missing_operand(self):
        import pytest
        with pytest.raises(ValueError):
            fixtures.assemble(["jp"])

    def test_unexpected_operand(self):
        import pytest
        with pytest.raises(ValueError):
            fixtures.assemble(["nop 0x12"])


class TestRunFixture:
    def test_pass(self):
        f = fixtures.Fixture("nop", ["nop"], expected="0000: nop")
        r = fixtures.run_fixture(f, toy_lifter)
        assert r is not None, "run_fixture() returned None"
        assert r["status"] == "pass"
        assert r["diff"] == ""

    def test_fail_produces_diff(self):
        f = fixtures.Fixture("nop", ["nop"], expected="0000: something else")
        r = fixtures.run_fixture(f, toy_lifter)
        assert r["status"] == "fail"
        assert "nop" in r["diff"]

    def test_no_golden_is_not_a_pass(self):
        f = fixtures.Fixture("nop", ["nop"])
        r = fixtures.run_fixture(f, toy_lifter)
        assert r["status"] == "no_golden"

    def test_records_actual(self):
        f = fixtures.Fixture("jp", ["jp 0x1234"], expected="wrong")
        r = fixtures.run_fixture(f, toy_lifter)
        assert "0x1234" in r["actual"]

    def test_records_name(self):
        f = fixtures.Fixture("my-case", ["nop"], expected="0000: nop")
        assert fixtures.run_fixture(f, toy_lifter)["name"] == "my-case"


class TestRunSuite:
    def suite(self):
        return [
            fixtures.Fixture("ok", ["nop"], expected="0000: nop"),
            fixtures.Fixture("bad", ["ret"], expected="nope"),
            fixtures.Fixture("new", ["nop"]),
        ]

    def test_counts(self):
        s = fixtures.run_suite(self.suite(), toy_lifter)
        assert s is not None, "run_suite() returned None"
        assert s["passed"] == 1
        assert s["failed"] == 1
        assert s["no_golden"] == 1

    def test_results_in_order(self):
        s = fixtures.run_suite(self.suite(), toy_lifter)
        assert [r["name"] for r in s["results"]] == ["ok", "bad", "new"]

    def test_empty_suite(self):
        s = fixtures.run_suite([], toy_lifter)
        assert s["passed"] == 0 and s["failed"] == 0


class TestRegenerate:
    def test_produces_goldens(self):
        fs = [fixtures.Fixture("a", ["nop"]), fixtures.Fixture("b", ["ret"])]
        new = fixtures.regenerate(fs, toy_lifter)
        assert new is not None, "regenerate() returned None"
        assert new["a"] == "0000: nop"
        assert new["b"] == "0000: ret"

    def test_does_not_mutate_fixtures(self):
        fs = [fixtures.Fixture("a", ["nop"])]
        fixtures.regenerate(fs, toy_lifter)
        assert fs[0].expected is None, \
            "regenerate() must not update fixtures in place -- a human reviews the diff"
