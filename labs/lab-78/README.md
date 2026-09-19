# Lab 78: Prune and Trap

## Objective

Build the pruning from Module 44, made safe by trap stubs.

## Background

The number that drives the whole unit: `wormsrevolution` lifted **88,816**
functions and reaches **444**. Over 99% of what you compiled never runs.

Pruning it is the highest-leverage optimisation available -- and it is only
safe because of `lttp-recompiled`'s pattern: **7,331 stubs plus 833 trap
stubs** for unresolved targets, so the program links, runs, and tells you
*which* pruned function actually mattered.

That converts the risk from "the game crashes mysteriously in chapter four"
into "the program prints the address of the one function I should not have
removed."

## Your Task

Implement in `prune.py`:

- `reachable(entry, call_graph)` -- static reachability.
- `observed(trace)` -- what actually ran.
- `live_set(entry, call_graph, trace)` -- the conservative union.
- `plan(all_functions, live)` -- what to keep, what to trap.
- `TrapRegistry` -- records which trap fired.

## Why the Union

Static reachability misses anything reached only through an indirect call.
Traces miss anything the playthrough did not touch. Neither alone is safe;
their union plus trap stubs is.
