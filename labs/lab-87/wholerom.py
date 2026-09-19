"""
Lab 87: Whole-ROM Emitter

Emit an entire address space as one C function with a label per
instruction, falling through on sequential code.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# An instruction is a dict:
#   {"addr": int, "mnemonic": str, "cycles": int,
#    "kind": "normal" | "jump" | "call" | "return",
#    "target": int or None}


def emit_label(addr):
    """Return the C label for *addr*, e.g. "L_0546"."""
    # TODO: Format as L_ plus four uppercase hex digits.
    pass


def emit_instruction(insn):
    """Emit the C for one instruction, without its label.

    Every instruction accumulates its cycle cost. Then:

      normal  -> nothing further
      jump    -> "goto L_XXXX;"
      call    -> "push_return(0xNNNN);" then "goto L_XXXX;" where the pushed
                 address is the instruction AFTER this one (addr + 1)
      return  -> "goto *pop_return();"

    Returns:
        A list of C statement strings, already indented four spaces.
    """
    # TODO: Build the list. Start with the cycles line, then the kind-specific
    #       statements.
    pass


def emit_rom(program):
    """Emit the whole ROM as a single C function.

    Structure:

        void run_rom(cpu_t *c) {
        L_0000: /* NOP */
            c->cycles += 4;
        L_0001: /* JP 0x0010 */
            c->cycles += 12;
            goto L_0010;
        ...
        }

    Sequential instructions simply fall through -- no dispatch, no branch.

    Args:
        program: list of instruction dicts, sorted by address.

    Returns:
        A string of C source.
    """
    # TODO: Open the function, emit a label and body per instruction with the
    #       mnemonic as a comment, then close.
    pass


def count_gotos(source):
    """Count `goto` statements in emitted source.

    Returns:
        An int. Computed transfers (`goto *`) count too -- they are still
        transfers, just not resolvable ones.
    """
    # TODO: Count occurrences of "goto".
    pass


def reachable_labels(program):
    """Which labels are actually targeted by something?

    A label is reachable-by-branch if some instruction jumps or calls to it.
    Fallthrough does not count: the point is to find labels that could be
    dropped entirely.

    Returns:
        A sorted list of addresses.
    """
    # TODO: Collect every non-None target from jump and call instructions.
    pass


def label_savings(program):
    """How many labels could be dropped?

    Returns:
        A dict with "total", "targeted" and "droppable".
    """
    total = len(program)
    targeted = len(reachable_labels(program) or [])
    return {"total": total, "targeted": targeted, "droppable": total - targeted}
