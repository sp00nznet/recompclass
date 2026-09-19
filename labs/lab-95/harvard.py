"""
Lab 95: Harvard Memory Model

A memory layer for a CPU with disjoint code and data spaces, and the test
that catches an implementation which conflates them.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class SpaceError(Exception):
    """Raised on an access outside a space."""


class HarvardMemory:
    """Two disjoint address spaces sharing no addresses.

    Attributes:
        rom: instruction space, read-only.
        ram: data and peripheral space.
    """

    def __init__(self, rom_size=0x10000, ram_size=0x200):
        self.rom = bytearray(rom_size)
        self.ram = bytearray(ram_size)
        self.io_handlers = {}     # ram address -> callable(value_or_None)

    def fetch(self, addr):
        """Fetch an instruction byte from ROM.

        Raises:
            SpaceError: if addr is outside ROM.
        """
        # TODO: Bounds-check against len(self.rom) and index it.
        pass

    def ldc(self, addr):
        """Read a data byte from ROM -- the one instruction that crosses over.

        Raises:
            SpaceError: if addr is outside ROM.
        """
        # TODO: Same as fetch. It is a separate method because the *reason*
        #       differs, and a reader needs to see which accesses are LDC.
        pass

    def load(self, addr):
        """Read an operand byte from RAM, honouring any I/O handler.

        Raises:
            SpaceError: if addr is outside RAM.
        """
        # TODO: Bounds-check, then call the handler if one is registered for
        #       this address, else index self.ram.
        pass

    def store(self, addr, value):
        """Write an operand byte to RAM, honouring any I/O handler.

        Raises:
            SpaceError: if addr is outside RAM.
        """
        # TODO: Bounds-check, then dispatch to the handler or write the byte.
        pass

    def map_io(self, addr, handler):
        """Register an I/O handler at a RAM address.

        The handler is called as handler(None) for a read and handler(value)
        for a write; its return value is used for reads.
        """
        self.io_handlers[addr] = handler


def detect_conflation(memory):
    """Check that the two spaces really are disjoint.

    Writes distinguishable values at the same numeric address in each space and
    verifies both survive. A flat implementation cannot pass this.

    Args:
        memory: a HarvardMemory.

    Returns:
        None if the spaces are disjoint, otherwise a detail string.
    """
    # TODO: Pick an address valid in both spaces. Put one value in rom
    #       directly, store a different one via store(), then compare what
    #       ldc() and load() return.
    pass
