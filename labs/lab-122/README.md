# Lab 122: Technique Writeup

## Objective

    Take something you built in this course and write it up so someone else can
    reimplement it.

    ## Background

    Module 63 section 2. The structure that works:

    1. **The problem, concretely.** Not "indirect calls are hard" but "22,097
       functions, a call through a vtable slot, no target at compile time."
    2. **What you tried that did not work**, and why. The part readers cannot
       get anywhere else, and the part everyone omits.
    3. **The technique**, with enough detail to reimplement -- a code listing,
       not a description of one.
    4. **What it cost.** `xboxrecomp` does this well: binary search over 22,097
       entries is at most 15 comparisons, and *"at ~120 ICALLs per second, this
       is negligible overhead."* A technique without its cost is unusable.
    5. **Where it does not apply.**
    6. **The measurement**, with the method to re-derive it.

    ## Your Task

    Write it. Then **give it to someone who has not seen your code and ask them
    to reimplement from it.** Record every question they ask.

    ## Report

    The writeup, the questions it failed to answer, and the revision.

    ## Checklist Before Publishing

    - [ ] Does every number have a method attached?
    - [ ] Have you said what it does **not** establish?
    - [ ] Have you named what you tried that failed?
    - [ ] Have you credited prior work by name?
    - [ ] Is anything a "first" you cannot verify?

**Deliverable:** a written report in your project repository.
