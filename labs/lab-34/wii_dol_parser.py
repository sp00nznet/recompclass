"""
Lab 34: Wii DOL Extended Parser

Parse DOL executable files for GameCube and Wii.
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOL_HEADER_SIZE = 0x100

NUM_TEXT_SECTIONS = 7
NUM_DATA_SECTIONS = 11

# Header field offsets
TEXT_OFFSETS_START = 0x0000     # 7 x uint32
DATA_OFFSETS_START = 0x001C    # 11 x uint32
TEXT_ADDRS_START = 0x0048      # 7 x uint32
DATA_ADDRS_START = 0x0064      # 11 x uint32
TEXT_SIZES_START = 0x0090      # 7 x uint32
DATA_SIZES_START = 0x00AC      # 11 x uint32
BSS_ADDR_OFFSET = 0x00D8
BSS_SIZE_OFFSET = 0x00DC
ENTRY_POINT_OFFSET = 0x00E0

# Wii MEM2 address range
MEM2_START = 0x90000000
MEM2_END = 0x94000000


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _read_u32_be(data, offset):
    """Read a big-endian 32-bit unsigned integer."""
    return struct.unpack_from(">I", data, offset)[0]


def parse_dol_header(data):
    """Parse the full DOL header into section descriptors.

    Args:
        data: bytes, at least 0x100 bytes of the DOL file.

    Returns:
        A dict with keys:
            "text_sections" - list of 7 dicts, each with keys:
                "file_offset" - int
                "load_address" - int
                "size" - int
            "data_sections" - list of 11 dicts (same keys)
            "bss_address" - int
            "bss_size" - int
            "entry_point" - int
    """
    # TODO: 1. Read the 7 text section file offsets starting at
    #          TEXT_OFFSETS_START (each is 4 bytes, big-endian).
    # TODO: 2. Read the 11 data section file offsets at DATA_OFFSETS_START.
    # TODO: 3. Read the 7 text section load addresses at TEXT_ADDRS_START.
    # TODO: 4. Read the 11 data section load addresses at DATA_ADDRS_START.
    # TODO: 5. Read the 7 text section sizes at TEXT_SIZES_START.
    # TODO: 6. Read the 11 data section sizes at DATA_SIZES_START.
    # TODO: 7. Build text_sections: combine offset[i], address[i], size[i].
    # TODO: 8. Build data_sections the same way.
    # TODO: 9. Read BSS address, BSS size, and entry point.
    # TODO: 10. Return the dict.
    pass


def get_text_sections(header):
    """Return only non-empty text sections (size > 0).

    Args:
        header: dict from parse_dol_header().

    Returns:
        List of section dicts with size > 0, preserving order.
        Each dict also gets an "index" key (0-6) for display.
    """
    # TODO: Filter header["text_sections"] to those with size > 0.
    #       Add "index": i to each.
    pass


def get_data_sections(header):
    """Return only non-empty data sections (size > 0).

    Args:
        header: dict from parse_dol_header().

    Returns:
        List of section dicts with size > 0, with "index" key (0-10).
    """
    # TODO: Same as get_text_sections but for data.
    pass


def get_entry_point(header):
    """Return the entry point address.

    Args:
        header: dict from parse_dol_header().

    Returns:
        int, the entry point address.
    """
    # TODO: Return header["entry_point"].
    pass


def get_bss_info(header):
    """Return BSS address and size.

    Args:
        header: dict from parse_dol_header().

    Returns:
        Tuple of (bss_address, bss_size).
    """
    # TODO: Return (header["bss_address"], header["bss_size"]).
    pass


def detect_platform(header):
    """Guess whether this is a GameCube or Wii DOL.

    Heuristic: if any section load address falls in the MEM2 range
    (0x90000000-0x93FFFFFF), it is a Wii DOL.

    Args:
        header: dict from parse_dol_header().

    Returns:
        "Wii" or "GameCube".
    """
    # TODO: Check all text and data sections. If any load_address
    #       is in [MEM2_START, MEM2_END), return "Wii".
    #       Otherwise return "GameCube".
    pass


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_dol_info(data):
    """Parse and display DOL header information."""
    header = parse_dol_header(data)
    if header is None:
        print("parse_dol_header() returned None -- implement the TODO sections.")
        return

    entry = get_entry_point(header)
    bss_addr, bss_size = get_bss_info(header)
    platform = detect_platform(header)

    print("=== DOL Header ===")
    print(f"Entry Point:  0x{entry:08X}")
    print(f"BSS:          0x{bss_addr:08X} (size: 0x{bss_size:08X})")
    print(f"Platform:     {platform}")

    print("\nText Sections:")
    for sec in get_text_sections(header):
        print(f"  T{sec['index']}: offset=0x{sec['file_offset']:08X}, "
              f"addr=0x{sec['load_address']:08X}, "
              f"size=0x{sec['size']:08X}")

    print("\nData Sections:")
    for sec in get_data_sections(header):
        print(f"  D{sec['index']}: offset=0x{sec['file_offset']:08X}, "
              f"addr=0x{sec['load_address']:08X}, "
              f"size=0x{sec['size']:08X}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.dol>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    if len(data) < DOL_HEADER_SIZE:
        print("Error: file too small for a DOL header.")
        sys.exit(1)

    print_dol_info(data)


if __name__ == "__main__":
    main()
