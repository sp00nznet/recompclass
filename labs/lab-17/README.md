# Lab 17: XEX2 Inspector

## Objective

Parse and inspect Xbox 360 XEX2 (Xenon Executable) format headers using
Python. The XEX2 format is the executable format for Xbox 360, analogous to
PE/COFF on Windows or ELF on Linux. Understanding this format is essential
for building a static recompiler targeting Xbox 360 games.

## Background

XEX2 files contain:

- A **magic number** (`XEX2` = `0x58455832`) identifying the format.
- **Module flags** indicating properties like title module, patch, etc.
- **Header fields** including the entry point, base address, and image size.
- **Optional headers** carrying additional metadata such as:
  - Security information (encryption keys, signatures)
  - Import libraries (kernel and other module imports)
  - Resource information (embedded resources)
  - TLS (Thread Local Storage) data
  - Execution ID (title ID, media ID, version)

The XEX2 format wraps a PE image that has been processed (compressed and/or
encrypted) for the Xbox 360. The headers describe how to unwrap and load this
PE image.

## Files

| File                  | Description                                    |
|-----------------------|------------------------------------------------|
| `xex2_inspector.py`   | Python script to parse XEX2 headers           |
| `test_lab.py`          | Test with a crafted minimal XEX2 header       |

## Tasks

1. Read through `xex2_inspector.py` and understand the header parsing logic.
2. Run the test to verify parsing of the synthetic header.
3. Study how optional headers are enumerated and decoded.
4. (Stretch) Add detection of compressed sections.
5. (Stretch) Add encryption flag detection.

## Running

```bash
python xex2_inspector.py <path_to_xex2_file>
python test_lab.py
```

## References

- Free60 XEX2 documentation
- XEX2 format specifications from the homebrew community
