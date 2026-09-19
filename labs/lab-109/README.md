# Lab 109: Upstream a Fix

## Objective

    Find a genuine bug in a toolkit you use, minimise it, and get it merged.

    ## Background

    Module 57. `lttp-recompiled` contains no code and produced **ten upstream
    fixes** to the toolkit it was stressing. A serious port is the best
    bug-finder a toolkit can have, because your target uses a different subset
    of the machine than its author's did.

    ## Your Task

    1. **Find one.** Not a feature request -- a case where the toolkit does the
       wrong thing.
    2. **Minimise it** (Module 39 section 4): shrink the input, then bisect the
       code.
    3. **Isolate it from your project.** If it reproduces with a synthetic
       fixture, the maintainer needs nothing of yours.
    4. **Bring differential evidence**: ours emits X, the reference produces Y,
       here is the state at divergence.
    5. **Bring a test** that fails before and passes after.
    6. **Say what you ruled out.**
    7. Submit it.

    ## Report

    The bug, the minimal reproducer, the evidence, and what happened. A rejected
    patch with a stated reason is a complete answer -- write up the reason.

    If you cannot share the binary it was found on, say so up front and describe
    the shape instead.

**Deliverable:** a written report in your project repository.
