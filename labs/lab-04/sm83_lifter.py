"""
Lab 4: SM83 Lifter

Translate SM83 (Game Boy CPU) instructions into equivalent C code strings.
Each instruction is represented as an opcode byte with optional operands,
and the lifter produces C statements that operate on a cpu_t struct.
"""

import sys


# ---------------------------------------------------------------------------
# SM83 Register Names
# ---------------------------------------------------------------------------

# 8-bit register encoding used in many SM83 opcodes (bits 5:3 or 2:0)
REG8_TABLE = {
    0: "b", 1: "c", 2: "d", 3: "e",
    4: "h", 5: "l", 6: "(hl)", 7: "a",
}

# 16-bit register pairs for PUSH/POP and LD rr, nn
REG16_TABLE = {
    0: ("b", "c"),      # BC
    1: ("d", "e"),      # DE
    2: ("h", "l"),      # HL
    3: ("a", "f"),      # AF (for PUSH/POP)
}

REG16_NAMES = {
    0: "bc", 1: "de", 2: "hl", 3: "sp",
}


# ---------------------------------------------------------------------------
# Lifter Functions
# ---------------------------------------------------------------------------

def lift_ld_r_r(dst_reg, src_reg):
    """Lift LD r, r' -- load 8-bit register to register.

    Example: LD B, C  ->  cpu.b = cpu.c;

    Args:
        dst_reg: Destination register name (e.g., "b").
        src_reg: Source register name (e.g., "c").

    Returns:
        C code string.
    """
    # Handle (HL) memory access
    if dst_reg == "(hl)":
        return f"mem_write8(cpu.h << 8 | cpu.l, cpu.{src_reg});"
    if src_reg == "(hl)":
        return f"cpu.{dst_reg} = mem_read8(cpu.h << 8 | cpu.l);"
    return f"cpu.{dst_reg} = cpu.{src_reg};"


def lift_ld_r_imm8(dst_reg, imm8):
    """Lift LD r, n -- load immediate 8-bit value into register.

    Example: LD A, 0x42  ->  cpu.a = 0x42;

    Args:
        dst_reg: Destination register name.
        imm8: 8-bit immediate value.

    Returns:
        C code string.
    """
    if dst_reg == "(hl)":
        return f"mem_write8(cpu.h << 8 | cpu.l, 0x{imm8:02x});"
    return f"cpu.{dst_reg} = 0x{imm8:02x};"


def lift_add_a(src_reg):
    """Lift ADD A, r -- add register to accumulator.

    Must set all four flags: Z, N=0, H, C.

    Example: ADD A, B  ->
        { uint8_t prev = cpu.a;
          cpu.a = (cpu.a + cpu.b) & 0xFF;
          SET_Z(cpu.a); SET_N(0);
          SET_H_ADD(prev, cpu.b); SET_C_ADD(prev, cpu.b); }

    Args:
        src_reg: Source register name.

    Returns:
        C code string.
    """
    if src_reg == "(hl)":
        src_expr = "mem_read8(cpu.h << 8 | cpu.l)"
    else:
        src_expr = f"cpu.{src_reg}"
    return (
        f"{{ uint8_t prev = cpu.a; uint8_t val = {src_expr}; "
        f"cpu.a = (cpu.a + val) & 0xFF; "
        f"SET_Z(cpu.a); SET_N(0); "
        f"SET_H_ADD(prev, val); SET_C_ADD(prev, val); }}"
    )


def lift_sub_a(src_reg):
    """Lift SUB A, r -- subtract register from accumulator.

    Must set all four flags: Z, N=1, H, C.

    Args:
        src_reg: Source register name.

    Returns:
        C code string.
    """
    # TODO: Implement SUB A, r. Follow the same pattern as lift_add_a
    #       but use subtraction. Remember:
    #       - N flag is always set to 1 for subtraction
    #       - Use SET_H_SUB and SET_C_SUB instead of the ADD variants
    #       - The result must be masked with & 0xFF
    pass


def lift_inc(reg):
    """Lift INC r -- increment 8-bit register.

    Flags affected: Z, N=0, H. C is not affected.

    Args:
        reg: Register name.

    Returns:
        C code string.
    """
    # TODO: Implement INC r.
    #       - Save old value for half-carry computation
    #       - Increment and mask with 0xFF
    #       - Set Z flag, clear N flag, set H flag for add with 1
    #       - Do NOT modify C flag
    pass


def lift_dec(reg):
    """Lift DEC r -- decrement 8-bit register.

    Flags affected: Z, N=1, H. C is not affected.

    Args:
        reg: Register name.

    Returns:
        C code string.
    """
    # TODO: Implement DEC r.
    #       Similar to INC but subtracts 1. N flag is set to 1.
    pass


def lift_cp(src_reg):
    """Lift CP r -- compare accumulator with register (subtract without storing).

    Sets flags as if SUB was performed, but A is not modified.

    Args:
        src_reg: Source register name.

    Returns:
        C code string.
    """
    # TODO: Implement CP r.
    #       - Compute (A - src) but do NOT store the result in A
    #       - Set all four flags based on the subtraction result
    pass


def lift_and_a(src_reg):
    """Lift AND r -- bitwise AND with accumulator.

    Flags: Z, N=0, H=1, C=0.

    Args:
        src_reg: Source register name.

    Returns:
        C code string.
    """
    # TODO: Implement AND A, r.
    #       - cpu.a &= cpu.<src_reg>
    #       - Z is set based on result, N=0, H=1 (always), C=0
    pass


def lift_or_a(src_reg):
    """Lift OR r -- bitwise OR with accumulator.

    Flags: Z, N=0, H=0, C=0.

    Args:
        src_reg: Source register name.

    Returns:
        C code string.
    """
    # TODO: Implement OR A, r.
    #       - cpu.a |= cpu.<src_reg>
    #       - Z is set based on result, N=0, H=0, C=0
    pass


def lift_xor_a(src_reg):
    """Lift XOR r -- bitwise XOR with accumulator.

    Flags: Z, N=0, H=0, C=0.

    Args:
        src_reg: Source register name.

    Returns:
        C code string.
    """
    # TODO: Implement XOR A, r.
    #       - cpu.a ^= cpu.<src_reg>
    #       - Z is set based on result, N=0, H=0, C=0
    pass


def lift_jr(condition, offset):
    """Lift JR cc, offset -- relative jump.

    Args:
        condition: Condition string ("always", "z", "nz", "c", "nc") or None.
        offset: Signed 8-bit offset (already sign-extended to int).

    Returns:
        C code string with a goto or branch statement.
    """
    target = f"(cpu.pc + {offset})"
    if condition is None or condition == "always":
        return f"cpu.pc = {target}; goto dispatch;"

    cond_map = {
        "z":  "FLAG_Z(cpu.f)",
        "nz": "!FLAG_Z(cpu.f)",
        "c":  "FLAG_C(cpu.f)",
        "nc": "!FLAG_C(cpu.f)",
    }
    cond_expr = cond_map.get(condition, condition)
    return f"if ({cond_expr}) {{ cpu.pc = {target}; goto dispatch; }}"


def lift_jp(condition, addr):
    """Lift JP cc, addr -- absolute jump.

    Args:
        condition: Condition string or None for unconditional.
        addr: 16-bit absolute target address.

    Returns:
        C code string.
    """
    # TODO: Implement JP. Similar to JR but with an absolute address
    #       instead of a relative offset.
    pass


def lift_call(condition, addr):
    """Lift CALL cc, addr -- call subroutine.

    Must push the return address onto the stack before jumping.

    Args:
        condition: Condition string or None for unconditional.
        addr: 16-bit target address.

    Returns:
        C code string.
    """
    # TODO: Implement CALL.
    #       - Push current PC+3 onto the stack (two bytes, little-endian)
    #         by decrementing SP twice and writing to memory
    #       - Set PC to addr
    #       - If conditional, wrap in an if statement
    pass


def lift_ret(condition=None):
    """Lift RET / RET cc -- return from subroutine.

    Must pop the return address from the stack.

    Args:
        condition: Condition string or None for unconditional.

    Returns:
        C code string.
    """
    pop_code = (
        "{ uint16_t addr = mem_read8(cpu.sp) | (mem_read8(cpu.sp + 1) << 8); "
        "cpu.sp += 2; cpu.pc = addr; goto dispatch; }"
    )
    if condition is None or condition == "always":
        return pop_code

    cond_map = {
        "z":  "FLAG_Z(cpu.f)",
        "nz": "!FLAG_Z(cpu.f)",
        "c":  "FLAG_C(cpu.f)",
        "nc": "!FLAG_C(cpu.f)",
    }
    cond_expr = cond_map.get(condition, condition)
    return f"if ({cond_expr}) {pop_code}"


def lift_push(reg_pair_idx):
    """Lift PUSH rr -- push 16-bit register pair onto the stack.

    Args:
        reg_pair_idx: Index into REG16_TABLE (0=BC, 1=DE, 2=HL, 3=AF).

    Returns:
        C code string.
    """
    # TODO: Implement PUSH rr.
    #       - Decrement SP by 2
    #       - Write high byte to SP+1, low byte to SP
    #       - Use REG16_TABLE to get the register names
    pass


def lift_pop(reg_pair_idx):
    """Lift POP rr -- pop 16-bit register pair from the stack.

    Args:
        reg_pair_idx: Index into REG16_TABLE (0=BC, 1=DE, 2=HL, 3=AF).

    Returns:
        C code string.
    """
    # TODO: Implement POP rr.
    #       - Read low byte from SP, high byte from SP+1
    #       - Increment SP by 2
    #       - If popping AF, mask F with 0xF0 (lower nibble is always 0)
    pass


# ---------------------------------------------------------------------------
# Master Lift Function
# ---------------------------------------------------------------------------

def lift_instruction(opcode, operands=None):
    """Lift a single SM83 instruction to C code.

    This is a dispatch function that routes to the specific lifter
    based on the opcode byte.

    Args:
        opcode: The SM83 opcode byte (0x00-0xFF).
        operands: Optional dict with instruction operands
                  (e.g., {"imm8": 0x42, "src": "b", "dst": "a"}).

    Returns:
        C code string, or None if the opcode is not yet implemented.
    """
    if operands is None:
        operands = {}

    # NOP
    if opcode == 0x00:
        return "/* nop */;"

    # LD r, r' -- opcodes 0x40-0x7F (excluding 0x76 = HALT)
    if 0x40 <= opcode <= 0x7F and opcode != 0x76:
        dst_idx = (opcode >> 3) & 0x07
        src_idx = opcode & 0x07
        return lift_ld_r_r(REG8_TABLE[dst_idx], REG8_TABLE[src_idx])

    # ADD A, r -- opcodes 0x80-0x87
    if 0x80 <= opcode <= 0x87:
        src_idx = opcode & 0x07
        return lift_add_a(REG8_TABLE[src_idx])

    # SUB A, r -- opcodes 0x90-0x97
    if 0x90 <= opcode <= 0x97:
        src_idx = opcode & 0x07
        return lift_sub_a(REG8_TABLE[src_idx])

    # AND A, r -- opcodes 0xA0-0xA7
    if 0xA0 <= opcode <= 0xA7:
        src_idx = opcode & 0x07
        return lift_and_a(REG8_TABLE[src_idx])

    # XOR A, r -- opcodes 0xA8-0xAF
    if 0xA8 <= opcode <= 0xAF:
        src_idx = opcode & 0x07
        return lift_xor_a(REG8_TABLE[src_idx])

    # OR A, r -- opcodes 0xB0-0xB7
    if 0xB0 <= opcode <= 0xB7:
        src_idx = opcode & 0x07
        return lift_or_a(REG8_TABLE[src_idx])

    # CP r -- opcodes 0xB8-0xBF
    if 0xB8 <= opcode <= 0xBF:
        src_idx = opcode & 0x07
        return lift_cp(REG8_TABLE[src_idx])

    # INC r -- opcodes 0x04, 0x0C, 0x14, 0x1C, 0x24, 0x2C, 0x34, 0x3C
    if opcode & 0xC7 == 0x04:
        reg_idx = (opcode >> 3) & 0x07
        return lift_inc(REG8_TABLE[reg_idx])

    # DEC r -- opcodes 0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D
    if opcode & 0xC7 == 0x05:
        reg_idx = (opcode >> 3) & 0x07
        return lift_dec(REG8_TABLE[reg_idx])

    # JR unconditional (0x18) and conditional (0x20, 0x28, 0x30, 0x38)
    if opcode == 0x18:
        return lift_jr("always", operands.get("offset", 0))
    if opcode in (0x20, 0x28, 0x30, 0x38):
        cond_map = {0x20: "nz", 0x28: "z", 0x30: "nc", 0x38: "c"}
        return lift_jr(cond_map[opcode], operands.get("offset", 0))

    # RET unconditional (0xC9) and conditional (0xC0, 0xC8, 0xD0, 0xD8)
    if opcode == 0xC9:
        return lift_ret()
    if opcode in (0xC0, 0xC8, 0xD0, 0xD8):
        cond_map = {0xC0: "nz", 0xC8: "z", 0xD0: "nc", 0xD8: "c"}
        return lift_ret(cond_map[opcode])

    # PUSH (0xC5, 0xD5, 0xE5, 0xF5)
    if opcode in (0xC5, 0xD5, 0xE5, 0xF5):
        pair_idx = (opcode >> 4) & 0x03
        # Map: C->0(BC), D->1(DE), E->2(HL), F->3(AF)
        pair_idx = {0xC5: 0, 0xD5: 1, 0xE5: 2, 0xF5: 3}[opcode]
        return lift_push(pair_idx)

    # POP (0xC1, 0xD1, 0xE1, 0xF1)
    if opcode in (0xC1, 0xD1, 0xE1, 0xF1):
        pair_idx = {0xC1: 0, 0xD1: 1, 0xE1: 2, 0xF1: 3}[opcode]
        return lift_pop(pair_idx)

    # Unimplemented opcode
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Demonstrate the lifter with a few example instructions."""
    examples = [
        (0x00, {}, "NOP"),
        (0x41, {}, "LD B, C"),
        (0x80, {}, "ADD A, B"),
        (0x90, {}, "SUB A, B"),
        (0x04, {}, "INC B"),
        (0x05, {}, "DEC B"),
        (0xA0, {}, "AND A, B"),
        (0xA8, {}, "XOR A, B"),
        (0xB0, {}, "OR A, B"),
        (0xB8, {}, "CP B"),
        (0x18, {"offset": 5}, "JR +5"),
        (0x20, {"offset": -3}, "JR NZ, -3"),
        (0xC9, {}, "RET"),
        (0xC5, {}, "PUSH BC"),
        (0xC1, {}, "POP BC"),
    ]

    print("SM83 Lifter -- Example Output")
    print("=" * 50)
    for opcode, operands, desc in examples:
        result = lift_instruction(opcode, operands)
        status = result if result else "(not yet implemented)"
        print(f"  0x{opcode:02X} {desc:16s} -> {status}")


if __name__ == "__main__":
    main()
