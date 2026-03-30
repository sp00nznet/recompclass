# Static Recompilation: From Theory to Practice

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Course Status](https://img.shields.io/badge/Course-In_Development-orange.svg)](#)
[![Modules](https://img.shields.io/badge/Modules-32-blue.svg)](#)
[![Labs](https://img.shields.io/badge/Labs-50-green.svg)](#)

> A two-semester open course on static binary recompilation -- the art of translating compiled programs from one platform to another at the source level.

---

## About This Course

Static recompilation is the process of disassembling a compiled binary, lifting its instructions into portable C source code, and recompiling that code to run natively on modern hardware -- no runtime emulator required. It is one of the most powerful techniques in software preservation, yet almost no structured learning material exists for it.

This course changes that. Across **8 Units**, **32 Modules**, and **50 Hands-on Labs**, you will go from understanding basic binary formats to recompiling real console games for modern platforms. Every module draws on real-world projects and production toolchains.

**Semester 1** ramps up slowly. Plenty of time to get comfortable reading assembly, using the tools, and understanding the mechanical process of lifting -- all before you touch a real console target. Your first recompilations are the simplest architectures: Game Boy, NES, SNES, GBA, and DOS.

**Semester 2** is where things get serious. N64, GameCube, Wii, Dreamcast, PS2, Saturn, Xbox, Xbox 360, and PS3. Multi-processor systems, GPU pipeline translation, and the hardest targets the community has tackled.

**Author:** [Ned Heller](https://github.com/sp00nznet) (sp00nznet) -- hobbyist and static recompilation practitioner with projects spanning 12 CPU architectures, including N64, SNES, Game Boy, NES, GBA, Xbox, Xbox 360, PS2, PS3, GameCube, Dreamcast, Saturn, Wii, and DOS.

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

---

## Getting Started

1. **Read the syllabus.** The [SYLLABUS.md](SYLLABUS.md) contains the full course roadmap, learning objectives, module dependencies, and lab assignments.

2. **Set up your tools.** Follow the [Tool Setup Guide](docs/tool-setup.md) to install the disassemblers, compilers, and recompilation toolchains used throughout the course.

3. **Start with Module 1.** Work through the units in order -- each module builds on the one before it. No rush. The first 8 modules are all foundations and theory before you recompile anything.

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
  labs/                50 hands-on lab exercises
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

*Built by [Ned Heller (sp00nznet)](https://github.com/sp00nznet) -- disassemble, lift, recompile, run.*

*This course stands on the shoulders of many contributors to the static recompilation community. Special thanks to [Mr-Wiseguy](https://github.com/Mr-Wiseguy) (N64Recomp, Zelda64Recomp), [Dario Samo](https://github.com/DarioSamo) (RT64), [Skyth](https://github.com/hedge-dev) (XenonRecomp, UnleashedRecomp), [Sajid](https://github.com/hedge-dev) (XenonAnalyse), [rexdex](https://github.com/rexdex) (foundational Xbox 360 recompiler), [arcanite24](https://github.com/arcanite24) (gb-recompiled), and the many porters and contributors who have made this field what it is today.*
