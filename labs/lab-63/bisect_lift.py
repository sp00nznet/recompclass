"""
Lab 63: Bisect Harness

A LIFT_LO/LIFT_HI style range switch, and a binary search that isolates
one bad function out of thousands.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def in_range(addr, lo, hi):
    """Is *addr* inside the inclusive range [lo, hi]?

    A range where lo > hi is empty -- nothing is lifted. That is the "all
    original" baseline and must be representable.
    """
    # TODO: Return the inclusive range test.
    pass


def run_with_range(addrs, lo, hi, oracle_fn, lifted_fn):
    """Execute each address with the lifted or the original implementation.

    Args:
        addrs: list of addresses, in execution order.
        lo, hi: inclusive range of addresses to run lifted.
        oracle_fn: callable(addr) -> value, the known-good implementation.
        lifted_fn: callable(addr) -> value, the implementation under test.

    Returns:
        A list of the values produced, in order.
    """
    # TODO: For each address, call lifted_fn if in_range, else oracle_fn.
    pass


def bisect(addrs, test):
    """Find the lowest address whose inclusion in the lifted range fails *test*.

    `test(lo, hi)` returns True when running [lo, hi] lifted is GOOD.

    The search assumes monotonicity: if lifting up to address X is bad, lifting
    up to anything beyond X is also bad. That holds when exactly one function is
    broken, which is the case this technique is for.

    Args:
        addrs: sorted list of candidate addresses.
        test: callable(lo, hi) -> bool.

    Returns:
        The offending address, or None if test(all) is already good.
    """
    # TODO: First check whether lifting everything is good -- if so, return None.
    #       Then binary search over the *index* into addrs for the smallest
    #       prefix [addrs[0], addrs[i]] that is bad, and return addrs[i].
    pass


def bisect_log(addrs, test):
    """Like bisect(), but also return every range tried.

    Returns:
        A tuple (found_addr_or_None, log), where log is a list of dicts with
        "lo", "hi" and "good".
    """
    # TODO: Wrap `test` so each call appends to a log, then run the same search.
    pass


def format_log(found, log):
    """Format a bisection log."""
    lines = [f"bisection: {len(log)} run(s)"]
    for entry in log:
        tag = "good" if entry["good"] else "BAD "
        lines.append(f"  [0x{entry['lo']:X}, 0x{entry['hi']:X}] {tag}")
    lines.append(f"  => {'0x%X' % found if found is not None else 'no bad function'}")
    return "\n".join(lines)
