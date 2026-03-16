# Lab 50: Project Regression Harness

## Objective

Build a regression test runner for recompilation projects. When you change
the recompiler, you need to verify that previously-working games still
produce correct output. This lab implements a runner that reads a TOML
config, executes binaries with recorded input, and compares output
checksums against expected values.

By the end of this lab you will be able to:

- Parse TOML configuration files for test specifications
- Run binaries with simulated input via subprocess
- Compute checksums of program output
- Report pass/fail results with diagnostic diffs

## Background

Regression testing in recompilation projects follows a pattern:

1. **Record** a known-good run: capture the binary's output (stdout,
   files, framebuffer dumps) and compute checksums.
2. **Store** the expected checksums in a config file alongside the
   input recording.
3. **Replay** on each new build: run the binary with the same input,
   compute checksums of the output, and compare.

### TOML Config Format

```toml
[project]
name = "MyRecomp"

[[tests]]
name = "boot_sequence"
binary = "./recomp_game"
args = ["--headless", "--frames", "60"]
input_file = "inputs/boot.bin"
expected_stdout_md5 = "d41d8cd98f00b204e9800998ecf8427e"
expected_exit_code = 0

[[tests]]
name = "menu_navigation"
binary = "./recomp_game"
args = ["--headless", "--frames", "120"]
input_file = "inputs/menu.bin"
expected_stdout_md5 = "098f6bcd4621d373cade4e832627b4f6"
expected_exit_code = 0
```

### Test Result Format

Each test produces a result with:
- `name`: test name
- `status`: "pass", "fail", or "error"
- `expected_md5`: expected checksum
- `actual_md5`: actual checksum
- `exit_code_match`: bool
- `message`: human-readable explanation

## Files

| File                   | Description                          |
|------------------------|--------------------------------------|
| `regression_runner.py` | Test runner (starter code)          |
| `test_lab.py`           | Pytest test suite                   |
| `sample_config.toml`   | Example TOML configuration          |

## Instructions

1. Install the `tomli` package if on Python < 3.11 (Python 3.11+ has
   `tomllib` in the standard library):
   ```
   pip install tomli
   ```
2. Open `regression_runner.py` and complete the `TODO` sections.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
=== Regression Test Results: MyRecomp ===

[PASS] boot_sequence
  MD5: d41d8cd98f00b204e9800998ecf8427e (match)
  Exit code: 0 (expected 0)

[FAIL] menu_navigation
  MD5: abc123... (expected: 098f6b...)
  Exit code: 0 (expected 0)

Results: 1 passed, 1 failed, 0 errors
```

## References

- TOML specification (toml.io)
- Python subprocess module documentation
- hashlib documentation
