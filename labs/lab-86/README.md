# Lab 86: Write a Mod

## Objective

    Override one function in a recompiled game with your own C implementation,
    using an auto-registering patch macro.

    ## Background

    Module 47 section 3, and the mechanism is a direct consequence of Module
    14's dispatch table. From `snesrecomp`'s `recomp_patch.h`:

    > **Mod / override pattern:** link a second `.obj` that defines another
    > `RECOMP_PATCH` at the same SNES address with a different function name.
    > **The last constructor to run wins**, so put mod objects after the original.

    Overriding a shipped game function is a **link-order question**. A modder
    writes a C function -- with types, a debugger, and no space constraint --
    and it replaces the original at the address the game calls.

    ## Your Task

    1. Pick a function whose effect you can see.
    2. Write a replacement in C, satisfying every caller's expectations:
       calling convention, register effects, and any memory the original wrote.
    3. Link it after the original and confirm yours runs.
    4. **Record the game revision it targets** -- addresses move (Module 46
       section 2).
    5. Document the link order.

    ## Report

    The mod, the documented link order, the revision it targets, and what went
    wrong the first time. Something will: the usual culprit is state the
    original function wrote that yours does not.

**Deliverable:** a written report in your project repository.
