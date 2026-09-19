"""
Lab 55: Synthetic Fixture Suite

Hand-assembled instruction fixtures and golden-output assertions -- the
highest-value test a recompiler can have, and legally free of the ROM.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import difflib

# A tiny assembler vocabulary: mnemonic -> (opcode, operand_bytes)
OPCODES = {
    "nop":   (0x00, 0),
    "ld_a":  (0x3E, 1),
    "add_a": (0x87, 0),
    "jp":    (0xC3, 2),
    "jp_nz": (0xC2, 2),
    "call":  (0xCD, 2),
    "ret":   (0xC9, 0),
    "jp_hl": (0xE9, 0),
}


class Fixture:
    """A named test case: source, assembled bytes, and expected lifter output.

    Attributes:
        name: what this fixture is testing.
        source: list of assembly lines.
        expected: the golden lifter output, or None if not yet recorded.
        why: one line saying why this case is hard. Fixtures without a
             reason tend to be the easy cases nobody needed tested.
    """

    def __init__(self, name, source, expected=None, why=""):
        self.name = name
        self.source = source
        self.expected = expected
        self.why = why


def assemble(lines):
    """Assemble a list of source lines into bytes.

    Each line is a mnemonic optionally followed by a hex operand:

        nop
        ld_a 0x42
        jp 0x1234

    Blank lines and lines starting with ";" are ignored. A 1-byte operand is
    emitted as-is; a 2-byte operand is little-endian.

    Args:
        lines: list of strings.

    Returns:
        A bytes object.

    Raises:
        ValueError: on an unknown mnemonic, or a missing or extra operand.
    """
    # TODO: For each meaningful line, split into mnemonic and optional operand.
    #       Look the mnemonic up in OPCODES to get (opcode, operand_bytes).
    #       Validate that an operand is present exactly when operand_bytes > 0.
    #       Emit the opcode, then the operand little-endian in the right width.
    pass


def run_fixture(fixture, lifter):
    """Run one fixture through *lifter* and compare against its golden text.

    Args:
        fixture: a Fixture.
        lifter: callable(bytes) -> str, the lifter under test.

    Returns:
        A dict with keys:
            "name"     - the fixture name
            "status"   - "pass", "fail", or "no_golden"
            "actual"   - the lifter's output
            "diff"     - unified diff text when status is "fail", else ""

    A fixture with expected=None is "no_golden" -- not a pass. An unrecorded
    golden is an untested fixture, and counting it as a pass is how a suite
    quietly stops testing anything.
    """
    # TODO: Call lifter(assemble(fixture.source)). If fixture.expected is None,
    #       return status "no_golden". Otherwise compare, and on mismatch build
    #       a unified diff with difflib.unified_diff over splitlines().
    pass


def run_suite(fixtures, lifter):
    """Run every fixture and summarise.

    Returns:
        A dict with keys:
            "results"   - list of run_fixture dicts, in input order
            "passed"    - int
            "failed"    - int
            "no_golden" - int
    """
    # TODO: Run each fixture, collect results, count each status.
    pass


def regenerate(fixtures, lifter):
    """Produce updated golden text for every fixture.

    This deliberately does NOT modify the fixtures in place. It returns the
    new goldens so a human can review the diff before committing them.

    Returns:
        A dict mapping fixture name -> new golden text.
    """
    # TODO: Run the lifter over each fixture's assembled bytes and collect
    #       the output by name.
    pass


def format_report(summary):
    """Format a suite summary, with diffs for failures."""
    lines = [f"fixtures: {len(summary['results'])}  "
             f"passed: {summary['passed']}  "
             f"failed: {summary['failed']}  "
             f"no golden: {summary['no_golden']}"]
    for r in summary["results"]:
        if r["status"] == "fail":
            lines.append(f"\nFAIL {r['name']}")
            lines.append(r["diff"])
        elif r["status"] == "no_golden":
            lines.append(f"\nNO GOLDEN {r['name']} -- record it or delete it")
    return "\n".join(lines)
