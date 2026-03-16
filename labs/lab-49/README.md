# Lab 49: BIOS HLE Shim (GBA)

## Objective

Implement high-level emulation (HLE) replacements for GBA BIOS calls.
Instead of emulating the BIOS ROM instruction-by-instruction, HLE
replaces entire BIOS functions with C implementations. This is both
faster and avoids needing the copyrighted BIOS binary.

By the end of this lab you will be able to:

- Implement GBA BIOS math functions (Div, Sqrt)
- Implement GBA BIOS memory functions (CpuSet, CpuFastSet)
- Interact with a simulated CPU state struct

## Background

The GBA BIOS provides system calls via the ARM `SWI` (Software Interrupt)
instruction. The game places arguments in registers, executes `SWI <n>`,
and the BIOS routine runs and places results back in registers.

For recompilation, we replace these with C functions that take a pointer
to the CPU state and modify registers directly.

### BIOS Calls to Implement

| SWI  | Name       | Input                              | Output                    |
|------|------------|-------------------------------------|---------------------------|
| 0x06 | Div        | r0 = numerator, r1 = denominator   | r0 = quotient, r1 = remainder, r3 = abs(quotient) |
| 0x08 | Sqrt       | r0 = value                         | r0 = floor(sqrt(value))   |
| 0x0B | CpuSet     | r0 = src, r1 = dst, r2 = control   | memory modified           |
| 0x0C | CpuFastSet | r0 = src, r1 = dst, r2 = control   | memory modified           |

### CpuSet Control Word (r2)

| Bits   | Field      | Description                        |
|--------|------------|------------------------------------|
| 20-0   | count      | Number of copies (words or halfwords) |
| 24     | fixed_src  | If set, source is fixed (fill mode) |
| 26     | word_size  | 0 = 16-bit (halfword), 1 = 32-bit (word) |

### CpuFastSet

Like CpuSet but always operates on 32-bit words and the count is
rounded up to a multiple of 8 (it copies 8 words per iteration).
The fixed_src flag works the same way (fill vs. copy).

### Memory Model

For this lab, the CPU state includes a flat memory buffer. Source and
destination addresses index into this buffer.

## Files

| File          | Description                          |
|---------------|--------------------------------------|
| `bios_hle.h`  | API declarations and CPU state      |
| `bios_hle.c`  | HLE implementations (starter code) |
| `test_bios.c`  | Test suite                          |
| `Makefile`      | Build and test targets              |

## Instructions

1. Read `bios_hle.h` to understand the CPU state struct.
2. Complete the `TODO` sections in `bios_hle.c`.
3. Build and test:
   ```bash
   make
   make test
   ```

## Expected Output

```
GBA BIOS HLE -- Test Suite

--- test_div ---
--- test_div_negative ---
--- test_sqrt ---
--- test_cpuset_copy ---
--- test_cpuset_fill ---
--- test_cpufastset_copy ---
--- test_cpufastset_fill ---

7 / 7 tests passed.
```

## References

- GBATEK (GBA/NDS Technical Info) -- BIOS Functions section
- mGBA BIOS HLE implementation
- ARM7TDMI Technical Reference Manual
