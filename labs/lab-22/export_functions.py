"""
Lab 22: Ghidra Script - Function Exporter

Export all identified functions from a Ghidra project to JSON.

When run inside Ghidra, the `ghidra` and `currentProgram` variables
are provided automatically. For testing, we use a mock module.
"""

import json
import os
import sys

# When running outside Ghidra, use the mock module in this directory.
# Inside Ghidra, these imports are provided by the runtime.
try:
    from ghidra.program.model.listing import FunctionManager  # noqa: F401
    _IN_GHIDRA = True
except ImportError:
    _IN_GHIDRA = False
    sys.path.insert(0, os.path.dirname(__file__))
    from mock_ghidra import MockProgram


# ---------------------------------------------------------------------------
# Function extraction
# ---------------------------------------------------------------------------

def get_all_functions(program):
    """Collect all functions from the program's FunctionManager.

    Args:
        program: a Ghidra Program object (or MockProgram for testing).

    Returns:
        A list of dicts, each with keys:
            "name"    - str, the function name
            "address" - str, the entry point formatted as "0xNNNNNNNN"
            "size"    - int, the function body size in bytes
    """
    # TODO: 1. Get the FunctionManager from program.
    #          Use: program.getFunctionManager()
    # TODO: 2. Get an iterator over all functions.
    #          Use: fm.getFunctions(True)  (True = forward order)
    # TODO: 3. For each function, extract:
    #          - name: func.getName()
    #          - address: format func.getEntryPoint() as "0x" + hex string,
    #            zero-padded to 8 hex digits
    #          - size: func.getBody().getNumAddresses()
    # TODO: 4. Return the list of dicts.
    pass


def export_to_json(program, output_path):
    """Export function information to a JSON file.

    Args:
        program: a Ghidra Program object (or MockProgram for testing).
        output_path: file path for the output JSON.

    Returns:
        The data dict that was written (for testing convenience).
    """
    # TODO: 1. Call get_all_functions(program) to get the function list.
    # TODO: 2. Build a dict with keys:
    #          "binary" - program.getName()
    #          "function_count" - len(functions)
    #          "functions" - the list from step 1
    # TODO: 3. Write the dict to output_path as formatted JSON.
    #          Use json.dump() with indent=2.
    # TODO: 4. Return the dict.
    pass


# ---------------------------------------------------------------------------
# Ghidra entry point
# ---------------------------------------------------------------------------

def run():
    """Entry point when run as a Ghidra script."""
    if _IN_GHIDRA:
        # In real Ghidra, currentProgram is a global
        import __main__
        program = __main__.currentProgram
        out = os.path.join(os.path.expanduser("~"), "functions.json")
        data = export_to_json(program, out)
        print(f"Exported {data['function_count']} functions to {out}")


if __name__ == "__main__":
    run()
