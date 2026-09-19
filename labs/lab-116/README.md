# Lab 116: Negative Results

## Objective

    Find three things you ruled out, and write them up where the next person
    will look.

    ## Background

    Module 60 section 1. Bring-up is mostly eliminating plausible wrong answers.
    You will spend a day proving something is *not* the cause, feel like you
    achieved nothing, and move on -- and then someone else will spend the same
    day on the same wrong answer. So will you, in four months.

    The corpus does this well in places. `outrun` documents a ruled-out red
    herring. `tamarecomp`'s validation records two harness bugs that
    impersonated CPU bugs, including Windows text-mode stdout expanding `0x0A`
    into `0x0D 0x0A` -- caught because `X = 0x0A0D` is impossible for a 12-bit
    register.

    ## Your Task

    Go through your project's history and find three. At least one must be a
    **harness bug that impersonated a target bug** -- you will have one.

    For each: the symptom, what you suspected, how you ruled it out, and what it
    actually was. Include the giveaway if there was one.

    ## Report

    Three writeups, placed where someone hitting the same symptom would find
    them -- the `docs/` directory, not a personal notebook.

    ## Why This One Matters

    This is the single most under-supplied artifact in the field and the cheapest
    to produce. You already did the work.

**Deliverable:** a written report in your project repository.
