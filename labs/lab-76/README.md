# Lab 76: Memory Access Ladder

## Objective

Implement Module 43's ladder and measure what each rung costs.

## Background

| Rung | What it is |
|---|---|
| 0 | a function with a chain of range comparisons |
| 1 | a flat array plus a base offset -- `burnout3`'s `FMEM32` |
| 2 | the guest's own addresses via the host MMU |

Rung 1 is the one to feel:

```c
#define FMEM32(addr) (*(volatile uint32_t *)((uintptr_t)(addr) + g_xbox_mem_offset))
```

A guest address plus a constant *is* a host address. No call, no branch.

The catch is section 2: when reads are raw arithmetic, a read of a hardware
register no longer calls you -- and the whole point of a hardware register
is that reading it *does something*.

## Your Task

Implement in `memladder.py`:

- `SwitchBus` -- rung 0.
- `FlatBus` -- rung 1, with an explicit I/O window check.
- `classify_static(addr, io_range)` -- the lift-time split.
- `benchmark(bus, accesses)` -- count the work each rung does.

## What to Report

Rung 1 must be faster *and* must still call the I/O handler for
memory-mapped addresses. A rung 1 that loses I/O is not a faster rung 1, it
is a broken program.
