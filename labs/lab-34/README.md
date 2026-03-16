# Lab 34: Wii DOL Extended Parser

## Objective

Parse DOL executable files used by both GameCube and Wii. The DOL format
is the native executable format for both consoles -- it defines where code
and data sections are loaded into memory and where execution begins.

## Background

The DOL header is 0x100 (256) bytes and describes up to 7 text (code)
sections and 11 data sections:

| Offset   | Size     | Field                              |
|----------|----------|------------------------------------|
| 0x0000   | 7 x 4   | Text section file offsets (7 entries) |
| 0x001C   | 11 x 4  | Data section file offsets (11 entries) |
| 0x0048   | 7 x 4   | Text section load addresses        |
| 0x0064   | 11 x 4  | Data section load addresses        |
| 0x0090   | 7 x 4   | Text section sizes                 |
| 0x00AC   | 11 x 4  | Data section sizes                 |
| 0x00D8   | 4       | BSS address                        |
| 0x00DC   | 4       | BSS size                           |
| 0x00E0   | 4       | Entry point address                |

All values are big-endian 32-bit unsigned integers. Unused sections
have all three fields (offset, address, size) set to zero.

### GameCube vs Wii Differences

- GC DOLs typically use address range 0x80003100-0x817FFFFF.
- Wii DOLs can use addresses up to 0x817FFFFF (MEM1) or in the MEM2
  range (0x90000000-0x93FFFFFF) for additional data.
- A DOL using MEM2 addresses is almost certainly a Wii title.

## Instructions

1. Open `wii_dol_parser.py` and implement the TODO functions.
2. `parse_dol_header()` -- read all section descriptors from the header.
3. `get_text_sections()` -- return only non-empty text sections.
4. `get_data_sections()` -- return only non-empty data sections.
5. `get_entry_point()` -- read the entry point address.
6. `get_bss_info()` -- read BSS address and size.
7. `detect_platform()` -- guess GameCube vs Wii based on addresses.
8. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
=== DOL Header ===
Entry Point:  0x800060A4
BSS:          0x80400000 (size: 0x00100000)
Platform:     GameCube (no MEM2 addresses)

Text Sections:
  T0: offset=0x00000100, addr=0x80003100, size=0x00200000
  T1: offset=0x00200100, addr=0x80203100, size=0x00050000

Data Sections:
  D0: offset=0x00250100, addr=0x80300000, size=0x00080000
```
