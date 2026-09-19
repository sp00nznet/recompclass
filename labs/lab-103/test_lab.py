"""
Tests for Lab 103: Symbol Importer
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import symimport


V1 = """
# upstream symbols
80056780 Player_Init 0x120
800568A0 Player_Update 0x80
80056920 Enemy_Init 0x40
"""

V2 = """
80056780 Player_Init 0x140
800568C0 Player_Update 0x80
80056960 Boss_Init 0x60
"""


class TestParse:
    def test_count(self):
        s = symimport.parse_symbols(V1)
        assert s is not None, "parse_symbols() returned None"
        assert len(s) == 3

    def test_fields(self):
        s = symimport.parse_symbols(V1)
        assert s[0]["addr"] == 0x80056780
        assert s[0]["name"] == "Player_Init"
        assert s[0]["size"] == 0x120

    def test_skips_comments(self):
        assert all(not x["name"].startswith("#") for x in symimport.parse_symbols(V1))

    def test_malformed(self):
        import pytest
        with pytest.raises(ValueError):
            symimport.parse_symbols("80056780 OnlyTwoFields")


class TestValidate:
    def test_clean(self):
        p = symimport.validate_symbols(symimport.parse_symbols(V1))
        assert p is not None, "validate_symbols() returned None"
        assert p == []

    def test_zero_size(self):
        p = symimport.validate_symbols([{"addr": 0x100, "name": "A", "size": 0}])
        assert len(p) == 1 and "A" in p[0]

    def test_duplicate_address(self):
        syms = [{"addr": 0x100, "name": "A", "size": 0x10},
                {"addr": 0x100, "name": "B", "size": 0x10}]
        assert symimport.validate_symbols(syms)

    def test_overlap(self):
        syms = [{"addr": 0x100, "name": "A", "size": 0x100},
                {"addr": 0x180, "name": "B", "size": 0x10}]
        p = symimport.validate_symbols(syms)
        assert any("overlap" in x.lower() for x in p)


class TestToFunctionSet:
    def test_provenance(self):
        fs = symimport.to_function_set(symimport.parse_symbols(V1), "abc123")
        assert fs is not None, "to_function_set() returned None"
        assert fs["source_commit"] == "abc123"
        assert fs["count"] == 3

    def test_lookup(self):
        fs = symimport.to_function_set(symimport.parse_symbols(V1), "abc123")
        assert fs["functions"]["Player_Init"]["addr"] == 0x80056780

    def test_duplicate_name(self):
        import pytest
        syms = [{"addr": 1, "name": "A", "size": 1}, {"addr": 2, "name": "A", "size": 1}]
        with pytest.raises(ValueError):
            symimport.to_function_set(syms, "x")


class TestDiff:
    def sets(self):
        a = symimport.to_function_set(symimport.parse_symbols(V1), "v1")
        b = symimport.to_function_set(symimport.parse_symbols(V2), "v2")
        return a, b

    def test_added_and_removed(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        assert d is not None, "diff_imports() returned None"
        assert d["added"] == ["Boss_Init"]
        assert d["removed"] == ["Enemy_Init"]

    def test_moved(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        moved = {m["name"] for m in d["moved"]}
        assert "Player_Update" in moved

    def test_resized(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        resized = {r["name"]: r for r in d["resized"]}
        assert resized["Player_Init"]["from"] == 0x120
        assert resized["Player_Init"]["to"] == 0x140

    def test_commits_recorded(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        assert d["from_commit"] == "v1" and d["to_commit"] == "v2"

    def test_first_import(self):
        _, b = self.sets()
        d = symimport.diff_imports(None, b)
        assert len(d["added"]) == 3
        assert d["from_commit"] is None
