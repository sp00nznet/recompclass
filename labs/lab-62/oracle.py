"""
Lab 62: Interpreter Oracle

Run a lifter and an interpreter over the same instruction stream and
report the first divergence with full state.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


FIELDS = ("pc", "a", "b", "x", "y", "sp", "flags")


class State:
    """A register snapshot, comparable field by field."""

    def __init__(self, **kwargs):
        for f in FIELDS:
            setattr(self, f, kwargs.get(f, 0))

    def as_dict(self):
        return {f: getattr(self, f) for f in FIELDS}

    def __eq__(self, other):
        return isinstance(other, State) and self.as_dict() == other.as_dict()

    def __repr__(self):
        return "State(" + ", ".join(
            f"{f}=0x{getattr(self, f):X}" for f in FIELDS) + ")"


def diff_states(a, b):
    """Return the names of fields that differ between two states.

    Args:
        a, b: State objects.

    Returns:
        A list of field names, in FIELDS order. Empty if identical.
    """
    # TODO: Compare each field in FIELDS and collect the names that differ.
    pass


def run_differential(program, impl_a, impl_b, limit=100000):
    """Step two implementations over *program* until they disagree.

    Each implementation is a callable(program, step_index, state) -> State,
    returning the state after executing one instruction. Both start from a
    zeroed State.

    Args:
        program: the instruction stream (opaque -- passed to both).
        impl_a: the reference (the oracle).
        impl_b: the implementation under test.
        limit: maximum steps before giving up.

    Returns:
        A dict with:
            "diverged"  - bool
            "step"      - the 0-based step at which they differ, or None
            "expected"  - impl_a's State at that step, or None
            "actual"    - impl_b's State at that step, or None
            "fields"    - list of differing field names, or []
            "steps_run" - how many steps completed

    An implementation raising StopIteration means the program ended; that is
    not a divergence, and the run stops cleanly.
    """
    # TODO: Loop up to `limit`. Advance both from their own previous state
    #       (they must not share one). Catch StopIteration from either to end
    #       the run. Compare with diff_states after each step.
    pass


def format_divergence(result):
    """Format a run_differential result as a report."""
    if not result["diverged"]:
        return (f"No divergence in {result['steps_run']} step(s).\n"
                f"Note: a clean run proves the two agree, not that either is "
                f"correct -- see Module 38 section 6.")

    lines = [f"Diverged at step {result['step']} after "
             f"{result['steps_run']} step(s):"]
    for f in result["fields"]:
        exp = getattr(result["expected"], f)
        act = getattr(result["actual"], f)
        lines.append(f"  {f:6s} expected 0x{exp:X}, got 0x{act:X}")
    return "\n".join(lines)
