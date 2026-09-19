# Lab 97: Front-End Reuse Audit

## Objective

    Take two toolkits that share a CPU, diff their front ends, and report what
    is genuinely machine-specific versus what drifted apart and should be shared.

    ## Background

    Module 34 section 3. `vic20recomp`'s README states that its decoder,
    flag-correct ALU, analyzer, C emitter and interpreter oracle are *the same
    battle-tested 6502 front end* that recompiled Apple II games -- only the
    machine around them changed.

    The design rule that enables it: **your lifter must not know what a memory
    address means.** It emits `bus_read8(addr)` and stops.

    ## Your Task

    Pick two toolkits sharing a CPU -- `apple2recomp` and `vic20recomp`, or any
    two of the Z80 family (`tirecomp`, `zxrecomp`, `pacrecomp`, `galaxrecomp`).

    1. Diff the decoder, ALU, analyzer and emitter.
    2. Classify every difference: genuinely machine-specific, an improvement
       only one side received, or accidental drift.
    3. Find any place a lifter special-cases an address because of what it
       means on that machine.

    ## Report

    The classification with examples, and a recommendation for what should be
    shared. Estimate what unifying them would cost and what it would buy.

**Deliverable:** a written report in your project repository.
