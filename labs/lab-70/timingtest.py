"""
Lab 70: Timing Regression Test

Assert that a fixed input reaches a known game state on a known frame --
catching a pacing bug that a frame-hash comparison cannot see.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class Timeline:
    """An ordered record of which state was observed on which frame."""

    def __init__(self, observations=None):
        self.observations = list(observations or [])   # list of (frame, state)

    def record(self, frame, state):
        self.observations.append((frame, state))

    def states(self):
        """Return the set of states observed."""
        return {s for _, s in self.observations}

    def frame_of(self, state):
        """Return the first frame at which *state* was observed, or None."""
        for frame, s in self.observations:
            if s == state:
                return frame
        return None


def compare_content(a, b):
    """The weak check: did both timelines see the same set of states?

    This deliberately ignores *when*. It is the comparison most projects
    actually run, and section "What You Must Demonstrate" in the README is
    about showing what it misses.

    Returns:
        A dict with:
            "match"   - bool
            "missing" - sorted states in a but not b
            "extra"   - sorted states in b but not a
    """
    # TODO: Compare the two state sets.
    pass


def compare_timeline(a, b, tolerance=0):
    """The real check: same states, reached at the same frames.

    A state reached more than *tolerance* frames away from the reference is a
    failure even though the state itself appeared.

    Args:
        a: the reference Timeline.
        b: the Timeline under test.
        tolerance: allowed absolute frame difference.

    Returns:
        A dict with:
            "match"    - bool
            "missing"  - sorted states absent from b
            "mistimed" - list of dicts with "state", "expected", "actual",
                         "delta", sorted by expected frame
    """
    # TODO: For each state in a, find its frame in b. Absent -> missing.
    #       Present but outside tolerance -> mistimed.
    pass


def assert_reaches(timeline, state, frame, tolerance=0):
    """Assert a single milestone was reached at about the right frame.

    Returns:
        None if satisfied, otherwise a detail string.
    """
    # TODO: Look up the frame, and compare against the expectation.
    pass


def format_comparison(result):
    """Format a timeline comparison."""
    if result["match"]:
        return "timeline matches"
    lines = ["timeline MISMATCH"]
    for s in result.get("missing", []):
        lines.append(f"  missing state: {s}")
    for m in result.get("mistimed", []):
        lines.append(f"  {m['state']}: expected frame {m['expected']}, "
                     f"got {m['actual']} (delta {m['delta']:+d})")
    return "\n".join(lines)
