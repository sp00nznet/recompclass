# Lab 79: Function Ordering

## Objective

Turn an execution trace into a function layout, and measure what it buys.

## Background

Module 44 section 4. Cheaper than PGO and most of the benefit for the cache
problem: given functions ranked by call count, the linker lays them out
contiguously, so hot functions share pages and cache lines instead of being
scattered through a multi-hundred-megabyte binary.

And the reuse argument: the trace that feeds this also feeds entry point
discovery (Module 33), the oracle (Module 38), and liveness (Module 44
section 1). **One recorded playthrough feeds four different things.**

## Your Task

Implement in `ordering.py`:

- `call_counts(trace)` -- how often each function ran.
- `order_by_heat(counts, all_functions)` -- the ordering file.
- `layout(order, sizes)` -- assign addresses in that order.
- `estimate_cache_misses(trace, layout, line_size)` -- a simple model.
- `compare_layouts(...)` -- original versus reordered.

## The Model

The cache model is deliberately crude: count distinct cache lines touched
by the trace. It is not accurate in absolute terms and it does not need to
be -- you are comparing two layouts over the same trace, and the crude model
ranks them correctly.
