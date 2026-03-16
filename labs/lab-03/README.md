# Lab 3: Multi-Architecture Disassembly

## Objective

Use the Capstone disassembly framework to disassemble the same (and different)
byte sequences under multiple CPU architectures: x86-32, MIPS, and PowerPC.
Then add ARM support and build a simple heuristic architecture detector.

By the end of this lab you will be able to:

- Configure Capstone for different architectures and endianness modes
- Understand how the same byte sequence decodes differently per architecture
- Recognize common instruction patterns that hint at the target architecture
- Use the shared `disasm_helpers` library

## Background

A static recompiler must know the source architecture before it can decode
instructions. In most real projects the architecture is known from the file
format (e.g., ELF e_machine, PE Machine field). However, when dealing with
raw firmware dumps or headerless ROM images, you may need heuristics to
identify the architecture.

Capstone supports many architectures through a uniform API. The
`disasm_helpers` module wraps Capstone with convenient presets.

## Instructions

1. Open `multi_disasm.py` and study the provided sample byte sequences.
2. Run the script to see how each byte sequence disassembles:
   ```
   python multi_disasm.py
   ```
3. Complete the TODOs:
   - Add ARM (32-bit) disassembly for the provided ARM sample bytes.
   - Implement the `detect_architecture()` heuristic function.
4. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Tips

- x86 instructions are variable-length (1-15 bytes). MIPS and PPC
  instructions are always 4 bytes. ARM instructions are 4 bytes in
  ARM mode, 2 bytes in Thumb mode.
- A high ratio of successfully decoded bytes vs. total input size is
  a signal that the architecture guess is correct.
- Common x86 prologues: `push ebp; mov ebp, esp` (bytes: 55 89 E5).
- Common MIPS prologues: `addiu $sp, $sp, -N` (opcode 0x27BD).
- Common PPC prologues: `stwu r1, -N(r1)` (opcode 0x9421).
