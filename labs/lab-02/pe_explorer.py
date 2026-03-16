"""
Lab 2: PE Explorer

Parse and display the structure of a Portable Executable (PE) file
using the pefile library.
"""

import sys
import os

try:
    import pefile
except ImportError:
    print("Error: the 'pefile' package is required. Install it with:")
    print("  pip install pefile")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Section Parsing
# ---------------------------------------------------------------------------

def dump_sections(pe):
    """Print information about each section in the PE file.

    For each section, display:
      - Name (decoded, stripped of null bytes)
      - Virtual Address
      - Virtual Size
      - Characteristics flags

    Args:
        pe: A loaded pefile.PE object.
    """
    print("--- Sections ---")
    for section in pe.sections:
        name = section.Name.decode("utf-8", errors="replace").rstrip("\x00")
        va = section.VirtualAddress
        size = section.Misc_VirtualSize
        flags = section.Characteristics
        print(f"  {name:<10s} VA: 0x{va:08x}  Size: 0x{size:08x}  Flags: 0x{flags:08x}")
    print()


# ---------------------------------------------------------------------------
# Import Parsing
# ---------------------------------------------------------------------------

def dump_imports(pe):
    """Print the import directory: each DLL and its imported functions.

    Args:
        pe: A loaded pefile.PE object.
    """
    print("--- Imports ---")
    if not hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        print("  (no imports)")
        print()
        return

    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll_name = entry.dll.decode("utf-8", errors="replace")
        print(f"  {dll_name}")
        for imp in entry.imports:
            if imp.name:
                func_name = imp.name.decode("utf-8", errors="replace")
                print(f"    {func_name}")
            else:
                print(f"    ordinal {imp.ordinal}")
    print()


# ---------------------------------------------------------------------------
# Export Parsing
# ---------------------------------------------------------------------------

def dump_exports(pe):
    """Print the export directory: each exported function name and ordinal.

    Args:
        pe: A loaded pefile.PE object.
    """
    print("--- Exports ---")
    # TODO: Check if pe has DIRECTORY_ENTRY_EXPORT. If so, iterate over
    #       pe.DIRECTORY_ENTRY_EXPORT.symbols and print each symbol's
    #       name (decoded) and ordinal. If there are no exports, print
    #       "(no exports)".
    #
    # Hint: The attribute to check is "DIRECTORY_ENTRY_EXPORT".
    #       Each symbol has .name (bytes or None) and .ordinal (int).
    print("  (not yet implemented)")
    print()


# ---------------------------------------------------------------------------
# Resource Parsing
# ---------------------------------------------------------------------------

def dump_resources(pe, indent=0):
    """Print the resource directory tree.

    Args:
        pe: A loaded pefile.PE object.
        indent: Current indentation level (for recursive display).
    """
    print("--- Resources ---")
    # TODO: Check if pe has DIRECTORY_ENTRY_RESOURCE. If so, walk the
    #       resource tree recursively. The tree has entries at:
    #         pe.DIRECTORY_ENTRY_RESOURCE.entries
    #       Each entry may have a .directory attribute (subdirectory) or
    #       a .data attribute (leaf resource).
    #
    # For each entry, print its id or name with appropriate indentation.
    # This is a stretch goal -- implement it after finishing exports.
    print("  (not yet implemented)")
    print()


# ---------------------------------------------------------------------------
# Main Display
# ---------------------------------------------------------------------------

def analyze_pe(filepath):
    """Load a PE file and display its structure.

    Args:
        filepath: Path to the PE file.
    """
    pe = pefile.PE(filepath)

    filename = os.path.basename(filepath)
    print(f"=== PE File: {filename} ===")
    print(f"Entry Point:   0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:08x}")
    print(f"Image Base:    0x{pe.OPTIONAL_HEADER.ImageBase:08x}")
    print()

    dump_sections(pe)
    dump_imports(pe)
    dump_exports(pe)
    dump_resources(pe)

    pe.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.exe|file.dll>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    analyze_pe(filepath)


if __name__ == "__main__":
    main()
