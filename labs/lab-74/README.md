# Lab 74: Vector Lifter With a Reference

## Objective

Lift vector instructions and prove them correct where it matters: NaN,
denormal, zero and saturation boundaries.

## Background

Module 42 section 4. The traps, in order of how much time they cost:

- **Reciprocal estimates.** The guest's `vrsqrte` has an architecturally
  defined low precision. `_mm_rsqrt_ps` has *a different* low precision.
- **Denormals.** Many consoles flush to zero in hardware. Your host may not.
- **NaN in min/max.** The guest and the host may disagree about which
  operand wins.
- **Saturation.** RSP and MMI integer SIMD saturate rather than wrapping.

All of these are exactly what a differential test catches and eyeballing
does not. Lab 39's project ships `sim_*` reference implementations alongside
its lifters for this reason.

## Your Task

Implement in `veclift.py`:

- `saturate(value, width, signed)` -- clamping, not wrapping.
- `vadd_sat(a, b, ...)` -- saturating elementwise add.
- `flush_denormals(vec, enabled)` -- model the guest's FTZ mode.
- `vmin(a, b, nan_wins)` -- min with an explicit NaN policy.
- `differential(op_a, op_b, cases)` -- compare two implementations.

## The Point

The lab is not the arithmetic. It is that **every one of these needs an
explicit policy**, and a lifter that does not state its NaN and denormal
behaviour has one anyway -- it just does not know what it is.
