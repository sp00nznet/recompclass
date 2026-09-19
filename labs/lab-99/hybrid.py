"""
Lab 99: Instrument a Hybrid

Count registered functions, hook hits and fallbacks, and report the
crossover metric -- what fraction of execution is actually native.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class Interceptor:
    """An interception registry with the counters the design owes you."""

    def __init__(self, fallback=None):
        self.registry = {}          # addr -> (callable, instruction_count)
        self.fallback = fallback    # callable(addr) -> instruction_count
        self.native_calls = 0
        self.fallback_calls = 0
        self.native_instructions = 0
        self.fallback_instructions = 0
        self.crashes = 0

    def register(self, addr, func, instructions=1):
        """Register a recompiled function at a guest address."""
        self.registry[addr] = (func, instructions)

    def dispatch(self, addr):
        """Run the recompiled function if there is one, else fall back.

        A registered function that raises is counted as a crash and falls back,
        which is what the real implementations do -- and is exactly why the
        counters matter.

        Returns:
            The number of instructions executed.

        Raises:
            RuntimeError: if nothing is registered and there is no fallback.
        """
        # TODO: Look up the address. On a hit, call it inside a try; on success
        #       count a native call and its instructions, on an exception count
        #       a crash and fall through. On a miss (or after a crash), use the
        #       fallback and count it, or raise if there is none.
        pass

    def crossover(self):
        """The fraction of executed instructions that ran as native code.

        Returns:
            A float in [0.0, 1.0]. Zero executed instructions gives 0.0.
        """
        # TODO: native_instructions / (native + fallback), guarding zero.
        pass

    def stats(self):
        """Return every counter, plus the crossover."""
        return {
            "registered": len(self.registry),
            "native_calls": self.native_calls,
            "fallback_calls": self.fallback_calls,
            "native_instructions": self.native_instructions,
            "fallback_instructions": self.fallback_instructions,
            "crashes": self.crashes,
            "crossover": self.crossover(),
        }


def honest_summary(stats):
    """A claim about a hybrid build that does not overstate it.

    Rules, in order:
      - no instructions executed -> "Nothing has executed."
      - crossover == 0.0         -> "N functions registered, but 0% of executed
                                     instructions ran native -- the fallback is
                                     running this program."
      - crossover == 1.0         -> "All executed instructions ran native code
                                     (N functions registered)."
      - otherwise                -> "P% of executed instructions ran native
                                     (N functions registered)."

    Then, if crashes > 0, append " C recompiled function(s) crashed and fell
    back."

    Returns:
        A string.
    """
    # TODO: Implement the rules. Percentages rounded to one decimal place.
    pass
