#!/usr/bin/env python3
"""
nid_resolver.py -- PS3 NID (Name ID) computation and resolution.

The PS3 identifies imported functions by a 32-bit hash (NID) rather than
by name string.  This module implements the NID hash algorithm and provides
lookup against a NID database.

Usage (standalone):
    python nid_resolver.py
"""

import hashlib
import json
import os
import sys
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
#  NID computation
# ---------------------------------------------------------------------------

def compute_nid(func_name: str) -> int:
    """
    Compute the PS3 NID for a given function name.

    Algorithm:
      1. Encode the function name as UTF-8.
      2. Compute the SHA-1 hash.
      3. Take the first 4 bytes of the digest as a big-endian uint32.

    Args:
        func_name: The function name string.

    Returns:
        The 32-bit NID value.
    """
    sha1_digest = hashlib.sha1(func_name.encode("utf-8")).digest()
    # First 4 bytes, big-endian.
    nid = int.from_bytes(sha1_digest[:4], byteorder="big")
    return nid


def compute_nid_hex(func_name: str) -> str:
    """Compute the NID and return it as a hex string like '0x1A2B3C4D'."""
    return f"0x{compute_nid(func_name):08X}"


# ---------------------------------------------------------------------------
#  NID Database
# ---------------------------------------------------------------------------

class NidDatabase:
    """
    A database mapping NID values to function names and module information.

    The database is loaded from a JSON file with the following structure:
    {
        "modules": {
            "module_name": {
                "nids": {
                    "0x1A2B3C4D": "functionName",
                    ...
                }
            },
            ...
        }
    }
    """

    def __init__(self):
        # Primary lookup: NID (int) -> list of (module, func_name).
        self._nid_to_names: Dict[int, List[tuple]] = {}
        # Reverse lookup: func_name (str) -> NID (int).
        self._name_to_nid: Dict[str, int] = {}

    def load(self, filepath: str) -> None:
        """Load a NID database from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        modules = data.get("modules", {})
        for module_name, module_data in modules.items():
            nids = module_data.get("nids", {})
            for nid_hex, func_name in nids.items():
                nid_int = int(nid_hex, 16)

                if nid_int not in self._nid_to_names:
                    self._nid_to_names[nid_int] = []
                self._nid_to_names[nid_int].append((module_name, func_name))
                self._name_to_nid[func_name] = nid_int

    def resolve(self, nid: int) -> Optional[List[tuple]]:
        """
        Resolve a NID to its function name(s).

        Args:
            nid: The 32-bit NID value.

        Returns:
            A list of (module_name, func_name) tuples, or None if not found.
        """
        return self._nid_to_names.get(nid)

    def resolve_hex(self, nid_hex: str) -> Optional[List[tuple]]:
        """Resolve a NID given as a hex string."""
        return self.resolve(int(nid_hex, 16))

    def lookup_name(self, func_name: str) -> Optional[int]:
        """Look up the NID for a given function name."""
        return self._name_to_nid.get(func_name)

    @property
    def size(self) -> int:
        """Number of unique NIDs in the database."""
        return len(self._nid_to_names)

    def verify_entry(self, func_name: str) -> bool:
        """
        Verify that the stored NID for a function matches the computed NID.

        This catches database errors where the NID was recorded incorrectly.
        """
        stored_nid = self.lookup_name(func_name)
        if stored_nid is None:
            return False
        computed_nid = compute_nid(func_name)
        return stored_nid == computed_nid

    # TODO: Implement suffix versioning support.
    # Some PS3 libraries version their NIDs by appending a suffix to the
    # function name before hashing, e.g., "funcName" + suffix_bytes.
    # Implement a method that tries known suffixes to resolve a NID.

    # TODO: Build a reverse lookup table.
    # Pre-compute NIDs for all known function names so that given a NID,
    # you can quickly find the name without iterating the whole database.


# ---------------------------------------------------------------------------
#  Demo / standalone usage
# ---------------------------------------------------------------------------

def demo():
    """Demonstrate NID computation and database lookup."""
    print("PS3 NID Resolver -- Demo\n")

    # Compute some NIDs.
    test_names = [
        "cellGcmInit",
        "cellSysmoduleLoadModule",
        "sys_process_exit",
        "cellPadGetData",
        "printf",
    ]

    print("NID Computation:")
    print("-" * 50)
    for name in test_names:
        print(f"  {name:40s} -> {compute_nid_hex(name)}")
    print()

    # Load database if available.
    db_path = os.path.join(os.path.dirname(__file__), "nid_database.json")
    if os.path.exists(db_path):
        db = NidDatabase()
        db.load(db_path)
        print(f"Loaded NID database with {db.size} entries.\n")

        print("Database Verification:")
        print("-" * 50)
        for name in test_names:
            result = db.lookup_name(name)
            if result is not None:
                match = "MATCH" if db.verify_entry(name) else "MISMATCH"
                print(f"  {name:40s} -> 0x{result:08X}  [{match}]")
            else:
                print(f"  {name:40s} -> (not in database)")
    else:
        print(f"Database file not found at {db_path}.")


if __name__ == "__main__":
    demo()
