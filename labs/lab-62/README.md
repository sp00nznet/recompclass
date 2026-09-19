# Lab 62: Interpreter Oracle

## Objective

Build the differential harness from Module 38: two implementations, one
input, and a report of exactly where and how they first disagree.

## Background

Module 38 section 1: *"You cannot differentially test without a reference,
and the reference you want is the original binary running -- not your beliefs
about it."*

And Module 53's project got this as right as it can be got: `difftest.py`
runs BrickEmuPy's E0C6200 core beside the recompiled output and compares
`pc, A, B, X, Y, SP, flags` **on every instruction** -- *"precisely because
that core was written by someone else, from the same Epson documentation, in
another language."*

It found a real bug 1,486 instructions in: `RST F, i` was inverted.
Completely silent -- the ROM ran, the screen drew, the device animated.

## Your Task

Implement in `oracle.py`:

- `State` -- a comparable register snapshot.
- `diff_states(a, b)` -- which fields differ.
- `run_differential(program, impl_a, impl_b, limit)` -- step both, stop at
  the first divergence.
- `format_divergence(result)` -- a report naming the step, the instruction,
  and every differing field.

## The Limitation to State

If your lifter and your interpreter share a decode table, this tests your
*lifting*, not your *decoding* -- a decode bug affects both identically and
is invisible. Say so when you report results. Module 38 section 2 grades
oracle strength, and "my own implementation sharing the decode table" is the
weak end.
