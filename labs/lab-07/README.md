# Lab 7: M/X Flag Tracker (65816)

## Objective

Implement a state machine that tracks the 65816 processor's M and X flag changes
to determine register widths (8-bit vs 16-bit) at each instruction.

## Background

The WDC 65816 processor has two key status flags that affect register widths:

- **M flag (bit 5)**: Controls accumulator width. When set, the accumulator is 8-bit; when clear, 16-bit.
- **X flag (bit 4)**: Controls index register width. When set, X/Y are 8-bit; when clear, 16-bit.

These flags are modified by two instructions:

- **SEP #imm** (Set Processor Status): Sets the bits indicated by the immediate value.
- **REP #imm** (Reset Processor Status): Clears the bits indicated by the immediate value.

For static recompilation, knowing the register width at every instruction is critical
because it determines how much data each instruction operates on. Getting this wrong
produces incorrect recompiled code.

## Tasks

1. Parse a sequence of 65816 instructions from text input.
2. Track SEP and REP instructions that modify M (bit 5 = 0x20) and X (bit 4 = 0x10).
3. Report the register width for accumulator and index registers at each instruction.
4. (TODO) Handle branching where flag state may differ along different paths.
5. (TODO) Handle merging states at join points (e.g., widen to "unknown" if paths disagree).

## Files

- `flag_tracker.py` — Main implementation
- `test_lab.py` — Test cases with known flag sequences

## Running

```bash
python flag_tracker.py
python test_lab.py
```

## Key Concepts

- Static analysis of processor state
- Abstract interpretation (flag states can be Known or Unknown)
- Forward dataflow analysis
- The challenge of variable-width ISAs in static recompilation
