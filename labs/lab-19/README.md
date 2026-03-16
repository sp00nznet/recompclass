# Lab 19: NID Resolver

## Objective

Implement PS3 NID (Name ID) resolution -- the hash-based function import
system used by PS3 executables (PRX/SPRX modules). Understanding NIDs is
essential for building a PS3 static recompiler because every imported function
in a PS3 binary is referenced by its NID hash rather than by name.

## Background

The PS3 uses a unique approach to dynamic linking. Instead of storing function
names as strings in the import table (like ELF on Linux), PS3 executables
store **NIDs** -- 32-bit identifiers derived from the function name using a
hash algorithm.

The NID computation algorithm:

1. Take the function name as a UTF-8 string (e.g., `"cellGcmInit"`).
2. Compute the SHA-1 hash of that string.
3. Take the **first 4 bytes** of the SHA-1 digest (big-endian).
4. The resulting 32-bit value is the NID.

For example:
- `"cellGcmInit"` -> SHA-1 -> first 4 bytes -> NID `0xB1A3A0A4` (example)

To resolve a NID back to a function name, you need a **NID database** -- a
mapping from NID values to known function names. The PS3 homebrew community
has built extensive NID databases covering the PS3 SDK.

### Suffix Versioning

Some PS3 modules use suffix versioning where a version suffix is appended
before hashing (e.g., `"cellGcmInit_1A2B3C4D"`). This is a stretch goal for
this lab.

## Files

| File                  | Description                                      |
|-----------------------|--------------------------------------------------|
| `nid_resolver.py`      | NID hash computation and resolution             |
| `nid_database.json`    | Sample database of ~30 common PS3 function NIDs |
| `test_lab.py`          | Tests for NID computation and resolution        |

## Tasks

1. Study the NID computation algorithm in `nid_resolver.py`.
2. Verify the implementation against the known NIDs in the database.
3. Run the tests to check correctness.
4. (Stretch) Implement suffix versioning support.
5. (Stretch) Build a reverse lookup table for fast NID-to-name resolution.

## Running

```bash
python nid_resolver.py
python test_lab.py
```
