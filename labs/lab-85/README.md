# Lab 85: Runtime Feature Set

## Objective

    Add the features users expect: save states, rebindable input, and saves in
    the platform-correct location, behind an overlay.

    ## Background

    Module 47 section 1. The baseline across finished ports in the corpus:
    `LinksAwakening` has save states, rebindable gamepad and keyboard, an ImGui
    debug overlay and an asset viewer; `diddykongracing` has a settings window
    on F1, a debug overlay on F2, and EEPROM saves written to AppData.

    Save states are nearly free -- your entire guest state is a struct and an
    array -- and they change how people use your build, including you while
    debugging.

    ## Your Task

    1. **Save states.** Serialise and restore guest state. Handle the
       runtime-side state too (timers, pending interrupts).
    2. **Rebindable input**, persisted.
    3. **Saves in the right place** -- the platform convention, not next to the
       executable.
    4. **An overlay** exposing all of it.
    5. Build it in the **toolkit**, not the game (Module 47 section 1).

    ## Report

    What you built, where it lives (toolkit or port), and one debugging task
    that got easier because save states exist.

**Deliverable:** a written report in your project repository.
