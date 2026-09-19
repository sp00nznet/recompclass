# Lab 69: Audio Clock Discipline

## Objective

Fix the drift problem from Module 40 section 5 with a feedback loop rather
than a better conversion.

## Background

The guest produces samples at its rate. Your host consumes them at its rate.
These are never the same number, and the difference is not constant.

Naive resampling gets the pitch right and still fails, because **the error
accumulates**. Too slow and the buffer underruns, which clicks. Too fast and
it overruns, which drops audio. Either way it happens once every few minutes
-- exactly long enough to be hard to reproduce.

The fix is a feedback loop: **measure the buffer fill and adjust the
consumption rate slightly** to hold it near a target. This is a clock
discipline loop, and it is the standard answer in every emulator that sounds
good.

## Your Task

Implement in `audioclock.py`:

- `Buffer` -- a ring buffer that reports underruns and overruns.
- `ClockDiscipline` -- proportional correction toward a target fill.
- `simulate(...)` -- run a producer/consumer mismatch over many frames.

## What to Measure

Run your loop against a fixed-ratio resampler over ten simulated minutes and
compare the fill level. The fixed ratio drifts monotonically to an underrun.
Yours should oscillate around the target and never hit either end.

Aim to **know** your latency rather than minimise it blindly: a stable 40ms
beats an unstable 15ms.
