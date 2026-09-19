# Lab 102: Read the Adjacent Literature

## Objective

    Read one paper from the binary rewriting community and report what transfers.

    ## Background

    Module 50 section 2. The security and systems communities have been working
    on your problems for thirty years under different names -- they say
    "rewriting" and "binary analysis" where preservation people say
    "recompilation". Searching the other field's terms finds solved problems.

    ## Your Task

    Pick one:

    - **RetroWrite** (Dinesh, Burow, Xu & Payer, IEEE S&P 2020) -- static
      rewriting for fuzzing and sanitization; recovers relocation information.
    - **rev.ng** (Di Federico, Payer & Agosta, CC 2017) -- lifts to LLVM IR,
      recovers CFGs and **function boundaries** (Module 34's root cause).
    - **BinRec** (Altinay et al., EuroSys 2020) -- dynamic traces guiding static
      lifting; the formal version of Module 49 section 4.
    - **LeanBin** (Wodiany, Pop & Luján, arXiv 2024) -- lifting for debloating;
      Module 44's 444-of-88,816 problem from a security motivation.

    ## Report

    One page: what problem it solves, what technique it uses, what transfers to
    a recompilation project in this course, and what does not -- with reasons.

    Be specific about the mismatch. These tools target server software, which
    has different properties from game binaries. Where their evaluation would
    not hold on your targets, say so.

**Deliverable:** a written report in your project repository.
