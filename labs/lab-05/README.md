# Lab 5: Memory Bus

## Objective

Implement a Game Boy memory bus in C. The memory bus is the central data
pathway connecting the CPU to ROM, RAM, video memory, and I/O registers.
A correct memory bus implementation is essential for any Game Boy
recompilation runtime.

By the end of this lab you will be able to:

- Describe the Game Boy memory map and the purpose of each region
- Implement read/write routing based on address ranges
- Handle special cases like echo RAM and restricted OAM access
- Understand how bank switching extends the addressable memory space

## Background

The Game Boy has a 16-bit address bus (0x0000-0xFFFF = 64 KB). The address
space is divided into fixed regions:

| Range           | Size   | Region                     |
|-----------------|--------|----------------------------|
| 0x0000 - 0x3FFF | 16 KB  | ROM Bank 0 (fixed)         |
| 0x4000 - 0x7FFF | 16 KB  | ROM Bank 1-N (switchable)  |
| 0x8000 - 0x9FFF | 8 KB   | Video RAM (VRAM)           |
| 0xA000 - 0xBFFF | 8 KB   | External RAM (cartridge)   |
| 0xC000 - 0xDFFF | 8 KB   | Work RAM (WRAM)            |
| 0xE000 - 0xFDFF | 7.5 KB | Echo RAM (mirror of WRAM)  |
| 0xFE00 - 0xFE9F | 160 B  | OAM (sprite attributes)    |
| 0xFEA0 - 0xFEFF | 96 B   | Unusable                   |
| 0xFF00 - 0xFF7F | 128 B  | I/O Registers              |
| 0xFF80 - 0xFFFE | 127 B  | High RAM (HRAM)            |
| 0xFFFF          | 1 B    | Interrupt Enable Register  |

## Instructions

1. Read through `memory_bus.h` to understand the data structures.
2. Open `memory_bus.c` and implement the `TODO` sections.
3. Build the project:
   ```
   make
   ```
4. Run the tests:
   ```
   make test
   ```

## Build Requirements

- A C compiler (gcc, clang, or MSVC)
- GNU Make (or compatible)

## Stretch Goals

- Implement MBC1 bank switching (write to 0x0000-0x7FFF to select banks)
- Implement echo RAM (0xE000-0xFDFF mirrors 0xC000-0xDDFF)
- Restrict OAM access during certain PPU modes
