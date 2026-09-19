"""
Lab 119: Verified Lifting Rules

Prove a lifting rule correct over its entire input space, and find what
a sampled differential test missed.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import itertools
import random


def exhaustive_verify(reference, candidate, width=8, arity=2, flag_states=(False,)):
    """Check *candidate* against *reference* over the entire input space.

    Args:
        reference: known-good callable(*operands, flag) -> result.
        candidate: the implementation under test, same signature.
        width: operand width in bits.
        arity: number of operands.
        flag_states: incoming flag values to try.

    Returns:
        A dict with:
            "verified"   - bool, True only if every input matched
            "checked"    - how many input combinations were tested
            "first_bad"  - the first failing (operands..., flag) tuple, or None
            "expected" / "actual" - values at that input, or None

    Stops at the first failure: once a rule is wrong, it is wrong.
    """
    # TODO: itertools.product over range(1 << width) repeated `arity` times,
    #       crossed with flag_states. Compare, counting as you go.
    pass


def sampled_verify(reference, candidate, width=8, arity=2, trials=10000,
                   seed=0, flag_states=(False,)):
    """Check a random sample -- the usual approach.

    Returns:
        The same shape as exhaustive_verify, plus "seed".
    """
    # TODO: Seed a random.Random, draw `trials` random input tuples, compare.
    pass


def compare_approaches(reference, candidate, width=8, arity=2, trials=10000,
                       seed=0):
    """Run both and report what sampling missed.

    Returns:
        A dict with:
            "exhaustive"  - the exhaustive result
            "sampled"     - the sampled result
            "missed"      - True if sampling passed while exhaustive failed
            "space_size"  - total inputs in the space
            "sampled_fraction" - trials / space_size, capped at 1.0
    """
    # TODO: Run both, compare their verdicts, and compute the coverage.
    pass
