# Lab 75: Lane Order and Permutes

## Objective

Get vector lane order right across an endianness boundary, and show what
getting it wrong looks like.

## Background

Module 42 section 4, last trap:

> **Lane order.** Big-endian guests (Xbox 360, PS3, N64) store vectors with
> lane 0 at the opposite end from a little-endian host. A permute constant
> lifted literally is mirrored. Get this wrong and geometry is scrambled in
> a way that looks like a renderer bug.

That last clause is why this deserves a lab. The symptom appears in the
renderer, so that is where people look.

## Your Task

Implement in `lanes.py`:

- `mirror_index(i, count)` -- the lane-order conversion.
- `permute(vec, control)` -- apply a permute control vector.
- `lift_permute_naive(control)` -- the wrong translation (copy it as-is).
- `lift_permute(control, count)` -- the correct one.
- `demonstrate_bug(vec, control)` -- run both and show the difference.

## What You Must Show

`demonstrate_bug` must return a case where naive and correct differ. A test
asserts it. Being able to *produce* the bug on demand is what makes it
findable later.
