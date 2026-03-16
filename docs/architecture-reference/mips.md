# MIPS (N64) Quick Reference

## Overview

The Nintendo 64 uses the NEC VR4300, a MIPS III 64-bit processor. In practice, most N64 code uses 32-bit operations. MIPS is a RISC architecture with fixed 32-bit instruction encoding, a load/store design, and a notable quirk: **branch delay slots**.

- Clock: 93.75 MHz
- 32-bit and 64-bit operation modes
- 5-stage pipeline

---

## Registers

| Number | Name    | Convention                    |
|--------|---------|-------------------------------|
| $0     | $zero   | Hardwired to zero             |
| $1     | $at     | Assembler temporary           |
| $2-$3  | $v0-$v1 | Return values                 |
| $4-$7  | $a0-$a3 | Function arguments            |
| $8-$15 | $t0-$t7 | Temporaries (caller-saved)    |
| $16-$23| $s0-$s7 | Saved (callee-saved)          |
| $24-$25| $t8-$t9 | More temporaries              |
| $26-$27| $k0-$k1 | Kernel reserved               |
| $28    | $gp     | Global pointer                |
| $29    | $sp     | Stack pointer                 |
| $30    | $fp/$s8 | Frame pointer / saved reg     |
| $31    | $ra     | Return address                |

**Special registers:** HI, LO (multiply/divide results), PC

---

## Instruction Formats

All instructions are 32 bits wide.

### R-Type (Register)
```
| opcode (6) | rs (5) | rt (5) | rd (5) | shamt (5) | funct (6) |
```

### I-Type (Immediate)
```
| opcode (6) | rs (5) | rt (5) | immediate (16) |
```

### J-Type (Jump)
```
| opcode (6) | target (26) |
```

---

## Key Instructions

| Category    | Instructions                              | Notes                          |
|-------------|-------------------------------------------|--------------------------------|
| Arithmetic  | ADD, ADDU, ADDI, ADDIU, SUB, SUBU        | ADD/SUB trap on overflow       |
| Logic       | AND, ANDI, OR, ORI, XOR, XORI, NOR       |                                |
| Shift       | SLL, SRL, SRA, SLLV, SRLV, SRAV         |                                |
| Set         | SLT, SLTI, SLTU, SLTIU                   | Set if Less Than               |
| Load Upper  | LUI                                       | Loads imm into upper 16 bits   |
| Load        | LB, LBU, LH, LHU, LW, LWL, LWR, LD     | LWL/LWR = unaligned load      |
| Store       | SB, SH, SW, SWL, SWR, SD                 | SWL/SWR = unaligned store      |
| Branch      | BEQ, BNE, BGTZ, BLEZ, BLTZ, BGEZ        | All have delay slots           |
| Branch+Link | BGEZAL, BLTZAL                            | Branch and link (conditional)  |
| Jump        | J, JAL                                    | 26-bit pseudo-direct           |
| Jump Reg    | JR, JALR                                  | Register-indirect jump         |
| Multiply    | MULT, MULTU, DIV, DIVU                   | Results in HI/LO               |
| HI/LO       | MFHI, MFLO, MTHI, MTLO                  | Move from/to HI/LO            |
| Coprocessor | MFC0, MTC0, MFC1, MTC1, CFC1, CTC1      |                                |
| System      | SYSCALL, BREAK, ERET                      |                                |
| Cache       | CACHE                                     | Cache maintenance ops          |

---

## Delay Slots

The instruction immediately after a branch or jump **always executes**, regardless of whether the branch is taken.

```
BEQ  $t0, $t1, target
ADDU $t2, $t3, $t4       <-- this ALWAYS executes (delay slot)
```

**Branch Likely** variants (BEQL, BNEL, etc.) nullify the delay slot if the branch is NOT taken. These are deprecated in later MIPS revisions but used in N64 code.

---

## Coprocessors

### COP0 -- System Control
Handles exceptions, TLB, interrupts, status/cause registers. Key registers:

| Register | Number | Purpose            |
|----------|--------|--------------------|
| Status   | 12     | Interrupt/mode bits|
| Cause    | 13     | Exception cause    |
| EPC      | 14     | Exception PC       |
| Count    | 9      | Timer counter      |
| Compare  | 11     | Timer compare      |
| EntryLo0 | 2     | TLB entry low 0    |
| EntryLo1 | 3     | TLB entry low 1    |
| EntryHi  | 10     | TLB entry high     |

### COP1 -- Floating Point Unit
- 32 single-precision or 16 double-precision registers (FR bit dependent)
- Instructions: ADD.S, SUB.S, MUL.S, DIV.S, MOV.S, CVT.x.y, C.cond.S
- FPU compare sets a condition bit; BC1T/BC1F branch on it

---

## N64 Memory Map (Key Regions)

| Address             | Description                |
|---------------------|----------------------------|
| 0x80000000-0x803FFFFF | RDRAM (4/8 MB, cached)   |
| 0xA0000000-0xA03FFFFF | RDRAM (uncached mirror)  |
| 0xA4000000-0xA4FFFFFF | SP (RSP) registers       |
| 0xA4300000-0xA43FFFFF | MI (MIPS Interface)      |
| 0xA4400000-0xA44FFFFF | VI (Video Interface)     |
| 0xB0000000-0xB3FFFFFF | ROM (cartridge, uncached)|

---

## Recompiler Pain Points

- **Delay slots:** Every branch/jump has a delay slot. The recompiler must emit the delay slot instruction before (or as part of) the branch. Branch Likely variants add further complexity.
- **Branch Likely instructions:** BEQL, BNEL, etc. nullify the delay slot on not-taken. Requires conditional execution of the delay slot.
- **Unaligned loads/stores:** LWL/LWR and SWL/SWR load/store partial words at unaligned addresses. Common in N64 code and require careful host translation.
- **TLB:** The N64 uses a software-managed TLB. Games can remap virtual addresses at runtime, making address translation a moving target.
- **HI/LO hazards:** MULT/DIV write HI and LO asynchronously. Accessing HI/LO too early after a multiply is undefined on real hardware; some games depend on specific timing.
- **Self-modifying code / DMA:** The N64 frequently DMAs code from ROM into RDRAM. The recompiler must invalidate translated blocks when DMA writes to code regions.
- **RSP microcode:** The Reality Signal Processor has its own instruction set that may also need recompilation for HLE approaches.
