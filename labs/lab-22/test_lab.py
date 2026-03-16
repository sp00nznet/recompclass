"""
Tests for Lab 22: Ghidra Script - Function Exporter
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

from mock_ghidra import make_test_program
import export_functions


PROGRAM = make_test_program()


class TestGetAllFunctions:
    def test_returns_list(self):
        result = export_functions.get_all_functions(PROGRAM)
        assert result is not None, "get_all_functions() returned None"
        assert isinstance(result, list)

    def test_correct_count(self):
        result = export_functions.get_all_functions(PROGRAM)
        assert len(result) == 5

    def test_function_names(self):
        result = export_functions.get_all_functions(PROGRAM)
        names = [f["name"] for f in result]
        assert "main" in names
        assert "init_hw" in names
        assert "game_loop" in names

    def test_address_format(self):
        result = export_functions.get_all_functions(PROGRAM)
        for func in result:
            assert func["address"].startswith("0x"), \
                f"Address should start with '0x', got {func['address']}"
            # Should be 0x + 8 hex digits
            hex_part = func["address"][2:]
            assert len(hex_part) == 8, \
                f"Address hex part should be 8 digits, got '{hex_part}'"

    def test_main_address(self):
        result = export_functions.get_all_functions(PROGRAM)
        main_func = [f for f in result if f["name"] == "main"][0]
        assert main_func["address"].upper() == "0x08000100"

    def test_sizes(self):
        result = export_functions.get_all_functions(PROGRAM)
        by_name = {f["name"]: f for f in result}
        assert by_name["main"]["size"] == 64
        assert by_name["init_hw"]["size"] == 32
        assert by_name["game_loop"]["size"] == 128


class TestExportToJson:
    def test_returns_dict(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            result = export_functions.export_to_json(PROGRAM, path)
            assert result is not None, "export_to_json() returned None"
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_writes_valid_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_functions.export_to_json(PROGRAM, path)
            with open(path) as f:
                data = json.load(f)
            assert "functions" in data
            assert "function_count" in data
            assert "binary" in data
        finally:
            os.unlink(path)

    def test_binary_name(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            data = export_functions.export_to_json(PROGRAM, path)
            assert data["binary"] == "test_binary"
        finally:
            os.unlink(path)

    def test_function_count_matches(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            data = export_functions.export_to_json(PROGRAM, path)
            assert data["function_count"] == len(data["functions"])
            assert data["function_count"] == 5
        finally:
            os.unlink(path)
