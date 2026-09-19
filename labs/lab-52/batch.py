"""
Lab 52: Batch Harness with Failure Categories

Run many targets through a pipeline unattended, isolating failures and
reporting them by category rather than as a single pass rate.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import json

# Failure categories, in pipeline order. A target is assigned the category of
# the first stage that failed.
CATEGORIES = ["ok", "extract_failed", "codegen_failed", "compile_failed",
              "crashed", "timeout", "error"]


class StageFailure(Exception):
    """Raised by a stage to report a categorised failure."""

    def __init__(self, category, message=""):
        super().__init__(message)
        self.category = category
        self.message = message


class Timeout(Exception):
    """Raised when a target exceeds its time budget."""


def run_target(target, stages, timeout=30):
    """Run one target through *stages*, catching everything.

    Each stage is a callable taking the value produced by the previous stage
    (the first receives *target*) and returning a value.

    A stage signals a categorised failure by raising StageFailure. A stage that
    raises Timeout is recorded as "timeout". Any other exception is "error" --
    an unexpected failure, which is itself useful information.

    Args:
        target: the target identifier (a path or name).
        stages: list of (stage_name, callable) pairs.
        timeout: seconds budget, passed through for the caller's use.

    Returns:
        A dict with keys:
            "target"   - the target
            "category" - one of CATEGORIES
            "stage"    - the stage name that failed, or None if ok
            "message"  - failure detail, or ""
    """
    # TODO: Walk the stages in order, passing each result to the next.
    #       Catch StageFailure -> use its category and the current stage name.
    #       Catch Timeout      -> category "timeout".
    #       Catch Exception    -> category "error", message = str(exc).
    #       If every stage completes, category "ok", stage None.
    pass


def run_batch(targets, stages, timeout=30):
    """Run every target, isolated from the others.

    One target failing -- for any reason, including a crash in your own
    harness code -- must not prevent the remaining targets from running.

    Returns:
        A list of result dicts from run_target, in target order.
    """
    # TODO: Call run_target for each target and collect the results.
    pass


def summarize(results):
    """Count results per category.

    Returns:
        A dict mapping category name -> count. Categories with no results
        are omitted. Also includes "total".
    """
    # TODO: Count each result's category, and add a "total" key.
    pass


def format_report(summary):
    """Format a summary as human-readable lines, most common category first."""
    total = summary.get("total", 0)
    lines = [f"=== Batch report: {total} target(s) ==="]
    for cat, count in sorted(
            ((k, v) for k, v in summary.items() if k != "total"),
            key=lambda kv: (-kv[1], kv[0])):
        pct = (100.0 * count / total) if total else 0.0
        lines.append(f"  {cat:16s} {count:5d}  {pct:5.1f}%")
    return "\n".join(lines)


def to_json(results):
    """Serialise results as JSON, one object per target, stably ordered."""
    return json.dumps(results, indent=2, sort_keys=True)
