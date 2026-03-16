# Lab 31: Trace Comparator

## Objective

Write a tool that compares two execution traces (CSV files containing
address and register state at each step) and finds the first point of
divergence. This is the primary debugging technique for recompilation --
you run the original in an emulator, run the recompiled version, and diff
their traces.

## Background

An execution trace logs the CPU state after every instruction. A typical
trace CSV looks like:

```csv
address,a,b,c,d,sp,flags
0x0100,0x00,0x00,0x00,0x00,0xFFFE,0x00
0x0101,0x42,0x00,0x00,0x00,0xFFFE,0x00
0x0103,0x42,0x00,0x00,0x00,0xFFFE,0x80
```

When two traces diverge, the first mismatch tells you exactly which
instruction your lifter got wrong. Maybe it is a flag computation error,
a wrong operand, or a missed memory write.

### What "Divergence" Means

Two trace lines diverge if any register value differs. The address
itself might also differ (e.g., a branch went the wrong way).

## Instructions

1. Open `trace_compare.py` and implement the TODO functions.
2. `load_trace()` -- parse a CSV trace file into a list of dicts.
3. `compare_traces()` -- walk two traces in parallel and find the first
   divergence.
4. `format_divergence()` -- produce a human-readable report of the
   mismatch.
5. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
Comparing trace_a.csv vs trace_b.csv...
Traces match for 5 steps.
DIVERGENCE at step 6 (line 7):
  Expected: address=0x0108, a=0x42, b=0x00, flags=0x80
  Got:      address=0x0108, a=0x43, b=0x00, flags=0x00
  Differs:  a (0x42 vs 0x43), flags (0x80 vs 0x00)
```
