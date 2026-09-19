# Lab 83: Input Verification

## Objective

Build the check from Module 46 section 2, and stop a whole category of
confused bug report.

## Background

Users will bring the wrong region, a bad dump, a different revision, a
re-release, or a file that is not the game. If your pipeline consumes that
silently, they get a crash a thousand lines later and file an issue about
your recompiler.

A good check tells them three things:

```
Expected: Rev A (US), SHA-256 3f9a...
Found:    Rev B (EU), SHA-256 71c4...
This project targets Rev A. Rev B has different function addresses
and the manifest hints will not apply.
```

**And it does not refuse to proceed.** Accept the input, warn loudly, and
record what you used -- an unknown revision is often worth trying, and the
user should know that is what they are doing.

## Your Task

Implement in `verify.py`:

- `hash_data(data)` -- SHA-256.
- `identify(data, known)` -- which known revision is this?
- `check(data, known, target)` -- the verdict plus a message.
- `provenance(...)` -- the record Module 33 section 6 asks for.

## The Design Rule

`check` returns a verdict of `match`, `known_mismatch` or `unknown`, and a
message. **None of them is a refusal.** A tool that refuses to run on an
unrecognised dump cannot be used to investigate an unrecognised dump.
