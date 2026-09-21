# Module 28: Xbox 360 and PowerPC Xenon

The Xbox 360 represents a massive leap in complexity from the N64. Where an N64 game has 2,000-5,000 functions, an Xbox 360 game routinely has 10,000-50,000 or more. The CPU is a triple-core PowerPC Xenon with VMX/Altivec SIMD, the executable format is encrypted and compressed, and the runtime must shim an entire modern console operating system. This is where static recompilation pushes against the boundaries of what was previously thought feasible.

This module covers the Xbox 360 hardware, the extraction and triage pipeline, XenonRecomp's codegen, PowerPC Xenon specifics that affect code generation, VMX-to-SIMDE translation, and the ReXGlue runtime layer.

---

## 1. The Xbox 360 Platform

Released in 2005, the Xbox 360 was a significant departure from its predecessor. Where the original Xbox used commodity PC hardware (an Intel x86 CPU, an NVIDIA GPU), the 360 used a custom IBM PowerPC processor and an ATI-designed GPU.

### CPU: PowerPC Xenon (Waternoose)

The Xenon processor contains three symmetric PowerPC cores, each clocked at 3.2 GHz:

- **3 cores**, each with **2 hardware threads** (6 hardware threads total)
- In-order execution (no out-of-order engine -- games must be carefully scheduled)
- **128 VMX/Altivec registers per thread** (128-bit SIMD)
- 32 KB L1 instruction cache + 32 KB L1 data cache per core
- 1 MB shared L2 cache
- Big-endian byte ordering

The in-order design is important for recompilation: it means instruction scheduling in the original binary is meaningful and intentional. The compiler that built the original game worked hard to hide latencies, and the recompiled code benefits from the host compiler re-scheduling for the host's out-of-order pipeline.

### Memory

512 MB of unified GDDR3 RAM shared between CPU and GPU. No separate VRAM. The memory bus is 128-bit wide at 700 MHz, providing 22.4 GB/s of bandwidth.

### GPU: Xenos

The Xenos GPU was designed by ATI (now AMD) and introduced unified shader architecture to consoles -- the same shader units handle both vertex and pixel processing. It has 48 unified shader units and 10 MB of embedded DRAM (eDRAM) used for the framebuffer and as a fast render target.

### XEX2 Executable Format

Xbox 360 executables use the XEX2 format, a Microsoft-designed container that wraps a PE (Portable Executable) image with:

- **Encryption**: AES encryption of the PE payload
- **Compression**: LZX compression of the encrypted data
- **Digital signatures**: RSA signatures for code integrity
- **Import tables**: References to Xbox 360 system libraries (xam.xex, xboxkrnl.exe)
- **Security headers**: Media type restrictions, region codes, title ID

```mermaid
flowchart TD
    XEX["XEX2 File"] --> Headers["XEX2 Headers\nSecurity, Import Tables\nCompression Info"]
    XEX --> Encrypted["Encrypted + Compressed\nPE Payload"]
    Encrypted -->|"Decrypt + Decompress"| PE["PE Image\n.text, .data, .rdata\nImport/Export Tables"]
    PE --> Code[".text Section\nPowerPC Xenon Code"]
    PE --> Data[".data / .rdata\nGame Data"]
    PE --> Imports["Import Table\nxam.xex functions\nxboxkrnl.exe functions"]

    style XEX fill:#2d3748,stroke:#4a5568,color:#fff
    style Headers fill:#744210,stroke:#975a16,color:#fff
    style Encrypted fill:#744210,stroke:#975a16,color:#fff
    style PE fill:#2b6cb0,stroke:#3182ce,color:#fff
    style Code fill:#2f855a,stroke:#38a169,color:#fff
    style Data fill:#2f855a,stroke:#38a169,color:#fff
    style Imports fill:#2f855a,stroke:#38a169,color:#fff
```

---

## 2. Getting from a Disc to Source

### Extraction and Triage

Before any recompiler runs, you have to get a PE image out of the shipping container.
Two container formats, depending on where the game came from:

- **Retail disc** -- an XGD image with an XDVDFS filesystem. Extract, then find the XEX.
- **XBLA / Games on Demand** -- an STFS or GoD package. Extract, then find the XEX.

Then **XEX triage**: decrypt and decompress the XEX2 to recover the raw PE, read the
headers for the image base (it is `0x82000000` on every retail title you are likely
to meet), and parse the import table to learn which kernel and XAM ordinals the game
needs. That last number matters more than it sounds -- see section 6.

### XenonRecomp: The Recompiler Pipeline

### XenonRecomp: The Recompiler Pipeline

[XenonRecomp](https://github.com/hedge-dev/XenonRecomp), created by **Skyth** ([hedge-dev](https://github.com/hedge-dev)), is the static recompiler for Xbox 360 binaries. Its codegen and instruction translation build on foundational work by **[rexdex](https://github.com/rexdex/recompiler)**, whose Xbox 360 recompiler was the first to prove static recompilation was viable on this platform. Skyth's collaboration with **Sajid** (who created XenonAnalyse for binary analysis) and **Hyper** (system-level features) culminated in **[UnleashedRecomp](https://github.com/hedge-dev/UnleashedRecomp)** -- a full native PC port of Sonic Unleashed from Xbox 360, and one of the most impressive demonstrations of static recompilation at scale.

XenonRecomp's pipeline follows the standard pattern but with Xbox 360-specific stages:

1. **XEX2 Parsing**: Decrypt and decompress to extract the raw PE
2. **PE Analysis**: Parse sections, resolve imports, identify code vs. data regions
3. **Function Identification**: Use a combination of call targets, prologue patterns (`mflr r12; stw r12, -8(r1); stwu r1, -N(r1)`), and manual symbol files
4. **Disassembly**: Recursive descent through PowerPC instructions
5. **Lifting**: Translate PPC instructions to C, handling the condition register, link register, VMX operations
6. **Code Generation**: Emit compilable C source with the ReXGlue runtime interface

### Function Identification in Stripped Binaries

Xbox 360 games are stripped -- no debug symbols, no function names. Finding function boundaries in a 20MB code section requires multiple strategies:

- **BL targets**: Every `BL` (Branch and Link) instruction identifies a function entry point
- **Prologue matching**: Xbox 360 compilers (Microsoft's PPC compiler) emit recognizable function prologues
- **Exception tables**: Some XEX2 files include exception handling tables that list function boundaries
- **Import stubs**: Functions that load from the import table have a distinctive stub pattern

Accuracy varies enormously by title and by how the game was compiled, and the useful
measure is not a percentage -- it is **how many addresses you had to hint by hand**.
On a well-behaved binary that number is startlingly small: see the table in section 6,
where a 14,781-function game needed exactly one hint. On a badly-behaved one you will
fight static-init thunks and tail calls for a day. Do not budget from an average.

---

## 3. PowerPC Xenon Specifics

PowerPC is a more complex architecture to recompile than MIPS. It has features that require careful modeling in the generated C code.

### Condition Register

The PowerPC condition register (CR) has 8 fields (CR0-CR7), each containing 4 bits: LT (less than), GT (greater than), EQ (equal), SO (summary overflow). Compare instructions write to a specific CR field, and branch instructions can test any CR field.

```asm
    cmpwi   cr6, r3, 0       ; compare r3 with 0, result in CR6
    cmpwi   cr7, r4, 10      ; compare r4 with 10, result in CR7
    blt     cr6, label1       ; branch if CR6.LT is set
    beq     cr7, label2       ; branch if CR7.EQ is set
```

The recompiler must model all 8 CR fields. The straightforward approach is to store each CR field as a struct:

```c
// cmpwi cr6, r3, 0
{
    int32_t a = (int32_t)ctx->r[3];
    int32_t b = 0;
    ctx->cr[6].lt = (a < b);
    ctx->cr[6].gt = (a > b);
    ctx->cr[6].eq = (a == b);
    ctx->cr[6].so = ctx->xer_so;
}

// blt cr6, label1
if (ctx->cr[6].lt) goto label1;
```

### Link Register and Count Register

PowerPC uses a **link register** (LR) for function calls and returns, and a **count register** (CTR) for counted loops and indirect branches:

- `BL target` -- branch to target, save return address in LR
- `BLR` -- branch to address in LR (function return)
- `MTCTR r3` -- move r3 into CTR
- `BDNZ loop` -- decrement CTR, branch if not zero
- `BCTR` -- branch to address in CTR (indirect call)

The LR and CTR must be modeled as context variables. `BCTR` (branch to CTR) is particularly challenging because it is an indirect jump -- the recompiler must determine the possible targets through analysis or emit a runtime dispatch.

### Special-Purpose Registers (MTxx/MFxx)

PowerPC has numerous special-purpose registers accessed via `MTSPR`/`MFSPR` (Move To/From Special-Purpose Register):

| SPR | Name | Purpose |
|---|---|---|
| 1 | XER | Fixed-point exception register (carry, overflow) |
| 8 | LR | Link register |
| 9 | CTR | Count register |
| 268-271 | TB | Time base (read-only timer) |

The recompiler must handle each SPR. Most are straightforward context variables, but the time base requires a runtime implementation that provides a monotonically increasing counter.

### VMX/Altivec (128-bit SIMD)

Xbox 360 games make **extremely heavy** use of VMX/Altivec SIMD instructions. Game math -- vector operations, matrix transformations, physics calculations, animation blending -- is almost entirely vectorized. A typical Xbox 360 game has thousands of VMX instructions.

VMX registers are 128 bits wide and can be interpreted as:

- 4 x 32-bit floats
- 4 x 32-bit integers
- 8 x 16-bit integers
- 16 x 8-bit integers
- 2 x 64-bit integers (Xenon extension)

---

## 4. VMX/Altivec to SIMDE Translation

The translation of VMX/Altivec SIMD operations to host-native SIMD is one of the most critical performance challenges in Xbox 360 recompilation.

### The Problem

VMX/Altivec instructions operate on 128-bit vectors with big-endian element ordering. x86 SSE operates on 128-bit vectors with little-endian element ordering. ARM NEON uses yet another convention. A direct 1:1 instruction mapping does not exist for most operations because the element ordering differs.

### SIMDE: The Translation Layer

SIMDE (SIMD Everywhere) is a header-only library that provides portable implementations of SIMD intrinsics. XenonRecomp generates C code that uses SIMDE Altivec intrinsics, which SIMDE then compiles to the optimal SIMD instructions for the host platform.

Here is a concrete example -- a vector dot product pattern common in game math:

```asm
; PowerPC VMX: dot product of v3 and v4, result in v5
    vmaddfp   v5, v3, v4, v0     ; v5 = v3 * v4 + v0 (v0 = zero vector)
    vperm     v6, v5, v5, v10    ; shuffle to prepare for horizontal add
    vaddfp    v5, v5, v6         ; partial horizontal add
    vperm     v6, v5, v5, v11    ; shuffle again
    vaddfp    v5, v5, v6         ; final horizontal sum in all elements
```

The generated SIMDE code:

```c
// vmaddfp v5, v3, v4, v0
ctx->v[5] = vec_madd(ctx->v[3], ctx->v[4], ctx->v[0]);

// vperm v6, v5, v5, v10
ctx->v[6] = vec_perm(ctx->v[5], ctx->v[5], ctx->v[10]);

// vaddfp v5, v5, v6
ctx->v[5] = vec_add(ctx->v[5], ctx->v[6]);

// vperm v6, v5, v5, v11
ctx->v[6] = vec_perm(ctx->v[5], ctx->v[5], ctx->v[11]);

// vaddfp v5, v5, v6
ctx->v[5] = vec_add(ctx->v[5], ctx->v[6]);
```

SIMDE compiles `vec_madd` to `_mm_fmadd_ps` (FMA3) or `_mm_add_ps(_mm_mul_ps(...))` (SSE) on x86, and to `vfmaq_f32` on ARM NEON. The `vec_perm` call compiles to `_mm_shuffle_epi8` (SSSE3) on x86.

### Endianness and Element Ordering

The most subtle issue is element ordering. VMX numbers elements 0-3 from left to right (big-endian convention), while SSE numbers elements 0-3 from right to left (little-endian convention). A `vperm` (vector permute) instruction that shuffles elements in a specific order on PowerPC must have its permute control vector byte-reversed when compiled for a little-endian host.

SIMDE handles this automatically when the permute control vector is a compile-time constant. When it is loaded from memory at runtime (common in Xbox 360 games that store permute tables), the recompiler must insert endian-swap logic.

```mermaid
flowchart LR
    subgraph PPC["PowerPC VMX (Big-Endian)"]
        direction TB
        P0["Element 0"] --- P1["Element 1"] --- P2["Element 2"] --- P3["Element 3"]
    end

    subgraph X86["x86 SSE (Little-Endian)"]
        direction TB
        X3["Element 3"] --- X2["Element 2"] --- X1["Element 1"] --- X0["Element 0"]
    end

    PPC -->|"SIMDE\nElement Reorder\n+ Byte Swap"| X86

    style PPC fill:#2b6cb0,stroke:#3182ce,color:#fff
    style X86 fill:#2f855a,stroke:#38a169,color:#fff
    style P0 fill:#2b6cb0,stroke:#3182ce,color:#fff
    style P1 fill:#2b6cb0,stroke:#3182ce,color:#fff
    style P2 fill:#2b6cb0,stroke:#3182ce,color:#fff
    style P3 fill:#2b6cb0,stroke:#3182ce,color:#fff
    style X0 fill:#2f855a,stroke:#38a169,color:#fff
    style X1 fill:#2f855a,stroke:#38a169,color:#fff
    style X2 fill:#2f855a,stroke:#38a169,color:#fff
    style X3 fill:#2f855a,stroke:#38a169,color:#fff
```

---

## 5. ReXGlue Runtime

The runtime for Xbox 360 recompilation is substantially more complex than for older consoles. The Xbox 360 has a full operating system with system libraries, and games call into these libraries extensively.

### Architecture

ReXGlue is the runtime shim layer that translates Xbox 360 API calls into modern PC equivalents:

```mermaid
flowchart TB
    Game["Recompiled Game Code\n(Generated C)"] --> ReXGlue["ReXGlue Runtime Layer"]
    ReXGlue --> GFX["Graphics Translation\nD3D9-like to D3D11/D3D12"]
    ReXGlue --> Audio["Audio Translation\nXAudio2 to Modern Audio"]
    ReXGlue --> Input["Input Translation\nXInput (shimmed directly)"]
    ReXGlue --> Kernel["Kernel Shims\nThreading, Memory, I/O"]
    ReXGlue --> Net["Network Stubs\nXLive / Matchmaking"]
    ReXGlue --> XAM["XAM Shims\nAchievements, Profiles\nContent Enumeration"]

    style Game fill:#2d3748,stroke:#4a5568,color:#fff
    style ReXGlue fill:#2b6cb0,stroke:#3182ce,color:#fff
    style GFX fill:#744210,stroke:#975a16,color:#fff
    style Audio fill:#744210,stroke:#975a16,color:#fff
    style Input fill:#2f855a,stroke:#38a169,color:#fff
    style Kernel fill:#744210,stroke:#975a16,color:#fff
    style Net fill:#4a5568,stroke:#718096,color:#fff
    style XAM fill:#4a5568,stroke:#718096,color:#fff
```

### Graphics: D3D9-like to D3D11/D3D12

Xbox 360 games use a graphics API that is a close cousin of Direct3D 9, with Xbox-specific extensions. The Xenos GPU has features not present in standard D3D9 (predicated tiling, eDRAM resolve, memexport). The graphics translation layer must:

- Translate vertex and pixel shader bytecode (Xbox 360 uses a modified D3D9 shader model)
- Map render state calls to D3D11/D3D12 pipeline state objects
- Handle the Xenos tiling architecture (games explicitly manage eDRAM partitioning)
- Translate texture formats (some are Xenos-specific swizzled formats)

### Audio: XAudio2 Translation

Xbox 360 games use XAudio2 for audio, which is convenient because XAudio2 also exists on Windows. However, the Xbox 360 version predates the Windows version and has API differences. The shim layer bridges these differences and handles Xbox 360-specific audio features like hardware XMA decoding.

### XInput: Direct Mapping

Xbox 360 controller input uses XInput, which is natively supported on Windows. This is one of the few areas where the API maps almost directly, requiring minimal shimming.

### Kernel and XAM

The Xbox 360 kernel (xboxkrnl.exe) and system library (xam.xex) export hundreds of functions for:

- **Threading**: Thread creation, synchronization primitives, thread-local storage
- **Memory management**: Virtual memory allocation, physical memory mapping
- **File I/O**: Content packages, save games, DLC enumeration
- **Networking**: Xbox Live services, matchmaking, leaderboards
- **Profile management**: Achievements, gamer profiles, settings

Many networking and Xbox Live functions are stubbed (returning success but doing nothing), since the Xbox Live infrastructure no longer exists for most games. Threading and memory management require careful reimplementation to match Xbox 360 semantics.

---

## 6. Real-World Projects

Every project below is public, and each README carries an **Honest scope** section
saying exactly how far it actually got. Read them in that spirit -- these are
bring-ups in progress, not finished ports, and the interesting material is in the gaps.

### [Worms Revolution](https://github.com/sp00nznet/wormsrevolution) -- playable, without text

Team17, 2012, GoD package. The one that actually plays -- with a caveat that matters, below: intro logos, full-motion video
decoding natively, animated title screen, and the tutorial playable end to end with
worms, terrain, weapons, physics, camera and input all working.

The number to stare at: codegen recompiled **88,816 functions**, and the entire
reachable game needs **444 registered functions**. Everything else is dead weight in
the binary -- unreferenced library code, dead branches, content paths this build never
touches. Your recompiler's function count is not a measure of the work.

Its one known gap is a good lesson too. In-game **text does not render** -- speech
bubbles appear empty, menu buttons are blank. Worms draws its text through *memexport*
vertex shaders, where the GPU writes generated geometry back to memory, and the D3D12
backend does not implement that yet, so those draws are dropped. That is a **runtime
GPU feature gap, not missing recompiled code.** Learning to tell those two apart
quickly is most of the skill in bring-up.

### [You Don't Know Jack](https://github.com/sp00nznet/ydkj) -- renders its front end

Jellyvision, XBLA. 5 MB guest image, **14,781 recompiled functions**, links into a
21 MB executable with **zero hand-written kernel stubs** -- the runtime already
exported all **209** kernel/XAM imports the game asked for, verified by diffing
`__imp__` symbols against the SDK libraries. Boots crash-free to the animated title
screen with text rendering correctly.

**One codegen hint.** The first pass surfaced a single unresolved call: a tail-call to
`0x82236F38` that discovery had not placed inside any function. One entry in the
manifest, second pass clean.

### [Civilization Revolution](https://github.com/sp00nznet/civrev) -- boots into engine init

2K/Firaxis, Gamebryo engine. 16.8 MB image, **40,067 functions**, **231 MB of generated
C++**, an 80 MB executable. Boots with zero fatal or unresolved lines all the way
through D3D12 device creation, audio and XMA threads, guest disk mount, XEX load and
GPU interrupt callback -- then dies in asset loading, because Gamebryo probes for a
`D:` installed-title mount and an `Assets/` + `Resource/Xenon/` layout the disc extract
does not provide, and does not error-check the misses.

This is the project that produced the **over-hinting trap** described in Module 14:
301 pointer-scan hints made the build worse, 21 runtime-harvested hints fixed it.

### [OutRun Online Arcade](https://github.com/sp00nznet/outrun) -- crashes in global init

Sega / Sumo Digital, XBLA, delisted 2011. 11.1 MB image, ~3,400 assets, recompiles with
**zero hints** and links with **no missing stubs**, and the runtime comes all the way up
before the guest crashes during its own global initialization -- an unchecked virtual
call on a subsystem object that should have been constructed and is null.

Worth studying because the README documents a **ruled-out red herring**: an early
suspect (a failed `ShaderDump` device probe) turned out to be a harmless get-file-size
on another thread. Bring-up is mostly eliminating plausible wrong answers, and writing
down the ones you eliminated is how you stop re-investigating them at 2am.

It also shows the limit of tolerance shims. Blunt tolerances get *past* the null
dereference -- and the next function genuinely needs that subsystem, so the crash just
moves. Tolerance buys you a debugger session, not a fix.

### [After Burner Climax](https://github.com/sp00nznet/afterburner) -- scaffolded

Sega AM2, XBLA, delisted 2015. A hefty 43.6 MB image, 4 function-entry hints, built but
not yet booted. Included here because a 3D/VMX-heavy arcade title will exercise far more
of the runtime than the 2D catalogue -- a useful reminder that "it recompiled cleanly"
predicts almost nothing about bring-up difficulty.

### Why these claims are structurally checkable

Module 27 gives a ten-minute test for whether a project's screenshots come from the
recompiled program or from its harness. Apply it here, because these repositories pass it
in a way that is worth seeing.

`wormsrevolution`'s entire hand-written surface is four files:

```
project/src/main.cpp                146 bytes
project/src/worms_app.h           1,589 bytes
project/src/stubs.cpp             3,942 bytes
project/src/dispatch_tolerance.cpp 2,785 bytes
```

`main.cpp` in full is an include and a `REX_DEFINE_APP` macro. `worms_app.h` is a
subclass of `rex::ReXApp` whose only override is a debug image dump gated behind an
environment variable. `ydkj` is smaller still -- three files, under 3 KB.

There is no renderer here. No asset loader, no menu code, no scene graph. Everything on
screen comes from the recompiled game driving the SDK runtime, because **there is nothing
else in the repository that could draw it.**

Contrast Module 27's `burnout3`, whose `src/game/` holds a 1,919-line hand-written
RenderWare renderer and an 825-line hand-written front-end menu with hardcoded labels.
Both projects are real work. Only one of them can point at a screenshot and say the
recompiled game produced it, and you can tell which from `ls` and `wc -l` before reading
a single claim.

This is the strongest argument for the toolkit-plus-thin-game-project structure this
course keeps recommending. When the per-title code is three files, "the game runs" means
something, because there is no room for it to mean anything else.

### Scale Summary

| Project | Image | Functions | Hints | Stubs | Output | Where it got to |
|---|---|---|---|---|---|---|
| [ydkj](https://github.com/sp00nznet/ydkj) | 5 MB | 14,781 | 1 | 0 | 21 MB | title screen renders |
| [outrun](https://github.com/sp00nznet/outrun) | 11.1 MB | -- | 0 | 0 | 22 MB | crash in guest global-init |
| [civrev](https://github.com/sp00nznet/civrev) | 16.8 MB | 40,067 | 24 | 1 bundle | 80 MB | engine init, no render |
| [wormsrevolution](https://github.com/sp00nznet/wormsrevolution) | -- | 88,816 (444 reached) | -- | -- | 74 MB | **playable** |
| [afterburner](https://github.com/sp00nznet/afterburner) | 43.6 MB | -- | 4 | -- | -- | built, not booted |

Read down the Hints column against the Functions column. Then read the last column.
**There is no correlation.** Codegen difficulty and bring-up difficulty are unrelated
problems, and the second one is where the months go.

### Lessons Learned

1. **VMX is everywhere.** In N64 games, you can recompile most of the game without worrying about the coprocessor. In Xbox 360 games, VMX instructions are in virtually every function. If your VMX lifting is wrong, nothing works.

2. **Endianness is pervasive.** The Xbox 360 is big-endian, PCs are little-endian. Every memory access that crosses the boundary between recompiled code and the host system must be byte-swapped. Getting this wrong produces bugs that are extremely difficult to diagnose -- the game runs but data is corrupted in subtle ways.

3. **Scale changes everything.** Recompiling 15,000 functions generates hundreds of thousands of lines of C. Compilation time becomes a real concern. Incremental builds, precompiled headers, and parallel compilation are not luxuries -- they are necessities.

4. **The runtime dwarfs the recompiler.** Writing XenonRecomp (the recompiler) is the smaller part of the project. Writing ReXGlue (the runtime) -- shimming the Xbox 360 OS, translating the graphics API, handling the audio system -- is where the majority of the work lives.

---

## Lab Reference

**Lab 17** walks you through analyzing an Xbox 360 XEX2 binary -- parsing the headers, examining the import table, running XenonRecomp on a subset of functions, and inspecting the generated C code for VMX operations and condition register handling.

---

## Next Module

[Module 29: GPU Pipeline Translation](../module-29-gpu-translation/lecture.md) -- Fixed-function to programmable shaders, texture format conversion, and resolution scaling. The GPU side of the recompilation problem.
