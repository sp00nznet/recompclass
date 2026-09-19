"""
Lab 106: Propose and Check

Take function-boundary proposals from any hypothesis generator and accept
or reject each one with structural and trace-based checkers.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def check_alignment(proposal, alignment):
    """Is the proposed address correctly aligned?

    Returns:
        None if fine, otherwise a reason string.
    """
    # TODO: addr % alignment must be 0.
    pass


def check_in_range(proposal, code_range):
    """Is the address inside the code region?

    Args:
        proposal: dict with "addr".
        code_range: (lo, hi) inclusive.

    Returns:
        None if fine, otherwise a reason string.
    """
    # TODO: Inclusive range test.
    pass


def check_not_mid_function(proposal, known):
    """Does this address fall inside a function we already know about?

    This is the check that caught civrev's over-hinting: a switch-table entry
    points into the middle of a real function, and hinting it splits that
    function in half.

    Args:
        proposal: dict with "addr".
        known: list of (start, size) tuples for functions already established.

    Returns:
        None if the address is not interior to any known function, otherwise a
        reason string. An address exactly at a known function's *start* is
        fine -- that is agreement, not a conflict.
    """
    # TODO: For each known function, reject when start < addr < start + size.
    pass


def check_observed(proposal, trace):
    """Did execution actually branch to this address?

    The strongest available evidence: a logged branch target is an observation,
    a pointer-shaped integer is a guess.

    Args:
        proposal: dict with "addr".
        trace: set or list of addresses execution actually reached.

    Returns:
        None if observed, otherwise a reason string. Not being observed is a
        weak signal, not proof of wrongness -- the caller decides how to weigh
        it, which is why this returns a reason rather than a verdict.
    """
    # TODO: Membership test.
    pass


def evaluate(proposals, code_range, known, trace, alignment=4):
    """Run every check over every proposal.

    Args:
        proposals: list of dicts with "addr" and "source".
        code_range: (lo, hi) inclusive.
        known: list of (start, size) tuples.
        trace: observed addresses.
        alignment: required alignment.

    Returns:
        A dict with:
            "accepted"  - proposals passing every hard check, sorted by addr
            "rejected"  - list of dicts with "addr", "source" and "reasons"
            "observed"  - how many accepted proposals were also observed
            "by_source" - dict mapping source -> {"accepted", "rejected"}

    Alignment, range and mid-function are **hard** checks: failing any one
    rejects the proposal. Being unobserved is recorded but does not reject.
    """
    # TODO: Run the three hard checks, collecting reasons. Record the observed
    #       count separately, and tally per source.
    pass


def format_evaluation(result):
    """Format an evaluation, per source."""
    lines = [f"accepted {len(result['accepted'])}, "
             f"rejected {len(result['rejected'])}, "
             f"{result['observed']} of the accepted were observed"]
    for source in sorted(result["by_source"]):
        counts = result["by_source"][source]
        lines.append(f"  {source:24s} +{counts['accepted']} -{counts['rejected']}")
    return "\n".join(lines)
