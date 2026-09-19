# Lab 94: Classify the Unknowns

## Objective

Turn an undifferentiated pile of unresolved transfers into a small number of
tractable problems.

## Background

Module 55 section 3. After assembling the address space, `cybikorecomp` had
227 genuinely indirect transfers. Backward-scanning each site's basic block
for the last write to the register it calls through gave:

| defining instruction | sites | what it is |
|---|---|---|
| `mov.l @(d:16,ERm), ERn` | 178 | a field of a struct -- **C++ virtual dispatch** |
| `mov.l @aa:16, ERn` | 43 | a fixed address in on-chip RAM |
| `mov.l @ERm, ERn` | 3 | a pointer |
| `mov.l @aa:24, ERn` | 1 | `0x200004` |
| nothing in the block | 2 | argument, or set further back |

> **Three different problems, not 227.**

## Your Task

Implement in `classify.py`:

- `find_definition(block, site_index, register)` -- the backward scan.
- `classify_site(block, site_index)` -- the mechanism.
- `classify_all(sites)` -- grouped counts.
- `report(groups)` -- sorted, with the interpretation attached.

## Why Grouping Beats Solving

227 unknowns is unactionable. Three mechanisms are three pieces of work you
can estimate separately -- and vtable dispatch, a fixed dispatch table and
genuine pointers each need a different approach.
