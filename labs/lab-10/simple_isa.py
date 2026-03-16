"""
Lab 10: Simple ISA Definition

Defines a minimal 8-instruction ISA for use with the recursive descent
disassembler. All instructions are fixed-width: 2 bytes (1 opcode + 1 operand).

This is intentionally simple to focus on the disassembly algorithm rather
than the complexity of a real instruction set.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


# ---------------------------------------------------------------------------
# Opcodes
# ---------------------------------------------------------------------------

class Opcode(IntEnum):
    """The opcodes for our simple ISA."""
    NOP   = 0x00    # No operation
    LOAD  = 0x01    # Load value into accumulator
    STORE = 0x02    # Store accumulator to memory
    ADD   = 0x03    # Add operand to accumulator
    SUB   = 0x04    # Subtract operand from accumulator
    CMP   = 0x05    # Compare operand with accumulator (sets zero flag)
    JMP   = 0x06    # Unconditional jump to operand address
    JZ    = 0x07    # Jump to operand address if zero flag is set
    HALT  = 0x08    # Stop execution


# Instruction width in bytes (fixed for all instructions)
INSTRUCTION_WIDTH = 2


# ---------------------------------------------------------------------------
# Instruction properties
# ---------------------------------------------------------------------------

def is_branch(opcode: int) -> bool:
    """Return True if this opcode is a branch (conditional or unconditional)."""
    return opcode in (Opcode.JMP, Opcode.JZ)


def is_unconditional_jump(opcode: int) -> bool:
    """Return True if this opcode is an unconditional jump."""
    return opcode == Opcode.JMP


def is_conditional_branch(opcode: int) -> bool:
    """Return True if this opcode is a conditional branch."""
    return opcode == Opcode.JZ


def is_terminator(opcode: int) -> bool:
    """
    Return True if this instruction ends a basic block.
    Terminators are: jumps, conditional branches, and halt.
    """
    return opcode in (Opcode.JMP, Opcode.JZ, Opcode.HALT)


def is_halt(opcode: int) -> bool:
    """Return True if this is a halt instruction."""
    return opcode == Opcode.HALT


# ---------------------------------------------------------------------------
# Decoded instruction
# ---------------------------------------------------------------------------

@dataclass
class DecodedInstruction:
    """A single decoded instruction."""
    address: int        # Byte address in the binary
    opcode: int         # Raw opcode byte
    operand: int        # Raw operand byte
    mnemonic: str = ""  # Human-readable mnemonic

    def __post_init__(self):
        if not self.mnemonic:
            try:
                self.mnemonic = Opcode(self.opcode).name
            except ValueError:
                self.mnemonic = f"UNK({self.opcode:02X})"

    @property
    def size(self) -> int:
        """Instruction size in bytes."""
        return INSTRUCTION_WIDTH

    @property
    def next_address(self) -> int:
        """Address of the next sequential instruction."""
        return self.address + INSTRUCTION_WIDTH

    @property
    def branch_target(self) -> Optional[int]:
        """For branch instructions, return the target address. None otherwise."""
        if is_branch(self.opcode):
            return self.operand  # The operand IS the target address (byte address)
        return None

    def __str__(self) -> str:
        if is_branch(self.opcode):
            return f"0x{self.address:04X}: {self.mnemonic} 0x{self.operand:02X}"
        elif self.opcode in (Opcode.NOP, Opcode.HALT):
            return f"0x{self.address:04X}: {self.mnemonic}"
        else:
            return f"0x{self.address:04X}: {self.mnemonic} {self.operand}"


# ---------------------------------------------------------------------------
# Decoder
# ---------------------------------------------------------------------------

def decode_instruction(data: bytes, offset: int) -> Optional[DecodedInstruction]:
    """
    Decode a single instruction from the binary data at the given offset.

    Returns None if the offset is out of bounds.
    """
    if offset + INSTRUCTION_WIDTH > len(data):
        return None

    opcode = data[offset]
    operand = data[offset + 1]

    return DecodedInstruction(
        address=offset,
        opcode=opcode,
        operand=operand,
    )


# ---------------------------------------------------------------------------
# Assembler (for building test binaries)
# ---------------------------------------------------------------------------

def assemble(instructions: list) -> bytes:
    """
    Simple assembler: convert a list of (opcode, operand) tuples to bytes.

    Example:
        assemble([(Opcode.LOAD, 42), (Opcode.HALT, 0)])
        -> b'\\x01\\x2a\\x08\\x00'
    """
    result = bytearray()
    for opcode, operand in instructions:
        result.append(opcode & 0xFF)
        result.append(operand & 0xFF)
    return bytes(result)


if __name__ == "__main__":
    # Demo: assemble and decode a small program
    program = assemble([
        (Opcode.LOAD, 10),
        (Opcode.ADD, 5),
        (Opcode.CMP, 15),
        (Opcode.JZ, 10),       # Jump to address 10 (byte offset) if zero
        (Opcode.HALT, 0),
        (Opcode.STORE, 0),     # Address 10: store result
        (Opcode.HALT, 0),
    ])

    print("=== Simple ISA Demo ===\n")
    print(f"Binary: {program.hex()}")
    print(f"Length: {len(program)} bytes\n")

    offset = 0
    while offset < len(program):
        instr = decode_instruction(program, offset)
        if instr is None:
            break
        print(f"  {instr}")
        offset += INSTRUCTION_WIDTH
