# Cell Broadband Engine (PS3) Quick Reference

## Overview

The Cell Broadband Engine (Cell BE) is a heterogeneous multi-core processor designed by Sony, Toshiba, and IBM. It powers the PlayStation 3 and features a unique dual-ISA architecture:

- **PPU (Power Processor Unit):** 1 core, 2 hardware threads, 64-bit PowerPC with VMX
- **SPU (Synergistic Processing Unit):** 6 available to games (7 physical, 1 reserved for OS), independent SIMD processors
- Clock: 3.2 GHz (both PPU and SPUs)
- System RAM: 256 MB XDR main memory + 256 MB GDDR3 video memory

The PPU orchestrates work; SPUs do the heavy computation.

---

## PPU (Power Processor Unit)

### Registers

| Register Set    | Count | Width   | Description                    |
|----------------|-------|---------|--------------------------------|
| GPR (r0-r31)    | 32    | 64-bit  | General purpose                |
| FPR (f0-f31)    | 32    | 64-bit  | Floating point                 |
| VR (v0-v127)    | 128   | 128-bit | VMX/Altivec vector registers   |
| CR              | 1     | 32-bit  | Condition register (8 fields)  |
| LR              | 1     | 64-bit  | Link register                  |
| CTR             | 1     | 64-bit  | Count register                 |
| XER             | 1     | 64-bit  | Fixed-point exception          |

### PPU Key Characteristics

- 64-bit PowerPC ISA with VMX (128 vector registers on Cell vs. standard 32)
- In-order execution (both PPU and SPU)
- Two hardware threads (SMT) sharing one core
- See the PowerPC reference card for the instruction set details

### PPU Calling Convention

| Register   | Usage                    |
|------------|--------------------------|
| r1         | Stack pointer            |
| r2         | TOC (Table of Contents)  |
| r3-r10     | Arguments / return value |
| r14-r31    | Callee-saved             |
| f1-f13     | FP arguments             |
| f14-f31    | FP callee-saved          |
| v2-v13     | Vector arguments         |
| v20-v31    | Vector callee-saved      |

---

## SPU (Synergistic Processing Unit)

### Architecture

- Fully independent processor with its own instruction set
- 128 x 128-bit unified register file (no separate int/float registers)
- 256 KB Local Store (LS) -- all code and data must reside here
- No direct access to main memory; all transfers via DMA
- No hardware branch prediction; software branch hints instead
- In-order, dual-issue pipeline (even/odd pipes)

### SPU Register File

All 128 registers ($0-$127) are 128 bits wide. They are interpreted based on the instruction:

| Interpretation     | Elements per Register |
|--------------------|-----------------------|
| 16 x byte          | Packed bytes          |
| 8 x halfword       | Packed 16-bit ints    |
| 4 x word           | Packed 32-bit ints    |
| 2 x doubleword     | Packed 64-bit ints    |
| 4 x float          | Packed 32-bit floats  |
| 2 x double         | Packed 64-bit doubles |

**Preferred slot:** The SPU has a concept of "preferred slot" -- element 0 is the leftmost (highest address) word. Scalar operations use the preferred slot (word 0 in big-endian layout).

### SPU Instruction Format

Fixed 32-bit instructions. Main formats:

| Format | Layout                                          |
|--------|-------------------------------------------------|
| RR     | opcode(11) | rB(7) | rA(7) | rT(7)             |
| RRR    | opcode(4) | rT(7) | rB(7) | rA(7) | rC(7)     |
| RI7    | opcode(11) | imm7(7) | rA(7) | rT(7)           |
| RI10   | opcode(8) | imm10(10) | rA(7) | rT(7)          |
| RI16   | opcode(9) | imm16(16) | rT(7)                  |
| RI18   | opcode(7) | imm18(18) | rT(7)                  |

### Key SPU Instructions

| Category     | Instructions                              | Notes                          |
|--------------|-------------------------------------------|--------------------------------|
| Load/Store   | lqd, lqx, lqa, lqr, stqd, stqx, stqa, stqr | Quadword (16-byte) aligned  |
| Integer      | a, ai, sf, sfi, mpya, mpyu, mpyh          | a=add, sf=subtract from       |
| Shift        | shl, shlh, shlhi, rotm, rothm, rot, roth  | Word/halfword variants        |
| Logic        | and, andi, or, ori, xor, xori, nand, nor  |                                |
| Compare      | ceq, ceqh, ceqb, cgt, cgth, cgtb, clgt   | Element-wise compare          |
| Select       | selb                                       | Bitwise select (mux)          |
| Shuffle      | shufb                                      | Byte shuffle with pattern     |
| Float        | fa, fs, fm, fma, fnms, frest, frsqest     | fma = multiply-add            |
| Double       | dfa, dfs, dfm, dfma                        | Double-precision              |
| Convert      | cflts, cfltu, csflt, cuflts               | Float <-> int conversions     |
| Branch       | br, bra, brsl, brasl                       | Relative/absolute, with link  |
| Cond Branch  | brz, brnz, brhz, brhnz, bi, biz, binz    | Test word/halfword for zero   |
| Branch Hint  | hbr, hbra, hbrr                            | Software branch prediction    |
| Channel      | rdch, wrch, rchcnt                         | Read/write MFC channels       |
| Stop         | stop, stopd                                | Halt SPU execution            |

### SPU Dual-Issue Pipeline

The SPU has two execution pipes:

| Pipe | Executes                                        |
|------|-------------------------------------------------|
| Even | Arithmetic, logic, shifts, float, byte ops      |
| Odd  | Load/store, branches, shuffle, channel ops       |

Two instructions can issue per cycle if one is even-pipe and the other is odd-pipe.

---

## DMA and MFC (Memory Flow Controller)

Each SPU has an MFC that handles DMA between Local Store and main memory.

### DMA Commands (issued via channel writes)

| Command | Description                           |
|---------|---------------------------------------|
| GET     | Main memory -> Local Store            |
| PUT     | Local Store -> Main memory            |
| GETL    | GET with list (scatter-gather)        |
| PUTL    | PUT with list (scatter-gather)        |

### DMA Parameters

| Parameter     | Description                          |
|---------------|--------------------------------------|
| Local Address | Offset in 256 KB Local Store         |
| EA            | Effective address in main memory     |
| Size          | Transfer size (up to 16 KB)          |
| Tag           | 0-31, used for completion tracking   |
| Class ID      | Command class                        |

### DMA Completion

```
wrch $MFC_WrTagMask, tag_mask    -- select tag(s) to wait for
wrch $MFC_WrTagUpdate, 2         -- 2 = wait for all selected
rdch $MFC_RdTagStat              -- blocks until complete
```

### Key MFC Channels

| Channel              | Number | Direction | Description             |
|----------------------|--------|-----------|-------------------------|
| MFC_WrMSSyncReq     | 9      | Write     | Memory sync request     |
| MFC_LSA              | 16     | Write     | Local Store address     |
| MFC_EAH              | 17     | Write     | EA high 32 bits         |
| MFC_EAL              | 18     | Write     | EA low 32 bits          |
| MFC_Size             | 19     | Write     | Transfer size           |
| MFC_TagID            | 20     | Write     | Tag ID (0-31)           |
| MFC_Cmd              | 21     | Write     | DMA command             |
| MFC_WrTagMask        | 22     | Write     | Tag mask for waiting    |
| MFC_WrTagUpdate      | 23     | Write     | Tag status update mode  |
| MFC_RdTagStat        | 24     | Read      | Tag status (blocking)   |
| SPU_RdInMbox         | 29     | Read      | Read from PPU mailbox   |
| SPU_WrOutMbox        | 28     | Write     | Write to PPU mailbox    |
| SPU_WrOutIntrMbox    | 30     | Write     | Write + interrupt PPU   |

---

## PS3 System Overview

```
+------------------+     XDR Bus      +------------------+
|   PPU (2 threads)|<================>|  256 MB XDR RAM  |
+------------------+                  +------------------+
        |
        | Element Interconnect Bus (EIB) -- 204.8 GB/s ring
        |
 +------+------+------+------+------+------+
 | SPU0 | SPU1 | SPU2 | SPU3 | SPU4 | SPU5 |  (6 available)
 | 256KB| 256KB| 256KB| 256KB| 256KB| 256KB|  Local Stores
 +------+------+------+------+------+------+
        |
        | FlexIO
        |
+------------------+
|   RSX GPU        |<===> 256 MB GDDR3
+------------------+
```

---

## Recompiler Pain Points

- **Dual ISA:** The PPU and SPU have completely different instruction sets. A PS3 recompiler must implement two separate recompilation backends (or at minimum interpret one ISA).
- **Local Store management:** SPU code and data share the 256 KB Local Store. Programs frequently overlay code segments, loading new code via DMA. The recompiler must detect code changes in the LS and invalidate translated blocks.
- **DMA scheduling:** SPUs access main memory exclusively through DMA. DMA transfers are asynchronous and tagged. Correct emulation requires modeling the MFC command queue and tag-based synchronization.
- **SPU branch hints:** The SPU has no hardware branch predictor. Instead, `hbr`/`hbra`/`hbrr` instructions inform the pipeline of upcoming branches. While a recompiler can ignore hints for correctness, they indicate control flow patterns useful for optimization.
- **SPU preferred slot:** Scalar operations work on the "preferred slot" (element 0). Moving data between slots requires shuffle instructions. This is a key performance concern when mapping to host SIMD.
- **SPU dual-issue scheduling:** Peak performance requires pairing even-pipe and odd-pipe instructions. An optimizing recompiler should attempt to preserve this scheduling.
- **HLE modules:** The PS3 system software exposes approximately 93 modules (syscalls, PRX libraries) that games link against. Functions like cellGcmInit, cellSpurs, cellFs, cellSysutil, etc. must be implemented via high-level emulation. This is a massive API surface.
- **VMX on PPU:** The PPU's 128 VMX registers (vs. standard 32) require careful register allocation on the host.
- **Memory model:** The PPU is weakly ordered. SPU local store is strongly ordered but DMA interactions with main memory require explicit barriers (MFC fences/barriers).
- **SPU thread management:** Games create and manage SPU threads via SPURS or raw SPU thread APIs. The recompiler/emulator must schedule SPU execution across host cores.
