"""
Lab 26: NES ROM Inspector

Parse and display the header fields of an iNES (.nes) ROM file.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Common mapper names (subset)
# ---------------------------------------------------------------------------

MAPPER_NAMES = {
    0:   "NROM",
    1:   "MMC1 (SxROM)",
    2:   "UxROM",
    3:   "CNROM",
    4:   "MMC3 (TxROM)",
    5:   "MMC5 (ExROM)",
    7:   "AxROM",
    9:   "MMC2 (PxROM)",
    10:  "MMC4 (FxROM)",
    11:  "Color Dreams",
    16:  "Bandai FCG",
    19:  "Namco 129/163",
    21:  "VRC4a/VRC4c",
    22:  "VRC2a",
    23:  "VRC2b/VRC4e",
    24:  "VRC6a",
    25:  "VRC4b/VRC4d",
    26:  "VRC6b",
    34:  "BNROM/NINA-001",
    66:  "GxROM",
    69:  "Sunsoft FME-7",
    71:  "Camerica/Codemasters",
    79:  "NINA-03/NINA-06",
    85:  "VRC7",
    118: "TxSROM (MMC3 variant)",
    119: "TQROM (MMC3 variant)",
}


# ---------------------------------------------------------------------------
# Header Parsing
# ---------------------------------------------------------------------------

INES_MAGIC = b"NES\x1a"


def validate_magic(rom_data):
    """Check whether the first 4 bytes match the iNES magic "NES\\x1A".

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        True if the magic bytes are correct, False otherwise.
    """
    # TODO: Compare rom_data[0:4] against INES_MAGIC.
    pass


def parse_prg_rom_size(rom_data):
    """Read the PRG ROM size from byte 4 of the header.

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        PRG ROM size in bytes (byte 4 * 16384).
    """
    # TODO: Read rom_data[4] and multiply by 16384 (16 KB).
    pass


def parse_chr_rom_size(rom_data):
    """Read the CHR ROM size from byte 5 of the header.

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        CHR ROM size in bytes (byte 5 * 8192).
        Returns 0 if the game uses CHR RAM instead.
    """
    # TODO: Read rom_data[5] and multiply by 8192 (8 KB).
    pass


def parse_mapper(rom_data):
    """Extract the mapper number from flags 6 and flags 7.

    The mapper number is:
        mapper = (flags7 & 0xF0) | (flags6 >> 4)

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        Tuple of (mapper_number, mapper_name_string).
        Use MAPPER_NAMES.get(mapper_number, "Unknown") for the name.
    """
    # TODO: Read rom_data[6] (flags6) and rom_data[7] (flags7).
    # TODO: Combine the nibbles to get the mapper number.
    # TODO: Look up the name in MAPPER_NAMES.
    pass


def parse_mirroring(rom_data):
    """Determine the nametable mirroring mode from flags 6.

    Bit 3 of flags 6: four-screen mode (overrides bit 0).
    Bit 0 of flags 6: 0 = Horizontal, 1 = Vertical.

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        A string: "Four-Screen", "Vertical", or "Horizontal".
    """
    # TODO: Read flags6 = rom_data[6].
    # TODO: If bit 3 is set, return "Four-Screen".
    # TODO: If bit 0 is set, return "Vertical".
    # TODO: Otherwise, return "Horizontal".
    pass


def parse_flags(rom_data):
    """Extract additional flags from flags byte 6.

    Args:
        rom_data: bytes of the ROM file.

    Returns:
        A dict with keys:
            "battery" - bool, True if battery-backed RAM present (bit 1)
            "trainer" - bool, True if 512-byte trainer present (bit 2)
    """
    # TODO: Read flags6 = rom_data[6].
    # TODO: Extract bit 1 (battery) and bit 2 (trainer).
    pass


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_header_info(rom_data):
    """Print all parsed header fields."""
    valid = validate_magic(rom_data)
    magic_str = "Valid (NES\\x1A)" if valid else "INVALID"
    print("=== NES ROM Header ===")
    print(f"Magic:      {magic_str}")

    prg = parse_prg_rom_size(rom_data)
    units = prg // 16384 if prg else 0
    print(f"PRG ROM:    {prg} bytes ({units} x 16 KB)")

    chr_size = parse_chr_rom_size(rom_data)
    if chr_size == 0:
        print("CHR ROM:    0 bytes (uses CHR RAM)")
    else:
        units = chr_size // 8192
        print(f"CHR ROM:    {chr_size} bytes ({units} x 8 KB)")

    mapper_num, mapper_name = parse_mapper(rom_data)
    print(f"Mapper:     {mapper_num} ({mapper_name})")

    mirroring = parse_mirroring(rom_data)
    print(f"Mirroring:  {mirroring}")

    fl = parse_flags(rom_data)
    print(f"Battery:    {'Yes' if fl['battery'] else 'No'}")
    print(f"Trainer:    {'Yes' if fl['trainer'] else 'No'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <rom.nes>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    with open(filepath, "rb") as f:
        rom_data = f.read()

    if len(rom_data) < 16:
        print("Error: file is too small to contain an iNES header.")
        sys.exit(1)

    print_header_info(rom_data)


if __name__ == "__main__":
    main()
