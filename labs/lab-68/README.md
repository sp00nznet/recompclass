# Lab 68: Frame Driver

## Objective

Fix the bug that opens Module 40: a recompiled loop that finishes in
microseconds because nothing is advancing time any more.

## Background

From `mariopaint`'s `main.c`:

> `$018260` is the important one. The ROM's title loop has no frame sync in
> it at all -- it spins polling the mouse bytes and bails to the demo after
> `$800` idle iterations. **On hardware an NMI drives the frame underneath
> it**; interpreted here, it burns all 2048 iterations instantly with nothing
> drawn and no input possible, so the title screen flashed past invisibly.

The ROM's loop is correct. On real hardware it takes seconds, because a
vertical-blank NMI fires 60 times a second underneath it. Lift that loop and
the NMI does not exist unless you arranged for it.

> **The original program assumed something else was advancing time. In your
> build, nothing is, unless you build it.**

`tirecomp` solves it with a hook in the dispatch loop:

```c
uint64_t ti_cycles = 0;
void (*ti_frame_hook)(void) = 0;
...
        fn();
        ti_cycles++;
        if (ti_frame_hook) ti_frame_hook();
```

## Your Task

Implement in `framedrv.py`:

- `CycleClock` -- accumulates cycles and fires a frame at a threshold.
- `run_loop(...)` -- run a guest loop with the hook installed.
- `detect_impossible_speed(...)` -- flag a loop that finished far too fast.

## The Trap

A tight loop with no control transfers and no memory access never calls your
runtime and hangs. **Pick a hook point the guest cannot avoid** -- every
basic block, or every backward branch.
