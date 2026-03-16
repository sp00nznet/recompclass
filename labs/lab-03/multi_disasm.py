"""
Lab 3: Multi-Architecture Disassembly

Disassemble byte sequences under different CPU architectures using
the Capstone framework via the shared disasm_helpers module.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from labs.lib.disasm_helpers import (
    create_disassembler,
    disassemble,
    format_disassembly,
    ARCH_PRESETS,
)


# ---------------------------------------------------------------------------
# Sample Byte Sequences
# ---------------------------------------------------------------------------

# x86-32: push ebp; mov ebp, esp; sub esp, 0x10; mov eax, [ebp+8]; ret
X86_32_BYTES = bytes([
    0x55,                         # push ebp
    0x89, 0xE5,                   # mov ebp, esp
    0x83, 0xEC, 0x10,             # sub esp, 0x10
    0x8B, 0x45, 0x08,             # mov eax, [ebp+8]
    0xC3,                         # ret
])

# MIPS32 (big-endian): addiu $sp, $sp, -32; sw $ra, 28($sp); jr $ra; nop
MIPS32_BYTES = bytes([
    0x27, 0xBD, 0xFF, 0xE0,      # addiu $sp, $sp, -32
    0xAF, 0xBF, 0x00, 0x1C,      # sw $ra, 28($sp)
    0x03, 0xE0, 0x00, 0x08,      # jr $ra
    0x00, 0x00, 0x00, 0x00,      # nop
])

# PPC32 (big-endian): stwu r1, -16(r1); mflr r0; stw r0, 20(r1); blr
PPC32_BYTES = bytes([
    0x94, 0x21, 0xFF, 0xF0,      # stwu r1, -16(r1)
    0x7C, 0x08, 0x02, 0xA6,      # mflr r0
    0x90, 0x01, 0x00, 0x14,      # stw r0, 20(r1)
    0x4E, 0x80, 0x00, 0x20,      # blr
])

# ARM32 (little-endian): push {fp, lr}; add fp, sp, #4; sub sp, sp, #8; bx lr
ARM32_BYTES = bytes([
    0x00, 0x48, 0x2D, 0xE9,      # push {fp, lr}
    0x04, 0xB0, 0x8D, 0xE2,      # add fp, sp, #4
    0x08, 0xD0, 0x4D, 0xE2,      # sub sp, sp, #8
    0x1E, 0xFF, 0x2F, 0xE1,      # bx lr
])


# ---------------------------------------------------------------------------
# Disassembly Functions
# ---------------------------------------------------------------------------

def disassemble_and_print(data, arch_name, label=None):
    """Disassemble bytes under the given architecture and print results.

    Args:
        data: Byte sequence to disassemble.
        arch_name: Architecture preset name (e.g., "x86-32").
        label: Optional label to print above the output.
    """
    if label:
        print(f"--- {label} ---")
    else:
        print(f"--- {arch_name} ---")

    instructions = disassemble(data, arch_name, base_addr=0)
    if instructions:
        print(format_disassembly(instructions, show_bytes=True))
    else:
        print("  (no valid instructions decoded)")
    print()


def disassemble_all_samples():
    """Disassemble each sample under its native architecture."""
    disassemble_and_print(X86_32_BYTES, "x86-32", label="x86-32 Sample")
    disassemble_and_print(MIPS32_BYTES, "mips32", label="MIPS32 Sample")
    disassemble_and_print(PPC32_BYTES, "ppc32", label="PPC32 Sample")

    # TODO: Disassemble ARM32_BYTES using the "arm32" preset.
    #       Call disassemble_and_print with the correct arguments.
    #       Uncomment the line below and fill in the arguments:
    # disassemble_and_print(???, ???, label="ARM32 Sample")


def cross_disassemble(data, label="unknown"):
    """Disassemble the same bytes under every available architecture.

    This demonstrates how different architectures decode the same bytes
    into entirely different instruction streams.

    Args:
        data: Byte sequence to disassemble.
        label: Label for the data being analyzed.
    """
    print(f"=== Cross-Disassembly: {label} ({len(data)} bytes) ===")
    print()
    for arch_name in ARCH_PRESETS:
        disassemble_and_print(data, arch_name)


# ---------------------------------------------------------------------------
# Architecture Detection (Heuristic)
# ---------------------------------------------------------------------------

def decode_ratio(data, arch_name):
    """Compute the ratio of successfully decoded bytes to total bytes.

    A higher ratio suggests the data is more likely to be valid code
    for the given architecture.

    Args:
        data: Byte sequence to test.
        arch_name: Architecture preset name.

    Returns:
        Float between 0.0 and 1.0.
    """
    if len(data) == 0:
        return 0.0
    instructions = disassemble(data, arch_name, base_addr=0)
    decoded_bytes = sum(len(raw) for _, _, _, raw in instructions)
    return decoded_bytes / len(data)


def detect_architecture(data):
    """Attempt to detect the CPU architecture of a byte sequence.

    Strategy:
      1. Compute the decode ratio for each architecture preset.
      2. Check for known prologue patterns as bonus signals.
      3. Return the architecture with the highest confidence.

    Args:
        data: Byte sequence to analyze.

    Returns:
        Tuple of (arch_name, confidence) where confidence is 0.0 to 1.0.
    """
    # TODO: Implement architecture detection. Steps:
    #
    # 1. For each architecture in ARCH_PRESETS, call decode_ratio(data, arch)
    #    and store the results.
    #
    # 2. (Bonus) Check for known prologue byte patterns:
    #    - x86-32: starts with 0x55 0x89 0xE5 (push ebp; mov ebp, esp)
    #    - MIPS32: first two bytes are 0x27 0xBD (addiu $sp)
    #    - PPC32:  first two bytes are 0x94 0x21 (stwu r1)
    #    If a prologue is found, boost that architecture's score.
    #
    # 3. Return the architecture name with the highest score and its
    #    confidence value as a tuple: (arch_name, confidence).
    #
    # Example return: ("x86-32", 0.95)

    return ("unknown", 0.0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Lab 3: Multi-Architecture Disassembly")
    print("=" * 60)
    print()

    # Part 1: Disassemble each sample under its native architecture
    print("PART 1: Native Disassembly")
    print()
    disassemble_all_samples()

    # Part 2: Cross-disassemble x86 bytes under all architectures
    print("PART 2: Cross-Disassembly Demo")
    print()
    cross_disassemble(X86_32_BYTES, label="x86-32 bytes")

    # Part 3: Architecture detection
    print("PART 3: Architecture Detection")
    print()
    samples = [
        ("x86-32 sample", X86_32_BYTES),
        ("MIPS32 sample", MIPS32_BYTES),
        ("PPC32 sample", PPC32_BYTES),
        ("ARM32 sample", ARM32_BYTES),
    ]
    for name, data in samples:
        arch, confidence = detect_architecture(data)
        print(f"  {name:20s} -> detected: {arch} (confidence: {confidence:.2f})")
    print()


if __name__ == "__main__":
    main()
