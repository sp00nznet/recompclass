# Lab 12: Micro-Lifter (MIPS)

## Objective

Build a small instruction lifter for a subset of MIPS that produces C code.
This is the core of what a static recompiler does: translating machine
instructions into equivalent high-level language statements.

## Background

"Lifting" is the process of translating low-level machine instructions into
a higher-level representation. In static recompilation, we lift machine code
directly to C (or another compiled language) so the result can be recompiled
for a different platform.

### MIPS Subset

This lab covers 10 MIPS instructions:

| Category     | Instruction | Format   | Operation                        |
|-------------|-------------|----------|----------------------------------|
| ALU          | ADD         | R-type   | rd = rs + rt                     |
| ALU          | ADDI        | I-type   | rt = rs + imm                    |
| ALU          | SUB         | R-type   | rd = rs - rt                     |
| ALU          | AND         | R-type   | rd = rs & rt                     |
| ALU          | OR          | R-type   | rd = rs | rt                     |
| ALU          | XOR         | R-type   | rd = rs ^ rt                     |
| Memory       | LW          | I-type   | rt = MEM[rs + imm]               |
| Memory       | SW          | I-type   | MEM[rs + imm] = rt               |
| Control Flow | BEQ         | I-type   | if (rs == rt) goto PC+4+imm*4    |
| Control Flow | J           | J-type   | goto target                      |

### Register Context

The lifted C code operates on a register context struct:

```c
typedef struct {
    uint32_t r[32];     /* General-purpose registers (r[0] is always 0) */
    uint32_t pc;        /* Program counter */
    uint8_t *mem;       /* Memory pointer */
} mips_state_t;
```

## Tasks

1. Lift ADD, LW, and J instructions to C (already implemented as examples).
2. (TODO) Implement lifting for ADDI, SUB, AND, OR, XOR, SW, BEQ.
3. (TODO) Add overflow detection for ADD/SUB.
4. Test each instruction's C output.

## Files

- `mips_lifter.py` — MIPS to C lifter
- `test_lab.py` — Tests for each instruction

## Running

```bash
python mips_lifter.py
python test_lab.py
```

## Key Concepts

- Instruction lifting / translation
- Register context structs in recompiled code
- Handling memory access in lifted code
- Branch translation and label generation
