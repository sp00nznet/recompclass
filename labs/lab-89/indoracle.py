"""
Lab 89: Independent Oracle

Differentially validate against a third-party implementation, and tell a
genuine target bug from a harness bug wearing its costume.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# Register widths in bits. A value wider than its register cannot come from
# the target -- it can only come from the harness.
REGISTER_WIDTHS = {"pc": 12, "a": 4, "b": 4, "x": 12, "y": 12, "sp": 8, "flags": 4}

# Fields whose value depends on how each side advances time, not on the CPU.
TIMING_FIELDS = {"cycles", "timer"}


def validate_state(state):
    """Check every register holds a value its width can represent.

    Returns:
        A list of (field, value, width) tuples for impossible values, sorted by
        field name. Empty means the state is at least representable.

    Fields not in REGISTER_WIDTHS are not checked.
    """
    # TODO: For each field in REGISTER_WIDTHS present in state, check
    #       0 <= value < (1 << width).
    pass


def compare_step(a, b):
    """Compare two states and classify any disagreement.

    Args:
        a: the reference (oracle) state dict.
        b: the state under test.

    Returns:
        A dict with:
            "agree"     - bool
            "fields"    - sorted list of differing field names
            "kind"      - None when they agree, otherwise one of
                          "impossible_value", "timing", "target_bug"
            "detail"    - a human-readable explanation, or ""

    Classification order matters:
      1. If either state holds an impossible value -> "impossible_value".
         Your harness is corrupting data; nothing else can be trusted.
      2. Else if every differing field is timing-derived -> "timing".
         Freeze the clocks and re-run; the test is about the CPU.
      3. Else -> "target_bug".
    """
    # TODO: Run validate_state on both, then diff the union of their keys,
    #       then classify in the order above.
    pass


def run_validation(steps, oracle_fn, target_fn, limit=1000000):
    """Step both implementations until they disagree.

    Args:
        steps: opaque program handle passed to both.
        oracle_fn: callable(steps, i) -> state dict.
        target_fn: callable(steps, i) -> state dict.
        limit: max steps.

    Returns:
        A dict with:
            "diverged"  - bool
            "step"      - index of the first disagreement, or None
            "kind"      - the classification, or None
            "fields"    - differing fields, or []
            "detail"    - explanation, or ""
            "steps_run" - how many steps completed

    A StopIteration from either side ends the run cleanly.
    """
    # TODO: Loop, call both, compare_step, and return on the first
    #       disagreement.
    pass


def format_validation(result):
    """Format a validation result, with advice keyed to the classification."""
    if not result["diverged"]:
        return f"no divergence in {result['steps_run']} step(s)"

    advice = {
        "impossible_value":
            "Your harness is corrupting data before the comparison. "
            "Check the trace transport (binary mode?) before the CPU.",
        "timing":
            "Only timing-derived fields differ. Freeze the clocks on both "
            "sides -- the test is about the CPU.",
        "target_bug":
            "A genuine semantic difference. Minimise it (Lab 66) and bisect "
            "(Lab 63).",
    }
    return (f"diverged at step {result['step']} [{result['kind']}]\n"
            f"  fields: {', '.join(result['fields'])}\n"
            f"  {result['detail']}\n"
            f"  -> {advice.get(result['kind'], '')}")
