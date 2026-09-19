# Lab 72: Profile a Recompiled Binary

## Objective

    Profile a real recompiled binary on a real workload and find out where the
    time actually goes.

    ## Background

    Module 41's warning: your intuitions were formed on hand-written code, and
    this is not hand-written code. The time is usually **not** in the lifted
    code -- it is in the runtime, memory access, dispatch, or graphics.

    And the number that governs everything: `wormsrevolution` lifted 88,816
    functions and reaches 444.

    ## Your Task

    1. Build with symbols and frame pointers.
    2. Profile a **real workload** -- gameplay, not boot-to-title.
    3. Produce a ranked breakdown separating: runtime, generated code, dispatch,
       graphics translation, memory access.
    4. Report **what fraction of lifted functions executed at all.**
    5. Pick one baseline from Module 41 section 2 and say how you compare.

    ## Report

    The breakdown, the executed-function fraction, and one sentence on whether
    the result surprised you. Include the command that re-runs the measurement.

    If you are slower than a mature emulator of the same system, stop and find
    the structural mistake -- that is a finding, not a failure.

**Deliverable:** a written report in your project repository.
