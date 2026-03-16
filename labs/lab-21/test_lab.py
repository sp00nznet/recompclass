"""
Tests for Lab 21: 6502 Instruction Decoder
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import decoder_6502


class TestDecodeInstruction:
    def test_lda_immediate(self):
        data = bytes([0xA9, 0x42])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None, "decode_instruction() returned None"
        assert result["mnemonic"] == "LDA"
        assert result["mode"] == "imm"
        assert result["operand"] == 0x42
        assert result["length"] == 2
        assert result["address"] == 0x8000

    def test_sta_absolute(self):
        data = bytes([0x8D, 0x00, 0x02])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None
        assert result["mnemonic"] == "STA"
        assert result["mode"] == "abs"
        assert result["operand"] == 0x0200
        assert result["length"] == 3

    def test_inx_implied(self):
        data = bytes([0xE8])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None
        assert result["mnemonic"] == "INX"
        assert result["mode"] == "imp"
        assert result["operand"] is None
        assert result["length"] == 1

    def test_asl_accumulator(self):
        data = bytes([0x0A])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None
        assert result["mnemonic"] == "ASL"
        assert result["mode"] == "acc"

    def test_bne_relative(self):
        data = bytes([0xD0, 0xFE])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None
        assert result["mnemonic"] == "BNE"
        assert result["mode"] == "rel"
        assert result["operand"] == 0xFE

    def test_jmp_indirect(self):
        data = bytes([0x6C, 0x00, 0xFF])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None
        assert result["mnemonic"] == "JMP"
        assert result["mode"] == "ind"
        assert result["operand"] == 0xFF00

    def test_lda_indirect_y(self):
        data = bytes([0xB1, 0x30])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None
        assert result["mnemonic"] == "LDA"
        assert result["mode"] == "izy"
        assert result["operand"] == 0x30

    def test_unknown_opcode(self):
        data = bytes([0x02])  # not in table
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is None

    def test_offset_into_data(self):
        data = bytes([0x00, 0x00, 0xA9, 0x10])
        result = decoder_6502.decode_instruction(data, 2, base_address=0x8000)
        assert result is not None
        assert result["mnemonic"] == "LDA"
        assert result["address"] == 0x8002

    def test_raw_bytes(self):
        data = bytes([0x8D, 0x00, 0x02])
        result = decoder_6502.decode_instruction(data, 0, base_address=0x8000)
        assert result is not None
        assert result["raw"] == bytes([0x8D, 0x00, 0x02])


class TestFormatInstruction:
    def _decode(self, bytez, addr=0x8000):
        return decoder_6502.decode_instruction(bytes(bytez), 0, base_address=addr)

    def test_format_immediate(self):
        d = self._decode([0xA9, 0x42])
        s = decoder_6502.format_instruction(d)
        assert s is not None, "format_instruction() returned None"
        assert "#$42" in s.upper()
        assert "LDA" in s

    def test_format_absolute(self):
        d = self._decode([0x8D, 0x00, 0x02])
        s = decoder_6502.format_instruction(d)
        assert "$0200" in s.upper()
        assert "STA" in s

    def test_format_implied(self):
        d = self._decode([0xE8])
        s = decoder_6502.format_instruction(d)
        assert "INX" in s

    def test_format_relative_forward(self):
        d = self._decode([0xD0, 0x04], addr=0x8000)
        s = decoder_6502.format_instruction(d)
        # Target = 0x8000 + 2 + 4 = 0x8006
        assert "$8006" in s.upper()

    def test_format_relative_backward(self):
        d = self._decode([0xD0, 0xFC], addr=0x8010)
        s = decoder_6502.format_instruction(d)
        # Target = 0x8010 + 2 + (-4) = 0x800E
        assert "$800E" in s.upper()

    def test_format_accumulator(self):
        d = self._decode([0x0A])
        s = decoder_6502.format_instruction(d)
        assert "ASL" in s
        assert "A" in s

    def test_format_indirect(self):
        d = self._decode([0x6C, 0x00, 0xFF])
        s = decoder_6502.format_instruction(d)
        assert "($FF00)" in s.upper()

    def test_format_zpx(self):
        d = self._decode([0xB5, 0x10])
        s = decoder_6502.format_instruction(d)
        assert "LDA" in s
        assert "$10" in s.upper()
        assert ",X" in s.upper()

    def test_format_izy(self):
        d = self._decode([0xB1, 0x30])
        s = decoder_6502.format_instruction(d)
        assert "($30),Y" in s.upper()


class TestDisassemble:
    def test_simple_program(self):
        code = bytes([
            0xA9, 0x42,         # LDA #$42
            0x8D, 0x00, 0x02,   # STA $0200
            0xE8,               # INX
            0x60,               # RTS
        ])
        lines = decoder_6502.disassemble(code, base_address=0x8000)
        assert lines is not None, "disassemble() returned None"
        assert len(lines) == 4

    def test_count_limit(self):
        code = bytes([0xEA] * 10)  # 10 NOPs
        lines = decoder_6502.disassemble(code, base_address=0x8000, count=3)
        assert lines is not None
        assert len(lines) == 3

    def test_empty_data(self):
        lines = decoder_6502.disassemble(b"", base_address=0x8000)
        assert lines is not None
        assert len(lines) == 0
