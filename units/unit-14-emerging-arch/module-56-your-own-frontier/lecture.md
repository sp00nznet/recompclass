# Module 56: Picking Your Own Frontier

Modules 53 to 55 each took a target nobody had recompiled and got somewhere. This module is
about how to choose the next one — yours — and how to tell early whether it is a week of
work, a year, or impossible.

The skill is **triage**, and it is mostly a small number of cheap measurements taken before
you are emotionally committed.

---

## 1. The Questions, Cheapest First

Roughly an afternoon, in this order, stopping early if an answer disqualifies the target.

### Is it even machine code? (Module 54 §1)

Imports and relocation density, compared against a known-native binary of similar size.
`worldempire`: one import, 14 relocations across 114 KB, versus 4,743 across 197 KB next
door. Ten minutes, and it changes the entire project.

### Can you get a copy, legally, and say so? (Module 45)

If the answer needs a paragraph of qualification, pick something else. There are plenty of
targets.

### Can you get the code *out*? (Module 33 §2)

Container, encryption, protection. A memory dump after the loader decrypts (Module 27) is
usually available; a target where you cannot reach plaintext code at all is not a
recompilation project.

### Is there an independent implementation you can run?

The single best predictor of whether the project will go smoothly, because it is your
oracle (Module 38) and often your documentation. `tamarecomp` had BrickEmuPy; every console
in Semester 2 had a mature emulator.

No emulator means you are debugging two unknowns at once — your lifter and your
understanding of the machine — with no way to separate them. Possible, and much slower.

### How much is statically resolvable?

The Module 55 measurement, and the one that decides the shape of the work:

1. Assemble the whole address space, including boot ROM and overlays.
2. Recursive descent from every entry point you can find.
3. Count unresolved transfers.
4. **Classify them by defining instruction.**

| Result | What it means |
|---|---|
| Near zero, all immediates | Module 53's situation — the ISA is doing you a favour |
| Dozens, a few mechanisms | normal; Module 14 applies |
| Hundreds, all vtable dispatch | C++; expect Module 27's experience |
| Thousands, unclassifiable | measure again — you probably have the address space wrong |

That last row is the common case for a first attempt, and Module 55's 2,533 → 227 is why
you re-measure before despairing.

### Is there a decomp, symbol file, or SDK?

Module 22's `luigismansion` was chosen because the Yasiki decompilation is **100%
complete** — no function discovery at all. Module 20's `racer` had none and hand-fixed 143
bad splits. Same era, same console class, wildly different projects.

### How big is the OS surface?

Count the imports (Module 15 §1). 147 kernel imports on Xbox. 209 on Xbox 360, already
provided. 93 HLE modules and 300+ syscalls on PS3. A bare-metal arcade board: zero.

This number is countable on day one and is the best single estimate of the runtime work.

---

## 2. What Makes a Target Genuinely Easy

From the corpus, the properties that actually correlate with success:

**A small, fully enumerable address space.** Module 53's 6,144 words.

**Immediate-only control flow.** If the ISA has nowhere to put a computed address, every
target is a build-time constant.

**A separable emulator.** Module 11's `snesrecomp` wraps LakeSnes rather than reimplementing
the SNES; the deciding property was that LakeSnes's hardware was separable *and* MIT
licensed (Module 45 §3).

**Little or no OS.** Arcade boards and cartridge consoles beat anything with a system
software layer.

**A documented commodity CPU.** Epson, Sanyo, Hitachi, Z80, 6502 — the datasheet exists.

**A corpus to validate against.** Hundreds of programs turn "it works" into a measurable
percentage (Module 39 §5).

And the properties that make it hard, in rough order of how much they cost:

**A large OS surface.** The PS3 is not hard because the Cell is hard.

**C++ with deep hierarchies.** Module 27's 178-site vtable classification, everywhere.

**Self-modifying code.** Common on Z80 home computers and hand-written assembly.

**Timing-dependent tricks.** Module 40's cycle-accurate tier.

**A programmable coprocessor.** Module 42 §5's microcode decision.

**A communications peripheral as the whole point.** Module 55 §6.

---

## 3. Deciding What "Done" Means Before You Start

Module 37's ladder has eight rungs. **Pick your target rung before you begin**, because the
work is wildly different and the honest README depends on it.

| Goal | Reasonable scope |
|---|---|
| Prove the ISA can be lifted | rung 2, with a differential test |
| A working toolkit others can use | rung 6 on one game, plus docs |
| One playable game | rung 7 |
| A verified reference implementation | rung 8, on something small |

Module 12's `lttp-recompiled` is the case for naming this early: judged as a port it is
incomplete, but it produced **ten upstream fixes** to the toolkit it was stressing. That is
a legitimate and valuable project shape — the **stress target** — and it only looks like
failure if nobody said what the goal was.

---

## 4. The Shape That Works

The corpus has a repeatable pattern for a new architecture, and it is worth following
deliberately:

**1. A toolkit repository**, named `<thing>recomp`, containing the decoder, the analyzer,
the emitter, the runtime and the docs — and no ROMs.

**2. A first game chosen to be the smallest honest instance of the platform.** Module 16's
rule. The corpus does this every time: `chipschallenge-lynx-recomp` is *"the first game on
the lynxrecomp toolkit"*; `newtris-newton-recomp` is *"the first title on newtonrecomp"*;
`blockdude-ti-recomp`, `jellymonsters-vic20-recomp`, `manicminer-zx-recomp`,
`oregontrail-apple2-recomp`.

**3. A second game**, which is what proves the toolkit is a toolkit rather than one project
with delusions of generality. `crystalmines2-lynx-recomp` is explicitly *"the second game on
the lynxrecomp toolkit."*

**4. Docs that separate fact from inference**, as `vmurecomp`'s CPU notes do.

**5. An honest README** with a status table and a scope statement.

---

## 5. Reusing What You Already Have

Before treating a target as new, check whether it is a machine you have already done with
different peripherals.

Module 34 §3's table: `apple2recomp` and `vic20recomp` share an entire 6502 front end —
decoder, flag-correct ALU, analyzer, C emitter and interpreter oracle. Only the machine
around them changed. `pacrecomp`, `galaxrecomp`, `tirecomp` and `zxrecomp` are four Z80
machines on one front end.

The corpus covers 6502, Z80, 68000, ARM, MIPS, PowerPC, SH, x86, V810, H8S, LC8670 and
E0C6200. **If your target's CPU is in that list, the CPU is not your project.** The machine
around it is.

That also tells you where the genuinely unexplored territory is: not another 6502 machine,
but another *kind* of thing — a CPU width nobody has tried, a VM nobody has lifted, a device
whose interesting part is not a CPU at all.

---

## 6. Some Frontiers That Are Still Open

Stated as observations rather than recommendations, and each with the reason it is hard:

**Palm OS (68K).** Researched in this corpus and never built. PumpkinOS reimplements roughly
800 system traps natively, which is most of a runtime. Every OS call goes through `TRAP #15`,
which is an unusually clean interception point. The obstacle is scope: the application
library is enormous and no single title is the obvious first target.

**Self-modifying Z80 programs.** `tirecomp` and `zxrecomp` work, and hand-written assembly
with SMC and `JP (HL)` remains the hard case on those platforms. A genuine research problem
with a large corpus to test against.

**Devices where the CPU is incidental.** Firmware for something whose purpose is a radio,
a motor controller, or a sensor. `nokia-recomp` is in this territory.

**Recompiling an emulator to run its own guests.** `twistedmetal-psn` does this once. The
general technique — static recompilation as an emulator optimisation — is barely explored.

**Anything with no emulator.** Hardest, and the place where a new toolkit is worth the most,
because you would be building the first implementation of anything for that machine.

---

## 7. Before You Commit

A checklist, all of it cheap:

- [ ] Confirmed it is machine code, not bytecode for a runtime
- [ ] Can obtain it legally and describe that plainly
- [ ] Can reach plaintext code
- [ ] Identified the CPU and found its datasheet
- [ ] Found an independent implementation, or accepted its absence
- [ ] Assembled the **whole** address space before measuring anything
- [ ] Counted unresolved transfers and **classified them**
- [ ] Counted the OS import surface
- [ ] Checked for a decomp, symbol file or SDK
- [ ] Chosen a target rung on Module 37's ladder
- [ ] Chosen a first game that is missing the platform's hardest problem
- [ ] Checked whether you already own the CPU front end

If that all holds, you have a project with a known shape. If it does not, you have learned
that in an afternoon rather than in March.

---

## Labs

- **Lab 96** -- Feasibility report: pick an unrecompiled target, run every measurement in
  §1, and write a report stating the shape of the work, the target rung, the first game,
  and the biggest unknown. Conclude with a recommendation, including "do not."
- **Lab 97** -- Front-end reuse audit: take two toolkits in this corpus that share a CPU,
  diff their front ends, and report what is genuinely machine-specific versus what drifted
  apart and should be shared.

---

**Unit 14 Capstone (Lab 98)**: Take a target nobody has recompiled, produce the
feasibility report, then build the decoder and an interpreter oracle for its ISA and
differentially validate them against an independent implementation — or, where none exists,
against real hardware.

---

**Next: [Module 57 -- Contributing Upstream](../../unit-15-tooling/module-57-contributing-upstream/lecture.md)**
