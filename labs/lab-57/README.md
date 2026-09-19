# Lab 57: Manifest-Driven Pipeline

## Objective

Build the manifest layer from Module 36: every decision in one declarative
file, nothing in your shell history, and derived state kept firmly out.

## Background

A recompilation project accumulates knowledge that cannot be regenerated:
addresses discovery missed, functions needing hand-written replacements,
imports with a different stack purge, memory regions that must map
somewhere specific. **That knowledge is the project.** Everything else
rebuilds from the input in minutes.

Look at what the ReXGlue ports commit: `worms_manifest.toml` is 8,431 bytes,
beside four source files totalling 8.5 KB. The manifest is as large as all
the hand-written code.

The rule for what belongs: **if you had to *learn* it, it goes in the file.
If the tool can read it off the binary, it does not.**

## Your Task

Implement in `manifest.py`:

- `parse_manifest(text)` -- a small INI-like format (no TOML dependency).
- `validate(manifest)` -- reject derived state and unknown sections loudly.
- `hints(manifest)` -- the function-entry hints, with their recorded source.
- `resolve_overrides(manifest)` -- per-import stack purges and forced modes.
- `derived_path(manifest, outdir)` -- where derived state goes: **not** in
  the manifest.

## The Rule That Matters

Module 36 section 3: the moment generated content lives in the manifest, the
diff stops being readable, merges become unresolvable, and you can no longer
tell a decision from a derivation. `validate()` enforces this -- a manifest
containing a `[discovered]` section is an error, not a convenience.

**Comment your hints.** A bare address is worthless in six months.
"runtime-harvested from a tolerant-dispatch boot" versus "pointer scan" is
exactly the distinction that decided Module 14's `civrev` bring-up: 301
scan hints made the build worse, 21 harvested ones fixed it.
