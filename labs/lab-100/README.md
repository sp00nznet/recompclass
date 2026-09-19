# Lab 100: Migration Ladder

## Objective

Build the migration path from Module 49 section 7, and measure it.

## Background

> A sane progression:
>
> 1. **Interception**, with the emulator doing everything. Playable, zero
>    native code.
> 2. **Move functions across**, hottest or most-interesting first. Still
>    playable throughout.
> 3. **Measure the crossover** -- the fraction of execution that is native.
>    This is your real progress metric.
> 4. **Flip the default** once the native path is complete enough.
> 5. **Drop the emulator**, if you ever fully resolve discovery.
>
> Each stage is shippable.

## Your Task

Implement in `migration.py`:

- `plan_migration(profile)` -- what order to port functions in.
- `simulate_migration(profile, order)` -- crossover after each step.
- `steps_to_reach(curve, target)` -- how many ports to hit a threshold.
- `verify_runnable(...)` -- the invariant: every step still runs.

## The Invariant

`verify_runnable` asserts that at every point in the migration, every
function is either ported *or* available in the emulator. That is what makes
each stage shippable, and it is the property an all-or-nothing bring-up
lacks.
