"""
Lab 27: ARM/Thumb Disassembler

Disassemble ARM and Thumb code using Capstone, with mode detection.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB


# ---------------------------------------------------------------------------
# Disassembly helpers
# ---------------------------------------------------------------------------

def disasm_arm(data, base_address=0):
    """Disassemble a binary blob as ARM (32-bit) instructions.

    Args:
        data: bytes of ARM machine code.
        base_address: address of the first byte.

    Returns:
        A list of tuples: (address, mnemonic, op_str, raw_bytes)
        where raw_bytes is the bytes of the instruction.
    """
    # TODO: 1. Create a Capstone disassembler for ARM mode:
    #          cs = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    # TODO: 2. Iterate over cs.disasm(data, base_address).
    # TODO: 3. For each instruction, append a tuple of
    #          (insn.address, insn.mnemonic, insn.op_str, insn.bytes)
    #          to a results list.
    # TODO: 4. Return the list.
    pass


def disasm_thumb(data, base_address=0):
    """Disassemble a binary blob as Thumb (16-bit) instructions.

    Args:
        data: bytes of Thumb machine code.
        base_address: address of the first byte.

    Returns:
        A list of tuples: (address, mnemonic, op_str, raw_bytes)
    """
    # TODO: Same as disasm_arm but use CS_MODE_THUMB.
    pass


def format_disasm(instructions, mode_label="ARM"):
    """Format a list of disassembled instructions for display.

    Args:
        instructions: list of (address, mnemonic, op_str, raw_bytes) tuples.
        mode_label: "ARM" or "THUMB" to prefix each line.

    Returns:
        A list of formatted strings like:
        "[ARM]   0x08000000: mov   r0, #0x42"
    """
    # TODO: For each instruction tuple, format as:
    #       f"[{mode_label:5s}] 0x{addr:08X}: {mnemonic:6s} {op_str}"
    # TODO: Return the list of strings.
    pass


def detect_mode_switches(instructions):
    """Scan disassembled instructions for BX (Branch and Exchange).

    A BX instruction switches between ARM and Thumb mode. The target
    register's bit 0 determines the mode, but since we don't know
    register values at static analysis time, we just report that a
    mode switch *could* happen.

    Args:
        instructions: list of (address, mnemonic, op_str, raw_bytes) tuples.

    Returns:
        A list of dicts with keys:
            "address"  - int, address of the BX instruction
            "register" - str, the register name (e.g. "r0", "lr")
    """
    # TODO: Find all instructions where mnemonic is "bx".
    # TODO: For each, return the address and the operand string (register).
    pass


def disasm_auto(sections, base_address=0):
    """Disassemble multiple sections with explicit mode annotations.

    This is a simplified version of automatic mode tracking. Instead of
    trying to follow BX targets (which requires runtime register values),
    the caller provides sections with their mode.

    Args:
        sections: list of dicts, each with:
            "data"    - bytes of machine code
            "offset"  - int, byte offset from base_address
            "mode"    - str, "arm" or "thumb"

    Returns:
        A list of formatted strings with mode labels.
    """
    # TODO: For each section:
    #       1. Compute the section's address: base_address + section["offset"]
    #       2. Disassemble using disasm_arm() or disasm_thumb() based on mode.
    #       3. Format with the appropriate label ("ARM" or "THUMB").
    #       4. Collect all formatted lines into one list.
    # TODO: Return the combined list.
    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Example ARM code: MOV R0, #0x42; BX LR
    arm_code = bytes([
        0x42, 0x00, 0xA0, 0xE3,    # MOV R0, #0x42
        0x1E, 0xFF, 0x2F, 0xE1,    # BX LR
    ])

    # Example Thumb code: MOVS R0, #0; ADDS R0, #1; BX LR
    thumb_code = bytes([
        0x00, 0x20,     # MOVS R0, #0
        0x01, 0x30,     # ADDS R0, #1
        0x70, 0x47,     # BX LR
    ])

    print("=== ARM Mode ===")
    arm_insns = disasm_arm(arm_code, base_address=0x08000000)
    if arm_insns:
        for line in format_disasm(arm_insns, "ARM"):
            print(line)
    else:
        print("disasm_arm() returned None -- implement the TODO sections.")

    print("\n=== Thumb Mode ===")
    thumb_insns = disasm_thumb(thumb_code, base_address=0x08000100)
    if thumb_insns:
        for line in format_disasm(thumb_insns, "THUMB"):
            print(line)
    else:
        print("disasm_thumb() returned None -- implement the TODO sections.")


if __name__ == "__main__":
    main()
