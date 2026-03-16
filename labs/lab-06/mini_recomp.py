"""
Lab 6: Mini-GB Recomp

A minimal static recompilation pipeline for Game Boy ROMs.
Reads SM83 machine code, decodes it, lifts each instruction to C,
and writes a compilable output file.

Pipeline stages:
  1. DECODE -- parse raw bytes into instruction records
  2. LIFT   -- translate each instruction to C code
  3. EMIT   -- write the C source file
  4. BUILD  -- compile with gcc (handled by Makefile)
"""

import sys
import os
import struct


# ---------------------------------------------------------------------------
# Sample ROM
# ---------------------------------------------------------------------------

# A tiny ROM that performs: A = 0x10, B = 0x20, A = A + B, store A to 0xC000
# Then halts.
#
# Address  Bytes       Instruction
# 0x0100   3E 10       LD A, 0x10
# 0x0102   06 20       LD B, 0x20
# 0x0104   80          ADD A, B
# 0x0105   EA 00 C0    LD (0xC000), A
# 0x0108   76          HALT
#
# The ROM must be at least 0x150 bytes for a valid header. We only care
# about the code starting at 0x0100.

SAMPLE_ROM = bytearray(0x150)
SAMPLE_ROM[0x0100] = 0x3E  # LD A, imm8
SAMPLE_ROM[0x0101] = 0x10  # immediate: 0x10
SAMPLE_ROM[0x0102] = 0x06  # LD B, imm8
SAMPLE_ROM[0x0103] = 0x20  # immediate: 0x20
SAMPLE_ROM[0x0104] = 0x80  # ADD A, B
SAMPLE_ROM[0x0105] = 0xEA  # LD (imm16), A
SAMPLE_ROM[0x0106] = 0x00  # low byte of address
SAMPLE_ROM[0x0107] = 0xC0  # high byte of address (0xC000)
SAMPLE_ROM[0x0108] = 0x76  # HALT


# ---------------------------------------------------------------------------
# Stage 1: DECODE
# ---------------------------------------------------------------------------

# Instruction record: (address, opcode, length, operand_bytes, mnemonic)
# operand_bytes is a bytes object of 0-2 bytes following the opcode.

# Instruction length table: maps opcode to total instruction length.
# Most SM83 instructions are 1 byte; those with immediate operands are longer.
INSTRUCTION_LENGTH = {}

# Default: 1 byte
for op in range(0x100):
    INSTRUCTION_LENGTH[op] = 1

# 2-byte instructions (8-bit immediate or relative offset)
for op in [
    0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E,  # LD r, imm8
    0xC6, 0xD6, 0xE6, 0xF6, 0xCE, 0xDE, 0xEE, 0xFE,  # ALU A, imm8
    0x18, 0x20, 0x28, 0x30, 0x38,                       # JR
    0xE0, 0xF0,                                          # LDH
    0xCB,                                                # CB prefix
]:
    INSTRUCTION_LENGTH[op] = 2

# 3-byte instructions (16-bit immediate or address)
for op in [
    0x01, 0x11, 0x21, 0x31,        # LD rr, imm16
    0xC2, 0xC3, 0xCA, 0xD2, 0xDA,  # JP
    0xC4, 0xCC, 0xCD, 0xD4, 0xDC,  # CALL
    0xEA, 0xFA,                     # LD (imm16), A / LD A, (imm16)
    0x08,                           # LD (imm16), SP
]:
    INSTRUCTION_LENGTH[op] = 3


def decode_instruction(rom_data, offset):
    """Decode a single SM83 instruction at the given offset.

    Args:
        rom_data: The full ROM as bytes.
        offset: Byte offset to decode at.

    Returns:
        Dict with keys: addr, opcode, length, operands (bytes), mnemonic (str).
        Returns None if offset is out of bounds.
    """
    if offset >= len(rom_data):
        return None

    opcode = rom_data[offset]
    length = INSTRUCTION_LENGTH.get(opcode, 1)

    # Guard against reading past end of ROM
    if offset + length > len(rom_data):
        length = 1

    operands = bytes(rom_data[offset + 1 : offset + length])

    # Build a simple mnemonic string for display
    mnemonic = f"0x{opcode:02X}"  # Placeholder

    return {
        "addr": offset,
        "opcode": opcode,
        "length": length,
        "operands": operands,
        "mnemonic": mnemonic,
    }


def decode_rom(rom_data, start_addr=0x0100, end_addr=None):
    """Decode all instructions from start_addr to end_addr (or HALT).

    Args:
        rom_data: The full ROM as bytes.
        start_addr: Address to begin decoding.
        end_addr: Address to stop (exclusive), or None to stop at HALT.

    Returns:
        List of instruction dicts.
    """
    instructions = []
    offset = start_addr

    while offset < len(rom_data):
        if end_addr is not None and offset >= end_addr:
            break

        insn = decode_instruction(rom_data, offset)
        if insn is None:
            break

        instructions.append(insn)

        # Stop after HALT
        if insn["opcode"] == 0x76:
            break

        offset += insn["length"]

    return instructions


# ---------------------------------------------------------------------------
# Stage 2: LIFT
# ---------------------------------------------------------------------------

def lift_instruction(insn):
    """Lift a decoded instruction dict to a C code string.

    Args:
        insn: Instruction dict from decode_instruction().

    Returns:
        C code string, or a comment indicating an unhandled opcode.
    """
    opcode = insn["opcode"]
    operands = insn["operands"]
    addr = insn["addr"]

    # LD A, imm8 (0x3E)
    if opcode == 0x3E:
        imm = operands[0]
        return f"cpu->a = 0x{imm:02X};"

    # LD B, imm8 (0x06)
    if opcode == 0x06:
        imm = operands[0]
        return f"cpu->b = 0x{imm:02X};"

    # ADD A, B (0x80)
    if opcode == 0x80:
        return (
            "{ uint8_t prev = cpu->a; "
            "cpu->a = (cpu->a + cpu->b) & 0xFF; "
            "SET_Z(cpu->a); SET_N(0); "
            "SET_H_ADD(prev, cpu->b); SET_C_ADD(prev, cpu->b); }"
        )

    # LD (imm16), A (0xEA)
    if opcode == 0xEA:
        addr16 = operands[0] | (operands[1] << 8)
        return f"mem_write8(0x{addr16:04X}, cpu->a);"

    # HALT (0x76)
    if opcode == 0x76:
        return "cpu->halted = true; return;"

    # TODO: Add more instruction handlers here. For a complete recompiler,
    #       you would handle all SM83 opcodes. Start with these common ones:
    #
    #   0x0E: LD C, imm8
    #   0x16: LD D, imm8
    #   0x1E: LD E, imm8
    #   0x26: LD H, imm8
    #   0x2E: LD L, imm8
    #   0x40-0x7F: LD r, r' (register-to-register loads, excluding HALT)
    #   0x90-0x97: SUB A, r
    #   0xA0-0xA7: AND A, r
    #   0xA8-0xAF: XOR A, r
    #   0xB0-0xB7: OR A, r
    #   0xC3: JP imm16
    #   0xCD: CALL imm16
    #   0xC9: RET
    #
    # Refer to your Lab 4 sm83_lifter.py for the C code patterns.
    # Remember to use cpu-> instead of cpu. (pointer vs struct).

    return f"/* UNHANDLED: opcode 0x{opcode:02X} at 0x{addr:04X} */;"


def lift_all(instructions):
    """Lift a list of decoded instructions to C code strings.

    Args:
        instructions: List of instruction dicts.

    Returns:
        List of (address, c_code_string) tuples.
    """
    lifted = []
    for insn in instructions:
        c_code = lift_instruction(insn)
        lifted.append((insn["addr"], c_code))
    return lifted


# ---------------------------------------------------------------------------
# Stage 3: EMIT
# ---------------------------------------------------------------------------

def emit_c_file(lifted_instructions, output_path="output.c"):
    """Write the lifted C code to a source file.

    Generates a complete C file with:
    - Include for runtime.h
    - A recompiled_main() function
    - Address labels as comments
    - A dispatch structure using the program counter

    Args:
        lifted_instructions: List of (address, c_code) tuples.
        output_path: Path to write the output file.
    """
    lines = []
    lines.append("/*")
    lines.append(" * Generated by mini_recomp.py")
    lines.append(" * This file is auto-generated -- do not edit by hand.")
    lines.append(" */")
    lines.append("")
    lines.append('#include "runtime.h"')
    lines.append("")
    lines.append("void recompiled_main(cpu_t *cpu)")
    lines.append("{")

    # TODO: Generate a dispatch mechanism. The simplest approach is a
    #       switch statement on cpu->pc with a surrounding loop:
    #
    #   while (!cpu->halted) {
    #       switch (cpu->pc) {
    #           case 0x0100:
    #               /* lifted code */
    #               cpu->pc = 0x0102;  /* advance to next instruction */
    #               break;
    #           ...
    #       }
    #   }
    #
    # For now, we emit a simpler linear sequence since our sample ROM
    # has no branches. Students should upgrade this to a switch dispatch
    # as a stretch goal.

    lines.append("    /* Linear execution of lifted code */")
    for addr, c_code in lifted_instructions:
        lines.append(f"    /* 0x{addr:04X} */ {c_code}")

    lines.append("}")
    lines.append("")

    source = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(source)

    print(f"Wrote {output_path} ({len(lines)} lines)")
    return source


# ---------------------------------------------------------------------------
# Pipeline Driver
# ---------------------------------------------------------------------------

def run_pipeline(rom_data, output_path="output.c"):
    """Run the full recompilation pipeline.

    Args:
        rom_data: ROM as bytes or bytearray.
        output_path: Where to write the generated C file.

    Returns:
        The generated C source as a string.
    """
    print("=== Mini-GB Recomp Pipeline ===")
    print()

    # Stage 1: Decode
    print("[Stage 1] Decoding ROM...")
    instructions = decode_rom(rom_data, start_addr=0x0100)
    print(f"  Decoded {len(instructions)} instructions:")
    for insn in instructions:
        ops_hex = " ".join(f"{b:02X}" for b in insn["operands"])
        print(f"    0x{insn['addr']:04X}: {insn['opcode']:02X} {ops_hex}")
    print()

    # Stage 2: Lift
    print("[Stage 2] Lifting to C...")
    lifted = lift_all(instructions)
    for addr, code in lifted:
        print(f"    0x{addr:04X}: {code}")
    print()

    # Stage 3: Emit
    print("[Stage 3] Emitting C source...")
    source = emit_c_file(lifted, output_path)
    print()

    print("[Stage 4] Build with: make")
    print("          Run with:   ./mini_gb")
    print()

    return source


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        # Read ROM from file
        filepath = sys.argv[1]
        if not os.path.isfile(filepath):
            print(f"Error: file not found: {filepath}")
            sys.exit(1)
        with open(filepath, "rb") as f:
            rom_data = f.read()
        print(f"Loaded ROM: {filepath} ({len(rom_data)} bytes)")
    else:
        # Use built-in sample ROM
        rom_data = bytes(SAMPLE_ROM)
        print(f"Using built-in sample ROM ({len(rom_data)} bytes)")

    print()
    run_pipeline(rom_data, output_path="output.c")


if __name__ == "__main__":
    main()
