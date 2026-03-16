# Lab 18: DOL Parser

## Objective

Parse the GameCube/Wii DOL (Dolphin) executable format using Python. DOL is
the primary executable format for both the GameCube and the Wii. Understanding
its structure is necessary for building recompilers or analysis tools targeting
these platforms.

## Background

A DOL file contains a simple flat header followed by raw section data. The
header layout is:

| Offset | Size    | Description                              |
|--------|---------|------------------------------------------|
| 0x000  | 7 x 4   | Text section file offsets (7 sections)   |
| 0x01C  | 11 x 4  | Data section file offsets (11 sections)  |
| 0x048  | 7 x 4   | Text section load addresses              |
| 0x064  | 11 x 4  | Data section load addresses              |
| 0x090  | 7 x 4   | Text section sizes                       |
| 0x0AC  | 11 x 4  | Data section sizes                       |
| 0x0D8  | 4       | BSS address                              |
| 0x0DC  | 4       | BSS size                                 |
| 0x0E0  | 4       | Entry point address                      |

All values are big-endian 32-bit unsigned integers. Unused sections have all
fields set to zero.

Key properties:

- Up to 7 **text** (code) sections and 11 **data** sections.
- The **BSS** section is zero-initialized memory (not stored in the file).
- Sections are loaded at their specified addresses in the GameCube/Wii's
  flat memory space.
- The **entry point** is the virtual address where execution begins.

## Files

| File              | Description                                   |
|-------------------|-----------------------------------------------|
| `dol_parser.py`    | Python script to parse DOL files             |
| `test_lab.py`      | Test with a crafted minimal DOL header       |

## Tasks

1. Read through `dol_parser.py` and understand the header parsing.
2. Run the tests to verify parsing of the synthetic header.
3. Study the memory map display and understand the section layout.
4. (Stretch) Add a function to extract and save individual sections to files.
5. (Stretch) Add detection of overlapping sections.

## Running

```bash
python dol_parser.py <path_to_dol_file>
python test_lab.py
```
