"""
Tests for Lab 87: Whole-ROM Emitter
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import wholerom


PROGRAM = [
    {"addr": 0x0000, "mnemonic": "NOP", "cycles": 4, "kind": "normal", "target": None},
    {"addr": 0x0001, "mnemonic": "ADD", "cycles": 7, "kind": "normal", "target": None},
    {"addr": 0x0002, "mnemonic": "JP 0x0005", "cycles": 12, "kind": "jump", "target": 0x0005},
    {"addr": 0x0003, "mnemonic": "CALL 0x0006", "cycles": 14, "kind": "call", "target": 0x0006},
    {"addr": 0x0004, "mnemonic": "RET", "cycles": 10, "kind": "return", "target": None},
    {"addr": 0x0005, "mnemonic": "NOP", "cycles": 4, "kind": "normal", "target": None},
    {"addr": 0x0006, "mnemonic": "NOP", "cycles": 4, "kind": "normal", "target": None},
]


class TestLabel:
    def test_format(self):
        assert wholerom.emit_label(0x546) == "L_0546"

    def test_uppercase(self):
        assert wholerom.emit_label(0xABC) == "L_0ABC"


class TestEmitInstruction:
    def test_normal_only_cycles(self):
        out = wholerom.emit_instruction(PROGRAM[0])
        assert out is not None, "emit_instruction() returned None"
        assert len(out) == 1
        assert "cycles" in out[0]

    def test_jump_emits_goto(self):
        out = wholerom.emit_instruction(PROGRAM[2])
        assert any("goto L_0005;" in line for line in out)

    def test_call_pushes_next_address(self):
        out = wholerom.emit_instruction(PROGRAM[3])
        joined = "".join(out)
        assert "0x0004" in joined
        assert "goto L_0006;" in joined

    def test_return_is_computed(self):
        out = wholerom.emit_instruction(PROGRAM[4])
        assert any("goto *" in line for line in out)

    def test_indented(self):
        out = wholerom.emit_instruction(PROGRAM[0])
        assert out[0].startswith("    ")


class TestEmitRom:
    def test_is_one_function(self):
        src = wholerom.emit_rom(PROGRAM)
        assert src is not None, "emit_rom() returned None"
        assert src.count("void run_rom") == 1

    def test_label_per_instruction(self):
        src = wholerom.emit_rom(PROGRAM)
        for insn in PROGRAM:
            assert f"L_{insn['addr']:04X}:" in src

    def test_sequential_falls_through(self):
        # Two adjacent normal instructions must have no branch between them.
        src = wholerom.emit_rom(PROGRAM)
        between = src.split("L_0000:")[1].split("L_0001:")[0]
        assert "goto" not in between

    def test_mnemonic_as_comment(self):
        assert "NOP" in wholerom.emit_rom(PROGRAM)


class TestCountGotos:
    def test_counts(self):
        src = wholerom.emit_rom(PROGRAM)
        n = wholerom.count_gotos(src)
        assert n is not None, "count_gotos() returned None"
        assert n == 3      # jump, call, return

    def test_zero(self):
        assert wholerom.count_gotos("no branches here") == 0


class TestReachable:
    def test_targets(self):
        r = wholerom.reachable_labels(PROGRAM)
        assert r is not None, "reachable_labels() returned None"
        assert r == [0x0005, 0x0006]

    def test_fallthrough_not_counted(self):
        assert 0x0001 not in wholerom.reachable_labels(PROGRAM)

    def test_savings(self):
        s = wholerom.label_savings(PROGRAM)
        assert s["total"] == 7
        assert s["targeted"] == 2
        assert s["droppable"] == 5
