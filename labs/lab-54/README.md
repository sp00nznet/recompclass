# Lab 54: Fallthrough Detector

## Objective

Detect incorrectly split functions statically, before running anything, and
emit an automated repair.

## Background

Module 34 catalogues this bug in four disguises across four architectures:

| Project | Fixes needed |
|---|---|
| racer | 143 |
| Rampage (World Tour) | 418 |
| pokemonsnap | ~390 |
| Rampage 2 | ~879 outstanding |

The cause, from pokemonsnap's README: *"The N64Recomp tool incorrectly
splits functions that lack standard prologues."* When discovery does not
recognise a prologue, it treats an internal branch target as a new function
-- so the first half runs off the end of its own body and falls through
into nothing.

The saving grace is that it is **statically detectable**. A function whose
last instruction is neither a return nor an unconditional branch is
suspicious on its face, and you can find every one of them without
executing a single instruction.

## Your Task

Given a function list (address, size, and decoded instructions), implement:

- `ends_with_terminator(func)` -- does this function end in a return or an
  unconditional branch?
- `find_fallthroughs(functions)` -- every function that does not.
- `propose_merges(functions)` -- for each fallthrough, if another function
  starts exactly where it ends, propose merging them.
- `apply_merges(functions, merges)` -- produce the repaired function list.

## Why This Matters

Module 34's advice is to automate the fix, because nobody hand-edits 418
functions twice. Rampage 2's honest note -- *"~879 potential 2-instruction
fallthrough functions need systematic fixing"* -- is the right way to hold
it: a counted, categorised debt rather than an unknown number of future
mystery crashes.
