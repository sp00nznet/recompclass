"""
Lab 32: Dead Code Eliminator

Identify unreachable functions in a call graph.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Call Graph
# ---------------------------------------------------------------------------

def load_call_graph(filepath):
    """Load a call graph from a JSON file.

    Args:
        filepath: path to the JSON file.

    Returns:
        A tuple of (entry_point, graph) where:
            entry_point: str, the name of the entry function.
            graph: dict mapping function_name -> list of callee names.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    return data["entry"], data["functions"]


def load_call_graph_from_dict(data):
    """Load a call graph from a dict (for testing).

    Args:
        data: dict with "entry" and "functions" keys.

    Returns:
        Same as load_call_graph().
    """
    return data["entry"], data["functions"]


def find_reachable(entry, graph):
    """Find all functions reachable from the entry point.

    Use BFS or DFS to traverse the call graph starting from *entry*.

    Args:
        entry: str, the entry function name.
        graph: dict mapping function_name -> list of callee names.

    Returns:
        A set of function names reachable from the entry point
        (including the entry point itself).
    """
    # TODO: 1. Initialize a set of visited functions and a work-list
    #          (queue or stack) containing just the entry point.
    # TODO: 2. While the work-list is not empty:
    #          a. Pop a function name.
    #          b. If already visited, skip it.
    #          c. Add it to the visited set.
    #          d. For each callee in graph[function_name], add it to
    #             the work-list (if it exists in the graph).
    # TODO: 3. Return the visited set.
    pass


def find_dead_code(entry, graph):
    """Find all functions NOT reachable from the entry point.

    Args:
        entry: str, the entry function name.
        graph: dict mapping function_name -> list of callee names.

    Returns:
        A set of function names that are in the graph but not reachable
        from the entry point.
    """
    # TODO: 1. Call find_reachable() to get the reachable set.
    # TODO: 2. Return the set difference: all functions minus reachable.
    pass


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_analysis(entry, graph):
    """Print a summary of reachable and dead functions."""
    reachable = find_reachable(entry, graph)
    dead = find_dead_code(entry, graph)

    if reachable is None or dead is None:
        print("Functions returned None -- implement the TODO sections.")
        return

    print(f"Entry point: {entry}")
    print(f"Reachable functions ({len(reachable)}):")
    print(f"  {', '.join(sorted(reachable))}")
    print(f"Dead code ({len(dead)}):")
    if dead:
        print(f"  {', '.join(sorted(dead))}")
    else:
        print("  (none)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) == 2:
        entry, graph = load_call_graph(sys.argv[1])
    else:
        # Built-in example
        example = {
            "entry": "main",
            "functions": {
                "main": ["init", "game_loop"],
                "init": ["load_assets"],
                "game_loop": ["update", "render"],
                "update": [],
                "render": ["draw_sprite"],
                "draw_sprite": [],
                "load_assets": [],
                "debug_dump": ["debug_print"],
                "debug_print": [],
            }
        }
        entry, graph = load_call_graph_from_dict(example)

    print_analysis(entry, graph)


if __name__ == "__main__":
    main()
