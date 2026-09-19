"""
Lab 66: Divergence Minimiser

Shrink a long failing input to a minimal reproducer by truncation and
backward bisection.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def truncate(inputs, index):
    """Return inputs up to and including *index*.

    Args:
        inputs: the sequence.
        index: 0-based index of the failing step.

    Returns:
        A new list. An index beyond the end returns the whole sequence; a
        negative index returns an empty list.
    """
    # TODO: Slice the list. Clamp index into range first.
    pass


def shrink_prefix(inputs, still_fails):
    """Remove as much of the leading input as possible.

    Binary search for the largest prefix that can be dropped while the
    remainder still fails.

    Args:
        inputs: the sequence (already truncated).
        still_fails: callable(sequence) -> bool.

    Returns:
        The shortest suffix found that still fails. If dropping nothing is the
        only option, returns the input unchanged.
    """
    # TODO: Binary search over how many leading elements to drop. Keep the
    #       largest drop that still fails.
    pass


def shrink_elements(inputs, still_fails):
    """Remove individual inputs that are not needed.

    Walks from the end to the start, trying to delete each element and keeping
    the deletion when the sequence still fails. Iterating backwards keeps the
    indices of the not-yet-visited elements stable.

    Returns:
        A list with the unnecessary elements removed.
    """
    # TODO: Copy the list, walk indices in reverse, try each deletion.
    pass


def minimise(inputs, still_fails, failure_index=None):
    """Run the whole minimisation procedure.

    Order: truncate (if a failure index is given), then shrink the prefix,
    then shrink individual elements.

    Returns:
        A dict with:
            "minimal"  - the reduced sequence
            "original" - the original length
            "final"    - the reduced length
            "ratio"    - final / original, 0.0 if original was empty
            "log"      - list of (stage_name, length_after) tuples

    Raises:
        ValueError: if the input does not fail to begin with, or if any stage
            produces a sequence that no longer fails. A minimiser that loses
            the bug has produced a different one.
    """
    # TODO: Validate that still_fails(inputs) is True up front, run the three
    #       stages recording the length after each, and assert the invariant
    #       after every stage.
    pass


def format_result(result):
    """Format a minimisation result."""
    lines = [f"minimised {result['original']} -> {result['final']} "
             f"({result['ratio'] * 100:.1f}% of original)"]
    for stage, length in result["log"]:
        lines.append(f"  after {stage:16s} {length}")
    return "\n".join(lines)
