# Lab 16: N64Recomp Configuration

## Objective

Write a well-structured N64Recomp `.toml` configuration file and use a Python
script to analyze the recompiler's output. This lab teaches you how N64Recomp
is configured and what its generated C code looks like.

## Background

[N64Recomp](https://github.com/N64Recomp/N64Recomp) is a static recompiler
that converts N64 MIPS binaries into C code that can be compiled for modern
platforms. It is configured via a TOML file that specifies:

- **Input ROM**: The path to the N64 ROM file (big-endian .z64 format).
- **Output directory**: Where generated C files are written.
- **Function declarations**: An optional list of known function names and their
  VRAM addresses, typically loaded from a symbol file.
- **Function overrides**: Functions that should be replaced with custom
  implementations instead of being recompiled.
- **Stub functions**: Functions whose bodies should be replaced with empty
  stubs (useful for functions that interact with hardware not present on PC).
- **Patches**: Modifications applied to the ROM before recompilation, used
  to fix issues or inject new behavior.

## Files

| File                    | Description                                      |
|-------------------------|--------------------------------------------------|
| `example.recomp.toml`   | Well-commented example configuration             |
| `analyze_output.py`     | Script to examine N64Recomp-generated C files    |

## Tasks

1. Read through `example.recomp.toml` and understand each configuration
   section.
2. Study the `analyze_output.py` script and understand what it looks for in
   the generated C code.
3. If you have N64Recomp installed, try running it with the example config
   on a test ROM, then analyze the output.
4. (Stretch) Extend the analysis script to cross-reference generated functions
   with a symbol file.

## Running the Analysis Script

```bash
# Point the script at the output directory from N64Recomp.
python analyze_output.py path/to/recomp_output/
```

## Notes

- You do not need an actual N64 ROM to complete the configuration portion of
  this lab. The analysis script can also be studied on its own.
- N64Recomp's TOML format may evolve over time. Refer to the official
  repository for the latest schema.
