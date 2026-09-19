# Lab 107: Equivalence Gate

## Objective

Build the checker from Module 52 section 3 -- the piece that makes any
hypothesis generator usable.

## Background

```
binary --> generator --> candidate C --> compile --> differential test --> accept/reject
                                                          ^
                                                   this is the product
```

The checker is the contribution. Without it you have a plausible-text
generator pointed at something where plausibility is the failure mode.

## Your Task

Implement in `eqgate.py`:

- `Gate` -- holds the reference and the test cases.
- `submit(candidate)` -- accept or reject, with a reason.
- `stats()` -- acceptance rate and rejection reasons.

## What It Must Reject

A candidate that fails on any case. A candidate that raises. A candidate
that is *correct on the given cases but wrong on a boundary case the gate
adds itself* -- because a generator that has seen your test cases will
happily fit them.

That last one is why `Gate` owns a set of mandatory probes the submitter
does not choose.
