# Lab 48: Register Trace Logger

## Objective

Implement a C library that logs CPU register state at function entry and
exit points. This is a key debugging tool for recompilation -- by
comparing register traces between the original emulated game and the
recompiled version, you can pinpoint exactly where behavior diverges.

By the end of this lab you will be able to:

- Define a register state struct for a target architecture
- Implement macro-based function instrumentation
- Write trace output in CSV format for automated comparison
- Build a reusable tracing library

## Background

When debugging a recompiled game, you often need to answer: "at which
function does behavior diverge from the original?" The register trace
logger instruments function entry/exit to capture register state, then
writes a CSV log that can be diff'd against a reference trace from an
emulator.

### Instrumentation Macros

```c
void my_function(CpuRegs *regs) {
    TRACE_ENTRY("my_function", regs);
    // ... function body ...
    TRACE_EXIT("my_function", regs);
}
```

### CSV Output Format

```
timestamp,function,direction,r0,r1,r2,r3,r4,r5,r6,r7,sp,lr,pc
0,func_a,entry,0x00000000,0x00000001,...
1,func_a,exit,0x00000005,0x00000001,...
```

### Register Set (simplified ARM-like)

For this lab, we use a simplified register set with 8 general-purpose
registers (r0-r7), stack pointer (sp), link register (lr), and program
counter (pc).

## Files

| File             | Description                          |
|------------------|--------------------------------------|
| `trace_logger.h` | API declarations and macros         |
| `trace_logger.c` | Implementation (starter code)       |
| `test_trace.c`   | Test suite                           |
| `Makefile`        | Build and test targets              |

## Instructions

1. Read `trace_logger.h` to understand the structures and macros.
2. Complete the `TODO` sections in `trace_logger.c`.
3. Build and test:
   ```bash
   make
   make test
   ```

## Expected Output

```
Register Trace Logger -- Test Suite

--- test_trace_entry ---
--- test_trace_exit ---
--- test_csv_output ---
--- test_multiple_functions ---
--- test_buffer_capacity ---

5 / 5 tests passed.
```

## References

- ARM Architecture Reference Manual (register naming)
- Recompilation debugging practices
