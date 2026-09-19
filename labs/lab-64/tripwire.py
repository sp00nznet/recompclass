"""
Lab 64: Boundary Tripwires

Assertions at every original-to-lifted boundary crossing, so silent
corruption surfaces at the call that caused it.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import copy


class TripwireFailure(Exception):
    """Raised when an invariant was violated across a boundary crossing."""

    def __init__(self, check, detail, call=None):
        super().__init__(f"{check}: {detail}" + (f" (call {call})" if call else ""))
        self.check = check
        self.detail = detail
        self.call = call


def check_stack(before, after):
    """Was the stack pointer restored across the call?

    Args:
        before, after: the stack pointer value before and after.

    Returns:
        None if the stack is intact, otherwise a detail string naming the
        delta -- e.g. "sp moved by -4 (0x1000 -> 0x0FFC)".
    """
    # TODO: Compare the two. On a mismatch return a string naming the delta
    #       and both values. Return None when they match.
    pass


def check_callee_saved(before, after, saved_regs):
    """Were the callee-saved registers preserved?

    Args:
        before, after: dicts mapping register name -> value.
        saved_regs: iterable of register names the ABI says must be preserved.

    Returns:
        None if all preserved, otherwise a detail string listing every
        clobbered register and its before/after values, comma separated,
        in *saved_regs* order.

    A register absent from either dict is not checked -- the caller decides
    what it recorded, and inventing a failure for a missing observation is
    how a tripwire starts crying wolf.
    """
    # TODO: Walk saved_regs, compare where both dicts have the register,
    #       and build the detail string.
    pass


def check_guards(memory, guards):
    """Are the guard bytes around protected regions intact?

    Args:
        memory: dict mapping address -> byte value.
        guards: dict mapping address -> expected byte value.

    Returns:
        None if every guard matches, otherwise a detail string naming each
        violated address in ascending order with expected and actual values.
        A guard address missing from memory counts as a violation -- something
        unmapped it.
    """
    # TODO: Compare each guard address against memory, in sorted order.
    pass


def guarded_call(fn, ctx, checks, call_name=None):
    """Run *fn* with tripwires around it.

    Args:
        fn: callable(ctx) -> value, the lifted function.
        ctx: a dict the checks read before and after. It must contain whatever
            the supplied checks need.
        checks: list of (name, callable(before_ctx, after_ctx) -> detail_or_None).
        call_name: optional identifier for the error message.

    Returns:
        The value fn returned.

    Raises:
        TripwireFailure: naming the FIRST check that fired, in list order.

    The before-snapshot must be a copy: if a check compares ctx against itself
    it can never fail, which is Module 35's "a check that cannot fail" in
    miniature.
    """
    # TODO: Deep-ish copy the context (a dict of dicts/ints is enough here),
    #       call fn, then run each check in order and raise on the first detail.
    pass
