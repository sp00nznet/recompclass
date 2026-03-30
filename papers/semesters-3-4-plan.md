# Semesters 3 and 4: Planning Document

**Status**: Planning only — not yet integrated into the course repo.

This document outlines the proposed structure for the second half of a four-semester static recompilation curriculum. Semesters 1 and 2 cover theory through advanced console architectures. Semesters 3 and 4 shift focus to **production-grade tooling, automation, real-world shipping, and emerging frontiers**.

---

## Design Principles

1. **Semesters 1-2 teach how to recompile.** Semesters 3-4 teach how to ship, scale, and push the boundaries.
2. **Semester 3** focuses on the engineering that turns a proof-of-concept into a releasable product: automated pipelines, CI/CD, quality assurance, performance engineering, and community distribution.
3. **Semester 4** focuses on frontiers: unsolved problems, hybrid techniques, tooling contributions, and original research. Students produce publishable work or contribute to open-source projects.
4. **Both semesters lean heavily on real projects** — students work with actual game binaries and contribute to actual recompilation toolchains.

---

## Semester 3: Production Engineering (Modules 33–48)

### Unit 9 — Automated Pipelines (Modules 33–36)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 33 | Automated Disassembly Pipelines | Batch ROM processing, parallel disassembly, function database construction, automated symbol import from decomp projects |
| 34 | Automated Lifting at Scale | Template-based lifter generation, ISA description languages (SLEIGH, GDSL), generating lifters from machine-readable ISA specs |
| 35 | CI/CD for Recompilation Projects | GitHub Actions/GitLab CI for recomp builds, automated regression testing, binary diffing in CI, ROM test suites |
| 36 | Configuration-Driven Recompilation | TOML/YAML project descriptors (N64Recomp's .recomp.toml pattern), declarative pipeline configuration, multi-target builds from single config |

**Unit 9 Capstone Lab**: Build a CI pipeline that takes a ROM as input, runs disassembly, lifting, compilation, and regression testing, and produces a native binary plus a test report.

---

### Unit 10 — Quality and Correctness (Modules 37–40)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 37 | Advanced Trace Comparison | Instruction-level trace diffing, trace compression, statistical divergence detection, trace-guided debugging |
| 38 | Fuzzing Recompiled Binaries | Input fuzzing for game state, differential fuzzing (emulator vs. recomp), coverage-guided testing, crash triage |
| 39 | Formal Verification Techniques | Property-based testing for lifters, SMT-based equivalence checking for instruction semantics, bounded model checking for flag computation |
| 40 | Audio and Timing Accuracy | Audio pipeline recompilation (APU, SPU, SCSP), sample-rate conversion, frame timing and vsync, input latency measurement |

**Unit 10 Capstone Lab**: Build a differential fuzzer that runs randomized inputs through both an emulator and a recompiled binary, detecting the first divergence and generating a minimal reproducer.

---

### Unit 11 — Performance Engineering (Modules 41–44)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 41 | Profiling Recompiled Binaries | perf, VTune, Instruments on recompiled code, identifying hot paths in generated C, profiling generated vs. hand-written code |
| 42 | SIMD Optimization for Lifted Code | Translating guest SIMD (VMX, VU, MMI, NEON) to host SIMD (SSE/AVX/NEON), auto-vectorization of scalar lifts, intrinsic selection |
| 43 | Memory Access Optimization | Cache-friendly memory layout for recompiled games, TLB pressure reduction, memory pool design for guest address spaces |
| 44 | Link-Time and Whole-Program Optimization | Selective LTO for recomp projects, profile-guided optimization (PGO) on generated code, function ordering, dead function elimination at scale |

**Unit 11 Capstone Lab**: Profile a recompiled N64 or GameCube title, identify the top 10 hot functions, and apply targeted optimizations that produce measurable speedup.

---

### Unit 12 — Shipping and Distribution (Modules 45–48)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 45 | Legal Considerations | Clean-room analysis, ROM distribution legality, patch-based distribution (ship the recompiler, not the ROM), license compliance (GPL in shims) |
| 46 | Packaging and Distribution | Asset extraction pipelines, user-provides-ROM workflows, installer design, Steam/itch.io/Flatpak distribution, update mechanisms |
| 47 | User Experience and Modding Support | Resolution scaling, widescreen hacks, controller remapping, mod hooks in recompiled code, save file compatibility |
| 48 | Semester 3 Project: Ship a Recompiled Game | Full end-to-end: select a title, recompile it, test it, package it, write documentation, and produce a distributable build that a non-technical user can run |

---

## Semester 4: Frontiers and Research (Modules 49–64)

### Unit 13 — Hybrid Techniques (Modules 49–52)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 49 | Static + Dynamic Hybrid Recompilation | Using JIT fallback for unresolvable code, lazy static recompilation, runtime-guided static analysis |
| 50 | Binary Rewriting and Patching | RetroWrite, rev.ng, BinRec approaches, rewriting binaries in-place vs. full recompilation, binary patching for bug fixes |
| 51 | Decompilation-Assisted Recompilation | Leveraging decomp projects (SM64, OoT, TWW) as ground truth, hybrid decomp/recomp pipelines, type recovery from decomp |
| 52 | Machine Learning for Binary Analysis | ML-based function boundary detection, learned instruction semantics, neural decompilation, embedding-based code similarity |

---

### Unit 14 — Emerging Architectures (Modules 53–56)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 53 | PSP / Allegrex (MIPS) | PSP recompilation, VFPU vector unit, media engine coprocessor, PSP homebrew scene tooling |
| 54 | Nintendo DS / ARM9+ARM7 | Dual-CPU ARM recompilation, 2D/3D GPU (NDS hardware renderer), touchscreen input shimming |
| 55 | PS Vita / ARM Cortex-A9 | ARMv7 recompilation, vita-specific GPU (SGX543MP4+), encrypted binary handling |
| 56 | Nintendo 3DS / ARM11+ARM9 | Dual ARM recompilation, stereoscopic 3D rendering, PICA200 GPU command translation |

---

### Unit 15 — Tooling Contributions (Modules 57–60)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 57 | Contributing to N64Recomp | Codebase walkthrough, adding a new game support, contributing overlays, RSP microcode support |
| 58 | Contributing to XenonRecomp | Codebase walkthrough, adding VMX128 instruction support, Xenos GPU improvements |
| 59 | Building a New Recompiler Framework | Architecture-agnostic design patterns, plugin-based ISA frontends, shared IR design, code generation backends |
| 60 | Ghidra and Capstone Extensions | Writing Ghidra processors for custom ISAs, Capstone architecture modules, analysis scripts for recomp pipelines |

---

### Unit 16 — Original Research and Capstone (Modules 61–64)

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| 61 | Writing a Technical Paper | Structure, methodology, related work survey, reproducibility, publishing venues (workshops, conferences, arXiv) |
| 62 | Open Problems in Static Recompilation | Self-modifying code, JIT-compiled guest code, encrypted binaries, anti-tamper/DRM, streaming/cloud targets |
| 63 | The Future of Preservation | Long-term archival formats, institutional preservation (libraries, museums), legal frameworks, community sustainability |
| 64 | Capstone Research Project | Original research contribution: new architecture support, novel technique, tool contribution, or published paper |

---

## Lab Planning

Semesters 3-4 would add approximately 40-50 new labs (Labs 51-100), continuing the hands-on pattern from semesters 1-2. Key lab types:

**Semester 3 labs** focus on automation and production:
- CI/CD pipeline construction
- Automated regression testing
- Differential fuzzing harnesses
- Profiling and optimization workflows
- Asset extraction and packaging tools

**Semester 4 labs** focus on contribution and research:
- Patches to real open-source recompilation tools
- New architecture support in existing frameworks
- Reproduction of published techniques
- Original experimental work

---

## Architecture Coverage: Full 4-Semester Map

| Semester | Architectures | Focus |
|----------|--------------|-------|
| 1 | SM83, 6502, 65816, ARM7TDMI, x86-16 | Foundations + simple targets |
| 2 | MIPS, PPC, SH-4, R5900, SH-2, x86-32, Xenon PPC, Cell | Complex consoles |
| 3 | (Same as 1-2, applied at production scale) | Engineering + shipping |
| 4 | Allegrex (MIPS), ARM9/ARM7, ARM Cortex-A9, ARM11, custom ISAs | Handhelds + emerging + research |

Total unique architectures by end of semester 4: **16+** (adding PSP, DS, Vita, 3DS architectures).

---

## Dependencies on Semesters 1-2

Semesters 3-4 assume completion of the full semester 1-2 curriculum. Specific prerequisites:

- **Unit 9** (Automated Pipelines) requires Module 16 (Semester 1 Project) and Module 17 (Build Systems)
- **Unit 10** (Quality) requires Module 18 (Testing and Validation)
- **Unit 11** (Performance) requires Module 19 (Optimization)
- **Unit 13** (Hybrid Techniques) requires all of Semester 2 console modules
- **Unit 14** (Emerging Architectures) requires Unit 3 (First Targets) + Unit 6 (Console Architectures)
- **Unit 15** (Tooling Contributions) requires Module 32 (Capstone Project)

---

## Open Questions

1. **Pacing**: Should semesters 3-4 also be 16 modules each (32 weeks), or could they be condensed to 12 modules each given that students are now experienced?
2. **Handheld focus**: PSP, DS, Vita, 3DS are included in semester 4 but could be swapped for other platforms (Wii U, Switch, mobile ARM). Community interest should drive selection.
3. **Research component**: Module 64's capstone research project is ambitious. Should this be a solo project or a collaborative one?
4. **Legal module placement**: Module 45 (Legal Considerations) could arguably come earlier. Students should understand distribution legality before they ship anything.
5. **Integration with semesters 1-2**: When semesters 3-4 are finalized, the SYLLABUS.md dependency map, pacing schedule, and README should be updated to reflect the full 4-semester structure. The current "two-semester" framing throughout the repo will need revision.

---

*This is a planning document. No course content has been written for semesters 3-4 yet. The next step after cleaning up semesters 1-2 is to finalize this outline, get feedback, and begin writing modules.*
