"""
Lab 103: Symbol Importer

Convert a decompilation project's symbols into your function-set file,
record which upstream commit they came from, and report what changed.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def parse_symbols(text):
    """Parse an upstream symbol file.

    Format, one symbol per line:

        80056780 Player_Init 0x120
        80056900 Player_Update 0x80

    Fields are whitespace-separated: hex address, name, hex size. Blank lines
    and lines starting with "#" are ignored.

    Returns:
        A list of dicts with "addr", "name" and "size", in file order.

    Raises:
        ValueError: on a malformed line. A symbol file you half-parsed is
            worse than one you rejected.
    """
    # TODO: Split lines, skip blanks and comments, split each into three
    #       fields, and parse the two hex numbers.
    pass


def validate_symbols(symbols):
    """Check imported symbols before trusting them.

    Returns:
        A list of problem strings. Empty means they look sane.

    Checks:
      - zero or negative size
      - duplicate addresses
      - overlapping extents (sorted by address, each must end at or before the
        next one starts)
    """
    # TODO: Run the three checks, reporting each problem with its symbol name.
    pass


def to_function_set(symbols, commit):
    """Convert symbols into a function set with provenance.

    Args:
        symbols: output of parse_symbols.
        commit: the upstream commit these came from.

    Returns:
        A dict with:
            "source_commit" - the commit string
            "count"         - how many symbols
            "functions"     - dict mapping name -> {"addr", "size"}

    Raises:
        ValueError: on a duplicate *name*. Two functions with one name means
            one silently shadows the other everywhere downstream.
    """
    # TODO: Build the dict, rejecting duplicate names.
    pass


def diff_imports(old, new):
    """Report what changed between two imports.

    Args:
        old, new: function sets from to_function_set. `old` may be None for a
            first import.

    Returns:
        A dict with:
            "added"    - sorted names only in new
            "removed"  - sorted names only in old
            "moved"    - sorted list of dicts with "name", "from", "to" for
                         functions whose address changed
            "resized"  - sorted list of dicts with "name", "from", "to" for
                         functions whose size changed
            "from_commit" / "to_commit"
    """
    # TODO: Handle old being None as an all-added first import, then compare.
    pass


def format_diff(diff):
    """Format an import diff."""
    lines = [f"import {diff['from_commit'] or '(first)'} -> {diff['to_commit']}"]
    for name in diff["added"]:
        lines.append(f"  + {name}")
    for name in diff["removed"]:
        lines.append(f"  - {name}")
    for m in diff["moved"]:
        lines.append(f"  ~ {m['name']} moved 0x{m['from']:X} -> 0x{m['to']:X}")
    for r in diff["resized"]:
        lines.append(f"  ~ {r['name']} resized 0x{r['from']:X} -> 0x{r['to']:X}")
    return "\n".join(lines)
