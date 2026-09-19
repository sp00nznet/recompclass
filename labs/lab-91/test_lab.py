"""
Tests for Lab 91: Stack to Locals
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import stacklocals


def ins(pc, op, pops=0, pushes=0, target=None):
    return {"pc": pc, "op": op, "pops": pops, "pushes": pushes, "target": target}


STRAIGHT = [
    ins(0, "push", pushes=1),
    ins(1, "push", pushes=1),
    ins(2, "add", pops=2, pushes=1),
    ins(3, "pop", pops=1),
    ins(4, "return"),
]

BRANCHING = [
    ins(0, "push", pushes=1),
    ins(1, "branch_if", pops=1, target=3),
    ins(2, "branch", target=3),
    ins(3, "return"),
]

UNBALANCED = [
    ins(0, "push", pushes=1),
    ins(1, "branch_if", pops=1, target=3),
    ins(2, "push", pushes=1),      # leaves depth 1 at pc 3
    ins(3, "return"),
]

UNDERFLOW = [
    ins(0, "pop", pops=1),
    ins(1, "return"),
]


class TestComputeDepths:
    def test_straight_line(self):
        d = stacklocals.compute_depths(STRAIGHT)
        assert d is not None, "compute_depths() returned None"
        assert d[0] == 0 and d[1] == 1 and d[2] == 2 and d[3] == 1 and d[4] == 0

    def test_branches_converge(self):
        d = stacklocals.compute_depths(BRANCHING)
        assert d[3] == 0

    def test_conflict_raises(self):
        import pytest
        with pytest.raises(stacklocals.StackError):
            stacklocals.compute_depths(UNBALANCED)

    def test_unreachable_absent(self):
        prog = [ins(0, "branch", target=2), ins(1, "push", pushes=1), ins(2, "return")]
        d = stacklocals.compute_depths(prog)
        assert 1 not in d


class TestVerifyBalance:
    def test_clean(self):
        p = stacklocals.verify_balance(STRAIGHT)
        assert p is not None, "verify_balance() returned None"
        assert p == []

    def test_reports_conflict_without_raising(self):
        p = stacklocals.verify_balance(UNBALANCED)
        assert len(p) >= 1

    def test_detects_underflow(self):
        p = stacklocals.verify_balance(UNDERFLOW)
        assert any("negative" in x.lower() or "underflow" in x.lower() for x in p)

    def test_return_not_at_zero(self):
        prog = [ins(0, "push", pushes=1), ins(1, "return")]
        p = stacklocals.verify_balance(prog)
        assert any("return" in x.lower() for x in p)


class TestMaxDepth:
    def test_value(self):
        assert stacklocals.max_depth(stacklocals.compute_depths(STRAIGHT)) == 2

    def test_empty(self):
        assert stacklocals.max_depth({}) == 0


class TestEmit:
    def test_declares_locals(self):
        d = stacklocals.compute_depths(STRAIGHT)
        lines = stacklocals.emit(STRAIGHT, d)
        assert lines is not None, "emit() returned None"
        assert any("s[" in line and ";" in line for line in lines[:1])

    def test_no_runtime_stack(self):
        d = stacklocals.compute_depths(STRAIGHT)
        joined = chr(10).join(stacklocals.emit(STRAIGHT, d))
        for marker in ("sp++", "sp--", "stack[", "->sp"):
            assert marker not in joined,                 f"{marker} means a runtime stack survived"

    def test_assigns_by_depth(self):
        d = stacklocals.compute_depths(STRAIGHT)
        joined = "\n".join(stacklocals.emit(STRAIGHT, d))
        assert "s[0] =" in joined and "s[1] =" in joined

    def test_comments_carry_pc(self):
        d = stacklocals.compute_depths(STRAIGHT)
        joined = "\n".join(stacklocals.emit(STRAIGHT, d))
        assert "2:" in joined
