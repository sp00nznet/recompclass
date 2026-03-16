# Lab 8: MZ Parser (DOS)

## Objective

Parse the DOS MZ executable format, extracting header fields, the relocation table,
and detecting common compression schemes like EXEPACK.

## Background

The MZ executable format (named after Mark Zbikowski) is the standard executable
format for DOS. Understanding this format is essential for recompiling DOS games
and applications, as you need to:

1. Parse the header to understand the memory layout.
2. Apply relocations to produce position-independent code for analysis.
3. Detect packing/compression that must be handled before disassembly.

### MZ Header Layout (28 bytes minimum)

| Offset | Size | Field                        |
|--------|------|------------------------------|
| 0x00   | 2    | Magic number (0x5A4D "MZ")   |
| 0x02   | 2    | Bytes on last page           |
| 0x04   | 2    | Pages in file (512 bytes ea) |
| 0x06   | 2    | Number of relocations        |
| 0x08   | 2    | Header size in paragraphs    |
| 0x0A   | 2    | Minimum extra paragraphs     |
| 0x0C   | 2    | Maximum extra paragraphs     |
| 0x0E   | 2    | Initial SS (relative)        |
| 0x10   | 2    | Initial SP                   |
| 0x12   | 2    | Checksum                     |
| 0x14   | 2    | Initial IP                   |
| 0x16   | 2    | Initial CS (relative)        |
| 0x18   | 2    | Relocation table offset      |
| 0x1A   | 2    | Overlay number               |

Each relocation entry is 4 bytes: offset (2 bytes) + segment (2 bytes).

## Tasks

1. Read and validate the MZ header magic number.
2. Parse all header fields listed above.
3. Parse and display the relocation table entries.
4. Detect EXEPACK compression by looking for the signature.
5. (TODO) Implement relocation application to the loaded image.
6. (TODO) Detect and handle overlays (multiple executables in one file).

## Files

- `mz_parser.py` — Main MZ parser implementation
- `test_lab.py` — Tests with a crafted minimal MZ binary

## Running

```bash
python mz_parser.py
python test_lab.py
```

## Key Concepts

- Binary file format parsing with struct
- Segment:offset addressing in real mode (physical = segment * 16 + offset)
- Relocation as a prerequisite for static analysis
- Detecting packers/compressors that obscure the real code
