# Lab 46: Capstone Multi-Arch Analyzer

## Objective

Build a tool that auto-detects the CPU architecture of a binary blob by
trying multiple Capstone disassembly configurations and picking the one
that produces the most valid decoded instructions. This is useful when
you have an unknown binary and need to figure out what architecture it
targets.

By the end of this lab you will be able to:

- Use Capstone to disassemble binary data for multiple architectures
- Implement a heuristic scoring system for disassembly quality
- Auto-detect architecture from raw binary blobs

## Background

When doing recompilation work, you sometimes encounter binary blobs
without metadata -- ROMs stripped of headers, code segments extracted
from save states, or embedded processor firmware. Identifying the
architecture is the first step.

The approach is brute-force: try disassembling the blob as each candidate
architecture and see which one produces the most sensible output. The
heuristic used here is simple: **whichever architecture decodes the
highest percentage of bytes into valid instructions wins**.

### Candidate Architectures

| Architecture | Capstone Constant         | Mode                     |
|-------------|---------------------------|--------------------------|
| x86 (32)    | `CS_ARCH_X86`            | `CS_MODE_32`             |
| x86 (64)    | `CS_ARCH_X86`            | `CS_MODE_64`             |
| ARM (32)    | `CS_ARCH_ARM`            | `CS_MODE_ARM`            |
| ARM Thumb   | `CS_ARCH_ARM`            | `CS_MODE_THUMB`          |
| ARM64       | `CS_ARCH_ARM64`          | `CS_MODE_ARM` (default)  |
| MIPS (32 BE)| `CS_ARCH_MIPS`           | `CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN` |
| MIPS (32 LE)| `CS_ARCH_MIPS`           | `CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN` |
| PPC (32 BE) | `CS_ARCH_PPC`            | `CS_MODE_32 + CS_MODE_BIG_ENDIAN` |

### Scoring Heuristic

For each architecture, compute:

```
score = decoded_bytes / total_bytes
```

Where `decoded_bytes` is the sum of the sizes of all successfully
decoded instructions.  A score of 1.0 means every byte was part of a
valid instruction.

If there is a tie, prefer the architecture with the most decoded
instructions (not bytes).

**Note:** This lab requires the `capstone` Python package. If not
installed, the tests will skip gracefully and you can still test the
scoring logic with mock data.

## Files

| File                     | Description                        |
|--------------------------|------------------------------------|
| `multi_arch_analyzer.py` | Architecture detector (starter)   |
| `test_lab.py`             | Pytest test suite                 |

## Instructions

1. Install Capstone if you have not already:
   ```
   pip install capstone
   ```
2. Open `multi_arch_analyzer.py` and complete the `TODO` sections.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## References

- Capstone disassembly framework (capstone-engine.org)
- Capstone Python bindings documentation
