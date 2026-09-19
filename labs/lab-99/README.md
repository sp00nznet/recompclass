# Lab 99: Instrument a Hybrid

## Objective

Make an interception-based project able to say something true about itself.

## Background

Module 49 section 2. Interception is a good design, and it costs you your
usual evidence: with the interpreter fallback enabled, **a build with zero
registered functions plays the game flawlessly.**

> So the design owes you instrumentation. Count registered functions, count
> hook hits, count fallbacks, and publish all three.

`gbarecomp`'s `interception.c` already has `successful` and `failed`
counters. They just are not in the README.

## Your Task

Implement in `hybrid.py`:

- `Interceptor` -- a registry plus counters.
- `dispatch(addr)` -- native if registered, else fallback.
- `crossover()` -- the fraction of *executed instructions* that ran native.
- `honest_summary()` -- a claim that refuses to overstate.

## Instructions, Not Calls

`crossover` weights by instructions executed, not by call count. A native
function called once that runs 10,000 instructions matters more than a
one-instruction stub called 500 times, and a call-count metric would say
the opposite.
