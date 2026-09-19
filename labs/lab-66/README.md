# Lab 66: Divergence Minimiser

## Objective

Turn a 3,600-frame recording and a frame number into a bug report.

## Background

Module 39 section 4. A raw failing input is a lead, not a finding. The
procedure:

1. **Truncate first.** If the divergence is at frame 2,150, everything after
   it is noise. Cut there.
2. **Bisect the input backwards.** Delete the first half; does it still
   diverge? This usually collapses thousands of frames into dozens.
3. **Then bisect the code** (Lab 63) to find the function.

Two nested bisections -- one over inputs, one over the address space -- is
the standard way to go from "something is wrong in a 40,000-function binary"
to a named function in an afternoon.

## Your Task

Implement in `minimise.py`:

- `truncate(inputs, index)` -- everything up to and including the failure.
- `shrink_prefix(inputs, still_fails)` -- bisect away the leading inputs.
- `shrink_elements(inputs, still_fails)` -- remove individual inputs.
- `minimise(inputs, still_fails)` -- the whole procedure, with a log.

`still_fails(sequence)` returns True when the sequence still reproduces.

## The Invariant

Every intermediate must still reproduce. A minimiser that returns something
which does *not* fail has produced a different bug, and you will chase it.
Assert this.
