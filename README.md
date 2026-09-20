# Static Recompilation: From Theory to Practice

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Course Status](https://img.shields.io/badge/Course-Complete-brightgreen.svg)](#)
[![Modules](https://img.shields.io/badge/Modules-64-blue.svg)](#)
[![Labs](https://img.shields.io/badge/Labs-123-green.svg)](#)

> An open course on static binary recompilation -- the art of translating compiled programs from one platform to another at the source level.
>
> Four semesters, 64 modules, 123 labs, 67 with generated reference solutions.

---

## About This Course

Static recompilation is the process of disassembling a compiled binary, lifting its instructions into portable C source code, and recompiling that code to run natively on modern hardware -- no runtime emulator required. It is one of the most powerful techniques in software preservation, yet almost no structured learning material exists for it.

This course changes that. Across **16 Units**, **64 Modules**, and **50 Hands-on Labs**, you will go from understanding basic binary formats to recompiling real console games for modern platforms.

Every module points at real, public, committed work -- specific files, specific commits, specific numbers -- rather than describing techniques in the abstract. Where a project's own README overstates what its code does, the course says so and shows you how to check. Module 37 is entirely about that skill.

**Semester 1** ramps up slowly. Plenty of time to get comfortable reading assembly, using the tools, and understanding the mechanical process of lifting -- all before you touch a real console target. Your first recompilations are the simplest architectures: Game Boy, NES, SNES, GBA, and DOS.

**Semester 2** is where things get serious. N64, GameCube, Wii, Dreamcast, PS2, Saturn, Xbox, Xbox 360, and PS3. Multi-processor systems, GPU pipeline translation, and the hardest targets the community has tackled.

**Projects this course draws on:** [Ned Heller](https://github.com/sp00nznet) (sp00nznet) -- hobbyist and static recompilation practitioner, maintaining a public corpus of recompilation toolkits and ports spanning 25+ CPU families. Consoles (N64, SNES, Game Boy, GBA, Xbox, Xbox 360, PS2, PS3, GameCube, Wii, Dreamcast, Saturn), arcade boards (Sega Model 2/3, Lindbergh, Namco System ES3, CPS1, Midway), handhelds and phones (PSP, Vita, N-Gage, iOS, Android), home computers (Apple II, VIC-20, ZX Spectrum, 68k Macintosh), and some genuinely strange ones -- a 4-bit Tamagotchi, the Apple Newton's bytecode, and a Dreamcast VMU.

**Community:** Join the [sp00nznet recomp Discord](https://discord.gg/CRpzGWZFcu) -- a place to discuss static recompilation, debugging, course material, or just hang out with others working on recomp projects.

---

## Why This Course?

Software preservation is a race against time. Hardware degrades, proprietary platforms disappear, and with them go decades of creative and technical work. Emulation has carried the preservation community far, but it has inherent limits: accuracy costs performance, and each target demands a purpose-built emulator.

Static recompilation offers a fundamentally different approach. Instead of simulating foreign hardware at runtime, we translate programs into native code that runs directly on modern machines. The result is faster, more portable, and often easier to maintain than a full emulator.

Despite its power, the static recompilation community has grown almost entirely through oral tradition -- scattered blog posts, reverse engineering forums, and reading other people's code. This course aims to be the comprehensive, structured resource the community has needed: a single path from foundational theory to shipping real recompiled binaries.

Whether you are a preservationist, a reverse engineer, a systems programmer, or simply someone who wants to understand what happens between "disassemble" and "it runs natively," this course is for you.

---

## Prerequisites

- Solid working knowledge of **C programming** (pointers, structs, bitwise operations)
- **No prior assembly experience required** -- Module 4 teaches you to read assembly from scratch
- Comfort with the **command line** (building projects, running scripts, navigating directories)
- A Linux, macOS, or WSL environment with a C compiler and Git installed

---

## Course Map

### Semester 1: Foundations and First Targets

#### Unit 1: Foundations (Modules 1--5)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 1](units/unit-1-foundations/module-01-what-is-static-recomp/) | What Is Static Recompilation? | Emulation vs. recompilation, the recomp pipeline, when and why to use static recomp |
| [Module 2](units/unit-1-foundations/module-02-binary-formats/) | Binary Formats and Loaders | ELF, PE, ROM headers, memory maps, entry points, segment layout |
| [Module 3](units/unit-1-foundations/module-03-cpu-architectures/) | CPU Architectures Overview | Registers, instruction encoding, calling conventions across Z80, 6502, MIPS, PPC, ARM, x86 |
| [Module 4](units/unit-1-foundations/module-04-reading-assembly/) | Reading Assembly | How to read x86, MIPS, ARM, Z80, PPC disassembly; compiler-generated patterns |
| [Module 5](units/unit-1-foundations/module-05-tooling-ghidra-capstone/) | Tooling Deep Dive | Ghidra navigation and scripting, Capstone API, building an analysis workflow |

#### Unit 2: Core Techniques (Modules 6--8)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 6](units/unit-2-core-techniques/module-06-control-flow-recovery/) | Control-Flow Recovery | Linear sweep vs. recursive descent, CFG construction, basic blocks, function boundaries |
| [Module 7](units/unit-2-core-techniques/module-07-lifting-fundamentals/) | Instruction Lifting Fundamentals | Register models in C, flag computation, translating instructions to C statements |
| [Module 8](units/unit-2-core-techniques/module-08-first-lift-z80/) | Your First Lift | Hand-translating Z80 assembly to C, building a runtime, verifying against an emulator |

#### Unit 3: First Targets (Modules 9--13)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 9](units/unit-3-first-targets/module-09-game-boy/) | Game Boy Recompilation | SM83 instruction set, ROM banking, tile-based graphics, gb-recompiled pipeline |
| [Module 10](units/unit-3-first-targets/module-10-nes-6502/) | NES Recompilation | 6502 CPU, PPU, mappers (MMC1/MMC3/NROM), iNES format |
| [Module 11](units/unit-3-first-targets/module-11-snes/) | SNES Recompilation | 65816 architecture, DMA, Mode 7, co-processors (SuperFX, DSP-1) |
| [Module 12](units/unit-3-first-targets/module-12-gba-arm7/) | GBA Recompilation | ARM7TDMI, ARM/Thumb interworking, BIOS HLE, tile and bitmap modes |
| [Module 13](units/unit-3-first-targets/module-13-dos/) | DOS Recompilation | Real-mode x86, interrupt-driven I/O, DOS API shims, segmented memory |

#### Unit 4: Pipeline Essentials (Modules 14--16)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 14](units/unit-4-pipeline-essentials/module-14-indirect-calls/) | The Indirect Call Problem | Jump tables, function pointers, dynamic dispatch, strategies for unresolved targets |
| [Module 15](units/unit-4-pipeline-essentials/module-15-hardware-shims/) | Hardware Shims and SDL2 | Graphics/audio/input abstraction, SDL2 integration, accuracy vs. performance |
| [Module 16](units/unit-4-pipeline-essentials/module-16-semester1-project/) | Semester 1 Mini-Project | Guided end-to-end recompilation of your chosen simple target |

### Semester 2: Console Architectures and Beyond

#### Unit 5: Pipeline Mastery (Modules 17--19)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 17](units/unit-5-pipeline-mastery/module-17-build-systems/) | Build Systems and Linking | CMake for recomp, generated + hand-written code, cross-platform builds |
| [Module 18](units/unit-5-pipeline-mastery/module-18-testing-validation/) | Testing and Validation | Trace comparison, screenshot diffing, regression harnesses, common bug patterns |
| [Module 19](units/unit-5-pipeline-mastery/module-19-optimization/) | Optimization | Dead code elimination, flag computation removal, compiler hints, PGO |

#### Unit 6: Console Architectures (Modules 20--25)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 20](units/unit-6-console-architectures/module-20-n64-mips/) | N64 / MIPS | VR4300, N64Recomp toolchain, endianness, TLB-mapped memory |
| [Module 21](units/unit-6-console-architectures/module-21-n64-rsp-rdp/) | N64 Deep Dive: RSP & RDP | RSP microcode, display lists, HLE vs LLE, RT64 backend |
| [Module 22](units/unit-6-console-architectures/module-22-gamecube-ppc/) | GameCube / PowerPC | Gekko, paired singles, GX/TEV pipeline, DOL format, gcrecomp |
| [Module 23](units/unit-6-console-architectures/module-23-wii-broadway/) | Wii / Broadway | Broadway CPU, IOS ARM coprocessor, IPC, Wii Remote shimming |
| [Module 24](units/unit-6-console-architectures/module-24-dreamcast-sh4/) | Dreamcast / SH-4 | SH-4 ISA, delay slots, PowerVR2 tile-based rendering, AICA sound |
| [Module 25](units/unit-6-console-architectures/module-25-ps2-ee/) | PS2 / Emotion Engine | R5900, 128-bit MMI, VU0/VU1 vector units, GS rasterizer, IOP |

#### Unit 7: Advanced Targets (Modules 26--29)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 26](units/unit-7-advanced-targets/module-26-saturn-sh2/) | Saturn / Dual SH-2 | Dual CPUs, VDP1+VDP2 graphics, SCU DSP, SCSP sound, 68K audio CPU |
| [Module 27](units/unit-7-advanced-targets/module-27-xbox-win32/) | Xbox / Win32 | x86 PE executables, NV2A GPU, DirectX 8 shimming, kernel emulation |
| [Module 28](units/unit-7-advanced-targets/module-28-xbox360-xenon/) | Xbox 360 / Xenon PPC | Tri-core PPC, VMX128 SIMD, XEX format, XenonRecomp, Xenos GPU |
| [Module 29](units/unit-7-advanced-targets/module-29-gpu-translation/) | GPU Pipeline Translation | Fixed-function → shaders, texture format conversion, resolution scaling |

#### Unit 8: Extreme Targets and Capstone (Modules 30--32)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 30](units/unit-8-extreme-targets/module-30-ps3-cell/) | PS3 / Cell Broadband Engine | Cell architecture, PPU + SPU recompilation, local store DMA, SPE scheduling |
| [Module 31](units/unit-8-extreme-targets/module-31-multithreaded-recomp/) | Multi-Threaded Recompilation | Dual-CPU, heterogeneous, synchronization, deterministic multi-threaded testing |
| [Module 32](units/unit-8-extreme-targets/module-32-capstone-project/) | Capstone Project | Full end-to-end recompilation of a real binary you choose |

### Semester 3 -- Production Engineering

| Module | Topic | Key Concepts |
|---|---|---|
| [Module 33](units/unit-9-automated-pipelines/module-33-automated-disassembly/) | Automated Disassembly Pipelines | Stage-based pipelines, container extraction, discovery as a committed artifact, batch harnesses |
| [Module 34](units/unit-9-automated-pipelines/module-34-lifting-at-scale/) | Automated Lifting at Scale | Where semantics live, table-driven decoding, front-end reuse, output volume, what counts as a function |
| [Module 35](units/unit-9-automated-pipelines/module-35-ci-for-recomp/) | CI/CD for Recompilation | Testing without shipping the ROM, synthetic fixtures, regression gates, the green badge that tests nothing |
| [Module 36](units/unit-9-automated-pipelines/module-36-config-driven-recomp/) | Configuration-Driven Recompilation | The manifest is the project, hint tables, multi-target builds, configurable escape hatches |
| [Module 37](units/unit-10-quality-correctness/module-37-what-it-works-means/) | What "It Works" Means | The ladder of evidence, harness-produced evidence, silent fallbacks, the ten-minute audit |
| [Module 38](units/unit-10-quality-correctness/module-38-differential-testing/) | Differential Testing and Oracles | Oracle before lifter, bisecting the lifted set, boundary tripwires, a full campaign read commit by commit |
| [Module 39](units/unit-10-quality-correctness/module-39-fuzzing-divergence/) | Fuzzing and Divergence Detection | Differential fuzzing, nested bisection over inputs and code, corpus runs, triage |
| [Module 40](units/unit-10-quality-correctness/module-40-audio-timing/) | Audio and Timing Accuracy | Who advances time, interrupts as the clock, audio deadlines, clock discipline, accuracy levels |
| [Module 41](units/unit-11-performance/module-41-profiling/) | Profiling Recompiled Binaries | 444 of 88,816, choosing a baseline, where the time really goes, build time |
| [Module 42](units/unit-11-performance/module-42-simd/) | SIMD for Lifted Code | Guest vector units to host SIMD, lane semantics, denormals and saturation, microcode |
| [Module 43](units/unit-11-performance/module-43-memory-access/) | Memory Access Optimization | From a switch to the host MMU, MMIO when access is free, endianness, cache |
| [Module 44](units/unit-11-performance/module-44-whole-program-opt/) | Whole-Program Optimization | Compile less, trap stubs, LTO, PGO, function ordering |
| [Module 45](units/unit-12-shipping/module-45-legal/) | Legal Considerations | Ship the tool not the output, licence compatibility, what clean room is not |
| [Module 46](units/unit-12-shipping/module-46-packaging/) | Packaging and Distribution | Input verification, extraction, legible failure, honest status |
| [Module 47](units/unit-12-shipping/module-47-ux-modding/) | UX and Modding Support | Save states and input, cheap vs expensive enhancements, modding by link order |
| [Module 48](units/unit-12-shipping/module-48-semester3-project/) | Semester 3 Project | Ship a recompiled game end to end, and audit your own claims |

### Semester 4 -- Frontiers and Research

| Module | Topic | Key Concepts |
|---|---|---|
| [Module 49](units/unit-13-hybrid/module-49-static-dynamic/) | Static and Dynamic, Together | The spectrum, interception vs fallback, traces feeding static analysis, migration as design |
| [Module 50](units/unit-13-hybrid/module-50-binary-rewriting/) | Binary Rewriting and Patching | RetroWrite, rev.ng, BinRec, LeanBin; LLVM IR vs C; when rewriting beats recompiling |
| [Module 51](units/unit-13-hybrid/module-51-decomp-assisted/) | Decompilation-Assisted Recompilation | What a symbol file buys, matching decomps as ground truth, feeding back |
| [Module 52](units/unit-13-hybrid/module-52-ml-binary-analysis/) | ML for Binary Analysis | Tasks with a checker vs without; evaluating claims, including this course's own |
| [Module 53](units/unit-14-emerging-arch/module-53-four-bit/) | Very Small Targets | A 4-bit CPU, one C function with 6,144 labels, a paging instruction that compiles to nothing |
| [Module 54](units/unit-14-emerging-arch/module-54-bytecode-targets/) | Bytecode Targets | When the "machine code" is a VM; a stack VM without a stack; silent encoding traps |
| [Module 55](units/unit-14-emerging-arch/module-55-undocumented-hardware/) | Undocumented Hardware | Measure, do not assume; assemble the whole address space; classify what is left |
| [Module 56](units/unit-14-emerging-arch/module-56-your-own-frontier/) | Picking Your Own Frontier | Feasibility triage, what makes a target easy or hard, frontiers still open |
| [Module 57](units/unit-15-tooling/module-57-contributing-upstream/) | Contributing Upstream | The project with no code and ten upstream fixes; where the open work is |
| [Module 58](units/unit-15-tooling/module-58-toolkit-design/) | Designing a Toolkit | The toolkit/port line, the second game as the test, automatic registration |
| [Module 59](units/unit-15-tooling/module-59-project-shapes/) | Project Shapes | Nine shapes, each with its own "done" condition -- most need no playable game |
| [Module 60](units/unit-15-tooling/module-60-docs-community/) | Documentation and Community | Write down what you ruled out; commit messages as documentation; credit by name |
| [Module 61](units/unit-16-research/module-61-open-problems/) | Open Problems | Ten unsolved things, each with what a real contribution would look like |
| [Module 62](units/unit-16-research/module-62-research-methods/) | Research Methods | Oracle first, corpus not examples, expect your harness to be the bug |
| [Module 63](units/unit-16-research/module-63-writing-it-up/) | Writing It Up | Picking the form, what a technique writeup contains, writing the retraction |
| [Module 64](units/unit-16-research/module-64-capstone/) | Capstone | Four shapes, auditing your own work, and what the course was about |

---

## Getting Started

1. **Read the syllabus.** The [SYLLABUS.md](SYLLABUS.md) contains the full course roadmap, learning objectives, module dependencies, and lab assignments.

2. **Set up your tools.** Follow the [Tool Setup Guide](docs/tool-setup.md) to install the disassemblers, compilers, and recompilation toolchains used throughout the course.

3. **Start with Module 1.** Work through the units in order -- each module builds on the one before it. No rush. The first 8 modules are all foundations and theory before you recompile anything.

4. **Work the labs.** Each lab lives in `labs/lab-NN/`. Fill in the functions marked `TODO` and run `python -m pytest labs/lab-NN` until it is green.

   78 of the 123 labs have tests. 67 of those ship a reference solution in `labs/lab-NN/solution/` -- read it *after* you have your own version working, since the interesting part is usually where the two differ. The remaining 11 tested labs have optional stretch goals beyond what their tests cover, so there is nothing to compare against; the other 45 are written exercises with no code to run.

   Solutions are generated from `tools/make_solutions.py` and CI checks that every one still passes its lab's tests, so they cannot drift away from the stubs they answer.

---

## Repository Structure

```
recompclass/
  README.md            This file
  SYLLABUS.md          Full course syllabus and schedule
  CONTRIBUTING.md      How to contribute
  LICENSE              MIT License
  docs/
    tool-setup.md      Environment and toolchain setup
    glossary.md        Terminology reference
    recommended-reading.md  Community resources and papers
    architecture-reference/  CPU ISA quick references (12 architectures)
    cheat-sheets/      Tool quick references
  units/
    unit-1-foundations/          Modules 1-5
    unit-2-core-techniques/     Modules 6-8
    unit-3-first-targets/       Modules 9-13
    unit-4-pipeline-essentials/ Modules 14-16
    unit-5-pipeline-mastery/    Modules 17-19
    unit-6-console-architectures/ Modules 20-25
    unit-7-advanced-targets/    Modules 26-29
    unit-8-extreme-targets/     Modules 30-32
    unit-9-automated-pipelines/ Modules 33-36   (Semester 3)
    unit-10-quality-correctness/ Modules 37-40  (Semester 3)
    unit-11-performance/        Modules 41-44   (Semester 3)
    unit-12-shipping/           Modules 45-48   (Semester 3)
    unit-13-hybrid/             Modules 49-52   (Semester 4)
    unit-14-emerging-arch/      Modules 53-56   (Semester 4)
    unit-15-tooling/            Modules 57-60   (Semester 4)
    unit-16-research/           Modules 61-64   (Semester 4)
  labs/                123 hands-on lab exercises
  papers/              Standalone write-ups, not part of the course path
  tools/               Lab scaffolding and the reference-solution generator
```

---

## Community

Have questions about static recompilation, need help debugging a recomp project, or want to discuss the course material? Join the **[sp00nznet recomp Discord](https://discord.gg/CRpzGWZFcu)**.

---

## Contributing

Contributions, corrections, and improvements are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting issues, pull requests, and new lab exercises.

---

## License

This course is released under the [MIT License](LICENSE). You are free to use, modify, and distribute the material with attribution.

---

## How This Course Was Written

Worth stating plainly, because the course asks you to be honest about your own work.

The recompilation projects this course draws on --
[the toolkits and the ports](https://github.com/sp00nznet?tab=repositories) -- are
[Ned Heller (sp00nznet)](https://github.com/sp00nznet)'s, built over years across
30-odd architectures.

The course material itself -- the module prose, the worked examples, the structure --
was **written by Claude (Anthropic)**, working from those repositories, their
documentation and their commit histories, and directed and corrected by Ned throughout.
Where a module cites a number, a file or a bug, it is pointing at real committed work in
a public repository; go read the source rather than trusting the summary. Where a module
is wrong, that is a course bug -- [open an issue](../../issues).

That division is the same one the course teaches: the artifact is the evidence, the
write-up is a claim about it, and the two should be checkable against each other.

---

*Built by [Ned Heller (sp00nznet)](https://github.com/sp00nznet) -- disassemble, lift, recompile, run.*

*This course stands on the shoulders of many contributors to the static recompilation community. Special thanks to [Mr-Wiseguy](https://github.com/Mr-Wiseguy) (N64Recomp, Zelda64Recomp), [Dario Samo](https://github.com/DarioSamo) (RT64), [Skyth](https://github.com/hedge-dev) (XenonRecomp, UnleashedRecomp), [Sajid](https://github.com/hedge-dev) (XenonAnalyse), [rexdex](https://github.com/rexdex) (foundational Xbox 360 recompiler), [arcanite24](https://github.com/arcanite24) (gb-recompiled), and the many porters and contributors who have made this field what it is today.*
