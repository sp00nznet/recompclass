# Broadway (Nintendo Wii) Quick Reference

## Overview

IBM Broadway is the CPU used in the Nintendo Wii. It is architecturally identical to the GameCube's IBM Gekko -- both are based on the PowerPC 750CXe core with paired-singles FPU extensions. The primary difference is clock speed: Broadway runs at 729 MHz versus Gekko's 485 MHz. For the full PowerPC instruction set reference, see **ppc.md**.

- Clock: 729 MHz (Gekko: 485 MHz)
- 32-bit PowerPC instruction encoding
- Big-endian
- In-order execution, 4-stage pipeline
- Hardware FPU with paired-singles extension

---

## Registers

Broadway uses the standard PowerPC register set (identical to Gekko):

| Register Set      | Count | Width   | Description                          |
|-------------------|-------|---------|--------------------------------------|
| GPR (r0-r31)      | 32    | 32-bit  | General purpose                      |
| FPR (f0-f31)      | 32    | 64-bit  | Floating point (double precision)    |
| CR                | 1     | 32-bit  | Condition Register (8 x 4-bit fields)|
| LR                | 1     | 32-bit  | Link Register (return address)       |
| CTR               | 1     | 32-bit  | Count Register (loop/branch target)  |
| XER               | 1     | 32-bit  | Fixed-point exception register       |
| FPSCR             | 1     | 32-bit  | FP status and control                |
| HID0, HID2, etc.  | --    | 32-bit  | Hardware implementation registers    |
| GQR0-GQR7         | 8     | 32-bit  | Graphics quantization registers      |

### Condition Register (CR)

CR contains 8 independent 4-bit fields (CR0-CR7):

| Bit | Meaning           |
|-----|--------------------|
| LT  | Less than          |
| GT  | Greater than       |
| EQ  | Equal              |
| SO  | Summary overflow   |

Compare instructions target a specific CR field. Conditional branches test a specific CR bit. CR logical instructions (crand, cror, crnor, etc.) manipulate individual bits.

### Calling Convention

| Register   | Usage                    |
|------------|--------------------------|
| r0         | Scratch (volatile)       |
| r1         | Stack pointer            |
| r2         | Small data area (SDA2)   |
| r3-r10     | Arguments / return value |
| r11-r12    | Scratch                  |
| r13        | Small data area (SDA)    |
| r14-r31    | Callee-saved             |
| f0         | Scratch                  |
| f1-f13     | FP arguments / return    |
| f14-f31    | Callee-saved             |
| LR         | Return address           |

---

## Paired Singles Extension

The defining feature of Gekko/Broadway that distinguishes them from generic PowerPC. Each 64-bit FPR is treated as two 32-bit single-precision floats (ps0 and ps1), processed in parallel.

### Key Paired Singles Instructions

| Instruction         | Description                              |
|---------------------|------------------------------------------|
| ps_add              | Paired add: fd.ps0 = fa.ps0+fb.ps0, fd.ps1 = fa.ps1+fb.ps1 |
| ps_sub              | Paired subtract                          |
| ps_mul              | Paired multiply                          |
| ps_madd             | Paired multiply-add                      |
| ps_msub             | Paired multiply-subtract                 |
| ps_nmadd            | Paired negative multiply-add             |
| ps_nmsub            | Paired negative multiply-subtract        |
| ps_div              | Paired divide                            |
| ps_res              | Paired reciprocal estimate               |
| ps_rsqrte           | Paired reciprocal square root estimate   |
| ps_sum0             | fd.ps0 = fa.ps0 + fc.ps1, fd.ps1 = fb.ps1 |
| ps_sum1             | fd.ps0 = fa.ps0, fd.ps1 = fb.ps0 + fc.ps1 |
| ps_muls0            | Multiply both by ps0 of second operand  |
| ps_muls1            | Multiply both by ps1 of second operand  |
| ps_madds0/1         | Multiply-add variants using ps0/ps1     |
| ps_merge00          | fd = {fa.ps0, fb.ps0}                   |
| ps_merge01          | fd = {fa.ps0, fb.ps1}                   |
| ps_merge10          | fd = {fa.ps1, fb.ps0}                   |
| ps_merge11          | fd = {fa.ps1, fb.ps1}                   |
| ps_neg              | Negate both elements                     |
| ps_abs              | Absolute value of both elements          |
| ps_mr               | Move register (paired)                   |
| ps_sel              | Paired select (conditional move)         |
| ps_cmpo0/1          | Compare ordered (ps0 or ps1)            |
| ps_cmpu0/1          | Compare unordered (ps0 or ps1)          |

### Quantized Load/Store (psq_l / psq_st)

These instructions load/store paired-singles with hardware dequantization/quantization, controlled by the GQR (Graphics Quantization Register):

| Instruction  | Description                                     |
|--------------|-------------------------------------------------|
| psq_l        | Quantized load: load 1 or 2 values, dequantize  |
| psq_lu       | Quantized load with update (pre-indexed)         |
| psq_st       | Quantized store: quantize, store 1 or 2 values   |
| psq_stu      | Quantized store with update                      |

GQR fields specify:
- **Type:** u8, s8, u16, s16, or float (no conversion)
- **Scale:** 6-bit scale factor for fixed-point conversion

This is heavily used by Nintendo's GX graphics library for vertex data. Integer vertex components (positions, normals, texture coords) are stored compactly in memory and converted to float on load.

---

## Broadway vs Gekko: Differences

| Feature              | Gekko (GameCube)        | Broadway (Wii)           |
|----------------------|-------------------------|--------------------------|
| Clock speed          | 485 MHz                 | 729 MHz                  |
| L1 I-cache           | 32 KB                   | 32 KB                    |
| L1 D-cache           | 32 KB                   | 32 KB                    |
| L2 cache             | 256 KB                  | 256 KB                   |
| Locked cache (DMA)   | 16 KB                   | 16 KB                    |
| ISA                  | PPC 750CXe + PS         | PPC 750CXe + PS          |
| Bus                  | 162 MHz, 64-bit         | 243 MHz, 64-bit          |
| Paired singles       | Yes                     | Yes (identical)          |
| GQR registers        | 8                       | 8                        |

The ISA is identical. A Gekko recompiler works on Broadway without modification. The only differences are clock speed, bus speed, and the surrounding system.

---

## Wii System Architecture

Unlike the GameCube, the Wii adds a separate ARM-based I/O processor called **Starlet** (later known as part of the **IOS** subsystem):

### IOS (ARM I/O Processor)

| Feature     | Detail                                          |
|-------------|-------------------------------------------------|
| CPU         | ARM926EJ-S (ARM9 core, not ARM7TDMI)           |
| Clock       | 243 MHz                                         |
| Role        | Security, I/O, storage, networking              |
| Interaction | Broadway communicates via IPC (inter-processor communication) through shared memory |

**IPC mechanism:**
1. Broadway writes a command to a shared memory location
2. Broadway writes the address to the IPC register (0x0D000000 region)
3. Starlet processes the request (disc read, USB, network, etc.)
4. Starlet signals completion via interrupt

### Wii Memory Map (Key Regions)

| Address Range            | Size    | Description                     |
|--------------------------|---------|---------------------------------|
| 0x00000000 - 0x017FFFFF  | 24 MB   | MEM1 (internal, 1T-SRAM)       |
| 0x10000000 - 0x13FFFFFF  | 64 MB   | MEM2 (external GDDR3)          |
| 0x0C000000 - 0x0C008000  | 32 KB   | Hardware registers              |
| 0x0D000000 - 0x0D00FFFF  | --      | IPC / IOS communication         |
| 0xFFF00000 - 0xFFFFFFFF  | 1 MB    | Boot ROM (1T-SRAM, locked)     |

MEM1 is the same 24 MB that GameCube games see. MEM2 is additional Wii-only memory. GameCube backward-compatibility mode disables MEM2.

---

## Key PPC Instructions (Quick Reference)

For the full instruction reference, see **ppc.md**. The most commonly encountered instructions in Wii game code:

| Category     | Instructions                                    | Notes                          |
|--------------|-------------------------------------------------|--------------------------------|
| Load         | lwz, lhz, lha, lbz, lfs, lfd, lmw              | lwz = load word and zero       |
| Store        | stw, sth, stb, stfs, stfd, stmw                 | stw = store word               |
| Arithmetic   | add, addi, addis, subf, mullw, divw             | addis = add immediate shifted  |
| Logic        | and, andi., or, ori, oris, xor, xori            | "." forms update CR0           |
| Shift/Rotate | slw, srw, sraw, srawi, rlwinm, rlwimi           | rlwinm = rotate and mask       |
| Compare      | cmpw, cmpwi, cmplw, cmplwi                      | Targets a CR field             |
| Branch       | b, bl, blr, bctr, bne, beq, blt, bgt, bdnz      | bl = branch and link           |
| LR/CTR       | mflr, mtlr, mfctr, mtctr                        | Move to/from special regs      |
| Sync         | sync, isync, eieio                               | Memory barriers                |
| System       | sc, rfi, mfmsr, mtmsr                           | Supervisor-level               |

---

## Recompiler Pain Points

Most recompiler challenges for Broadway are identical to Gekko and general PowerPC (see **ppc.md**). Wii-specific concerns:

- **Paired-singles quantized loads/stores:** The psq_l/psq_st instructions with GQR-controlled dequantization are unique to Gekko/Broadway. The GQR registers can change at runtime, making it hard to statically determine the data type and scale. Many recompilers JIT the conversion based on current GQR values and invalidate when GQR changes.
- **Paired-singles semantics:** Each FPR holds two 32-bit floats. Standard PowerPC FPU instructions (fadd, fmul, etc.) operate on ps0 only but may affect ps1 in implementation-defined ways. The recompiler must maintain both slots.
- **IOS interaction:** Broadway communicates with the ARM I/O processor via IPC for disc access, USB, and networking. Recompilers must either HLE these IPC calls or emulate the ARM side.
- **MEM2 access:** Wii games use 64 MB of MEM2 in addition to 24 MB of MEM1. Memory access patterns and DMA differ from GameCube.
- **GameCube backward compatibility:** The Wii can run GameCube games natively, but the memory map and I/O change. A recompiler targeting both must handle the mode difference.
- **Condition Register complexity:** Same as all PowerPC -- 8 independent 4-bit CR fields with CR logical operations. See ppc.md for details.
- **Rotate-and-mask instructions:** rlwinm and rlwimi combine rotation with bit masking. These require careful decomposition on the host. See ppc.md.
- **Big-endian byte order:** Host systems are typically little-endian. All memory accesses must byte-swap.
