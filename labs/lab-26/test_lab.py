"""
Tests for Lab 26: NES ROM Inspector

Uses synthetic iNES headers to verify parsing functions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import nes_inspector


def make_ines_header(prg_units=2, chr_units=1, flags6=0x00, flags7=0x00):
    """Build a minimal 16-byte iNES header."""
    header = bytearray(16)
    header[0:4] = b"NES\x1a"
    header[4] = prg_units
    header[5] = chr_units
    header[6] = flags6
    header[7] = flags7
    return bytes(header)


# ---------------------------------------------------------------------------
# Magic validation
# ---------------------------------------------------------------------------

class TestValidateMagic:
    def test_valid_magic(self):
        rom = make_ines_header()
        result = nes_inspector.validate_magic(rom)
        assert result is not None, "validate_magic() returned None"
        assert result is True

    def test_invalid_magic(self):
        rom = b"\x00" * 16
        assert nes_inspector.validate_magic(rom) is False

    def test_partial_magic(self):
        rom = bytearray(16)
        rom[0:3] = b"NES"
        rom[3] = 0x00  # should be 0x1A
        assert nes_inspector.validate_magic(bytes(rom)) is False


# ---------------------------------------------------------------------------
# PRG ROM size
# ---------------------------------------------------------------------------

class TestPrgRomSize:
    def test_two_units(self):
        rom = make_ines_header(prg_units=2)
        result = nes_inspector.parse_prg_rom_size(rom)
        assert result is not None, "parse_prg_rom_size() returned None"
        assert result == 32768  # 2 * 16384

    def test_one_unit(self):
        rom = make_ines_header(prg_units=1)
        assert nes_inspector.parse_prg_rom_size(rom) == 16384

    def test_sixteen_units(self):
        rom = make_ines_header(prg_units=16)
        assert nes_inspector.parse_prg_rom_size(rom) == 16 * 16384


# ---------------------------------------------------------------------------
# CHR ROM size
# ---------------------------------------------------------------------------

class TestChrRomSize:
    def test_one_unit(self):
        rom = make_ines_header(chr_units=1)
        result = nes_inspector.parse_chr_rom_size(rom)
        assert result is not None, "parse_chr_rom_size() returned None"
        assert result == 8192

    def test_zero_means_chr_ram(self):
        rom = make_ines_header(chr_units=0)
        assert nes_inspector.parse_chr_rom_size(rom) == 0

    def test_four_units(self):
        rom = make_ines_header(chr_units=4)
        assert nes_inspector.parse_chr_rom_size(rom) == 4 * 8192


# ---------------------------------------------------------------------------
# Mapper number
# ---------------------------------------------------------------------------

class TestMapper:
    def test_mapper_0(self):
        rom = make_ines_header(flags6=0x00, flags7=0x00)
        result = nes_inspector.parse_mapper(rom)
        assert result is not None, "parse_mapper() returned None"
        num, name = result
        assert num == 0
        assert "NROM" in name

    def test_mapper_1(self):
        # Mapper 1: low nibble in flags6 bits 4-7 = 0x1, flags7 high = 0x0
        rom = make_ines_header(flags6=0x10, flags7=0x00)
        num, name = nes_inspector.parse_mapper(rom)
        assert num == 1
        assert "MMC1" in name

    def test_mapper_4(self):
        rom = make_ines_header(flags6=0x40, flags7=0x00)
        num, name = nes_inspector.parse_mapper(rom)
        assert num == 4
        assert "MMC3" in name

    def test_mapper_high_nibble(self):
        # Mapper 66: flags6 bits 4-7 = 0x2, flags7 bits 4-7 = 0x4
        # mapper = 0x40 | 0x02 = 0x42 = 66
        rom = make_ines_header(flags6=0x20, flags7=0x40)
        num, name = nes_inspector.parse_mapper(rom)
        assert num == 66


# ---------------------------------------------------------------------------
# Mirroring
# ---------------------------------------------------------------------------

class TestMirroring:
    def test_horizontal(self):
        rom = make_ines_header(flags6=0x00)
        result = nes_inspector.parse_mirroring(rom)
        assert result is not None, "parse_mirroring() returned None"
        assert result == "Horizontal"

    def test_vertical(self):
        rom = make_ines_header(flags6=0x01)
        assert nes_inspector.parse_mirroring(rom) == "Vertical"

    def test_four_screen(self):
        rom = make_ines_header(flags6=0x08)
        assert nes_inspector.parse_mirroring(rom) == "Four-Screen"

    def test_four_screen_overrides_bit0(self):
        rom = make_ines_header(flags6=0x09)  # both bit 0 and bit 3 set
        assert nes_inspector.parse_mirroring(rom) == "Four-Screen"


# ---------------------------------------------------------------------------
# Additional flags
# ---------------------------------------------------------------------------

class TestFlags:
    def test_no_flags(self):
        rom = make_ines_header(flags6=0x00)
        result = nes_inspector.parse_flags(rom)
        assert result is not None, "parse_flags() returned None"
        assert result["battery"] is False
        assert result["trainer"] is False

    def test_battery(self):
        rom = make_ines_header(flags6=0x02)
        result = nes_inspector.parse_flags(rom)
        assert result["battery"] is True
        assert result["trainer"] is False

    def test_trainer(self):
        rom = make_ines_header(flags6=0x04)
        result = nes_inspector.parse_flags(rom)
        assert result["battery"] is False
        assert result["trainer"] is True

    def test_both_flags(self):
        rom = make_ines_header(flags6=0x06)
        result = nes_inspector.parse_flags(rom)
        assert result["battery"] is True
        assert result["trainer"] is True
