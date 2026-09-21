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


class TestExports:
    """dump_exports was a TODO that no test exercised."""

    def _pe_with_exports(self):
        pe = MagicMock()
        sym1 = MagicMock()
        sym1.name = b"CreateWidget"
        sym1.ordinal = 1
        sym2 = MagicMock()
        sym2.name = None          # exported by ordinal only
        sym2.ordinal = 2
        pe.DIRECTORY_ENTRY_EXPORT.symbols = [sym1, sym2]
        return pe

    def _capture(self, fn, *args):
        old, sys.stdout = sys.stdout, StringIO()
        try:
            fn(*args)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = old

    def test_lists_named_export(self):
        out = self._capture(pe_explorer.dump_exports, self._pe_with_exports())
        assert "CreateWidget" in out

    def test_lists_ordinal(self):
        out = self._capture(pe_explorer.dump_exports, self._pe_with_exports())
        assert "1" in out and "2" in out

    def test_unnamed_export_does_not_crash(self):
        out = self._capture(pe_explorer.dump_exports, self._pe_with_exports())
        assert "not yet implemented" not in out

    def test_no_export_directory(self):
        pe = MagicMock()
        del pe.DIRECTORY_ENTRY_EXPORT
        out = self._capture(pe_explorer.dump_exports, pe)
        assert "no exports" in out.lower()


class TestResources:
    """dump_resources was a TODO that no test exercised."""

    def _capture(self, fn, *args):
        old, sys.stdout = sys.stdout, StringIO()
        try:
            fn(*args)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = old

    def _pe_with_resources(self):
        pe = MagicMock()
        leaf = MagicMock()
        del leaf.directory
        leaf.name = None
        leaf.id = 101
        leaf.data.struct.Size = 512

        branch = MagicMock()
        branch.name = "ICON"
        branch.id = None
        branch.directory.entries = [leaf]

        pe.DIRECTORY_ENTRY_RESOURCE.entries = [branch]
        return pe

    def test_walks_into_subdirectory(self):
        out = self._capture(pe_explorer.dump_resources, self._pe_with_resources())
        assert "ICON" in out
        assert "101" in out

    def test_reports_leaf_size(self):
        out = self._capture(pe_explorer.dump_resources, self._pe_with_resources())
        assert "512" in out

    def test_no_resource_directory(self):
        pe = MagicMock()
        del pe.DIRECTORY_ENTRY_RESOURCE
        out = self._capture(pe_explorer.dump_resources, pe)
        assert "no resources" in out.lower()
