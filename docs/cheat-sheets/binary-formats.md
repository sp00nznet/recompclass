# Binary Format Quick Reference

## Format Overview Table

| Format    | Platform(s)         | Magic Bytes (hex)          | Endianness | Key Feature                        |
|-----------|---------------------|----------------------------|------------|------------------------------------|
| MZ        | DOS                 | `4D 5A`                    | Little     | DOS executable, base for PE        |
| PE        | Windows / Xbox      | `4D 5A` ... `50 45 00 00`  | Little     | Sections, imports, exports, relocs |
| XBE       | Xbox                | `58 42 45 48`              | Little     | Xbox-signed PE variant             |
| XEX2      | Xbox 360            | `58 45 58 32`              | Big        | Encrypted/compressed PPC code      |
| DOL       | GameCube / Wii      | (none -- no magic)         | Big        | Fixed-layout PPC executable        |
| ELF       | PS2 / Linux / etc.  | `7F 45 4C 46`              | Varies     | Universal format, sections + segments |
| SELF      | PS3                 | `53 43 45 00`              | Big        | Signed/encrypted ELF wrapper       |
| GB ROM    | Game Boy            | `CE ED 66 66` at 0x104     | Little     | Nintendo logo check, fixed header  |
| SNES ROM  | SNES                | (none -- detected by header offset) | Little | LoROM/HiROM mapping modes     |
| N64 z64   | Nintendo 64         | `80 37 12 40`              | Big        | Big-endian raw ROM image           |

## Key Field Offsets

### MZ (DOS)

| Field                | Offset   | Size    |
|----------------------|----------|---------|
| Magic ("MZ")         | 0x00     | 2 bytes |
| Entry point (CS:IP)  | 0x14     | 4 bytes |
| Relocation table     | 0x18     | 2 bytes (offset to table) |
| PE header offset     | 0x3C     | 4 bytes (0 if pure DOS) |

### PE (Windows / Xbox)

| Field                | Offset           | Size    |
|----------------------|------------------|---------|
| MZ magic             | 0x00             | 2 bytes |
| PE offset            | 0x3C             | 4 bytes |
| PE signature         | PE_offset + 0x00 | 4 bytes |
| Machine type         | PE_offset + 0x04 | 2 bytes |
| Number of sections   | PE_offset + 0x06 | 2 bytes |
| Entry point RVA      | PE_offset + 0x28 | 4 bytes |
| Image base           | PE_offset + 0x34 | 4 bytes |
| Section table        | After optional header |       |
| Import directory     | Data directory entry 1 |      |

### XBE (Xbox)

| Field                | Offset   | Size    |
|----------------------|----------|---------|
| Magic ("XBEH")       | 0x00     | 4 bytes |
| Base address          | 0x104    | 4 bytes |
| Entry point (encoded) | 0x128   | 4 bytes |
| Section headers offset | 0x120  | 4 bytes |
| Number of sections   | 0x11C    | 4 bytes |

### XEX2 (Xbox 360)

| Field                | Offset   | Size    |
|----------------------|----------|---------|
| Magic ("XEX2")       | 0x00     | 4 bytes |
| Module flags         | 0x04     | 4 bytes |
| Header count         | 0x14     | 4 bytes |
| Optional headers     | 0x18     | Variable |
| Entry point          | Optional header (key 0x00010100) | |
| Base address         | Optional header (key 0x00010201) | |

Note: XEX2 code is typically compressed and/or encrypted. Decryption is required before disassembly.

### DOL (GameCube / Wii)

| Field                | Offset   | Size    |
|----------------------|----------|---------|
| Text section offsets | 0x00     | 7 x 4 bytes |
| Data section offsets | 0x1C     | 11 x 4 bytes |
| Text section addresses | 0x48   | 7 x 4 bytes |
| Data section addresses | 0x64   | 11 x 4 bytes |
| Text section sizes   | 0x90     | 7 x 4 bytes |
| Data section sizes   | 0xAC     | 11 x 4 bytes |
| BSS address          | 0xD8     | 4 bytes |
| BSS size             | 0xDC     | 4 bytes |
| Entry point          | 0xE0     | 4 bytes |

Note: DOL has no magic bytes. Identify by context (file extension, fixed 0x100-byte header).

### ELF

| Field                | Offset   | Size           |
|----------------------|----------|----------------|
| Magic (7F ELF)       | 0x00     | 4 bytes        |
| Class (32/64-bit)    | 0x04     | 1 byte         |
| Endianness           | 0x05     | 1 byte (1=LE, 2=BE) |
| Machine type         | 0x12     | 2 bytes        |
| Entry point          | 0x18     | 4 or 8 bytes   |
| Program header offset | 0x1C (32) / 0x20 (64) | 4 or 8 bytes |
| Section header offset | 0x20 (32) / 0x28 (64) | 4 or 8 bytes |

### SELF (PS3)

| Field                | Offset   | Size    |
|----------------------|----------|---------|
| Magic ("SCE\0")      | 0x00     | 4 bytes |
| Version              | 0x04     | 4 bytes |
| Key type             | 0x08     | 2 bytes |
| Category             | 0x0A     | 2 bytes |
| ELF offset           | 0x10     | 8 bytes |
| Program info offset  | 0x18     | 8 bytes |

Note: Inner ELF must be decrypted before analysis.

### GB ROM

| Field                | Offset   | Size    |
|----------------------|----------|---------|
| Entry point          | 0x100    | 4 bytes (usually nop + jp) |
| Nintendo logo        | 0x104    | 48 bytes |
| Title                | 0x134    | 16 bytes |
| Cartridge type       | 0x147    | 1 byte  |
| ROM size             | 0x148    | 1 byte  |
| RAM size             | 0x149    | 1 byte  |
| Header checksum      | 0x14D    | 1 byte  |

### SNES ROM

| Field                | Offset (LoROM)  | Offset (HiROM) |
|----------------------|-----------------|-----------------|
| Internal name        | 0x7FC0          | 0xFFC0          |
| Map mode             | 0x7FD5          | 0xFFD5          |
| ROM type             | 0x7FD6          | 0xFFD6          |
| ROM size             | 0x7FD7          | 0xFFD7          |
| Reset vector (entry) | 0x7FFC          | 0xFFFC          |

Note: SNES ROMs have no magic. Detect by checking header checksum complement at the known offsets. May include a 512-byte copier header that shifts all offsets.

### N64 z64 (Big-Endian)

| Field                | Offset   | Size    |
|----------------------|----------|---------|
| Magic                | 0x00     | 4 bytes (`80 37 12 40`) |
| Clock rate           | 0x04     | 4 bytes |
| Entry point          | 0x08     | 4 bytes |
| CRC1                 | 0x10     | 4 bytes |
| CRC2                 | 0x14     | 4 bytes |
| Internal name        | 0x20     | 20 bytes |
| Code start           | 0x1000   | Boot code loads here |

Note: Other byte orderings exist -- v64 (`37 80 40 12`, byte-swapped) and n64 (`40 12 37 80`, little-endian). Convert to z64 (big-endian) before analysis.

## How to Identify Format from First Bytes

```
Read bytes at offset 0x00:
  4D 5A         -> MZ stub present -> check offset 0x3C for PE header
  58 42 45 48   -> XBE (Xbox)
  58 45 58 32   -> XEX2 (Xbox 360)
  7F 45 4C 46   -> ELF -> check 0x05 for endianness
  53 43 45 00   -> SELF (PS3)
  80 37 12 40   -> N64 z64 (big-endian)
  37 80 40 12   -> N64 v64 (byte-swapped)

No magic at 0x00:
  Check 0x104 for CE ED 66 66 -> Game Boy ROM
  Check 0xE0 for plausible PPC entry address -> DOL (GameCube/Wii)
  Check 0x7FDC/0xFFDC for checksum complement -> SNES ROM
```

## Common Tools by Format

| Format   | Tools                                                     |
|----------|-----------------------------------------------------------|
| MZ / PE  | Ghidra, IDA, PE-bear, CFF Explorer, `objdump`, `dumpbin` |
| XBE      | Ghidra (with XBE loader), XbeTool, Cxbx-Reloaded         |
| XEX2     | Ghidra (with XEX loader), xextool, xenia                 |
| DOL      | Ghidra, `doltool`, Dolphin debugger                       |
| ELF      | Ghidra, IDA, `readelf`, `objdump`, `binutils`             |
| SELF     | Ghidra, `scetool` (decrypter), RPCS3                      |
| GB ROM   | Ghidra (with SM83 module), `rgbds`, BGB debugger          |
| SNES ROM | Ghidra (with 65816 module), `bsnes` debugger, no$sns      |
| N64 z64  | Ghidra, IDA, `n64split`, Ares debugger                    |
