# Lab 115: Machine Document

## Objective

    Write the ISA and memory-model notes for a target you have worked on,
    marking every statement as published fact or inference.

    ## Background

    Module 60 section 3. Project documentation is current-state and goes stale.
    **Machine documentation outlives your project entirely** -- someone writing
    an emulator, a disassembler or a different recompiler wants it.

    `vmurecomp`'s `docs/CPU.md` sets the standard in its opening lines:

    > This is not a datasheet -- it records the decisions the decoder and runtime
    > had to make, and **which of them rest on published facts versus convention**.

    Six months on you will not remember which of your facts came from a datasheet
    and which from watching a program behave. An inference that hardened into an
    assumption is how a project gets stuck -- and how a wrong fact propagates
    into everyone who reads your notes.

    ## Your Task

    Cover: register file and widths, memory model (including whether spaces are
    disjoint), the opcode map, control flow and any paging, interrupts and their
    priority, timing and clocks, and peripherals.

    **Mark every statement.** Published fact, convention, or inference from
    observation. Cite the datasheet where you have one.

    Then give it to someone who has not worked on the target and ask them to use
    it. Record what they had to ask.

    ## Report

    The document, and the questions it failed to answer.

**Deliverable:** a written report in your project repository.
