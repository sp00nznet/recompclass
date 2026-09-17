# The Case for Static Recompilation: Reviving Dead Architectures in the Age of Modern Computing

**Ned Heller (sp00nznet)**

*Draft v2 — March 2026*

*Research assisted by AutoResearchClaw (literature discovery, citation verification) and Understand-Anything (codebase architectural analysis of N64Recomp).*

---

## Abstract

Static recompilation — the ahead-of-time translation of legacy machine code into native executables for modern architectures — has moved from theoretical curiosity to practical reality. This paper examines what distinguishes static recompilation from its siblings (dynamic binary translation, emulation, and decompilation), why the convergence of modern compiler infrastructure, community-driven reverse engineering, and vastly more powerful host hardware has made this approach newly viable, and what philosophical motivations drive practitioners in the field. We survey the landscape from early academic work by Cifuentes (1996) and Sites et al. (1993) through contemporary projects such as N64Recomp and XenonRecomp, and situate static recompilation within the broader discourse on digital heritage preservation. We include a detailed source-level analysis of the N64Recomp tool to illustrate how theory maps to implementation. We also engage with critical perspectives — notably the argument advanced in "The Audacity of Static Recompilation" — that the technique is inherently audacious, pushing against fundamental limits of static analysis.

---

## 1. Introduction

Every computing platform ever manufactured is dying. Hardware degrades, capacitors leak, custom silicon becomes irreplaceable, and the software ecosystems built on those platforms face extinction alongside them. The question is not *whether* these systems will become inaccessible, but *how* — and whether we choose to intervene.

The dominant intervention strategy for the past three decades has been emulation: the construction of software models that mimic legacy hardware at runtime. Emulation has been remarkably successful, but it carries inherent costs. Every guest instruction must be interpreted or dynamically translated on the fly, imposing a performance multiplier that scales with the complexity of the emulated system. For simple 8-bit platforms, this overhead is negligible on modern hardware. For the PlayStation 2, the Xbox 360, or the Nintendo 64's notoriously idiosyncratic architecture, the cost is substantial — and for some titles, prohibitive.

Static recompilation offers a fundamentally different proposition: translate the binary *once*, ahead of time, into native code for the host platform. The result is not an emulator running a ROM. It is a native executable — one that can be compiled with modern optimizers, linked against modern libraries, and executed without any runtime translation layer at all.

This paper examines why this matters, why it works now when it did not before, and why people do it.

---

## 2. Definitions and Taxonomy

To reason clearly about static recompilation, we must first distinguish it from related techniques that are often conflated in popular discourse.

### 2.1 Emulation (Interpretation)

A software model of the target hardware executes guest instructions one at a time, translating each to equivalent host operations at runtime. This is the oldest and most straightforward approach. Interpreters are relatively simple to write and reason about, but their per-instruction overhead is high — typically 10–100x slower than native execution depending on the complexity gap between guest and host [1].

### 2.2 Dynamic Binary Translation (DBT)

Rather than interpreting each instruction individually, a dynamic translator converts *blocks* of guest instructions into host code at runtime, caching the results for reuse. Systems like Apple's Rosetta 2, QEMU, and the Xenia Xbox 360 emulator employ this strategy. Performance improves significantly over interpretation, but the translation engine itself consumes resources, and the requirement to translate code on first encounter introduces latency. Cifuentes and Malhotra (1996) note that dynamic translators typically require 15–17 host instructions per guest instruction due to runtime bookkeeping [2].

### 2.3 Decompilation

Decompilation attempts to recover high-level source code (typically C) from a binary. Projects like the Super Mario 64 decomp, the Zelda Reverse Engineering Team (ZRET), and the Metroid Prime decomp have produced compilable C source for entire games — but these are massive, multi-year community efforts requiring deep reverse engineering of every function. Decompilation produces human-readable code; static recompilation does not need to.

### 2.4 Static Recompilation

Static recompilation operates at the instruction level: each guest instruction is translated to an equivalent sequence of host instructions (or, more commonly, to C/C++ statements that a host compiler then optimizes). The translation happens once, before runtime. The output is a native binary that requires no emulation layer, no JIT compiler, and no interpreter.

The critical distinction is *when* the translation occurs and *what* it produces:

| Technique | Translation Time | Output | Performance | Human Effort |
|---|---|---|---|---|
| Interpretation | Runtime (per instruction) | None (in-memory) | Lowest | Low |
| Dynamic BT | Runtime (per block) | Cached native blocks | Medium | Low |
| Decompilation | Offline | Human-readable source | Highest | Very High |
| Static Recompilation | Offline | Compilable C/C++ or native | High | Medium |

Static recompilation occupies a sweet spot: it produces near-native performance without requiring the enormous human effort of full decompilation.

### 2.5 Adjacent Techniques: Binary Rewriting and Lifting

Recent work in the security and systems communities has produced related techniques that share conceptual DNA with static recompilation but serve different purposes. **RetroWrite** [11] performs static binary rewriting for instrumentation, enabling fuzzing and sanitization of COTS binaries without source code. **rev.ng** [12] lifts binaries to LLVM IR for analysis, recovering control flow graphs and function boundaries. **LeanBin** [13] harnesses lifting and recompilation specifically for binary debloating — removing unnecessary code to reduce attack surface. **BinRec** [10] combines dynamic traces with static lifting, using runtime information to guide recompilation. These tools address security and optimization concerns rather than preservation, but they validate the broader feasibility of offline binary transformation and contribute shared infrastructure (particularly LLVM-based lifting) to the field.

---

## 3. Why Now? The Convergence of Enabling Factors

Static binary translation is not a new idea. Gary Kildall's XLT86, which translated 8080 assembly to 8086, dates to 1981 [3]. Frances Allen's foundational work on control flow analysis — essential for understanding program structure in binaries — was published in 1970 [4]. Sites et al. described practical binary translation techniques at Digital Equipment Corporation in 1993 [5]. Cifuentes's UQBT framework demonstrated retargetable static translation in the late 1990s [2].

Yet for decades, static recompilation remained largely academic. Several factors have converged to change this.

### 3.1 Modern Compiler Infrastructure

The maturity of LLVM and GCC as optimization backends means that statically recompiled code — even when generated as naive C/C++ — can be aggressively optimized by world-class compilers. XenonRecomp translates PowerPC instructions into C++ statements manipulating a central processor context structure; the C++ compiler then applies register allocation, inlining, constant folding, and vectorization that would be extraordinarily difficult to implement in a custom code generator [6].

N64Recomp takes the same approach with striking clarity. Examining the source code, we find that each MIPS instruction is translated into a corresponding C macro invocation. The `recomp.h` header defines the runtime representation:

```c
typedef uint64_t gpr;

typedef struct {
    gpr r0,  r1,  r2,  r3,  r4,  r5,  r6,  r7,
        r8,  r9,  r10, r11, r12, r13, r14, r15,
        r16, r17, r18, r19, r20, r21, r22, r23,
        r24, r25, r26, r27, r28, r29, r30, r31;
    fpr f0,  f1,  f2,  f3, /* ... */ f30, f31;
    uint64_t hi, lo;
    uint32_t status_reg;
    uint8_t mips3_float_mode;
} recomp_context;
```

Every recompiled function takes the same signature: `void func_name(uint8_t* rdram, recomp_context* ctx)`. The first argument is a pointer to a flat byte array representing the N64's 8MB of RDRAM; the second is the full processor context. This uniformity means the C compiler can treat register accesses as simple struct member accesses and optimize accordingly.

The instruction `addiu $r4, $r4, 0x20` becomes:

```c
ctx->r4 = ADD32(ctx->r4, 0X20);
```

Where `ADD32` is defined as:

```c
#define ADD32(a, b) \
    ((gpr)(int32_t)((a) + (b)))
```

The cast to `int32_t` and back to `gpr` (uint64_t) faithfully reproduces the MIPS sign-extension behavior. The C compiler sees a 32-bit addition with sign extension — straightforward to optimize.

The recompiler does not need to be a good optimizer. It merely needs to produce *correct* code and delegate optimization to infrastructure that thousands of engineers have spent decades refining.

### 3.2 Overwhelming Host Performance

A modern x86-64 processor operating at 5+ GHz with wide superscalar execution, deep out-of-order pipelines, and enormous caches is orders of magnitude more powerful than the guest platforms being recompiled. The Nintendo 64's R4300i ran at 93.75 MHz. The Xbox 360's Xenon ran at 3.2 GHz but with a deeply different microarchitecture. When the host is 50–100x more powerful than the guest, the overhead of imperfect translation — redundant memory operations, suboptimal register allocation, unnecessary byte-swapping — is absorbed by sheer computational surplus. Static recompilation does not need to produce *optimal* code. It needs to produce *correct* code that is *good enough*, and modern hardware provides the margin for "good enough" to mean "runs beautifully."

### 3.3 Community Reverse Engineering Knowledge

Decades of emulator development, ROM hacking, and decompilation projects have produced extraordinarily detailed knowledge of legacy platforms. The N64 community understands the VR4300 instruction set, the Reality Coprocessor's command format, and the memory map of dozens of titles. The Xbox 360 community has mapped the Xenon's PowerPC extensions, VMX128 vector instructions, and XEX container format. This institutional knowledge — much of it undocumented except in emulator source code and forum posts — is the substrate on which static recompilation tools are built.

N64Recomp explicitly depends on this knowledge ecosystem. It uses [rabbitizer](https://github.com/Decompollaborate/rabbitizer) — a community-built MIPS instruction decoder from the decompilation community — for instruction analysis, and requires symbol metadata (typically from decompilation projects) provided via ELF files to identify function boundaries.

### 3.4 Improved Static Analysis Techniques

The classical objection to static recompilation is that static analysis cannot resolve indirect branches — computed jumps, virtual function calls, and jump tables whose targets depend on runtime state. This remains true in the general case, but practical solutions have emerged.

N64Recomp's `analysis.cpp` reveals a sophisticated approach to this problem. The analyzer maintains a `RegState` structure for each of the 32 MIPS registers, tracking the provenance of values through `lui`/`addiu`/`addu`/`lw` instruction sequences — the standard MIPS pattern for constructing addresses:

```cpp
struct RegState {
    uint32_t prev_lui;           // upper 16 bits loaded by LUI
    uint32_t prev_addiu_vram;    // lower 16 bits added by ADDIU
    uint32_t prev_addu_vram;     // result of ADDU combining regs
    uint8_t prev_addend_reg;     // which register was added
    bool valid_lui;
    bool valid_addiu;
    bool valid_addend;
    // For tracking values loaded from RAM (jump tables)
    uint32_t loaded_lw_vram;
    uint32_t loaded_address;
    bool valid_loaded;
};
```

When a `jr` (jump-register) instruction is encountered, the analyzer checks whether the target register's provenance traces back to a `lw` (load-word) from a computed address — the signature of a jump table. If so, the recompiler emits a C `switch` statement rather than an indirect call. The `recompilation.cpp` file converts jump table entries into `addiu` pseudo-instructions at recompilation time, preserving the table offsets so the C compiler can optimize the resulting switch.

For function pointer calls (`jalr` — jump-and-link-register), the recompiler emits a runtime lookup:

```c
LOOKUP_FUNC(ctx->r25)(rdram, ctx);
```

Where `LOOKUP_FUNC` resolves to `get_function((int32_t)(val))`, a runtime function that maps virtual addresses to recompiled function pointers. This is the escape hatch for cases static analysis cannot resolve — and critically, it only fires for genuine indirect calls, not for the statically-resolvable majority.

The `resolve_jal` function in `recompilation.cpp` shows the multi-tier resolution strategy for direct calls (`jal` instructions):

1. If the target is in the same section — always resolve statically (it must be loaded)
2. If exactly one non-relocatable function matches the target address — resolve statically
3. If multiple functions match (overlays!) — emit a `LOOKUP_FUNC` for runtime resolution
4. If no match but target is in the current section — create a new static function entry

This is not a general solution — it exploits deep knowledge of the N64's overlay system and ABI conventions — but it is a *sufficient* solution for the platform in question.

---

## 4. The Memory Model: A Case Study in Platform-Specific Translation

One of the most illuminating aspects of N64Recomp's implementation is its memory model. The N64's R4300i uses big-endian byte ordering and a 32-bit virtual address space mapped through a TLB. Recompiled code runs on little-endian x86-64 hosts. Rather than byte-swapping every memory access, N64Recomp uses XOR-based address manipulation — a well-known trick from the N64 emulation community:

```c
#define MEM_W(offset, reg) \
    (*(int32_t*)(rdram + ((((reg) + (offset))) - 0xFFFFFFFF80000000)))

#define MEM_H(offset, reg) \
    (*(int16_t*)(rdram + ((((reg) + (offset)) ^ 2) - 0xFFFFFFFF80000000)))

#define MEM_B(offset, reg) \
    (*(int8_t*)(rdram + ((((reg) + (offset)) ^ 3) - 0xFFFFFFFF80000000)))
```

Word-aligned (32-bit) accesses need no XOR — the byte ordering within a word is handled by storing data in host-native order. Half-word accesses XOR with 2, and byte accesses XOR with 3. This exploits the property that within a 32-bit word, XORing the byte offset with `(4 - access_size)` converts between big-endian and little-endian addressing.

The `0xFFFFFFFF80000000` subtraction maps N64 KSEG0/KSEG1 virtual addresses (which begin at `0x80000000` sign-extended to 64 bits) down to zero-based offsets into the flat `rdram` array. This is a direct, zero-cost address translation at compile time — no TLB simulation needed for the common case.

For relocatable overlays — code segments the N64 loads dynamically at varying addresses — the recompiler emits relocation macros:

```c
ctx->r24 = S32(RELOC_HI16(1754, 0X630) << 16);
```

Where `1754` is the section index and `0x630` is the offset within that section. The runtime implements `RELOC_HI16`/`RELOC_LO16` to adjust addresses based on where the overlay is currently loaded, allowing overlays to function correctly even when loaded at different addresses than the original binary expected.

---

## 5. The Audacity Problem

In "The Audacity of Static Recompilation," the technical challenges of XenonRecomp's approach to Xbox 360 binaries are laid bare [6]. The word "audacity" is well-chosen: static recompilation asks us to believe that a binary — stripped of symbols, debug information, and all the contextual knowledge that the original developers possessed — can be mechanically translated into correct, performant code for an entirely different architecture.

The fundamental difficulties are real and well-documented:

**The Halting Problem's Shadow.** In the general case, determining which bytes in a binary constitute code (versus data) is undecidable. Static recompilers must make assumptions — that code sections are reliably identified, that data and code do not overlap in pathological ways — that are not guaranteed to hold for all binaries [2]. N64Recomp sidesteps this by requiring ELF metadata with symbol information, explicitly declining to solve the general problem.

**Register Architecture Mismatch.** The Xbox 360's Xenon provides 32 general-purpose registers and 128 VMX128 vector registers per hardware thread. x86-64 provides 16 GPRs and limited vector registers. The recompiler must spill the difference to memory. N64Recomp faces a similar challenge — the R4300i has 32 GPRs plus 32 FPRs, mapped to a context struct that the C compiler's register allocator handles. The `RECOMP_FUNC` macro in `recomp.h` is carefully defined per compiler to disable inter-procedural optimization, ensuring the compiler doesn't make assumptions across function boundaries that could break interposition:

```c
#if defined(__GNUC__)
    #define RECOMP_FUNC __attribute__((noipa, optimize("rounding-math")))
#elif defined(__clang__)
    #define RECOMP_FUNC extern inline __attribute__((weak,noinline))
#elif defined(_MSC_VER)
    #define RECOMP_FUNC __declspec(noinline)
#endif
```

**Unified vs. Discrete Memory.** The Xbox 360's unified memory architecture, where CPU and GPU share coherent access to the same physical memory, has no direct equivalent on PC hardware with discrete GPUs [6]. The N64 has a similar unified architecture, but N64Recomp addresses this differently — the flat `rdram` array is CPU-only, and GPU interactions are handled by the runtime's Reality Display Processor (RDP) implementation rather than by the recompiler itself.

**Self-Modifying Code.** Any binary that modifies its own code at runtime is fundamentally incompatible with static recompilation. N64Recomp's approach of requiring pre-identified function boundaries via ELF metadata implicitly excludes self-modifying code — a pragmatic constraint that works for the vast majority of N64 titles compiled from C by period-era compilers (mips gcc 2.7.2 and IDO).

---

## 6. Motivations: Why People Do This

The motivations driving static recompilation practitioners are diverse, and understanding them is essential to understanding the field.

### 6.1 Preservation as Restoration

For some practitioners — this author included — static recompilation is fundamentally a restorative act. It is the digital equivalent of brushing sediment off a fossil and placing it in a museum. The software is already dead in a meaningful sense: the hardware it was built for is failing, the development tools that created it are lost, the institutional knowledge that surrounded it has dispersed. Static recompilation does not merely keep the software *accessible*; it brings it back to life in a form that can be experienced on contemporary hardware, studied, modified, and shared.

This is not nostalgia, though nostalgia is a valid motivator. It is an act of cultural stewardship. Rahm-Skageby and Carlsson (2021) describe retrocomputing communities as functioning "not only as storages but also as social venues and 'memory banks'" — living repositories of technical and cultural knowledge that would otherwise be lost [8]. The decomp and recomp communities are the archivists of an art form that mainstream institutions have largely ignored.

### 6.2 Performance and Enhancement

Others are motivated primarily by what static recompilation *enables*. Because the output is a native executable, it can be linked against modern graphics APIs, enabling enhancements that emulation cannot easily provide: native widescreen and ultrawide support, high-framerate rendering, ray tracing, modern input handling, and rapid load times. Zelda 64: Recompiled runs Majora's Mask at 4K with ray tracing — not as an emulated ROM with shaders bolted on, but as a native application making direct OpenGL/Vulkan calls [7]. This is a qualitative, not merely quantitative, improvement over emulation.

### 6.3 Modding and Extensibility

Static recompilation produces artifacts that are amenable to modification in ways that emulated ROMs are not. N64Recomp's architecture directly enables this: because every function is emitted as a separate C file with a standard signature (`void func(uint8_t* rdram, recomp_context* ctx)`), modders can replace individual functions by providing alternative implementations that the linker will prefer over the originals. The README describes this explicitly: "providing the recompiled patches to the linker before providing the original recompiler output will result in the patches taking priority." N64Recomp's mod framework in 2025 extends this to allow complex interoperation between mods through shared APIs [7] — a capability that is extraordinarily difficult to achieve when all code is being dynamically translated through an emulation layer.

### 6.4 The Intellectual Challenge

We would be remiss not to acknowledge that static recompilation is, for many practitioners, simply a deeply satisfying intellectual challenge. The intersection of compiler theory, reverse engineering, platform-specific knowledge, and systems programming required to make it work is among the most demanding in applied computer science. "The Audacity of Static Recompilation" captures this dimension well: there is something thrilling about attempting what ought to be impossible and making it work anyway [6].

---

## 7. Critical Perspectives

Not all views of static recompilation are favorable, and intellectual honesty requires engaging with the criticisms.

### 7.1 Legal and Ethical Concerns

Static recompilation operates in legally ambiguous territory. Unlike emulation, which (in the United States) has been partially shielded by precedent (*Sony v. Connectix*, *Sega v. Accolade*), static recompilation involves direct transformation of copyrighted binary code. The output binary contains translated representations of every instruction in the original — it is, in a meaningful sense, a derivative work. Rights holders have not broadly tested this in court, and the legal landscape remains uncertain [9].

### 7.2 Correctness and Fidelity

Purists in the emulation community argue that static recompilation sacrifices accuracy for performance. An accurate emulator models the guest hardware cycle-by-cycle, reproducing timing-dependent behavior, hardware bugs, and edge cases that static recompilation may not capture. N64Recomp's codebase reveals the tension: the `RECOMP_FUNC` attribute carefully preserves floating-point rounding behavior (GCC's `optimize("rounding-math")`, MSVC's `fenv_access(on)`) because the N64's MIPS FPU rounding modes affect game behavior. The `recomp.h` header implements rounding mode getters/setters that map MIPS rounding modes to C99 `fesetround` constants. This level of care is necessary precisely because static recompilation cannot rely on cycle-accurate hardware simulation — it must explicitly model every observable behavior in C.

### 7.3 Sustainability and Scope

Each static recompilation tool is, to a significant degree, platform-specific. N64Recomp understands the R4300i and the N64's memory map. XenonRecomp understands PowerPC and the XEX format. There is limited transferability between them. Critics argue that the effort invested in a static recompiler for one platform might be better spent improving general-purpose emulation infrastructure that benefits all software for that platform.

However, the emergence of shared infrastructure — particularly LLVM-based binary lifting (rev.ng [12], LeanBin [13]) — suggests the field may be moving toward more retargetable frameworks. The operational abstraction layer in N64Recomp's `operations.cpp`, which maps MIPS instructions to abstract `BinaryOp` and `UnaryOp` types before the `CGenerator` backend emits C code, hints at a natural extension point: a different generator backend could target LLVM IR, Rust, or any other language.

---

## 8. The Road Ahead

Static recompilation is entering a period of rapid maturation. N64Recomp reported in early 2025 that the tool can compile "nearly all N64 games" into native PC executables, with a focus on lower-end hardware and Steam Deck compatibility [7]. XenonRecomp has demonstrated the first working static recompilation of Xbox 360 PowerPC executables to x86-64 [6]. The Unleashed Recomp project has produced a native PC port of Sonic Unleashed running at 144Hz [9].

Several open questions remain:

- **Generalization.** Can static recompilation tooling be made more retargetable, reducing the per-platform engineering effort? LLVM's intermediate representation is an obvious candidate for a common translation target. N64Recomp's separation of instruction analysis (`operations.cpp`) from code generation (`cgenerator.cpp`) already embodies this principle.
- **Automation.** Current tools require significant manual annotation — function boundaries, jump table locations, overlay configurations. Can machine learning or improved static analysis reduce this burden? The `RegState`-tracking approach in N64Recomp's analyzer is a form of abstract interpretation; more sophisticated dataflow analyses could resolve additional indirect branches automatically.
- **Legal clarity.** The preservation community would benefit enormously from legal precedent or legislative action clarifying the status of binary translation for preservation purposes.
- **Hybrid approaches.** BinRec [10] demonstrated dynamic binary lifting — using runtime traces to guide static recompilation — and this hybrid approach may resolve many of the limitations of purely static analysis. LeanBin [13] similarly combines lifting with recompilation for debloating, suggesting that the boundary between static and dynamic approaches is increasingly porous.

---

## 9. Conclusion

Static recompilation is not a replacement for emulation. It is a complement — a technique that excels precisely where emulation struggles, and that produces artifacts with fundamentally different properties than emulated software. It is made possible by the convergence of mature compiler infrastructure, overwhelming host performance, decades of community reverse engineering, and improved static analysis techniques.

The N64Recomp codebase demonstrates these principles in concrete terms: a 13-file C++ project that translates MIPS binaries into compilable C, using a flat memory array with XOR-based endianness handling, a context struct that the host compiler's register allocator can optimize, pattern-matching analysis for jump tables, runtime function lookup for the genuinely unresolvable cases, and per-compiler attribute tuning to preserve floating-point semantics. It is elegant in its directness — and it works.

But beyond the technical arguments, there is something worth saying plainly: the software of the past deserves to survive. Not as museum curiosities locked behind glass, but as living, runnable, modifiable programs that future generations can experience, study, and build upon. Static recompilation, for all its audacity, is one of the most powerful tools we have for making that happen.

We are brushing off fossils and putting them in museums — but museums where you can touch the exhibits.

---

## References

[1] J. Smith and R. Nair, *Virtual Machines: Versatile Platforms for Systems and Processes*. Morgan Kaufmann, 2005.

[2] C. Cifuentes and V. Malhotra, "Binary Translation: Static, Dynamic, Retargetable?" in *Proc. International Conference on Software Maintenance*, 1996. DOI: 10.1109/ICSM.1996.565017

[3] G. Kildall, "XLT86 — 8080 to 8086 Assembly Language Translation," Digital Research, 1981.

[4] F. E. Allen, "Control Flow Analysis," in *Proc. ACM SIGPLAN Symposium on Compiler Optimization*, 1970. DOI: 10.1145/800028.808479

[5] R. L. Sites, A. Chernoff, M. B. Kirk, M. P. Marks, and S. G. Robinson, "Binary Translation," *Digital Technical Journal*, vol. 4, no. 4, 1993.

[6] "The Audacity of Static Recompilation," TC Tech Stuff, 2024. Available: https://tctechstuff.com/the-audacity-of-static-recompilation/

[7] N64Recomp project, Wiseguy. Available: https://github.com/N64Recomp/N64Recomp. See also: "N64 Recompilation is about to have a big 2025," ReadOnlyMemo. Available: https://readonlymemo.com/n64-recompilation-releases-modding-2025/

[8] J. Rahm-Skageby and A. Carlsson, "The archive and the scene: On the cultural techniques of retrocomputing databases," *New Media & Society*, vol. 23, no. 5, 2021. DOI: 10.1177/1461444820954186

[9] "Static Recompilation: A Revolution for Retrogaming," ExtendsClass Blog, 2024. Available: https://extendsclass.com/blog/static-recompilation-a-revolution-for-retrogaming

[10] A. Altinay et al., "BinRec: Dynamic Binary Lifting and Recompilation," in *Proc. EuroSys*, 2020. DOI: 10.1145/3342195.3387550

[11] S. Dinesh, N. Burow, D. Xu, and M. Payer, "RetroWrite: Statically Instrumenting COTS Binaries for Fuzzing and Sanitization," in *Proc. IEEE Symposium on Security and Privacy*, 2020. DOI: 10.1109/SP40000.2020.00009

[12] A. Di Federico, M. Payer, and G. Agosta, "rev.ng: A Unified Binary Analysis Framework to Recover CFGs and Function Boundaries," in *Proc. 26th International Conference on Compiler Construction*, 2017. DOI: 10.1145/3033019.3033028

[13] I. Wodiany, A. Pop, and M. Luján, "LeanBin: Harnessing Lifting and Recompilation to Debloat Binaries," arXiv:2406.16162, 2024.

[14] N. Ramsey, "The New Jersey Machine-Code Toolkit," Bell Communications Research, 1995.

---

## Appendix A: Methodology Note

### Tools Used

**AutoResearchClaw** (https://github.com/aiming-lab/AutoResearchClaw) — An autonomous research pipeline that searches OpenAlex, Semantic Scholar, and arXiv for academic literature with 4-layer citation verification (arXiv ID, DOI, title matching, relevance scoring). Used in this paper for literature discovery in Section 2.5 and throughout the reference list. References [10]–[13] were identified or verified through AutoResearchClaw's `search_papers()` API, which deduplicates across sources by DOI and fuzzy title matching.

**Understand-Anything** (https://github.com/Lum1104/Understand-Anything) — A codebase analysis tool that uses a multi-agent pipeline (project scanner, file analyzer, architecture analyzer, tour builder, graph reviewer) to produce interactive knowledge graphs of software projects. The N64Recomp architectural analysis in Sections 3–5 was informed by the analytical framework this tool provides: examining the project through the lens of architectural layers (analysis, operations, code generation, runtime), dependency relationships (rabbitizer for decoding, ELFIO for ELF parsing, fmtlib for output), and the data flow from binary input through instruction decoding to C code emission.

---

*This paper was prepared as a standalone position paper and is not currently integrated into the Recompclass curriculum.*
