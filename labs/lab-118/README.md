# Lab 118: Measure an Open Problem

## Objective

    Pick an open problem where the honest state is "nobody has counted", build
    the corpus and the measurement, and publish the number with its method.

    ## Background

    Module 61. Several of the problems there are open mainly because nobody has
    measured anything:

    - **How common is self-modifying code**, really, across a large corpus of
      ZX Spectrum or TI-83 programs? Nobody has published that number and the
      field's intuition may be badly wrong in either direction.
    - **How statically recompilable is a given ROM?** There is no accepted
      metric. `cybikorecomp`'s unresolved-transfer count before and after
      assembling the address space is the closest thing.
    - **Does pointer-scan hinting help or hurt**, measured across N targets
      rather than the one where it went wrong?

    ## Your Task

    Follow Module 62's method:

    1. Ask something that **can be answered no**.
    2. Build or identify the corpus, and identify it precisely (hashes, or a
       documented acquisition procedure).
    3. Build the measurement, and **prove it detects a bug you inject**.
    4. Measure. Vary one thing.
    5. Suspect the harness first.
    6. Report failures categorised and partials honestly.

    ## Report

    The number, the method, the corpus, and the code. Plus: what result would
    have made you abandon the hypothesis, and whether you got close to it.

    A measurement is a complete contribution and the cheapest kind to make.

**Deliverable:** a written report in your project repository.
