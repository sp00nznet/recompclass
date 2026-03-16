# Lab 26: NES ROM Inspector

## Objective

Parse and display the header fields of an NES ROM file in iNES format.
This is the NES equivalent of Lab 01 (Game Boy ROM Inspector) -- before
you can recompile a NES game, you need to know what mapper it uses, how
much PRG/CHR ROM it has, and what mirroring mode is set.

## Background

The iNES format (.nes) is the standard ROM dump format for NES games.
The header is 16 bytes:

| Offset | Size | Field                                           |
|--------|------|-------------------------------------------------|
| 0-3    | 4    | Magic: "NES" + 0x1A                             |
| 4      | 1    | PRG ROM size in 16 KB units                     |
| 5      | 1    | CHR ROM size in 8 KB units (0 = uses CHR RAM)   |
| 6      | 1    | Flags 6: mapper low nibble, mirroring, battery   |
| 7      | 1    | Flags 7: mapper high nibble, NES 2.0 indicator   |
| 8      | 1    | PRG RAM size in 8 KB units (0 = infer 8 KB)     |
| 9      | 1    | Flags 9: TV system                               |
| 10     | 1    | Flags 10: TV system, PRG RAM presence            |
| 11-15  | 5    | Padding (should be zero)                         |

### Flags 6 Bit Layout

```
7654 3210
||||||||
|||||||+- Mirroring: 0 = horizontal, 1 = vertical
||||||+-- Battery-backed PRG RAM at $6000-$7FFF
|||||+--- 512-byte trainer present
||||+---- Four-screen VRAM
++++----- Lower nibble of mapper number
```

### Mapper Number

The full mapper number is assembled from two nibbles:
    mapper = (flags7 & 0xF0) | (flags6 >> 4)

## Instructions

1. Open `nes_inspector.py` and implement each TODO function.
2. Functions to implement:
   - `validate_magic()` -- check the "NES\x1A" signature
   - `parse_prg_rom_size()` -- PRG ROM size in bytes
   - `parse_chr_rom_size()` -- CHR ROM size in bytes
   - `parse_mapper()` -- mapper number
   - `parse_mirroring()` -- mirroring type string
   - `parse_flags()` -- battery, trainer, four-screen flags
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
=== NES ROM Header ===
Magic:      Valid (NES\x1A)
PRG ROM:    32768 bytes (2 x 16 KB)
CHR ROM:    8192 bytes (1 x 8 KB)
Mapper:     0 (NROM)
Mirroring:  Horizontal
Battery:    No
Trainer:    No
```
