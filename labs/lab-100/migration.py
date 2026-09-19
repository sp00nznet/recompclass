"""
Lab 100: Migration Ladder

Move functions from the emulator to native code one at a time, keeping the
program runnable at every step, and plot the crossover.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def plan_migration(profile):
    """Decide what order to port functions in.

    Hottest first: porting the function that executes most instructions moves
    the crossover furthest per unit of work.

    Args:
        profile: dict mapping function name -> instructions executed.

    Returns:
        A list of names, sorted by instruction count descending then name
        ascending. The tie-break keeps the plan stable between runs.
    """
    # TODO: Sort the profile.
    pass


def simulate_migration(profile, order):
    """Compute the crossover after each porting step.

    Args:
        profile: name -> instructions executed.
        order: the porting order.

    Returns:
        A list of floats, length len(order) + 1. Index 0 is 0.0 (nothing
        ported); index i is the crossover after porting order[:i].
    """
    # TODO: Accumulate instructions as functions are ported, dividing by the
    #       total each time. Guard a zero total.
    pass


def steps_to_reach(curve, target):
    """How many ports are needed to reach *target* crossover?

    Args:
        curve: output of simulate_migration.
        target: the crossover to reach, 0.0 to 1.0.

    Returns:
        The number of functions that must be ported, or None if the curve
        never reaches the target.
    """
    # TODO: Find the first index whose value is >= target; that index is the
    #       number of ports.
    pass


def verify_runnable(all_functions, ported, emulated):
    """Check the invariant that makes every migration step shippable.

    Every function must be either ported to native code or available in the
    emulator. A function that is neither means the program cannot run.

    Args:
        all_functions: every function the program needs.
        ported: set of names ported to native.
        emulated: set of names the emulator can run.

    Returns:
        A sorted list of names that are neither. Empty means runnable.
    """
    # TODO: Return the names in neither set.
    pass


def format_curve(curve, order):
    """Format a migration curve."""
    lines = ["ported | crossover | function"]
    for i, value in enumerate(curve):
        name = order[i - 1] if i > 0 else "(none)"
        lines.append(f"{i:6d} | {value * 100:8.1f}% | {name}")
    return "\n".join(lines)
