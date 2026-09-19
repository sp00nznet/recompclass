"""
Lab 88: Fold a Paging Instruction

Statically track a paged architecture's latched page so the paging
instruction emits nothing at all -- and assert the invariant that allows it.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class PagingError(Exception):
    """Raised when the folding assumption does not hold."""


def resolve_targets(program):
    """Fold each PSET's page into the transfer instruction that follows it.

    An instruction is a dict:
        {"addr": int, "op": "PSET"|"JP"|"CALL"|"NOP"|...,
         "page": int or None, "offset": int or None}

    A transfer's absolute target is `(latched_page << 8) | offset`.

    Args:
        program: list of instruction dicts, in address order.

    Returns:
        A new list where every transfer has an added "target" key holding its
        resolved absolute address, and non-transfers have "target": None.
        PSET instructions are left in place -- emit() decides to drop them.

    Raises:
        PagingError: if a transfer is reached with no page ever latched. That
            is a genuinely unresolvable target, not something to guess at.
    """
    # TODO: Walk the program carrying the latched page. On PSET, update it.
    #       On JP/CALL, compute the target. Raise if no page has been latched.
    pass


def check_pset_invariant(program):
    """Is every PSET immediately followed by a control transfer?

    This is the assumption that lets PSET be folded away entirely, including
    its interrupt hold-off.

    Returns:
        A list of addresses of PSET instructions that are NOT followed by a
        transfer, sorted. Empty means the fold is sound.
    """
    # TODO: For each PSET, look at the next instruction in the list.
    #       A PSET as the final instruction is also a violation.
    pass


def emit(program):
    """Emit C, dropping PSET entirely.

    Every instruction still gets a label, so a computed transfer can reach it.
    A PSET's body is empty -- a comment recording what was folded, nothing else.

    Returns:
        A list of source lines.

    Raises:
        PagingError: if the invariant does not hold. Emitting a fold whose
            precondition is unchecked is how a silent bug ships.
    """
    # TODO: Call check_pset_invariant first and raise if it reports anything.
    #       Then resolve targets and emit: label, comment, and for transfers a
    #       goto to the resolved label.
    pass


def folding_report(program):
    """Summarise what folding achieved.

    Returns:
        A dict with:
            "instructions" - total
            "psets"        - how many PSETs
            "folded"       - how many emitted nothing (same as psets when the
                             invariant holds)
            "transfers"    - how many resolved transfers
    """
    psets = sum(1 for i in program if i["op"] == "PSET")
    transfers = sum(1 for i in program if i["op"] in ("JP", "CALL"))
    violations = check_pset_invariant(program) or []
    return {"instructions": len(program), "psets": psets,
            "folded": psets - len(violations), "transfers": transfers}
