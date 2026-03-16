"""
Tests for Lab 35: SH-2 Delay Slot Lifter
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import sh2_lifter


# ---------------------------------------------------------------------------
# Helper to build SH-2 code
# ---------------------------------------------------------------------------

def pack_sh2(*words):
    """Pack 16-bit words as big-endian bytes."""
    return struct.pack(">" + "H" * len(words), *words)


BASE = 0x06000000

# Instruction encodings
MOV_R0_R1    = 0x6103   # MOV R0, R1
ADD_R2_R3    = 0x332C   # ADD R2, R3
CMP_EQ_R0_R1 = 0x3100  # CMP/EQ R0, R1
BT_PLUS_2    = 0x8902   # BT +2  -> target = PC+4+2*2 = PC+8
BF_PLUS_1    = 0x8B01   # BF +1  -> target = PC+4+1*2 = PC+6
BRA_PLUS_3   = 0xA003   # BRA +3 -> target = PC+4+3*2 = PC+10
RTS          = 0x000B   # RTS
JSR_R4       = 0x440B   # JSR @R4
NOP_MOV      = 0x6003   # MOV R0, R0 (effectively NOP)


# ---------------------------------------------------------------------------
# decode_sh2
# ---------------------------------------------------------------------------

class TestDecodeSH2:
    def test_returns_dict(self):
        data = pack_sh2(MOV_R0_R1)
        result = sh2_lifter.decode_sh2(data, 0, BASE)
        assert result is not None, "decode_sh2() returned None"
        assert isinstance(result, dict)

    def test_mov(self):
        data = pack_sh2(MOV_R0_R1)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "MOV"
        assert r["rn"] == 1
        assert r["rm"] == 0
        assert r["has_delay"] is False

    def test_add(self):
        data = pack_sh2(ADD_R2_R3)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "ADD"
        assert r["rn"] == 3
        assert r["rm"] == 2

    def test_cmp_eq(self):
        data = pack_sh2(CMP_EQ_R0_R1)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "CMP/EQ"
        assert r["rn"] == 1
        assert r["rm"] == 0

    def test_bt(self):
        data = pack_sh2(BT_PLUS_2)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "BT"
        assert r["has_delay"] is True
        # target = BASE + 4 + 2*2 = BASE + 8
        assert r["target"] == BASE + 8

    def test_bf(self):
        data = pack_sh2(BF_PLUS_1)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "BF"
        assert r["has_delay"] is True
        assert r["target"] == BASE + 6

    def test_bra(self):
        data = pack_sh2(BRA_PLUS_3)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "BRA"
        assert r["has_delay"] is True
        assert r["target"] == BASE + 10

    def test_bra_negative(self):
        # BRA -2: disp = 0xFFE -> sign_extend_12 -> -2
        # target = BASE + 4 + (-2)*2 = BASE + 0
        data = pack_sh2(0xAFFE)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "BRA"
        assert r["target"] == BASE + 0

    def test_rts(self):
        data = pack_sh2(RTS)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "RTS"
        assert r["has_delay"] is True

    def test_jsr(self):
        data = pack_sh2(JSR_R4)
        r = sh2_lifter.decode_sh2(data, 0, BASE)
        assert r["mnemonic"] == "JSR"
        assert r["has_delay"] is True
        assert r["rm"] == 4

    def test_out_of_bounds(self):
        result = sh2_lifter.decode_sh2(bytes(1), 0, BASE)
        assert result is None

    def test_address(self):
        data = pack_sh2(MOV_R0_R1, ADD_R2_R3)
        r = sh2_lifter.decode_sh2(data, 2, BASE)
        assert r["address"] == BASE + 2


# ---------------------------------------------------------------------------
# lift_instruction
# ---------------------------------------------------------------------------

class TestLiftInstruction:
    def _decode(self, word):
        return sh2_lifter.decode_sh2(pack_sh2(word), 0, BASE)

    def test_mov(self):
        instr = self._decode(MOV_R0_R1)
        c = sh2_lifter.lift_instruction(instr)
        assert c is not None, "lift_instruction() returned None"
        assert "regs[1]" in c
        assert "regs[0]" in c

    def test_add(self):
        instr = self._decode(ADD_R2_R3)
        c = sh2_lifter.lift_instruction(instr)
        assert "regs[3]" in c
        assert "+" in c

    def test_cmp_eq(self):
        instr = self._decode(CMP_EQ_R0_R1)
        c = sh2_lifter.lift_instruction(instr)
        assert "T" in c
        assert "==" in c

    def test_bt(self):
        instr = self._decode(BT_PLUS_2)
        c = sh2_lifter.lift_instruction(instr)
        assert "if" in c.lower()
        assert "T" in c
        assert "goto" in c

    def test_bra(self):
        instr = self._decode(BRA_PLUS_3)
        c = sh2_lifter.lift_instruction(instr)
        assert "goto" in c

    def test_rts(self):
        instr = self._decode(RTS)
        c = sh2_lifter.lift_instruction(instr)
        assert "PR" in c


# ---------------------------------------------------------------------------
# lift_block -- delay slot handling
# ---------------------------------------------------------------------------

class TestLiftBlock:
    def test_returns_list(self):
        data = pack_sh2(MOV_R0_R1)
        result = sh2_lifter.lift_block(data, BASE)
        assert result is not None, "lift_block() returned None"
        assert isinstance(result, list)

    def test_simple_instruction(self):
        data = pack_sh2(MOV_R0_R1)
        lines = sh2_lifter.lift_block(data, BASE)
        # Should have at least one line of C code
        c_lines = [l for l in lines if "regs" in l]
        assert len(c_lines) >= 1

    def test_delay_slot_before_branch(self):
        """The delay slot instruction must appear BEFORE the branch in output."""
        # BRA target ; ADD R2, R3 (delay slot)
        data = pack_sh2(BRA_PLUS_3, ADD_R2_R3)
        lines = sh2_lifter.lift_block(data, BASE)
        text = "\n".join(lines)

        # Find positions of the ADD and goto in the output
        add_pos = None
        goto_pos = None
        for i, line in enumerate(lines):
            if "regs[3]" in line and "+" in line:
                add_pos = i
            if "goto" in line.lower() and "label" in line.lower():
                goto_pos = i

        assert add_pos is not None, "ADD not found in output"
        assert goto_pos is not None, "goto not found in output"
        assert add_pos < goto_pos, \
            "Delay slot (ADD) must appear BEFORE the branch (goto)"

    def test_rts_delay_slot(self):
        """RTS also has a delay slot."""
        # RTS ; MOV R0,R0 (delay slot)
        data = pack_sh2(RTS, NOP_MOV)
        lines = sh2_lifter.lift_block(data, BASE)
        text = "\n".join(lines)
        assert "PR" in text  # RTS uses PR

    def test_conditional_delay_slot(self):
        """BT/BF delay slots are always executed."""
        # BT target ; ADD R2,R3 (delay slot)
        data = pack_sh2(BT_PLUS_2, ADD_R2_R3)
        lines = sh2_lifter.lift_block(data, BASE)

        add_pos = None
        if_pos = None
        for i, line in enumerate(lines):
            if "regs[3]" in line and "+" in line:
                add_pos = i
            if "if" in line.lower():
                if_pos = i

        assert add_pos is not None, "Delay slot ADD not found"
        assert if_pos is not None, "Conditional branch not found"
        assert add_pos < if_pos, \
            "Delay slot must execute before the conditional branch"

    def test_mixed_block(self):
        """A block with non-branch instructions followed by a branch."""
        # MOV R0,R1 ; CMP/EQ R0,R1 ; BT +2 ; ADD R2,R3 (delay)
        data = pack_sh2(MOV_R0_R1, CMP_EQ_R0_R1, BT_PLUS_2, ADD_R2_R3)
        lines = sh2_lifter.lift_block(data, BASE)
        assert lines is not None
        # Should have output for all 4 instructions
        text = "\n".join(lines)
        assert "regs[1]" in text    # MOV
        assert "T" in text          # CMP/EQ and BT
        assert "regs[3]" in text    # ADD (delay slot)
