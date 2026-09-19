# Lab 119: Verified Lifting Rules

## Objective

Do what Module 61 section 3 says nobody has done properly: **prove** a
lifting rule rather than sampling it.

## Background

> A differential test over a million instructions found a real bug in
> `tamarecomp` at instruction 1,486. It cannot tell you there is not another
> at ten million.

For *instruction lifting rules* the input space is often small enough to
enumerate outright. An 8-bit two-operand ALU op has 65,536 inputs, times a
few flag states. That is not a sampling problem; it is a loop.

> the payoff is permanent: a verified rule never needs retesting.

## Your Task

Implement in `verifylift.py`:

- `exhaustive_verify(reference, candidate, width, arity)` -- every input.
- `sampled_verify(...)` -- the usual approach, for comparison.
- `compare_approaches(...)` -- what sampling missed.

## The Result to Report

Construct a rule that is wrong on a *single* input pair, and show that
sampling misses it while exhaustive verification finds it every time. That
contrast is the argument for the technique.
