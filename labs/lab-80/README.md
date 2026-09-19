# Lab 80: Unit 11 Capstone: Measured Optimisation

## Objective

Profile a recompiled title, optimise its ten hottest functions, and prove
behaviour did not change.

## Your Task

**Profile first** (Lab 72). Whole binary, real workload.

**Apply targeted optimisations** from Unit 11: memory access (Lab 76),
endianness (Lab 77), SIMD where the guest used vectors (Lab 74), pruning
(Lab 78), function ordering (Lab 79).

**Measure after each one**, separately. A combined "we made it 3x faster" is
not a result you can act on later.

**Prove correctness held.** Every technique in Unit 11 changes what code
exists or where it lives. Run your Unit 10 differential test after each step.

## Report

Before and after per optimisation, with a re-runnable measurement command.
Report the **99th percentile frame time**, not the mean -- for a game the
question is whether any frame missed its deadline.

## What Good Looks Like

An optimisation you tried that did **not** help, written up with why. Module
62 section 6: a negative result is a result, and this is the unit where
people quietly discard them.
