# Lab 67: Triage Tool

## Objective

Turn a directory of failing reproducers into a ranked work list.

## Background

Module 39 section 6. A good fuzzing run produces more failures than you can
fix, most of which are the same bug wearing different hats.

- **Deduplicate by cause, not symptom.** Two crashes at the same address are
  one bug. The cheapest fingerprint is the first differing function address
  plus the diverging instruction.
- **Rank by reachability, not severity.** A divergence in a function called
  every frame outranks a spectacular crash in an optional code path. Your
  existing execution traces already say which is which.
- **Separate "diverges" from "crashes."** A crash is loud and often shallow.
  A quiet arithmetic divergence corrupts a save file two hours later.

## Your Task

Implement in `triage.py`:

- `fingerprint(report)` -- the dedup key.
- `deduplicate(reports)` -- group by fingerprint.
- `rank(groups, trace_counts)` -- order by reachability.
- `triage(reports, trace_counts)` -- the whole pipeline.

## Why Reachability

Module 41's number: `wormsrevolution` lifted 88,816 functions and reaches
444. A bug in a function nothing calls is not worth your Tuesday.
