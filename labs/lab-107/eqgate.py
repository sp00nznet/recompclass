"""
Lab 107: Equivalence Gate

A gate that accepts candidate implementations only if they behave
identically to the original, and refuses everything else.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class Gate:
    """Accepts a candidate only if it matches the reference on every case.

    Attributes:
        reference: the known-good callable.
        cases: the caller-supplied argument tuples.
        probes: mandatory extra cases the gate always adds. A submitter who
            has seen `cases` can fit them; probes are what catch that.
    """

    def __init__(self, reference, cases, probes=None):
        self.reference = reference
        self.cases = list(cases)
        self.probes = list(probes or [])
        self.accepted = 0
        self.rejected = 0
        self.reasons = {}

    def all_cases(self):
        """Every case a candidate must satisfy: supplied cases plus probes."""
        return self.cases + self.probes

    def submit(self, candidate):
        """Test a candidate against the reference.

        Returns:
            A dict with:
                "accepted" - bool
                "reason"   - "" when accepted, otherwise one of
                             "raised", "mismatch"
                "detail"   - explanation
                "case"     - the first failing case, or None

        A candidate that raises on any case is rejected with "raised" -- an
        exception is not a near miss.

        Records the outcome in self.accepted / self.rejected / self.reasons.
        """
        # TODO: Walk all_cases(). Call the reference and the candidate inside
        #       a try. On an exception from the candidate, reject as "raised".
        #       On a mismatch, reject as "mismatch". Otherwise accept.
        pass

    def stats(self):
        """Return acceptance statistics.

        Returns:
            A dict with "submitted", "accepted", "rejected", "rate"
            (accepted / submitted, 0.0 when none) and "reasons".
        """
        # TODO: Assemble from the counters.
        pass


def make_boundary_probes(width=8):
    """Standard probes for an 8-bit two-operand function.

    Returns:
        A list of (a, b) tuples covering the values where flag and width bugs
        live: 0, 1, the nibble boundary, the signed boundary, and the maximum.
    """
    mask = (1 << width) - 1
    signed = 1 << (width - 1)
    edges = [0, 1, 0x0F, 0x10, signed - 1, signed, mask]
    return [(a, b) for a in edges for b in edges]
