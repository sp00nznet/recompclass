"""
Lab 73: Guest-Level Sampling Profiler

Sample the program counter and resolve each sample to a guest function,
producing a profile in the game's own terms rather than the host's.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import bisect


def resolve(addr, functions):
    """Find the function containing *addr*.

    Args:
        addr: the sampled program counter.
        functions: list of (start, size, name) tuples, not necessarily sorted.

    Returns:
        The function name, or None if the address is in no known function.

    Use a binary search over the sorted starts -- a profiler that is O(n) per
    sample changes the thing it is measuring.
    """
    # TODO: Sort by start once (or accept a pre-sorted list), bisect for the
    #       last function starting at or before addr, then check that addr is
    #       actually inside its extent.
    pass


class Sampler:
    """Collects PC samples and resolves them to guest functions."""

    def __init__(self, functions):
        self.functions = sorted(functions, key=lambda f: f[0])
        self.samples = []
        self.unresolved = 0

    def sample(self, addr):
        """Record one sample.

        Samples that resolve to no function increment self.unresolved -- that
        count is itself informative, because it usually means execution left
        the recompiled image.
        """
        # TODO: Append the (addr, name) pair, or bump unresolved.
        pass

    def profile(self):
        """Return a ranked profile.

        Returns:
            A list of dicts with "name", "samples" and "percent", sorted by
            sample count descending then name ascending. Percent is of total
            samples taken, including unresolved ones -- otherwise a build that
            spends half its time outside the image looks perfectly healthy.
        """
        # TODO: Count per name, compute percentages against
        #       len(self.samples) + self.unresolved, and sort.
        pass


def detect_spin(samples, threshold=0.9):
    """Is the program stuck?

    Args:
        samples: list of (addr, name) pairs, in time order.
        threshold: fraction of samples at one address that counts as a spin.

    Returns:
        None if execution looks healthy, otherwise a detail string naming the
        address, the function and the fraction.

    An empty sample list is not a spin.
    """
    # TODO: Count addresses. If the most common exceeds threshold, report it.
    pass


def format_profile(sampler):
    """Format a profile."""
    rows = sampler.profile()
    total = len(sampler.samples) + sampler.unresolved
    lines = [f"{total} samples ({sampler.unresolved} outside the image)"]
    for r in rows:
        lines.append(f"  {r['percent']:5.1f}%  {r['samples']:6d}  {r['name']}")
    return "\n".join(lines)
