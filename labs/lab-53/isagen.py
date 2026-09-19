"""
Lab 53: Table-Driven Lifter Generation

Parse a machine-readable ISA description into a decoder table, then
generate a lifter and a matching interpreter from that one table.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# Control-flow classes. Every opcode has exactly one.
CLASSES = {"normal", "branch", "cond_branch", "call", "return", "indirect"}

# Classes that end a basic block.
TERMINATORS = {"branch", "cond_branch", "call", "return", "indirect"}


class Entry:
    """One decoded opcode definition."""

    def __init__(self, opcode, mnemonic, operand, cls, cycles, semantics):
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.operand = operand        # "none", "imm8" or "imm16"
        self.cls = cls
        self.cycles = cycles
        self.semantics = semantics

    @property
    def length(self):
        """Total instruction length in bytes, including the opcode."""
        return 1 + {"none": 0, "imm8": 1, "imm16": 2}[self.operand]

    def __repr__(self):
        return f"Entry(0x{self.opcode:02X}, {self.mnemonic})"


def parse_isa(text):
    """Parse an ISA description into a list of Entry objects.

    Format, one instruction per line, fields separated by "|":

        opcode | mnemonic | operand | class | cycles | semantics

    Blank lines and lines whose first non-space character is "#" are ignored.
    Fields are stripped of surrounding whitespace. The opcode is hex ("0x3E").

    Args:
        text: the description.

    Returns:
        A list of Entry objects, in file order.

    Raises:
        ValueError: on an unknown class, a bad operand kind, or a duplicate
            opcode. Failing loudly here is the point -- a typo in an ISA
            table that silently becomes a wrong instruction is Module 38's
            worst bug class.
    """
    # TODO: Split into lines, skip blanks and comments, split each on "|",
    #       strip fields, validate class against CLASSES and operand against
    #       the length map, reject duplicate opcodes, and build Entry objects.
    pass


def build_table(entries):
    """Build a 256-entry table indexed by opcode.

    Args:
        entries: list of Entry objects.

    Returns:
        A list of length 256, each element an Entry or None.
    """
    # TODO: Allocate [None] * 256 and place each entry at its opcode.
    pass


def check_coverage(table):
    """Report which opcodes are undefined.

    Returns:
        A dict with keys:
            "defined"   - int, how many opcodes have entries
            "undefined" - sorted list of opcode ints with no entry
    """
    # TODO: Count non-None entries; collect the indices of the None ones.
    pass


def emit_lifter(table):
    """Generate C source for a lifter from the table.

    The output is a function containing a switch over the opcode. Each case
    emits the entry's cycle cost, then its semantics, then breaks.

        void lift(uint8_t op, cpu_t *c) {
            switch (op) {
            case 0x00: /* NOP */
                c->cycles += 4;
                pass;
                break;
            ...
            default:
                unknown_opcode(op);
                break;
            }
        }

    Undefined opcodes are not emitted -- they fall to `default`.

    Returns:
        A string of C source.
    """
    # TODO: Build the function text. Iterate opcodes 0..255 in order, skipping
    #       None entries. Include the mnemonic as a comment on each case.
    pass


def emit_interpreter(table):
    """Generate Python source for an interpreter from the SAME table.

    The output defines `def step(op, cpu):` with an if/elif chain mirroring
    the lifter's switch -- same cycle costs, same semantics, same order.

        def step(op, cpu):
            if op == 0x00:  # NOP
                cpu.cycles += 4
            elif ...
            else:
                raise ValueError(f"unknown opcode {op:#04x}")

    Returns:
        A string of Python source.
    """
    # TODO: Same iteration as emit_lifter, different syntax. Use "if" for the
    #       first entry and "elif" thereafter, and end with the else clause.
    pass


def terminators(table):
    """Return the sorted opcodes whose class ends a basic block."""
    return sorted(i for i, e in enumerate(table) if e and e.cls in TERMINATORS)
