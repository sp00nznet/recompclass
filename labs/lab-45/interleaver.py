"""
Lab 45: Dual-CPU Interleaver

Cycle-approximate interleaving of two simulated CPU instruction streams.
"""


# ---------------------------------------------------------------------------
# CPU state
# ---------------------------------------------------------------------------

class CpuState:
    """Represents one CPU's execution state.

    Attributes
    ----------
    cpu_id : str
        Identifier (e.g. "A" or "B").
    instructions : list of dict
        Each dict has "name" (str) and "cycles" (int).
    pc : int
        Program counter (index into instructions).
    cycles_used : int
        Cycles consumed in the current slice.
    total_cycles : int
        Total cycles consumed across all slices.
    finished : bool
        True when all instructions have been executed.
    """

    def __init__(self, cpu_id, instructions):
        self.cpu_id = cpu_id
        self.instructions = instructions
        self.pc = 0
        self.cycles_used = 0
        self.total_cycles = 0
        self.finished = False

    def current_insn(self):
        """Return the current instruction dict, or None if finished."""
        if self.pc >= len(self.instructions):
            self.finished = True
            return None
        return self.instructions[self.pc]

    def is_at_sync(self):
        """Return True if the current instruction is a SYNC point."""
        insn = self.current_insn()
        return insn is not None and insn["name"] == "SYNC"


# ---------------------------------------------------------------------------
# Interleaver functions -- complete the TODOs
# ---------------------------------------------------------------------------

def run_slice(cpu, budget):
    """Run instructions on *cpu* until the cycle budget is exhausted,
    a SYNC is hit, or the instruction stream ends.

    Parameters
    ----------
    cpu : CpuState
        The CPU to execute on.
    budget : int
        Maximum cycles to execute in this slice.

    Returns
    -------
    list of tuple
        Executed instructions as (cpu_id, insn_name, cycle_timestamp).
        The cycle_timestamp is the cpu.total_cycles value *after*
        the instruction finishes.

    Rules:
    - Before executing an instruction, check if adding its cycle cost
      would exceed the budget.  If so, stop (do not execute it).
    - If the instruction is a SYNC, add it to the trace (with its
      current total_cycles timestamp), advance pc past it, and stop.
    - Otherwise, execute the instruction: advance pc, add cycles to
      cycles_used and total_cycles.
    """
    # TODO: implement the slice execution loop
    pass


def interleave(stream_a, stream_b, budget_a=10, budget_b=10):
    """Interleave two instruction streams with cycle budgets.

    Parameters
    ----------
    stream_a : list of dict
        Instructions for CPU A.
    stream_b : list of dict
        Instructions for CPU B.
    budget_a : int
        Cycle budget per slice for CPU A.
    budget_b : int
        Cycle budget per slice for CPU B.

    Returns
    -------
    list of tuple
        Complete execution trace as (cpu_id, insn_name, cycle_timestamp).

    Algorithm:
    1. Create CpuState for each CPU.
    2. While at least one CPU is not finished:
       a. Reset cpu_a.cycles_used to 0.
       b. Run a slice on CPU A with budget_a.
       c. Reset cpu_b.cycles_used to 0.
       d. Run a slice on CPU B with budget_b.
       e. Append results to the trace.
    3. Return the complete trace.
    """
    # TODO: implement the interleaving loop
    pass


def format_trace(trace):
    """Format an execution trace as a human-readable string.

    Parameters
    ----------
    trace : list of tuple
        (cpu_id, insn_name, cycle_timestamp)

    Returns
    -------
    str
        Multi-line string with one line per instruction.
    """
    lines = []
    for cpu_id, name, ts in trace:
        lines.append(f"[{cpu_id}] @{ts:4d}  {name}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    stream_a = [
        {"name": "mov r0, #1",  "cycles": 1},
        {"name": "mov r1, #2",  "cycles": 1},
        {"name": "add r0, r1",  "cycles": 1},
        {"name": "SYNC",        "cycles": 0},
        {"name": "mul r2, r0",  "cycles": 3},
        {"name": "str r2, [sp]","cycles": 2},
    ]

    stream_b = [
        {"name": "ldr r0, [x]", "cycles": 2},
        {"name": "ldr r1, [y]", "cycles": 2},
        {"name": "SYNC",        "cycles": 0},
        {"name": "add r0, r1",  "cycles": 1},
        {"name": "str r0, [z]", "cycles": 2},
    ]

    trace = interleave(stream_a, stream_b, budget_a=5, budget_b=5)
    print(format_trace(trace))
