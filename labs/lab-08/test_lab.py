"""
Lab 8 Tests: DOS MZ Executable Parser

Tests with crafted minimal MZ binaries to verify correct header parsing,
relocation table parsing, and EXEPACK detection.
"""

import struct
import unittest
from mz_parser import MZParser, MZHeader, RelocationEntry, MZ_MAGIC


def build_mz_binary(
    num_relocs=0,
    reloc_entries=None,
    code=b"",
    initial_cs=0,
    initial_ip=0,
    initial_ss=0,
    initial_sp=0x100,
    extra_header_data=b"",
):
    """
    Helper to build a minimal MZ binary for testing.

    The header is always 2 paragraphs (32 bytes).
    Relocation table starts at offset 0x1C (right after the fixed header).
    """
    if reloc_entries is None:
        reloc_entries = []

    header_para = 2  # 32 bytes
    reloc_data = b""
    for offset, segment in reloc_entries:
        reloc_data += struct.pack("<HH", offset, segment)

    # Total file content: header + reloc entries + code
    total_data = bytearray(header_para * 16)
    # We will build the header into total_data, then append reloc + code.

    image = reloc_data + extra_header_data + code
    full_file = bytes(header_para * 16) + image

    # Calculate pages and last-page bytes
    file_len = len(full_file)
    pages = (file_len + 511) // 512
    last_page_bytes = file_len % 512

    header = struct.pack("<14H",
        MZ_MAGIC,
        last_page_bytes,
        pages,
        num_relocs,
        header_para,
        0,          # Min extra
        0xFFFF,     # Max extra
        initial_ss,
        initial_sp,
        0,          # Checksum
        initial_ip,
        initial_cs,
        0x1C,       # Relocation table offset
        0,          # Overlay number
    )

    # Overwrite the header portion
    result = bytearray(header)
    # Pad to 32 bytes
    result += b"\x00" * (header_para * 16 - len(header))
    # Append image (reloc entries + code)
    result += image

    return bytes(result)


class TestMZHeaderParsing(unittest.TestCase):
    """Test basic MZ header parsing."""

    def test_valid_magic(self):
        data = build_mz_binary(code=b"\xCC")
        parser = MZParser(data)
        self.assertTrue(parser.parse())
        self.assertTrue(parser.header.is_valid())
        self.assertEqual(parser.header.magic, MZ_MAGIC)

    def test_invalid_magic(self):
        data = bytearray(build_mz_binary(code=b"\xCC"))
        data[0] = 0x00  # Corrupt magic
        data[1] = 0x00
        parser = MZParser(bytes(data))
        self.assertFalse(parser.parse())

    def test_data_too_short(self):
        parser = MZParser(b"MZ")
        self.assertFalse(parser.parse())

    def test_header_fields(self):
        data = build_mz_binary(
            initial_cs=0x0010,
            initial_ip=0x0100,
            initial_ss=0x0020,
            initial_sp=0x0200,
            code=b"\x90" * 16,
        )
        parser = MZParser(data)
        self.assertTrue(parser.parse())
        self.assertEqual(parser.header.initial_cs, 0x0010)
        self.assertEqual(parser.header.initial_ip, 0x0100)
        self.assertEqual(parser.header.initial_ss, 0x0020)
        self.assertEqual(parser.header.initial_sp, 0x0200)

    def test_header_size_in_bytes(self):
        data = build_mz_binary(code=b"\x90")
        parser = MZParser(data)
        parser.parse()
        # Header is 2 paragraphs = 32 bytes
        self.assertEqual(parser.header.header_size_bytes, 32)

    def test_entry_point_text(self):
        data = build_mz_binary(initial_cs=0x1234, initial_ip=0x5678, code=b"\x90")
        parser = MZParser(data)
        parser.parse()
        self.assertEqual(parser.header.entry_point_text, "1234:5678")


class TestRelocationTable(unittest.TestCase):
    """Test relocation table parsing."""

    def test_no_relocations(self):
        data = build_mz_binary(num_relocs=0, code=b"\x90" * 4)
        parser = MZParser(data)
        parser.parse()
        self.assertEqual(len(parser.relocations), 0)

    def test_single_relocation(self):
        data = build_mz_binary(
            num_relocs=1,
            reloc_entries=[(0x0004, 0x0000)],
            code=b"\x90" * 16,
        )
        parser = MZParser(data)
        parser.parse()
        self.assertEqual(len(parser.relocations), 1)
        self.assertEqual(parser.relocations[0].offset, 0x0004)
        self.assertEqual(parser.relocations[0].segment, 0x0000)

    def test_multiple_relocations(self):
        entries = [(0x0004, 0x0000), (0x0010, 0x0100), (0x0020, 0x0200)]
        data = build_mz_binary(
            num_relocs=3,
            reloc_entries=entries,
            code=b"\x90" * 64,
        )
        parser = MZParser(data)
        parser.parse()
        self.assertEqual(len(parser.relocations), 3)
        for i, (expected_off, expected_seg) in enumerate(entries):
            self.assertEqual(parser.relocations[i].offset, expected_off)
            self.assertEqual(parser.relocations[i].segment, expected_seg)

    def test_relocation_linear_address(self):
        entry = RelocationEntry(offset=0x0010, segment=0x1000)
        # Linear = 0x1000 * 16 + 0x0010 = 0x10010
        self.assertEqual(entry.linear_address, 0x10010)


class TestExepackDetection(unittest.TestCase):
    """Test EXEPACK compression detection."""

    def test_not_exepacked(self):
        data = build_mz_binary(code=b"\xB8\x00\x4C\xCD\x21")
        parser = MZParser(data)
        parser.parse()
        self.assertFalse(parser.is_exepacked)

    def test_exepack_signature_in_code(self):
        """EXEPACK string in the code region should be detected."""
        code = b"\x90" * 16 + b"EXEPACK" + b"\x90" * 16
        data = build_mz_binary(code=code)
        parser = MZParser(data)
        parser.parse()
        self.assertTrue(parser.is_exepacked)


class TestCodeImage(unittest.TestCase):
    """Test code image extraction."""

    def test_get_code_image(self):
        code = bytes([0xB8, 0x00, 0x4C, 0xCD, 0x21])
        data = build_mz_binary(code=code)
        parser = MZParser(data)
        parser.parse()
        image = parser.get_code_image()
        # The image starts after the header; code is at the end of the image
        self.assertTrue(image.endswith(code))

    def test_apply_relocations_not_implemented(self):
        data = build_mz_binary(code=b"\x90")
        parser = MZParser(data)
        parser.parse()
        with self.assertRaises(NotImplementedError):
            parser.apply_relocations()

    def test_detect_overlays_not_implemented(self):
        data = build_mz_binary(code=b"\x90")
        parser = MZParser(data)
        parser.parse()
        with self.assertRaises(NotImplementedError):
            parser.detect_overlays()


if __name__ == "__main__":
    unittest.main()
