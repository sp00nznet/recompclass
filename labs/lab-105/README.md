# Lab 105: Feed Back

## Objective

    Produce an artifact useful to a decompilation project and offer it upstream.

    ## Background

    Module 51 section 6. The relationship goes both ways, and this is the part
    most recompilation projects miss. Your recompiler produces things a decomp
    team wants and cannot easily generate:

    - **Function boundaries** your recursive descent found that their hand work
      has not reached.
    - **Execution traces** ranking their unmatched functions by how often they
      actually run -- a prioritisation they otherwise guess at.
    - **Divergence reports.** If your output and their matching C disagree,
      exactly one of you is wrong.

    ## Your Task

    Pick a target with an active decompilation project. Produce one of the above,
    in a format they can use -- ask first rather than inventing one.

    Then offer it. Approach as a peer: their work deleted an entire phase of
    yours (Module 51 section 2), so lead with what you can give back.

    ## Report

    The artifact, how you generated it, the response, and what you learned about
    their workflow. A polite decline is a valid outcome and still worth writing
    up -- note why it was not useful.

**Deliverable:** a written report in your project repository.
