"""
Lab 51: Pipeline Driver with Content-Hash Caching

A stage-based pipeline driver. Each stage is a pure function over files,
so a stage whose inputs have not changed does not need to run again.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import hashlib
import json


class Stage:
    """One pipeline stage.

    Attributes:
        name: stage name, used in the cache key.
        version: tool version string. Changing it invalidates the cache.
        func: callable(inputs: list[str], outdir: str) -> list[str].
              Returns the paths it produced.
    """

    def __init__(self, name, version, func):
        self.name = name
        self.version = version
        self.func = func


def hash_file(path):
    """Return the SHA-256 hex digest of a file's contents.

    Args:
        path: path to the file.

    Returns:
        A 64-character lowercase hex string.
    """
    # TODO: Read the file in binary mode and return hashlib.sha256(data).hexdigest().
    pass


def stage_key(stage, inputs):
    """Compute a cache key for running *stage* over *inputs*.

    The key must change if any of these change:
      - the stage name
      - the stage's tool version
      - the contents of any input file

    Args:
        stage: a Stage.
        inputs: list of input file paths.

    Returns:
        A hex string.
    """
    # TODO: Build a stable string from stage.name, stage.version and the
    #       sorted (path, hash_file(path)) pairs, then hash it.
    #       Sorting matters: the same inputs in a different order are the
    #       same inputs, and must produce the same key.
    pass


class Pipeline:
    """Runs stages in order, skipping those whose inputs are unchanged."""

    def __init__(self, stages, outdir):
        self.stages = stages
        self.outdir = outdir
        self.cache = {}        # stage_key -> list of output paths
        self.ran = []          # names of stages that executed this run
        self.skipped = []      # names of stages served from cache
        self._provenance = {}

    def run(self, inputs):
        """Run every stage in order, threading outputs into the next stage.

        For each stage:
          - compute its key from the current inputs
          - if the key is in self.cache, record a skip and reuse the outputs
          - otherwise run it, store the outputs under the key, record a run

        Args:
            inputs: list of paths feeding the first stage.

        Returns:
            The final stage's output paths.
        """
        # TODO: Implement the loop described above. Reset self.ran and
        #       self.skipped at the start so repeated runs report correctly,
        #       and record provenance as you go (see provenance()).
        pass

    def provenance(self):
        """Return a record of the last run.

        Returns:
            A dict with keys:
                "inputs"  - list of (path, hash) pairs for the initial inputs
                "stages"  - list of dicts, one per stage, each with
                            "name", "version", "key", "cached" (bool),
                            "outputs" (list of paths)
        """
        # TODO: Return the provenance record built during run().
        pass


def format_provenance(record):
    """Format a provenance record as human-readable lines."""
    lines = ["=== Provenance ==="]
    for path, digest in record.get("inputs", []):
        lines.append(f"  input  {path}  {digest[:12]}")
    for st in record.get("stages", []):
        tag = "CACHED" if st["cached"] else "RAN   "
        lines.append(f"  {tag} {st['name']:20s} v{st['version']:8s} {st['key'][:12]}")
    return "\n".join(lines)
