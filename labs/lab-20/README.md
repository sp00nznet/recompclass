# Lab 20: SPU DMA Simulator

## Objective

Simulate the PS3 SPU's 256KB local store and DMA (Direct Memory Access)
transfer mechanism. This is the most advanced lab in the course, combining
memory management, alignment constraints, and the unique architecture of the
Cell Broadband Engine's Synergistic Processing Units (SPUs).

## Background

The PS3's Cell processor contains one PPU (PowerPC Processing Unit) and
six usable SPUs (Synergistic Processing Units). Each SPU has:

- **256KB Local Store (LS)**: A private, fast memory that is the only memory
  the SPU can directly access. It holds both code and data.
- **DMA Engine**: The mechanism by which the SPU transfers data between its
  local store and main memory (accessed by the PPU).

The SPU cannot directly read or write main memory. All data movement between
main memory and the local store must go through DMA transfers. This is
fundamentally different from a traditional CPU cache -- the programmer
explicitly manages all data movement.

### DMA Transfer Rules

- Transfers must be **16-byte aligned** in both local store and main memory.
- Transfer sizes must be **16 bytes, or a multiple of 16 bytes** (up to 16KB
  per single transfer).
- Transfers are **asynchronous** -- the SPU initiates a transfer and can
  continue executing while the DMA engine moves data in the background.
- Transfers are grouped by **tags** (0-31). The SPU can wait for all
  transfers with a given tag to complete.

### DMA Commands

- **GET**: Transfer data from main memory to local store.
- **PUT**: Transfer data from local store to main memory.
- **LIST GET/PUT**: Transfer a list of (main memory address, size) pairs
  to/from contiguous local store memory.

## Files

| File          | Description                                    |
|---------------|------------------------------------------------|
| `spu_sim.h`   | Header defining SPU local store and DMA types |
| `spu_sim.c`   | Implementation of the SPU simulator           |
| `test_spu.c`  | Test suite for DMA transfers                  |
| `Makefile`     | Build and test targets                        |

## Tasks

1. Read through `spu_sim.h` to understand the data structures.
2. Complete the DMA transfer functions in `spu_sim.c`.
3. Run the tests and ensure all alignment and size constraints are enforced.
4. (Stretch) Implement DMA tag groups and completion events.
5. (Stretch) Implement mailbox communication between PPU and SPU contexts.

## Building and Testing

```bash
make
make test
```

## References

- Cell Broadband Engine Programming Handbook (IBM)
- SPU ISA documentation
- PS3 Developer Wiki (SPU DMA section)
