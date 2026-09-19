# Lab 88: Fold a Paging Instruction

## Objective

Make 162 instructions disappear at compile time, and prove you were allowed
to.

## Background

Module 53 section 4. The E0C6200 reaches its address space through `PSET`,
which latches a page that the *following* jump or call consumes. Normally a
recompiler's problem -- the target depends on runtime state.

Except the page is always an immediate. So:

> **`PSET` emits nothing at all** -- all 162 of them stop being control flow
> and become compile-time facts.

And the subtlety worth reading twice:

> Not even its one-instruction interrupt hold-off survives: that exists to
> keep an interrupt out of the gap between a `PSET` and the jump consuming
> the page it latched, and **generated code has no interrupt point there**.

You are allowed to drop it *provided* the assumption holds -- which is why
*"every reachable `PSET` in this ROM is immediately followed by a control
transfer, which the test suite asserts."*

## Your Task

Implement in `paging.py`:

- `resolve_targets(program)` -- fold each `PSET` into the transfer after it.
- `check_pset_invariant(program)` -- is every `PSET` followed by a transfer?
- `emit(program)` -- generate code, emitting nothing for `PSET`.
- `folding_report(program)`.

## The Rule

**An assumption that enables an optimisation must be asserted, not
remembered.** `check_pset_invariant` is not optional politeness; it is what
makes the fold sound.
