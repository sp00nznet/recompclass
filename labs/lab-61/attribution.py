"""
Lab 61: Attribution Harness

Count what the guest did and what your harness did, separately, so a
screenshot stops being the only evidence you have.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


GUEST = "guest"
HARNESS = "harness"
SOURCES = (GUEST, HARNESS)


class Attribution:
    """Counts draws and dispatches, tagged by who caused them."""

    def __init__(self):
        self.frame = {"draws": {GUEST: 0, HARNESS: 0},
                      "dispatch": {"native": 0, "fallback": 0}}
        self.session = {"draws": {GUEST: 0, HARNESS: 0},
                        "dispatch": {"native": 0, "fallback": 0},
                        "frames": 0}

    def record_draw(self, source, count=1):
        """Record *count* draw calls attributed to *source*.

        Args:
            source: GUEST or HARNESS.
            count: how many draws.

        Raises:
            ValueError: on an unknown source. A draw you cannot attribute is
                worse than one you did not count -- it is the exact ambiguity
                this harness exists to remove.
        """
        # TODO: Validate source against SOURCES, then add to both the frame
        #       and session counters.
        pass

    def record_dispatch(self, native):
        """Record one dispatch.

        Args:
            native: True if a recompiled function ran, False if it fell back
                to an interpreter, emulator, or stub.
        """
        # TODO: Increment "native" or "fallback" in both frame and session.
        pass

    def end_frame(self):
        """Close the current frame and return its summary.

        Returns:
            A dict with "draws" and "dispatch" sub-dicts for this frame only.

        The frame counters reset afterwards; the session counters do not.
        """
        # TODO: Snapshot the frame counters, bump session["frames"], reset the
        #       frame counters, and return the snapshot.
        pass

    def session_summary(self):
        """Return session totals plus the derived ratios.

        Returns:
            A dict with:
                "frames"          - int
                "draws"           - {GUEST: int, HARNESS: int}
                "dispatch"        - {"native": int, "fallback": int}
                "guest_draw_ratio" - guest draws / total draws, 0.0 if none
                "native_ratio"     - native / total dispatches, 0.0 if none
        """
        # TODO: Copy the session counters and compute the two ratios, guarding
        #       against division by zero.
        pass


def honest_claim(summary):
    """Return a claim about the evidence that refuses to overstate it.

    Rules, checked in this order:

      - No draws at all            -> "Nothing has been drawn."
      - No guest draws             -> "All N draws came from the harness; the
                                       guest has not drawn anything."
      - Some guest draws           -> "X of N draws came from guest code
                                       (P%); the rest are harness."
      - All draws from guest       -> "All N draws came from guest code."

    Then, if any dispatches were recorded, append one sentence:

      - fallback == 0  -> " All N dispatches ran native code."
      - otherwise      -> " F of N dispatches fell back."

    Returns:
        A string.
    """
    # TODO: Implement the rules above. Percentages are rounded to whole
    #       numbers. The point of the ordering is that the weakest true
    #       statement wins.
    pass
