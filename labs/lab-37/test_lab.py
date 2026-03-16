"""
Tests for Lab 37: Xbox XBE Header Inspector

Uses a synthetic XBE image to verify parsing functions.
"""

import struct
import xbe_inspector as xbe


# ---------------------------------------------------------------------------
# Helpers: build a minimal synthetic XBE
# ---------------------------------------------------------------------------

BASE_ADDR  = 0x00010000
IMAGE_SIZE = 0x00020000

# Pre-computed encoded values
ENTRY_POINT     = 0x00015A3C
ENTRY_ENCODED   = ENTRY_POINT ^ xbe.ENTRY_RETAIL_KEY

THUNK_ADDR      = 0x00018000
THUNK_ENCODED   = THUNK_ADDR ^ xbe.THUNK_RETAIL_KEY


def build_minimal_xbe():
    """Build a minimal synthetic XBE for testing.

    Layout (file offsets):
      0x0000 - 0x017F: XBE header
      0x0180 - 0x01FF: padding
      0x0200 - 0x02A7: 3 section headers (56 bytes each)
      0x02A8 - 0x02C0: section name strings
      0x8000 - 0x8010: kernel thunk table
    """
    # Start with a large zero-filled buffer
    data = bytearray(IMAGE_SIZE)

    # --- XBE header ---
    struct.pack_into("<I", data, 0x000, xbe.XBE_MAGIC)
    # Signature: 256 bytes of 0xAA
    data[0x004:0x104] = b"\xAA" * 256
    struct.pack_into("<I", data, 0x104, BASE_ADDR)
    struct.pack_into("<I", data, 0x108, 0x1000)       # headers size
    struct.pack_into("<I", data, 0x10C, IMAGE_SIZE)    # image size
    struct.pack_into("<I", data, 0x110, 0x0180)        # image header size
    struct.pack_into("<I", data, 0x114, 0x60000000)    # timestamp
    struct.pack_into("<I", data, 0x118, 0)             # cert addr
    struct.pack_into("<I", data, 0x11C, 3)             # num sections
    # section headers at file offset 0x0200 -> VA = BASE + 0x0200
    struct.pack_into("<I", data, 0x120, BASE_ADDR + 0x0200)
    struct.pack_into("<I", data, 0x124, 0)             # init flags
    struct.pack_into("<I", data, 0x128, ENTRY_ENCODED) # entry point (encoded)
    # pad to 0x16C for thunk addr
    struct.pack_into("<I", data, 0x16C, THUNK_ENCODED)
    struct.pack_into("<I", data, 0x174, 0)             # num lib versions
    struct.pack_into("<I", data, 0x178, 0)             # lib versions addr

    # --- Section headers at file offset 0x0200 ---
    names_base = BASE_ADDR + 0x02A8

    sections = [
        # (flags, vaddr, vsize, raw_addr, raw_size, name_offset)
        (0, BASE_ADDR + 0x1000, 0x8000, 0x1000, 0x8000, 0),
        (0, BASE_ADDR + 0x9000, 0x2000, 0x9000, 0x2000, 8),
        (0, BASE_ADDR + 0xB000, 0x1000, 0xB000, 0x1000, 16),
    ]
    names = [b".text\x00\x00\x00", b".rdata\x00\x00", b".data\x00\x00\x00"]

    for i, (flags, va, vs, ra, rs, noff) in enumerate(sections):
        off = 0x0200 + i * 56
        struct.pack_into("<I", data, off + 0x00, flags)
        struct.pack_into("<I", data, off + 0x04, va)
        struct.pack_into("<I", data, off + 0x08, vs)
        struct.pack_into("<I", data, off + 0x0C, ra)
        struct.pack_into("<I", data, off + 0x10, rs)
        struct.pack_into("<I", data, off + 0x14, names_base + noff)

    # --- Section name strings at file offset 0x02A8 ---
    for i, name in enumerate(names):
        data[0x02A8 + i * 8: 0x02A8 + i * 8 + len(name)] = name

    # --- Kernel thunk table at file offset 0x8000 ---
    thunk_off = THUNK_ADDR - BASE_ADDR
    ordinals = [166, 187, 236, 300]
    for j, ordinal in enumerate(ordinals):
        struct.pack_into("<I", data, thunk_off + j * 4, ordinal | 0x80000000)
    struct.pack_into("<I", data, thunk_off + len(ordinals) * 4, 0)  # terminator

    return bytes(data)


FAKE_XBE = build_minimal_xbe()


# ---------------------------------------------------------------------------
# Magic validation
# ---------------------------------------------------------------------------

class TestValidateMagic:
    def test_valid_magic(self):
        assert xbe.validate_magic(FAKE_XBE) is True

    def test_invalid_magic(self):
        bad = b"\x00\x00\x00\x00" + b"\x00" * 300
        assert xbe.validate_magic(bad) is False

    def test_wrong_magic(self):
        bad = struct.pack("<I", 0x12345678) + b"\x00" * 300
        assert xbe.validate_magic(bad) is False


# ---------------------------------------------------------------------------
# Header parsing
# ---------------------------------------------------------------------------

class TestParseHeader:
    def test_base_address(self):
        hdr = xbe.parse_header(FAKE_XBE)
        assert hdr["base_address"] == BASE_ADDR

    def test_image_size(self):
        hdr = xbe.parse_header(FAKE_XBE)
        assert hdr["image_size"] == IMAGE_SIZE

    def test_num_sections(self):
        hdr = xbe.parse_header(FAKE_XBE)
        assert hdr["num_sections"] == 3

    def test_entry_point_raw(self):
        hdr = xbe.parse_header(FAKE_XBE)
        assert hdr["entry_point_raw"] == ENTRY_ENCODED

    def test_thunk_addr_raw(self):
        hdr = xbe.parse_header(FAKE_XBE)
        assert hdr["thunk_addr_raw"] == THUNK_ENCODED


# ---------------------------------------------------------------------------
# Entry point decoding
# ---------------------------------------------------------------------------

class TestDecodeEntryPoint:
    def test_retail_decode(self):
        ep, variant = xbe.decode_entry_point(ENTRY_ENCODED, BASE_ADDR, IMAGE_SIZE)
        assert ep == ENTRY_POINT
        assert variant == "retail"

    def test_debug_decode(self):
        debug_ep = 0x00015A3C
        debug_enc = debug_ep ^ xbe.ENTRY_DEBUG_KEY
        # Make the retail decode fall outside the image range
        ep, variant = xbe.decode_entry_point(debug_enc, BASE_ADDR, IMAGE_SIZE)
        assert variant == "debug"
        assert ep == debug_ep

    def test_unknown(self):
        # Both decodes should be out of range for a tiny image
        _, variant = xbe.decode_entry_point(0xFFFFFFFF, 0, 0x100)
        assert variant == "unknown"


# ---------------------------------------------------------------------------
# Thunk address decoding
# ---------------------------------------------------------------------------

class TestDecodeThunkAddr:
    def test_retail_thunk(self):
        addr, variant = xbe.decode_thunk_addr(THUNK_ENCODED, BASE_ADDR, IMAGE_SIZE)
        assert addr == THUNK_ADDR
        assert variant == "retail"


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------

class TestParseSections:
    def test_num_sections(self):
        hdr = xbe.parse_header(FAKE_XBE)
        sections = xbe.parse_sections(FAKE_XBE, hdr)
        assert len(sections) == 3

    def test_section_fields(self):
        hdr = xbe.parse_header(FAKE_XBE)
        sections = xbe.parse_sections(FAKE_XBE, hdr)
        sec0 = sections[0]
        assert sec0["vaddr"] == BASE_ADDR + 0x1000
        assert sec0["vsize"] == 0x8000
        assert sec0["raw_addr"] == 0x1000

    def test_section_names(self):
        hdr = xbe.parse_header(FAKE_XBE)
        sections = xbe.parse_sections(FAKE_XBE, hdr)
        for sec in sections:
            sec["name"] = xbe.read_section_name(
                FAKE_XBE, sec["name_addr"], hdr["base_address"])
        assert sections[0]["name"] == ".text"
        assert sections[1]["name"] == ".rdata"
        assert sections[2]["name"] == ".data"


# ---------------------------------------------------------------------------
# Kernel thunk table
# ---------------------------------------------------------------------------

class TestKernelThunkTable:
    def test_ordinals(self):
        thunk_off = THUNK_ADDR - BASE_ADDR
        ordinals = xbe.parse_kernel_thunk_table(FAKE_XBE, thunk_off)
        assert ordinals == [166, 187, 236, 300]

    def test_empty_table(self):
        # Table that starts with zero terminator
        data = struct.pack("<I", 0) + b"\x00" * 100
        ordinals = xbe.parse_kernel_thunk_table(data, 0)
        assert ordinals == []


# ---------------------------------------------------------------------------
# Full inspection
# ---------------------------------------------------------------------------

class TestInspectXbe:
    def test_full_inspection(self):
        info = xbe.inspect_xbe(FAKE_XBE)
        assert info["valid"] is True
        assert info["entry_point"] == ENTRY_POINT
        assert info["entry_variant"] == "retail"
        assert len(info["sections"]) == 3
        assert info["sections"][0]["name"] == ".text"
        assert info["kernel_imports"] == [166, 187, 236, 300]

    def test_invalid_xbe(self):
        info = xbe.inspect_xbe(b"\x00" * 1024)
        assert info["valid"] is False
