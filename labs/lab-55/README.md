# Lab 55: Synthetic Fixture Suite

## Objective

Build the fixture suite from Module 35: small, hand-assembled byte sequences
that exercise the hard cases, with golden assertions on the lifter's exact
output.

## Background

You cannot commit a game ROM (Module 45). You *can* commit a 64-byte blob of
hand-assembled instructions that exercises every addressing mode, and assert
on the exact C your lifter emits for it.

This is the highest-value test a recompiler can have. It is fast, legal,
fails loudly on any unintended semantic change, and doubles as documentation
of what your lifter is supposed to produce. `tirecomp` ships
`tests/test_decode.c`, `tests/test_rt.c` and `tests/test_tivar.c` for exactly
this.

**Build fixtures for the cases you know are hard**, not the easy ones:

- Flag-setting arithmetic at every width
- Delay slots, on every architecture that has them
- Width-sensitive instructions under each mode setting
- Mode interworking across a mode-switching branch
- Every control-flow class, so an indirect jump cannot silently become a
  plain branch

## Your Task

Implement in `fixtures.py`:

- `Fixture` -- a named byte sequence with expected output.
- `assemble(lines)` -- a tiny assembler so fixtures are readable.
- `run_fixture(fixture, lifter)` -- lift and compare against the golden text.
- `run_suite(fixtures, lifter)` -- run all, report failures with diffs.
- `regenerate(fixtures, lifter)` -- produce updated goldens.

## The Trap

Module 35 section 3: when output legitimately changes, the temptation is to
regenerate goldens without reading the diff. **Make regeneration explicit and
reviewable** -- a separate command, output committed as a normal change, and
the diff read in review. A golden test you rubber-stamp is the CI equivalent
of a job that cannot fail.
