"""
Lab 94: Classify the Unknowns

Backward-scan each indirect transfer for the write that defined its target
register, and group the sites by mechanism.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# An instruction is a dict: {"op": str, "dst": reg or None, "mode": str or None}
#
# Addressing modes that define a register, and what each implies:
MECHANISMS = {
    "displacement": "C++ virtual dispatch (a field of a struct)",
    "absolute16": "a fixed address in on-chip RAM (a dispatch table)",
    "indirect": "a genuine pointer",
    "absolute24": "a fixed far address",
}

UNKNOWN = "no definition in this block"


def find_definition(block, site_index, register):
    """Scan backwards for the last write to *register* before *site_index*.

    Args:
        block: list of instruction dicts, in order.
        site_index: index of the indirect transfer.
        register: the register it calls through.

    Returns:
        The defining instruction dict, or None if nothing in this block
        writes that register.
    """
    # TODO: Walk indices site_index-1 down to 0, returning the first
    #       instruction whose "dst" is the register.
    pass


def classify_site(block, site_index):
    """Classify one indirect transfer by what defined its target.

    Args:
        block: the basic block containing the site.
        site_index: index of the transfer, whose dict has a "reg" key.

    Returns:
        The addressing mode string of the defining instruction, or UNKNOWN.
    """
    # TODO: Read the site's "reg", call find_definition, and return the
    #       defining instruction's "mode" (or UNKNOWN when there is none).
    pass


def classify_all(sites):
    """Classify a list of (block, site_index) pairs.

    Returns:
        A dict mapping mechanism -> count.
    """
    # TODO: Classify each and tally.
    pass


def report(groups):
    """Format grouped counts, largest first, with the interpretation.

    Returns:
        A list of dicts with "mechanism", "count" and "means", sorted by count
        descending then mechanism ascending.
    """
    # TODO: Build and sort, looking each mechanism up in MECHANISMS and
    #       falling back to the mechanism string itself.
    pass


def summary_line(groups):
    """One line stating the real size of the problem."""
    total = sum(groups.values())
    return f"{total} indirect transfer(s) -- {len(groups)} different problem(s)"
