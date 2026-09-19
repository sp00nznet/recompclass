# Lab 91: Stack to Locals

## Objective

Implement Module 54's central trick, and the corpus check that proves it.

## Background

From `newtonrecomp`:

> NewtonScript is a stack VM, but **a recompiler that emits a runtime stack
> array and a `sp` is just an interpreter with extra steps.** The stack depth
> at every pc is statically determined, so each stack slot becomes a plain C
> local (`s[0]`, `s[1]`, ...) with no pushing or popping at run time.

It generalises to every stack VM -- JVM, CLR, p-code, Forth. **Stack depth
is a static property.**

And the verification is free: a stack VM has an invariant -- depth must
balance at every merge point and at return -- that you can check **without
running anything**, across thousands of programs.

## Your Task

Implement in `stacklocals.py`:

- `compute_depths(program)` -- depth at every pc, following branches.
- `verify_balance(program)` -- the corpus check.
- `emit(program)` -- C using numbered locals.
- `max_depth(depths)` -- how many locals to declare.

## Where This Earns Its Keep

`verify_balance` is what catches Module 54's `07 00 07` escape bug: a
misparse produces *plausible instructions*, so the code looks fine and the
stack does not balance.
