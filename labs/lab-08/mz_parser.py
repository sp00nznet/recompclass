"""
Lab 8: DOS MZ Executable Parser

Parses the MZ (Mark Zbikowski) executable format used by DOS programs.
Extracts header fields, relocation table entries, and detects EXEPACK compression.
"""

import struct
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# MZ Header structure
# ---------------------------------------------------------------------------

MZ_MAGIC = 0x5A4D          # "MZ" in little-endian
MZ_MAGIC_ALT = 0x4D5A      # "ZM" (some tools use this)
MZ_HEADER_SIZE = 28         # Minimum header size in bytes
PARAGRAPH_SIZE = 16         # A DOS paragraph is 16 bytes
PAGE_SIZE = 512             # A DOS page is 512 bytes

# EXEPACK signature string found in packed executables
EXEPACK_SIGNATURE = b"RB"  # EXEPACK uses "RB" marker at the start of packed data


@dataclass
class RelocationEntry:
    """A single MZ relocation entry (segment:offset pair)."""
    offset: int     # Offset within the segment
    segment: int    # Segment value

    @property
    def linear_address(self) -> int:
        """Convert segment:offset to a linear address."""
        return self.segment * PARAGRAPH_SIZE + self.offset

    def __str__(self) -> str:
        return f"{self.segment:04X}:{self.offset:04X} (linear: 0x{self.linear_address:05X})"


@dataclass
class MZHeader:
    """Parsed MZ executable header."""
    magic: int = 0                  # Magic number (should be 0x5A4D)
    bytes_on_last_page: int = 0     # Number of bytes on the last page
    pages_in_file: int = 0          # Total number of 512-byte pages
    num_relocations: int = 0        # Number of relocation entries
    header_size_para: int = 0       # Header size in paragraphs (16-byte units)
    min_extra_para: int = 0         # Minimum extra memory (paragraphs)
    max_extra_para: int = 0         # Maximum extra memory (paragraphs)
    initial_ss: int = 0             # Initial SS register value (relative)
    initial_sp: int = 0             # Initial SP register value
    checksum: int = 0               # Checksum (rarely used)
    initial_ip: int = 0             # Initial IP register value (entry point offset)
    initial_cs: int = 0             # Initial CS register value (relative)
    reloc_table_offset: int = 0     # Offset to the relocation table
    overlay_number: int = 0         # Overlay number (0 = main executable)

    @property
    def header_size_bytes(self) -> int:
        """Header size in bytes."""
        return self.header_size_para * PARAGRAPH_SIZE

    @property
    def file_size(self) -> int:
        """Calculate the executable size from page count and last-page bytes."""
        if self.pages_in_file == 0:
            return 0
        size = (self.pages_in_file - 1) * PAGE_SIZE
        if self.bytes_on_last_page > 0:
            size += self.bytes_on_last_page
        else:
            size += PAGE_SIZE
        return size

    @property
    def code_start_offset(self) -> int:
        """Offset in the file where the code/data image begins."""
        return self.header_size_bytes

    @property
    def entry_point_text(self) -> str:
        """Human-readable entry point."""
        return f"{self.initial_cs:04X}:{self.initial_ip:04X}"

    @property
    def stack_pointer_text(self) -> str:
        """Human-readable initial stack pointer."""
        return f"{self.initial_ss:04X}:{self.initial_sp:04X}"

    def is_valid(self) -> bool:
        """Check if the magic number is valid."""
        return self.magic in (MZ_MAGIC, MZ_MAGIC_ALT)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class MZParser:
    """
    Parses a DOS MZ executable from raw bytes.

    Usage:
        parser = MZParser(raw_bytes)
        parser.parse()
        print(parser.header)
        for entry in parser.relocations:
            print(entry)
    """

    def __init__(self, data: bytes):
        self.data = data
        self.header = MZHeader()
        self.relocations: List[RelocationEntry] = []
        self._is_exepacked = False

    def parse(self) -> bool:
        """
        Parse the MZ executable. Returns True on success, False on failure.
        """
        if not self._parse_header():
            return False
        self._parse_relocations()
        self._detect_exepack()
        return True

    def _parse_header(self) -> bool:
        """Parse the 28-byte MZ header."""
        if len(self.data) < MZ_HEADER_SIZE:
            print(f"Error: Data too short for MZ header ({len(self.data)} < {MZ_HEADER_SIZE})")
            return False

        # Unpack the header fields (all little-endian unsigned 16-bit words)
        fields = struct.unpack_from("<14H", self.data, 0)

        self.header.magic               = fields[0]
        self.header.bytes_on_last_page  = fields[1]
        self.header.pages_in_file       = fields[2]
        self.header.num_relocations     = fields[3]
        self.header.header_size_para    = fields[4]
        self.header.min_extra_para      = fields[5]
        self.header.max_extra_para      = fields[6]
        self.header.initial_ss          = fields[7]
        self.header.initial_sp          = fields[8]
        self.header.checksum            = fields[9]
        self.header.initial_ip          = fields[10]
        self.header.initial_cs          = fields[11]
        self.header.reloc_table_offset  = fields[12]
        self.header.overlay_number      = fields[13]

        if not self.header.is_valid():
            print(f"Error: Invalid MZ magic number: 0x{self.header.magic:04X}")
            return False

        return True

    def _parse_relocations(self) -> None:
        """Parse the relocation table."""
        self.relocations.clear()

        if self.header.num_relocations == 0:
            return

        offset = self.header.reloc_table_offset
        for i in range(self.header.num_relocations):
            entry_offset = offset + i * 4
            if entry_offset + 4 > len(self.data):
                print(f"Warning: Relocation table truncated at entry {i}")
                break

            rel_offset, rel_segment = struct.unpack_from("<HH", self.data, entry_offset)
            self.relocations.append(RelocationEntry(
                offset=rel_offset,
                segment=rel_segment,
            ))

    def _detect_exepack(self) -> None:
        """
        Detect EXEPACK compression.

        EXEPACK executables typically have the string "RB" near the entry point
        and contain the EXEPACK unpacker code. A more robust check looks for
        the "EXEPACK" or "RB" signature in the code area.
        """
        code_start = self.header.code_start_offset
        if code_start >= len(self.data):
            return

        code_region = self.data[code_start:]

        # Look for the EXEPACK text signature in the code region
        if b"EXEPACK" in code_region:
            self._is_exepacked = True
            return

        # Look for the "RB" signature at the expected location.
        # In EXEPACK, the entry point typically points to the unpacker,
        # and "RB" appears at a specific offset relative to CS:IP.
        entry_linear = self.header.initial_cs * PARAGRAPH_SIZE + self.header.initial_ip
        if entry_linear < len(code_region) and entry_linear >= 2:
            if code_region[entry_linear - 2 : entry_linear] == EXEPACK_SIGNATURE:
                self._is_exepacked = True

    @property
    def is_exepacked(self) -> bool:
        """Returns True if EXEPACK compression was detected."""
        return self._is_exepacked

    def get_code_image(self) -> bytes:
        """
        Return the raw code/data image (everything after the header).
        """
        start = self.header.code_start_offset
        return self.data[start:]

    def apply_relocations(self, load_segment: int = 0x1000) -> bytearray:
        """
        Apply relocations to the code image, simulating loading at `load_segment`.

        Each relocation entry points to a 16-bit word in the image that needs
        the load segment added to it.

        TODO: Implement this method.
              - Copy the code image into a mutable bytearray.
              - For each relocation entry, calculate its position in the image:
                  position = entry.segment * 16 + entry.offset
              - Read the 16-bit word at that position.
              - Add load_segment to it.
              - Write the updated word back.
              - Return the modified image.
        """
        raise NotImplementedError("Relocation application not yet implemented")

    def detect_overlays(self) -> Optional[int]:
        """
        Detect if the file contains overlay data beyond the main executable.

        TODO: Implement this method.
              - Calculate the expected file size from the header.
              - If the actual data is larger, the extra bytes are overlay data.
              - Return the offset where overlay data begins, or None if no overlays.
        """
        raise NotImplementedError("Overlay detection not yet implemented")


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_mz_info(parser: MZParser) -> None:
    """Pretty-print the parsed MZ information."""
    h = parser.header

    print("=== MZ Executable Header ===")
    print(f"  Magic:                0x{h.magic:04X} ({'valid' if h.is_valid() else 'INVALID'})")
    print(f"  Bytes on last page:   {h.bytes_on_last_page}")
    print(f"  Pages in file:        {h.pages_in_file}")
    print(f"  Calculated file size: {h.file_size} bytes")
    print(f"  Number of relocs:     {h.num_relocations}")
    print(f"  Header size:          {h.header_size_para} paragraphs ({h.header_size_bytes} bytes)")
    print(f"  Min extra memory:     {h.min_extra_para} paragraphs")
    print(f"  Max extra memory:     {h.max_extra_para} paragraphs")
    print(f"  Initial SS:SP:        {h.stack_pointer_text}")
    print(f"  Checksum:             0x{h.checksum:04X}")
    print(f"  Entry point (CS:IP):  {h.entry_point_text}")
    print(f"  Reloc table offset:   0x{h.reloc_table_offset:04X}")
    print(f"  Overlay number:       {h.overlay_number}")
    print(f"  EXEPACK detected:     {'Yes' if parser.is_exepacked else 'No'}")

    if parser.relocations:
        print(f"\n=== Relocation Table ({len(parser.relocations)} entries) ===")
        for i, entry in enumerate(parser.relocations):
            print(f"  [{i:3d}] {entry}")
    else:
        print("\n  No relocations.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Lab 8: MZ Parser (DOS) ===\n")

    # Build a minimal MZ executable for demonstration.
    # This is a tiny valid MZ file with:
    #   - 2-paragraph (32-byte) header
    #   - 1 relocation entry
    #   - A few bytes of "code"
    header = struct.pack("<14H",
        0x5A4D,     # Magic "MZ"
        16,         # Bytes on last page (16 bytes of code)
        1,          # 1 page (512 bytes, but file can be smaller)
        1,          # 1 relocation entry
        2,          # Header size: 2 paragraphs (32 bytes)
        0,          # Min extra paragraphs
        0xFFFF,     # Max extra paragraphs
        0x0000,     # Initial SS
        0x0100,     # Initial SP
        0x0000,     # Checksum
        0x0000,     # Initial IP
        0x0000,     # Initial CS
        0x001C,     # Relocation table offset (right after the 28-byte header)
        0x0000,     # Overlay number
    )

    # Relocation entry at offset 0x001C: segment:offset = 0000:0004
    reloc = struct.pack("<HH", 0x0004, 0x0000)

    # Code image (starts at offset 32)
    # Simple sequence: MOV AX, 0x4C00 / INT 0x21 (DOS exit)
    code = bytes([
        0xB8, 0x00, 0x4C,      # MOV AX, 4C00h
        0xCD, 0x21,             # INT 21h
        0x00, 0x10,             # Relocation target word at offset 4-5
        0x00, 0x00, 0x00,       # Padding
    ])

    # Pad header to 32 bytes (2 paragraphs)
    raw = header + reloc + code

    parser = MZParser(raw)
    if parser.parse():
        display_mz_info(parser)
    else:
        print("Failed to parse MZ executable.")
