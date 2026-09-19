# Lab 104: Matching Decomp as Oracle

## Objective

Use a matching decompilation as the specification, and report how much of
your output it actually covers.

## Background

Module 51 section 5. A fully matching decompilation compiles to a
byte-identical binary, so **the decomp's C *is* the specification.** Your
recompiled output should behave identically, and you can compare at function
granularity with known-correct expected behaviour.

If your target is one of the N64 or GameCube games with a matching decomp --
Super Mario 64, Ocarina of Time, Wind Waker, Metroid Prime, Melee -- Module
38's oracle problem is already solved, and you should build the harness
before writing a lifter.

## Your Task

Implement in `decomporacle.py`:

- `compare_function(name, cases, decomp_fn, recomp_fn)` -- one function.
- `run_suite(...)` -- all of them.
- `coverage(suite_result, all_functions)` -- how much is actually tested.
- `honest_report(...)`.

## The Coverage Number Is the Point

A suite that tests 40 of 4,000 functions and passes is not evidence the
build is correct. `coverage` makes that visible, and `honest_report` refuses
to describe a low-coverage pass as validation.
