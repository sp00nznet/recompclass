# Lab 87: Whole-ROM Emitter

## Objective

Build Module 53's codegen strategy: not one C function per guest function,
but **one C function, thousands of labels**.

## Background

From `tamarecomp`'s header:

> The recompiled ROM is one C function with a label per instruction word, so
> this holds only the architectural state -- there is no instruction pointer
> to maintain except at a computed transfer.

The emitter reports `47567 lines from 6144 ROM words`, and:

- **Sequential instructions fall through with no branch at all.**
- **Direct jumps are `goto`.**
- Function boundaries -- Module 34's recurring nightmare -- are never needed,
  because you never emit a function.

This works when the whole address space fits in one C function your compiler
will accept. Right for small embedded targets and arcade boards; wrong for
anything Module 34 sized.

## Your Task

Implement in `wholerom.py`:

- `emit_label(addr)` / `emit_instruction(...)`.
- `emit_rom(program)` -- the whole function.
- `count_gotos(source)` -- how many transfers survived as branches.
- `reachable_labels(program)` -- which labels anything targets.

## What to Notice

Most labels are never targeted. Emitting them all is wasteful but harmless,
and `reachable_labels` tells you how many you could drop -- which is the
same liveness question as Module 44, at instruction granularity.
