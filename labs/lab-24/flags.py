"""
Lab 24: Flag Computation Library

Implement Z80-style flag computation for arithmetic operations.
All values are 8-bit unsigned (0-255).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def compute_add_flags(a, b):
    """Compute flags for: result = a + b (8-bit).

    Args:
        a: int, first operand (0-255).
        b: int, second operand (0-255).

    Returns:
        Dict with keys "Z", "N", "H", "C" (each a bool):
          Z = True if (a + b) & 0xFF == 0
          N = False (ADD clears the subtract flag)
          H = True if carry from bit 3 to bit 4
              i.e., (a & 0x0F) + (b & 0x0F) > 0x0F
          C = True if carry out of bit 7
              i.e., a + b > 0xFF
    """
    # TODO: Implement this function.
    pass


def compute_sub_flags(a, b):
    """Compute flags for: result = a - b (8-bit).

    Args:
        a: int, first operand (0-255).
        b: int, second operand (0-255).

    Returns:
        Dict with keys "Z", "N", "H", "C" (each a bool):
          Z = True if (a - b) & 0xFF == 0
          N = True (SUB always sets the subtract flag)
          H = True if borrow from bit 4
              i.e., (a & 0x0F) - (b & 0x0F) < 0
          C = True if borrow (a < b)
    """
    # TODO: Implement this function.
    pass


def compute_and_flags(a, b):
    """Compute flags for: result = a & b (8-bit).

    Args:
        a: int, first operand (0-255).
        b: int, second operand (0-255).

    Returns:
        Dict with keys "Z", "N", "H", "C" (each a bool):
          Z = True if (a & b) == 0
          N = False
          H = True  (AND always sets H on the Z80)
          C = False (AND always clears C)
    """
    # TODO: Implement this function.
    pass


def compute_inc_flags(a, old_carry):
    """Compute flags for: result = a + 1 (8-bit).

    INC does not affect the carry flag -- it preserves whatever
    the carry was before.

    Args:
        a: int, the value being incremented (0-255).
        old_carry: bool, the current carry flag value.

    Returns:
        Dict with keys "Z", "N", "H", "C" (each a bool):
          Z = True if (a + 1) & 0xFF == 0
          N = False
          H = True if carry from bit 3 to bit 4
              i.e., (a & 0x0F) + 1 > 0x0F  (same as: (a & 0x0F) == 0x0F)
          C = old_carry (unchanged)
    """
    # TODO: Implement this function.
    pass


def compute_dec_flags(a, old_carry):
    """Compute flags for: result = a - 1 (8-bit).

    DEC does not affect the carry flag -- it preserves whatever
    the carry was before.

    Args:
        a: int, the value being decremented (0-255).
        old_carry: bool, the current carry flag value.

    Returns:
        Dict with keys "Z", "N", "H", "C" (each a bool):
          Z = True if (a - 1) & 0xFF == 0
          N = True
          H = True if borrow from bit 4
              i.e., (a & 0x0F) - 1 < 0  (same as: (a & 0x0F) == 0x00)
          C = old_carry (unchanged)
    """
    # TODO: Implement this function.
    pass
