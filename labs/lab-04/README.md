# Lab 4: SM83 Lifter

## Objective

Manually translate SM83 (Game Boy CPU) instructions into equivalent C code.
This is the core of the "lifting" stage in a static recompilation pipeline:
converting machine instructions into a higher-level representation.

By the end of this lab you will be able to:

- Describe the SM83 register set and flag behavior
- Translate arithmetic, logic, load, and control-flow instructions to C
- Handle flag computation for the Z, N, H, and C flags
- Understand how a lifter maps source ISA semantics to target language code

## Background

The SM83 is a modified Z80 variant used in the original Game Boy. It has an
8-bit accumulator (A), six general-purpose 8-bit registers (B, C, D, E, H, L),
a 16-bit stack pointer (SP), a 16-bit program counter (PC), and a flags
register (F) with four flags:

| Flag | Bit | Meaning                        |
|------|-----|--------------------------------|
| Z    | 7   | Zero -- result is zero         |
| N    | 6   | Subtract -- last op was a sub  |
| H    | 5   | Half-carry -- carry from bit 3 |
| C    | 4   | Carry -- carry from bit 7      |

In our lifter, the CPU state is represented as a C struct:

```c
typedef struct {
    uint8_t a, b, c, d, e, h, l, f;
    uint16_t sp, pc;
} cpu_t;
```

Each SM83 instruction is translated to one or more lines of C code that
manipulate this struct.

## Instructions

1. Open `sm83_lifter.py` and study the example implementations.
2. Complete each `TODO` to implement the remaining instruction lifters.
3. Run the tests to check your work:
   ```
   python -m pytest test_lab.py -v
   ```
4. Try adding support for additional instructions beyond the required set.

## Flag Helpers

The starter code uses helper macros/functions for flag computation:

- `SET_Z(val)` -- sets Z flag if val == 0
- `SET_N(flag)` -- sets or clears the N flag
- `SET_H_ADD(a, b)` -- sets H flag for addition half-carry
- `SET_H_SUB(a, b)` -- sets H flag for subtraction half-borrow
- `SET_C_ADD(a, b)` -- sets C flag for addition carry
- `SET_C_SUB(a, b)` -- sets C flag for subtraction borrow
