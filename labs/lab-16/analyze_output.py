#!/usr/bin/env python3
"""
analyze_output.py -- Analyze N64Recomp-generated C source files.

This script examines the C files produced by N64Recomp and reports:
  - Total number of generated functions
  - Size distribution of functions (by line count)
  - Functions containing indirect jumps (jr $reg where reg != $ra)
  - Basic statistics about the recompilation output

Usage:
    python analyze_output.py <output_directory>
"""

import os
import re
import sys
from collections import defaultdict


def find_c_files(directory):
    """Find all .c files in the given directory."""
    c_files = []
    for root, _dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".c"):
                c_files.append(os.path.join(root, f))
    return sorted(c_files)


def extract_functions(filepath):
    """
    Extract recompiled function definitions from a C file.

    N64Recomp generates functions with a consistent signature pattern:
        void recomp_<name>(uint8_t* rdram, recomp_context* ctx) {

    Returns a list of dicts: { 'name': str, 'start_line': int,
                                'end_line': int, 'body': str }
    """
    functions = []

    # Pattern matching N64Recomp's generated function signatures.
    func_pattern = re.compile(
        r"^void\s+(recomp_\w+)\s*\("
    )

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    current_func = None
    brace_depth = 0
    body_lines = []

    for i, line in enumerate(lines, start=1):
        if current_func is None:
            match = func_pattern.match(line)
            if match:
                current_func = {
                    "name": match.group(1),
                    "start_line": i,
                    "end_line": i,
                    "body_lines": [],
                }
                brace_depth = 0
                body_lines = []

        if current_func is not None:
            body_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "{" in "".join(body_lines):
                current_func["end_line"] = i
                current_func["body"] = "".join(body_lines)
                current_func["line_count"] = i - current_func["start_line"] + 1
                functions.append(current_func)
                current_func = None
                body_lines = []

    return functions


def check_indirect_jumps(func_body):
    """
    Check if a function body contains indirect jump patterns.

    In N64Recomp output, indirect jumps (jr $reg where reg != $ra) are
    translated into switch statements or computed gotos.  We look for
    telltale patterns like 'switch' or 'goto *'.
    """
    # N64Recomp typically translates indirect jumps to switch statements
    # on the target address.
    if "switch" in func_body:
        return True
    if "goto *" in func_body:
        return True
    # Also check for comments mentioning indirect jumps.
    if "jr " in func_body.lower() and "jr $ra" not in func_body.lower():
        return True
    return False


def size_bucket(line_count):
    """Categorize a function by its line count."""
    if line_count <= 10:
        return "tiny (1-10 lines)"
    elif line_count <= 50:
        return "small (11-50 lines)"
    elif line_count <= 200:
        return "medium (51-200 lines)"
    elif line_count <= 500:
        return "large (201-500 lines)"
    else:
        return "huge (500+ lines)"


def analyze_directory(directory):
    """Run the full analysis on a directory of generated C files."""
    c_files = find_c_files(directory)
    if not c_files:
        print(f"No .c files found in '{directory}'.")
        return

    print(f"Analyzing {len(c_files)} C file(s) in '{directory}'...\n")

    all_functions = []
    file_func_counts = {}

    for path in c_files:
        funcs = extract_functions(path)
        all_functions.extend(funcs)
        file_func_counts[os.path.basename(path)] = len(funcs)

    total = len(all_functions)
    print(f"Total recompiled functions: {total}")
    print()

    # --- Functions per file ---
    print("Functions per file:")
    for fname, count in sorted(file_func_counts.items()):
        print(f"  {fname}: {count}")
    print()

    # --- Size distribution ---
    buckets = defaultdict(int)
    for func in all_functions:
        buckets[size_bucket(func["line_count"])] += 1

    print("Size distribution:")
    for bucket in [
        "tiny (1-10 lines)",
        "small (11-50 lines)",
        "medium (51-200 lines)",
        "large (201-500 lines)",
        "huge (500+ lines)",
    ]:
        count = buckets.get(bucket, 0)
        print(f"  {bucket}: {count}")
    print()

    # --- Indirect jumps ---
    indirect = [f for f in all_functions if check_indirect_jumps(f["body"])]
    print(f"Functions with indirect jumps: {len(indirect)}")
    for func in indirect[:20]:  # Show at most 20.
        print(f"  {func['name']} (line {func['start_line']})")
    if len(indirect) > 20:
        print(f"  ... and {len(indirect) - 20} more.")
    print()

    # --- Largest functions ---
    largest = sorted(all_functions, key=lambda f: f["line_count"], reverse=True)
    print("Top 10 largest functions:")
    for func in largest[:10]:
        print(f"  {func['name']}: {func['line_count']} lines")
    print()

    # --- TODO: cross-reference with symbol file ---
    # TODO: Load a symbol file (address -> name mapping) and report:
    #   - Functions present in symbols but missing from output (not recompiled)
    #   - Functions in output that have no symbol (unnamed / auto-generated)
    #   - Address range coverage statistics


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output_directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a directory.")
        sys.exit(1)

    analyze_directory(target_dir)
