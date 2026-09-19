# Lab 111: Extract a Toolkit

## Objective

    Split a single-game project into a toolkit and a port, then bring up a
    second, deliberately different game on it.

    ## Background

    Module 58. The line goes at **"is this true of the machine, or of this
    program?"** And Module 58 section 2: a toolkit with one port is one project
    with delusions of generality -- you cannot tell which decisions are general
    until something else has to live with them.

    The target to aim at: `wormsrevolution`'s entire hand-written surface is four
    files, 8.5 KB, of which `main.cpp` is **146 bytes**.

    ## Your Task

    1. **Split.** Machine-general code to the toolkit; program-specific to the
       port.
    2. **Confirm the port still works**, unchanged in behaviour.
    3. **Bring up a second game** that differs in one specific way -- a different
       mapper, compiler, or peripheral. Same-again proves nothing.
    4. **Record every place the split forced a change.** These are the
       assumptions you did not know you had made.
    5. Add auto-registration (Lab 112) and a worked example to the tree.

    ## Report

    The before/after structure, the size of the per-game surface for both games,
    and the list of forced changes. That list is the actual deliverable.

**Deliverable:** a written report in your project repository.
