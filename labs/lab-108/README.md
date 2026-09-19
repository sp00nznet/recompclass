# Lab 108: Unit 13 Capstone: Move Along the Spectrum

## Objective

Take a project that is purely static or purely interception-based and move
it one step along Module 49's spectrum.

## Your Task

Pick one:

**Add trace-guided discovery** to a static project. Record a playthrough,
harvest entry points, and measure the change in discovered functions and
unresolved transfers. Compare against pointer-scan hinting -- Module 14's
`civrev` found 301 scan hints made things *worse* and 21 runtime-harvested
hints fixed it.

**Add an interpreter fallback** to a project that currently returns zero on
a miss, and measure how often it fires.

**Add a migration path** to an interception project: auto-registration
(Lab 112), the A/B lever (Lab 63), and the crossover metric (Lab 99).

## Report

The crossover metric before and after -- what fraction of executed
instructions run as native code -- plus what the change cost in complexity.

## The Honest Part

State your project's position on Module 49 section 6's table, and check
whether your README describes the architecture you actually have. The
corpus's clearest failure is not a bad design choice; it is a good design
choice described as something else.
