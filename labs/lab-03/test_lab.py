"""
Tests for Lab 3: Multi-Architecture Disassembly
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from labs.lib.disasm_helpers import disassemble
import multi_disasm


class TestDisassembly:
    def test_x86_32_decodes(self):
        instructions = disassemble(multi_disasm.X86_32_BYTES, "x86-32")
        assert len(instructions) > 0, "x86-32 sample should decode to at least one instruction"
        # First instruction should be 'push'
        _, mnemonic, _, _ = instructions[0]
        assert mnemonic == "push"

    def test_mips32_decodes(self):
        instructions = disassemble(multi_disasm.MIPS32_BYTES, "mips32")
        assert len(instructions) > 0, "MIPS32 sample should decode"
        _, mnemonic, _, _ = instructions[0]
        assert mnemonic == "addiu"

    def test_ppc32_decodes(self):
        instructions = disassemble(multi_disasm.PPC32_BYTES, "ppc32")
        assert len(instructions) > 0, "PPC32 sample should decode"

    def test_arm32_decodes(self):
        instructions = disassemble(multi_disasm.ARM32_BYTES, "arm32")
        assert len(instructions) > 0, "ARM32 sample should decode"


class TestDecodeRatio:
    def test_native_ratio_high(self):
        ratio = multi_disasm.decode_ratio(multi_disasm.X86_32_BYTES, "x86-32")
        assert ratio > 0.8, f"x86-32 bytes should have high decode ratio for x86-32, got {ratio}"

    def test_empty_data(self):
        ratio = multi_disasm.decode_ratio(b"", "x86-32")
        assert ratio == 0.0


class TestDetectArchitecture:
    def test_detect_returns_tuple(self):
        result = multi_disasm.detect_architecture(multi_disasm.X86_32_BYTES)
        assert isinstance(result, tuple) and len(result) == 2, \
            "detect_architecture should return (arch_name, confidence)"

    def test_detect_x86(self):
        arch, confidence = multi_disasm.detect_architecture(multi_disasm.X86_32_BYTES)
        # Once implemented, this should detect x86-32
        if arch != "unknown":
            assert arch == "x86-32", f"Expected x86-32, got {arch}"
            assert confidence > 0.5
