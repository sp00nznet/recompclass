# Lab 13: Flag Helper Library

## Objective

Build a reusable C library for computing CPU status flags resulting from 8-bit
ALU operations. Accurate flag computation is one of the most error-prone parts
of static recompilation -- getting it wrong leads to broken control flow in the
recompiled binary.

## Background

Most CPUs maintain a set of status flags that are updated after arithmetic and
logic operations. Common flags include:

- **Zero (Z)**: Set when the result is zero.
- **Carry (C)**: Set when an unsigned operation overflows (e.g., 0xFF + 1).
- **Overflow (V)**: Set when a signed operation overflows (e.g., 0x7F + 1).
- **Negative/Sign (N)**: Set when the result's most significant bit is 1.
- **Half-Carry (H)**: Set when there is a carry out of the lower nibble (bit 3
  to bit 4). Used by some architectures (Z80, SM83/Game Boy, etc.).

In a static recompiler, you must decide how to compute these flags. The two
main strategies are:

1. **Eager**: Compute all flags after every instruction (simple but slow).
2. **Lazy**: Defer flag computation until a flag is actually read (fast but
   complex).

This lab focuses on the eager approach. You will implement helper functions that
take operands, perform the operation, and return both the result and the
complete set of flags.

## Files

| File            | Description                                      |
|-----------------|--------------------------------------------------|
| `flags.h`       | Header declaring flag types and helper functions |
| `flags.c`       | Implementation of flag computation               |
| `test_flags.c`  | Test cases covering edge cases                   |
| `Makefile`      | Build and test targets                           |

## Tasks

1. Read through `flags.h` to understand the `FlagResult` structure.
2. Implement `add_flags_u8` and `sub_flags_u8` in `flags.c`.
3. Implement flag updates for AND, OR, and XOR operations.
4. Run the tests and make sure all edge cases pass.
5. (Stretch) Add 16-bit variants of each function.

## Building and Testing

```bash
make
make test
```

## Key Edge Cases to Understand

- `0xFF + 0x01` -- carry, zero, half-carry
- `0x00 - 0x01` -- carry (borrow), negative
- `0x7F + 0x01` -- overflow (positive + positive = negative)
- `0x80 - 0x01` -- overflow (negative - positive = positive)
- `0x0F + 0x01` -- half-carry only
