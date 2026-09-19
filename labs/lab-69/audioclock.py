"""
Lab 69: Audio Clock Discipline

A feedback loop that holds the audio buffer near a target fill level,
instead of a fixed resample ratio that drifts into an underrun.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class Buffer:
    """A fixed-capacity sample buffer that counts its own failures."""

    def __init__(self, capacity):
        self.capacity = capacity
        self.level = 0
        self.underruns = 0
        self.overruns = 0

    def write(self, count):
        """Add *count* samples, dropping any that do not fit.

        Returns:
            How many samples were actually stored. An overrun (any drop)
            increments self.overruns once per call, not once per sample.
        """
        # TODO: Clamp to capacity, count an overrun if anything was dropped.
        pass

    def read(self, count):
        """Remove up to *count* samples.

        Returns:
            How many samples were actually available. An underrun (fewer
            available than requested) increments self.underruns once per call.
        """
        # TODO: Clamp to level, count an underrun if short.
        pass

    @property
    def fill(self):
        """Fill level as a fraction of capacity, 0.0 to 1.0."""
        return self.level / self.capacity if self.capacity else 0.0


class ClockDiscipline:
    """Adjusts the consumption rate to hold a buffer near a target fill.

    The correction is proportional to the error, clamped so the pitch shift
    stays inaudible. A large correction fixes drift quickly and sounds wrong,
    which is not a trade worth making.
    """

    def __init__(self, target_fill=0.5, gain=0.05, max_correction=0.02):
        self.target_fill = target_fill
        self.gain = gain
        self.max_correction = max_correction

    def correction(self, fill):
        """Return the multiplier to apply to the nominal consumption rate.

        A fill above target means consume slightly faster (>1.0); below target,
        slightly slower (<1.0).

        The correction is `1.0 + clamp(gain * (fill - target), +/- max)`.

        Returns:
            A float near 1.0.
        """
        # TODO: Compute the error, scale by gain, clamp to +/- max_correction,
        #       and return 1.0 plus that.
        pass


def simulate(frames, produced_per_frame, nominal_consumed, capacity,
             discipline=None, drift=0.0):
    """Simulate a producer/consumer mismatch over many frames.

    Each frame: the guest writes `produced_per_frame` samples (scaled by
    `1.0 + drift` to model a clock that is slightly off), then the host reads
    `nominal_consumed` samples scaled by the discipline's correction.

    The buffer starts half full, which is what a real runtime does so there is
    slack in both directions.

    Args:
        frames: how many frames to run.
        produced_per_frame: guest sample rate per frame.
        nominal_consumed: host sample rate per frame.
        capacity: buffer size in samples.
        discipline: a ClockDiscipline, or None for a fixed ratio.
        drift: fractional clock error on the producer side.

    Returns:
        A dict with:
            "underruns" - int
            "overruns"  - int
            "fills"     - list of fill levels, one per frame
            "final_fill" - the last fill level
    """
    # TODO: Build the Buffer at half capacity, loop over frames, apply the
    #       correction when a discipline is given, and record the fill each
    #       frame.
    pass


def format_report(result):
    """Format a simulation result."""
    fills = result["fills"]
    lo = min(fills) if fills else 0.0
    hi = max(fills) if fills else 0.0
    return (f"frames:    {len(fills)}\n"
            f"underruns: {result['underruns']}\n"
            f"overruns:  {result['overruns']}\n"
            f"fill:      {lo:.2f} .. {hi:.2f} (final {result['final_fill']:.2f})")
