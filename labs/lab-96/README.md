# Lab 96: Feasibility Report

## Objective

    Pick a target nobody has recompiled, run every measurement in Module 56
    section 1, and write a report that ends in a recommendation -- **including
    "do not".**

    ## Your Task

    In order, stopping early if an answer disqualifies it:

    1. **Is it machine code?** Imports and relocation density against a
       known-native binary of similar size (Module 54 section 1).
    2. **Can you get a copy legally, and say so plainly?**
    3. **Can you reach plaintext code?**
    4. **Is there an independent implementation you can run?** The single best
       predictor of whether this goes smoothly.
    5. **How much resolves statically?** Assemble the *whole* address space
       first (Module 55 section 2), then count unresolved transfers and
       **classify them by defining instruction**.
    6. **Is there a decomp, symbol file or SDK?**
    7. **How big is the OS import surface?**

    ## Report

    The measurements with their methods, the shape of the work, your target rung
    on Module 37's ladder, your proposed first game, the biggest unknown, and a
    recommendation.

    ## What Good Looks Like

    A well-documented "this is not worth doing, here is why" is a real
    contribution and almost nobody publishes one (Module 59 section 6). If that
    is your conclusion, it is a complete answer to this lab.

**Deliverable:** a written report in your project repository.
