# Lab 51: Pipeline Driver with Content-Hash Caching

## Objective

Build the pipeline driver from Module 33: a sequence of stages, each taking
files and producing files, with a content-hash cache so unchanged stages are
skipped.

## Background

A recompilation pipeline is a chain of file transformations:

```
container --> image --> function set --> disassembly --> lifted C --> binary
```

Treating each stage as a pure function over files buys three things:
caching (unchanged inputs mean no rerun), inspection (every intermediate is
a file you can diff), and bisection (rerun one stage in isolation).

The cache key for a stage is the hash of its inputs **plus the version of
the tool that produced them**. Leaving the tool version out is the classic
mistake: you change the lifter, the inputs are identical, and the cache
serves you yesterday's output.

## Your Task

Implement in `pipeline.py`:

- `hash_file(path)` -- SHA-256 of a file's contents, as hex.
- `stage_key(stage, inputs)` -- a cache key combining the stage name, its
  tool version, and the hashes of every input file.
- `Pipeline.run(...)` -- execute stages in order, skipping any whose key is
  already in the cache, and record what ran versus what was skipped.
- `Pipeline.provenance()` -- a record of inputs, tool versions and outputs
  for the last run (Module 33 section 6).

## Why This Matters

Module 37's standard is that a number you cannot re-derive is an impression.
A pipeline you cannot re-run from scratch cannot produce re-derivable
numbers, so this is the foundation everything in Semester 3 sits on.
