# Lab 101: Patch Versus Recompile

## Objective

    Implement the same behaviour change twice -- as a byte patch and as a
    recompiled override -- and compare.

    ## Background

    Module 50 section 4. The corpus patches constantly: `diddykongracing`
    neutralises three anti-piracy checks; `--protect_zero=false` changes
    behaviour without changing code.

    And the inversion worth testing: **once a program is recompiled, patching
    gets easier, not harder.** A ROM hack must not change any size; a recompiled
    program's patch is a C function with a debugger and no space constraint.

    ## Your Task

    Pick a behaviour you can see and change it both ways.

    **As a byte patch:** find the bytes, change them, keep the size identical.
    **As a recompiled override:** replace the function in C (Lab 86).

    Compare: effort, fragility across revisions, what each lets you do next,
    debuggability, and what happens when you get it wrong.

    ## Report

    Both implementations, the comparison, and a recommendation for when each is
    right. Note whether the recompiled version let you do something the patch
    could not -- extra state, a longer string, a call to a host library.

**Deliverable:** a written report in your project repository.
