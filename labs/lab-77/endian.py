"""
Lab 77: Endianness Two Ways

Byte-swap-on-access versus swapped storage with an address XOR, compared
on read-heavy and write-heavy workloads.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def swap32(value):
    """Byte-swap a 32-bit value.

    Returns:
        The swapped value, masked to 32 bits.
    """
    # TODO: Reverse the four bytes.
    pass


def byte_xor(addr):
    """The address XOR that selects the right byte within a swapped word.

    With 32-bit words stored byte-swapped, byte N of a guest word lives at
    host offset N ^ 3.
    """
    return addr ^ 3


class SwapOnAccess:
    """Store native, swap on every word access.

    Attributes:
        swaps: how many byte-swaps were performed.
    """

    def __init__(self, size):
        self.memory = bytearray(size)
        self.swaps = 0

    def read32(self, addr):
        """Read a big-endian 32-bit word, swapping to host order."""
        # TODO: Read four bytes little-endian from self.memory, swap, count it.
        pass

    def read8(self, addr):
        """Read one byte. No swap is needed for a single byte."""
        # TODO: Index directly.
        pass

    def write32(self, addr, value):
        """Write a 32-bit word in guest order, swapping on the way in."""
        # TODO: Swap, count it, store four bytes little-endian.
        pass


class SwappedStorage:
    """Store pre-swapped, so aligned word access is free.

    Attributes:
        xors: how many address XORs were performed (sub-word accesses only).
        swaps: how many byte-swaps were performed -- should stay at zero for
            aligned word access, which is the entire point.
    """

    def __init__(self, size):
        self.memory = bytearray(size)
        self.xors = 0
        self.swaps = 0

    def read32(self, addr):
        """Read an aligned 32-bit word. No swap, no XOR."""
        # TODO: The word is already in host order: read four bytes
        #       little-endian and return.
        pass

    def read8(self, addr):
        """Read one byte, XOR-ing the address to find it."""
        # TODO: Count the XOR and index at byte_xor(addr).
        pass

    def write32(self, addr, value):
        """Write an aligned 32-bit word. No swap, no XOR."""
        # TODO: Store four bytes little-endian.
        pass


def compare(workload, size=0x100):
    """Run a workload through both strategies and compare cost and results.

    Args:
        workload: list of ("w32", addr, value) / ("r32", addr, None) /
            ("r8", addr, None) tuples.
        size: memory size for both.

    Returns:
        A dict with:
            "agree"          - bool, did every read match?
            "mismatches"     - list of (index, op, addr, a_value, b_value)
            "swap_cost"      - swaps performed by SwapOnAccess
            "storage_cost"   - xors performed by SwappedStorage
    """
    # TODO: Build one of each, replay the workload on both, compare every
    #       read's result, and report the two counters.
    pass
