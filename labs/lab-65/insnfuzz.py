"""
Lab 65: Instruction Fuzzer

Random operands and register state through both a lifter and an
interpreter, weighted toward the values where flag bugs live.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import random

# Widths in bits -> mask
MASKS = {8: 0xFF, 16: 0xFFFF, 32: 0xFFFFFFFF}


def interesting_values(width):
    """Return the boundary values worth over-sampling for *width* bits.

    These are where flag bugs live: zero, all-ones, the signed boundaries,
    the nibble boundaries, and one either side of each.

    For 8 bits that is:
        0x00, 0x01, 0x0F, 0x10, 0x7F, 0x80, 0x81, 0xFE, 0xFF

    For wider widths, the same shape scaled: 0, 1, the low-nibble boundary
    (0x0F/0x10), the signed boundary (0x7F/0x80 scaled to the width), and the
    top two values.

    Returns:
        A sorted list of ints, no duplicates.
    """
    # TODO: Build the list for the given width using MASKS[width], the signed
    #       boundary (1 << (width - 1)), and the nibble boundary. Deduplicate
    #       and sort.
    pass


def gen_operand(rng, width, edge_bias=0.5):
    """Generate one operand, biased toward interesting values.

    Args:
        rng: a random.Random.
        width: bit width.
        edge_bias: probability of drawing from interesting_values() rather
            than uniformly. 0.0 is pure uniform, 1.0 is edges only.

    Returns:
        An int in [0, MASKS[width]].
    """
    # TODO: With probability edge_bias, choose from interesting_values(width);
    #       otherwise rng.randint over the full range.
    pass


def fuzz_instruction(name, impl_a, impl_b, width=8, trials=1000, seed=0,
                     edge_bias=0.5, arity=2):
    """Run one instruction through two implementations many times.

    Both implementations are callable(*operands) -> dict of results (registers,
    flags -- whatever the instruction produces). They are compared by equality.

    Args:
        name: instruction name, for the report.
        impl_a: reference implementation.
        impl_b: implementation under test.
        width: operand width in bits.
        trials: how many cases to run.
        seed: RNG seed. The same seed must produce the same cases.
        edge_bias: passed to gen_operand.
        arity: how many operands the instruction takes.

    Returns:
        A dict with:
            "name"      - the instruction name
            "trials"    - how many ran (stops early on first failure)
            "failed"    - bool
            "operands"  - the failing operand tuple, or None
            "expected"  - impl_a's result for it, or None
            "actual"    - impl_b's result for it, or None
            "seed"      - the seed, so the run can be replayed
    """
    # TODO: Seed a random.Random. Generate `arity` operands per trial, call
    #       both implementations, compare, and stop at the first mismatch.
    pass


def shrink_case(operands, still_fails, width=8):
    """Reduce a failing operand tuple to a simpler one that still fails.

    Tries, for each operand in turn, replacing it with each interesting value
    (smallest first) and keeping the change if the case still fails. Repeats
    until a full pass makes no change.

    Args:
        operands: the failing tuple.
        still_fails: callable(tuple) -> bool.
        width: operand width.

    Returns:
        A simpler failing tuple. If *still_fails* is False for the input, the
        input is returned unchanged.
    """
    # TODO: Loop until stable. For each position, try each candidate from
    #       interesting_values(width) and keep the first that still fails.
    pass


def format_result(result):
    """Format a fuzz result."""
    if not result["failed"]:
        return (f"{result['name']}: {result['trials']} trials, no divergence "
                f"(seed {result['seed']})")
    ops = ", ".join(f"0x{v:X}" for v in result["operands"])
    return (f"{result['name']}: FAILED after {result['trials']} trials "
            f"(seed {result['seed']})\n"
            f"  operands: {ops}\n"
            f"  expected: {result['expected']}\n"
            f"  actual:   {result['actual']}")
