# Lab 95: Harvard Memory Model

## Objective

Implement a memory model that breaks the flat-space assumption baked into
most of this course.

## Background

Module 55 section 4. `vmurecomp`'s `docs/CPU.md` on the Sanyo LC8670:

> Two **disjoint** address spaces:
> - **ROM**, 64 KB, used for instruction fetch and by `LDC`.
> - **RAM**, 512 bytes, used for every operand and every peripheral.

Address `0x100` in ROM and address `0x100` in RAM are different locations.
**The instruction determines which space you are in**, not the address.

This breaks a single `mem[]` array, Module 43's "guest address plus a base
offset is a host address", and any analysis that follows a pointer without
knowing which space it points into.

## Your Task

Implement in `harvard.py`:

- `HarvardMemory` -- two independent spaces.
- `fetch(addr)` / `load(addr)` / `store(addr, value)` / `ldc(addr)`.
- `detect_conflation(memory)` -- the test that catches a flat model.

## The Test That Matters

`detect_conflation` writes distinguishable values to the same address in
both spaces and checks they stay distinct. A flat implementation fails it
immediately; a correct one cannot.
