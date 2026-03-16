"""
Tests for Lab 45: Dual-CPU Interleaver
"""

from interleaver import CpuState, run_slice, interleave


# ---------------------------------------------------------------------------
# CpuState basics
# ---------------------------------------------------------------------------

class TestCpuState:
    def test_initial_state(self):
        cpu = CpuState("A", [{"name": "nop", "cycles": 1}])
        assert cpu.pc == 0
        assert cpu.finished is False

    def test_current_insn(self):
        insns = [{"name": "add", "cycles": 2}]
        cpu = CpuState("A", insns)
        assert cpu.current_insn() == {"name": "add", "cycles": 2}

    def test_finished_when_empty(self):
        cpu = CpuState("A", [])
        assert cpu.current_insn() is None
        assert cpu.finished is True

    def test_sync_detection(self):
        cpu = CpuState("A", [{"name": "SYNC", "cycles": 0}])
        assert cpu.is_at_sync() is True

    def test_not_sync(self):
        cpu = CpuState("A", [{"name": "nop", "cycles": 1}])
        assert cpu.is_at_sync() is False


# ---------------------------------------------------------------------------
# run_slice
# ---------------------------------------------------------------------------

class TestRunSlice:
    def test_simple_slice(self):
        insns = [
            {"name": "i0", "cycles": 1},
            {"name": "i1", "cycles": 1},
            {"name": "i2", "cycles": 1},
        ]
        cpu = CpuState("A", insns)
        trace = run_slice(cpu, budget=3)
        assert len(trace) == 3
        assert trace[0] == ("A", "i0", 1)
        assert trace[1] == ("A", "i1", 2)
        assert trace[2] == ("A", "i2", 3)

    def test_budget_exhaustion(self):
        insns = [
            {"name": "i0", "cycles": 3},
            {"name": "i1", "cycles": 3},
            {"name": "i2", "cycles": 3},
        ]
        cpu = CpuState("A", insns)
        trace = run_slice(cpu, budget=5)
        # Only first instruction fits (3 cycles), second doesn't (3+3=6 > 5)
        # Wait -- 3 <= 5 so first fits, then 3+3=6 > 5 so second doesn't
        assert len(trace) == 1
        assert cpu.pc == 1

    def test_stops_at_sync(self):
        insns = [
            {"name": "i0", "cycles": 1},
            {"name": "SYNC", "cycles": 0},
            {"name": "i1", "cycles": 1},
        ]
        cpu = CpuState("A", insns)
        trace = run_slice(cpu, budget=10)
        # Should execute i0, then hit SYNC (add it to trace and stop)
        assert len(trace) == 2
        assert trace[1][1] == "SYNC"
        assert cpu.pc == 2  # past the SYNC

    def test_empty_stream(self):
        cpu = CpuState("A", [])
        trace = run_slice(cpu, budget=10)
        assert trace == []
        assert cpu.finished is True

    def test_multi_cycle_instruction(self):
        insns = [
            {"name": "mul", "cycles": 4},
            {"name": "add", "cycles": 1},
        ]
        cpu = CpuState("A", insns)
        trace = run_slice(cpu, budget=10)
        assert len(trace) == 2
        assert trace[0] == ("A", "mul", 4)
        assert trace[1] == ("A", "add", 5)

    def test_preserves_total_cycles_across_slices(self):
        insns = [
            {"name": "i0", "cycles": 3},
            {"name": "i1", "cycles": 3},
            {"name": "i2", "cycles": 3},
        ]
        cpu = CpuState("A", insns)

        trace1 = run_slice(cpu, budget=5)
        assert len(trace1) == 1
        assert cpu.total_cycles == 3

        cpu.cycles_used = 0  # reset for next slice
        trace2 = run_slice(cpu, budget=5)
        assert len(trace2) == 1
        assert cpu.total_cycles == 6
        # Timestamp should be based on total_cycles
        assert trace2[0][2] == 6


# ---------------------------------------------------------------------------
# interleave
# ---------------------------------------------------------------------------

class TestInterleave:
    def test_simple_alternation(self):
        a = [{"name": "a0", "cycles": 1}, {"name": "a1", "cycles": 1}]
        b = [{"name": "b0", "cycles": 1}, {"name": "b1", "cycles": 1}]
        trace = interleave(a, b, budget_a=1, budget_b=1)
        names = [t[1] for t in trace]
        # With budget=1 each, should alternate: a0, b0, a1, b1
        assert names == ["a0", "b0", "a1", "b1"]

    def test_unequal_lengths(self):
        a = [{"name": "a0", "cycles": 1}]
        b = [{"name": "b0", "cycles": 1}, {"name": "b1", "cycles": 1},
             {"name": "b2", "cycles": 1}]
        trace = interleave(a, b, budget_a=10, budget_b=10)
        names = [t[1] for t in trace]
        assert "a0" in names
        assert "b0" in names
        assert "b1" in names
        assert "b2" in names

    def test_sync_alignment(self):
        a = [
            {"name": "a0", "cycles": 1},
            {"name": "SYNC", "cycles": 0},
            {"name": "a1", "cycles": 1},
        ]
        b = [
            {"name": "b0", "cycles": 1},
            {"name": "b1", "cycles": 1},
            {"name": "SYNC", "cycles": 0},
            {"name": "b2", "cycles": 1},
        ]
        trace = interleave(a, b, budget_a=10, budget_b=10)
        names = [t[1] for t in trace]
        # A runs a0 then SYNC; B runs b0, b1 then SYNC; then a1, b2
        assert "SYNC" in names

    def test_both_empty(self):
        trace = interleave([], [], budget_a=5, budget_b=5)
        assert trace == []

    def test_one_empty(self):
        a = [{"name": "a0", "cycles": 1}]
        trace = interleave(a, [], budget_a=5, budget_b=5)
        assert len(trace) == 1
        assert trace[0][1] == "a0"

    def test_large_budget(self):
        a = [{"name": f"a{i}", "cycles": 1} for i in range(5)]
        b = [{"name": f"b{i}", "cycles": 1} for i in range(5)]
        trace = interleave(a, b, budget_a=100, budget_b=100)
        # All of A should run first, then all of B (budget large enough)
        names = [t[1] for t in trace]
        a_names = [n for n in names if n.startswith("a")]
        b_names = [n for n in names if n.startswith("b")]
        assert len(a_names) == 5
        assert len(b_names) == 5

    def test_cpu_ids_correct(self):
        a = [{"name": "a0", "cycles": 1}]
        b = [{"name": "b0", "cycles": 1}]
        trace = interleave(a, b, budget_a=10, budget_b=10)
        for cpu_id, name, _ in trace:
            if name.startswith("a"):
                assert cpu_id == "A"
            elif name.startswith("b"):
                assert cpu_id == "B"
