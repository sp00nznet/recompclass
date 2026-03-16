"""
Lab 35: SH-2 Delay Slot Lifter

Lift SH-2 instructions to pseudo-C with correct delay slot handling.
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# SH-2 Decoder
# ---------------------------------------------------------------------------

def _sign_extend_8(val):
    """Sign-extend an 8-bit value to a Python int."""
    if val & 0x80:
        return val - 0x100
    return val


def _sign_extend_12(val):
    """Sign-extend a 12-bit value to a Python int."""
    if val & 0x800:
        return val - 0x1000
    return val


def decode_sh2(data, offset, base_address=0):
    """Decode a single 16-bit SH-2 instruction.

    Args:
        data: bytes of SH-2 machine code (big-endian).
        offset: byte offset into data.
        base_address: address of the first byte of data.

    Returns:
        A dict with keys:
            "address"    - int, the instruction's address
            "raw"        - int, the raw 16-bit instruction word
            "mnemonic"   - str, e.g. "MOV", "ADD", "BRA"
            "has_delay"  - bool, True if this instruction has a delay slot
            "rn"         - int or None, destination register number
            "rm"         - int or None, source register number
            "disp"       - int or None, signed displacement (for branches)
            "target"     - int or None, computed branch target address

        Returns None if offset is out of range.

    Encoding patterns (big-endian 16-bit word):
        MOV Rm, Rn:    0110 nnnn mmmm 0011
        ADD Rm, Rn:    0011 nnnn mmmm 1100
        CMP/EQ Rm, Rn: 0011 nnnn mmmm 0000
        BT disp:       1000 1001 dddd dddd
        BF disp:       1000 1011 dddd dddd
        BRA disp:      1010 dddd dddd dddd
        JSR @Rm:       0100 mmmm 0000 1011
        RTS:           0000 0000 0000 1011
    """
    # TODO: 1. Check bounds: offset + 2 <= len(data). Return None if not.
    # TODO: 2. Read the 16-bit big-endian word:
    #          word = struct.unpack_from(">H", data, offset)[0]
    # TODO: 3. Compute the instruction address: base_address + offset
    # TODO: 4. Decode based on the bit pattern:
    #
    #   RTS:  word == 0x000B
    #         mnemonic="RTS", has_delay=True, no registers, no disp
    #
    #   MOV:  (word & 0xF00F) == 0x6003
    #         rn = (word >> 8) & 0xF
    #         rm = (word >> 4) & 0xF
    #         mnemonic="MOV", has_delay=False
    #
    #   ADD:  (word & 0xF00F) == 0x300C
    #         rn = (word >> 8) & 0xF
    #         rm = (word >> 4) & 0xF
    #         mnemonic="ADD", has_delay=False
    #
    #   CMP/EQ: (word & 0xF00F) == 0x3000
    #         rn = (word >> 8) & 0xF
    #         rm = (word >> 4) & 0xF
    #         mnemonic="CMP/EQ", has_delay=False
    #
    #   BT:   (word & 0xFF00) == 0x8900
    #         disp = sign_extend_8(word & 0xFF)
    #         target = address + 4 + disp * 2
    #         mnemonic="BT", has_delay=True
    #
    #   BF:   (word & 0xFF00) == 0x8B00
    #         disp = sign_extend_8(word & 0xFF)
    #         target = address + 4 + disp * 2
    #         mnemonic="BF", has_delay=True
    #
    #   BRA:  (word & 0xF000) == 0xA000
    #         disp = sign_extend_12(word & 0xFFF)
    #         target = address + 4 + disp * 2
    #         mnemonic="BRA", has_delay=True
    #
    #   JSR:  (word & 0xF0FF) == 0x400B
    #         rm = (word >> 8) & 0xF
    #         mnemonic="JSR", has_delay=True
    #
    #   Otherwise: mnemonic="UNKNOWN", has_delay=False
    #
    # TODO: 5. Return the dict.
    pass


# ---------------------------------------------------------------------------
# Lifter
# ---------------------------------------------------------------------------

def lift_instruction(instr):
    """Lift a single decoded SH-2 instruction to pseudo-C.

    Args:
        instr: dict from decode_sh2().

    Returns:
        A string of pseudo-C code (without the delay slot handling --
        that is done by lift_block).

    Output for each mnemonic:
        MOV:    "regs[{rn}] = regs[{rm}];"
        ADD:    "regs[{rn}] = regs[{rn}] + regs[{rm}];"
        CMP/EQ: "T = (regs[{rn}] == regs[{rm}]);"
        BT:     "if (T) goto label_{target:08X};"
        BF:     "if (!T) goto label_{target:08X};"
        BRA:    "goto label_{target:08X};"
        JSR:    "PR = 0x{address+4:08X}; goto *regs[{rm}];"
        RTS:    "goto *PR;"
        UNKNOWN: "/* unknown: 0x{raw:04X} */;"
    """
    # TODO: Implement based on the mnemonic.
    pass


def lift_block(data, base_address=0):
    """Lift a block of SH-2 instructions to pseudo-C with delay slot handling.

    The key rule: when an instruction has a delay slot (has_delay=True),
    the next instruction is the delay slot. It must be lifted BEFORE the
    branch instruction's C code.

    The output should include comments showing the original address and
    mnemonic, then the C code.

    Args:
        data: bytes of SH-2 code (big-endian).
        base_address: address of the first byte.

    Returns:
        A list of strings (lines of pseudo-C).
    """
    # TODO: 1. Initialize offset = 0 and an output list.
    # TODO: 2. While offset < len(data):
    #          a. Decode the instruction at offset.
    #          b. If it has a delay slot:
    #             - Decode the NEXT instruction (offset + 2) as the delay slot.
    #             - Emit a comment for the branch instruction.
    #             - Emit the lifted delay slot instruction (with a "// delay slot" comment).
    #             - Emit the lifted branch instruction.
    #             - Advance offset by 4 (skip both instructions).
    #          c. If no delay slot:
    #             - Emit a comment and the lifted instruction.
    #             - Advance offset by 2.
    # TODO: 3. Return the output list.
    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Example: MOV R0,R1 ; CMP/EQ R2,R1 ; BT +4 ; ADD R3,R0 ; (target) RTS; NOP
    #
    # MOV R0, R1:   0x6103  -> 0110 0001 0000 0011
    # CMP/EQ R2,R1: 0x3120  -> 0011 0001 0010 0000
    # BT +2:        0x8902  -> 1000 1001 0000 0010  (target = addr+4+2*2 = addr+8)
    # ADD R3, R0:   0x303C  -> 0011 0000 0011 1100  (delay slot of BT)
    # RTS:          0x000B  -> 0000 0000 0000 1011
    # NOP (MOV R0,R0): 0x6003 -> delay slot of RTS

    program = struct.pack(">HHHHHH",
        0x6103,  # MOV R0, R1
        0x3120,  # CMP/EQ R2, R1
        0x8902,  # BT +2
        0x303C,  # ADD R3, R0  (delay slot of BT)
        0x000B,  # RTS
        0x6003,  # MOV R0, R0 (delay slot of RTS, effectively NOP)
    )

    lines = lift_block(program, base_address=0x06000000)
    if lines is None:
        print("lift_block() returned None -- implement the TODO sections.")
        return

    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
