# PowerPC (Xbox 360 / GameCube) Quick Reference

## Overview

PowerPC is a RISC architecture used in multiple console generations. The GameCube/Wii use the IBM Gekko/Broadway (32-bit PowerPC with paired-singles FPU). The Xbox 360 uses the Xenon (3-core 64-bit PowerPC with VMX/Altivec). The PS3's PPU is also PowerPC-based (covered in the Cell reference).

- Fixed 32-bit instruction encoding
- Big-endian (bi-endian capable but consoles use big-endian)
- Load/store architecture

---

## Registers

| Register Set      | Count | Width   | Description                         |
|-------------------|-------|---------|-------------------------------------|
| GPR (r0-r31)      | 32    | 32/64   | General purpose                     |
| FPR (f0-f31)      | 32    | 64-bit  | Floating point (double precision)   |
| CR                | 1     | 32-bit  | Condition Register (8 x 4-bit fields)|
| LR                | 1     | 32/64   | Link Register (return address)      |
| CTR               | 1     | 32/64   | Count Register (loop counter/branch)|
| XER               | 1     | 32-bit  | Fixed-point exception register      |
| FPSCR             | 1     | 32-bit  | FP status and control               |

### Condition Register (CR) Fields

CR is divided into 8 fields (CR0-CR7), each with 4 bits:

| Bit | Meaning                  |
|-----|--------------------------|
| LT  | Less than                |
| GT  | Greater than             |
| EQ  | Equal                    |
| SO  | Summary overflow         |

Compare instructions target a specific CR field. Branches test a specific CR bit.

---

## Instruction Format

All instructions are 32 bits, aligned on 4-byte boundaries.

Common formats:
- **D-form:** opcode | rD | rA | immediate(16)
- **X-form:** opcode | rD | rA | rB | extended opcode
- **I-form:** opcode | LI(24) | AA | LK (branch)
- **B-form:** opcode | BO | BI | BD(14) | AA | LK (conditional branch)

---

## Key Instructions

| Category     | Instructions                                    | Notes                          |
|--------------|-------------------------------------------------|--------------------------------|
| Load         | lwz, lhz, lha, lbz, lfd, lfs, lmw              | lwz = load word and zero       |
| Store        | stw, sth, stb, stfd, stfs, stmw                 | stw = store word               |
| Load/Store Update | lwzu, stwu, lfdu, etc.                     | Pre-indexed: updates rA        |
| Arithmetic   | add, addi, addis, subf, mullw, divw, neg        | addis = add immediate shifted  |
| Logic        | and, andi., or, ori, oris, xor, xori, nand, nor | "." forms update CR0           |
| Shift/Rotate | slw, srw, sraw, srawi, rlwinm, rlwimi           | rlwinm = rotate and mask       |
| Compare      | cmpw, cmpwi, cmplw, cmplwi                      | Targets a CR field             |
| Branch       | b, bl, ba, bla                                   | bl = branch and link           |
| Cond Branch  | bne, beq, blt, bgt, ble, bge, bdnz              | Mnemonics for bc instruction   |
| Link/Count   | blr, bctr, bctrl, blrl                           | Branch to LR or CTR            |
| LR/CTR       | mflr, mtlr, mfctr, mtctr                        | Move to/from special regs      |
| System       | sc, rfi, mfmsr, mtmsr, mfspr, mtspr             | Supervisor-level               |
| Sync         | sync, isync, eieio                               | Memory barriers                |

### Record Bit (".")

Many instructions have a "." variant (e.g., `add.`, `and.`) that updates CR0 based on the result. This is encoded as bit 31 of the instruction word.

---

## VMX / Altivec (Xbox 360 Xenon)

128 vector registers (VR0-VR127 on Xenon; 32 on standard Altivec).

Each register holds 128 bits, interpretable as:

| Interpretation   | Elements        |
|------------------|-----------------|
| 16 x byte        | Packed bytes    |
| 8 x halfword     | Packed shorts   |
| 4 x word         | Packed ints     |
| 4 x float        | Packed floats   |

Key VMX instructions:

| Instruction     | Description                        |
|-----------------|------------------------------------|
| lvx, stvx       | Load/store vector (128-bit aligned)|
| vaddsws         | Vector add signed word saturate    |
| vmaddfp         | Vector multiply-add float          |
| vperm           | Vector permute (byte shuffle)      |
| vsel            | Vector select (bitwise mux)        |
| vcmpgtfp.       | Vector compare greater-than float  |
| vand, vor, vxor | Vector bitwise operations          |
| vsldoi          | Vector shift left double by octet  |

---

## Gekko / Broadway Paired Singles (GameCube / Wii)

The Gekko extends PowerPC with "paired singles" -- each FPR holds two 32-bit floats processed in parallel. Key instructions:

| Instruction      | Description                        |
|------------------|------------------------------------|
| ps_add           | Paired add                         |
| ps_mul           | Paired multiply                    |
| ps_madd          | Paired multiply-add                |
| ps_merge00/01/10/11 | Merge elements between pairs   |
| psq_l, psq_st   | Quantized load/store (GX vertex)   |

---

## Calling Convention (System V / Xenon)

| Register   | Usage                    |
|------------|--------------------------|
| r0         | Scratch (volatile)       |
| r1         | Stack pointer            |
| r2         | TOC pointer (64-bit)     |
| r3-r10     | Arguments / return       |
| r11-r12    | Scratch                  |
| r13        | Small data area pointer  |
| r14-r31    | Callee-saved             |
| f0         | Scratch                  |
| f1-f13     | FP arguments / return    |
| f14-f31    | Callee-saved             |
| LR         | Return address           |

---

## Recompiler Pain Points

- **Condition Register complexity:** CR has 8 independent 4-bit fields. Any field can be targeted by compares, and any bit can be tested by branches. CR logical instructions (crand, cror, etc.) operate on individual bits. Mapping this to x86 flags is nontrivial.
- **Link Register / CTR branching:** Indirect branches via LR (blr) and CTR (bctr) require tracking these registers. `bdnz` decrements CTR and branches if nonzero -- a loop construct with no direct x86 equivalent.
- **Paired Singles (Gekko):** The quantized load/store instructions (psq_l/psq_st) with scale/type fields are unique to GameCube/Wii and require special handling.
- **VMX/Altivec (Xenon):** 128 vector registers and SIMD operations must be mapped to host SIMD (SSE/AVX/NEON). The `vperm` instruction is particularly powerful and hard to emulate efficiently.
- **Rotate-and-mask instructions:** `rlwinm` and `rlwimi` combine rotation with bit masking in a single instruction. Very flexible but requires careful decomposition on the host.
- **Memory ordering:** `sync`, `isync`, and `eieio` have specific memory barrier semantics important for multi-core (Xenon) recompilation.
- **Big-endian byte order:** Host systems are typically little-endian. All memory accesses must byte-swap unless the recompiler maintains a byte-swapped memory image.
