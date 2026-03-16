"""
Lab 1: Game Boy ROM Inspector

Parse and display the header fields of a Game Boy ROM file.
The header occupies offsets 0x100-0x14F in the ROM.
"""

import sys
import os

# Allow imports from the labs package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from labs.lib.disasm_helpers import hex_dump, read_u8


# ---------------------------------------------------------------------------
# Lookup Tables
# ---------------------------------------------------------------------------

CARTRIDGE_TYPES = {
    0x00: "ROM ONLY",
    0x01: "MBC1",
    0x02: "MBC1+RAM",
    0x03: "MBC1+RAM+BATTERY",
    0x05: "MBC2",
    0x06: "MBC2+BATTERY",
    0x08: "ROM+RAM",
    0x09: "ROM+RAM+BATTERY",
    0x0B: "MMM01",
    0x0C: "MMM01+RAM",
    0x0D: "MMM01+RAM+BATTERY",
    0x0F: "MBC3+TIMER+BATTERY",
    0x10: "MBC3+TIMER+RAM+BATTERY",
    0x11: "MBC3",
    0x12: "MBC3+RAM",
    0x13: "MBC3+RAM+BATTERY",
    0x19: "MBC5",
    0x1A: "MBC5+RAM",
    0x1B: "MBC5+RAM+BATTERY",
    0x1C: "MBC5+RUMBLE",
    0x1D: "MBC5+RUMBLE+RAM",
    0x1E: "MBC5+RUMBLE+RAM+BATTERY",
    0x20: "MBC6",
    0x22: "MBC7+SENSOR+RUMBLE+RAM+BATTERY",
    0xFC: "POCKET CAMERA",
    0xFD: "BANDAI TAMA5",
    0xFE: "HuC3",
    0xFF: "HuC1+RAM+BATTERY",
}

ROM_SIZES = {
    0x00: "32 KB (2 banks)",
    0x01: "64 KB (4 banks)",
    0x02: "128 KB (8 banks)",
    0x03: "256 KB (16 banks)",
    0x04: "512 KB (32 banks)",
    0x05: "1 MB (64 banks)",
    0x06: "2 MB (128 banks)",
    0x07: "4 MB (256 banks)",
    0x08: "8 MB (512 banks)",
}

RAM_SIZES = {
    0x00: "None",
    0x01: "2 KB",
    0x02: "8 KB (1 bank)",
    0x03: "32 KB (4 banks)",
    0x04: "128 KB (16 banks)",
    0x05: "64 KB (8 banks)",
}


# ---------------------------------------------------------------------------
# Header Parsing
# ---------------------------------------------------------------------------

def read_rom(filepath):
    """Read a ROM file and return its contents as bytes."""
    with open(filepath, "rb") as f:
        return f.read()


def parse_title(rom_data):
    """Extract the ROM title from header bytes 0x134-0x143.

    The title is stored as ASCII, padded with null bytes.

    Returns:
        The title as a stripped string.
    """
    # TODO: Extract bytes 0x134 through 0x143 from rom_data,
    #       decode them as ASCII, and strip trailing null bytes / whitespace.
    #       Hint: use rom_data[0x134:0x144] and .decode("ascii", errors="replace")
    pass


def parse_cartridge_type(rom_data):
    """Read the cartridge type byte at offset 0x147.

    Returns:
        Tuple of (byte_value, description_string).
    """
    # TODO: Read the byte at offset 0x147, look it up in CARTRIDGE_TYPES,
    #       and return (value, description). Use "UNKNOWN" for missing keys.
    pass


def parse_rom_size(rom_data):
    """Read the ROM size byte at offset 0x148.

    Returns:
        Tuple of (byte_value, description_string).
    """
    # TODO: Read the byte at offset 0x148 and look it up in ROM_SIZES.
    pass


def parse_ram_size(rom_data):
    """Read the RAM size byte at offset 0x149.

    Returns:
        Tuple of (byte_value, description_string).
    """
    # TODO: Read the byte at offset 0x149 and look it up in RAM_SIZES.
    pass


def compute_header_checksum(rom_data):
    """Compute the header checksum over bytes 0x134-0x14C.

    The algorithm:
        x = 0
        for addr in range(0x134, 0x14D):
            x = (x - rom[addr] - 1) & 0xFF

    Returns:
        The computed checksum as an integer (0-255).
    """
    # TODO: Implement the checksum algorithm described above.
    pass


def validate_checksum(rom_data):
    """Compare the computed header checksum against the stored value at 0x14D.

    Returns:
        Tuple of (stored_checksum, computed_checksum, is_valid).
    """
    stored = read_u8(rom_data, 0x14D)
    computed = compute_header_checksum(rom_data)
    return (stored, computed, stored == computed)


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_header_info(rom_data):
    """Print all parsed header fields in a formatted layout."""
    print("=== Game Boy ROM Header ===")

    title = parse_title(rom_data)
    print(f"Title:          {title}")

    cart_val, cart_desc = parse_cartridge_type(rom_data)
    print(f"Cartridge Type: {cart_desc} (0x{cart_val:02x})")

    rom_val, rom_desc = parse_rom_size(rom_data)
    print(f"ROM Size:       {rom_desc} (0x{rom_val:02x})")

    ram_val, ram_desc = parse_ram_size(rom_data)
    print(f"RAM Size:       {ram_desc} (0x{ram_val:02x})")

    stored, computed, valid = validate_checksum(rom_data)
    status = "VALID" if valid else f"INVALID (expected 0x{computed:02x})"
    print(f"Header Checksum: 0x{stored:02x} [{status}]")

    print()
    print("=== Raw Header Hex Dump (0x100-0x14F) ===")
    print(hex_dump(rom_data[0x100:0x150], base_addr=0x100))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <rom.gb>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    rom_data = read_rom(filepath)
    if len(rom_data) < 0x150:
        print("Error: file is too small to contain a valid Game Boy ROM header.")
        sys.exit(1)

    print_header_info(rom_data)


if __name__ == "__main__":
    main()
