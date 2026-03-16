"""
Lab 21: 6502 Instruction Decoder

Decode raw 6502 bytes into mnemonics, addressing modes, and operands.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Opcode Table
# ---------------------------------------------------------------------------
# Each entry: opcode_byte -> (mnemonic, addressing_mode, total_instruction_bytes)
#
# Addressing mode keys:
#   "imp"  = Implied           (1 byte total)
#   "acc"  = Accumulator       (1 byte total)
#   "imm"  = Immediate         (2 bytes total)
#   "zp"   = Zero Page         (2 bytes total)
#   "zpx"  = Zero Page,X       (2 bytes total)
#   "zpy"  = Zero Page,Y       (2 bytes total)
#   "abs"  = Absolute          (3 bytes total)
#   "abx"  = Absolute,X        (3 bytes total)
#   "aby"  = Absolute,Y        (3 bytes total)
#   "ind"  = Indirect          (3 bytes total)
#   "izx"  = (Indirect,X)      (2 bytes total)
#   "izy"  = (Indirect),Y      (2 bytes total)
#   "rel"  = Relative          (2 bytes total)

OPCODE_TABLE = {
    # LDA
    0xA9: ("LDA", "imm", 2),
    0xA5: ("LDA", "zp",  2),
    0xB5: ("LDA", "zpx", 2),
    0xAD: ("LDA", "abs", 3),
    0xBD: ("LDA", "abx", 3),
    0xB9: ("LDA", "aby", 3),
    0xA1: ("LDA", "izx", 2),
    0xB1: ("LDA", "izy", 2),
    # LDX
    0xA2: ("LDX", "imm", 2),
    0xA6: ("LDX", "zp",  2),
    0xB6: ("LDX", "zpy", 2),
    0xAE: ("LDX", "abs", 3),
    0xBE: ("LDX", "aby", 3),
    # LDY
    0xA0: ("LDY", "imm", 2),
    0xA4: ("LDY", "zp",  2),
    0xB4: ("LDY", "zpx", 2),
    0xAC: ("LDY", "abs", 3),
    0xBC: ("LDY", "abx", 3),
    # STA
    0x85: ("STA", "zp",  2),
    0x95: ("STA", "zpx", 2),
    0x8D: ("STA", "abs", 3),
    0x9D: ("STA", "abx", 3),
    0x99: ("STA", "aby", 3),
    0x81: ("STA", "izx", 2),
    0x91: ("STA", "izy", 2),
    # STX
    0x86: ("STX", "zp",  2),
    0x96: ("STX", "zpy", 2),
    0x8E: ("STX", "abs", 3),
    # STY
    0x84: ("STY", "zp",  2),
    0x94: ("STY", "zpx", 2),
    0x8C: ("STY", "abs", 3),
    # ADC
    0x69: ("ADC", "imm", 2),
    0x65: ("ADC", "zp",  2),
    0x6D: ("ADC", "abs", 3),
    # SBC
    0xE9: ("SBC", "imm", 2),
    0xE5: ("SBC", "zp",  2),
    0xED: ("SBC", "abs", 3),
    # AND
    0x29: ("AND", "imm", 2),
    0x25: ("AND", "zp",  2),
    0x2D: ("AND", "abs", 3),
    # ORA
    0x09: ("ORA", "imm", 2),
    0x05: ("ORA", "zp",  2),
    0x0D: ("ORA", "abs", 3),
    # EOR
    0x49: ("EOR", "imm", 2),
    0x45: ("EOR", "zp",  2),
    0x4D: ("EOR", "abs", 3),
    # CMP
    0xC9: ("CMP", "imm", 2),
    0xC5: ("CMP", "zp",  2),
    0xCD: ("CMP", "abs", 3),
    # CPX / CPY
    0xE0: ("CPX", "imm", 2),
    0xC0: ("CPY", "imm", 2),
    # INC / DEC
    0xE6: ("INC", "zp",  2),
    0xEE: ("INC", "abs", 3),
    0xC6: ("DEC", "zp",  2),
    0xCE: ("DEC", "abs", 3),
    # INX / INY / DEX / DEY
    0xE8: ("INX", "imp", 1),
    0xC8: ("INY", "imp", 1),
    0xCA: ("DEX", "imp", 1),
    0x88: ("DEY", "imp", 1),
    # ASL
    0x0A: ("ASL", "acc", 1),
    0x06: ("ASL", "zp",  2),
    0x0E: ("ASL", "abs", 3),
    # LSR
    0x4A: ("LSR", "acc", 1),
    0x46: ("LSR", "zp",  2),
    0x4E: ("LSR", "abs", 3),
    # ROL / ROR
    0x2A: ("ROL", "acc", 1),
    0x6A: ("ROR", "acc", 1),
    # Branches (relative)
    0x10: ("BPL", "rel", 2),
    0x30: ("BMI", "rel", 2),
    0x50: ("BVC", "rel", 2),
    0x70: ("BVS", "rel", 2),
    0x90: ("BCC", "rel", 2),
    0xB0: ("BCS", "rel", 2),
    0xD0: ("BNE", "rel", 2),
    0xF0: ("BEQ", "rel", 2),
    # JMP
    0x4C: ("JMP", "abs", 3),
    0x6C: ("JMP", "ind", 3),
    # JSR / RTS / RTI
    0x20: ("JSR", "abs", 3),
    0x60: ("RTS", "imp", 1),
    0x40: ("RTI", "imp", 1),
    # Stack
    0x48: ("PHA", "imp", 1),
    0x68: ("PLA", "imp", 1),
    0x08: ("PHP", "imp", 1),
    0x28: ("PLP", "imp", 1),
    # Flags
    0x18: ("CLC", "imp", 1),
    0x38: ("SEC", "imp", 1),
    0x58: ("CLI", "imp", 1),
    0x78: ("SEI", "imp", 1),
    0xD8: ("CLD", "imp", 1),
    0xF8: ("SED", "imp", 1),
    0xB8: ("CLV", "imp", 1),
    # NOP / BRK
    0xEA: ("NOP", "imp", 1),
    0x00: ("BRK", "imp", 1),
    # Transfer
    0xAA: ("TAX", "imp", 1),
    0x8A: ("TXA", "imp", 1),
    0xA8: ("TAY", "imp", 1),
    0x98: ("TYA", "imp", 1),
    0xBA: ("TSX", "imp", 1),
    0x9A: ("TXS", "imp", 1),
}


# ---------------------------------------------------------------------------
# Decoder
# ---------------------------------------------------------------------------

def decode_instruction(data, offset, base_address=0):
    """Decode a single 6502 instruction from *data* at *offset*.

    Args:
        data: bytes or bytearray of the binary image.
        offset: byte offset into *data* where the instruction starts.
        base_address: the memory address corresponding to offset 0 in *data*.

    Returns:
        A dict with keys:
            "address"  - int, the memory address of this instruction
            "opcode"   - int, the raw opcode byte
            "mnemonic" - str, e.g. "LDA"
            "mode"     - str, addressing mode key (e.g. "imm", "abs")
            "length"   - int, total instruction length in bytes
            "operand"  - int or None, the operand value (8-bit or 16-bit)
            "raw"      - bytes, the raw instruction bytes

        Returns None if the opcode is not in OPCODE_TABLE.
    """
    # TODO: 1. Read the opcode byte at data[offset].
    # TODO: 2. Look it up in OPCODE_TABLE. Return None if not found.
    # TODO: 3. Based on the instruction length (1, 2, or 3):
    #          - length 1: operand is None
    #          - length 2: operand is the single byte at data[offset+1]
    #          - length 3: operand is two bytes combined little-endian
    #                      (data[offset+1] | data[offset+2] << 8)
    # TODO: 4. Return the dict described above.
    #          "address" = base_address + offset
    #          "raw" = data[offset : offset + length]
    pass


def format_instruction(decoded):
    """Format a decoded instruction dict into a human-readable string.

    Args:
        decoded: dict returned by decode_instruction().

    Returns:
        A string like "$8000: LDA #$42" or "$8005: INX"

    Formatting rules by addressing mode:
        imp  -> "MNEMONIC"
        acc  -> "MNEMONIC A"
        imm  -> "MNEMONIC #$nn"
        zp   -> "MNEMONIC $nn"
        zpx  -> "MNEMONIC $nn,X"
        zpy  -> "MNEMONIC $nn,Y"
        abs  -> "MNEMONIC $nnnn"
        abx  -> "MNEMONIC $nnnn,X"
        aby  -> "MNEMONIC $nnnn,Y"
        ind  -> "MNEMONIC ($nnnn)"
        izx  -> "MNEMONIC ($nn,X)"
        izy  -> "MNEMONIC ($nn),Y"
        rel  -> "MNEMONIC $nnnn"  (show the absolute target address)
    """
    # TODO: Build the formatted string.
    #       Start with: f"${decoded['address']:04X}: {decoded['mnemonic']}"
    #       Then append the operand in the correct syntax.
    #
    #       For "rel" mode, compute the branch target:
    #           signed_offset = operand if operand < 128 else operand - 256
    #           target = address + length + signed_offset
    #       Format the target as $nnnn (4 hex digits).
    #
    #       For 1-byte operands, format as $nn (2 hex digits).
    #       For 2-byte operands, format as $nnnn (4 hex digits).
    pass


def disassemble(data, base_address=0, count=None):
    """Disassemble a stream of 6502 bytes.

    Args:
        data: bytes of 6502 machine code.
        base_address: starting address for the first byte.
        count: maximum number of instructions to decode (None = decode all).

    Returns:
        A list of formatted instruction strings.
    """
    # TODO: Walk through data, calling decode_instruction() and
    #       format_instruction() for each instruction.
    #       - Advance offset by the instruction's length.
    #       - If decode_instruction() returns None (unknown opcode),
    #         skip 1 byte and continue.
    #       - Stop when you reach the end of data, or after decoding
    #         *count* instructions (if count is not None).
    #       - Return the list of formatted strings.
    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Example: decode a small code snippet
    code = bytes([
        0xA9, 0x42,             # LDA #$42
        0x8D, 0x00, 0x02,       # STA $0200
        0xE8,                   # INX
        0xD0, 0xF9,             # BNE $8002
        0x60,                   # RTS
    ])
    lines = disassemble(code, base_address=0x8000)
    if lines:
        for line in lines:
            print(line)
    else:
        print("disassemble() returned None -- implement the TODO sections.")


if __name__ == "__main__":
    main()
