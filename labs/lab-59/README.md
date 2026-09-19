# Lab 59: Unit 9 Capstone: A Pipeline That Survives Being Broken

## Objective

Combine Labs 51-58 into one pipeline that takes a target from container to
built binary, caches correctly, is driven by a manifest, and gates on
something real.

## Your Task

**Build the pipeline.** Stages from extraction through to a compiled
artifact, with content-hash caching (Lab 51) and a provenance record.

**Drive it from a manifest** (Lab 57). Every decision in the file, nothing
in your shell history. Hints commented with where they came from.

**Make it batch** (Lab 52). Several targets, isolated, with categorised
failures and a machine-readable report.

**Add the checks.** Fallthrough detection (Lab 54) and a synthetic fixture
suite (Lab 55) in CI.

**Then break it on purpose** (Lab 56), at every stage, and confirm every
gate goes red.

## Deliverable

A repository where three commands take a clean checkout to a built artifact,
plus a report covering: what the cache saves on a warm run, the batch report
for your corpus with failures categorised, and the break-it table from Lab 56.

## What Good Looks Like

Someone else clones it, follows the README, and gets the same numbers you
did. Module 37's standard: a result you cannot re-derive is an impression.
