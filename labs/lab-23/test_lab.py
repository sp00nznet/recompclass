"""
Tests for Lab 23: CFG Builder (Recursive Descent)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import cfg_builder
from cfg_builder import BasicBlock


# ---------------------------------------------------------------------------
# Test programs
# ---------------------------------------------------------------------------

# Linear: LOAD r0 ; STORE r1 ; RET
LINEAR_PROG = bytes([
    0x02, 0x00,     # 0000: LOAD r0
    0x03, 0x01,     # 0002: STORE r1
    0x08,           # 0004: RET
])

# Branch: LOAD r0 ; BEQ 0007 ; STORE r1 ; RET
BRANCH_PROG = bytes([
    0x02, 0x00,             # 0000: LOAD r0
    0x06, 0x07, 0x00,       # 0002: BEQ 0007
    0x03, 0x01,             # 0005: STORE r1
    0x08,                   # 0007: RET
])

# Jump: NOP ; JMP 0004 ; NOP ; RET
JUMP_PROG = bytes([
    0x01,                   # 0000: NOP
    0x05, 0x04, 0x00,       # 0001: JMP 0004
    0x01,                   # 0004: NOP
    0x08,                   # 0005: RET
])

# Loop: LOAD r0 ; ADD r1 ; BEQ 0006 ; JMP 0000 ; RET
LOOP_PROG = bytes([
    0x02, 0x00,             # 0000: LOAD r0
    0x04, 0x01,             # 0002: ADD r1
    0x06, 0x09, 0x00,       # 0004: BEQ 0009
    0x05, 0x00, 0x00,       # 0007: JMP 0000
    0x08,                   # 000A: RET  (only reachable via BEQ fall... wait)
])


class TestBuildCFGLinear:
    def test_returns_dict(self):
        cfg = cfg_builder.build_cfg(LINEAR_PROG, entry_point=0)
        assert cfg is not None, "build_cfg() returned None"
        assert isinstance(cfg, dict)

    def test_single_block(self):
        cfg = cfg_builder.build_cfg(LINEAR_PROG, entry_point=0)
        # Linear code with RET at end = one basic block
        assert len(cfg) == 1
        assert 0 in cfg

    def test_block_has_three_instructions(self):
        cfg = cfg_builder.build_cfg(LINEAR_PROG, entry_point=0)
        block = cfg[0]
        assert len(block.instructions) == 3

    def test_no_successors(self):
        cfg = cfg_builder.build_cfg(LINEAR_PROG, entry_point=0)
        block = cfg[0]
        assert len(block.successors) == 0


class TestBuildCFGBranch:
    def test_three_blocks(self):
        cfg = cfg_builder.build_cfg(BRANCH_PROG, entry_point=0)
        assert cfg is not None
        # Block at 0x0000 (LOAD + BEQ), block at 0x0005 (STORE), block at 0x0007 (RET)
        assert len(cfg) == 3

    def test_entry_block_successors(self):
        cfg = cfg_builder.build_cfg(BRANCH_PROG, entry_point=0)
        block = cfg[0]
        targets = {addr for addr, _ in block.successors}
        # BEQ has both fall-through (0x0005) and taken (0x0007)
        assert 0x0005 in targets
        assert 0x0007 in targets

    def test_edge_labels(self):
        cfg = cfg_builder.build_cfg(BRANCH_PROG, entry_point=0)
        block = cfg[0]
        labels = {addr: lbl for addr, lbl in block.successors}
        assert labels[0x0005] == "fall"
        assert labels[0x0007] == "taken"


class TestBuildCFGJump:
    def test_two_blocks(self):
        cfg = cfg_builder.build_cfg(JUMP_PROG, entry_point=0)
        assert cfg is not None
        # Block at 0x0000 (NOP + JMP), block at 0x0004 (NOP + RET)
        assert len(cfg) == 2

    def test_jump_no_fallthrough(self):
        cfg = cfg_builder.build_cfg(JUMP_PROG, entry_point=0)
        block = cfg[0]
        labels = [lbl for _, lbl in block.successors]
        # JMP only has "taken", no "fall"
        assert "taken" in labels
        assert "fall" not in labels


class TestCfgToDot:
    def test_returns_string(self):
        cfg = cfg_builder.build_cfg(LINEAR_PROG, entry_point=0)
        dot = cfg_builder.cfg_to_dot(cfg)
        assert dot is not None, "cfg_to_dot() returned None"
        assert isinstance(dot, str)

    def test_contains_digraph(self):
        cfg = cfg_builder.build_cfg(LINEAR_PROG, entry_point=0)
        dot = cfg_builder.cfg_to_dot(cfg)
        assert "digraph" in dot

    def test_contains_edges(self):
        cfg = cfg_builder.build_cfg(BRANCH_PROG, entry_point=0)
        dot = cfg_builder.cfg_to_dot(cfg)
        assert "->" in dot

    def test_contains_block_labels(self):
        cfg = cfg_builder.build_cfg(BRANCH_PROG, entry_point=0)
        dot = cfg_builder.cfg_to_dot(cfg)
        assert "blk_0000" in dot.lower() or "blk_0000" in dot
