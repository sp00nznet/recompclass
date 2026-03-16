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

**N64Recomp Community**
The N64 static recompilation project and its community are a major reference point for this course. The project demonstrates a complete pipeline: ROM loading, MIPS disassembly, C code generation, and runtime library. Follow the project's GitHub repository and associated Discord server for discussions.

**Static Recompilation Discord Communities**
Several Discord servers focus on console reverse engineering and recompilation work. These are good places to ask questions, share progress, and learn from others working on similar projects. Search for communities around specific consoles (N64, PS2, GameCube) or general reverse engineering.

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

The following projects by sp00nznet (Ned Heller) serve as practical, real-world examples of static recompilation at various stages of development. They are referenced throughout the course labs:

**ppc750-recomp**
A static recompiler targeting the PowerPC 750 (Gekko/Broadway) ISA, relevant to GameCube and Wii titles. Demonstrates DOL loading, PowerPC disassembly, CFG construction, and C code generation.

**sh4-recomp**
A static recompiler for the SH-4 architecture (Dreamcast). Notable for its handling of delay slots and the SH-4's compact 16-bit instruction encoding (SH-2 compat mode).

**spu-recomp**
A static recompiler for the Cell SPU. Showcases the unique challenges of the SPU architecture: 128-bit register file, local store memory model, and channel-based I/O.

**sm83-recomp**
A recompiler for the Game Boy's SM83 CPU. A good starting point for learning because the SM83 has a small instruction set and simple memory model, making the full pipeline easy to follow.

**65816-recomp**
A recompiler for the 65816 processor used in the SNES. Demonstrates handling of bank switching, variable-width registers (8/16-bit accumulator and index modes), and the 65816's many addressing modes.

**xb-recomp**
A static recompiler targeting the original Xbox (x86-based). Covers XBE loading, x86 disassembly, and the particular challenges of recompiling x86 code (variable-length instructions, complex flag behavior, segmented legacy).

These repositories illustrate different design decisions and tradeoffs across a range of guest architectures. Studying how each one handles binary loading, disassembly, control flow analysis, and code generation will reinforce the concepts taught in the course.
