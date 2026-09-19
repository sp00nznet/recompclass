"""
Lab 104: Matching Decomp as Oracle

Function-level differential testing against a matching decompilation, with
honest coverage reporting.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def compare_function(name, cases, decomp_fn, recomp_fn):
    """Differentially test one function against the decomp's version.

    Args:
        name: function name.
        cases: list of argument tuples.
        decomp_fn: the decompiled reference.
        recomp_fn: your recompiled version.

    Returns:
        A dict with:
            "name"      - the function name
            "cases"     - how many cases ran
            "status"    - "pass", "fail" or "error"
            "failures"  - list of dicts with "case", "expected", "actual"
            "message"   - detail for "error"

    A function that raises on some case is "error" -- distinct from a wrong
    answer, because the two send you to different places.
    """
    # TODO: Run both over every case inside a try. Collect mismatches. An
    #       exception from either implementation makes the whole function
    #       "error" with the message.
    pass


def run_suite(suite, decomp, recomp):
    """Run every function in the suite.

    Args:
        suite: dict mapping function name -> list of argument tuples.
        decomp: dict mapping name -> reference callable.
        recomp: dict mapping name -> callable under test.

    Returns:
        A dict with:
            "results"  - list of compare_function dicts, sorted by name
            "passed" / "failed" / "errors" - counts
            "missing"  - sorted names in the suite with no implementation on
                         one side or the other
    """
    # TODO: Skip names missing from either side into "missing"; run the rest.
    pass


def coverage(suite_result, all_functions):
    """How much of the program is actually covered?

    Args:
        suite_result: output of run_suite.
        all_functions: every function in the binary.

    Returns:
        A dict with:
            "tested"   - how many functions the suite exercised
            "total"    - len(all_functions)
            "fraction" - tested / total, 0.0 when total is 0
            "untested" - sorted names with no test
    """
    # TODO: Count the tested names from the results and compare against the
    #       full list.
    pass


def honest_report(suite_result, cov):
    """A report that refuses to describe low coverage as validation.

    Rules:
      - any failures or errors -> "N function(s) diverge from the decomp."
      - all passed and coverage >= 0.8 -> "All N tested functions match the
        decomp (P% coverage)."
      - all passed and coverage < 0.8  -> "All N tested functions match, but
        only P% of the binary is covered -- this is not validation of the
        build."

    Returns:
        A string.
    """
    # TODO: Implement the three cases. Percentages to one decimal place.
    pass
