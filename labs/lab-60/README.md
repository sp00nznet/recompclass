# Lab 60: Audit Three Projects

## Objective

    Apply Module 37's ten-minute audit to three real recompilation repositories,
    one of which is your own.

    ## Background

    The audit, from Module 37 section 6:

    1. **Read the `.gitignore` first.** It tells you whether the interesting half
       of the project is even present, and therefore what any other observation
       can prove.
    2. **`ls src/` for hand-written names.** `fe_menu.c`, `rw_renderer.c`,
       `static_textures.c` are harness. Generated output is thousands of
       `sub_XXXXXXXX` functions in numbered files.
    3. **`wc -l` both groups.**
    4. **Audit the toolkit, not the port.** If the toolkit is emulator-hosted,
       no port on it can claim more than the toolkit allows.
    5. **Find the fallback. Is it silent?**
    6. **What drives the frame loop** -- the game, or the project's code?
    7. **Look for the counters.**

    ## Your Task

    For each of three projects, produce a one-paragraph evidence assessment and
    place it on the **ladder of evidence** (Module 37 section 5).

    Be specific. "The README claims X; `src/foo.c` line N does Y" is an
    assessment. "Seems overstated" is not.

    ## Report

    Three assessments, each naming its rung and the evidence for it. For your
    own project, say what you will change as a result.

    Be fair: the goal is accuracy in both directions. A project that is *more*
    impressive than its README claims is also a finding worth reporting.

**Deliverable:** a written report in your project repository.
