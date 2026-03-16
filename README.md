# Static Recompilation: From Theory to Practice

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Course Status](https://img.shields.io/badge/Course-In_Development-orange.svg)](#)

> An open course on static binary recompilation -- the art of translating compiled programs from one platform to another at the source level.

---

## About This Course

Static recompilation is the process of disassembling a compiled binary, lifting its instructions into portable C source code, and recompiling that code to run natively on modern hardware -- no runtime emulator required. It is one of the most powerful techniques in software preservation, yet almost no structured learning material exists for it.

This course changes that. Across **5 Units**, **16 Modules**, and **20 Hands-on Labs**, you will go from understanding basic binary formats to recompiling real console games for modern platforms. Every module draws on real-world projects and production toolchains.

**Author:** [Ned Heller](https://github.com/sp00nznet) (sp00nznet) -- hobbyist and static recompilation practitioner with projects spanning 10 CPU architectures, including N64, SNES, Game Boy, Xbox, Xbox 360, PS2, PS3, GameCube, Dreamcast, and DOS.

---

## Why This Course?

Software preservation is a race against time. Hardware degrades, proprietary platforms disappear, and with them go decades of creative and technical work. Emulation has carried the preservation community far, but it has inherent limits: accuracy costs performance, and each target demands a purpose-built emulator.

Static recompilation offers a fundamentally different approach. Instead of simulating foreign hardware at runtime, we translate programs into native code that runs directly on modern machines. The result is faster, more portable, and often easier to maintain than a full emulator.

Despite its power, the static recompilation community has grown almost entirely through oral tradition -- scattered blog posts, reverse engineering forums, and reading other people's code. This course aims to be the comprehensive, structured resource the community has needed: a single path from foundational theory to shipping real recompiled binaries.

Whether you are a preservationist, a reverse engineer, a systems programmer, or simply someone who wants to understand what happens between "disassemble" and "it runs natively," this course is for you.

---

## Prerequisites

- Solid working knowledge of **C programming** (pointers, structs, bitwise operations)
- Basic **assembly awareness** -- you do not need to be fluent, but you should know what registers, opcodes, and a call stack are
- Comfort with the **command line** (building projects, running scripts, navigating directories)
- A Linux, macOS, or WSL environment with a C compiler and Git installed

---

## Course Map

### Unit 1: Foundations (Modules 1--3)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 1](units/unit1/module01/) | What Is Static Recompilation? | Emulation vs. recompilation, the recomp pipeline, when and why to use static recomp |
| [Module 2](units/unit1/module02/) | Binary Formats and Loaders | ELF, PE, ROM headers, memory maps, entry points, segment layout |
| [Module 3](units/unit1/module03/) | CPU Architectures Overview | Registers, instruction encoding, calling conventions across MIPS, PPC, x86, Z80, 65816, SH-4 |

### Unit 2: First Recompilations (Modules 4--7)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 4](units/unit2/module04/) | Game Boy Recompilation | Z80/SM83 instruction set, ROM banking, tile-based graphics, building a minimal runtime |
| [Module 5](units/unit2/module05/) | SNES Recompilation | 65816 architecture, DMA, Mode 7, co-processors (SuperFX, DSP-1) |
| [Module 6](units/unit2/module06/) | DOS Recompilation | Real-mode x86, interrupt-driven I/O, DOS API shims, segmented memory |
| [Module 7](units/unit2/module07/) | The Indirect Call Problem | Jump tables, function pointers, dynamic dispatch, strategies for unresolved targets |

### Unit 3: Pipeline Deep Dive (Modules 8--10)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 8](units/unit3/module08/) | Disassembly and Analysis | Linear sweep vs. recursive descent, Capstone and Ghidra integration, control flow recovery |
| [Module 9](units/unit3/module09/) | Instruction Lifting | Translating machine instructions to C, semantic preservation, handling flags and condition codes |
| [Module 10](units/unit3/module10/) | Runtime Libraries and Hardware Shims | Graphics (SDL2, D3D, Vulkan), audio, input, OS-level abstraction layers |

### Unit 4: Console Architectures (Modules 11--14)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 11](units/unit4/module11/) | N64 / MIPS Recompilation | MIPS III instruction set, N64Recomp toolchain, RSP/RDP graphics pipeline |
| [Module 12](units/unit4/module12/) | Xbox 360 / PowerPC Recompilation | PPC64 with VMX128, XenonRecomp, XEX format, Xbox 360 GPU shaders |
| [Module 13](units/unit4/module13/) | Xbox / Win32 Recompilation | x86-to-x86 recompilation, DirectX API translation, PE patching and relinking |
| [Module 14](units/unit4/module14/) | GameCube, Dreamcast, and PS2 | PPC (Gekko), SH-4, MIPS R5900 (Emotion Engine), multi-target strategies |

### Unit 5: Extreme Targets (Modules 15--16)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [Module 15](units/unit5/module15/) | PS3 / Cell Broadband Engine | Cell architecture, SPU programs, PPU recompilation, handling heterogeneous cores |
| [Module 16](units/unit5/module16/) | Capstone Project | Full end-to-end recompilation of a real binary, from raw ROM/ISO to native executable |

---

## Getting Started

1. **Read the syllabus.** The [SYLLABUS.md](SYLLABUS.md) contains the full course roadmap, learning objectives, and module dependencies.

2. **Set up your tools.** Follow the [Tool Setup Guide](docs/tool-setup.md) to install the disassemblers, compilers, and recompilation toolchains used throughout the course.

3. **Start with Module 1.** Work through the units in order -- each module builds on the one before it.

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
  units/
    unit1/             Foundations (Modules 1-3)
    unit2/             First Recompilations (Modules 4-7)
    unit3/             Pipeline Deep Dive (Modules 8-10)
    unit4/             Console Architectures (Modules 11-14)
    unit5/             Extreme Targets (Modules 15-16)
  labs/                Hands-on lab exercises
  examples/            Reference code and sample binaries
```

---

## Contributing

Contributions, corrections, and improvements are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting issues, pull requests, and new lab exercises.

---

## License

This course is released under the [MIT License](LICENSE). You are free to use, modify, and distribute the material with attribution.

---

*Built by [Ned Heller (sp00nznet)](https://github.com/sp00nznet) -- disassemble, lift, recompile, run.*

*This course stands on the shoulders of many contributors to the static recompilation community. Special thanks to [Mr-Wiseguy](https://github.com/Mr-Wiseguy) (N64Recomp, Zelda64Recomp), [Dario Samo](https://github.com/DarioSamo) (RT64), [Skyth](https://github.com/hedge-dev) (XenonRecomp, UnleashedRecomp), [Sajid](https://github.com/hedge-dev) (XenonAnalyse), [rexdex](https://github.com/rexdex) (foundational Xbox 360 recompiler), [arcanite24](https://github.com/arcanite24) (gb-recompiled), and the many porters and contributors who have made this field what it is today.*
