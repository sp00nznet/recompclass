# Glossary of Static Recompilation Terms

A reference of key terminology used throughout this course. Definitions are written in the context of static recompilation work rather than general computer science.

---

**Basic Block** — A straight-line sequence of instructions with exactly one entry point and one exit point. Basic blocks are the fundamental unit of control flow analysis and the building blocks of a CFG.

**Binary Translation** — The process of converting machine code from one ISA to another. Static binary translation performs this ahead of time on the entire binary, whereas dynamic binary translation does it at runtime.

**Calling Convention** — The rules governing how functions receive parameters and return values at the machine level (e.g., which registers hold arguments, who saves/restores registers, stack alignment). Correctly modeling calling conventions is essential when generating recompiled code that interacts with a native runtime.

**CFG (Control Flow Graph)** — A directed graph where each node is a basic block and each edge represents a possible flow of execution (branches, falls-through, calls). Building an accurate CFG is typically the first major step in a static recompiler pipeline.

**Code Generation** — The phase of a recompiler that emits target-architecture source code or machine code from the analyzed intermediate representation. This is sometimes called the "backend" of the recompiler.

**Context Struct** — A C/C++ structure that models the guest CPU's register file and relevant processor state. Recompiled functions typically receive a pointer to a context struct so they can read and write guest registers.

**Cross-Compilation** — Compiling code on one platform to produce binaries for a different platform. In static recompilation, the generated C code is cross-compiled from the host to produce a native executable that reimplements the guest binary's behavior.

**Delay Slot** — An instruction slot immediately following a branch instruction that executes before the branch takes effect. Common on MIPS and SH-4. A recompiler must account for delay slots to preserve correct program behavior.

**Disassembly** — The process of converting raw machine code bytes back into human-readable assembly mnemonics. Disassembly is the first step in understanding a binary and feeds into the lifter.

**Dispatch Table** — A lookup structure (often a function pointer array) used at runtime to resolve indirect calls or jumps to the correct recompiled function. Dispatch tables bridge the gap between guest addresses and host function pointers.

**DMA (Direct Memory Access)** — A hardware mechanism that transfers data between memory regions (or between memory and peripherals) without CPU involvement. Recompilers targeting consoles like the PS2 or PS3 must shim or emulate DMA transfers.

**DOL** — The executable format used by Nintendo GameCube and Wii. A DOL file contains code and data sections with load addresses, making it relatively straightforward to parse for recompilation.

**Dynamic Recompilation (JIT)** — A technique that translates guest machine code to host machine code at runtime, one block or trace at a time, caching the results. Contrasted with static recompilation, which performs translation ahead of time.

**ELF (Executable and Linkable Format)** — A standard executable format used on Linux, many consoles, and embedded systems. ELF files contain section headers, symbol tables, and relocation info that are valuable inputs to a recompiler.

**Emulation** — Reproducing the behavior of one system on another. Static recompilation is a form of emulation that trades runtime interpretation overhead for ahead-of-time translation, while still relying on a runtime library to emulate hardware.

**Endianness** — The byte order used to store multi-byte values in memory. Many console CPUs are big-endian (PowerPC, MIPS on N64) while x86 hosts are little-endian, so a recompiler must insert byte-swap operations where necessary.

**Flag Computation** — The process of computing CPU status flags (zero, carry, overflow, negative) that result from arithmetic and logic operations. Recompilers must decide whether to eagerly compute all flags or lazily compute them only when a subsequent instruction actually reads them.

**Function Boundary Detection** — The analysis step that determines where functions begin and end in a binary. Techniques include recursive descent from known entry points, symbol table parsing, and heuristic pattern matching.

**Hardware Shim** — A host-side implementation that stands in for a piece of guest hardware. For example, a shim for a console's audio hardware would accept the same register writes the original code performs and translate them into host audio API calls.

**HLE (High-Level Emulation)** — Replacing low-level guest code (such as OS calls or library functions) with equivalent high-level host implementations rather than recompiling the original instructions. HLE can drastically simplify recompilation of OS and library code.

**Indirect Call/Jump** — A branch whose target address is computed at runtime (e.g., jumping through a register or a function pointer). Indirect control flow is one of the hardest problems in static recompilation because the target set may not be fully known at analysis time.

**Instruction Lifting** — Translating a single guest instruction into an equivalent sequence of operations in the target language or intermediate representation. Lifting is the core per-instruction work of a recompiler.

**Interpreter Fallback** — A mechanism that falls back to an instruction-level interpreter for code regions that the static recompiler cannot handle (e.g., self-modifying code or insufficiently analyzed indirect jumps).

**ISA (Instruction Set Architecture)** — The specification of a processor's machine language, including opcodes, register set, addressing modes, and encoding. Each recompiler targets a specific guest ISA.

**Kernel Shim** — A host-side implementation of guest operating system or kernel services. When recompiled code makes a syscall, the kernel shim intercepts it and provides equivalent functionality using the host OS.

**Lifter** — The component of a recompiler that converts disassembled guest instructions into target code or an intermediate representation. "Lifter" and "instruction lifting" are standard terms in the binary translation community.

**Linear Sweep** — A disassembly strategy that decodes instructions sequentially from a starting address. Simple but prone to errors when data is interleaved with code. Contrast with recursive descent.

**LLE (Low-Level Emulation)** — Emulating hardware and software at the register-transfer or instruction level rather than replacing it with high-level equivalents. LLE is more accurate but more complex than HLE.

**Local Store (SPU)** — The 256 KB private memory of each Synergistic Processing Unit on the Cell processor. SPU programs run entirely from local store, and a recompiler must model this memory space and DMA transfers to/from main memory.

**Memory Bus** — The communication pathway between the CPU, memory, and peripherals. Console memory buses often have specific timing and width characteristics that affect how a recompiler must model memory accesses.

**Memory-Mapped I/O (MMIO)** — Hardware registers accessed through normal memory read/write operations at specific addresses. A recompiler's runtime must intercept accesses to MMIO regions and route them to the appropriate hardware shim.

**Native Code** — Machine code that runs directly on the host CPU without interpretation or translation at runtime. The output of a static recompiler is native code (or C code that compiles to native code).

**NID (PS3)** — A numeric identifier used by the PS3's dynamic linker to resolve imported and exported library functions. NIDs are hashed from function name strings and are essential for identifying HLE targets in PS3 recompilation.

**Opcode** — The portion of a machine instruction that specifies the operation to perform. The opcode is the primary input to the lifter's instruction dispatch logic.

**Overlay** — A code segment that is loaded into a shared memory region on demand, replacing a previous overlay. Common on memory-constrained platforms like the N64. Overlays require special handling in a recompiler because the same address can contain different code at different times.

**PE (Portable Executable)** — The executable format used on Windows and the original Xbox (as XBE wraps PE structures). Understanding PE headers, sections, and imports is necessary for recompiling Windows or Xbox binaries.

**Pipeline (Recomp)** — The end-to-end sequence of stages in a static recompiler: binary loading, disassembly, CFG construction, lifting, optimization, and code generation. Each stage feeds its output into the next.

**PPU (Cell)** — The Power Processing Unit, the main general-purpose core of the Cell Broadband Engine used in the PS3. PPU code is PowerPC-based and is typically the primary recompilation target for PS3 projects.

**Recursive Descent** — A disassembly strategy that follows control flow edges (branches, calls) to discover code. More accurate than linear sweep for binaries with embedded data, but can miss code only reachable through indirect jumps.

**Register Model** — The way a recompiler represents the guest CPU's registers in the generated code. Common approaches include fields in a context struct, local variables, or mapping guest registers to host registers.

**Recompiler** — A tool that translates a binary program from one ISA (the guest) into equivalent source code or machine code for another ISA (the host). In this course, "recompiler" always refers to a static (ahead-of-time) recompiler unless otherwise noted.

**ROM** — A read-only memory image, typically a dump of a game cartridge or disc. ROMs are the primary input to many recompilation projects.

**Runtime Library** — The host-side support code that recompiled functions link against. The runtime typically provides the context struct, memory access helpers, hardware shims, and any interpreter fallback.

**SELF (Signed ELF, PS3)** — The encrypted and signed executable format used on the PS3. SELF files must be decrypted before they can be disassembled and recompiled; the inner payload is a standard ELF.

**SPU (Synergistic Processing Unit)** — One of the six available co-processors on the Cell Broadband Engine. SPUs have their own ISA, register file (128 x 128-bit), and local store, requiring a separate recompiler and runtime from the PPU.

**Static Recompilation** — The technique of translating an entire guest binary into host source code or machine code ahead of time, producing a standalone native executable. The central subject of this course.

**Syscall** — A software interrupt that requests a service from the guest operating system kernel. Recompiled code that performs syscalls must be intercepted and routed to a kernel shim or HLE implementation.

**VMX/AltiVec** — The SIMD (Single Instruction, Multiple Data) extension for PowerPC processors, used on GameCube, Wii, and PS3. Recompiling VMX instructions often requires mapping them to host SIMD equivalents (SSE, AVX, or NEON).

**VTable** — A table of function pointers used to implement virtual method dispatch in C++ programs. VTables are a common source of indirect calls that a recompiler must resolve or handle via a dispatch table.

**XBE** — The executable format for the original Xbox. XBE files wrap a PE-like structure with Xbox-specific headers and kernel import tables.

**XEX2** — The executable format for the Xbox 360. XEX2 files contain compressed and encrypted PowerPC code along with metadata about the title, required libraries, and security information. Decryption and decompression are prerequisites to recompilation.
