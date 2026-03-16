# SH-2 (Sega Saturn) Quick Reference

## Overview

The Hitachi (now Renesas) SH-2 is a 32-bit RISC processor used in the Sega Saturn as a dual-CPU configuration: SH2 master (28.6 MHz) and SH2 slave (28.6 MHz). It also appears in the Sega 32X add-on (2x SH-2 at 23 MHz). The SH-2 uses fixed 16-bit instruction encoding for excellent code density, similar to the later SH-4 used in the Dreamcast.

- Clock: 28.6 MHz (Saturn), 23 MHz (32X)
- 16-bit instruction encoding, 32-bit data path
- Big-endian
- 5-stage pipeline

---

## Registers

### General Purpose Registers

| Register  | Description                             |
|-----------|-----------------------------------------|
| R0 - R14  | General purpose (R0 has special roles)  |
| R15       | Stack pointer (by convention)           |

R0 is special: used as source/destination in many immediate and displacement addressing modes (e.g., `MOV.L @(disp, R0), Rn`).

### Special Registers

| Register | Description                                 |
|----------|---------------------------------------------|
| PC       | Program counter                             |
| PR       | Procedure register (return address for BSR/JSR) |
| SR       | Status register (flags and mode bits)       |
| GBR      | Global base register (for peripheral I/O)  |
| VBR      | Vector base register (exception table base) |
| MACH     | Multiply-accumulate high (upper 32 bits)    |
| MACL     | Multiply-accumulate low (lower 32 bits)     |

### Status Register (SR)

| Bit(s) | Name  | Description                              |
|--------|-------|------------------------------------------|
| 0      | T     | True/false condition bit                 |
| 1      | S     | Specifies saturation for MAC operations  |
| 4:7    | IMASK | Interrupt mask level (0-15)              |
| 9      | Q     | Used by DIV1 instruction                 |
| 8      | M     | Used by DIV1 instruction                 |

The T bit serves as the sole condition flag. All comparisons set T, and conditional branches test only T.

---

## Addressing Modes

| Mode                    | Syntax          | Description                       |
|-------------------------|-----------------|-----------------------------------|
| Register direct         | Rn              | Value in register                 |
| Register indirect       | @Rn             | Memory at address in Rn           |
| Post-increment          | @Rn+            | Access then Rn += operand size    |
| Pre-decrement           | @-Rn            | Rn -= operand size then access    |
| Displacement            | @(disp, Rn)     | Rn + disp (scaled by op size)     |
| Indexed                 | @(R0, Rn)       | R0 + Rn                          |
| GBR displacement        | @(disp, GBR)    | GBR + disp (scaled)              |
| GBR indexed             | @(R0, GBR)      | R0 + GBR                         |
| PC-relative             | @(disp, PC)     | PC + 4 + disp (for MOV, scaled)  |
| Immediate               | #imm            | 8-bit sign-extended immediate     |

**Displacement sizes are small:** Typically 4-8 bits, scaled by operand size (x1 for byte, x2 for word, x4 for long). This forces heavy use of PC-relative constant pool loads for larger values.

---

## Key Instructions

| Category    | Instructions                                     | Notes                           |
|-------------|--------------------------------------------------|---------------------------------|
| Data Move   | MOV, MOV.B, MOV.W, MOV.L, MOVA                  | MOVA = move aligned address     |
| Arithmetic  | ADD, ADDC, ADDV, SUB, SUBC, SUBV, NEG, NEGC     | C variants carry through T      |
| Multiply    | MUL.L, MULS.W, MULU.W, DMULS.L, DMULU.L        | Results in MACL (and MACH)      |
| MAC         | MAC.W, MAC.L                                      | Multiply-accumulate             |
| Logic       | AND, OR, XOR, NOT, TST                            | TST sets T bit without storing  |
| Shift       | SHLL, SHLR, SHAL, SHAR, ROTL, ROTR, ROTCL, ROTCR| Single-bit shifts               |
| Shift (n)   | SHLL2, SHLL8, SHLL16, SHLR2, SHLR8, SHLR16     | Fixed multi-bit shifts          |
| Compare     | CMP/EQ, CMP/GE, CMP/GT, CMP/HI, CMP/HS, CMP/PL, CMP/PZ, CMP/STR | All set T bit |
| Branch      | BT, BF, BT/S, BF/S                               | Branch if T set/clear; /S = delay slot |
| Jump        | BRA, BSR, BRAF, BSRF, JMP, JSR                   | All have delay slots            |
| Return      | RTS, RTE                                           | Both have delay slots           |
| T-bit       | SETT, CLRT, MOVT                                  | Direct T manipulation           |
| System      | TRAPA, SLEEP, NOP                                 |                                 |
| Byte Swap   | SWAP.B, SWAP.W                                     | Byte/word swap in register      |
| Extend      | EXTS.B, EXTS.W, EXTU.B, EXTU.W                    | Sign/zero extend                |
| Division    | DIV0S, DIV0U, DIV1                                 | Multi-step division             |
| Misc        | DT                                                 | Decrement and set T if zero     |

### DT (Decrement and Test)

`DT Rn` decrements Rn by 1 and sets T=1 if the result is zero. This is the SH-2's loop-counter instruction:

```
    MOV     #10, R3       ; loop count
loop:
    ; ... loop body ...
    DT      R3            ; R3--; T = (R3 == 0)
    BF      loop          ; branch if T == 0
    NOP                   ; delay slot
```

---

## Delay Slots

All branch and jump instructions on the SH-2 have a delay slot -- the instruction immediately following them always executes:

- BRA, BSR, BRAF, BSRF, JMP, JSR, RTS, RTE
- BT/S, BF/S (delayed conditional branch)

The non-delayed conditional branches (BT, BF) do **not** have delay slots.

```
BRA     target
MOV     R0, R1         ; delay slot: always executes before branch takes effect
```

**No branch in a delay slot.** Placing a branch or another delay-slot instruction in a delay slot is undefined behavior.

---

## MAC (Multiply-Accumulate) Operations

The SH-2 has dedicated multiply-accumulate support using MACH:MACL as a 64-bit accumulator:

| Instruction | Operation                                    |
|-------------|----------------------------------------------|
| MAC.W @Rm+, @Rn+ | MACH:MACL += (signed 16-bit @Rm) * (signed 16-bit @Rn); auto-increment both |
| MAC.L @Rm+, @Rn+ | MACH:MACL += (signed 32-bit @Rm) * (signed 32-bit @Rn); auto-increment both |

When SR.S = 1, MAC.W saturates to a 32-bit result in MACL. These instructions are used heavily in audio DSP code on the Saturn.

---

## GBR-Relative Addressing

GBR (Global Base Register) provides efficient access to I/O registers and global data:

| Instruction              | Operation                        |
|--------------------------|----------------------------------|
| MOV.B @(disp, GBR), R0  | R0 = byte at GBR + disp         |
| MOV.W @(disp, GBR), R0  | R0 = word at GBR + disp         |
| MOV.L @(disp, GBR), R0  | R0 = long at GBR + disp         |
| AND.B #imm, @(R0, GBR)  | Byte AND at R0+GBR              |
| OR.B  #imm, @(R0, GBR)  | Byte OR at R0+GBR               |
| XOR.B #imm, @(R0, GBR)  | Byte XOR at R0+GBR              |
| TST.B #imm, @(R0, GBR)  | Test byte at R0+GBR, set T      |

Note: GBR-relative loads always target R0. This is a common source of register-allocation constraints.

---

## Saturn Memory Map (Key Regions)

| Address Range           | Description                     |
|-------------------------|---------------------------------|
| 0x00000000 - 0x0007FFFF | BIOS ROM (512 KB)              |
| 0x00100000 - 0x0010007F | SMPC registers                 |
| 0x00180000 - 0x0018FFFF | Backup RAM (64 KB)             |
| 0x00200000 - 0x002FFFFF | Work RAM Low (1 MB)            |
| 0x01000000 - 0x017FFFFF | Cartridge expansion            |
| 0x02000000 - 0x03FFFFFF | CD-ROM access                  |
| 0x05A00000 - 0x05AFFFFF | VDP1 VRAM (512 KB)            |
| 0x05C00000 - 0x05C7FFFF | VDP2 VRAM (512 KB)            |
| 0x05E00000 - 0x05EFFFFF | VDP2 CRAM (color RAM, 4 KB)   |
| 0x05F00000 - 0x05FFFFFF | VDP2 registers                 |
| 0x06000000 - 0x060FFFFF | Work RAM High (1 MB)           |

The master and slave SH-2s share the same address space but can contend on bus access. Work RAM High is faster for the master CPU.

---

## Comparison: SH-2 vs SH-4

The SH-4 (used in the Dreamcast, covered in sh4.md) is a direct descendant. Key differences:

| Feature              | SH-2                         | SH-4                              |
|----------------------|------------------------------|------------------------------------|
| Clock                | 28.6 MHz                     | 200 MHz                           |
| Pipeline             | 5-stage                      | 5-stage (superscalar, 2-issue)    |
| FPU                  | None (no hardware float)     | Full FPU (single + double)        |
| FP vector ops        | None                         | FIPR, FTRV (dot product, matrix)  |
| FP register banks    | None                         | 2 banks (FR/XF, swapped via FPSCR.FR) |
| MMU                  | None                         | Full TLB-based MMU                |
| Cache                | None                         | 8 KB I-cache, 16 KB operand cache |
| Store queues         | None                         | 2x 32-byte SQ for burst DMA      |
| Banked GPRs          | None                         | 2 banks of R0-R7 (via SR.RB)     |
| FPSCR                | N/A                          | Controls FP precision, rounding, bank |
| BRAF/BSRF            | Present                      | Present                           |
| Instruction encoding | 16-bit fixed                 | 16-bit fixed (same base ISA)     |

If you've built an SH-4 recompiler, the SH-2 integer core is a strict subset -- remove FPU handling, banked registers, MMU, cache, and store queues.

---

## Recompiler Pain Points

- **Delay slots:** Every branch and jump instruction has a delay slot. The recompiler must always fetch and execute the instruction after a branch before transferring control. BT/BF (non-delayed) are the exception.
- **Dual-CPU synchronization:** The Saturn runs two SH-2s in parallel sharing the same address space. Correct recompilation requires either lock-step emulation or careful handling of shared memory synchronization.
- **T-bit as sole condition flag:** All comparisons flow through the single T bit. This is simpler than multi-flag architectures but the recompiler must track T-bit state precisely since many instructions (ADDC, SUBC, ROTCL, DT, etc.) modify it.
- **DIV1 multi-step division:** 32-bit division is performed by 32 iterations of DIV1, using M, Q, and T bits. The recompiler can either emulate each step or pattern-match the division loop and replace it with a native divide.
- **PC-relative constant pools:** The 16-bit instruction encoding forces use of nearby literal pools for 32-bit constants. The recompiler must identify `MOV.L @(disp, PC), Rn` loads and resolve the constants at translation time.
- **MAC saturation:** When SR.S=1, MAC.W saturates results. The recompiler must check the S bit to determine MAC behavior.
- **R0 constraints:** Many addressing modes implicitly use or target R0, making register allocation around these instructions tricky.
- **Bus contention (Saturn):** Master and slave SH-2 CPUs contend for bus access. Timing-sensitive code may depend on bus arbitration behavior that is difficult to recompile accurately.
