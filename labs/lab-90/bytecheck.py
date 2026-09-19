"""
Lab 90: Is It Bytecode?

Classify binaries as native code or bytecode from import count and
relocation density, against a known-native reference.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# Modules a native Windows program of this era cannot avoid.
SYSTEM_MODULES = {"KERNEL", "USER", "GDI", "KRNL386", "KERNEL32", "USER32", "GDI32"}


def relocation_density(binary):
    """Relocations per kilobyte of code.

    Args:
        binary: dict with "relocations" (int) and "code_bytes" (int).

    Returns:
        A float. A binary with no code has density 0.0 rather than raising --
        it is a degenerate input, not an error.
    """
    # TODO: relocations / (code_bytes / 1024), guarding zero.
    pass


def is_runtime_only(binary, system_modules=None):
    """Does this binary import nothing but somebody's runtime?

    Args:
        binary: dict with "imports" (list of module name strings).
        system_modules: the set a native program cannot avoid.

    Returns:
        True if the imports include no system module and at least one
        non-system module. A binary with no imports at all is not
        runtime-only -- it is something else, and saying so is more honest
        than guessing.

    Module names are compared case-insensitively and without any extension.
    """
    # TODO: Normalise the names, then apply the rule above.
    pass


def classify(binary, reference=None):
    """Classify a binary as native code, bytecode, or uncertain.

    Args:
        binary: dict with "name", "imports", "relocations", "code_bytes".
        reference: a known-native binary dict to compare density against, or
            None to use an absolute threshold.

    Returns:
        A dict with:
            "name"     - the binary's name
            "verdict"  - "native", "bytecode" or "uncertain"
            "density"  - its relocation density
            "reasons"  - list of human-readable strings

    Rules:
      - Runtime-only imports is strong evidence for bytecode.
      - Density below 10% of the reference (or below 1.0 per KB with no
        reference) is strong evidence for bytecode.
      - Both -> "bytecode". Neither -> "native". Exactly one -> "uncertain",
        because one signal is a hint and two are a finding.
    """
    # TODO: Compute both signals, build the reasons list, and apply the rules.
    pass


def format_classification(result):
    """Format a classification."""
    lines = [f"{result['name']}: {result['verdict'].upper()} "
             f"(density {result['density']:.2f}/KB)"]
    for r in result["reasons"]:
        lines.append(f"  - {r}")
    return "\n".join(lines)
