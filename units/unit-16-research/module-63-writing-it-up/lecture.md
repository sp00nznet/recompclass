# Module 63: Writing It Up

A result nobody can read is a result nobody has. This module is about turning work into
something that survives you — and about picking the right form, because most recompilation
work should not be a paper.

---

## 1. Pick the Form That Fits

| Form | Good for | Effort |
|---|---|---|
| A good commit log | the debugging narrative | free, if you write them as you go |
| A `docs/` file | a machine, a mechanism, a measurement | an afternoon |
| A README section | what your project is and is not | an hour |
| A writeup or blog post | a technique other projects should adopt | a day or two |
| A paper | a measured result with a method | weeks |

**Most work belongs in the middle three.** The corpus's best material is a `docs/` file:
`tamarecomp`'s `VALIDATION.md`, `cybikorecomp`'s `INDIRECT.md`, `vmurecomp`'s `CPU.md`,
`xboxrecomp`'s `indirect-calls.md`. Each is one topic, a few pages, written once, permanently
useful.

Module 60's point bears repeating here: **commit messages are documentation**, and they are
the form with the best effort-to-value ratio in this entire list. `encarta`'s `IR32:`
sequence is a complete debugging narrative that cost nothing extra to produce.

---

## 2. What a Technique Writeup Contains

The shape that works, in order:

**The problem, concretely.** Not "indirect calls are hard" but "22,097 functions, a call
through a vtable slot, and no way to know the target at compile time."

**What you tried that did not work**, and why. This is the part readers cannot get anywhere
else, and the part everyone omits. `civrev`'s 301-hint failure is more instructive than its
24-hint success.

**The technique**, with enough detail to reimplement. A code listing, not a description of a
code listing.

**What it cost.** `xboxrecomp` does this well: binary search over 22,097 entries is at most
15 comparisons, and *"at ~120 ICALLs per second, this is negligible overhead."* A technique
without its cost is unusable — the reader cannot tell whether it applies to them.

**Where it does not apply.** Module 53's whole-ROM-as-one-function works because the address
space is 6,144 words. Saying so is what stops someone trying it on a PS3 title.

**The measurement.** Module 62 §8: the number and the method to re-derive it.

---

## 3. Write the Retraction

If something you published turns out to be wrong, the writeup is the correction — and doing
it in public is worth more than the original claim.

`xboxdashboard`'s README carries its retraction permanently:

> An earlier version of this README claimed a "green orb at 60fps". That orb was ours — a
> hand-written disc drawn by scaffolding in this repo... Treat any screenshot from before
> 2026-09-02 as retired.

Three things that make it a good retraction: it says what was claimed, it says what was
actually happening, and it tells readers what to do with the old evidence. Compare
`tokyojungle`'s function-count note and `encarta`'s `retract "it decodes"` commit — same
three elements, different scales.

**Keep it visible.** A correction buried in a commit does not reach someone reading the
README today.

---

## 4. If You Do Write a Paper

Two exist in this repository and are worth reading as examples of the form:
[`papers/why-static-recompilation.md`](../../../papers/why-static-recompilation.md) and
[its v2](../../../papers/why-static-recompilation-v2.md), with
[`papers/challenges-in-static-recompilation.md`](../../../papers/challenges-in-static-recompilation.md).

Notes specific to this field:

**Position papers need a real position.** "Static recompilation is interesting" is not one.
Preservation-as-restoration, or the claim that the runtime rather than the lifter is the hard
problem, are.

**Measured results need a corpus** (Module 62 §3) and a stated success criterion.

**Cite the adjacent literature.** Module 50's four — RetroWrite, rev.ng, BinRec, LeanBin —
plus the historical work: Cifuentes on decompilation, Sites on binary translation, FX!32.
The security and systems communities have been working on your problem under different
names for thirty years.

**Cite the practitioners too**, by repository and commit. A claim about what projects do
should point at the projects.

**Say what the paper does not establish.** A technique demonstrated on one target is a
demonstration, not a general result, and saying so is what makes the rest credible.

---

## 5. Where to Put It

**In the repository**, as `docs/`. The most durable option: versioned, next to the code,
found by anyone who clones.

**In the commit log.** Free, permanent, searchable, and nobody rewrites it.

**On a blog.** Reaches people, and rots. Link back to the repository so the canonical version
is the one that gets updated.

**In the community.** Module 60 §7: the Discord's value is that people find out what others
are stuck on before duplicating a month of work.

**Where the platform's community already is.** Cemetech for calculators, Planet Virtual Boy,
the N64 and GameCube decomp Discords, retro hardware forums. These people have the knowledge
you needed and want the knowledge you produced.

**In a venue**, if it is a measured result. Preservation and emulation conferences, and the
security/systems venues where the adjacent work appears.

---

## 6. The Checklist

Before publishing anything:

- [ ] Does every number have a method attached?
- [ ] Could a reader re-derive at least one of them?
- [ ] Have you said what it does **not** establish?
- [ ] Have you named what you tried that failed?
- [ ] Have you credited the prior work, by name (Module 60 §5)?
- [ ] Have you said where the technique stops applying?
- [ ] Would it survive Module 37's ten-minute audit?
- [ ] Is anything a "first" you cannot verify?

That last one is worth a sentence. "The first X" is a claim about everyone else's work and is
usually wrong, because somebody did it quietly in 2009 and did not write it up — which is the
problem this whole unit exists to fix. Describe what you did.

---

## Labs

- **Lab 122** -- Technique writeup: take something you built in this course and write it up
  in the §2 structure, including what you tried that failed and the cost measurement. Give
  it to someone who has not seen the code and ask them to reimplement from it.
- **Lab 123** -- Machine document: write the ISA and memory-model notes for a target,
  explicitly marking each statement as published fact or inference (Module 60 §3).

---

**Next: [Module 64 -- Capstone](../module-64-capstone/lecture.md)**
