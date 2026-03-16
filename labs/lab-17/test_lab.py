#!/usr/bin/env python3
"""
test_lab.py -- Tests for the XEX2 inspector using a crafted minimal header.

We construct a synthetic XEX2 header in memory (as a bytes object) and verify
that the parser extracts the correct fields.  No real XEX2 file is needed.
"""

import struct
import sys

from xex2_inspector import (
    XEX2_MAGIC,
    OPT_HEADER_ENTRY_POINT,
    OPT_HEADER_BASE_ADDRESS,
    parse_xex2,
    format_module_flags,
    MODULE_FLAG_TITLE,
    MODULE_FLAG_USER_MODE,
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


def build_minimal_xex2(
    module_flags=0x00000001,
    pe_data_offset=0x00001000,
    security_info_offset=0x00000200,
    entry_point=0x82000000,
    base_address=0x82000000,
):
    """
    Build a minimal synthetic XEX2 header as bytes.

    Layout:
      - 24 bytes: main header
      - 8 bytes per optional header entry
    """
    optional_headers = [
        (OPT_HEADER_ENTRY_POINT, entry_point),
        (OPT_HEADER_BASE_ADDRESS, base_address),
    ]

    # Main header: magic, module_flags, pe_data_offset, reserved,
    #              security_info_offset, optional_header_count
    header = struct.pack(
        ">6I",
        XEX2_MAGIC,
        module_flags,
        pe_data_offset,
        0,  # reserved
        security_info_offset,
        len(optional_headers),
    )

    # Optional header entries.
    for hid, value in optional_headers:
        header += struct.pack(">II", hid, value)

    return header


def test_parse_basic():
    """Test basic parsing of a minimal XEX2 header."""
    print("--- test_parse_basic ---")

    data = build_minimal_xex2()
    hdr = parse_xex2(data)

    check(hdr.magic == XEX2_MAGIC, "magic should be XEX2")
    check(hdr.module_flags == 0x00000001, "module_flags should be 0x01")
    check(hdr.pe_data_offset == 0x00001000, "pe_data_offset")
    check(hdr.security_info_offset == 0x00000200, "security_info_offset")
    check(hdr.optional_header_count == 2, "optional_header_count")
    check(hdr.entry_point == 0x82000000, "entry_point extracted")
    check(hdr.base_address == 0x82000000, "base_address extracted")


def test_optional_headers():
    """Test that optional headers are enumerated correctly."""
    print("--- test_optional_headers ---")

    data = build_minimal_xex2(entry_point=0x82010000, base_address=0x82000000)
    hdr = parse_xex2(data)

    check(len(hdr.optional_headers) == 2, "should have 2 optional headers")

    ep_hdr = hdr.optional_headers[0]
    check(ep_hdr.header_id == OPT_HEADER_ENTRY_POINT, "first header is entry point")
    check(ep_hdr.data_or_offset == 0x82010000, "entry point value correct")
    check(ep_hdr.name == "Entry Point", "entry point name resolved")

    ba_hdr = hdr.optional_headers[1]
    check(ba_hdr.header_id == OPT_HEADER_BASE_ADDRESS, "second header is base address")
    check(ba_hdr.data_or_offset == 0x82000000, "base address value correct")


def test_invalid_magic():
    """Test that invalid magic is rejected."""
    print("--- test_invalid_magic ---")

    bad_data = struct.pack(">6I", 0xDEADBEEF, 0, 0, 0, 0, 0)
    try:
        parse_xex2(bad_data)
        check(False, "should have raised ValueError")
    except ValueError:
        check(True, "ValueError raised for bad magic")


def test_too_small():
    """Test that truncated data is rejected."""
    print("--- test_too_small ---")

    try:
        parse_xex2(b"\x00" * 10)
        check(False, "should have raised ValueError")
    except ValueError:
        check(True, "ValueError raised for truncated data")


def test_module_flags_display():
    """Test the module flags formatter."""
    print("--- test_module_flags_display ---")

    flags = MODULE_FLAG_TITLE | MODULE_FLAG_USER_MODE
    result = format_module_flags(flags)
    check("TITLE" in result, "TITLE flag present")
    check("USER_MODE" in result, "USER_MODE flag present")
    check("DLL" not in result, "DLL flag absent")

    check(format_module_flags(0) == "(none)", "no flags = (none)")


if __name__ == "__main__":
    print("XEX2 Inspector -- Test Suite\n")

    test_parse_basic()
    test_optional_headers()
    test_invalid_magic()
    test_too_small()
    test_module_flags_display()

    print(f"\n{tests_passed} / {tests_run} tests passed.")
    sys.exit(0 if tests_passed == tests_run else 1)
