# Lab 81: Dependency Audit

## Objective

    Enumerate every third-party component in a recompilation project, its
    licence, and how it is linked -- then say whether the project's declared
    licence is compatible with all of it.

    ## Background

    Module 45 section 3. `snesrecomp` can be permissive because LakeSnes is
    **MIT**; had it been GPL, every port linking it would inherit that. This is
    an architectural constraint, not paperwork: retrofitting a licence change
    onto a project that links a GPL emulator means replacing the emulator.

    *This lab is not legal advice.* It is an inventory exercise.

    ## Your Task

    For a project of your choice (ideally your own):

    1. List every third-party component -- vendored source, submodules, linked
       libraries, tools your build shells out to.
    2. For each: its licence, its version, and **how it is linked** (static,
       dynamic, vendored, invoked as a subprocess).
    3. Note anything with no licence at all. "It's on GitHub" is not a licence.
    4. Produce a `NOTICE` file preserving every required notice.
    5. State whether the declared licence is compatible with everything above.

    ## Report

    The inventory table, the `NOTICE` file, and your compatibility conclusion
    with reasoning. Flag anything you could not determine rather than guessing.

**Deliverable:** a written report in your project repository.
