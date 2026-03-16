"""
Tests for Lab 34: Wii DOL Extended Parser

Uses synthetic DOL headers to verify parsing.
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import wii_dol_parser


def make_dol_header(text_sections=None, data_sections=None,
                    bss_addr=0, bss_size=0, entry_point=0):
    """Build a synthetic DOL header.

    Args:
        text_sections: list of (file_offset, load_address, size) tuples.
                       Max 7 entries.
        data_sections: list of (file_offset, load_address, size) tuples.
                       Max 11 entries.
        bss_addr: BSS address.
        bss_size: BSS size.
        entry_point: entry point address.

    Returns:
        bytes, a 0x100-byte DOL header.
    """
    header = bytearray(0x100)

    if text_sections is None:
        text_sections = []
    if data_sections is None:
        data_sections = []

    # Text section offsets (0x0000)
    for i, (off, _, _) in enumerate(text_sections[:7]):
        struct.pack_into(">I", header, 0x0000 + i * 4, off)
    # Data section offsets (0x001C)
    for i, (off, _, _) in enumerate(data_sections[:11]):
        struct.pack_into(">I", header, 0x001C + i * 4, off)
    # Text section addresses (0x0048)
    for i, (_, addr, _) in enumerate(text_sections[:7]):
        struct.pack_into(">I", header, 0x0048 + i * 4, addr)
    # Data section addresses (0x0064)
    for i, (_, addr, _) in enumerate(data_sections[:11]):
        struct.pack_into(">I", header, 0x0064 + i * 4, addr)
    # Text section sizes (0x0090)
    for i, (_, _, sz) in enumerate(text_sections[:7]):
        struct.pack_into(">I", header, 0x0090 + i * 4, sz)
    # Data section sizes (0x00AC)
    for i, (_, _, sz) in enumerate(data_sections[:11]):
        struct.pack_into(">I", header, 0x00AC + i * 4, sz)

    struct.pack_into(">I", header, 0x00D8, bss_addr)
    struct.pack_into(">I", header, 0x00DC, bss_size)
    struct.pack_into(">I", header, 0x00E0, entry_point)

    return bytes(header)


# GameCube-style header
GC_HEADER = make_dol_header(
    text_sections=[
        (0x00000100, 0x80003100, 0x00200000),
        (0x00200100, 0x80203100, 0x00050000),
    ],
    data_sections=[
        (0x00250100, 0x80300000, 0x00080000),
    ],
    bss_addr=0x80400000,
    bss_size=0x00100000,
    entry_point=0x800060A4,
)

# Wii-style header (has MEM2 data section)
WII_HEADER = make_dol_header(
    text_sections=[
        (0x00000100, 0x80003100, 0x00300000),
    ],
    data_sections=[
        (0x00300100, 0x80400000, 0x00100000),
        (0x00400100, 0x90000000, 0x00200000),  # MEM2
    ],
    bss_addr=0x80600000,
    bss_size=0x00050000,
    entry_point=0x800061A0,
)


# ---------------------------------------------------------------------------
# parse_dol_header
# ---------------------------------------------------------------------------

class TestParseDolHeader:
    def test_returns_dict(self):
        result = wii_dol_parser.parse_dol_header(GC_HEADER)
        assert result is not None, "parse_dol_header() returned None"
        assert isinstance(result, dict)

    def test_text_sections_count(self):
        result = wii_dol_parser.parse_dol_header(GC_HEADER)
        assert len(result["text_sections"]) == 7

    def test_data_sections_count(self):
        result = wii_dol_parser.parse_dol_header(GC_HEADER)
        assert len(result["data_sections"]) == 11

    def test_entry_point(self):
        result = wii_dol_parser.parse_dol_header(GC_HEADER)
        assert result["entry_point"] == 0x800060A4

    def test_bss(self):
        result = wii_dol_parser.parse_dol_header(GC_HEADER)
        assert result["bss_address"] == 0x80400000
        assert result["bss_size"] == 0x00100000

    def test_text_section_values(self):
        result = wii_dol_parser.parse_dol_header(GC_HEADER)
        t0 = result["text_sections"][0]
        assert t0["file_offset"] == 0x00000100
        assert t0["load_address"] == 0x80003100
        assert t0["size"] == 0x00200000


# ---------------------------------------------------------------------------
# get_text_sections / get_data_sections
# ---------------------------------------------------------------------------

class TestGetSections:
    def test_text_nonempty(self):
        header = wii_dol_parser.parse_dol_header(GC_HEADER)
        result = wii_dol_parser.get_text_sections(header)
        assert result is not None, "get_text_sections() returned None"
        assert len(result) == 2  # only 2 non-empty text sections

    def test_data_nonempty(self):
        header = wii_dol_parser.parse_dol_header(GC_HEADER)
        result = wii_dol_parser.get_data_sections(header)
        assert len(result) == 1

    def test_section_has_index(self):
        header = wii_dol_parser.parse_dol_header(GC_HEADER)
        text = wii_dol_parser.get_text_sections(header)
        assert "index" in text[0]
        assert text[0]["index"] == 0
        assert text[1]["index"] == 1

    def test_wii_data_sections(self):
        header = wii_dol_parser.parse_dol_header(WII_HEADER)
        result = wii_dol_parser.get_data_sections(header)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# entry point and BSS
# ---------------------------------------------------------------------------

class TestEntryAndBss:
    def test_entry_point(self):
        header = wii_dol_parser.parse_dol_header(GC_HEADER)
        assert wii_dol_parser.get_entry_point(header) == 0x800060A4

    def test_bss_info(self):
        header = wii_dol_parser.parse_dol_header(GC_HEADER)
        addr, size = wii_dol_parser.get_bss_info(header)
        assert addr == 0x80400000
        assert size == 0x00100000


# ---------------------------------------------------------------------------
# detect_platform
# ---------------------------------------------------------------------------

class TestDetectPlatform:
    def test_gamecube(self):
        header = wii_dol_parser.parse_dol_header(GC_HEADER)
        result = wii_dol_parser.detect_platform(header)
        assert result is not None, "detect_platform() returned None"
        assert result == "GameCube"

    def test_wii(self):
        header = wii_dol_parser.parse_dol_header(WII_HEADER)
        result = wii_dol_parser.detect_platform(header)
        assert result == "Wii"
