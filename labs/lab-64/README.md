# Lab 64: Boundary Tripwires

## Objective

Build the tripwires from Module 38 section 5, so a lifted function that
corrupts state is caught at the call that did it rather than three minutes
later somewhere unrelated.

## Background

From `encarta`'s log:

```
Add R2L_HEAPCHECK diagnostic (HeapValidate after each real->lifted call)
```

Validate the heap after *every* call from original code into lifted code.
The bugs this catches are the ones Module 38's taxonomy is full of:

| Bug | Tripwire that catches it |
|---|---|
| `KERNEL.197 was skewing the caller's stack` | stack pointer restored |
| ABI mismatch at the boundary | callee-saved registers preserved |
| `the decode thunk writes pixels over its own plane table` | guard bytes |
| heap corruption from a bad write | heap validation |

These are expensive and that is fine -- they run under a debug flag, all the
time, until the project stabilises.

## Your Task

Implement in `tripwire.py`:

- `check_stack(before, after)` -- stack pointer restored?
- `check_callee_saved(before, after, saved_regs)` -- ABI honoured?
- `check_guards(memory, guards)` -- guard bytes intact?
- `guarded_call(fn, ctx, checks)` -- run a call with every check, and report
  which fired.

## The Design Rule

A tripwire must name **which** invariant broke and **at which call**. A
check that reports "something is wrong" has moved the problem, not solved
it -- and Module 46 section 4 makes the same point about user-facing errors.
