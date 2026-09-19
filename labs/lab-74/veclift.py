"""
Lab 74: Vector Lifter With a Reference

Lift a guest vector ISA to host intrinsics, with scalar reference
implementations, and differentially test them at the boundaries.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import math


def saturate(value, width=8, signed=False):
    """Clamp *value* into the range representable in *width* bits.

    Saturating arithmetic clamps at the boundary rather than wrapping. The RSP
    and MMI both do this, and a lifter that wraps produces plausible garbage.

    Args:
        value: the unclamped integer.
        width: bit width.
        signed: signed range if True.

    Returns:
        The clamped value.
    """
    # TODO: Compute the range for (width, signed) and clamp.
    pass


def vadd_sat(a, b, width=8, signed=False):
    """Elementwise saturating add of two equal-length vectors.

    Raises:
        ValueError: if the lengths differ. A silent zip() would truncate,
            which is the kind of quiet wrongness this whole unit is about.
    """
    # TODO: Validate lengths, then saturate each elementwise sum.
    pass


def flush_denormals(vec, enabled=True):
    """Model the guest's flush-to-zero mode.

    Many consoles flush denormals to zero in hardware; your host may not, and
    the difference is both a slowdown and a numeric difference.

    Args:
        vec: list of floats.
        enabled: whether FTZ is on.

    Returns:
        A new list, with denormals replaced by 0.0 (preserving sign) when
        enabled. Zero, infinity and NaN pass through untouched.
    """
    # TODO: A float is denormal when it is non-zero, finite, and its magnitude
    #       is below sys.float_info.min. Preserve the sign of the zero.
    pass


def vmin(a, b, nan_wins=False):
    """Elementwise minimum with an explicit NaN policy.

    Args:
        a, b: equal-length lists of floats.
        nan_wins: if True, a NaN operand propagates. If False, the non-NaN
            operand is chosen (the common hardware behaviour).

    Returns:
        A new list.

    Raises:
        ValueError: on a length mismatch.
    """
    # TODO: Handle the NaN cases explicitly before comparing. math.isnan().
    pass


def differential(op_a, op_b, cases):
    """Compare two implementations over a list of argument tuples.

    Comparison treats NaN as equal to NaN -- otherwise every case containing a
    NaN reports a spurious divergence and the real ones are lost in the noise.

    Args:
        op_a: reference callable.
        op_b: callable under test.
        cases: list of argument tuples.

    Returns:
        A dict with "total", "diverged" (count), and "failures" (list of dicts
        with "case", "expected" and "actual").
    """
    # TODO: Run both over each case, compare with NaN-aware equality, collect.
    pass


def interesting_floats():
    """Float values worth testing: zeros, denormals, infinities, NaN."""
    import sys
    tiny = sys.float_info.min
    return [0.0, -0.0, tiny, -tiny, tiny / 2, -tiny / 2,
            1.0, -1.0, float("inf"), float("-inf"), float("nan")]
