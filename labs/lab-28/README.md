# Lab 28: GBA Header Parser

## Objective

Parse and validate a GBA ROM header, including the complement checksum.
This is the GBA equivalent of Lab 01 / Lab 26 -- you need to understand
the ROM layout before you can feed it into a recompilation pipeline.

## Background

GBA ROMs start with a 192-byte header at address 0x00000000 in the
cartridge address space (mapped to 0x08000000 at runtime):

| Offset | Size | Field                              |
|--------|------|------------------------------------|
| 0x00   | 4    | Entry point (ARM branch instruction)|
| 0x04   | 156  | Nintendo logo (compressed bitmap)  |
| 0xA0   | 12   | Game title (ASCII, null-padded)    |
| 0xAC   | 4    | Game code (ASCII)                  |
| 0xB0   | 2    | Maker code (ASCII)                 |
| 0xB2   | 1    | Fixed value (must be 0x96)         |
| 0xB3   | 1    | Main unit code                     |
| 0xB4   | 1    | Device type                        |
| 0xB5   | 7    | Reserved (should be zero)          |
| 0xBC   | 1    | Software version                   |
| 0xBD   | 1    | Complement check                   |
| 0xBE   | 2    | Reserved (should be zero)          |

### Complement Check

The complement check at 0xBD is computed as:

```
checksum = 0
for byte in rom[0xA0:0xBD]:
    checksum = (checksum - byte) & 0xFF
checksum = (checksum - 0x19) & 0xFF
```

The BIOS verifies this on startup. If it is wrong, the GBA locks up.

### Entry Point

The entry point at offset 0x00 is an ARM branch instruction. The
standard encoding is `0xEA00002E` which branches to 0xC0 (past the
header). To decode it:

```
branch_offset = (entry_word & 0x00FFFFFF)
if branch_offset & 0x800000:
    branch_offset |= 0xFF000000  # sign extend
target = 8 + (branch_offset << 2)  # pipeline offset + shifted
```

## Instructions

1. Open `gba_inspector.py` and implement each TODO function.
2. Functions to implement:
   - `parse_entry_point()` -- decode the ARM branch at offset 0
   - `parse_game_title()` -- extract the 12-byte title
   - `parse_game_code()` -- extract the 4-byte game code
   - `parse_maker_code()` -- extract the 2-byte maker code
   - `compute_complement()` -- compute the header complement checksum
   - `validate_header()` -- compare computed vs stored checksum
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
=== GBA ROM Header ===
Entry Point:  0x000000C0
Game Title:   POKEMONFIRE
Game Code:    BPRE
Maker Code:   01
Complement:   0xDD [VALID]
```
