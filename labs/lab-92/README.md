# Lab 92: Encoding Traps

## Objective

Decode an encoding with an escape hatch, and build the check that catches
getting it wrong -- because getting it wrong does not crash.

## Background

Module 54 section 4, from `newtonrecomp`'s `BYTECODE.md`:

> `pop-handlers` is simple-op 7, and 7 cannot fit in the 3-bit field, so it
> is encoded **`07 00 07`** -- three bytes. Read it as one and the two
> operand bytes masquerade as a `pop` and another `pop-handlers`, which
> **silently corrupts every function containing a `try` block**. Across the
> archive the escape occurs **10,818 times** and its operand is always 7.

And the gap: *"Opcodes 1 and 2 are unused -- that gap is what makes the
table look 'shifted' if you guess at it."*

The misparse does not crash. It produces *plausible instructions*, and only
in functions with exception handlers. Your decoder works on most of the
corpus and quietly mangles a subset.

## Your Task

Implement in `encoding.py`:

- `decode_one(data, pos)` -- one instruction, handling the escape.
- `decode_all(data)` -- a whole stream.
- `decode_naive(data)` -- the buggy version that ignores the escape.
- `corpus_check(programs)` -- find where the two disagree.

## The Deliverable

`corpus_check` must find programs where naive and correct decoders disagree
and report **how many** and **where**. That count is the argument: 10,818 is
persuasive, one example is not.
