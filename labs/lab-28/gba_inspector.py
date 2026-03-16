"""
Lab 28: GBA Header Parser

Parse and validate a GBA ROM header.
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Header Parsing
# ---------------------------------------------------------------------------

def parse_entry_point(rom_data):
    """Decode the ARM branch instruction at offset 0x00.

    The entry point is encoded as an ARM 'B' (branch) instruction:
        bits 31-28: condition (0xE = always)
        bits 27-24: 0xA (branch opcode)
        bits 23-0:  signed offset (in words, added to PC+8)

    Target = 8 + (sign_extended_offset << 2)

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        The branch target address as an int.
    """
    # TODO: 1. Read the 32-bit word at offset 0 (little-endian).
    #          Hint: struct.unpack_from("<I", rom_data, 0)[0]
    # TODO: 2. Extract the 24-bit offset: entry_word & 0x00FFFFFF
    # TODO: 3. Sign-extend: if bit 23 is set, OR with 0xFF000000
    #          and convert to a signed value (subtract 0x100000000 if needed,
    #          or use Python's two's complement).
    # TODO: 4. Compute target = 8 + (offset << 2)
    # TODO: 5. Return the target address.
    pass


def parse_game_title(rom_data):
    """Extract the game title from offset 0xA0 (12 bytes, ASCII).

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        The title as a string, stripped of null bytes and whitespace.
    """
    # TODO: Read rom_data[0xA0:0xAC], decode as ASCII, strip nulls.
    pass


def parse_game_code(rom_data):
    """Extract the 4-byte game code from offset 0xAC.

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        The game code as a string.
    """
    # TODO: Read rom_data[0xAC:0xB0] and decode as ASCII.
    pass


def parse_maker_code(rom_data):
    """Extract the 2-byte maker code from offset 0xB0.

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        The maker code as a string.
    """
    # TODO: Read rom_data[0xB0:0xB2] and decode as ASCII.
    pass


def compute_complement(rom_data):
    """Compute the header complement checksum.

    Algorithm:
        checksum = 0
        for byte in rom_data[0xA0:0xBD]:
            checksum = (checksum - byte) & 0xFF
        checksum = (checksum - 0x19) & 0xFF

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        The computed complement as an int (0-255).
    """
    # TODO: Implement the algorithm above.
    pass


def validate_header(rom_data):
    """Compare the computed complement against the stored value at 0xBD.

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        Tuple of (stored, computed, is_valid).
    """
    # TODO: Read the stored value at rom_data[0xBD].
    # TODO: Compute the expected value with compute_complement().
    # TODO: Return (stored, computed, stored == computed).
    pass


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_header_info(rom_data):
    """Print all parsed header fields."""
    print("=== GBA ROM Header ===")

    entry = parse_entry_point(rom_data)
    print(f"Entry Point:  0x{entry:08X}")

    title = parse_game_title(rom_data)
    print(f"Game Title:   {title}")

    code = parse_game_code(rom_data)
    print(f"Game Code:    {code}")

    maker = parse_maker_code(rom_data)
    print(f"Maker Code:   {maker}")

    stored, computed, valid = validate_header(rom_data)
    status = "VALID" if valid else f"INVALID (expected 0x{computed:02X})"
    print(f"Complement:   0x{stored:02X} [{status}]")

    fixed = rom_data[0xB2]
    print(f"Fixed (0x96): 0x{fixed:02X} {'OK' if fixed == 0x96 else 'BAD'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <rom.gba>")
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, "rb") as f:
        rom_data = f.read()

    if len(rom_data) < 0xC0:
        print("Error: file too small for a GBA ROM header.")
        sys.exit(1)

    print_header_info(rom_data)


if __name__ == "__main__":
    main()
