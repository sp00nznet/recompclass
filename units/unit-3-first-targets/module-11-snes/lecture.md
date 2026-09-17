# Module 11: SNES -- 65816 and Hardware Integration

The Super Nintendo Entertainment System is the first major step up in complexity from the Game Boy. Its CPU, the Ricoh 5A22 (based on the Western Design Center 65816), introduces a concept that will haunt you through the rest of this course: **variable-width registers controlled by runtime state**. The size of an operand is not encoded in the instruction -- it depends on flags in the processor status register that can change at any point during execution. The recompiler must know the state of these flags at every instruction, or it cannot even determine how many bytes an instruction occupies.

This module covers the 65816's unique challenges, the strategy for tracking register width at recompile time, the SNES memory map, and a powerful integration pattern: using the recompiled CPU code to drive an existing emulator's hardware implementation.

---

## 1. The 65816 Challenge

The 65816 is a 16-bit extension of the 6502, the legendary 8-bit processor used in the NES, Apple II, and Commodore 64. It maintains full backward compatibility with the 6502 while adding:

- A 24-bit address bus (16MB address space, vs. the 6502's 64KB)
- 16-bit accumulator and index registers (when enabled)
- New addressing modes and instructions
- Bank registers that extend the address space

The backward compatibility is both a strength and a source of complexity. The processor can operate in "emulation mode" (behaving like a 6502) or "native mode" (using the full 65816 feature set). SNES games run almost entirely in native mode, but the boot process starts in emulation mode and switches.

The defining challenge of the 65816 is the **M and X flags** in the processor status register (P register). These two bits control the width of the processor's data registers:

- **M flag (bit 5)**: When set, the accumulator (A) is 8-bit. When clear, A is 16-bit.
- **X flag (bit 4)**: When set, index registers (X, Y) are 8-bit. When clear, X and Y are 16-bit.

This means that the same opcode can operate on either 8-bit or 16-bit data depending on the current state of these flags. The instruction `LDA #imm` loads a 1-byte immediate when M=1 or a 2-byte immediate when M=0. The instruction itself does not encode which size is in use -- the processor just knows based on the current P register.

For a disassembler, this is a fundamental problem. You cannot even determine the size of an instruction without knowing the M/X state. If you get it wrong, you will read the wrong number of bytes for the immediate operand and every subsequent instruction in the stream will be misaligned. One wrong flag assumption can cascade into an entirely incorrect disassembly.

---

## 2. M/X Flag Tracking

The recompiler must track the M and X flag state at every instruction. This is a static analysis problem: given the control flow graph, determine what values M and X can hold at each point in the program.

### How M/X State Changes

Only two instructions modify the M and X flags:

- **SEP #imm** (Set Processor Status): Sets the bits specified by the immediate operand. `SEP #0x20` sets the M flag (8-bit accumulator). `SEP #0x10` sets the X flag (8-bit index registers). `SEP #0x30` sets both.
- **REP #imm** (Reset Processor Status): Clears the bits specified by the immediate operand. `REP #0x20` clears M (16-bit accumulator). `REP #0x10` clears X (16-bit index). `REP #0x30` clears both.

The PLP (Pull Processor Status) instruction also modifies M/X by loading the entire P register from the stack, but the value pulled is usually deterministic if you track what was pushed.

### Static Analysis Strategy

The analysis propagates known M/X state through the control flow graph:

```mermaid
stateDiagram-v2
    [*] --> EmulationMode: Reset
    EmulationMode --> NativeMode: CLC + XCE
    NativeMode --> M1X1: SEP #0x30
    NativeMode --> M0X0: REP #0x30
    M1X1 --> M0X1: REP #0x20
    M1X1 --> M1X0: REP #0x10
    M0X0 --> M1X0: SEP #0x20
    M0X0 --> M0X1: SEP #0x10
    M0X1 --> M0X0: REP #0x10
    M0X1 --> M1X1: SEP #0x20
    M1X0 --> M1X1: SEP #0x10
    M1X0 --> M0X0: REP #0x20

    note right of M1X1: A=8-bit, X/Y=8-bit
    note right of M0X0: A=16-bit, X/Y=16-bit
    note right of M0X1: A=16-bit, X/Y=8-bit
    note right of M1X0: A=8-bit, X/Y=16-bit
```

The algorithm works as follows:

1. Start at the entry point. The SNES boots in emulation mode; after the game's initialization code runs `CLC; XCE` to switch to native mode, M and X are typically set to known values by an immediate SEP or REP.
2. At each instruction, check whether it is SEP, REP, or PLP. If so, update the known M/X state.
3. At branch points, propagate the current state to both targets.
4. At merge points (where two control flow paths converge), check whether the incoming states agree. If both paths arrive with M=1, then M=1 at the merge. If one path has M=1 and the other has M=0, the state is **ambiguous**.
5. Iterate until the analysis reaches a fixed point (no more changes propagate).

### Handling Ambiguity

When the static analysis cannot determine the M/X state, the recompiler has two options:

**Option A: Emit runtime checks.** Generate C code that reads the M/X flags at runtime and branches to the correct implementation:

```c
if (ctx->p & 0x20) {
    // M=1: 8-bit accumulator
    ctx->a = (ctx->a & 0xFF00) | (mem_read(addr) & 0xFF);
} else {
    // M=0: 16-bit accumulator
    ctx->a = mem_read(addr) | (mem_read(addr + 1) << 8);
}
```

This is correct but adds overhead. Every ambiguous instruction becomes a branch.

**Option B: Require annotations.** Fail the recompilation and ask the user to provide the M/X state at the ambiguous point. This produces cleaner output but requires human intervention.

In practice, most SNES games follow disciplined patterns -- they set M/X at the top of functions and do not change them across function calls in unpredictable ways. Ambiguity is uncommon in well-structured game code, and when it occurs, it is usually at a small number of points that can be annotated.

---

## 3. LakeSnes Integration

A SNES game is more than its CPU. The SNES has:

- **PPU (Picture Processing Unit)**: Two PPU chips that handle backgrounds (up to 4 layers), sprites, rotation/scaling (Mode 7), and color math.
- **APU (Audio Processing Unit)**: The Sony SPC700 processor and its DSP, running independently with its own 64KB of RAM. Communicates with the main CPU through four 8-bit I/O ports.
- **DMA/HDMA**: Direct Memory Access for bulk data transfer and Horizontal-blanking DMA for per-scanline register updates.

Reimplementing all of this hardware from scratch would be an enormous effort. There is a better approach: **use the recompiled CPU as an orchestrator that drives an existing emulator's hardware**.

LakeSnes is a clean, well-structured SNES emulator written in C. Its architecture separates the CPU from the rest of the hardware cleanly -- the CPU communicates with other components through memory-mapped reads and writes. This separation makes it an ideal candidate for integration.

The pattern works like this:

```mermaid
flowchart TB
    subgraph "Recompiled Code"
        RC["Recompiled 65816 Code\n(Generated C)"]
    end

    subgraph "LakeSnes Hardware"
        PPU["PPU\n(Video Rendering)"]
        APU["APU / SPC700\n(Audio)"]
        DMA["DMA / HDMA\n(Data Transfer)"]
        MMIO["Memory-Mapped I/O\n(Registers)"]
    end

    subgraph "Runtime"
        MEM["Memory Bus\n(Dispatch)"]
        SYNC["Cycle Synchronization"]
    end

    RC -->|"mem_read / mem_write"| MEM
    MEM -->|"0x2100-0x21FF"| PPU
    MEM -->|"0x2140-0x2143"| APU
    MEM -->|"0x4300-0x43FF"| DMA
    MEM -->|"Other I/O"| MMIO
    SYNC -->|"Advance PPU/APU\nby elapsed cycles"| PPU
    SYNC -->|"Advance PPU/APU\nby elapsed cycles"| APU

    style RC fill:#2b6cb0,stroke:#3182ce,color:#fff
    style PPU fill:#975a16,stroke:#b7791f,color:#fff
    style APU fill:#975a16,stroke:#b7791f,color:#fff
    style DMA fill:#975a16,stroke:#b7791f,color:#fff
    style MMIO fill:#975a16,stroke:#b7791f,color:#fff
    style MEM fill:#2f855a,stroke:#38a169,color:#fff
    style SYNC fill:#2f855a,stroke:#38a169,color:#fff
```

The recompiled CPU code replaces LakeSnes's CPU interpreter. When the recompiled code reads or writes a memory address in the I/O range, the memory bus routes that access to LakeSnes's PPU, APU, or DMA implementation. A synchronization layer tracks how many cycles the recompiled code has consumed and advances the PPU and APU accordingly.

The advantages of this approach are significant:

- **Pixel-perfect graphics** without reimplementing the SNES PPU (which is extremely complex, with mode 7 affine transformations, color windowing, mosaic effects, and dozens of edge cases).
- **Accurate audio** without reimplementing the SPC700 DSP.
- **Reduced development time**: You write the recompiler and a thin integration layer, not an entire hardware emulation stack.
- **Proven correctness**: LakeSnes has been tested against hundreds of games and test ROMs. Its PPU and APU implementations are known to be accurate.

The main challenge is cycle synchronization. The SNES PPU and APU run concurrently with the CPU and expect to be advanced at a specific rate. If the recompiled code runs a large block of instructions without yielding to the PPU, mid-frame rendering effects will break. The synchronization layer must insert yield points where the recompiled code "catches up" the hardware to the current cycle count.

---

## 4. SNES Memory Map

The SNES has a 24-bit address space organized into 256 banks of 64KB each. The mapping varies depending on the cartridge type.

### LoROM

In LoROM mapping, ROM data occupies the upper half of banks `0x00-0x7F`:

| Bank Range | Address Range | Maps To |
|---|---|---|
| 0x00-0x3F | 0x0000-0x1FFF | WRAM (first 8KB, mirrored) |
| 0x00-0x3F | 0x2000-0x5FFF | Hardware registers (PPU, APU, DMA) |
| 0x00-0x3F | 0x6000-0x7FFF | Expansion (rarely used) |
| 0x00-0x3F | 0x8000-0xFFFF | ROM (lower 32KB of ROM bank) |
| 0x40-0x6F | 0x0000-0x7FFF | ROM (upper range, varies) |
| 0x40-0x6F | 0x8000-0xFFFF | ROM |
| 0x70-0x7D | 0x0000-0x7FFF | SRAM |
| 0x7E | 0x0000-0xFFFF | WRAM (first 64KB) |
| 0x7F | 0x0000-0xFFFF | WRAM (second 64KB) |
| 0x80-0xFF | | Mirror of 0x00-0x7F |

### HiROM

HiROM maps the full 64KB of each bank to ROM, with hardware registers accessible only through bank 0x00-0x3F:

| Bank Range | Address Range | Maps To |
|---|---|---|
| 0x00-0x3F | 0x0000-0x1FFF | WRAM (first 8KB, mirrored) |
| 0x00-0x3F | 0x2000-0x5FFF | Hardware registers |
| 0x00-0x3F | 0x6000-0x7FFF | Expansion / SRAM |
| 0x00-0x3F | 0x8000-0xFFFF | ROM (same as bank 0x40-0x7D) |
| 0x40-0x7D | 0x0000-0xFFFF | ROM (full 64KB banks) |
| 0x7E-0x7F | 0x0000-0xFFFF | WRAM (128KB) |
| 0x80-0xFF | | Mirror of 0x00-0x7F |

### ExHiROM

ExHiROM extends the address space for ROMs larger than 4MB, using banks `0x40-0x7D` and `0xC0-0xFF` for ROM data. Only a handful of games use this mapping (notably *Tales of Phantasia* and *Star Ocean*).

### DMA and HDMA

**DMA (Direct Memory Access)** transfers blocks of data between any two addresses at high speed, bypassing the CPU. It is commonly used to transfer tile data, palettes, and tilemaps to VRAM during VBlank. The CPU is halted during DMA.

**HDMA (Horizontal-blank DMA)** transfers small amounts of data automatically at the start of each scanline. It is used for per-scanline effects: gradient backgrounds, wavy distortion, parallax scrolling, and color math changes across the screen. HDMA is configured once per frame and runs autonomously.

For the recompiler, DMA is relatively straightforward -- it is a bulk memory copy triggered by writing to specific I/O registers. HDMA is more involved because it operates on a per-scanline basis and the integration layer must ensure it fires at the correct times relative to the PPU's rendering.

---

## 5. Instruction Lifting Specifics

The 65816 has approximately 256 opcodes, but many of them change behavior based on the M/X flags. The lifter must generate width-dependent code.

### Width-Dependent Operations

A simple load instruction changes based on M flag state:

```c
// LDA #imm with M=1 (8-bit accumulator)
ctx->a = (ctx->a & 0xFF00) | imm8;
update_nz_8(ctx, imm8);

// LDA #imm with M=0 (16-bit accumulator)
ctx->a = imm16;
update_nz_16(ctx, imm16);
```

Note that when the accumulator is in 8-bit mode, the high byte of A (sometimes called "B" or the "hidden" byte) is preserved. This is a common source of bugs in recompilers that treat 8-bit mode as simply using a uint8_t.

### ADC and SBC with Decimal Mode

The 65816 supports BCD (Binary-Coded Decimal) arithmetic via the D flag. When the D flag is set, ADC and SBC treat their operands as packed BCD values. This means `0x09 + 0x01 = 0x10` rather than `0x0A`.

```c
// ADC in decimal mode (8-bit)
void adc_decimal_8(Context65816 *ctx, uint8_t operand) {
    uint8_t al = (ctx->a & 0x0F) + (operand & 0x0F) + ctx->flag_c;
    if (al > 9) al += 6;
    uint8_t ah = (ctx->a >> 4) + (operand >> 4) + (al > 0x0F ? 1 : 0);
    if (ah > 9) ah += 6;
    ctx->flag_c = ah > 0x0F;
    ctx->a = (ctx->a & 0xFF00) | ((ah << 4) | (al & 0x0F));
    update_nz_8(ctx, ctx->a & 0xFF);
}
```

Most SNES games do not use decimal mode, but some do (notably sports games for score display). The lifter must handle it correctly.

### MVN and MVP: Block Move Instructions

The 65816 has two block move instructions that copy a range of memory:

- **MVN (Move Negative)**: Copies C+1 bytes from source to destination, incrementing addresses. Used for forward copies.
- **MVP (Move Positive)**: Copies C+1 bytes from source to destination, decrementing addresses. Used for backward copies (when source and destination overlap).

These instructions are unusual because they modify the program counter to re-execute themselves until the byte count (in C register) reaches `0xFFFF`. In the original hardware, the CPU fetches and decodes the same instruction repeatedly.

For the recompiler, the simplest approach is to emit a loop:

```c
// MVN: Move block negative (forward copy)
// src_bank and dst_bank come from the instruction operands
ctx->db = dst_bank;
do {
    uint8_t byte = mem_read((src_bank << 16) | ctx->x);
    mem_write((dst_bank << 16) | ctx->y, byte);
    ctx->x++;
    ctx->y++;
    ctx->a--;  // A is used as the counter (actually C register)
} while (ctx->a != 0xFFFF);
```

This is semantically equivalent to the hardware behavior but executes in a single pass rather than refetching the instruction each iteration.

---

## 6. Real-World Reference

### [snesrecomp](https://github.com/sp00nznet/snesrecomp) -- hardware, not a recompiler

Correct a likely assumption first: snesrecomp does **not** contain a 65816 lifter. It
is two things, and neither generates code.

**The hardware**, as a linkable library. It does not reimplement the PPU, SPC700, DMA
or Mode 7 -- it wraps [LakeSnes](https://github.com/sp00nznet/LakeSnes) (MIT) and
exposes it behind `bus_write8(bank, addr, val)`. Its README states the strategy
directly:

> Chop up an emulator, turn the hardware into libraries, let game-specific projects
> link against them.

**An op kit.** `include/snesrecomp/cpu_ops.h` holds one macro or inline function per
65816 instruction, over a global `g_cpu`. Register width lives there as ordinary
runtime state -- `flag_M` and `flag_X` are booleans that `REP`/`SEP` write and every
width-sensitive op reads -- which is how the module's static M/X tracking problem gets
deferred rather than solved.

Your lifter's job is therefore to decide *which* op to emit with *which* operand. The
semantics are somebody else's already-tested code.

**And it is the interception host.** This is the part to understand before you read any
status claim about a SNES port. `src/recomp_interp.c` runs LakeSnes's timed frame loop
(`snes_runFrame`, real PPU/APU/NMI timing) and installs `g_cpuRecompHook`, which the
emulated CPU calls **at every opcode fetch**. If a recompiled function is registered at
that address, it runs; otherwise the emulator interprets the original 65816 code.

Read the contract in `include/snesrecomp/func_table.h` closely:

> If a recompiled native function is registered for the address, it is called. Otherwise,
> if the interpreter fallback is enabled, the original 65816 code at that address is
> executed on the LakeSnes CPU (see `recomp_interp_call`) and the call still **"succeeds"
> (returns true)**. Only when interpretation is disabled does an unregistered address
> return false.

**The fallback reports success.** With interpretation enabled -- the default -- a project
with zero recompiled functions registered runs the game flawlessly and reports that every
dispatch succeeded. Module 12 shows the GBA toolkit doing the identical thing on top of
mGBA, including silently rolling back functions that crash.

That is not a flaw; it is what makes incremental migration possible. But it means **"the
game is playable" is not a statement about your recompiler**, and any SNES or GBA port
that leads with a screenshot is telling you about the emulator underneath it. The number
that means something is how many functions are registered and passing with the fallback
*off*.

### The pattern that matters: [mk](https://github.com/sp00nznet/mk) (Super Mario Kart)

*Super Mario Kart*, playable end to end -- title, driver select, class and cup select,
a live Mode-7 race, save states, two-player keyboard and gamepad, and lockstep netplay.

To be precise about what that sentence means: **the game plays because LakeSnes is
running the real ROM.** The repository says so -- the recompiled-shell path is "where the
static-recompilation work grows incrementally." Take the playability as evidence that the
*harness* is right, and look elsewhere for evidence about the lifter.

The part to steal is not the game, it is the **migration strategy**. The project runs
in two modes against the same backend:

| Mode | What runs the game |
|---|---|
| real-frame (default) | LakeSnes runs the genuine ROM through its cycle-accurate frame -- **this is the mode the screenshots are from** |
| `SMK_SHELLS=1` | hand-written recompiled functions run where they exist, LakeSnes interprets the rest |

Recompiled functions are declared with `RECOMP_PATCH(name, snes_addr) { ... }` and
auto-register into the dispatch table at static-init time. Adding a translated
function is a one-line change with no central registration list to edit --
`include/snesrecomp/recomp_patch.h` credits N64Recomp's macro of the same name for the
idea.

This is **incremental recompilation**, and it dissolves the worst thing about starting
a recompilation project: you do not need a complete, correct lift before you have
anything that runs. You have a playable game on day one, because the emulator is still
there. You then move it function by function into native C, and at every single commit
the thing still boots. If a recompiled function is wrong, you delete the shell and the
emulator covers it again while you think.

Compare that with the all-or-nothing bring-ups in Modules 27 and 28, where nothing runs
until nearly everything is lifted, and a single bad function is a crash in a 40,000-
function binary. **If your platform has a good open emulator, start this way.**

The same header also documents the modding hook that falls out for free: link a second
object defining a `RECOMP_PATCH` at the same SNES address, and the last constructor to
run wins. Overriding a shipped game function is a link-order question.

### [mariopaint](https://github.com/sp00nznet/mariopaint) -- the best-documented hybrid

*Mario Paint* makes two points, and unlike most ports its source is committed, so you can
check both.

**Peripherals are content.** The title's whole reason to exist was the **SNES Mouse**, so
the port implements the SNES Mouse serial protocol and drives it from your PC mouse. No
amount of PPU accuracy substitutes for that one peripheral.

**And it is honest about being a hybrid.** `src/main/main.c` registers the recompiled
functions, then:

```c
/* Anything not yet recompiled runs the original ROM code on the
 * LakeSnes CPU instead of silently doing nothing. */
recomp_interp_set_enabled(true);
```

The 8,398 lines in `src/recomp/` (`mp_title.c`, `mp_canvas.c`, `mp_tools.c`,
`mp_shapes.c` ...) are hand-translated 65816 routines, and they are doing real work --
the comments explain that the ROM's title loop has no frame sync of its own, so
interpreted it "burns all 2048 iterations instantly with nothing drawn," and the screen
only appears because the recompiled `mp_018260` drives a frame per iteration.

So this is a genuine partial recompilation on an emulator host. Both halves are load-
bearing, and the repository says which is which.

### The A/B lever -- steal this

The same file documents the single best debugging affordance in the SNES corpus:

```c
/*
 * MP_INTERP_FUNCS="018000,0087EE" -- hand specific addresses back to the
 * interpreter even though a recompiled version exists. Registering NULL
 * makes func_table_lookup miss, so dispatch falls through to the genuine
 * ROM code. This is the A/B lever for "is our translation of X wrong?":
 * run it interpreted and see if the symptom goes away.
 */
```

An environment variable that moves any function back to ground truth, one address at a
time, without rebuilding. Paired with `MP_REALFRAME=1`, which runs the genuine ROM
through LakeSnes so you can "capture the same frame both ways and diff," you get a
complete differential workflow for free.

**This is the compensation for the emulator host.** Module 12's GBA toolkit has the same
architecture and none of this instrumentation, which is why its claims are harder to
believe. If you build a hybrid, build the levers that let you prove which half did the
work -- otherwise the emulator underneath makes every result unfalsifiable. Module 18
develops this.

### [3dsnes](https://github.com/sp00nznet/3dsnes) -- and how to measure a corpus

Not a recompilation -- it is a voxel renderer that turns the SNES tile and sprite
output into 3D scenes -- but it is included here for its validation method, which
Module 18 returns to. It reports **340 of 375 games (91%)** drawing a real 3D scene,
and the README is careful about how that number was obtained: an unattended run over
the whole corpus, *"not by spot-checks."*

That distinction is the entire difference between a number you can publish and a number
you cannot. If you cannot re-derive your compatibility figure by running one command
tonight, you do not have a compatibility figure -- you have an impression.

## Lab

The following lab accompanies this module:

- **Lab 7** -- SNES recompilation: Build a 65816 lifter with M/X flag tracking, integrate with LakeSnes for hardware, and recompile a SNES ROM

---

**Next: [Module 12 -- GBA: ARM7TDMI Recompilation](../module-12-gba-arm7/lecture.md)**
