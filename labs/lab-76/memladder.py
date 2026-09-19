"""
Lab 76: Memory Access Ladder

Three rungs of guest memory access -- a switch, a flat array, and a based
pointer -- measured on the same workload.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class IOTrap(Exception):
    """Raised when a bus implementation loses a memory-mapped access."""


class SwitchBus:
    """Rung 0: a chain of range comparisons, one per access.

    Attributes:
        comparisons: how many range checks were performed. This is the cost
            being measured.
    """

    def __init__(self, regions, io_handler=None):
        # regions: list of (start, size, bytearray) in check order
        self.regions = regions
        self.io_handler = io_handler
        self.comparisons = 0

    def read(self, addr):
        """Read one byte, walking the region list in order.

        Increments self.comparisons once per region examined, including the
        one that matches.

        Returns:
            The byte value.

        Raises:
            IOTrap: if no region matches and there is no io_handler.
        """
        # TODO: Walk self.regions in order, counting comparisons. On a match,
        #       return the byte at the right offset. On no match, call the
        #       io_handler if set, else raise IOTrap.
        pass


class FlatBus:
    """Rung 1: one array plus a base offset, with an I/O window check.

    Attributes:
        checks: how many I/O window comparisons were performed -- one per
            access, which is the entire per-access cost.
    """

    def __init__(self, size, base, io_range=None, io_handler=None):
        self.memory = bytearray(size)
        self.base = base
        self.io_range = io_range        # (lo, hi) inclusive, or None
        self.io_handler = io_handler
        self.checks = 0

    def read(self, addr):
        """Read one byte by offset arithmetic, after one I/O window check.

        Returns:
            The byte value.

        Raises:
            IOTrap: if the address is in the I/O window and no handler is set.
                Silently returning RAM for a hardware register is the exact
                failure Module 43 section 2 warns about.
        """
        # TODO: Increment checks. If io_range is set and addr falls inside it,
        #       delegate to io_handler (or raise IOTrap). Otherwise index
        #       self.memory at addr - self.base.
        pass


def classify_static(addr, io_range):
    """Decide at lift time whether an access needs the slow path.

    Most guest addresses are compile-time constants, so the lifter can emit the
    fast path directly and skip the runtime check entirely.

    Args:
        addr: the constant address, or None if it is computed at runtime.
        io_range: (lo, hi) inclusive, or None.

    Returns:
        "fast"    - a constant address outside the I/O window
        "io"      - a constant address inside it
        "dynamic" - not known at lift time, needs the runtime check
    """
    # TODO: Return the three cases above.
    pass


def benchmark(bus, accesses):
    """Run a list of addresses through a bus and report its work.

    Returns:
        A dict with "accesses", "work" (the bus's own counter) and
        "work_per_access".
    """
    # TODO: Read each address, then read the counter -- `comparisons` on a
    #       SwitchBus, `checks` on a FlatBus.
    pass
