"""
Lab 68: Frame Driver

A cycle-counted hook that advances a frame, so a loop which assumed an
interrupt was running underneath it no longer completes instantly.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class CycleClock:
    """Counts guest cycles and fires a frame callback at a fixed budget.

    Attributes:
        cycles_per_frame: how many guest cycles make one frame.
        cycles: total cycles counted.
        frames: how many frames have fired.
    """

    def __init__(self, cycles_per_frame, on_frame=None):
        self.cycles_per_frame = cycles_per_frame
        self.on_frame = on_frame
        self.cycles = 0
        self.frames = 0
        self._budget = 0

    def tick(self, cycles):
        """Advance the clock by *cycles*, firing frames as the budget is crossed.

        A single tick large enough to cross several frame boundaries must fire
        the callback once per boundary -- a slow instruction does not get to
        skip frames.

        Args:
            cycles: guest cycles consumed.

        Returns:
            How many frames fired during this tick.
        """
        # TODO: Add to self.cycles and self._budget. While _budget is at least
        #       cycles_per_frame, subtract one frame's worth, bump self.frames,
        #       and call self.on_frame if set. Return the number fired.
        pass


def run_loop(iterations, cycles_per_iteration, clock, body=None):
    """Run a guest loop with the clock ticking on every iteration.

    This is the hook point: the loop body may do nothing observable, but the
    clock still advances, so frames still fire.

    Args:
        iterations: how many times the loop runs.
        cycles_per_iteration: guest cycles each iteration costs.
        clock: a CycleClock.
        body: optional callable(i) run each iteration.

    Returns:
        A dict with "iterations" and "frames" (fired during this loop).
    """
    # TODO: Loop, calling body(i) if given, then clock.tick(...), summing the
    #       frames that fired.
    pass


def detect_impossible_speed(expected_cycles, actual_cycles, tolerance=0.5):
    """Flag work that completed far faster than the guest's own timing allows.

    This is the Module 40 signature: a loop that should take a frame consumed
    almost no guest cycles, because nothing was advancing time.

    Args:
        expected_cycles: what the operation should have cost.
        actual_cycles: what it actually consumed.
        tolerance: actual below expected * tolerance is suspicious.

    Returns:
        None if the timing is plausible, otherwise a detail string naming both
        numbers and the ratio.

    An expected_cycles of 0 cannot be too fast, and returns None.
    """
    # TODO: Guard against expected_cycles == 0, compute the ratio, and return
    #       a detail string when it is below tolerance.
    pass


def format_report(clock, loop_result):
    """Format a frame-driver report."""
    return (f"iterations: {loop_result['iterations']}\n"
            f"cycles:     {clock.cycles}\n"
            f"frames:     {clock.frames}\n"
            f"cycles/frame budget: {clock.cycles_per_frame}")
