"""
Tests for Lab 76: Memory Access Ladder
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import memladder


def switch_bus(io_handler=None):
    return memladder.SwitchBus([
        (0x0000, 0x100, bytearray(b"\x11" * 0x100)),
        (0x0100, 0x100, bytearray(b"\x22" * 0x100)),
        (0x0200, 0x100, bytearray(b"\x33" * 0x100)),
    ], io_handler=io_handler)


class TestSwitchBus:
    def test_reads_first_region(self):
        assert switch_bus().read(0x0010) == 0x11

    def test_reads_last_region(self):
        assert switch_bus().read(0x0210) == 0x33

    def test_counts_comparisons(self):
        b = switch_bus()
        b.read(0x0210)
        assert b.comparisons == 3, "a late region costs every earlier check"

    def test_first_region_is_cheap(self):
        b = switch_bus()
        b.read(0x0010)
        assert b.comparisons == 1

    def test_unmapped_traps(self):
        import pytest
        with pytest.raises(memladder.IOTrap):
            switch_bus().read(0x9999)

    def test_unmapped_goes_to_handler(self):
        seen = []
        b = switch_bus(io_handler=lambda a: seen.append(a) or 0xAB)
        assert b.read(0x9999) == 0xAB
        assert seen == [0x9999]


class TestFlatBus:
    def test_reads(self):
        b = memladder.FlatBus(0x1000, base=0x8000)
        b.memory[0x10] = 0x55
        assert b.read(0x8010) == 0x55

    def test_one_check_per_access(self):
        b = memladder.FlatBus(0x1000, base=0x8000)
        b.read(0x8000)
        b.read(0x8FFF)
        assert b.checks == 2, "the cost must not grow with the address"

    def test_io_window_traps(self):
        import pytest
        b = memladder.FlatBus(0x1000, base=0x8000, io_range=(0x8800, 0x88FF))
        with pytest.raises(memladder.IOTrap):
            b.read(0x8810)

    def test_io_window_calls_handler(self):
        seen = []
        b = memladder.FlatBus(0x1000, base=0x8000, io_range=(0x8800, 0x88FF),
                              io_handler=lambda a: seen.append(a) or 0x7F)
        assert b.read(0x8810) == 0x7F
        assert seen == [0x8810]

    def test_outside_io_window_is_ram(self):
        b = memladder.FlatBus(0x1000, base=0x8000, io_range=(0x8800, 0x88FF),
                              io_handler=lambda a: 0x7F)
        b.memory[0x10] = 0x22
        assert b.read(0x8010) == 0x22


class TestClassifyStatic:
    def test_fast(self):
        assert memladder.classify_static(0x8010, (0x8800, 0x88FF)) == "fast"

    def test_io(self):
        assert memladder.classify_static(0x8810, (0x8800, 0x88FF)) == "io"

    def test_dynamic(self):
        assert memladder.classify_static(None, (0x8800, 0x88FF)) == "dynamic"

    def test_no_io_range(self):
        assert memladder.classify_static(0x8010, None) == "fast"


class TestBenchmark:
    def test_flat_beats_switch(self):
        accesses = [0x0210] * 100
        sw = memladder.benchmark(switch_bus(), accesses)
        assert sw is not None, "benchmark() returned None"

        flat = memladder.FlatBus(0x1000, base=0x0000)
        fl = memladder.benchmark(flat, accesses)
        assert fl["work"] < sw["work"]

    def test_reports_per_access(self):
        r = memladder.benchmark(switch_bus(), [0x0210] * 10)
        assert abs(r["work_per_access"] - 3.0) < 1e-9
