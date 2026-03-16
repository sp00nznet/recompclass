"""
Tests for Lab 27: ARM/Thumb Disassembler
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import arm_disasm


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

# ARM: MOV R0, #0x42 ; MOV R1, #0x10 ; BX LR
ARM_CODE = bytes([
    0x42, 0x00, 0xA0, 0xE3,    # MOV R0, #0x42
    0x10, 0x10, 0xA0, 0xE3,    # MOV R1, #0x10
    0x1E, 0xFF, 0x2F, 0xE1,    # BX LR
])

# Thumb: MOVS R0, #0 ; ADDS R0, #1 ; BX LR
THUMB_CODE = bytes([
    0x00, 0x20,     # MOVS R0, #0
    0x01, 0x30,     # ADDS R0, #1
    0x70, 0x47,     # BX LR
])

BASE = 0x08000000


# ---------------------------------------------------------------------------
# ARM disassembly
# ---------------------------------------------------------------------------

class TestDisasmArm:
    def test_returns_list(self):
        result = arm_disasm.disasm_arm(ARM_CODE, BASE)
        assert result is not None, "disasm_arm() returned None"
        assert isinstance(result, list)

    def test_instruction_count(self):
        result = arm_disasm.disasm_arm(ARM_CODE, BASE)
        assert len(result) == 3

    def test_tuple_structure(self):
        result = arm_disasm.disasm_arm(ARM_CODE, BASE)
        addr, mnem, ops, raw = result[0]
        assert isinstance(addr, int)
        assert isinstance(mnem, str)
        assert isinstance(ops, str)

    def test_first_instruction(self):
        result = arm_disasm.disasm_arm(ARM_CODE, BASE)
        addr, mnem, ops, _ = result[0]
        assert addr == BASE
        assert "mov" in mnem.lower()

    def test_addresses_increment_by_4(self):
        result = arm_disasm.disasm_arm(ARM_CODE, BASE)
        assert result[1][0] == BASE + 4
        assert result[2][0] == BASE + 8

    def test_empty_data(self):
        result = arm_disasm.disasm_arm(b"", BASE)
        assert result is not None
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Thumb disassembly
# ---------------------------------------------------------------------------

class TestDisasmThumb:
    def test_returns_list(self):
        result = arm_disasm.disasm_thumb(THUMB_CODE, BASE)
        assert result is not None, "disasm_thumb() returned None"
        assert isinstance(result, list)

    def test_instruction_count(self):
        result = arm_disasm.disasm_thumb(THUMB_CODE, BASE)
        assert len(result) == 3

    def test_first_instruction(self):
        result = arm_disasm.disasm_thumb(THUMB_CODE, BASE)
        addr, mnem, ops, _ = result[0]
        assert addr == BASE
        assert "mov" in mnem.lower()

    def test_addresses_increment_by_2(self):
        result = arm_disasm.disasm_thumb(THUMB_CODE, BASE)
        assert result[1][0] == BASE + 2


# ---------------------------------------------------------------------------
# Format
# ---------------------------------------------------------------------------

class TestFormatDisasm:
    def test_returns_list(self):
        insns = arm_disasm.disasm_arm(ARM_CODE, BASE)
        result = arm_disasm.format_disasm(insns, "ARM")
        assert result is not None, "format_disasm() returned None"
        assert isinstance(result, list)

    def test_contains_mode_label(self):
        insns = arm_disasm.disasm_arm(ARM_CODE, BASE)
        lines = arm_disasm.format_disasm(insns, "ARM")
        assert "ARM" in lines[0]

    def test_contains_address(self):
        insns = arm_disasm.disasm_arm(ARM_CODE, BASE)
        lines = arm_disasm.format_disasm(insns, "ARM")
        assert "08000000" in lines[0].upper()


# ---------------------------------------------------------------------------
# Mode switch detection
# ---------------------------------------------------------------------------

class TestDetectModeSwitches:
    def test_arm_bx(self):
        insns = arm_disasm.disasm_arm(ARM_CODE, BASE)
        switches = arm_disasm.detect_mode_switches(insns)
        assert switches is not None, "detect_mode_switches() returned None"
        assert len(switches) == 1
        assert switches[0]["address"] == BASE + 8

    def test_thumb_bx(self):
        insns = arm_disasm.disasm_thumb(THUMB_CODE, BASE)
        switches = arm_disasm.detect_mode_switches(insns)
        assert len(switches) == 1

    def test_no_bx(self):
        # ARM code without BX
        code = bytes([
            0x42, 0x00, 0xA0, 0xE3,    # MOV R0, #0x42
            0x10, 0x10, 0xA0, 0xE3,    # MOV R1, #0x10
        ])
        insns = arm_disasm.disasm_arm(code, BASE)
        switches = arm_disasm.detect_mode_switches(insns)
        assert len(switches) == 0


# ---------------------------------------------------------------------------
# Auto disassembly
# ---------------------------------------------------------------------------

class TestDisasmAuto:
    def test_mixed_sections(self):
        sections = [
            {"data": ARM_CODE,   "offset": 0,    "mode": "arm"},
            {"data": THUMB_CODE, "offset": 0x100, "mode": "thumb"},
        ]
        result = arm_disasm.disasm_auto(sections, base_address=BASE)
        assert result is not None, "disasm_auto() returned None"
        assert isinstance(result, list)
        # 3 ARM + 3 Thumb = 6 total lines
        assert len(result) == 6

    def test_mode_labels_present(self):
        sections = [
            {"data": ARM_CODE,   "offset": 0,    "mode": "arm"},
            {"data": THUMB_CODE, "offset": 0x100, "mode": "thumb"},
        ]
        result = arm_disasm.disasm_auto(sections, base_address=BASE)
        has_arm = any("ARM" in line for line in result)
        has_thumb = any("THUMB" in line for line in result)
        assert has_arm
        assert has_thumb
