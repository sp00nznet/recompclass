"""
Tests for Lab 77: Endianness Two Ways
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import endian


class TestSwap32:
    def test_basic(self):
        assert endian.swap32(0x11223344) == 0x44332211

    def test_involutive(self):
        assert endian.swap32(endian.swap32(0xDEADBEEF)) == 0xDEADBEEF

    def test_zero(self):
        assert endian.swap32(0) == 0


class TestSwapOnAccess:
    def test_roundtrip(self):
        m = endian.SwapOnAccess(0x100)
        m.write32(0, 0x11223344)
        assert m.read32(0) == 0x11223344

    def test_counts_swaps(self):
        m = endian.SwapOnAccess(0x100)
        m.write32(0, 1)
        m.read32(0)
        assert m.swaps == 2

    def test_byte_read_needs_no_swap(self):
        m = endian.SwapOnAccess(0x100)
        m.write32(0, 0x11223344)
        before = m.swaps
        m.read8(0)
        assert m.swaps == before


class TestSwappedStorage:
    def test_roundtrip(self):
        m = endian.SwappedStorage(0x100)
        m.write32(0, 0x11223344)
        assert m.read32(0) == 0x11223344

    def test_word_access_is_free(self):
        m = endian.SwappedStorage(0x100)
        m.write32(0, 1)
        m.read32(0)
        assert m.swaps == 0, "aligned word access must not swap"
        assert m.xors == 0

    def test_byte_access_costs_an_xor(self):
        m = endian.SwappedStorage(0x100)
        m.write32(0, 0x11223344)
        m.read8(0)
        assert m.xors == 1

    def test_byte_order_matches_guest(self):
        # Guest big-endian word 0x11223344: byte 0 is 0x11.
        a = endian.SwapOnAccess(0x100)
        b = endian.SwappedStorage(0x100)
        a.write32(0, 0x11223344)
        b.write32(0, 0x11223344)
        assert a.read8(0) == b.read8(0)
        assert a.read8(3) == b.read8(3)


class TestCompare:
    def test_agreement(self):
        wl = [("w32", 0, 0x11223344), ("r32", 0, None), ("r8", 1, None)]
        r = endian.compare(wl)
        assert r is not None, "compare() returned None"
        assert r["agree"] is True
        assert r["mismatches"] == []

    def test_word_heavy_favours_storage(self):
        wl = [("w32", 0, 0x11223344)] + [("r32", 0, None)] * 100
        r = endian.compare(wl)
        assert r["storage_cost"] < r["swap_cost"]

    def test_byte_heavy_favours_swapping(self):
        wl = [("w32", 0, 0x11223344)] + [("r8", 1, None)] * 100
        r = endian.compare(wl)
        assert r["swap_cost"] < r["storage_cost"]
