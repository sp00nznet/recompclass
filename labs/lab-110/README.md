# Lab 110: Fill a Named Gap

## Objective

    Implement something a project has explicitly documented as missing.

    ## Background

    Module 57 section 4. `ps3recomp`'s `docs/MODULE_STATUS.md` tracks every HLE
    module as Not Started / Stubbed / Partial / Complete -- which doubles as a
    contribution roadmap. **Check it first; it moves.**

    The shape to look for: **the plumbing is done and the payload is missing.**
    `cellVdec` sequences callbacks correctly and never decodes a frame. That is
    an unusually good contribution target, because the interface is pinned down
    by a working caller, so you can tell immediately whether you are right.

    ## Your Task

    1. Find a gap a project has named as open.
    2. Confirm it is still open, and say so in your first message.
    3. Implement against the interface its existing callers already define.
    4. Verify -- ideally differentially, against whatever the real thing did.
    5. Submit with your verification method.

    ## Report

    The gap, your implementation, how you verified it, and the outcome. Include
    what the existing callers told you about the interface that the
    documentation did not.

**Deliverable:** a written report in your project repository.
