# Lab 61: Attribution Harness

## Objective

Instrument a recompiled project so every frame reports how many draws came
from guest code versus harness code, and how many dispatches hit the
fallback.

## Background

Module 37's characteristic failure: your harness produces your evidence. A
green orb at 60fps drawn by 2,204 return-zero stubs. A menu drawn from
hardcoded strings. A game that plays perfectly because an emulator is
underneath it.

`xboxdashboard`'s corrected README is the standard to aim at:

> ...the stream contains **0 draws**, so no geometry has been submitted yet,
> and **nothing in this repo has ever put a pixel on screen that the
> dashboard did not ask for.**

You cannot say that without counting. This lab builds the counter.

## Your Task

Implement in `attribution.py`:

- `Attribution` -- records events tagged `guest` or `harness`.
- `record_draw`, `record_dispatch` -- the two things worth attributing.
- `frame_summary()` -- per-frame counts, reset each frame.
- `session_summary()` -- totals, plus the ratio that matters.
- `honest_claim()` -- a sentence you could put in a README, which refuses to
  overstate.

## The Part That Matters

`honest_claim()` must return something *weaker* when the evidence is weak.
If every draw came from the harness, it has to say so. A reporting function
that always sounds good is the thing this whole unit exists to prevent.
