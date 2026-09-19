"""
Lab 91: Stack to Locals

Compute static stack depth for a stack VM and emit numbered C locals
instead of a runtime stack.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class StackError(Exception):
    """Raised when the stack does not balance."""


# An instruction is a dict:
#   {"pc": int, "op": str, "pops": int, "pushes": int,
#    "target": int or None}   # branch target, if any
#   Ops "branch" (unconditional) and "branch_if" (conditional) use target.
#   Op "return" ends a path.


def compute_depths(program):
    """Compute the stack depth on entry to every instruction.

    Starts at pc 0 with depth 0 and follows both fallthrough and branch edges.
    Unreachable instructions get no entry.

    Args:
        program: list of instruction dicts, indexed by position; each "pc" is
            its index.

    Returns:
        A dict mapping pc -> depth on entry.

    Raises:
        StackError: if two paths reach the same pc with different depths --
            that is the misparse signature, and guessing which is right would
            hide it.
    """
    # TODO: Work-list traversal from pc 0. For each instruction compute the
    #       depth after it (depth - pops + pushes), then propagate to the
    #       fallthrough and/or branch successors, checking for conflicts.
    pass


def verify_balance(program):
    """Check the stack invariant across a whole program.

    Returns:
        A list of human-readable problem strings. Empty means it balances.

    Checks:
      - depth never goes negative (an instruction popped more than existed)
      - every "return" is reached at depth 0
      - compute_depths raises no conflict (reported as a problem, not an
        exception, so a corpus run can continue to the next program)
    """
    # TODO: Call compute_depths inside a try. Then walk the instructions with
    #       known depths, checking the two conditions above.
    pass


def max_depth(depths):
    """The most locals any point in the program needs."""
    return max(depths.values()) if depths else 0


def emit(program, depths):
    """Emit C using numbered locals instead of a runtime stack.

    Each instruction consumes its operands from the top slots and writes its
    result to the slot at its entry depth minus its pops.

        /*   46: find-var 0 */
        s[0] = op_find_var();
        /*   47: get-var 5  */
        s[1] = op_get_var();

    Args:
        program: the instructions.
        depths: output of compute_depths.

    Returns:
        A list of source lines, starting with the local declaration.
    """
    # TODO: Emit a declaration sized by max_depth, then one commented line per
    #       reachable instruction assigning to s[depth - pops] when it pushes,
    #       or a bare call when it does not.
    pass
