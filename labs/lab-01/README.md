# Lab 1: ROM Inspector (Game Boy)

## Objective

Parse and display the header of a Game Boy ROM file. The Game Boy ROM header
occupies bytes 0x100 through 0x14F and contains metadata about the cartridge
including its title, type, memory sizes, and a header checksum.

By the end of this lab you will be able to:

- Open and read binary files in Python
- Extract fixed-width fields from a binary header
- Interpret lookup tables that map byte values to human-readable descriptions
- Validate data with a simple checksum algorithm

## Background

Every Game Boy cartridge ROM begins with a 336-byte header region. The most
important fields live between offsets 0x134 and 0x14F. The boot ROM checks
the header checksum at 0x14D before allowing the game to run, so valid ROMs
always have a correct checksum.

## Instructions

1. Open `rom_inspector.py` and read through the provided starter code.
2. Complete each section marked with a `TODO` comment.
3. Run the script against a `.gb` ROM file:
   ```
   python rom_inspector.py path/to/rom.gb
   ```
4. Run the tests to verify your implementation:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output Format

```
=== Game Boy ROM Header ===
Title:          POKEMON RED
Cartridge Type: MBC3+RAM+BATTERY (0x13)
ROM Size:       1 MB (64 banks) (0x06)
RAM Size:       32 KB (4 banks) (0x03)
Header Checksum: 0x91 [VALID]
```

## Header Field Reference

| Offset  | Size | Field           |
|---------|------|-----------------|
| 0x134   | 16   | Title           |
| 0x147   | 1    | Cartridge Type  |
| 0x148   | 1    | ROM Size        |
| 0x149   | 1    | RAM Size        |
| 0x14D   | 1    | Header Checksum |

## Checksum Algorithm

The header checksum is computed over bytes 0x134 through 0x14C:

```
x = 0
for addr in range(0x134, 0x14D):
    x = (x - rom[addr] - 1) & 0xFF
```

The result must match the byte at 0x14D.
