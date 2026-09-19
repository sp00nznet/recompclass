# Lab 89: Independent Oracle

## Objective

Run a full-state comparison against an implementation you did not write,
and survive the false alarms.

## Background

Module 53 section 5. `tamarecomp` compares `pc, A, B, X, Y, SP, flags`
against BrickEmuPy's core on every instruction -- *"precisely because that
core was written by someone else, from the same Epson documentation, in
another language."*

It found `RST F, i` inverted 1,486 instructions in. **Completely silent.**

And two false alarms arrived first, each looking exactly like a CPU bug:

- Windows `stdout` is a **text stream** and expanded every `0x0A` in the
  binary trace into `0x0D 0x0A`. The giveaway was the value of `X`, with
  *"the culprit bytes sitting right there in it"* -- a register
  holding something its own width cannot explain.
- The reference advanced its oscillator inside every `clock()` while the
  runtime only moved time in `tama_step`, so one register read disagreed by
  a tick. Timers are now frozen on both sides: *"the test is about the CPU."*

## Your Task

Implement in `indoracle.py`:

- `REGISTER_WIDTHS` / `validate_state(state)` -- can this value even exist?
- `compare_step(a, b)` -- full-state diff with plausibility checking.
- `run_validation(...)` -- step both, classify the first disagreement.

## The Classification

A disagreement is one of: `target_bug`, `impossible_value` (a register
holding something its width cannot represent -- your harness is corrupting
data), or `timing` (only timing-derived fields differ). Getting this triage
right is the difference between a day and a week.
