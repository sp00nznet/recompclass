# SH-4 (Dreamcast) Quick Reference

## Overview

The Hitachi (now Renesas) SH-4 is a 32-bit RISC processor used in the Sega Dreamcast. It features fixed 16-bit instruction encoding (compact code density), a 5-stage pipeline, and hardware FPU with both single and double precision modes.

- Clock: 200 MHz
- 16-bit instruction encoding (Thumb-like density)
- Little-endian (configurable, Dreamcast uses little-endian)
- 4 GB virtual address space with MMU

---

## Registers

### General Purpose Registers

| Register  | Description                            |
|-----------|----------------------------------------|
| R0 - R7   | General purpose (R0 has special roles) |
| R8 - R15  | General purpose                        |

R0 is special: used as index in some addressing modes (e.g., @(disp, R0), @(R0, Rn)) and as the implicit destination for certain instructions.

### Special Registers

| Register | Description                                |
|----------|--------------------------------------------|
| PC       | Program counter                            |
| PR       | Procedure register (return address)        |
| SR       | Status register (flags, mode bits)         |
| GBR      | Global base register (for @(disp, GBR))   |
| VBR      | Vector base register (exception table)     |
| MACH     | Multiply-accumulate high                   |
| MACL     | Multiply-accumulate low                    |
| FPSCR    | FPU status/control register                |
| FPUL     | FPU communication register (FPU <-> GPR)  |

### Floating Point Registers

| Register Set | Count | Width  | Description                     |
|-------------|-------|--------|---------------------------------|
| FR0 - FR15  | 16    | 32-bit | Single-precision bank 0         |
| DR0 - DR14  | 8     | 64-bit | Double-precision pairs (even)   |
| FV0 - FV12  | 4     | 128-bit| 4-element float vectors         |
| XF0 - XF15  | 16    | 32-bit | Single-precision bank 1         |
| XMTRX       | 1     | 4x4    | Matrix in XF bank               |

The FPSCR.FR bit swaps which bank is active (FR vs XF).

### Status Register (SR)

| Bit(s)  | Name | Description                          |
|---------|------|--------------------------------------|
| 0       | T    | True/false (condition bit)           |
| 1       | S    | Specifies saturation for MAC        |
| 4       | IMASK| Interrupt mask (4 bits, 3:0)        |
| 9       | Q    | Used by DIV1 instruction            |
| 8       | M    | Used by DIV1 instruction            |
| 28      | RB   | Register bank select (0 or 1)       |
| 29      | BL   | Block interrupts                    |
| 30      | FD   | FPU disable                         |
| 31      | MD   | Processor mode (0=user, 1=priv)     |

---

## Addressing Modes

| Mode                    | Syntax          | Description                    |
|-------------------------|-----------------|--------------------------------|
| Register direct         | Rn              | Value in register              |
| Register indirect       | @Rn             | Memory at address in Rn        |
| Post-increment          | @Rn+            | Access then Rn += size         |
| Pre-decrement           | @-Rn            | Rn -= size then access         |
| Displacement            | @(disp, Rn)     | Rn + disp (scaled by op size)  |
| Indexed                 | @(R0, Rn)       | R0 + Rn                       |
| GBR displacement        | @(disp, GBR)    | GBR + disp                    |
| GBR indexed             | @(R0, GBR)      | R0 + GBR                      |
| PC-relative             | @(disp, PC)     | PC + 4 + disp (for MOV)       |

Note: Displacements are small (4-8 bits) and scaled by operand size (x1, x2, or x4).

---

## Key Instructions

| Category    | Instructions                                     | Notes                           |
|-------------|--------------------------------------------------|---------------------------------|
| Data Move   | MOV, MOV.B, MOV.W, MOV.L, MOVA                  | MOVA = move effective address   |
| Arithmetic  | ADD, ADDC, ADDV, SUB, SUBC, SUBV, NEG, NEGC     | C variants use/set T bit       |
| Multiply    | MUL.L, MULS.W, MULU.W, DMULS.L, DMULU.L        | Results in MACL (and MACH)     |
| MAC         | MAC.W, MAC.L                                      | Multiply-accumulate            |
| Logic       | AND, OR, XOR, NOT, TST                            | TST sets T bit                 |
| Shift       | SHLL, SHLR, SHAL, SHAR, ROTL, ROTR, ROTCL, ROTCR| Single-bit shifts              |
| Shift (n)   | SHLL2, SHLL8, SHLL16, SHLR2, SHLR8, SHLR16     | Fixed multi-bit shifts         |
| Compare     | CMP/EQ, CMP/GE, CMP/GT, CMP/HI, CMP/HS, CMP/PL, CMP/PZ, CMP/STR | Set T bit |
| Branch      | BT, BF, BT/S, BF/S                               | Branch if T set/clear; /S = delay slot |
| Jump        | BRA, BSR, BRAF, BSRF, JMP, JSR                   | BRA/BSR/JMP/JSR have delay slots|
| Return      | RTS, RTE                                           | RTS has delay slot             |
| T-bit       | SETT, CLRT, MOVT                                  | Manipulate T flag              |
| System      | TRAPA, SLEEP, NOP                                 |                                |
| FPU         | FADD, FSUB, FMUL, FDIV, FMAC, FCMP/EQ, FCMP/GT | Single or double per FPSCR.PR |
| FPU Move    | FMOV, FLDS, FSTS, FLOAT, FTRC                    | FTRC = truncate to int         |
| FPU Vector  | FIPR, FTRV                                         | Inner product, matrix transform|
| Byte Swap   | SWAP.B, SWAP.W                                     | Byte/word swap in register     |
| Extend      | EXTS.B, EXTS.W, EXTU.B, EXTU.W                    | Sign/zero extend               |
| Div         | DIV0S, DIV0U, DIV1                                 | Multi-step division using M/Q/T|

---

## Delay Slots

The following instructions have a **delay slot** (the instruction after them always executes):

- BRA, BSR, BRAF, BSRF, JMP, JSR, RTS, RTE
- BT/S, BF/S (delayed conditional branch)

The non-delayed conditional branches (BT, BF) do NOT have delay slots.

```
BRA target
MOV R0, R1       <-- delay slot: always executes
```

---

## Dreamcast Memory Map (Key Regions)

| Address Range         | Description                |
|-----------------------|----------------------------|
| 0x00000000-0x001FFFFF | Boot ROM (2 MB)           |
| 0x04000000-0x04FFFFFF | VRAM (8 MB, 64-bit bus)   |
| 0x0C000000-0x0CFFFFFF | System RAM (16 MB)         |
| 0x0E000000-0x0EFFFFFF | System RAM mirror          |
| 0x10000000-0x107FFFFF | Tile accelerator (TA)     |
| 0xFF000000-0xFFFFFFFF | On-chip I/O, cache, store queue |

### Store Queues (SQ)

0xE0000000-0xE3FFFFFF -- Two 32-byte store queues for burst DMA writes. Used extensively by games for fast PVR2 transfers. Trigger by writing to the SQ region.

---

## Recompiler Pain Points

- **Delay slots:** BRA, BSR, JMP, JSR, RTS, and delayed conditional branches (BT/S, BF/S) all have delay slots. Since there are also non-delayed branches (BT, BF), the recompiler must distinguish between them.
- **Banked registers:** SR.RB swaps R0-R7 between two physical banks. Kernel code uses banked registers for fast exception handling. The recompiler must track which bank is active.
- **FPU precision modes:** FPSCR.PR toggles between single (32-bit) and double (64-bit) precision for all FPU operations. FPSCR.SZ toggles transfer size. Same opcodes, different behavior.
- **FPU bank switching:** FPSCR.FR swaps the FR and XF register banks. FTRV (matrix transform) uses the inactive bank as a matrix.
- **DIV1 multi-step division:** Division is performed by repeated DIV1 instructions using the M, Q, and T bits. This is a 32-iteration loop for 32-bit division and requires precise flag tracking.
- **T-bit as condition flag:** All comparisons and conditions flow through the single T bit. Branches test only T. This is simpler than x86 flags but requires careful T-bit tracking since many instructions modify it.
- **16-bit instruction encoding:** The compact encoding means small displacement fields, leading to heavy use of PC-relative loads from literal pools. The recompiler must identify and handle these constant loads.
- **Store queues:** The SQ mechanism requires special memory-mapped write handling for fast DMA to VRAM.
