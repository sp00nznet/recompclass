# Lab 22: Ghidra Script - Function Exporter

## Objective

Write a Ghidra headless-compatible Python script that exports all
identified functions (name, address, size) to a JSON file. This is a
common first step in a recompilation pipeline: you need a machine-readable
inventory of every function the disassembler found.

## Background

Ghidra is a free reverse-engineering tool from the NSA that can analyze
binaries for many architectures. It exposes a Java/Python scripting API
that lets you automate tasks like extracting function lists, cross-references,
and decompiled output.

In a recomp workflow, you typically run Ghidra in headless mode:

```
analyzeHeadless /path/to/project MyProject \
    -import target.bin \
    -postScript export_functions.py \
    -scriptPath /path/to/scripts
```

Since not everyone has Ghidra installed, this lab provides a mock `ghidra`
module that simulates the relevant API. Your script should work against
both the mock and real Ghidra.

### Key Ghidra API Concepts

- `currentProgram` -- the program being analyzed
- `currentProgram.getFunctionManager()` -- manages all identified functions
- `func.getName()` -- function name (string)
- `func.getEntryPoint()` -- entry address (Address object)
- `func.getBody().getNumAddresses()` -- size in bytes

## Instructions

1. Open `export_functions.py` and review the provided skeleton.
2. Implement `get_all_functions()` -- iterate over the function manager
   and collect each function's name, address, and size.
3. Implement `export_to_json()` -- write the function list to a JSON file.
4. Run the tests (these use the mock module, no Ghidra needed):
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

The script produces a JSON file like:

```json
{
  "binary": "test_binary",
  "function_count": 3,
  "functions": [
    {"name": "main",  "address": "0x08000100", "size": 64},
    {"name": "init",  "address": "0x08000200", "size": 32},
    {"name": "loop",  "address": "0x08000300", "size": 128}
  ]
}
```
