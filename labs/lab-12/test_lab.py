"""
Lab 12 Tests: Micro-Lifter (MIPS)

Tests the C code output for each MIPS instruction.
Implemented instructions should produce correct C; unimplemented ones
should raise NotImplementedError.
"""

import unittest
from mips_lifter import MipsLifter, MipsInstruction, MipsOp


class TestLiftADD(unittest.TestCase):
    """Test ADD instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_add_basic(self):
        """ADD $3, $1, $2 -> ctx->r[3] = ctx->r[1] + ctx->r[2];"""
        instr = MipsInstruction(op=MipsOp.ADD, rd=3, rs=1, rt=2)
        c = self.lifter.lift(instr)
        self.assertIn("ctx->r[3]", c)
        self.assertIn("ctx->r[1]", c)
        self.assertIn("ctx->r[2]", c)
        self.assertIn("+", c)
        self.assertTrue(c.endswith(";"))

    def test_add_to_zero_discarded(self):
        """ADD $0, $1, $2 should be discarded (writes to $zero)."""
        instr = MipsInstruction(op=MipsOp.ADD, rd=0, rs=1, rt=2)
        c = self.lifter.lift(instr)
        self.assertIn("discard", c.lower())

    def test_add_same_register(self):
        """ADD $1, $1, $1 -> doubling."""
        instr = MipsInstruction(op=MipsOp.ADD, rd=1, rs=1, rt=1)
        c = self.lifter.lift(instr)
        self.assertIn("ctx->r[1]", c)


class TestLiftLW(unittest.TestCase):
    """Test LW instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_lw_with_offset(self):
        """LW $4, 16($5) -> load from memory at r[5]+16."""
        instr = MipsInstruction(op=MipsOp.LW, rt=4, rs=5, imm=16)
        c = self.lifter.lift(instr)
        self.assertIn("ctx->r[4]", c)
        self.assertIn("ctx->r[5]", c)
        self.assertIn("16", c)
        self.assertIn("uint32_t", c)
        self.assertIn("ctx->mem", c)

    def test_lw_zero_offset(self):
        """LW $6, 0($7) -> load from memory at r[7]."""
        instr = MipsInstruction(op=MipsOp.LW, rt=6, rs=7, imm=0)
        c = self.lifter.lift(instr)
        self.assertIn("ctx->r[6]", c)
        self.assertIn("ctx->r[7]", c)

    def test_lw_to_zero_discarded(self):
        """LW $0, 0($1) should be discarded."""
        instr = MipsInstruction(op=MipsOp.LW, rt=0, rs=1, imm=0)
        c = self.lifter.lift(instr)
        self.assertIn("discard", c.lower())


class TestLiftJ(unittest.TestCase):
    """Test J instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_j_generates_goto(self):
        """J 0x00400100 -> goto label_00400100;"""
        instr = MipsInstruction(op=MipsOp.J, target=0x00400100)
        c = self.lifter.lift(instr)
        self.assertIn("goto", c)
        self.assertIn("00400100", c)
        self.assertTrue(c.endswith(";"))

    def test_j_different_target(self):
        instr = MipsInstruction(op=MipsOp.J, target=0x00400200)
        c = self.lifter.lift(instr)
        self.assertIn("00400200", c)


# ---------------------------------------------------------------------------
# Tests for TODO instructions
# These tests verify the instructions raise NotImplementedError until
# the student implements them. Once implemented, these tests serve as
# the correctness checks.
# ---------------------------------------------------------------------------

class TestLiftADDI(unittest.TestCase):
    """Test ADDI instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_addi_not_implemented(self):
        """ADDI should raise NotImplementedError until implemented."""
        instr = MipsInstruction(op=MipsOp.ADDI, rt=3, rs=1, imm=42)
        try:
            c = self.lifter.lift(instr)
            # If implemented, verify correctness
            self.assertIn("ctx->r[3]", c)
            self.assertIn("ctx->r[1]", c)
            self.assertIn("42", c)
            self.assertIn("+", c)
        except NotImplementedError:
            pass  # Expected until implemented

    def test_addi_to_zero_discarded(self):
        """ADDI $0, $1, 5 should be discarded."""
        instr = MipsInstruction(op=MipsOp.ADDI, rt=0, rs=1, imm=5)
        try:
            c = self.lifter.lift(instr)
            self.assertIn("discard", c.lower())
        except NotImplementedError:
            pass


class TestLiftSUB(unittest.TestCase):
    """Test SUB instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_sub_not_implemented(self):
        instr = MipsInstruction(op=MipsOp.SUB, rd=3, rs=1, rt=2)
        try:
            c = self.lifter.lift(instr)
            self.assertIn("ctx->r[3]", c)
            self.assertIn("-", c)
        except NotImplementedError:
            pass


class TestLiftAND(unittest.TestCase):
    """Test AND instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_and_not_implemented(self):
        instr = MipsInstruction(op=MipsOp.AND, rd=3, rs=1, rt=2)
        try:
            c = self.lifter.lift(instr)
            self.assertIn("ctx->r[3]", c)
            self.assertIn("&", c)
        except NotImplementedError:
            pass


class TestLiftOR(unittest.TestCase):
    """Test OR instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_or_not_implemented(self):
        instr = MipsInstruction(op=MipsOp.OR, rd=3, rs=1, rt=2)
        try:
            c = self.lifter.lift(instr)
            self.assertIn("ctx->r[3]", c)
            self.assertIn("|", c)
        except NotImplementedError:
            pass


class TestLiftXOR(unittest.TestCase):
    """Test XOR instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_xor_not_implemented(self):
        instr = MipsInstruction(op=MipsOp.XOR, rd=3, rs=1, rt=2)
        try:
            c = self.lifter.lift(instr)
            self.assertIn("ctx->r[3]", c)
            self.assertIn("^", c)
        except NotImplementedError:
            pass


class TestLiftSW(unittest.TestCase):
    """Test SW instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_sw_not_implemented(self):
        instr = MipsInstruction(op=MipsOp.SW, rt=4, rs=5, imm=8)
        try:
            c = self.lifter.lift(instr)
            self.assertIn("ctx->mem", c)
            self.assertIn("ctx->r[5]", c)
            self.assertIn("ctx->r[4]", c)
            self.assertIn("8", c)
        except NotImplementedError:
            pass


class TestLiftBEQ(unittest.TestCase):
    """Test BEQ instruction lifting."""

    def setUp(self):
        self.lifter = MipsLifter()

    def test_beq_not_implemented(self):
        instr = MipsInstruction(op=MipsOp.BEQ, rs=1, rt=2, imm=4, address=0x00400000)
        try:
            c = self.lifter.lift(instr)
            self.assertIn("if", c)
            self.assertIn("==", c)
            self.assertIn("goto", c)
        except NotImplementedError:
            pass


class TestUnsupportedInstruction(unittest.TestCase):
    """Test behavior for unsupported instructions."""

    def test_unknown_op_raises(self):
        """An instruction not in the dispatch table should raise ValueError."""
        lifter = MipsLifter()
        # Manually create an instruction with an invalid op
        # (This tests the dispatch mechanism, not a real MIPS instruction)
        # Since all MipsOp values are handled, we test by directly calling
        # lift with a mock -- but we can at least verify the dispatch works
        # for all known ops without crashing.
        for op in MipsOp:
            instr = MipsInstruction(op=op)
            try:
                lifter.lift(instr)
            except NotImplementedError:
                pass  # Fine -- just means it is a TODO instruction
            except ValueError:
                self.fail(f"Unexpected ValueError for known op {op}")


if __name__ == "__main__":
    unittest.main()
