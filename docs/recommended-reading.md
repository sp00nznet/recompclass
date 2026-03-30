# Recommended Reading and Resources

A curated list of books, papers, tools, communities, and architecture references relevant to static recompilation. Items marked with [essential] are directly used or referenced in the course labs.

---

## Books

**"Reverse Engineering for Beginners" by Dennis Yurichev** [essential]
Also known as "RE4B." A free, comprehensive introduction to reverse engineering covering x86, ARM, and MIPS. Excellent for understanding disassembly patterns, calling conventions, and compiler output. Available as a free PDF from the author's website (beginners.re).

**"Computer Systems: A Programmer's Perspective" by Randal E. Bryant and David R. O'Hallaron** [essential]
The standard reference for understanding how programs map to hardware: memory layout, linking, machine-level representations of C code, and processor architecture. Chapters on machine-level programming and linking are particularly relevant.

**"Engineering a Compiler" by Keith D. Cooper and Linda Torczon**
Covers compiler construction from front end to back end. The chapters on intermediate representations, control flow analysis, and code generation directly apply to building a recompiler backend.

**"Compilers: Principles, Techniques, and Tools" by Aho, Lam, Sethi, and Ullman**
The classic "Dragon Book." More theoretical than Cooper/Torczon but provides deep coverage of optimization, data flow analysis, and code generation that advanced recompiler work benefits from.

**"Linkers and Loaders" by John R. Levine**
Explains executable formats (ELF, PE, COFF), symbol resolution, relocation, and dynamic linking. Essential background for writing binary loaders in a recompiler pipeline.

---

## Papers and Technical Documentation

**"QEMU, a Fast and Portable Dynamic Translator" by Fabrice Bellard**
The foundational paper on QEMU's approach to binary translation using a tiny code generator (TCG). While QEMU is a dynamic translator, the techniques for instruction lifting and intermediate representation are directly applicable to static recompilation.

**"A Retargetable Static Binary Translator for the ARM Architecture" (various authors)**
Academic work on static binary translation challenges including indirect branch resolution, code discovery, and self-modifying code. Search for this in IEEE or ACM digital libraries.

**"Scalable Validation of Binary Lifters" (various authors)**
Covers techniques for verifying that lifted/translated code is semantically equivalent to the original. Relevant to building confidence that your recompiler output is correct.

**QEMU Technical Documentation**
The QEMU wiki and source tree document TCG (Tiny Code Generator) internals, the guest-to-IR-to-host pipeline, and per-architecture frontends. Valuable as a reference implementation of instruction semantics.

---

## Online Resources

**Ghidra Documentation and Training**
Ghidra ships with built-in help and a "GhidraClass" directory containing NSA-authored training materials. The Ghidra GitHub repository also has extensive documentation on its decompiler, scripting API (Java and Python), and analysis engines.

**Capstone Engine Documentation**
The Capstone website (capstone-engine.org) provides API references for C and Python. The GitHub repository includes example scripts for each supported architecture.

**Compiler Explorer (godbolt.org)** [essential]
An online tool that shows compiler output for C/C++ code in real time. Invaluable for understanding what assembly your generated C code produces and for verifying that your lifted code compiles to reasonable output.

**OSDev Wiki**
Community wiki covering low-level systems programming: executable formats, calling conventions, memory management, and hardware programming. Useful as a quick reference when encountering unfamiliar system-level concepts.

**Wikipedia ISA Articles**
The Wikipedia pages for MIPS, PowerPC, x86, ARM, SH-4, and other architectures provide good high-level summaries of register sets, instruction encoding, and addressing modes.

---

## Community

**N64Recomp** (Mr-Wiseguy) -- [github.com/N64Recomp/N64Recomp](https://github.com/N64Recomp/N64Recomp)
The N64 static recompilation toolchain and its community are a major reference point for this course. The project demonstrates a complete pipeline: ROM loading, MIPS disassembly, C code generation, and runtime library. The [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) project is the flagship example. Follow the project's GitHub and Discord for discussions. Wiseguy and Dario discussed the project's design on [Software Engineering Daily (Oct 2024)](https://softwareengineeringdaily.com/2024/10/02/n64-recompiled-with-dario-and-wiseguy/).

**RT64** (Dario Samo) -- [github.com/rt64/rt64](https://github.com/rt64/rt64)
The modern N64 rendering backend, with accuracy-first design and no per-game workarounds.

**XenonRecomp / UnleashedRecomp** (Skyth, Sajid, Hyper at hedge-dev) -- [github.com/hedge-dev/XenonRecomp](https://github.com/hedge-dev/XenonRecomp)
Xbox 360 static recompilation toolchain. UnleashedRecomp (Sonic Unleashed PC port) is the showcase project.

**rexdex/recompiler** -- [github.com/rexdex/recompiler](https://github.com/rexdex/recompiler)
The foundational Xbox 360 static recompiler that inspired later work.

**gb-recompiled** (arcanite24 / Brandon G. Neri) -- [github.com/arcanite24/gb-recompiled](https://github.com/arcanite24/gb-recompiled)
Game Boy static recompiler with advanced indirect jump resolution. Successfully processes 98.9% of the tested ROM library.

**RexGlueSDK** (tomcl7) -- [github.com/rexglue/rexglue-sdk](https://github.com/rexglue/rexglue-sdk)
Xbox 360 recompilation runtime with growing wiki documentation.

**Gilgamesh** (Andrea Orru) -- [github.com/AndreaOrru/gilgamesh](https://github.com/AndreaOrru/gilgamesh)
SNES reverse engineering toolkit with static recompilation support for the 65C816.

**PS2Recomp** (ran-j) -- [github.com/ran-j/PS2Recomp](https://github.com/ran-j/PS2Recomp)
PS2 ELF static recompiler (MIPS R5900). Early development.

**ReadOnlyMemo** -- [readonlymemo.com](https://readonlymemo.com/decompilation-projects-and-n64-recompiled-list/)
Maintains an updated list of decompilation and recompilation projects across all platforms.

**sp00nznet recomp Discord** -- [discord.gg/CRpzGWZFcu](https://discord.gg/CRpzGWZFcu)
The community Discord for this course and sp00nznet's recompilation projects. A place to discuss debugging, recomp work, course material, and connect with others in the static recompilation space.

**Static Recompilation Discord Communities**
Several Discord servers focus on console reverse engineering and recompilation work. Search for communities around specific consoles (N64, PS2, GameCube) or general reverse engineering.

**Emulation Development Communities**
The broader emulation development community (forums, Discord servers, subreddits) has decades of accumulated knowledge about console hardware, ROM formats, and software behavior that directly supports recompilation work.

---

## Architecture References (ISA Manuals)

Understanding the guest ISA is a prerequisite for writing a lifter. The following manuals are the authoritative references for architectures covered in this course:

**SM83 (Game Boy / Game Boy Color)**
The SM83 is a Sharp CPU loosely based on the Z80/8080. The "Game Boy CPU Manual" and Pan Docs are the standard community references since no official Sharp datasheet is widely available.

**65816 (SNES)**
The WDC 65C816 datasheet from Western Design Center is the official reference. The "65816 Programming Manual" covers the instruction set, addressing modes, and bank-switching behavior.

**MIPS (N64, PS1, PS2)**
"MIPS IV Instruction Set" and "MIPS R4000 User's Manual" from MIPS Technologies. The VR4300 (N64) is a MIPS III/IV variant. The Emotion Engine (PS2) extends MIPS III with multimedia instructions.

**PowerPC (GameCube, Wii, Xbox 360, PS3 PPU)**
"PowerPC Microprocessor Family: The Programming Environments Manual" from IBM/Freescale. The Gekko (GameCube) and Broadway (Wii) are based on the 750 series. The Xenon (Xbox 360) and Cell PPU (PS3) are 64-bit PowerPC variants.

**x86 / x86-64 (Original Xbox, PC)**
"Intel 64 and IA-32 Architectures Software Developer's Manual" (the multi-volume SDM). The original Xbox uses a Pentium III-class x86 CPU.

**SH-4 (Dreamcast)**
"SH-4 Software Manual" from Hitachi/Renesas. Covers the instruction set, pipeline behavior, and the FPU -- all necessary for Dreamcast recompilation.

**Cell Broadband Engine (PS3: PPU + SPU)**
"Cell Broadband Engine Programming Handbook" and "SPU ISA" from IBM. The SPU has a unique 128-register SIMD architecture with its own instruction set entirely distinct from the PPU's PowerPC ISA.

---

## sp00nznet Projects as Learning References

The following projects by [sp00nznet](https://github.com/sp00nznet) (Ned Heller) serve as practical, real-world examples of static recompilation at various stages of development. They are referenced throughout the course labs.

### Recompilation Toolkits

**gb-recompiled** -- [github.com/sp00nznet/gb-recompiled](https://github.com/sp00nznet/gb-recompiled)
A recompiler for the Game Boy's SM83 CPU. A good starting point for learning because the SM83 has a small instruction set and simple memory model, making the full pipeline easy to follow.

**snesrecomp** -- [github.com/sp00nznet/snesrecomp](https://github.com/sp00nznet/snesrecomp)
A recompiler for the 65816 processor used in the SNES. Demonstrates handling of bank switching, variable-width registers (8/16-bit accumulator and index modes), and the 65816's many addressing modes.

**gbarecomp** -- [github.com/sp00nznet/gbarecomp](https://github.com/sp00nznet/gbarecomp)
A static recompilation toolkit for the Game Boy Advance (ARM7TDMI). Covers ARM/Thumb interworking, BIOS HLE, and tile/bitmap mode graphics shimming.

**pcrecomp** -- [github.com/sp00nznet/pcrecomp](https://github.com/sp00nznet/pcrecomp)
A static recompiler for DOS/PC x86 targets. Handles real-mode segmented memory, DOS API shimming, and interrupt-driven I/O translation.

**gcrecomp** -- [github.com/sp00nznet/gcrecomp](https://github.com/sp00nznet/gcrecomp)
A static recompiler targeting the PowerPC 750 (Gekko/Broadway) ISA, relevant to GameCube and Wii titles. Demonstrates DOL loading, PowerPC disassembly, CFG construction, and C code generation.

**dcrecomp** -- [github.com/sp00nznet/dcrecomp](https://github.com/sp00nznet/dcrecomp)
A static recompiler for the SH-4 architecture (Dreamcast/Naomi). Notable for its handling of delay slots and the SH-4's compact 16-bit instruction encoding.

**xboxrecomp** -- [github.com/sp00nznet/xboxrecomp](https://github.com/sp00nznet/xboxrecomp)
A static recompiler targeting the original Xbox (x86-based). Covers XBE loading, x86 disassembly, and the particular challenges of recompiling x86 code (variable-length instructions, complex flag behavior).

**ps3recomp** -- [github.com/sp00nznet/ps3recomp](https://github.com/sp00nznet/ps3recomp)
PS3 runtime libraries and recompilation support. Showcases the unique challenges of the Cell architecture: PPU (PowerPC) + SPU recompilation, 128-bit register file, local store memory model, and channel-based I/O.

**360tools** -- [github.com/sp00nznet/360tools](https://github.com/sp00nznet/360tools)
Xbox 360 analysis and recompilation utilities. Used alongside XenonRecomp for Xenon PPC targets.

**neogeorecomp** -- [github.com/sp00nznet/neogeorecomp](https://github.com/sp00nznet/neogeorecomp)
Neo Geo MVS/AES runtime for 68000-based arcade hardware recompilation.

**MidwayRecomp** -- [github.com/sp00nznet/MidwayRecomp](https://github.com/sp00nznet/MidwayRecomp)
MIPS-IV recompiler for Midway arcade hardware. Demonstrates recompilation of arcade board targets beyond home consoles.

**genrecomp** -- [github.com/sp00nznet/genrecomp](https://github.com/sp00nznet/genrecomp)
Genesis/Mega Drive recompilation toolkit.

### Game-Specific Recompilation Projects

These repositories demonstrate end-to-end recompilation of specific titles and serve as case studies:

**flow** -- [github.com/sp00nznet/flow](https://github.com/sp00nznet/flow)
First native PC port of thatgamecompany's flOw (PS3 → C++). Over 91,000 PowerPC functions lifted to C++, ~190 MB of generated source. The most ambitious PS3 recomp project to date.

**mk** -- [github.com/sp00nznet/mk](https://github.com/sp00nznet/mk)
Super Mario Kart (SNES 65C816 → native). A complete SNES recompilation case study.

**mariopaint** -- [github.com/sp00nznet/mariopaint](https://github.com/sp00nznet/mariopaint)
Mario Paint (SNES → native PC).

**racer** -- [github.com/sp00nznet/racer](https://github.com/sp00nznet/racer)
Star Wars Episode I: Racer (N64 → native).

**Rampage** -- [github.com/sp00nznet/Rampage](https://github.com/sp00nznet/Rampage)
Rampage World Tour and Rampage 2 (N64 → native).

**crazytaxi** -- [github.com/sp00nznet/crazytaxi](https://github.com/sp00nznet/crazytaxi)
Crazy Taxi (Dreamcast SH-4 → x86-64).

**ww** -- [github.com/sp00nznet/ww](https://github.com/sp00nznet/ww)
GameCube game static recompilation.

**burnout3** -- [github.com/sp00nznet/burnout3](https://github.com/sp00nznet/burnout3)
Burnout 3: Takedown (Xbox → Windows x86-64).

**fallout1-re** / **fallout2-re** -- [github.com/sp00nznet/fallout1-re](https://github.com/sp00nznet/fallout1-re), [github.com/sp00nznet/fallout2-re](https://github.com/sp00nznet/fallout2-re)
DOS-era Fallout reverse engineering and recompilation projects.

These repositories illustrate different design decisions and tradeoffs across a range of guest architectures. Studying how each one handles binary loading, disassembly, control flow analysis, and code generation will reinforce the concepts taught in the course.
