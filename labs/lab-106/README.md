# Lab 106: Propose and Check

## Objective

Build the pipeline Module 52 argues is the only usable shape: a hypothesis
generator whose output is **mechanically checked**.

## Background

> An ML technique is usable in a recompilation pipeline exactly when its
> output is **mechanically checkable**. Where it is, the model is a
> productivity tool and the checker is the source of truth.

The generator can be anything -- a model, a heuristic, a pointer scan.
Module 14's `civrev` is the cautionary case: 301 pointer-scan proposals made
the build *worse*, 21 runtime-harvested ones fixed it. The difference was
not the generator; it was that one set had been checked against execution.

## Your Task

Implement in `proposecheck.py`:

- `check_alignment(proposal, alignment)`.
- `check_in_range(proposal, code_range)`.
- `check_not_mid_function(proposal, known)` -- the jump-table trap.
- `check_observed(proposal, trace)` -- the strongest check.
- `evaluate(proposals, ...)` -- accept, reject with reasons, and rank.

## The Check That Caught civrev

`check_not_mid_function` is the one that matters. A pointer scan cannot tell
a vtable slot from a switch-table entry, and switch-table entries point into
the *middle* of functions. Hinting those splits real functions in half.
