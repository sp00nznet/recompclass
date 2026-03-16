"""
Lab 50: Project Regression Harness

A regression test runner that reads TOML config, executes binaries,
and compares output checksums against expected values.
"""

import hashlib
import subprocess
import sys

# ---------------------------------------------------------------------------
# TOML loading -- handle Python 3.11+ (tomllib) and older (tomli)
# ---------------------------------------------------------------------------

try:
    import tomllib                   # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib      # pip install tomli
    except ModuleNotFoundError:
        tomllib = None


# ---------------------------------------------------------------------------
# Result dataclass-like dict
# ---------------------------------------------------------------------------

def make_result(name, status, expected_md5="", actual_md5="",
                exit_code_match=True, message=""):
    """Create a test result dict.

    Parameters
    ----------
    name : str
    status : str
        "pass", "fail", or "error"
    expected_md5 : str
    actual_md5 : str
    exit_code_match : bool
    message : str

    Returns
    -------
    dict
    """
    return {
        "name": name,
        "status": status,
        "expected_md5": expected_md5,
        "actual_md5": actual_md5,
        "exit_code_match": exit_code_match,
        "message": message,
    }


# ---------------------------------------------------------------------------
# Core functions -- complete the TODOs
# ---------------------------------------------------------------------------

def load_config(path):
    """Load and parse a TOML config file.

    Parameters
    ----------
    path : str
        Path to the .toml file.

    Returns
    -------
    dict
        Parsed TOML as a Python dict.

    Raises
    ------
    RuntimeError
        If tomllib is not available.
    FileNotFoundError
        If the file does not exist.
    """
    # TODO:
    # 1. If tomllib is None, raise RuntimeError("TOML library not available").
    # 2. Open the file in binary mode ("rb").
    # 3. Parse with tomllib.load().
    # 4. Return the result.
    pass


def parse_config(config):
    """Extract the project name and test list from a parsed config.

    Parameters
    ----------
    config : dict
        Parsed TOML config.

    Returns
    -------
    tuple of (str, list of dict)
        (project_name, tests)
        Each test dict has: name, binary, args, input_file,
        expected_stdout_md5, expected_exit_code.
    """
    # TODO:
    # 1. Get project name from config["project"]["name"].
    # 2. Get tests list from config["tests"].
    # 3. For each test, fill in defaults for missing keys:
    #    - args: default to []
    #    - input_file: default to ""
    #    - expected_stdout_md5: default to ""
    #    - expected_exit_code: default to 0
    # 4. Return (project_name, tests).
    pass


def compute_md5(data):
    """Compute the MD5 hex digest of bytes data.

    Parameters
    ----------
    data : bytes

    Returns
    -------
    str
        32-character hex digest string.
    """
    # TODO: use hashlib.md5(data).hexdigest()
    pass


def run_test_binary(binary, args, input_file="", timeout=30):
    """Run a binary with arguments and optional input file.

    Parameters
    ----------
    binary : str
        Path to the binary or command name.
    args : list of str
        Command-line arguments.
    input_file : str
        Path to a file whose contents are fed to stdin.
        If empty string, no stdin input.
    timeout : int
        Maximum seconds to wait.

    Returns
    -------
    tuple of (bytes, int)
        (stdout_data, exit_code)
        If the process times out, return (b"", -1).

    Use subprocess.run with capture_output=True.
    """
    # TODO:
    # 1. Build the command list: [binary] + args.
    # 2. If input_file is a non-empty string, read its contents as bytes
    #    and pass to subprocess via input= parameter.
    # 3. Run subprocess.run with capture_output=True, timeout=timeout.
    # 4. Return (result.stdout, result.returncode).
    # 5. Catch subprocess.TimeoutExpired -> return (b"", -1).
    # 6. Catch FileNotFoundError -> return (b"", -1).
    pass


def run_single_test(test):
    """Run a single test and return a result dict.

    Parameters
    ----------
    test : dict
        A test spec from parse_config.

    Returns
    -------
    dict
        A result dict from make_result.
    """
    # TODO:
    # 1. Call run_test_binary(test["binary"], test["args"],
    #                         test["input_file"]).
    # 2. If exit_code is -1, return an "error" result.
    # 3. Compute the MD5 of stdout_data.
    # 4. Check if MD5 matches expected_stdout_md5.
    # 5. Check if exit_code matches expected_exit_code.
    # 6. If both match, return a "pass" result.
    #    Otherwise return a "fail" result with a descriptive message.
    pass


def run_all_tests(config_path):
    """Run all tests defined in a TOML config file.

    Parameters
    ----------
    config_path : str
        Path to the .toml config file.

    Returns
    -------
    dict with keys:
        "project_name" : str
        "results"      : list of result dicts
        "passed"       : int
        "failed"       : int
        "errors"       : int
    """
    # TODO:
    # 1. Load and parse the config.
    # 2. Run each test with run_single_test.
    # 3. Count passes, failures, errors.
    # 4. Return the summary dict.
    pass


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def format_report(summary):
    """Format a test summary as a human-readable report string.

    Parameters
    ----------
    summary : dict
        From run_all_tests.

    Returns
    -------
    str
    """
    lines = []
    lines.append(f"=== Regression Test Results: {summary['project_name']} ===")
    lines.append("")

    for r in summary["results"]:
        tag = r["status"].upper()
        lines.append(f"[{tag}] {r['name']}")
        if r["actual_md5"]:
            if r["status"] == "pass":
                lines.append(f"  MD5: {r['actual_md5']} (match)")
            else:
                lines.append(f"  MD5: {r['actual_md5']} "
                             f"(expected: {r['expected_md5']})")
        if r["message"]:
            lines.append(f"  {r['message']}")
        lines.append("")

    lines.append(f"Results: {summary['passed']} passed, "
                 f"{summary['failed']} failed, "
                 f"{summary['errors']} errors")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python regression_runner.py <config.toml>")
        sys.exit(1)

    summary = run_all_tests(sys.argv[1])
    print(format_report(summary))
    sys.exit(0 if summary["failed"] == 0 and summary["errors"] == 0 else 1)
