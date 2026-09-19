# Lab 58: Variant Build

## Objective

Build the multi-target support from Module 36 section 4: two ROM revisions,
two manifests, one runtime -- plus a report of how the addresses moved.

## Background

The corpus does this repeatedly. `oracle-recompiled` builds *Oracle of Ages*
and *Oracle of Seasons* from one monorepo. `Rampage` carries *World Tour*
(3,736 functions) and *Universal Tour* (4,788) side by side.
`pokemon-crystal` is *"the second Generation II title attempted with this
toolchain (after pokemon-gold); same mapper, same recipe."*

Without a manifest this is a branch you will never merge.

The interesting part is the **address delta**. Two revisions of one game
share almost all their code, shifted. If you can compute the shift, you can
carry symbols, hints and mods from one revision to the other instead of
rediscovering them -- which is Module 47 section 3's problem, since a mod
records the revision it targets and breaks on any other.

## Your Task

Implement in `variant.py`:

- `load_variants(manifests)` -- several manifests sharing one runtime.
- `common_functions(a, b)` -- functions present in both, matched by name.
- `compute_deltas(a, b)` -- the address shift per matched function.
- `dominant_shift(deltas)` -- the most common shift, and how much of the
  binary it covers.
- `port_hints(hints, shift)` -- carry hints across using that shift.
- `format_delta_report(...)`.

## What the Numbers Mean

A single dominant shift covering most functions means one revision inserted
code near the start and everything after moved by a fixed amount -- hints
port mechanically. **Many small clusters means the revisions genuinely
diverge**, and porting anything is per-function work. Knowing which you have
before you start is the point of the lab.
