# Lab 2: PE Explorer

## Objective

Explore the Portable Executable (PE) format used by Windows executables and
DLLs. You will parse and display the internal structure of a PE file, including
its section table, import directory, and entry point.

By the end of this lab you will be able to:

- Use the `pefile` Python library to load and inspect PE binaries
- Understand the role of sections, imports, and exports in an executable
- Identify the entry point and understand its significance for recompilation
- Navigate the PE data directories

## Background

The PE format is the standard executable format on Windows. It evolved from
COFF (Common Object File Format) and contains rich metadata about how the
operating system should load the binary into memory. Understanding PE structure
is essential for any Windows-targeted static recompilation project.

Key structures:

- **Sections**: Named blocks (.text, .data, .rdata, etc.) with different
  permissions and purposes.
- **Import Directory**: Lists DLLs and functions the executable depends on.
- **Export Directory**: Lists functions the binary makes available to others.
- **Entry Point**: The relative virtual address where execution begins.

## Prerequisites

Install the `pefile` library:

```
pip install pefile
```

## Instructions

1. Open `pe_explorer.py` and read through the starter code.
2. Complete each section marked with a `TODO` comment.
3. Run the script against any PE file (.exe or .dll):
   ```
   python pe_explorer.py C:\Windows\System32\notepad.exe
   ```
4. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output Format

```
=== PE File: notepad.exe ===
Entry Point:   0x00012345
Image Base:    0x00400000

--- Sections ---
  .text     VA: 0x00001000  Size: 0x00034000  Flags: 0x60000020
  .rdata    VA: 0x00036000  Size: 0x0000e000  Flags: 0x40000040
  .data     VA: 0x00044000  Size: 0x00002000  Flags: 0xc0000040
  ...

--- Imports ---
  KERNEL32.dll
    GetProcAddress
    LoadLibraryA
    ...

--- Exports ---
  (no exports)
```
