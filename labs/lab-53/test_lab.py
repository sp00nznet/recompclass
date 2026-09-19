"""
Tests for Lab 53: Table-Driven Lifter Generation
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import isagen


SAMPLE = """
# opcode | mnemonic | operand | class | cycles | semantics
0x00 | NOP   | none  | normal   | 4  | pass
0x3E | LD_A  | imm8  | normal   | 8  | cpu.a = imm
0xC3 | JP    | imm16 | branch   | 16 | cpu.pc = imm
0xC2 | JP_NZ | imm16 | cond_branch | 12 | cpu.pc = imm if not cpu.z else cpu.pc
0xCD | CALL  | imm16 | call     | 24 | cpu.push(cpu.pc); cpu.pc = imm
0xC9 | RET   | none  | return   | 16 | cpu.pc = cpu.pop()
0xE9 | JP_HL | none  | indirect | 4  | cpu.pc = cpu.hl
"""


def parsed():
    e = isagen.parse_isa(SAMPLE)
    assert e is not None, "parse_isa() returned None"
    return e


def table():
    t = isagen.build_table(parsed())
    assert t is not None, "build_table() returned None"
    return t


class TestParse:
    def test_count(self):
        assert len(parsed()) == 7

    def test_skips_comments_and_blanks(self):
        assert all(e.mnemonic != "#" for e in parsed())

    def test_fields(self):
        first = parsed()[0]
        assert first.opcode == 0x00
        assert first.mnemonic == "NOP"
        assert first.operand == "none"
        assert first.cls == "normal"
        assert first.cycles == 4

    def test_strips_whitespace(self):
        assert parsed()[1].mnemonic == "LD_A"

    def test_hex_opcode(self):
        assert parsed()[6].opcode == 0xE9

    def test_rejects_bad_class(self):
        import pytest
        with pytest.raises(ValueError):
            isagen.parse_isa("0x00 | NOP | none | teleport | 4 | pass")

    def test_rejects_bad_operand(self):
        import pytest
        with pytest.raises(ValueError):
            isagen.parse_isa("0x00 | NOP | imm32 | normal | 4 | pass")

    def test_rejects_duplicate_opcode(self):
        import pytest
        with pytest.raises(ValueError):
            isagen.parse_isa("0x00 | NOP | none | normal | 4 | pass\n"
                             "0x00 | NOP2 | none | normal | 4 | pass")


class TestLength:
    def test_none(self):
        assert parsed()[0].length == 1

    def test_imm8(self):
        assert parsed()[1].length == 2

    def test_imm16(self):
        assert parsed()[2].length == 3


class TestTable:
    def test_size(self):
        assert len(table()) == 256

    def test_placement(self):
        assert table()[0xC3].mnemonic == "JP"

    def test_holes_are_none(self):
        assert table()[0x01] is None


class TestCoverage:
    def test_counts(self):
        c = isagen.check_coverage(table())
        assert c is not None, "check_coverage() returned None"
        assert c["defined"] == 7
        assert len(c["undefined"]) == 249

    def test_undefined_sorted(self):
        u = isagen.check_coverage(table())["undefined"]
        assert u == sorted(u)
        assert 0x01 in u
        assert 0x00 not in u


class TestEmitLifter:
    def test_is_c(self):
        src = isagen.emit_lifter(table())
        assert src is not None, "emit_lifter() returned None"
        assert "switch" in src
        assert "default:" in src

    def test_has_a_case_per_entry(self):
        src = isagen.emit_lifter(table())
        for op in (0x00, 0x3E, 0xC3, 0xE9):
            assert f"case 0x{op:02X}:" in src

    def test_no_case_for_holes(self):
        assert "case 0x01:" not in isagen.emit_lifter(table())

    def test_includes_cycles(self):
        assert "c->cycles += 24;" in isagen.emit_lifter(table())

    def test_mnemonic_in_comment(self):
        assert "JP_HL" in isagen.emit_lifter(table())


class TestEmitInterpreter:
    def test_is_python_and_runs(self):
        src = isagen.emit_interpreter(table())
        assert src is not None, "emit_interpreter() returned None"
        ns = {}
        exec(compile(src, "<generated>", "exec"), ns)
        assert "step" in ns

    def test_dispatches(self):
        ns = {}
        exec(compile(isagen.emit_interpreter(table()), "<gen>", "exec"), ns)

        class Cpu:
            cycles = 0
            a = 0
        cpu = Cpu()
        ns["step"](0x00, cpu)
        assert cpu.cycles == 4

    def test_unknown_opcode_raises(self):
        import pytest
        ns = {}
        exec(compile(isagen.emit_interpreter(table()), "<gen>", "exec"), ns)

        class Cpu:
            cycles = 0
        with pytest.raises(ValueError):
            ns["step"](0x01, Cpu())

    def test_same_cycle_costs_as_lifter(self):
        # The whole point of one table: the two backends cannot disagree.
        c_src = isagen.emit_lifter(table())
        py_src = isagen.emit_interpreter(table())
        for e in parsed():
            assert f"+= {e.cycles};" in c_src
            assert f"+= {e.cycles}" in py_src


class TestTerminators:
    def test_finds_them(self):
        t = isagen.terminators(table())
        assert 0xC3 in t and 0xC9 in t and 0xE9 in t and 0xCD in t

    def test_excludes_normal(self):
        t = isagen.terminators(table())
        assert 0x00 not in t and 0x3E not in t
