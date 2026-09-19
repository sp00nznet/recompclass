"""
Lab 75: Lane Order and Permutes

Lift a big-endian guest's permute to a little-endian host correctly, and
demonstrate the mirrored-constant bug the naive translation produces.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def mirror_index(i, count):
    """Convert a lane index between big-endian and little-endian ordering.

    With `count` lanes, lane 0 at one end corresponds to lane `count - 1` at
    the other. The conversion is its own inverse.

    Raises:
        ValueError: if i is outside [0, count).
    """
    # TODO: Validate and return the mirrored index.
    pass


def permute(vec, control):
    """Apply a permute control vector.

    Args:
        vec: the source lanes.
        control: list of source indices, one per destination lane.

    Returns:
        A new list where result[i] = vec[control[i]].

    Raises:
        IndexError: if any control entry is out of range.
    """
    # TODO: Build the permuted list, validating each index.
    pass


def lift_permute_naive(control):
    """The WRONG translation: copy the guest's control vector unchanged.

    This is what a lifter does when nobody thought about lane order. It is
    correct only when the guest and host agree on lane numbering.

    Returns:
        The control vector, unchanged.
    """
    # TODO: Return control unchanged (a copy, so callers cannot alias it).
    pass


def lift_permute(control, count):
    """The correct translation for a big-endian guest on a little-endian host.

    Both the *position* of each control entry and the *value* it selects are
    expressed in guest lane numbering, so both must be mirrored.

    Args:
        control: the guest's control vector.
        count: the number of lanes.

    Returns:
        A control vector in host lane numbering.
    """
    # TODO: For each host destination lane i, the guest destination is
    #       mirror_index(i, count); look up the guest source there and mirror
    #       it back to host numbering.
    pass


def demonstrate_bug(vec, control):
    """Run both translations and report whether they differ.

    Returns:
        A dict with:
            "naive"   - result of permuting with the naive control
            "correct" - result of permuting with the corrected control
            "differ"  - bool
    """
    # TODO: Apply both and compare.
    pass
