"""
Lab 12: Micro-Lifter (MIPS)

Lifts a subset of MIPS instructions to C code that operates on a
register context struct. This is the core translation step in a
static recompiler.

Supported instructions (10 total):
  ALU:     ADD, ADDI, SUB, AND, OR, XOR
  Memory:  LW, SW
  Control: BEQ, J

Already implemented: ADD, LW, J
TODO: ADDI, SUB, AND, OR, XOR, SW, BEQ
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


# ---------------------------------------------------------------------------
# Instruction types
# ---------------------------------------------------------------------------

class MipsOp(Enum):
    """MIPS instruction opcodes (simplified -- not real encoding)."""
    ADD  = auto()
    ADDI = auto()
    SUB  = auto()
    AND  = auto()
    OR   = auto()
    XOR  = auto()
    LW   = auto()
    SW   = auto()
    BEQ  = auto()
    J    = auto()


@dataclass
class MipsInstruction:
    """
    A decoded MIPS instruction in a simplified representation.

    For R-type (ADD, SUB, AND, OR, XOR):
        rs, rt, rd are register indices (0-31)

    For I-type (ADDI, LW, SW, BEQ):
        rs, rt are register indices; imm is the immediate value

    For J-type (J):
        target is the jump target address
    """
    op: MipsOp
    rd: int = 0             # Destination register (R-type)
    rs: int = 0             # Source register 1
    rt: int = 0             # Source register 2 / destination (I-type)
    imm: int = 0            # Immediate value (I-type)
    target: int = 0         # Jump target (J-type)
    address: int = 0        # Address of this instruction in the original binary


# ---------------------------------------------------------------------------
# Register name helper
# ---------------------------------------------------------------------------

def reg(index: int) -> str:
    """
    Return the C expression for accessing a MIPS register.
    Register 0 ($zero) is always 0 in MIPS; we still reference ctx->r[0]
    but note that writes to r[0] should be discarded.
    """
    return f"ctx->r[{index}]"


# ---------------------------------------------------------------------------
# Lifter
# ---------------------------------------------------------------------------

class MipsLifter:
    """
    Lifts MIPS instructions to C statements.

    Each lift_* method returns a string containing one or more C statements
    that implement the instruction's semantics using a mips_state_t context.

    The generated code assumes:
        mips_state_t *ctx;   // CPU state (registers + memory)
    """

    def lift(self, instr: MipsInstruction) -> str:
        """
        Lift a single MIPS instruction to C code.

        Args:
            instr: The decoded MIPS instruction.

        Returns:
            A string containing C statement(s) implementing the instruction.

        Raises:
            ValueError: If the instruction opcode is not supported.
        """
        dispatch = {
            MipsOp.ADD:  self.lift_add,
            MipsOp.ADDI: self.lift_addi,
            MipsOp.SUB:  self.lift_sub,
            MipsOp.AND:  self.lift_and,
            MipsOp.OR:   self.lift_or,
            MipsOp.XOR:  self.lift_xor,
            MipsOp.LW:   self.lift_lw,
            MipsOp.SW:   self.lift_sw,
            MipsOp.BEQ:  self.lift_beq,
            MipsOp.J:    self.lift_j,
        }

        handler = dispatch.get(instr.op)
        if handler is None:
            raise ValueError(f"Unsupported instruction: {instr.op}")

        return handler(instr)

    # -------------------------------------------------------------------
    # IMPLEMENTED: ADD, LW, J
    # -------------------------------------------------------------------

    def lift_add(self, instr: MipsInstruction) -> str:
        """
        ADD rd, rs, rt  ->  rd = rs + rt

        Note: In real MIPS, ADD traps on overflow. We ignore that here.
        TODO: Add overflow detection.
        """
        # Guard against writes to $zero
        if instr.rd == 0:
            return "/* ADD to $zero -- discarded */"
        return f"{reg(instr.rd)} = {reg(instr.rs)} + {reg(instr.rt)};"

    def lift_lw(self, instr: MipsInstruction) -> str:
        """
        LW rt, imm(rs)  ->  rt = *(uint32_t*)(mem + rs + imm)

        Loads a 32-bit word from memory at address (rs + imm).
        """
        if instr.rt == 0:
            return "/* LW to $zero -- discarded */"
        offset_expr = f"{reg(instr.rs)} + {instr.imm}" if instr.imm != 0 else reg(instr.rs)
        return f"{reg(instr.rt)} = *(uint32_t *)(ctx->mem + {offset_expr});"

    def lift_j(self, instr: MipsInstruction) -> str:
        """
        J target  ->  goto label

        Unconditional jump. In recompiled code, this becomes a goto
        to the label corresponding to the target address.
        """
        return f"goto label_{instr.target:08X};"

    # -------------------------------------------------------------------
    # TODO: Implement the remaining 7 instructions
    # -------------------------------------------------------------------

    def lift_addi(self, instr: MipsInstruction) -> str:
        """
        ADDI rt, rs, imm  ->  rt = rs + imm

        TODO: Implement this instruction.
              - The destination is rt (not rd).
              - The immediate value is a signed 16-bit integer,
                but for this lab treating it as a plain int is fine.
              - Guard against writes to $zero.
        """
        raise NotImplementedError("ADDI lifting not yet implemented")

    def lift_sub(self, instr: MipsInstruction) -> str:
        """
        SUB rd, rs, rt  ->  rd = rs - rt

        TODO: Implement this instruction.
              - Same structure as ADD but with subtraction.
              - Guard against writes to $zero.
        """
        raise NotImplementedError("SUB lifting not yet implemented")

    def lift_and(self, instr: MipsInstruction) -> str:
        """
        AND rd, rs, rt  ->  rd = rs & rt

        TODO: Implement this instruction.
              - Bitwise AND.
              - Guard against writes to $zero.
        """
        raise NotImplementedError("AND lifting not yet implemented")

    def lift_or(self, instr: MipsInstruction) -> str:
        """
        OR rd, rs, rt  ->  rd = rs | rt

        TODO: Implement this instruction.
              - Bitwise OR.
              - Guard against writes to $zero.
        """
        raise NotImplementedError("OR lifting not yet implemented")

    def lift_xor(self, instr: MipsInstruction) -> str:
        """
        XOR rd, rs, rt  ->  rd = rs ^ rt

        TODO: Implement this instruction.
              - Bitwise XOR.
              - Guard against writes to $zero.
        """
        raise NotImplementedError("XOR lifting not yet implemented")

    def lift_sw(self, instr: MipsInstruction) -> str:
        """
        SW rt, imm(rs)  ->  *(uint32_t*)(mem + rs + imm) = rt

        TODO: Implement this instruction.
              - This is the reverse of LW: store rt to memory.
              - The memory address is (rs + imm).
        """
        raise NotImplementedError("SW lifting not yet implemented")

    def lift_beq(self, instr: MipsInstruction) -> str:
        """
        BEQ rs, rt, offset  ->  if (rs == rt) goto label

        TODO: Implement this instruction.
              - Compare rs and rt.
              - If equal, jump to the target address.
              - The target address is: instr.address + 4 + (instr.imm * 4)
                (In real MIPS, the offset is relative to the next instruction.)
              - Generate an if-goto statement.
        """
        raise NotImplementedError("BEQ lifting not yet implemented")


# ---------------------------------------------------------------------------
# C code preamble (for context)
# ---------------------------------------------------------------------------

C_PREAMBLE = """\
#include <stdint.h>

typedef struct {
    uint32_t r[32];     /* General-purpose registers (r[0] is always 0) */
    uint32_t pc;        /* Program counter */
    uint8_t *mem;       /* Memory pointer */
} mips_state_t;
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Lab 12: Micro-Lifter (MIPS) ===\n")
    print("C preamble (register context struct):")
    print(C_PREAMBLE)

    lifter = MipsLifter()

    # Demonstrate the three implemented instructions
    examples = [
        MipsInstruction(op=MipsOp.ADD, rd=3, rs=1, rt=2),
        MipsInstruction(op=MipsOp.ADD, rd=0, rs=1, rt=2),  # Write to $zero
        MipsInstruction(op=MipsOp.LW, rt=4, rs=5, imm=16),
        MipsInstruction(op=MipsOp.LW, rt=6, rs=7, imm=0),
        MipsInstruction(op=MipsOp.J, target=0x00400100),
    ]

    print("Lifted instructions:")
    for instr in examples:
        c_code = lifter.lift(instr)
        print(f"  {instr.op.name:5s} -> {c_code}")

    print()
    print("Remaining instructions (ADDI, SUB, AND, OR, XOR, SW, BEQ) are TODO.")
    print("Implement them by following the patterns in the existing lift methods.")
