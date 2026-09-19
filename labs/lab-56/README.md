# Lab 56: Break Your Own CI

## Objective

    Prove that every gate in your CI can actually fail.

    ## Background

    Module 35 opens with a real bug from this repository: a job called "Run
    Python labs" that ran `python test_lab.py`, which defines pytest classes
    and exits 0. It passed on every commit for months and tested nothing, while
    a genuine `NameError` sat in a shared lab helper.

    **A CI step that cannot fail is worse than no CI step**, because it converts
    "untested" into "tested" in every reader's head, including yours.

    ## Your Task

    Take a pipeline with CI (yours, or the one from Lab 59) and, for each gate:

    1. Introduce a real defect of the kind that gate exists to catch.
    2. Run CI. Confirm it goes red, and that the message names the problem.
    3. Revert.

    Defects worth trying: a syntax error in a generated file; a lifter change
    that alters golden output; a deleted runtime symbol; a test that imports a
    module that no longer exists; a solution left stale after a stub change.

    ## Report

    A table of gate, defect injected, did it fail, and how legible the message
    was. **Any gate that stayed green is the finding** -- write up why, and
    either fix it or delete it.

**Deliverable:** a written report in your project repository.
