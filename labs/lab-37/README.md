# Lab 37: Xbox XBE Header Inspector

## Objective

Parse the header of an original Xbox XBE (Xbox Executable) file. XBE is
the executable format used by the original Xbox, analogous to ELF on Linux
or PE on Windows.

By the end of this lab you will be able to:

- Read and validate the XBE magic number and signature region
- Extract base address, entry point, and section headers
- Parse the kernel import thunk table to identify imported functions
- Decode library version stamps

## Background

Every original Xbox game ships as an XBE file. The XBE header sits at the
start of the file and contains metadata the Xbox kernel needs to load and
run the executable.

### XBE Header Layout (all fields little-endian)

| Offset | Size | Field                      |
|--------|------|----------------------------|
| 0x000  | 4    | Magic ("XBEH" = 0x48454258)|
| 0x004  | 256  | Digital signature          |
| 0x104  | 4    | Base address               |
| 0x108  | 4    | Size of headers            |
| 0x10C  | 4    | Size of image              |
| 0x110  | 4    | Size of image header       |
| 0x114  | 4    | Timestamp                  |
| 0x118  | 4    | Certificate address        |
| 0x11C  | 4    | Number of sections         |
| 0x120  | 4    | Section headers address    |
| 0x124  | 4    | Init flags                 |
| 0x128  | 4    | Entry point (encoded)      |
| 0x16C  | 4    | Kernel thunk table address (encoded) |
| 0x174  | 4    | Number of library versions |
| 0x178  | 4    | Library versions address   |

### Entry Point Encoding

The stored entry point is XOR-encoded. For retail XBEs the key is
`0xA8FC57AB`. For debug XBEs the key is `0x94859D4B`. If decoding with
the retail key produces an address within the image (>= base, < base +
image size), it is retail; otherwise try debug.

### Kernel Thunk Table

The thunk table address is also XOR-encoded (retail: `0x5B6D40B6`,
debug: `0x46437E4B`). It points to an array of 32-bit ordinals
terminated by zero. Each ordinal identifies a kernel function.

### Section Header (each 56 bytes)

| Offset | Size | Field                   |
|--------|------|-------------------------|
| 0x00   | 4    | Flags                   |
| 0x04   | 4    | Virtual address         |
| 0x08   | 4    | Virtual size            |
| 0x0C   | 4    | Raw address (file off.) |
| 0x10   | 4    | Raw size                |
| 0x14   | 4    | Section name address    |

### Common Kernel Imports (partial list)

| Ordinal | Function                  |
|---------|---------------------------|
| 1       | AvGetSavedDataAddress     |
| 49      | HalReturnToFirmware       |
| 116     | MmAllocateContiguousMemory|
| 165     | NtCreateFile              |
| 187     | NtReadFile                |
| 236     | PsCreateSystemThreadEx    |
| 300     | RtlInitAnsiString        |
| 327     | XeLoadSection             |

## Files

| File               | Description                          |
|--------------------|--------------------------------------|
| `xbe_inspector.py` | XBE header parser (starter code)    |
| `test_lab.py`       | Pytest test suite                   |

## Instructions

1. Open `xbe_inspector.py` and read the starter code.
2. Complete each function marked with a `TODO` comment.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
=== XBE Header ===
Magic:          XBEH
Base Address:   0x00010000
Entry Point:    0x00015A3C (retail)
Sections:       3
  .text   VA=0x00011000  Size=0x00008000  Raw=0x00001000
  .rdata  VA=0x00019000  Size=0x00002000  Raw=0x00009000
  .data   VA=0x0001B000  Size=0x00001000  Raw=0x0000B000
Kernel Imports: [166, 187, 236, 300]
```

## References

- Caustik's XBE documentation (xboxdevwiki.net)
- OpenXDK header definitions
