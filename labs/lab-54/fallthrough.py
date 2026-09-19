"""
Lab 54: Fallthrough Detector

Find functions that end without a terminator -- the signature of the
single most common discovery bug in static recompilation.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# A tiny instruction model. Each instruction is a dict:
#   {"addr": int, "size": int, "mnemonic": str}
#
# Control-flow classes, by mnemonic:
RETURNS = {"ret", "rts", "jr_ra"}
UNCONDITIONAL_BRANCHES = {"jmp", "bra", "b", "j"}
CONDITIONAL_BRANCHES = {"beq", "bne", "bcc", "bcs", "jne", "je"}


def ends_with_terminator(func):
    """Does *func* end with a return or an unconditional branch?

    A function that ends any other way -- with arithmetic, a load, or a
    *conditional* branch -- runs off the end of its own body, which is the
    fallthrough signature.

    Args:
        func: dict with "addr", "size" and "instructions" (list of dicts).

    Returns:
        True if the last instruction terminates control flow.
        Returns False for a function with no instructions.
    """
    # TODO: Look at the last instruction's mnemonic. It terminates if it is in
    #       RETURNS or UNCONDITIONAL_BRANCHES. A conditional branch does NOT
    #       terminate -- control can fall through it.
    pass


def find_fallthroughs(functions):
    """Return every function that does not end with a terminator.

    Args:
        functions: list of function dicts.

    Returns:
        A list of the suspicious functions, in input order.
    """
    # TODO: Filter with ends_with_terminator().
    pass


def end_address(func):
    """Return the address just past the end of *func*."""
    return func["addr"] + func["size"]


def propose_merges(functions):
    """Propose merges that would repair fallthroughs.

    A fallthrough function whose end address is exactly the start address of
    another function was almost certainly split from it. Merging them restores
    the original.

    Args:
        functions: list of function dicts.

    Returns:
        A list of (first_addr, second_addr) tuples, sorted by first_addr.
        A function that falls through into nothing (no function starts where
        it ends) is NOT proposed -- that is a different problem, and the
        caller should be told about it separately via find_fallthroughs().
    """
    # TODO: Build an address -> function index. For each fallthrough function,
    #       check whether end_address(func) is the start of another function.
    #       If so, propose the pair.
    pass


def apply_merges(functions, merges):
    """Return a new function list with the proposed merges applied.

    A merged function starts at the first function's address, has the combined
    size, and has both instruction lists concatenated.

    Merges chain: if A merges into B and B merges into C, the result is one
    function spanning all three.

    Args:
        functions: list of function dicts.
        merges: list of (first_addr, second_addr) tuples.

    Returns:
        A new list, sorted by address. The input is not modified.
    """
    # TODO: Follow the merge chains. Start from each function that is not the
    #       *second* element of any merge, then keep absorbing successors while
    #       a merge exists from the current end.
    pass


def format_report(functions):
    """Summarise the fallthrough situation for a function list."""
    bad = find_fallthroughs(functions) or []
    merges = propose_merges(functions) or []
    lines = [
        f"functions:      {len(functions)}",
        f"fallthroughs:   {len(bad)}",
        f"repairable:     {len(merges)}",
        f"unexplained:    {len(bad) - len(merges)}",
    ]
    return "\n".join(lines)
