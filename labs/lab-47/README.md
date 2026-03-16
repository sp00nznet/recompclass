# Lab 47: Endianness Conversion Library

## Objective

Implement a byte-swap utility library for recompilation of big-endian
console games on little-endian hosts. N64, GameCube, Wii, PS3, and Xbox
360 are all big-endian, while x86/x64 hosts are little-endian. Every
multi-byte value read from the original game's memory must be byte-swapped.

By the end of this lab you will be able to:

- Implement 16, 32, and 64-bit byte-swap functions
- Build conditional swap functions that check host endianness
- Swap arrays of values in-place (bulk buffer conversion)

## Background

Endianness determines the order in which bytes of a multi-byte value are
stored in memory:

- **Big-endian** (BE): most significant byte first. `0x12345678` is stored
  as `12 34 56 78`.
- **Little-endian** (LE): least significant byte first. `0x12345678` is
  stored as `78 56 34 12`.

For recompilation, we need:

1. **Unconditional swaps**: always reverse byte order.
2. **Conditional swaps**: only swap if the host is little-endian (i.e.,
   converting from big-endian game data to host order).
3. **Buffer swaps**: convert entire arrays of 16-bit or 32-bit values.

### Functions to Implement

| Function          | Description                                  |
|-------------------|----------------------------------------------|
| `swap16(x)`       | Unconditional 16-bit byte swap              |
| `swap32(x)`       | Unconditional 32-bit byte swap              |
| `swap64(x)`       | Unconditional 64-bit byte swap              |
| `be16_to_host(x)` | Swap if host is LE, no-op if host is BE     |
| `be32_to_host(x)` | Swap if host is LE, no-op if host is BE     |
| `be64_to_host(x)` | Swap if host is LE, no-op if host is BE     |
| `swap_buf16(buf, count)` | Swap array of 16-bit values in-place  |
| `swap_buf32(buf, count)` | Swap array of 32-bit values in-place  |

## Files

| File             | Description                            |
|------------------|----------------------------------------|
| `endian_utils.h` | API declarations and macros           |
| `endian_utils.c` | Implementation (starter code)         |
| `test_endian.c`  | Test suite                             |
| `Makefile`        | Build and test targets                |

## Instructions

1. Read `endian_utils.h` to understand the API.
2. Complete the `TODO` sections in `endian_utils.c`.
3. Build and test:
   ```bash
   make
   make test
   ```

## Expected Output

```
Endianness Utils -- Test Suite

--- test_swap16 ---
--- test_swap32 ---
--- test_swap64 ---
--- test_conditional_swap ---
--- test_swap_buf16 ---
--- test_swap_buf32 ---
--- test_round_trip ---

7 / 7 tests passed.
```

## References

- N64/GameCube/Wii use big-endian MIPS/PPC
- x86/x64 is always little-endian
- GCC/Clang `__builtin_bswap` intrinsics
