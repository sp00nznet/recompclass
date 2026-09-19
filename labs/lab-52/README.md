# Lab 52: Batch Harness with Failure Categories

## Objective

Build the batch harness from Module 33 section 4: run a directory of targets
through a pipeline without supervision, and produce a machine-readable report
that separates failures by *kind*.

## Background

Single-target work cannot tell you whether your recompiler is robust. Corpus
runs can -- `gb-recompiled` reports 1,592 of 1,609 ROMs recompiling, and
`3dsnes` reports 340 of 375 games rendering, *"verified by an unattended run
of the whole corpus rather than by spot-checks."*

A harness needs four properties:

- **Isolation.** One target's crash must not stop the run.
- **A timeout.** Some inputs hang. Assume it.
- **Machine-readable output.** One row per target, diffable between runs.
- **Failure categories, not a pass/fail bit.** "extraction failed",
  "codegen failed", "compile failed", "linked but crashed" are four
  different engineering problems whose counts move independently.

That last one is the point of the lab. A single percentage hides the fact
that you fixed six compile failures and introduced three crashes.

## Your Task

Implement in `batch.py`:

- `run_target(target, stages, timeout)` -- run one target through the stages,
  catching exceptions and timeouts, returning a result dict with a category.
- `run_batch(targets, stages, timeout)` -- run all of them, isolated.
- `summarize(results)` -- counts per category.
- `format_report(summary)` and `to_json(results)`.

## Why This Matters

Module 39 calls corpus runs "fuzzing the toolkit". They find the mapper you
never implemented and the header variant you assumed away -- and they give
you a number that moves, which Module 37 says is the only kind worth
publishing.
