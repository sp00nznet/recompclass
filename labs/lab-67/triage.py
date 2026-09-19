"""
Lab 67: Triage Tool

Deduplicate failing reproducers by cause, then rank the surviving groups
by how much of the program they actually affect.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


from collections import Counter

KINDS = ("crash", "divergence")


def fingerprint(report):
    """Return a dedup key for a failure report.

    Args:
        report: dict with "func" (int address), "insn" (str) and "kind"
            (one of KINDS).

    Returns:
        A tuple (func, insn, kind). Two reports with the same fingerprint are
        the same bug.

    Raises:
        ValueError: on an unknown kind. A report you cannot classify would
            form its own group and quietly look like a distinct bug.
    """
    # TODO: Validate report["kind"] against KINDS and build the tuple.
    pass


def deduplicate(reports):
    """Group reports by fingerprint.

    Returns:
        A list of dicts, one per distinct bug, each with:
            "fingerprint" - the key
            "func"        - the function address
            "insn"        - the instruction
            "kind"        - the kind
            "count"       - how many reports collapsed into this group
            "examples"    - the reports themselves, in input order

    Groups are returned in first-seen order so the output is stable.
    """
    # TODO: Walk the reports, keying an ordered dict by fingerprint.
    pass


def rank(groups, trace_counts):
    """Order groups by how much of the program they affect.

    Sort key, highest first:
      1. execution count of the group's function (0 if it never ran)
      2. the group's report count
      3. divergences before crashes -- a quiet wrong answer is worse than a
         loud stop, because nothing tells you about it
      4. function address, so the order is deterministic

    Args:
        groups: output of deduplicate().
        trace_counts: dict mapping function address -> times executed.

    Returns:
        A new list, sorted. Each group gains a "reach" key with its execution
        count.
    """
    # TODO: Annotate each group with its reach, then sort by the key above.
    #       Remember that "divergences first" means they sort HIGHER.
    pass


def triage(reports, trace_counts):
    """Deduplicate and rank in one step.

    Returns:
        A dict with:
            "total"   - how many reports came in
            "unique"  - how many distinct bugs
            "groups"  - the ranked groups
    """
    # TODO: Chain deduplicate() and rank().
    pass


def format_triage(result):
    """Format a triage result as a work list."""
    lines = [f"{result['total']} report(s) -> {result['unique']} distinct bug(s)"]
    for i, g in enumerate(result["groups"], 1):
        lines.append(
            f"  {i}. 0x{g['func']:08X} {g['insn']:12s} {g['kind']:10s} "
            f"x{g['count']:<4d} reach={g['reach']}")
    return "\n".join(lines)
