# Lab 10: Recursive Descent Disassembler

## Objective

Build a recursive descent disassembler for a simplified instruction set
architecture (ISA), constructing a control flow graph (CFG) of basic blocks.

## Background

Disassemblers come in two main flavors:

1. **Linear sweep**: Start at the beginning and decode every byte sequentially.
   Simple but easily confused by data embedded in code or variable-length encodings.

2. **Recursive descent**: Start at known entry points and follow control flow.
   Only disassembles code that is actually reachable, building a CFG as it goes.

For static recompilation, recursive descent is strongly preferred because it
produces a CFG that directly maps to the structure we need for generating
recompiled code.

### The Simple ISA

This lab uses a simplified 8-instruction ISA with fixed-width 2-byte encoding:

| Opcode | Mnemonic | Operand     | Description                          |
|--------|----------|-------------|--------------------------------------|
| 0x00   | NOP      | (unused)    | No operation                         |
| 0x01   | LOAD     | register    | Load value into register             |
| 0x02   | STORE    | register    | Store register to memory             |
| 0x03   | ADD      | register    | Add register to accumulator          |
| 0x04   | SUB      | register    | Subtract register from accumulator   |
| 0x05   | CMP      | register    | Compare register with accumulator    |
| 0x06   | JMP      | target addr | Unconditional jump (byte address)    |
| 0x07   | JZ       | target addr | Jump if zero flag set (byte address) |
| 0x08   | HALT     | (unused)    | Stop execution                       |

Each instruction is exactly 2 bytes: 1 byte opcode + 1 byte operand.

## Tasks

1. Define the simple ISA (provided in `simple_isa.py`).
2. Implement recursive descent disassembly starting from an entry point.
3. Build basic blocks -- maximal sequences of instructions with no internal branches.
4. Construct a CFG as an adjacency list.
5. (TODO) Detect unreachable code regions.
6. (TODO) Handle overlapping instructions (not possible in this fixed-width ISA, but show the pattern for variable-width).

## Files

- `simple_isa.py` — ISA definition
- `recursive_disasm.py` — Recursive descent disassembler
- `test_lab.py` — Tests with hand-crafted binaries

## Running

```bash
python recursive_disasm.py
python test_lab.py
```

## Key Concepts

- Recursive descent vs linear sweep disassembly
- Basic block identification
- Control flow graph construction
- The exploration queue / worklist algorithm
