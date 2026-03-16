"""
Lab 31: Trace Comparator

Compare two execution traces (CSV) and find the first divergence.
"""

import sys
import os
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Trace Loading
# ---------------------------------------------------------------------------

def load_trace(filepath):
    """Load an execution trace from a CSV file.

    The CSV has a header row with column names (e.g., address, a, b, c, d,
    sp, flags). Each subsequent row is one trace step. All values are
    hex strings (with or without "0x" prefix).

    Args:
        filepath: path to the CSV file.

    Returns:
        A list of dicts, one per trace step. Each dict maps column name
        to an int value. For example:
            {"address": 0x0100, "a": 0x00, "b": 0x00, ...}
    """
    # TODO: 1. Open the file and create a csv.DictReader.
    # TODO: 2. For each row, convert every value from hex string to int.
    #          Handle both "0x1A" and "1A" formats (use int(val, 16)).
    # TODO: 3. Return the list of dicts.
    pass


def load_trace_from_string(text):
    """Load a trace from a CSV string (for testing without files).

    Args:
        text: a string in CSV format (with header row).

    Returns:
        Same format as load_trace().
    """
    # TODO: 1. Split text into lines.
    # TODO: 2. Use csv.DictReader on the lines.
    # TODO: 3. Convert values the same way as load_trace().
    pass


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_traces(trace_a, trace_b):
    """Compare two traces and find the first divergence.

    Args:
        trace_a: list of dicts (the reference/expected trace).
        trace_b: list of dicts (the test trace to compare against).

    Returns:
        None if the traces match completely (up to the shorter length).

        If a divergence is found, return a dict with:
            "step"     - int, the 0-based step index where divergence occurs
            "expected" - dict, the trace_a row at that step
            "got"      - dict, the trace_b row at that step
            "differs"  - list of column names that differ
    """
    # TODO: 1. Walk both traces in parallel (zip or index loop).
    # TODO: 2. At each step, compare every key/value pair.
    # TODO: 3. If any values differ, collect the differing column names
    #          and return the divergence dict.
    # TODO: 4. If no divergences found, return None.
    pass


def format_divergence(div):
    """Format a divergence dict into a human-readable string.

    Args:
        div: dict returned by compare_traces(), or None.

    Returns:
        A string describing the divergence. If div is None, return
        "Traces match."
    """
    # TODO: If div is None, return "Traces match."
    # TODO: Otherwise, build a multi-line string showing:
    #       - The step number (0-based) and CSV line number (step + 2,
    #         accounting for the header row).
    #       - The expected values.
    #       - The actual values.
    #       - Which columns differ and their values.
    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <trace_a.csv> <trace_b.csv>")
        sys.exit(1)

    trace_a = load_trace(sys.argv[1])
    trace_b = load_trace(sys.argv[2])

    if trace_a is None or trace_b is None:
        print("Error: load_trace() returned None.")
        sys.exit(1)

    print(f"Comparing {sys.argv[1]} vs {sys.argv[2]}...")
    div = compare_traces(trace_a, trace_b)
    print(format_divergence(div))


if __name__ == "__main__":
    main()
