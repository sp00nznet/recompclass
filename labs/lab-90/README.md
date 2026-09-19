# Lab 90: Is It Bytecode?

## Objective

Answer Module 54's first question -- *which program am I recompiling?* --
in ten minutes, from two numbers.

## Background

`worldempire` is the worked example:

```
EMPIRE.EXE   411,785 bytes   NE, 15 segments, 114,025 bytes of "code"
             imported modules: VBRUN300     <- and nothing else
             relocations: 14 total, 13 of them internal
```

**One imported module.** *"A native Windows program cannot draw a pixel or
open a window without KERNEL, USER and GDI. This one never calls them."*

**Fourteen relocations across 114 KB.** *"The Even More Incredible Machine
has 4,743 across 197 KB in the folder next door. Fourteen means almost
nothing in those segments is machine code at all."*

**Relocation density is a proxy for "is this really code."** Machine code is
full of absolute addresses needing fixup; a blob of p-code is not.

## Your Task

Implement in `bytecheck.py`:

- `relocation_density(binary)` -- relocations per KB of code.
- `is_runtime_only(binary, system_modules)` -- imports nothing but a runtime.
- `classify(binary, reference)` -- native / bytecode / uncertain, with
  reasons.

## Report Reasons, Not Just a Verdict

`classify` must return **why**. A verdict you cannot argue with is a verdict
you cannot check, and Module 37 is unambiguous about that.
