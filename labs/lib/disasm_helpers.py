"""
Shared helper functions for recompclass labs.

Provides common utilities for disassembly, binary parsing, and
display formatting used across multiple lab exercises.
"""

from capstone import Cs, CS_ARCH_X86, CS_ARCH_MIPS, CS_ARCH_PPC, CS_ARCH_ARM
from capstone import CS_MODE_16, CS_MODE_32, CS_MODE_64, CS_MODE_MIPS32
from capstone import CS_MODE_BIG_ENDIAN, CS_MODE_LITTLE_ENDIAN
import struct


# Architecture presets for Capstone
ARCH_PRESETS = {
    "x86-16":    (CS_ARCH_X86, CS_MODE_16),
    "x86-32":    (CS_ARCH_X86, CS_MODE_32),
    "x86-64":    (CS_ARCH_X86, CS_MODE_64),
    "mips32":    (CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_BIG_ENDIAN),
    "mips32le":  (CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN),
    "ppc32":     (CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN),
    "arm32":     (CS_ARCH_ARM, CS_MODE_ARM),
}


def create_disassembler(arch_name):
    """Create a Capstone disassembler for the given architecture preset.

    Args:
        arch_name: One of the keys in ARCH_PRESETS.

    Returns:
        A Capstone Cs instance configured for the architecture.
    """
    if arch_name not in ARCH_PRESETS:
        raise ValueError(
            f"Unknown architecture '{arch_name}'. "
            f"Available: {', '.join(ARCH_PRESETS.keys())}"
        )
    arch, mode = ARCH_PRESETS[arch_name]
    return Cs(arch, mode)


def disassemble(data, arch_name, base_addr=0):
    """Disassemble binary data and return a list of instruction tuples.

    Args:
        data: Bytes to disassemble.
        arch_name: Architecture preset name.
        base_addr: Base address for disassembly.

    Returns:
        List of (address, mnemonic, op_str, bytes) tuples.
    """
    md = create_disassembler(arch_name)
    md.detail = True
    results = []
    for insn in md.disasm(data, base_addr):
        results.append((insn.address, insn.mnemonic, insn.op_str, insn.bytes))
    return results


def format_disassembly(instructions, show_bytes=True):
    """Format disassembled instructions as a string table.

    Args:
        instructions: List of (address, mnemonic, op_str, bytes) tuples.
        show_bytes: Whether to include raw byte column.

    Returns:
        Formatted string.
    """
    lines = []
    for addr, mnemonic, op_str, raw in instructions:
        if show_bytes:
            hex_bytes = raw.hex()
            lines.append(f"  {addr:08x}:  {hex_bytes:<16s}  {mnemonic:<8s} {op_str}")
        else:
            lines.append(f"  {addr:08x}:  {mnemonic:<8s} {op_str}")
    return "\n".join(lines)


def read_u8(data, offset):
    """Read an unsigned 8-bit integer."""
    return data[offset]


def read_u16_le(data, offset):
    """Read an unsigned 16-bit little-endian integer."""
    return struct.unpack_from("<H", data, offset)[0]


def read_u16_be(data, offset):
    """Read an unsigned 16-bit big-endian integer."""
    return struct.unpack_from(">H", data, offset)[0]


def read_u32_le(data, offset):
    """Read an unsigned 32-bit little-endian integer."""
    return struct.unpack_from("<I", data, offset)[0]


def read_u32_be(data, offset):
    """Read an unsigned 32-bit big-endian integer."""
    return struct.unpack_from(">I", data, offset)[0]


def hex_dump(data, base_addr=0, width=16):
    """Produce a hex dump of binary data.

    Args:
        data: Bytes to dump.
        base_addr: Starting address label.
        width: Bytes per line.

    Returns:
        Formatted hex dump string.
    """
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"  {base_addr + i:08x}:  {hex_part:<{width * 3}}  {ascii_part}")
    return "\n".join(lines)
