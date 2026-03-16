"""
Tests for Lab 1: Game Boy ROM Inspector

Uses a synthetic ROM header to verify parsing functions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from labs.lib.disasm_helpers import read_u8
import rom_inspector


def make_test_rom():
    """Build a minimal 0x150-byte ROM with a valid header.

    The title is 'TESTROM', cartridge type is ROM ONLY (0x00),
    ROM size is 32 KB (0x00), RAM size is None (0x00), and the
    header checksum is computed correctly.
    """
    rom = bytearray(0x150)

    # Entry point: NOP; JP 0x0150
    rom[0x100] = 0x00  # NOP
    rom[0x101] = 0xC3  # JP
    rom[0x102] = 0x50
    rom[0x103] = 0x01

    # Nintendo logo (normally checked by boot ROM, filled with 0x00 here)

    # Title at 0x134-0x143 (16 bytes, null-padded)
    title = b"TESTROM"
    rom[0x134:0x134 + len(title)] = title

    # Cartridge type
    rom[0x147] = 0x00  # ROM ONLY

    # ROM size
    rom[0x148] = 0x00  # 32 KB

    # RAM size
    rom[0x149] = 0x00  # None

    # Compute header checksum over 0x134-0x14C
    x = 0
    for addr in range(0x134, 0x14D):
        x = (x - rom[addr] - 1) & 0xFF
    rom[0x14D] = x

    return bytes(rom)


# Shared test ROM
TEST_ROM = make_test_rom()


class TestParseTitle:
    def test_title_extracted(self):
        title = rom_inspector.parse_title(TEST_ROM)
        assert title is not None, "parse_title() returned None -- did you implement it?"
        assert "TESTROM" in title


class TestCartridgeType:
    def test_rom_only(self):
        val, desc = rom_inspector.parse_cartridge_type(TEST_ROM)
        assert val == 0x00
        assert desc == "ROM ONLY"


class TestRomSize:
    def test_32kb(self):
        val, desc = rom_inspector.parse_rom_size(TEST_ROM)
        assert val == 0x00
        assert "32 KB" in desc


class TestRamSize:
    def test_none(self):
        val, desc = rom_inspector.parse_ram_size(TEST_ROM)
        assert val == 0x00
        assert "None" in desc


class TestChecksum:
    def test_checksum_valid(self):
        computed = rom_inspector.compute_header_checksum(TEST_ROM)
        assert computed is not None, "compute_header_checksum() returned None -- did you implement it?"
        stored = read_u8(TEST_ROM, 0x14D)
        assert computed == stored, f"Checksum mismatch: computed 0x{computed:02x}, stored 0x{stored:02x}"

    def test_validate_checksum(self):
        stored, computed, valid = rom_inspector.validate_checksum(TEST_ROM)
        assert valid, "Checksum validation failed on test ROM"
