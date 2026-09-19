# Lab 71: Unit 10 Capstone: Differential Fuzzer with Nested Minimisation

## Objective

Combine Labs 62-70 into a loop that finds a divergence, shrinks it, locates
the responsible function, and produces a claim that survives an audit.

## Your Task

**Oracle** (Lab 62). Independent if you can get one -- Module 53's project
used a core written by someone else, in another language, from the same
datasheet.

**Fuzz** (Lab 65, 66). Randomised inputs through both implementations,
deterministic and replayable, detecting the first divergence.

**Minimise twice.** Input bisection (Lab 66), then code bisection (Lab 63)
to find the function.

**Tripwire** (Lab 64). Boundary assertions so silent corruption surfaces at
the call that caused it.

**Keep every reproducer** as a regression test.

## Deliverable

A one-command differential run, a corpus of minimised reproducers, and for
each finding: the minimal input, the implicated function, and the divergence.

## The Part That Is Graded

An **evidence statement** for your result that would survive Module 37's
audit. State your rung, how you measured, what you did not test, and one
thing you ruled out. If your fuzzer found nothing, say that -- and say what
would have to be true for that to be good news rather than a broken harness.
