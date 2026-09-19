"""
Tests for Lab 95: Harvard Memory Model
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import harvard


def mem():
    return harvard.HarvardMemory(rom_size=0x1000, ram_size=0x200)


class TestSpaces:
    def test_fetch(self):
        m = mem()
        m.rom[0x100] = 0xAB
        assert m.fetch(0x100) == 0xAB

    def test_load_and_store(self):
        m = mem()
        m.store(0x100, 0xCD)
        assert m.load(0x100) == 0xCD

    def test_same_address_different_values(self):
        m = mem()
        m.rom[0x100] = 0xAA
        m.store(0x100, 0xBB)
        assert m.fetch(0x100) == 0xAA
        assert m.load(0x100) == 0xBB

    def test_ldc_reads_rom(self):
        m = mem()
        m.rom[0x100] = 0x77
        m.store(0x100, 0x88)
        assert m.ldc(0x100) == 0x77

    def test_rom_bounds(self):
        import pytest
        with pytest.raises(harvard.SpaceError):
            mem().fetch(0x2000)

    def test_ram_bounds(self):
        import pytest
        with pytest.raises(harvard.SpaceError):
            mem().load(0x300)

    def test_ram_address_valid_in_rom_is_still_rejected(self):
        # 0x300 is a fine ROM address and an invalid RAM one.
        import pytest
        m = mem()
        assert m.fetch(0x300) == 0
        with pytest.raises(harvard.SpaceError):
            m.load(0x300)


class TestIO:
    def test_read_handler(self):
        m = mem()
        m.map_io(0x50, lambda v: 0x5A)
        assert m.load(0x50) == 0x5A

    def test_write_handler(self):
        seen = []
        m = mem()
        m.map_io(0x50, lambda v: seen.append(v))
        m.store(0x50, 0x99)
        assert seen == [0x99]

    def test_handler_does_not_touch_ram(self):
        m = mem()
        m.map_io(0x50, lambda v: 0x5A)
        m.store(0x50, 0x99)
        assert m.ram[0x50] == 0


class TestDetectConflation:
    def test_correct_model_passes(self):
        assert harvard.detect_conflation(mem()) is None

    def test_flat_model_caught(self):
        class Flat(harvard.HarvardMemory):
            def __init__(self):
                super().__init__(rom_size=0x1000, ram_size=0x200)
                self.ram = self.rom        # the bug: one array for both
        d = harvard.detect_conflation(Flat())
        assert d is not None
