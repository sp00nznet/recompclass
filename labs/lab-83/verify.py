"""
Lab 83: Input Verification

Identify the user's copy by hash, name the revision it found, warn clearly
on a mismatch, and print a provenance record.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import hashlib


def hash_data(data):
    """Return the SHA-256 hex digest of *data*."""
    # TODO: hashlib.sha256(data).hexdigest()
    pass


def identify(data, known):
    """Identify which known revision *data* is.

    Args:
        data: the bytes.
        known: dict mapping sha256 hex -> revision label.

    Returns:
        The label, or None if unrecognised.
    """
    # TODO: Hash and look up.
    pass


def check(data, known, target):
    """Verify the user's copy against the revision this project targets.

    Args:
        data: the bytes they supplied.
        known: dict mapping sha256 hex -> label.
        target: the label this project targets.

    Returns:
        A dict with:
            "verdict" - "match", "known_mismatch" or "unknown"
            "found"   - the identified label, or None
            "digest"  - the hash of what they gave you
            "message" - what to tell them

    The message must always name the digest, so a bug report carries it even
    when the revision is unrecognised. No verdict refuses to proceed.
    """
    # TODO: Identify, compare against target, and build the message for each
    #       of the three cases. For a known mismatch, say what it means:
    #       different addresses, hints will not apply.
    pass


def provenance(data, known, target, tool_versions):
    """Build the provenance record for a run.

    Args:
        data: the input bytes.
        known: the revision table.
        target: the targeted label.
        tool_versions: dict mapping tool name -> version string.

    Returns:
        A dict with "digest", "identified", "target", "verdict" and "tools"
        (a sorted list of "name=version" strings, so the record is stable
        between runs and diffable).
    """
    # TODO: Reuse check(), then add the sorted tool list.
    pass


def format_provenance(record):
    """Format a provenance record for printing at startup."""
    lines = ["=== Provenance ==="]
    lines.append(f"  input:      {record['digest'][:16]}...")
    lines.append(f"  identified: {record['identified'] or '(unrecognised)'}")
    lines.append(f"  target:     {record['target']}")
    lines.append(f"  verdict:    {record['verdict']}")
    for t in record["tools"]:
        lines.append(f"  tool:       {t}")
    return "\n".join(lines)
