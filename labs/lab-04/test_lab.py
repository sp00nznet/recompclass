"""
Tests for Lab 4: SM83 Lifter

Verifies that known opcodes produce correct C code output.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import sm83_lifter


class TestNop:
    def test_nop(self):
        result = sm83_lifter.lift_instruction(0x00)
        assert result is not None
        assert "nop" in result.lower()


class TestLdRegReg:
    def test_ld_b_c(self):
        result = sm83_lifter.lift_instruction(0x41)
        assert result is not None
        assert "cpu.b" in result
        assert "cpu.c" in result

    def test_ld_a_l(self):
        # LD A, L is opcode 0x7D (dst=7=A, src=5=L)
        result = sm83_lifter.lift_instruction(0x7D)
        assert result is not None
        assert "cpu.a" in result
        assert "cpu.l" in result

    def test_ld_from_hl(self):
        # LD A, (HL) is opcode 0x7E (dst=7=A, src=6=(HL))
        result = sm83_lifter.lift_instruction(0x7E)
        assert result is not None
        assert "mem_read8" in result


class TestAddA:
    def test_add_a_b(self):
        result = sm83_lifter.lift_instruction(0x80)
        assert result is not None
        assert "cpu.a" in result
        assert "SET_Z" in result
        assert "SET_N(0)" in result
        assert "SET_H_ADD" in result
        assert "SET_C_ADD" in result


class TestSubA:
    def test_sub_a_b(self):
        result = sm83_lifter.lift_instruction(0x90)
        if result is None:
            # Not yet implemented -- student TODO
            return
        assert "cpu.a" in result
        assert "SET_N(1)" in result
        assert "SET_H_SUB" in result
        assert "SET_C_SUB" in result


class TestIncDec:
    def test_inc_b(self):
        result = sm83_lifter.lift_instruction(0x04)
        if result is None:
            return
        assert "cpu.b" in result
        assert "SET_Z" in result

    def test_dec_b(self):
        result = sm83_lifter.lift_instruction(0x05)
        if result is None:
            return
        assert "cpu.b" in result
        assert "SET_N(1)" in result


class TestLogic:
    def test_and_a_b(self):
        result = sm83_lifter.lift_instruction(0xA0)
        if result is None:
            return
        assert "cpu.a" in result
        assert "&" in result or "and" in result.lower()

    def test_xor_a_b(self):
        result = sm83_lifter.lift_instruction(0xA8)
        if result is None:
            return
        assert "cpu.a" in result
        assert "^" in result or "xor" in result.lower()

    def test_or_a_b(self):
        result = sm83_lifter.lift_instruction(0xB0)
        if result is None:
            return
        assert "cpu.a" in result
        assert "|" in result or "or" in result.lower()


class TestCompare:
    def test_cp_b(self):
        result = sm83_lifter.lift_instruction(0xB8)
        if result is None:
            return
        # CP should NOT modify A
        assert "cpu.a =" not in result or "cpu.a = cpu.a" not in result
        assert "SET_Z" in result


class TestJumps:
    def test_jr_unconditional(self):
        result = sm83_lifter.lift_instruction(0x18, {"offset": 10})
        assert result is not None
        assert "cpu.pc" in result
        assert "10" in result

    def test_jr_nz(self):
        result = sm83_lifter.lift_instruction(0x20, {"offset": -5})
        assert result is not None
        assert "if" in result
        assert "FLAG_Z" in result

    def test_ret_unconditional(self):
        result = sm83_lifter.lift_instruction(0xC9)
        assert result is not None
        assert "mem_read8" in result
        assert "cpu.sp" in result

    def test_ret_conditional(self):
        result = sm83_lifter.lift_instruction(0xC0)
        assert result is not None
        assert "if" in result


class TestPushPop:
    def test_push_bc(self):
        result = sm83_lifter.lift_instruction(0xC5)
        if result is None:
            return
        assert "cpu.sp" in result

    def test_pop_bc(self):
        result = sm83_lifter.lift_instruction(0xC1)
        if result is None:
            return
        assert "cpu.sp" in result


class TestUnimplemented:
    def test_halt_returns_none(self):
        # HALT (0x76) is not implemented in this lab
        result = sm83_lifter.lift_instruction(0x76)
        assert result is None
