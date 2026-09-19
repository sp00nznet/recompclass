# Lab 65: Instruction Fuzzer

## Objective

Build the cheapest thing in Module 39: an instruction fuzzer that needs no
game and no runtime, and finds wrong-width arithmetic and bad-flag bugs
before they ever reach a target.

## Background

Module 39 section 2: *"If you build one thing from this module, build this."*

1. Pick an instruction from your decode table.
2. Generate random operands and random starting register state.
3. Execute it in your interpreter and in your lifted code.
4. Compare all registers and flags.

And the detail that makes it work:

> **Weight the generator toward the edges.** Uniform random operands almost
> never produce `0x00`, `0xFF`, `0x7F`, `0x80`, or exact nibble boundaries
> -- which is where flag bugs live. Half your inputs should come from a
> table of interesting values.

## Your Task

Implement in `insnfuzz.py`:

- `interesting_values(width)` -- the boundary table.
- `gen_operand(rng, width, edge_bias)` -- biased generation.
- `fuzz_instruction(...)` -- run one instruction many times through both.
- `shrink_case(case, still_fails)` -- reduce a failing case to a minimal one.

## Determinism

Every run takes a seed and must reproduce exactly (Module 39 section 3). A
failing case you cannot replay is not a finding.
