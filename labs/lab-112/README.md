# Lab 112: Auto-Registration

## Objective

Build the ergonomic decision Module 58 section 4 calls the best in the
corpus, and get the modding hook for free.

## Background

`snesrecomp`'s `recomp_patch.h`:

```c
RECOMP_PATCH(smk_80FF70, 0x80FF70) { ... }
```

> auto-registers it in the snesrecomp dispatch table at its original SNES
> 24-bit bank:address, before `main()` runs. **No central registration list
> needed.**

A central list is a merge conflict on every contribution, a thing to forget,
and a reason for a newcomer's first patch not to work.

And the bonus, from Module 47 section 3:

> **Mod / override pattern:** link a second `.obj` that defines another
> `RECOMP_PATCH` at the same address with a different function name. **The
> last constructor to run wins**, so put mod objects after the original.

## Your Task

Implement in `autoreg.py`:

- `Registry` -- registration, lookup, and override tracking.
- `register(addr, name, func)` -- last registration wins.
- `overrides()` -- which addresses were overridden, and by what.
- `emit_registration(name, addr)` -- the generated C.

## Why Track Overrides

"Last wins" is only usable if you can see it happened. A silent override is
a debugging session where your breakpoint never fires.
