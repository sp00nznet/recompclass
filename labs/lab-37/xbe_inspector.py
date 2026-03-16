"""
Lab 37: Xbox XBE Header Inspector

Parse the header of an original Xbox XBE executable file.
All fields are little-endian (x86).
"""

import struct

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

XBE_MAGIC = 0x48454258   # "XBEH" in little-endian

# XOR keys for entry point decoding
ENTRY_RETAIL_KEY = 0xA8FC57AB
ENTRY_DEBUG_KEY  = 0x94859D4B

# XOR keys for kernel thunk table address
THUNK_RETAIL_KEY = 0x5B6D40B6
THUNK_DEBUG_KEY  = 0x46437E4B

# Section header size
SECTION_HEADER_SIZE = 56

# Common kernel import ordinals (for display)
KERNEL_IMPORTS = {
    1:   "AvGetSavedDataAddress",
    49:  "HalReturnToFirmware",
    116: "MmAllocateContiguousMemory",
    165: "NtCreateFile",
    166: "NtCreateMutant",
    187: "NtReadFile",
    236: "PsCreateSystemThreadEx",
    300: "RtlInitAnsiString",
    327: "XeLoadSection",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_u32(data, offset):
    """Read a little-endian unsigned 32-bit value."""
    return struct.unpack_from("<I", data, offset)[0]


def read_bytes(data, offset, count):
    """Read *count* raw bytes from *data* at *offset*."""
    return data[offset:offset + count]


# ---------------------------------------------------------------------------
# Parsing functions -- complete the TODOs
# ---------------------------------------------------------------------------

def validate_magic(data):
    """Check that *data* starts with the XBE magic number.

    Returns
    -------
    bool
        True if the first 4 bytes match XBE_MAGIC.
    """
    # TODO: read the first 4 bytes as a little-endian u32 and compare
    # to XBE_MAGIC.
    pass


def parse_header(data):
    """Parse the XBE image header from *data*.

    Returns
    -------
    dict with keys:
        "magic"              : int  -- should be XBE_MAGIC
        "base_address"       : int  -- image base address
        "headers_size"       : int  -- size of all headers
        "image_size"         : int  -- total image size
        "timestamp"          : int  -- build timestamp
        "cert_addr"          : int  -- certificate address
        "num_sections"       : int  -- number of sections
        "section_headers_addr": int -- file-relative section table address
        "entry_point_raw"    : int  -- XOR-encoded entry point
        "thunk_addr_raw"     : int  -- XOR-encoded thunk table address
        "num_lib_versions"   : int  -- number of library version entries
        "lib_versions_addr"  : int  -- address of library version table
    """
    # TODO: read each field from the documented offsets using read_u32.
    # Return a dict with the keys listed above.
    pass


def decode_entry_point(raw_entry, base_address, image_size):
    """Decode the XOR-encoded entry point.

    Try decoding with the retail key first.  If the result falls within
    [base_address, base_address + image_size), return (decoded, "retail").
    Otherwise try the debug key and return (decoded, "debug").
    If neither works, return (raw_entry, "unknown").

    Returns
    -------
    tuple of (int, str)
        (decoded_address, variant_string)
    """
    # TODO: XOR raw_entry with ENTRY_RETAIL_KEY, check range.
    #       If not in range, try ENTRY_DEBUG_KEY.
    pass


def decode_thunk_addr(raw_thunk, base_address, image_size):
    """Decode the XOR-encoded kernel thunk table address.

    Same approach as decode_entry_point but using THUNK_RETAIL_KEY /
    THUNK_DEBUG_KEY.

    Returns
    -------
    tuple of (int, str)
    """
    # TODO: same pattern as decode_entry_point
    pass


def parse_section_header(data, offset):
    """Parse one 56-byte section header at *offset*.

    Returns
    -------
    dict with keys:
        "flags"      : int
        "vaddr"      : int  -- virtual address
        "vsize"      : int  -- virtual size
        "raw_addr"   : int  -- raw (file) address
        "raw_size"   : int  -- raw (file) size
        "name_addr"  : int  -- address of the section name string
    """
    # TODO: read the six u32 fields at consecutive 4-byte offsets
    pass


def parse_sections(data, header):
    """Parse all section headers.

    The section table starts at header["section_headers_addr"] relative
    to header["base_address"] (convert to file offset by subtracting
    base_address).  There are header["num_sections"] entries, each
    SECTION_HEADER_SIZE bytes.

    Returns
    -------
    list of dict
        Each dict is from parse_section_header.
    """
    # TODO: calculate the file offset of the section table, then parse
    # each section header.
    pass


def read_section_name(data, name_addr, base_address):
    """Read a null-terminated section name string.

    Parameters
    ----------
    data : bytes
        Full XBE file data.
    name_addr : int
        Virtual address of the name string.
    base_address : int
        Image base address (subtract to get file offset).

    Returns
    -------
    str
        The section name (ASCII).
    """
    # TODO: convert name_addr to a file offset, then read bytes until
    # a null terminator (0x00) or 32 bytes max.
    pass


def parse_kernel_thunk_table(data, thunk_file_offset):
    """Parse the kernel import thunk table.

    Starting at *thunk_file_offset*, read u32 values until a zero
    terminator.  Each non-zero value is an ordinal OR'd with 0x80000000.
    Mask off the high bit to get the actual ordinal.

    Returns
    -------
    list of int
        Ordinal numbers of imported kernel functions.
    """
    # TODO: read u32s in a loop, mask off bit 31, collect ordinals,
    # stop at zero.
    pass


# ---------------------------------------------------------------------------
# High-level inspect function
# ---------------------------------------------------------------------------

def inspect_xbe(data):
    """Full inspection of an XBE file.

    Returns
    -------
    dict with keys:
        "valid"       : bool
        "header"      : dict (from parse_header)
        "entry_point" : int
        "entry_variant": str ("retail" / "debug")
        "sections"    : list of dict (with added "name" key)
        "kernel_imports": list of int (ordinals)
    """
    result = {"valid": validate_magic(data)}
    if not result["valid"]:
        return result

    hdr = parse_header(data)
    result["header"] = hdr

    ep, variant = decode_entry_point(
        hdr["entry_point_raw"], hdr["base_address"], hdr["image_size"])
    result["entry_point"] = ep
    result["entry_variant"] = variant

    sections = parse_sections(data, hdr)
    for sec in sections:
        sec["name"] = read_section_name(data, sec["name_addr"],
                                         hdr["base_address"])
    result["sections"] = sections

    thunk_decoded, _ = decode_thunk_addr(
        hdr["thunk_addr_raw"], hdr["base_address"], hdr["image_size"])
    thunk_file_off = thunk_decoded - hdr["base_address"]
    result["kernel_imports"] = parse_kernel_thunk_table(data, thunk_file_off)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python xbe_inspector.py <file.xbe>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        raw = f.read()

    info = inspect_xbe(raw)
    if not info["valid"]:
        print("Not a valid XBE file.")
        sys.exit(1)

    hdr = info["header"]
    print("=== XBE Header ===")
    print(f"Magic:          XBEH")
    print(f"Base Address:   0x{hdr['base_address']:08X}")
    print(f"Entry Point:    0x{info['entry_point']:08X} ({info['entry_variant']})")
    print(f"Sections:       {hdr['num_sections']}")
    for sec in info["sections"]:
        print(f"  {sec['name']:<8s} VA=0x{sec['vaddr']:08X}  "
              f"Size=0x{sec['vsize']:08X}  Raw=0x{sec['raw_addr']:08X}")
    ordinals = info["kernel_imports"]
    print(f"Kernel Imports: {ordinals}")
