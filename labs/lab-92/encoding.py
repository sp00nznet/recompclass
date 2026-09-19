"""
Lab 92: Encoding Traps

A bytecode decoder with a multi-byte escape, and the corpus check that
catches a misparse producing plausible-but-wrong instructions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# Encoding: one byte, opcode:5 | a:3.
# If a == 7, a 16-bit big-endian operand follows; otherwise B = a.
# Opcode 0 is the "simple" set, where B selects the instruction.
ESCAPE = 7

SIMPLE_OPS = {0: "pop", 1: "dup", 2: "return", 3: "push-self",
              4: "set-lex-scope", 5: "iter-next", 6: "iter-done",
              7: "pop-handlers"}

# Opcodes 1 and 2 are unused: the gap that makes a guessed table look shifted.
OPCODES = {0: "simple", 3: "push", 4: "push-const", 5: "call", 6: "invoke",
           7: "send", 11: "branch", 12: "branch-if-true", 13: "branch-if-false"}


class DecodeError(Exception):
    """Raised when a byte stream cannot be decoded."""


def decode_one(data, pos):
    """Decode one instruction at *pos*.

    Returns:
        A dict with:
            "pos"    - where it started
            "opcode" - the 5-bit opcode
            "name"   - the instruction name
            "b"      - the operand value
            "length" - 1 or 3

    For opcode 0, "name" comes from SIMPLE_OPS[b].

    Raises:
        DecodeError: on a truncated escape, or an unknown opcode or simple-op.
    """
    # TODO: Read the byte. opcode = byte >> 3, a = byte & 7. If a == ESCAPE,
    #       read a 16-bit big-endian operand from the next two bytes (length 3);
    #       otherwise b = a (length 1). Then resolve the name, remembering that
    #       opcode 0 resolves through SIMPLE_OPS.
    pass


def decode_all(data):
    """Decode a whole byte stream.

    Returns:
        A list of instruction dicts.

    Raises:
        DecodeError: propagated from decode_one.
    """
    # TODO: Walk the stream, advancing by each instruction's length.
    pass


def decode_naive(data):
    """The BUGGY decoder: treats every instruction as one byte.

    This is what you get if you miss the escape. It does not crash -- it
    produces plausible instructions, which is exactly why the bug survives.

    Returns:
        A list of instruction dicts, all with length 1. Unknown opcodes and
        simple-ops become "?" rather than raising, because the whole point is
        that this decoder does not complain.
    """
    # TODO: One byte per instruction, b = byte & 7, names looked up leniently.
    pass


def corpus_check(programs):
    """Find programs where the naive and correct decoders disagree.

    Args:
        programs: dict mapping program name -> bytes.

    Returns:
        A dict with:
            "total"      - programs checked
            "disagree"   - how many differ
            "escapes"    - total escape sequences found across the corpus
            "affected"   - sorted names of the differing programs
            "errors"     - sorted names that failed to decode at all

    A program the correct decoder cannot decode is counted in "errors" and not
    in "disagree" -- those are different problems.
    """
    # TODO: For each program, decode both ways (guarding DecodeError), compare
    #       the instruction-name sequences, and count escapes (length == 3).
    pass
