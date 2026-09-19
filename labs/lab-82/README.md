# Lab 82: Ship-the-Tool Workflow

## Objective

    Restructure a project so a user with their own copy can go from binary to
    running build with documented commands -- and so a fresh clone contains no
    copyrighted material.

    ## Background

    Module 45 section 1. Every port in the corpus says a version of *"bring your
    own disc; no game files included"*, and the architectural consequence is
    that **the recompiled output is gitignored too, not just the ROM**.

    ## Your Task

    1. Audit what a fresh clone contains. Anything derived from the original
       binary?
    2. Fix the `.gitignore` -- ROM, assets, **and generated output**.
    3. Document the user's path: where their copy goes, what commands to run,
       what they will see.
    4. Verify: clone into a clean directory and confirm nothing copyrighted is
       present.
    5. Note what this costs you in verifiability (Module 45 section 2) and say
       so in the README.

    ## Report

    The before/after of what ships, the user-facing commands, and a paragraph on
    which of your README's numbers a reader can and cannot check.

**Deliverable:** a written report in your project repository.
