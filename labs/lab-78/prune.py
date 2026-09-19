"""
Lab 78: Prune and Trap

Compute a live function set from a trace, emit trap stubs for the rest,
and find a function you should not have removed.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def reachable(entry, call_graph):
    """Statically reachable functions from *entry*.

    Args:
        entry: the entry function name.
        call_graph: dict mapping name -> list of callee names.

    Returns:
        A set including the entry itself. Callees not present in the graph are
        still included -- an unknown callee is still a call.
    """
    # TODO: Work-list traversal from the entry.
    pass


def observed(trace):
    """Functions that actually executed.

    Args:
        trace: list of function names, in execution order, possibly repeated.

    Returns:
        A set of names.
    """
    # TODO: Set of the trace.
    pass


def live_set(entry, call_graph, trace):
    """The conservative union of static reachability and observation.

    Neither source alone is safe: static analysis misses indirect calls, and a
    trace misses whatever the playthrough did not reach.

    Returns:
        A set of names.
    """
    # TODO: Union the two.
    pass


def plan(all_functions, live):
    """Decide what to keep and what to replace with a trap stub.

    Args:
        all_functions: iterable of every function name.
        live: the live set.

    Returns:
        A dict with:
            "keep"      - sorted list of live function names
            "trap"      - sorted list of names to replace with trap stubs
            "kept"      - int
            "trapped"   - int
            "reduction" - trapped / total, 0.0 if there are no functions
    """
    # TODO: Partition and count.
    pass


class TrapRegistry:
    """Records which trap stubs fired, so a bad prune names itself."""

    def __init__(self, trapped):
        self.trapped = set(trapped)
        self.fired = {}

    def call(self, name):
        """A trapped function was called.

        Returns:
            The number of times this trap has now fired.

        Raises:
            KeyError: if *name* was never trapped -- that means the caller and
                the plan disagree, which is worth knowing loudly.
        """
        # TODO: Validate membership, increment and return the count.
        pass

    def report(self):
        """Which traps fired, most frequent first.

        Returns:
            A list of (name, count) tuples, sorted by count descending then
            name ascending.
        """
        # TODO: Sort self.fired.
        pass

    @property
    def clean(self):
        """True if no trap has fired -- the prune looks safe so far."""
        return not self.fired
