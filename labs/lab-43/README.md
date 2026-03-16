# Lab 43: Cell PPU/SPU Memory Bridge

## Objective

Implement a DMA bridge between PPU main memory and SPU local stores for
the PS3's Cell processor. This is the memory transfer layer that
recompiled PS3 games rely on -- every SPU data access must go through
DMA, and getting the alignment and size rules right is critical.

By the end of this lab you will be able to:

- Implement DMA put/get transfers with alignment enforcement
- Model multiple SPU local stores with 256KB boundaries
- Implement a DMA barrier (wait) operation
- Handle transfer validation and error reporting

## Background

Each SPU on the Cell processor has a 256KB local store. The SPU cannot
directly access main memory -- all data movement goes through DMA
transfers managed by the Memory Flow Controller (MFC).

### DMA Rules

- All transfers must be **16-byte aligned** (both source and destination).
- Transfer sizes must be exactly 1, 2, 4, 8, or a **multiple of 16 bytes**.
- Maximum single transfer size is **16KB** (16384 bytes).
- Each SPU has its own local store; DMA addresses are offsets within it.

### Functions to Implement

| Function   | Direction              | Description                    |
|------------|------------------------|--------------------------------|
| `dma_put`  | Main memory -> LS      | Copy from main mem to local store |
| `dma_get`  | LS -> Main memory      | Copy from local store to main mem |
| `dma_wait` | Barrier                | Wait for all pending DMA (no-op in sim) |

## Files

| File            | Description                           |
|-----------------|---------------------------------------|
| `dma_bridge.h`  | API declarations and constants       |
| `dma_bridge.c`  | DMA bridge implementation (starter)  |
| `test_bridge.c` | Test suite                            |
| `Makefile`       | Build and test targets               |

## Instructions

1. Read `dma_bridge.h` to understand the data structures.
2. Complete the `TODO` sections in `dma_bridge.c`.
3. Build and test:
   ```bash
   make
   make test
   ```

## Expected Output

```
Cell DMA Bridge -- Test Suite

--- test_dma_put ---
--- test_dma_get ---
--- test_round_trip ---
--- test_alignment_check ---
--- test_size_check ---
--- test_bounds_check ---
--- test_multi_spu ---

7 / 7 tests passed.
```

## References

- Cell Broadband Engine Programming Handbook (IBM)
- SPU Runtime Management Library documentation
