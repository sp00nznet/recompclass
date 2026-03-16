#!/usr/bin/env python3
"""
xex2_inspector.py -- Parse and display Xbox 360 XEX2 executable headers.

The XEX2 format is the primary executable format for the Xbox 360.
This script reads the header structures and displays their contents
in a human-readable format.

Usage:
    python xex2_inspector.py <path_to_xex2_file>
"""

import struct
import sys
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------

XEX2_MAGIC = 0x58455832  # "XEX2" in ASCII

# Module flags (bitfield).
MODULE_FLAG_TITLE        = 0x00000001
MODULE_FLAG_EXPORTS      = 0x00000002
MODULE_FLAG_DEBUGGER     = 0x00000004
MODULE_FLAG_DLL          = 0x00000008
MODULE_FLAG_PATCH        = 0x00000010
MODULE_FLAG_PATCH_FULL   = 0x00000020
MODULE_FLAG_PATCH_DELTA  = 0x00000040
MODULE_FLAG_USER_MODE    = 0x00000080

# Well-known optional header IDs.
OPT_HEADER_RESOURCE_INFO       = 0x000002FF
OPT_HEADER_BASE_FILE_FORMAT    = 0x000003FF
OPT_HEADER_ENTRY_POINT         = 0x00040006
OPT_HEADER_BASE_ADDRESS        = 0x00040200
OPT_HEADER_IMPORT_LIBRARIES    = 0x000103FF
OPT_HEADER_TLS_INFO            = 0x00020104
OPT_HEADER_EXECUTION_ID        = 0x00040406
OPT_HEADER_IMAGE_BASE_ADDRESS  = 0x00040201
OPT_HEADER_ORIGINAL_BASE_ADDR  = 0x00040203
OPT_HEADER_LAN_KEY             = 0x00040404
OPT_HEADER_BOUNDING_PATH       = 0x000080FF
OPT_HEADER_DEVICE_ID           = 0x00040405

# Map of known optional header IDs to names for display.
OPT_HEADER_NAMES = {
    OPT_HEADER_RESOURCE_INFO:      "Resource Info",
    OPT_HEADER_BASE_FILE_FORMAT:   "Base File Format",
    OPT_HEADER_ENTRY_POINT:        "Entry Point",
    OPT_HEADER_BASE_ADDRESS:       "Base Address",
    OPT_HEADER_IMPORT_LIBRARIES:   "Import Libraries",
    OPT_HEADER_TLS_INFO:           "TLS Info",
    OPT_HEADER_EXECUTION_ID:       "Execution ID",
    OPT_HEADER_IMAGE_BASE_ADDRESS: "Image Base Address",
    OPT_HEADER_ORIGINAL_BASE_ADDR: "Original Base Address",
    OPT_HEADER_LAN_KEY:            "LAN Key",
    OPT_HEADER_BOUNDING_PATH:      "Bounding Path",
    OPT_HEADER_DEVICE_ID:          "Device ID",
}


# ---------------------------------------------------------------------------
#  Data structures
# ---------------------------------------------------------------------------

@dataclass
class OptionalHeader:
    """Represents one optional header entry in the XEX2 header."""
    header_id: int
    data_or_offset: int  # Either the value itself or an offset, depending on size class.
    name: str = ""

    def __post_init__(self):
        self.name = OPT_HEADER_NAMES.get(self.header_id, f"Unknown (0x{self.header_id:08X})")


@dataclass
class Xex2Header:
    """Parsed XEX2 main header."""
    magic: int = 0
    module_flags: int = 0
    pe_data_offset: int = 0      # Offset to the embedded PE image data.
    reserved: int = 0
    security_info_offset: int = 0
    optional_header_count: int = 0
    optional_headers: List[OptionalHeader] = field(default_factory=list)

    # Derived / extracted values.
    entry_point: Optional[int] = None
    base_address: Optional[int] = None


# ---------------------------------------------------------------------------
#  Parsing
# ---------------------------------------------------------------------------

def parse_xex2(data: bytes) -> Xex2Header:
    """
    Parse a XEX2 header from raw bytes.

    Args:
        data: The raw bytes of the XEX2 file (or at least the header portion).

    Returns:
        A populated Xex2Header.

    Raises:
        ValueError: If the magic number does not match.
    """
    if len(data) < 24:
        raise ValueError("Data too small to contain a XEX2 header.")

    hdr = Xex2Header()

    # XEX2 header layout (all fields big-endian):
    #   0x00: uint32  magic           ("XEX2")
    #   0x04: uint32  module_flags
    #   0x08: uint32  pe_data_offset
    #   0x0C: uint32  reserved
    #   0x10: uint32  security_info_offset
    #   0x14: uint32  optional_header_count
    (
        hdr.magic,
        hdr.module_flags,
        hdr.pe_data_offset,
        hdr.reserved,
        hdr.security_info_offset,
        hdr.optional_header_count,
    ) = struct.unpack_from(">6I", data, 0)

    if hdr.magic != XEX2_MAGIC:
        raise ValueError(
            f"Invalid XEX2 magic: 0x{hdr.magic:08X} (expected 0x{XEX2_MAGIC:08X})"
        )

    # Parse optional header entries.
    # Each entry is 8 bytes: (header_id: u32, data_or_offset: u32).
    offset = 24  # Start right after the main header.
    for _ in range(hdr.optional_header_count):
        if offset + 8 > len(data):
            break
        hid, value = struct.unpack_from(">II", data, offset)
        opt = OptionalHeader(header_id=hid, data_or_offset=value)
        hdr.optional_headers.append(opt)
        offset += 8

        # Extract commonly-needed values directly.
        if hid == OPT_HEADER_ENTRY_POINT:
            hdr.entry_point = value
        elif hid == OPT_HEADER_BASE_ADDRESS:
            hdr.base_address = value

    return hdr


# ---------------------------------------------------------------------------
#  Display
# ---------------------------------------------------------------------------

def format_module_flags(flags: int) -> str:
    """Return a human-readable list of module flag names."""
    names = []
    flag_map = [
        (MODULE_FLAG_TITLE,       "TITLE"),
        (MODULE_FLAG_EXPORTS,     "EXPORTS"),
        (MODULE_FLAG_DEBUGGER,    "DEBUGGER"),
        (MODULE_FLAG_DLL,         "DLL"),
        (MODULE_FLAG_PATCH,       "PATCH"),
        (MODULE_FLAG_PATCH_FULL,  "PATCH_FULL"),
        (MODULE_FLAG_PATCH_DELTA, "PATCH_DELTA"),
        (MODULE_FLAG_USER_MODE,   "USER_MODE"),
    ]
    for bit, name in flag_map:
        if flags & bit:
            names.append(name)
    return ", ".join(names) if names else "(none)"


def display_header(hdr: Xex2Header) -> None:
    """Print a formatted display of the parsed XEX2 header."""
    print("=" * 60)
    print("XEX2 Header")
    print("=" * 60)
    print(f"  Magic:                0x{hdr.magic:08X}")
    print(f"  Module Flags:         0x{hdr.module_flags:08X} [{format_module_flags(hdr.module_flags)}]")
    print(f"  PE Data Offset:       0x{hdr.pe_data_offset:08X}")
    print(f"  Security Info Offset: 0x{hdr.security_info_offset:08X}")
    print(f"  Optional Headers:     {hdr.optional_header_count}")
    print()

    if hdr.entry_point is not None:
        print(f"  Entry Point:          0x{hdr.entry_point:08X}")
    if hdr.base_address is not None:
        print(f"  Base Address:         0x{hdr.base_address:08X}")
    print()

    if hdr.optional_headers:
        print("Optional Headers:")
        print("-" * 60)
        for opt in hdr.optional_headers:
            print(f"  [{opt.name}]")
            print(f"    ID:    0x{opt.header_id:08X}")
            print(f"    Value: 0x{opt.data_or_offset:08X}")
        print()

    # TODO: Parse and display security info structure at security_info_offset.
    # TODO: Parse import library table if OPT_HEADER_IMPORT_LIBRARIES is present.
    # TODO: Detect compressed/encrypted sections from the base file format header.


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def inspect_file(filepath: str) -> Xex2Header:
    """Load a XEX2 file and display its header information."""
    with open(filepath, "rb") as f:
        data = f.read()

    hdr = parse_xex2(data)
    display_header(hdr)
    return hdr


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <xex2_file>")
        sys.exit(1)

    try:
        inspect_file(sys.argv[1])
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)
