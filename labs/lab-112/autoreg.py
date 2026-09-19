"""
Lab 112: Auto-Registration

A self-registering function table where adding a function is one line and
an override is a link-order question.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class Registry:
    """A self-registering function table. Last registration at an address wins."""

    def __init__(self):
        self.table = {}      # addr -> (name, func)
        self.history = {}    # addr -> list of names, in registration order

    def register(self, addr, name, func):
        """Register a function at a guest address.

        A later registration at the same address replaces the earlier one --
        that is the override mechanism, not a bug. Both are recorded in the
        history so the override is visible.

        Returns:
            True if this registration overrode an earlier one, False if it was
            the first at that address.
        """
        # TODO: Record in history, note whether the address was already
        #       occupied, then set the table entry.
        pass

    def lookup(self, addr):
        """Return the callable registered at *addr*, or None."""
        # TODO: Return the function half of the table entry.
        pass

    def name_at(self, addr):
        """Return the name registered at *addr*, or None."""
        # TODO: Return the name half.
        pass

    def overrides(self):
        """Which addresses were overridden?

        Returns:
            A list of dicts with "addr", "active" (the winning name) and
            "shadowed" (the names it replaced, in registration order), sorted
            by address. Addresses registered once are not included.
        """
        # TODO: Walk history for entries with more than one name.
        pass

    def call(self, addr, *args):
        """Dispatch to the registered function.

        Raises:
            KeyError: if nothing is registered at that address.
        """
        func = self.lookup(addr)
        if func is None:
            raise KeyError(f"nothing registered at 0x{addr:X}")
        return func(*args)


def emit_registration(name, addr):
    """Emit the C that makes a function self-register.

    Produces a constructor-attributed registrar so the function is in the table
    before main() runs, with no central list to edit:

        void name(void);
        static void __attribute__((constructor)) register_name(void) {
            recomp_register(0xNNNNNN, "name", name);
        }

    Returns:
        A string of C source.
    """
    # TODO: Build the three lines, formatting the address as six hex digits.
    pass


def emit_link_order_note(registry):
    """Explain the override situation in a form a modder can act on."""
    overrides = registry.overrides() or []
    if not overrides:
        return "No overrides: every address is registered exactly once."
    lines = ["Overrides in effect (last registration wins):"]
    for o in overrides:
        shadowed = ", ".join(o["shadowed"])
        lines.append(f"  0x{o['addr']:06X}: {o['active']} (shadows {shadowed})")
    return "\n".join(lines)
