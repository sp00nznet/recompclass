#!/usr/bin/env python3
"""
test_lab.py -- Tests for the DOL parser using a crafted minimal header.

We construct a synthetic DOL header in memory and verify that the parser
extracts the correct fields.
"""

import struct
import sys

from dol_parser import (
    DOL_HEADER_SIZE,
    NUM_TEXT_SECTIONS,
    NUM_DATA_SECTIONS,
    parse_dol,
    validate_sections,
)

tests_run = 0
tests_passed = 0


def check(condition, msg):
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        print(f"  FAIL: {msg}")


def build_minimal_dol(
    text0_offset=0x100,
    text0_addr=0x80003100,
    text0_size=0x2000,
    data0_offset=0x2100,
    data0_addr=0x80006000,
    data0_size=0x1000,
    bss_addr=0x80007000,
    bss_size=0x500,
    entry_point=0x80003100,
):
    """
    Build a minimal synthetic DOL header (256 bytes).

    Only text section 0 and data section 0 are populated; all others are zero.
    """
    # Allocate a zeroed header.
    hdr = bytearray(DOL_HEADER_SIZE)

    # Text offsets (7 entries at 0x00).
    struct.pack_into(">I", hdr, 0x00, text0_offset)

    # Data offsets (11 entries at 0x1C).
    struct.pack_into(">I", hdr, 0x1C, data0_offset)

    # Text addresses (7 entries at 0x48).
    struct.pack_into(">I", hdr, 0x48, text0_addr)

    # Data addresses (11 entries at 0x64).
    struct.pack_into(">I", hdr, 0x64, data0_addr)

    # Text sizes (7 entries at 0x90).
    struct.pack_into(">I", hdr, 0x90, text0_size)

    # Data sizes (11 entries at 0xAC).
    struct.pack_into(">I", hdr, 0xAC, data0_size)

    # BSS.
    struct.pack_into(">I", hdr, 0xD8, bss_addr)
    struct.pack_into(">I", hdr, 0xDC, bss_size)

    # Entry point.
    struct.pack_into(">I", hdr, 0xE0, entry_point)

    # Append some dummy section data so file size validates.
    padding_size = (data0_offset + data0_size) - DOL_HEADER_SIZE
    if padding_size > 0:
        hdr += bytearray(padding_size)

    return bytes(hdr)


def test_parse_basic():
    """Test basic parsing of a minimal DOL header."""
    print("--- test_parse_basic ---")

    data = build_minimal_dol()
    hdr = parse_dol(data)

    check(hdr.entry_point == 0x80003100, "entry_point")
    check(hdr.bss_address == 0x80007000, "bss_address")
    check(hdr.bss_size == 0x500, "bss_size")

    check(len(hdr.text_sections) == NUM_TEXT_SECTIONS, "7 text section slots")
    check(len(hdr.data_sections) == NUM_DATA_SECTIONS, "11 data section slots")


def test_text_section():
    """Test that text section 0 is parsed correctly."""
    print("--- test_text_section ---")

    data = build_minimal_dol()
    hdr = parse_dol(data)

    t0 = hdr.text_sections[0]
    check(t0.is_used, "text0 is used")
    check(t0.file_offset == 0x100, "text0 file_offset")
    check(t0.load_address == 0x80003100, "text0 load_address")
    check(t0.size == 0x2000, "text0 size")
    check(t0.end_address == 0x80003100 + 0x2000, "text0 end_address")
    check(t0.section_type == "text", "text0 section_type")

    # Remaining text sections should be unused.
    for i in range(1, NUM_TEXT_SECTIONS):
        check(not hdr.text_sections[i].is_used, f"text{i} is unused")


def test_data_section():
    """Test that data section 0 is parsed correctly."""
    print("--- test_data_section ---")

    data = build_minimal_dol()
    hdr = parse_dol(data)

    d0 = hdr.data_sections[0]
    check(d0.is_used, "data0 is used")
    check(d0.file_offset == 0x2100, "data0 file_offset")
    check(d0.load_address == 0x80006000, "data0 load_address")
    check(d0.size == 0x1000, "data0 size")

    for i in range(1, NUM_DATA_SECTIONS):
        check(not hdr.data_sections[i].is_used, f"data{i} is unused")


def test_all_sections():
    """Test the all_sections property."""
    print("--- test_all_sections ---")

    data = build_minimal_dol()
    hdr = parse_dol(data)

    used = hdr.all_sections
    check(len(used) == 2, "should have 2 used sections")
    types = {s.section_type for s in used}
    check("text" in types, "has a text section")
    check("data" in types, "has a data section")


def test_validation():
    """Test that validation catches out-of-bounds sections."""
    print("--- test_validation ---")

    # Build a DOL where data section extends past file end.
    data = build_minimal_dol(data0_offset=0x2100, data0_size=0xFFFF)
    hdr = parse_dol(data)

    warnings = validate_sections(hdr, file_size=len(data))
    check(len(warnings) > 0, "should warn about out-of-bounds section")


def test_too_small():
    """Test that truncated data is rejected."""
    print("--- test_too_small ---")

    try:
        parse_dol(b"\x00" * 10)
        check(False, "should have raised ValueError")
    except ValueError:
        check(True, "ValueError raised for truncated data")


if __name__ == "__main__":
    print("DOL Parser -- Test Suite\n")

    test_parse_basic()
    test_text_section()
    test_data_section()
    test_all_sections()
    test_validation()
    test_too_small()

    print(f"\n{tests_passed} / {tests_run} tests passed.")
    sys.exit(0 if tests_passed == tests_run else 1)
