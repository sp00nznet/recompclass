"""
Tests for Lab 24: Flag Computation Library

Verified against documented Z80 behavior.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import flags


# ---------------------------------------------------------------------------
# ADD flags
# ---------------------------------------------------------------------------

class TestAddFlags:
    def test_returns_dict(self):
        result = flags.compute_add_flags(0, 0)
        assert result is not None, "compute_add_flags() returned None"
        assert isinstance(result, dict)
        for key in ("Z", "N", "H", "C"):
            assert key in result, f"Missing key '{key}'"

    def test_zero_plus_zero(self):
        f = flags.compute_add_flags(0, 0)
        assert f["Z"] is True      # 0 + 0 = 0
        assert f["N"] is False     # ADD clears N
        assert f["H"] is False     # no half-carry
        assert f["C"] is False     # no carry

    def test_half_carry(self):
        f = flags.compute_add_flags(0x0F, 0x01)
        assert f["Z"] is False     # result = 0x10
        assert f["H"] is True      # 0xF + 0x1 = 0x10, carry from bit 3
        assert f["C"] is False

    def test_full_carry(self):
        f = flags.compute_add_flags(0xFF, 0x01)
        assert f["Z"] is True      # (0xFF + 0x01) & 0xFF = 0x00
        assert f["C"] is True      # 0xFF + 0x01 = 0x100
        assert f["H"] is True      # 0xF + 0x1 overflows nibble

    def test_no_carries(self):
        f = flags.compute_add_flags(0x10, 0x20)
        assert f["Z"] is False
        assert f["H"] is False
        assert f["C"] is False

    def test_both_carries(self):
        f = flags.compute_add_flags(0xFF, 0xFF)
        assert f["C"] is True      # 0x1FE > 0xFF
        assert f["H"] is True      # 0xF + 0xF = 0x1E > 0x0F


# ---------------------------------------------------------------------------
# SUB flags
# ---------------------------------------------------------------------------

class TestSubFlags:
    def test_returns_dict(self):
        result = flags.compute_sub_flags(0, 0)
        assert result is not None, "compute_sub_flags() returned None"

    def test_equal_values(self):
        f = flags.compute_sub_flags(0x10, 0x10)
        assert f["Z"] is True
        assert f["N"] is True
        assert f["H"] is False
        assert f["C"] is False

    def test_borrow(self):
        f = flags.compute_sub_flags(0x00, 0x01)
        assert f["Z"] is False     # (0x00 - 0x01) & 0xFF = 0xFF
        assert f["N"] is True
        assert f["C"] is True      # borrow: 0 < 1
        assert f["H"] is True      # nibble borrow: 0x0 - 0x1 < 0

    def test_half_borrow(self):
        f = flags.compute_sub_flags(0x10, 0x01)
        assert f["Z"] is False
        assert f["H"] is True      # 0x0 - 0x1 < 0
        assert f["C"] is False     # no full borrow

    def test_no_borrows(self):
        f = flags.compute_sub_flags(0x3F, 0x0F)
        assert f["Z"] is False
        assert f["H"] is False     # 0xF - 0xF = 0, no borrow
        assert f["C"] is False


# ---------------------------------------------------------------------------
# AND flags
# ---------------------------------------------------------------------------

class TestAndFlags:
    def test_returns_dict(self):
        result = flags.compute_and_flags(0xFF, 0xFF)
        assert result is not None, "compute_and_flags() returned None"

    def test_nonzero_result(self):
        f = flags.compute_and_flags(0xFF, 0x0F)
        assert f["Z"] is False
        assert f["N"] is False
        assert f["H"] is True      # AND always sets H
        assert f["C"] is False     # AND always clears C

    def test_zero_result(self):
        f = flags.compute_and_flags(0xF0, 0x0F)
        assert f["Z"] is True
        assert f["H"] is True
        assert f["C"] is False


# ---------------------------------------------------------------------------
# INC flags
# ---------------------------------------------------------------------------

class TestIncFlags:
    def test_returns_dict(self):
        result = flags.compute_inc_flags(0, False)
        assert result is not None, "compute_inc_flags() returned None"

    def test_inc_zero(self):
        f = flags.compute_inc_flags(0, False)
        assert f["Z"] is False     # 0 + 1 = 1
        assert f["N"] is False
        assert f["H"] is False
        assert f["C"] is False     # carry preserved

    def test_inc_0xFF_wraps(self):
        f = flags.compute_inc_flags(0xFF, False)
        assert f["Z"] is True      # (0xFF + 1) & 0xFF = 0
        assert f["H"] is True      # 0xF + 1 > 0xF

    def test_inc_preserves_carry(self):
        f = flags.compute_inc_flags(0x00, True)
        assert f["C"] is True      # carry unchanged
        f2 = flags.compute_inc_flags(0x00, False)
        assert f2["C"] is False

    def test_inc_half_carry(self):
        f = flags.compute_inc_flags(0x0F, False)
        assert f["H"] is True      # 0xF + 1 = 0x10
        assert f["Z"] is False

    def test_inc_no_half_carry(self):
        f = flags.compute_inc_flags(0x0E, False)
        assert f["H"] is False     # 0xE + 1 = 0xF, no overflow


# ---------------------------------------------------------------------------
# DEC flags
# ---------------------------------------------------------------------------

class TestDecFlags:
    def test_returns_dict(self):
        result = flags.compute_dec_flags(1, False)
        assert result is not None, "compute_dec_flags() returned None"

    def test_dec_one(self):
        f = flags.compute_dec_flags(1, False)
        assert f["Z"] is True      # 1 - 1 = 0
        assert f["N"] is True
        assert f["H"] is False     # 0x1 - 0x1 = 0, no borrow
        assert f["C"] is False

    def test_dec_zero_wraps(self):
        f = flags.compute_dec_flags(0, False)
        assert f["Z"] is False     # (0 - 1) & 0xFF = 0xFF
        assert f["N"] is True
        assert f["H"] is True      # 0x0 - 0x1 < 0

    def test_dec_preserves_carry(self):
        f = flags.compute_dec_flags(5, True)
        assert f["C"] is True
        f2 = flags.compute_dec_flags(5, False)
        assert f2["C"] is False

    def test_dec_0x10(self):
        f = flags.compute_dec_flags(0x10, False)
        assert f["Z"] is False     # 0x10 - 1 = 0x0F
        assert f["H"] is True      # 0x0 - 0x1 < 0
