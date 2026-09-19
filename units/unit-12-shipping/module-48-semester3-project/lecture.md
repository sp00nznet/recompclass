# Module 48: Semester 3 Project — Ship a Recompiled Game

Semester 1 taught you to recompile. Semester 2 took you through real console
architectures. Semester 3 has been about everything between "it runs on my machine" and
"someone else can use it."

This project is that gap, end to end. Take a target, build a repeatable pipeline, produce
evidence for what you claim, make it fast enough, and package it so a stranger can run it.

The deliverable is not a running game. **The deliverable is a project that somebody else
could pick up.**

---

## 1. Choosing a Target

Module 16 gave the selection rule for your first recompilation: pick something missing the
hardest problem on the platform. That rule was about learning the pipeline.

This time the constraints are different, because the work is about *shipping*:

**Pick something you can finish.** You are doing automation, evidence, performance and
packaging on top of the recompilation. If the recompilation itself is a six-month problem,
nothing else in this unit gets done.

**Pick something with a reference you can run.** Module 38 is load-bearing here and you
need an oracle — an emulator, an interpreter, or the original binary.

**Pick something you can legally work with and describe.** Module 45.

Three shapes that work well:

| Shape | Why |
|---|---|
| A small complete game on an existing toolkit | the pipeline work is real, the lifting is done |
| A second game on a toolkit that has one | you will find every place the toolkit was accidentally game-specific |
| Your Semester 1 project, taken to shippable | you already know its bugs; now make it usable |

That middle one is underrated. Module 9's `oracle-recompiled` builds two sister games from
one runtime; Module 20's `Rampage` repository carries *World Tour* (3,736 functions) and
*Universal Tour* (4,788) side by side. The second title is where a "toolkit" stops being
one project with delusions of generality.

---

## 2. What to Build

### Unit 9: a pipeline someone else can run

- Stage-based, from container to binary, with content-hash caching (Module 33).
- Function discovery output committed as a **file**, not held in your shell history.
- A manifest carrying every decision, with hints commented to say where they came from
  (Module 36).
- Three commands from clean checkout to build.
- CI that gates on something real — and that you have deliberately broken to prove it goes
  red (Module 35 §1).

### Unit 10: evidence

- An **oracle**, built before you needed it (Module 38 §1).
- A differential test you can run with one command.
- A fuzzing loop, even a crude one, plus every reproducer it found kept as a regression
  test (Module 39).
- An honest statement of where you are on Module 37's ladder.

### Unit 11: measured performance

- A profile of the whole binary, runtime included, on a real workload (Module 41).
- One targeted optimisation, with a before/after that you can re-derive by running one
  command.
- The fraction of lifted functions that actually execute. Expect to be surprised.

### Unit 12: shipping

- Input verification that names what it found and warns without refusing (Module 46 §2).
- Legible failures — categorised, with addresses (Module 46 §4).
- A README a stranger can follow, with an honest scope section.
- Save states, rebindable input, saves in the right place (Module 47).
- One worked mod, if your dispatch supports it.

---

## 3. A Suggested Order

Roughly the order the corpus's successful projects went in, which is not the order people
expect.

**Weeks 1–2: pipeline and oracle, before anything works.** Resist starting on the game.
The oracle is what makes the next six weeks fast, and `encarta`'s first commits were the
oracle, not the lifter.

**Weeks 3–5: bring-up.** The recompilation itself. Expect the shape from Module 28's
table: codegen is quick, bring-up is where the time goes, and the two are uncorrelated.
Keep a log of ruled-out hypotheses as you go (Module 46 §4) — you will not remember them
later and you will re-investigate them at 2am.

**Week 6: evidence.** Differential testing, fuzzing, and the honest claim. Do this *before*
optimising, because Unit 11 changes what code exists and you need a way to tell whether it
still works.

**Week 7: performance.** Profile first. Expect the answer to be the runtime or memory
access, not anything clever.

**Week 8: packaging.** Then hand it to somebody and watch them fail, without helping. Every
place they get stuck is a documentation bug.

---

## 4. What to Write Down

This is the part most projects skip, so it is worth being specific about.

**A status table with real states.** `pokemon-crystal`'s uses `⏳ user-test` for "I believe
this works but nobody has verified it" — which is real information.

**An Honest scope section.** `ydkj`'s: *"the front-end renders and reaches the interactive
title screen; input into an actual question round hasn't been driven yet."*

**Numbers with their provenance.** Function count, hint count, stub count, generated size,
binary size, and — if you claim a compatibility figure — *how you measured it*. `3dsnes`'s
"340 of 375, by an unattended corpus run, not by spot-checks" is the standard.

**What you ruled out.** `outrun`'s red herring writeup.

**Attribution.** Every toolkit, emulator and decomp project you built on, by name.

---

## 5. How to Assess Your Own Work

Run Module 37's ten-minute audit on your own repository, as if you had never seen it:

1. What does the `.gitignore` say is missing, and what does that mean for your claims?
2. `ls src/` — how much is hand-written harness?
3. `wc -l` both halves.
4. Is your fallback silent? Would your project "work" if every recompiled function were
   wrong?
5. What drives the frame loop — the game, or you?
6. Do you print `successful` and `failed`?
7. Could a reader re-derive any number in your README?

If question 4 makes you uncomfortable, that is the module working. Most projects in this
corpus would have failed at least one of these before someone looked.

### Signs it went well

- Someone else built it from the README without asking you anything.
- Your compatibility or correctness number can be regenerated by one command.
- You retracted something. `xboxdashboard` deleted a screenshot and 2,204 stubs;
  `tokyojungle` revised a function count *downward*. Both projects are better for it.
- You can say precisely what does not work.

### Signs it did not

- The README is more impressive than `git log`.
- The only way to build it is to ask you.
- Every number goes up and none has a method attached.
- You do not know what fraction of your lifted code executes.

---

## 6. Where This Goes

Semester 4 is about frontiers: hybrid static/dynamic techniques, decompilation-assisted
recompilation, contributing upstream to the toolkits you have been using, and architectures
nobody has recompiled yet — including some genuinely strange ones, where the CPU is 4 bits
wide or the "machine code" is bytecode for an interpreter that also has to be recompiled.

If your Semester 3 project is solid, it is also the foundation for that work. And if you
contributed a fix upstream along the way — the way Module 12's `lttp-recompiled` produced
ten fixes to the toolkit it was stressing — you have already started.

---

## Deliverables

- [ ] A public repository with no copyrighted material in it
- [ ] Three commands from clean checkout to build
- [ ] A manifest carrying every decision, with commented hints
- [ ] CI that gates on something real, proven by breaking it
- [ ] An oracle and a one-command differential test
- [ ] A fuzzing loop and its accumulated reproducers as regression tests
- [ ] A profile, one measured optimisation, and a re-runnable measurement
- [ ] Input verification, categorised failures, addresses in error messages
- [ ] Save states, rebindable input, platform-correct save paths
- [ ] A README with a status table, an honest scope section, and sourced numbers
- [ ] Your position on Module 37's ladder, stated explicitly
- [ ] Attribution for everything you built on

---

**Semester 3 complete.** Next: **Semester 4 — Frontiers and Research** *(Modules 49-64, not
yet written — see [SYLLABUS.md](../../../SYLLABUS.md) for the outline)*
