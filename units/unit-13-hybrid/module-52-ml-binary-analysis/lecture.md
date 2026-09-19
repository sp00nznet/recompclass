# Module 52: Machine Learning for Binary Analysis

This module comes with a warning that the rest of the course has earned the right to give.

Module 37 established a standard: when a project claims something works, ask what the
evidence would look like if it did not. That standard applies with particular force here,
because machine learning applied to binary analysis is an area with enthusiastic claims, a
shortage of reproducible evaluation, and a failure mode — **plausible-looking wrong output**
— that is exactly the kind this field is worst at detecting.

So this module is organised around what is verifiable, what is promising, and what to be
suspicious of.

---

## 1. The Structural Problem

Start with why this is harder than it looks.

A language model that produces C from machine code produces C that *looks* right. It has the
shape of decompiled code, the variable names are plausible, the control flow is sensible.
And Module 37's whole catalogue of failures — the menu drawn by the harness, the orb drawn
by scaffolding, the codec that "decoded" its own code segment — is about exactly this
failure mode: **output that resembles success closely enough that a human stops checking.**

Recompilation has an unusually strong defence, and you should insist on it here: a perfect
oracle exists (Module 38 §1). The original binary runs. Anything a model produces can be
differentially tested against it.

**The rule for this entire module:** an ML technique is usable in a recompilation pipeline
exactly when its output is **mechanically checkable**. Where it is, the model is a
productivity tool and the checker is the source of truth. Where it is not, you are
substituting a confident guess for an observation, which Module 33 §3 already told you is
the wrong trade.

---

## 2. Verifiable: Tasks With a Checker

These are worth doing today, because you can tell when they are wrong.

### Function boundary detection

Module 34's recurring root cause. A model proposing boundaries is a *hypothesis generator*,
and Module 34 §5 already gives you the checker: a function ending without a terminator is
suspicious, and the fallthrough detector finds it statically.

Better still, Module 49 §4's insight applies — a proposed boundary that execution never
reaches is unfalsifiable, but one that a trace confirms is settled. Use ML to propose, use
traces and structural checks to dispose.

### Naming

Given a function's code, propose a name. This is where models are genuinely strong and where
being wrong is cheap: a badly named function is a documentation defect, not a correctness
defect.

Given Module 41's point that generated code is thousands of near-identical `sub_XXXXXXXX`
functions, plausible names are a real improvement to a profile even at imperfect accuracy —
*provided* names from a model are marked as such and never confused with names imported from
a decompilation (Module 51 §4).

### Code similarity

Finding that a function in your binary matches a known library routine — `memcpy`, a CRC, a
decompressor — is a well-suited task, and it is checkable: you can differentially test the
candidate against the real implementation.

This is valuable precisely because of Module 55 §2's finding: CyOS calls into the boot ROM
constantly for `memcpy` and `memset`. Identifying library code lets you replace it with a
native implementation rather than lifting it.

### Format and protocol inference

Proposing a structure for an undocumented file format, then validating the parse against the
whole corpus. Module 54 §4's `newtcc check unna.zip` is the shape of the checker: a
hypothesis that fails on any file in the archive is wrong.

---

## 3. Unverifiable: Be Suspicious

**Neural decompilation** — producing readable, idiomatic source from a binary — is the
headline application and the one to hold to the strictest standard.

The output is prose-like, fluent, and does not compile to the same behaviour unless
something checks it. If a model emits a function and nothing verifies equivalence against
the original, you have generated something that *reads* like the program and may not *be*
the program.

That is not a reason to dismiss it. It is a reason to insist on the pipeline:

```
binary ──▶ model ──▶ candidate C ──▶ compile ──▶ differential test vs original ──▶ accept/reject
                                                          ▲
                                                   this is the product
```

The checker is the contribution. Without it you have a plausible-text generator pointed at
something where plausibility is the failure mode.

**Semantic summaries** — "this function handles collision detection" — have the same
property and lower stakes. Useful for orientation, never a basis for a decision.

**LeanBin** [Wodiany, Pop & Luján, arXiv 2024] is worth reading as a contrast: it uses
lifting and recompilation for debloating with measurable outcomes (size, attack surface).
Measurable outcomes are what to look for when evaluating any claim in this space.

---

## 4. What Is Actually Running in This Corpus

Two real, verifiable applications, both narrow, both with checkers.

**[honyaku](https://github.com/sp00nznet/honyaku)** — *"LLM-driven Japanese to English
translation pipeline for 2D console games, built on the recomp static-recompilation
toolchains. Tools only; no game data."*

Note why this works. Translation is a task models are genuinely good at; the output is
**text, evaluated by humans who read the language**; and recompilation is what makes it
insertable — once the game is C, the text is data you control rather than bytes in a fixed
space. A ROM translation hack must fit the original string length. A recompiled game's
strings do not.

This is the honest shape of ML in this field right now: **not doing the recompilation, but
doing something adjacent that recompilation unlocked.**

**[recomp-harness-mcp](https://github.com/sp00nznet/recomp-harness-mcp)** — *"MCP server
that lets AI agents discover, build, recompile, and run a collection of static-recompilation
projects."*

Automation of the pipeline, not the analysis. An agent that runs Module 33's batch harness
and reports categorised failures is doing work that is entirely checkable — the build either
succeeded or it did not.

**[ida-recomp-toolkit](https://github.com/sp00nznet/ida-recomp-toolkit)** is the
non-ML comparison worth keeping in view: a headless IDA Pro toolkit for cross-validating
recompilation projects. Conventional analysis tooling remains extremely strong, and
"somebody else's implementation" (Module 53 §5) beats a model that agrees with you.

---

## 5. And This Course

Consistency requires saying it: **the prose of this course was written by a language model**
(see the README), working from the repositories, their documentation and their commit
histories.

Which is why the course is built the way it is. Every claim points at a specific file,
commit or number in a public repository, because that is what makes the text checkable
rather than merely plausible. Module 37's ten-minute audit applies to this course as much as
to any project in it, and the corrections in its git history — a misattributed project, a
fabricated statistic, a directory tree that did not exist — are what the standard catches
when it is enforced.

That is the working relationship to aim for. Not *the model produces the artifact*, but **the
model produces a claim and something mechanical checks it.**

---

## 6. Evaluating a Claim in This Space

A checklist, and it is Module 37's applied to a new subject:

- [ ] **What does it output, and how would you know it was wrong?**
- [ ] Is there a checker, and is the checker the actual contribution?
- [ ] Was it evaluated on a corpus or on examples? (Module 39 §5)
- [ ] Are the failures reported, categorised, and counted?
- [ ] Could you re-derive the headline number by running one command?
- [ ] Does the failure mode look like success?

That last question is the one specific to this area. A crashing decompiler is honest. One
that emits confident, wrong, compilable C is the thing this course has spent two units
learning to detect.

---

## Labs

- **Lab 106** -- Propose and check: use any hypothesis generator you like — a model, a
  heuristic, a pointer scan — to propose function boundaries, then build the structural and
  trace-based checkers that accept or reject each proposal. Report the acceptance rate and
  what the rejected ones had in common.
- **Lab 107** -- Equivalence gate: build a pipeline that takes candidate C for a function,
  compiles it, and differentially tests it against the original binary's behaviour, refusing
  anything that diverges. Then feed it deliberately wrong candidates and confirm they are
  rejected.

---

**Unit 13 Capstone (Lab 108)**: Take a project that is purely static or purely
interception-based and move it one step along Module 49's spectrum — adding trace-guided
discovery, an interpreter fallback, or a migration path — and report the crossover metric
before and after.

---

**Next: [Module 53 -- Very Small Targets](../../unit-14-emerging-arch/module-53-four-bit/lecture.md)**
