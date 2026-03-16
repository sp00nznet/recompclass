"""
SimpleISA -- a toy 8-instruction architecture for learning CFG construction.

Each instruction is 1-3 bytes:
  byte 0: opcode
  byte 1-2: operand (if any)

This module is provided complete -- you do not need to modify it.
"""


# Instruction definitions: opcode -> (mnemonic, operand_bytes)
INSTRUCTIONS = {
    0x01: ("NOP",   0),   # no operand
    0x02: ("LOAD",  1),   # 1-byte register operand
    0x03: ("STORE", 1),   # 1-byte register operand
    0x04: ("ADD",   1),   # 1-byte register operand
    0x05: ("JMP",   2),   # 2-byte absolute address (little-endian)
    0x06: ("BEQ",   2),   # 2-byte absolute address (little-endian)
    0x07: ("CALL",  2),   # 2-byte absolute address (little-endian)
    0x08: ("RET",   0),   # no operand
}

# Opcodes that end a basic block
BRANCH_OPCODES = {0x05, 0x06, 0x07, 0x08}

# Opcodes that transfer control to an address operand
JUMP_OPCODES = {0x05, 0x06, 0x07}

# Opcodes that have a fall-through to the next instruction
# (JMP and RET do not fall through)
FALLTHROUGH_OPCODES = {0x06, 0x07}

# Opcodes that terminate control flow (no fall-through, no jump target
# that we follow in this block's context)
TERMINATOR_OPCODES = {0x05, 0x08}


def decode_one(data, offset):
    """Decode a single instruction at the given offset.

    Args:
        data: bytes of the program image.
        offset: byte offset to decode at.

    Returns:
        A dict with keys:
            "address"  - int offset
            "opcode"   - int raw opcode byte
            "mnemonic" - str
            "length"   - int total bytes
            "operand"  - int or None
                         For register operands: the register number.
                         For address operands: the 16-bit target address.

        Returns None if the opcode is invalid or data is too short.
    """
    if offset >= len(data):
        return None

    op = data[offset]
    if op not in INSTRUCTIONS:
        return None

    mnemonic, operand_bytes = INSTRUCTIONS[op]
    length = 1 + operand_bytes

    if offset + length > len(data):
        return None

    operand = None
    if operand_bytes == 1:
        operand = data[offset + 1]
    elif operand_bytes == 2:
        operand = data[offset + 1] | (data[offset + 2] << 8)

    return {
        "address": offset,
        "opcode": op,
        "mnemonic": mnemonic,
        "length": length,
        "operand": operand,
    }


def format_instruction(instr):
    """Format a decoded instruction for display."""
    if instr is None:
        return "<invalid>"
    mnemonic = instr["mnemonic"]
    if instr["operand"] is None:
        return f"{instr['address']:04X}: {mnemonic}"
    if instr["opcode"] in JUMP_OPCODES:
        return f"{instr['address']:04X}: {mnemonic} {instr['operand']:04X}"
    return f"{instr['address']:04X}: {mnemonic} r{instr['operand']}"
