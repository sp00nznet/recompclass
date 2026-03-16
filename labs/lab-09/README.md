# Lab 9: Dispatch Table Generator

## Objective

Generate C dispatch tables for handling indirect jumps in recompiled code.
This addresses the core problem from Module 7: when the original binary
performs an indirect jump (e.g., `JMP [table + reg*4]`), the recompiled code
needs a mechanism to route execution to the correct recompiled function.

## Background

Indirect jumps are one of the hardest problems in static recompilation. The
original binary might compute a jump target at runtime, but the recompiled code
has replaced machine code with C functions -- there is no machine code at the
original addresses anymore. We need a dispatch mechanism that maps original
addresses to recompiled function pointers.

### Three Common Strategies

1. **Switch/Case Dispatch**: A simple `switch` statement over known target
   addresses. Easy to understand, O(n) worst case with compiler optimizations.

2. **Binary Search Dispatch**: Manually coded binary search over a sorted
   array of known targets. O(log n) guaranteed.

3. **Hash Table Dispatch**: A hash map from original address to function pointer.
   O(1) average case, but requires a good hash function and collision handling.

## Tasks

1. Generate a switch/case dispatch function in C.
2. Generate a binary search dispatch function in C.
3. Generate a hash table dispatch function in C.
4. (TODO) Add performance comparison scaffolding.
5. (TODO) Add a fallback to an interpreter for unknown addresses.

## Files

- `dispatch_gen.py` — Dispatch table generator
- `dispatch.h` — C header defining the dispatch interface
- `test_lab.py` — Tests that generated C code is syntactically valid

## Running

```bash
python dispatch_gen.py
python test_lab.py
```

## Key Concepts

- Indirect jump resolution in static recompilation
- Trade-offs between dispatch strategies (code size, speed, complexity)
- Code generation from Python to C
- Function pointer tables
