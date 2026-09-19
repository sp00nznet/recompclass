# Lab 121: Harness Validation

## Objective

Prove your measurement works before you trust what it measures.

## Background

Module 62 section 5: **expect your harness to be the bug.** `tamarecomp`'s
validation hit two before the real one, each looking exactly like a CPU bug.

And Module 35 section 1's rule, from a real defect in this repository: a CI
job that ran `python test_lab.py` passed for months and tested nothing.

> **A CI step that cannot fail is worse than no CI step**, because it
> converts "untested" into "tested" in every reader's head, including yours.

So: before believing a clean run, **inject a bug you understand and confirm
the harness goes red.**

## Your Task

Implement in `harnessval.py`:

- `Mutation` -- a named, reversible defect.
- `validate_harness(harness, subject, mutations)` -- inject each, check.
- `report(results)` -- which mutations were caught, which escaped.

## The Finding

A mutation the harness does **not** catch is the result. It tells you
precisely which class of bug your measurement is blind to -- and Module 62
section 6 says a negative result is a result.
