"""
Tests for Lab 2: PE Explorer

Uses a mock PE object to verify parsing functions without needing
a real PE file on disk.
"""

import sys
import os
from unittest.mock import MagicMock
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pe_explorer


def make_mock_pe():
    """Create a mock pefile.PE object with sections and imports."""
    pe = MagicMock()

    # Optional header
    pe.OPTIONAL_HEADER.AddressOfEntryPoint = 0x1000
    pe.OPTIONAL_HEADER.ImageBase = 0x00400000

    # Sections
    section1 = MagicMock()
    section1.Name = b".text\x00\x00\x00"
    section1.VirtualAddress = 0x1000
    section1.Misc_VirtualSize = 0x5000
    section1.Characteristics = 0x60000020

    section2 = MagicMock()
    section2.Name = b".data\x00\x00\x00"
    section2.VirtualAddress = 0x6000
    section2.Misc_VirtualSize = 0x1000
    section2.Characteristics = 0xC0000040

    pe.sections = [section1, section2]

    # Imports
    imp_func1 = MagicMock()
    imp_func1.name = b"GetProcAddress"
    imp_func1.ordinal = None

    imp_func2 = MagicMock()
    imp_func2.name = b"LoadLibraryA"
    imp_func2.ordinal = None

    imp_entry = MagicMock()
    imp_entry.dll = b"KERNEL32.dll"
    imp_entry.imports = [imp_func1, imp_func2]

    pe.DIRECTORY_ENTRY_IMPORT = [imp_entry]

    return pe


class TestDumpSections:
    def test_sections_printed(self, capsys):
        pe = make_mock_pe()
        pe_explorer.dump_sections(pe)
        output = capsys.readouterr().out
        assert ".text" in output
        assert ".data" in output
        assert "0x60000020" in output

    def test_section_count(self):
        pe = make_mock_pe()
        assert len(pe.sections) == 2


class TestDumpImports:
    def test_imports_printed(self, capsys):
        pe = make_mock_pe()
        pe_explorer.dump_imports(pe)
        output = capsys.readouterr().out
        assert "KERNEL32.dll" in output
        assert "GetProcAddress" in output
        assert "LoadLibraryA" in output

    def test_no_imports(self, capsys):
        pe = MagicMock(spec=[])
        pe_explorer.dump_imports(pe)
        output = capsys.readouterr().out
        assert "no imports" in output


class TestDumpExports:
    def test_exports_callable(self, capsys):
        """Verify dump_exports runs without error (even if not yet implemented)."""
        pe = make_mock_pe()
        pe_explorer.dump_exports(pe)
        # Should produce some output without crashing
        output = capsys.readouterr().out
        assert len(output) > 0
