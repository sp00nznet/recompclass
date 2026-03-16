"""
Tests for Lab 39: PPC VMX128 Lifter
"""

import pytest
import vmx128_lifter as lft


# ---------------------------------------------------------------------------
# Individual lifters
# ---------------------------------------------------------------------------

class TestLiftVaddps:
    def test_basic(self):
        insn = {"op": "vaddps", "vD": 10, "vA": 1, "vB": 2}
        result = lft.lift_vaddps(insn)
        assert result == "vr[10] = _mm_add_ps(vr[1], vr[2]);"

    def test_high_regs(self):
        insn = {"op": "vaddps", "vD": 127, "vA": 100, "vB": 50}
        result = lft.lift_vaddps(insn)
        assert "vr[127]" in result
        assert "vr[100]" in result
        assert "vr[50]" in result


class TestLiftVmulps:
    def test_basic(self):
        insn = {"op": "vmulps", "vD": 11, "vA": 3, "vB": 4}
        result = lft.lift_vmulps(insn)
        assert result == "vr[11] = _mm_mul_ps(vr[3], vr[4]);"


class TestLiftVdot3:
    def test_basic(self):
        insn = {"op": "vdot3", "vD": 5, "vA": 3, "vB": 4}
        result = lft.lift_vdot3(insn)
        assert result == "vr[5] = vdot3_sse(vr[3], vr[4]);"


class TestLiftVperm:
    def test_basic(self):
        insn = {"op": "vperm", "vD": 6, "vA": 1, "vB": 2, "vC": 3}
        result = lft.lift_vperm(insn)
        assert result == "vr[6] = vperm_sse(vr[1], vr[2], vr[3]);"


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

class TestLiftInstruction:
    def test_vaddps(self):
        insn = {"op": "vaddps", "vD": 0, "vA": 1, "vB": 2}
        result = lft.lift_instruction(insn)
        assert "_mm_add_ps" in result

    def test_unknown_opcode(self):
        with pytest.raises(ValueError, match="Unknown opcode"):
            lft.lift_instruction({"op": "vfoo", "vD": 0, "vA": 0, "vB": 0})


# ---------------------------------------------------------------------------
# Block lifting
# ---------------------------------------------------------------------------

class TestLiftBlock:
    def test_empty(self):
        assert lft.lift_block([]) == []

    def test_multiple(self):
        insns = [
            {"op": "vaddps", "vD": 10, "vA": 1, "vB": 2},
            {"op": "vmulps", "vD": 11, "vA": 3, "vB": 4},
        ]
        stmts = lft.lift_block(insns)
        assert len(stmts) == 2
        assert "_mm_add_ps" in stmts[0]
        assert "_mm_mul_ps" in stmts[1]


# ---------------------------------------------------------------------------
# Function emission
# ---------------------------------------------------------------------------

class TestEmitFunction:
    def test_structure(self):
        insns = [
            {"op": "vaddps", "vD": 10, "vA": 1, "vB": 2},
        ]
        src = lft.emit_function("test_func", insns)
        assert "void test_func(__m128 vr[128])" in src
        assert "{" in src
        assert "}" in src
        assert "    vr[10] = _mm_add_ps(vr[1], vr[2]);" in src

    def test_empty_body(self):
        src = lft.emit_function("empty_func", [])
        assert "void empty_func" in src
        assert "{" in src
        assert "}" in src


# ---------------------------------------------------------------------------
# Simulation (verify the math is correct)
# ---------------------------------------------------------------------------

class TestSimulation:
    def test_vaddps(self):
        a = (1.0, 2.0, 3.0, 4.0)
        b = (5.0, 6.0, 7.0, 8.0)
        result = lft.sim_vaddps(a, b)
        assert result == (6.0, 8.0, 10.0, 12.0)

    def test_vmulps(self):
        a = (2.0, 3.0, 4.0, 5.0)
        b = (10.0, 10.0, 10.0, 10.0)
        result = lft.sim_vmulps(a, b)
        assert result == (20.0, 30.0, 40.0, 50.0)

    def test_vdot3(self):
        a = (1.0, 2.0, 3.0, 999.0)
        b = (4.0, 5.0, 6.0, 999.0)
        result = lft.sim_vdot3(a, b)
        # dot3 = 1*4 + 2*5 + 3*6 = 32
        assert result == (32.0, 32.0, 32.0, 32.0)

    def test_vdot3_orthogonal(self):
        a = (1.0, 0.0, 0.0, 0.0)
        b = (0.0, 1.0, 0.0, 0.0)
        result = lft.sim_vdot3(a, b)
        assert result == (0.0, 0.0, 0.0, 0.0)

    def test_vperm_identity(self):
        a = (10.0, 20.0, 30.0, 40.0)
        b = (50.0, 60.0, 70.0, 80.0)
        ctrl = (0, 1, 2, 3)  # select all from a
        result = lft.sim_vperm(a, b, ctrl)
        assert result == (10.0, 20.0, 30.0, 40.0)

    def test_vperm_swap(self):
        a = (10.0, 20.0, 30.0, 40.0)
        b = (50.0, 60.0, 70.0, 80.0)
        ctrl = (4, 5, 6, 7)  # select all from b
        result = lft.sim_vperm(a, b, ctrl)
        assert result == (50.0, 60.0, 70.0, 80.0)

    def test_vperm_mix(self):
        a = (10.0, 20.0, 30.0, 40.0)
        b = (50.0, 60.0, 70.0, 80.0)
        ctrl = (0, 4, 1, 5)  # interleave
        result = lft.sim_vperm(a, b, ctrl)
        assert result == (10.0, 50.0, 20.0, 60.0)
