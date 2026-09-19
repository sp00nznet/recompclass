"""
Lab 57: Manifest-Driven Pipeline

Convert a pipeline driven by command-line flags into one driven by a
declarative manifest, keeping derived state out of the source file.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import os


# Sections a manifest may contain. Anything else is an error -- a typo'd
# section name that is silently ignored is a decision that quietly stopped
# applying.
KNOWN_SECTIONS = {"project", "input", "entrypoint", "imports", "memory"}

# Sections that must NEVER appear: these hold derived state, which belongs in
# the output directory as a cache, not in the manifest as a source.
FORBIDDEN_SECTIONS = {"discovered", "cache", "generated", "analysis"}


class ManifestError(Exception):
    """Raised for a manifest that cannot be trusted."""


def parse_manifest(text):
    """Parse an INI-like manifest.

        [project]
        name = worms
        base = 0x82000000

        [entrypoint.functions]
        0x82236F38 = tail-call discovery missed
        0x82E80100 = runtime-harvested (tolerant dispatch boot)

        [imports]
        XUsbcamGetState = purge:8

    Rules:
      - `[section]` starts a section; `[a.b]` is a subsection, stored under the
        key "a.b".
      - `key = value`, both stripped.
      - Blank lines and lines starting with "#" are ignored.
      - A key before any section header is an error.

    Returns:
        A dict mapping section name -> dict of key/value strings, preserving
        insertion order.

    Raises:
        ManifestError: on a key outside a section, or a malformed line.
    """
    # TODO: Walk the lines. Track the current section. Build nested dicts.
    pass


def validate(manifest):
    """Check a parsed manifest, raising on anything untrustworthy.

    Rejects:
      - any section whose top-level name is in FORBIDDEN_SECTIONS
      - any section whose top-level name is not in KNOWN_SECTIONS
      - a missing [project] section, or a [project] without a name

    Returns:
        True if the manifest is valid.

    Raises:
        ManifestError: with a message naming the offending section.
    """
    # TODO: For each section, take the part before any "." as its top-level
    #       name and check it against FORBIDDEN_SECTIONS then KNOWN_SECTIONS.
    #       Then check [project] exists and has a "name".
    pass


def hints(manifest):
    """Extract function-entry hints with their recorded provenance.

    Reads the "entrypoint.functions" section, where each key is a hex address
    and each value is a free-text note saying where the hint came from.

    Returns:
        A list of dicts with keys "addr" (int) and "source" (str), sorted by
        address. Returns [] if the section is absent.

    Raises:
        ManifestError: if a hint has an empty note. An address with no
            recorded provenance is the thing Module 14 warns about -- you
            cannot later tell a runtime-verified hint from a pointer-scan guess.
    """
    # TODO: Read the section, parse each key with int(key, 16), require a
    #       non-empty value, sort by address.
    pass


def resolve_overrides(manifest):
    """Parse the [imports] section into per-import overrides.

    Each value is a comma-separated list of `field:value` pairs:

        XUsbcamGetState = purge:8
        SomeOtherImport = purge:4, mode:stub

    Returns:
        A dict mapping import name -> dict of field -> value, with "purge"
        converted to int. Returns {} if the section is absent.

    Raises:
        ManifestError: on a malformed pair or a non-integer purge.
    """
    # TODO: Split each value on ",", then each item on ":", strip both sides,
    #       and convert purge to int.
    pass


def derived_path(manifest, outdir):
    """Return where derived state for this project should be written.

    Derived state is a cache. It goes in the output directory, named after the
    project, and it is never written back into the manifest.

    Returns:
        A path string: "<outdir>/<project name>.derived.json"
    """
    # TODO: Read the project name and build the path with os.path.join.
    pass
