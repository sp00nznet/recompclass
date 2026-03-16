"""
Tests for Lab 50: Project Regression Harness

Tests the regression runner components using mock data, without needing
real binaries or TOML libraries for the core logic tests.
"""

import hashlib
import os
import tempfile
import pytest

import regression_runner as rr


# ---------------------------------------------------------------------------
# MD5 computation
# ---------------------------------------------------------------------------

class TestComputeMd5:
    def test_empty(self):
        # MD5 of empty bytes
        expected = hashlib.md5(b"").hexdigest()
        assert rr.compute_md5(b"") == expected

    def test_hello(self):
        expected = hashlib.md5(b"hello").hexdigest()
        assert rr.compute_md5(b"hello") == expected

    def test_known_value(self):
        # MD5("hello world") = 5eb63bbbe01eeed093cb22bb8f5acdc3
        assert rr.compute_md5(b"hello world") == "5eb63bbbe01eeed093cb22bb8f5acdc3"


# ---------------------------------------------------------------------------
# Result creation
# ---------------------------------------------------------------------------

class TestMakeResult:
    def test_pass(self):
        r = rr.make_result("test1", "pass", "abc", "abc", True, "")
        assert r["name"] == "test1"
        assert r["status"] == "pass"
        assert r["exit_code_match"] is True

    def test_fail(self):
        r = rr.make_result("test2", "fail", "abc", "def", True, "MD5 mismatch")
        assert r["status"] == "fail"
        assert r["message"] == "MD5 mismatch"


# ---------------------------------------------------------------------------
# Config parsing
# ---------------------------------------------------------------------------

class TestParseConfig:
    def test_basic_config(self):
        config = {
            "project": {"name": "TestProject"},
            "tests": [
                {
                    "name": "test1",
                    "binary": "echo",
                    "args": ["hi"],
                    "input_file": "",
                    "expected_stdout_md5": "abc123",
                    "expected_exit_code": 0,
                },
            ],
        }
        name, tests = rr.parse_config(config)
        assert name == "TestProject"
        assert len(tests) == 1
        assert tests[0]["name"] == "test1"
        assert tests[0]["binary"] == "echo"

    def test_defaults(self):
        config = {
            "project": {"name": "P"},
            "tests": [
                {
                    "name": "minimal",
                    "binary": "true",
                },
            ],
        }
        name, tests = rr.parse_config(config)
        assert tests[0]["args"] == []
        assert tests[0]["input_file"] == ""
        assert tests[0]["expected_stdout_md5"] == ""
        assert tests[0]["expected_exit_code"] == 0

    def test_multiple_tests(self):
        config = {
            "project": {"name": "Multi"},
            "tests": [
                {"name": "a", "binary": "echo", "args": ["1"]},
                {"name": "b", "binary": "echo", "args": ["2"]},
                {"name": "c", "binary": "echo", "args": ["3"]},
            ],
        }
        _, tests = rr.parse_config(config)
        assert len(tests) == 3


# ---------------------------------------------------------------------------
# TOML loading (skipped if no TOML library)
# ---------------------------------------------------------------------------

class TestLoadConfig:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            rr.load_config("/nonexistent/path/config.toml")

    @pytest.mark.skipif(rr.tomllib is None, reason="TOML library not available")
    def test_load_sample(self):
        sample_path = os.path.join(os.path.dirname(__file__), "sample_config.toml")
        config = rr.load_config(sample_path)
        assert "project" in config
        assert "tests" in config
        assert config["project"]["name"] == "SampleRecomp"
        assert len(config["tests"]) == 2

    def test_no_toml_library(self):
        if rr.tomllib is None:
            with pytest.raises(RuntimeError, match="TOML"):
                rr.load_config("any_file.toml")


# ---------------------------------------------------------------------------
# Binary execution
# ---------------------------------------------------------------------------

class TestRunTestBinary:
    def test_echo(self):
        stdout, code = rr.run_test_binary("echo", ["hello"])
        # echo adds a newline
        assert b"hello" in stdout
        assert code == 0

    def test_nonexistent_binary(self):
        stdout, code = rr.run_test_binary("nonexistent_binary_xyz", [])
        assert code == -1

    def test_with_input_file(self):
        # Create a temp file with input data
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt",
                                          delete=False) as f:
            f.write(b"test input\n")
            tmp_path = f.name

        try:
            # Use 'cat' on Unix-like systems (or the test will be skipped)
            if os.name == "nt":
                # On Windows, use 'findstr' with pattern "." to echo stdin
                stdout, code = rr.run_test_binary(
                    "findstr", [".*"], input_file=tmp_path)
            else:
                stdout, code = rr.run_test_binary(
                    "cat", [], input_file=tmp_path)
            assert b"test input" in stdout
            assert code == 0
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Single test execution
# ---------------------------------------------------------------------------

class TestRunSingleTest:
    def test_passing_test(self):
        # Compute what echo "hello" produces
        import subprocess
        proc = subprocess.run(["echo", "hello"], capture_output=True)
        expected_md5 = hashlib.md5(proc.stdout).hexdigest()

        test = {
            "name": "echo_test",
            "binary": "echo",
            "args": ["hello"],
            "input_file": "",
            "expected_stdout_md5": expected_md5,
            "expected_exit_code": 0,
        }
        result = rr.run_single_test(test)
        assert result["status"] == "pass"
        assert result["exit_code_match"] is True

    def test_failing_md5(self):
        test = {
            "name": "bad_md5",
            "binary": "echo",
            "args": ["something"],
            "input_file": "",
            "expected_stdout_md5": "0000000000000000000000000000dead",
            "expected_exit_code": 0,
        }
        result = rr.run_single_test(test)
        assert result["status"] == "fail"

    def test_error_on_missing_binary(self):
        test = {
            "name": "missing",
            "binary": "nonexistent_command_xyz_123",
            "args": [],
            "input_file": "",
            "expected_stdout_md5": "",
            "expected_exit_code": 0,
        }
        result = rr.run_single_test(test)
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

class TestFormatReport:
    def test_format(self):
        summary = {
            "project_name": "TestProject",
            "results": [
                rr.make_result("t1", "pass", "abc", "abc", True, ""),
                rr.make_result("t2", "fail", "abc", "def", True, "MD5 mismatch"),
            ],
            "passed": 1,
            "failed": 1,
            "errors": 0,
        }
        report = rr.format_report(summary)
        assert "TestProject" in report
        assert "[PASS] t1" in report
        assert "[FAIL] t2" in report
        assert "1 passed" in report
        assert "1 failed" in report

    def test_all_pass(self):
        summary = {
            "project_name": "Perfect",
            "results": [
                rr.make_result("t1", "pass", "a", "a", True, ""),
            ],
            "passed": 1,
            "failed": 0,
            "errors": 0,
        }
        report = rr.format_report(summary)
        assert "1 passed" in report
        assert "0 failed" in report
