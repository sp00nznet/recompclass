"""
Tests for Lab 28: GBA Header Parser

Uses a synthetic GBA ROM header to verify parsing functions.
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import gba_inspector


def make_gba_header(title=b"TESTGAME", game_code=b"ATST",
                    maker_code=b"01"):
    """Build a synthetic GBA ROM header (at least 0xC0 bytes)."""
    rom = bytearray(0xC0)

    # Entry point: B to 0xC0 (standard)
    # target = 8 + (offset << 2) = 0xC0
    # offset = (0xC0 - 8) >> 2 = 0xB8 >> 2 = 0x2E
    # ARM encoding: 0xEA00002E
    struct.pack_into("<I", rom, 0, 0xEA00002E)

    # Nintendo logo placeholder (0x04 to 0x9F) -- zeros for testing

    # Game title at 0xA0 (12 bytes)
    rom[0xA0:0xA0 + len(title)] = title[:12]

    # Game code at 0xAC (4 bytes)
    rom[0xAC:0xAC + len(game_code)] = game_code[:4]

    # Maker code at 0xB0 (2 bytes)
    rom[0xB0:0xB0 + len(maker_code)] = maker_code[:2]

    # Fixed value at 0xB2
    rom[0xB2] = 0x96

    # Compute complement checksum
    checksum = 0
    for b in rom[0xA0:0xBD]:
        checksum = (checksum - b) & 0xFF
    checksum = (checksum - 0x19) & 0xFF
    rom[0xBD] = checksum

    return bytes(rom)


TEST_ROM = make_gba_header()


class TestEntryPoint:
    def test_standard_entry(self):
        result = gba_inspector.parse_entry_point(TEST_ROM)
        assert result is not None, "parse_entry_point() returned None"
        assert result == 0xC0, f"Expected 0xC0, got 0x{result:X}"

    def test_custom_entry(self):
        rom = bytearray(0xC0)
        # B to 0x100: offset = (0x100 - 8) >> 2 = 0x3E
        struct.pack_into("<I", rom, 0, 0xEA00003E)
        result = gba_inspector.parse_entry_point(bytes(rom))
        assert result == 0x100


class TestGameTitle:
    def test_title(self):
        result = gba_inspector.parse_game_title(TEST_ROM)
        assert result is not None, "parse_game_title() returned None"
        assert "TESTGAME" in result

    def test_padded_title(self):
        rom = make_gba_header(title=b"AB")
        result = gba_inspector.parse_game_title(rom)
        assert result.strip() == "AB"


class TestGameCode:
    def test_game_code(self):
        result = gba_inspector.parse_game_code(TEST_ROM)
        assert result is not None, "parse_game_code() returned None"
        assert result == "ATST"


class TestMakerCode:
    def test_maker_code(self):
        result = gba_inspector.parse_maker_code(TEST_ROM)
        assert result is not None, "parse_maker_code() returned None"
        assert result == "01"


class TestComplement:
    def test_computed_matches_stored(self):
        computed = gba_inspector.compute_complement(TEST_ROM)
        assert computed is not None, "compute_complement() returned None"
        stored = TEST_ROM[0xBD]
        assert computed == stored, \
            f"Computed 0x{computed:02X} != stored 0x{stored:02X}"

    def test_validate_valid(self):
        result = gba_inspector.validate_header(TEST_ROM)
        assert result is not None, "validate_header() returned None"
        stored, computed, valid = result
        assert valid is True

    def test_validate_invalid(self):
        bad = bytearray(TEST_ROM)
        bad[0xBD] = (bad[0xBD] + 1) & 0xFF  # corrupt checksum
        stored, computed, valid = gba_inspector.validate_header(bytes(bad))
        assert valid is False
