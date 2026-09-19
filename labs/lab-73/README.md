# Lab 73: Guest-Level Sampling Profiler

## Objective

Build a profiler that reports in guest functions, which a host profiler
cannot do.

## Background

Module 41 section 4. Generated code is thousands of near-identical
`sub_XXXXXXXX` functions, and a host profiler shows you host symbols. But
Module 30's spin watchdog already does the useful half:

> A built-in **spin watchdog** periodically samples the main thread's PC and
> resolves it to a guest function, so a silent hang becomes a named address
> to chase.

The same mechanism is a serviceable profiler. Sample periodically, resolve
to a *guest* function, and you get a profile in terms of the game's own
structure.

## Your Task

Implement in `gprof.py`:

- `resolve(addr, functions)` -- address to the function containing it.
- `Sampler` -- collects samples and counts them per function.
- `profile()` -- ranked results with percentages.
- `detect_spin(samples, threshold)` -- the watchdog: is one address
  dominating in a way that means we are stuck?

## Why Both

A profiler and a hang detector are the same instrument read two ways. If
90% of samples land on one address, that is either your hottest function or
your hang -- and the difference is whether the address is *advancing*.
