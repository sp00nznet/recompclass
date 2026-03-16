#!/usr/bin/env python3
"""
dol_parser.py -- Parse GameCube/Wii DOL executable files.

The DOL format is straightforward: a fixed-size header describing up to
7 text sections and 11 data sections, followed by the raw section data.

Usage:
    python dol_parser.py <path_to_dol_file>
"""

import struct
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------

DOL_HEADER_SIZE = 0x100   # The header is always 256 bytes.
NUM_TEXT_SECTIONS = 7
NUM_DATA_SECTIONS = 11

# ---------------------------------------------------------------------------
#  Data structures
# ---------------------------------------------------------------------------

@dataclass
class DolSection:
    """Represents one section (text or data) in a DOL file."""
    index: int
    section_type: str    # "text" or "data"
    file_offset: int
    load_address: int
    size: int

    @property
    def end_address(self) -> int:
        return self.load_address + self.size

    @property
    def is_used(self) -> bool:
        """A section is unused if all its fields are zero."""
        return self.file_offset != 0 or self.load_address != 0 or self.size != 0

    def __str__(self) -> str:
        return (
            f"{self.section_type}{self.index}: "
            f"file=0x{self.file_offset:08X}  "
            f"addr=0x{self.load_address:08X}  "
            f"size=0x{self.size:08X} ({self.size} bytes)"
        )


@dataclass
class DolHeader:
    """Parsed DOL header."""
    text_sections: List[DolSection] = field(default_factory=list)
    data_sections: List[DolSection] = field(default_factory=list)
    bss_address: int = 0
    bss_size: int = 0
    entry_point: int = 0

    @property
    def all_sections(self) -> List[DolSection]:
        """Return all used sections (text + data)."""
        return [s for s in self.text_sections + self.data_sections if s.is_used]


# ---------------------------------------------------------------------------
#  Parsing
# ---------------------------------------------------------------------------

def parse_dol(data: bytes) -> DolHeader:
    """
    Parse a DOL header from raw bytes.

    Args:
        data: The raw bytes of the DOL file (at least DOL_HEADER_SIZE bytes).

    Returns:
        A populated DolHeader.

    Raises:
        ValueError: If the data is too small.
    """
    if len(data) < DOL_HEADER_SIZE:
        raise ValueError(
            f"Data too small ({len(data)} bytes); need at least {DOL_HEADER_SIZE}."
        )

    hdr = DolHeader()

    # Unpack all header fields at once.
    # Text offsets: 7 x uint32 at 0x00
    text_offsets = struct.unpack_from(">7I", data, 0x00)
    # Data offsets: 11 x uint32 at 0x1C
    data_offsets = struct.unpack_from(">11I", data, 0x1C)
    # Text addresses: 7 x uint32 at 0x48
    text_addrs = struct.unpack_from(">7I", data, 0x48)
    # Data addresses: 11 x uint32 at 0x64
    data_addrs = struct.unpack_from(">11I", data, 0x64)
    # Text sizes: 7 x uint32 at 0x90
    text_sizes = struct.unpack_from(">7I", data, 0x90)
    # Data sizes: 11 x uint32 at 0xAC
    data_sizes = struct.unpack_from(">11I", data, 0xAC)

    # BSS and entry point.
    hdr.bss_address = struct.unpack_from(">I", data, 0xD8)[0]
    hdr.bss_size    = struct.unpack_from(">I", data, 0xDC)[0]
    hdr.entry_point = struct.unpack_from(">I", data, 0xE0)[0]

    # Build section lists.
    for i in range(NUM_TEXT_SECTIONS):
        sec = DolSection(
            index=i,
            section_type="text",
            file_offset=text_offsets[i],
            load_address=text_addrs[i],
            size=text_sizes[i],
        )
        hdr.text_sections.append(sec)

    for i in range(NUM_DATA_SECTIONS):
        sec = DolSection(
            index=i,
            section_type="data",
            file_offset=data_offsets[i],
            load_address=data_addrs[i],
            size=data_sizes[i],
        )
        hdr.data_sections.append(sec)

    return hdr


# ---------------------------------------------------------------------------
#  Validation
# ---------------------------------------------------------------------------

def validate_sections(hdr: DolHeader, file_size: int) -> List[str]:
    """
    Validate section boundaries against the file size.

    Returns a list of warning strings (empty if all is well).
    """
    warnings = []

    for sec in hdr.all_sections:
        end_in_file = sec.file_offset + sec.size
        if end_in_file > file_size:
            warnings.append(
                f"{sec.section_type}{sec.index}: file range "
                f"0x{sec.file_offset:08X}-0x{end_in_file:08X} exceeds "
                f"file size 0x{file_size:08X}"
            )

    # TODO: Detect overlapping sections in the memory map.
    # For each pair of used sections, check if their [load_address, end_address)
    # ranges overlap.

    return warnings


# ---------------------------------------------------------------------------
#  Display
# ---------------------------------------------------------------------------

def display_header(hdr: DolHeader, file_size: Optional[int] = None) -> None:
    """Print a formatted display of the parsed DOL header."""
    print("=" * 65)
    print("DOL Header")
    print("=" * 65)
    print(f"  Entry Point:  0x{hdr.entry_point:08X}")
    print(f"  BSS Address:  0x{hdr.bss_address:08X}")
    print(f"  BSS Size:     0x{hdr.bss_size:08X} ({hdr.bss_size} bytes)")
    print()

    # Text sections.
    print("Text Sections:")
    print("-" * 65)
    for sec in hdr.text_sections:
        if sec.is_used:
            print(f"  {sec}")
    unused_text = sum(1 for s in hdr.text_sections if not s.is_used)
    if unused_text:
        print(f"  ({unused_text} unused text section(s) omitted)")
    print()

    # Data sections.
    print("Data Sections:")
    print("-" * 65)
    for sec in hdr.data_sections:
        if sec.is_used:
            print(f"  {sec}")
    unused_data = sum(1 for s in hdr.data_sections if not s.is_used)
    if unused_data:
        print(f"  ({unused_data} unused data section(s) omitted)")
    print()

    # Memory map (sorted by load address).
    used = hdr.all_sections
    if used:
        print("Memory Map (sorted by load address):")
        print("-" * 65)
        for sec in sorted(used, key=lambda s: s.load_address):
            bar_len = min(sec.size // 1024, 40)  # 1 char per KB, max 40.
            bar = "#" * max(bar_len, 1)
            print(
                f"  0x{sec.load_address:08X} - 0x{sec.end_address:08X}  "
                f"{sec.section_type}{sec.index}  {bar}"
            )
        # Include BSS in the map.
        if hdr.bss_size > 0:
            bss_end = hdr.bss_address + hdr.bss_size
            bar_len = min(hdr.bss_size // 1024, 40)
            bar = "." * max(bar_len, 1)
            print(
                f"  0x{hdr.bss_address:08X} - 0x{bss_end:08X}  "
                f"bss    {bar}"
            )
        print()

    # Validation warnings.
    if file_size is not None:
        warnings = validate_sections(hdr, file_size)
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  - {w}")
            print()

    # TODO: Extract and save individual sections to separate files.


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def inspect_file(filepath: str) -> DolHeader:
    """Load a DOL file and display its header information."""
    with open(filepath, "rb") as f:
        data = f.read()

    hdr = parse_dol(data)
    display_header(hdr, file_size=len(data))
    return hdr


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dol_file>")
        sys.exit(1)

    try:
        inspect_file(sys.argv[1])
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)
