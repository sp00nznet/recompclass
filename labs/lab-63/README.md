# Lab 63: Bisect Harness

## Objective

Build the single most transferable technique in this course: `git bisect`,
applied to the address space.

## Background

From `encarta`'s commit log:

```
Add LIFT_LO/LIFT_HI: bisect the lifted set to find a bad lift
```

A range filter. Functions inside `[LIFT_LO, LIFT_HI]` run lifted; everything
else runs as the original. Then binary search the range. Roughly a dozen runs
isolates one bad function out of thousands, and **each run requires no
thought** -- only "did the symptom happen?"

The prerequisite, from Module 38 section 4: both implementations must be
simultaneously available and switchable **at runtime**. If switching needs a
30-minute rebuild you will not do it, and you will read generated assembly
instead.

## Your Task

Implement in `bisect_lift.py`:

- `in_range(addr, lo, hi)` -- the filter itself.
- `run_with_range(addrs, lo, hi, oracle_fn, lifted_fn)` -- run a program
  with that range lifted.
- `bisect(addrs, test)` -- binary search for the lowest address whose
  inclusion makes `test` fail.
- `bisect_log(addrs, test)` -- the same, returning every range tried.

`test(lo, hi)` returns True when the symptom is **absent** (the run is good).

## Why the Log Matters

Module 62 section 8: a result you cannot re-derive is an impression.
`bisect_log` is what turns "we found the bad function" into a record someone
else can check -- and it tells you immediately if your test is
non-deterministic, because the search will not converge.
