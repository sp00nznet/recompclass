# Lab 70: Timing Regression Test

## Objective

Build the timing check from Module 40 section 7, and demonstrate it catching
a bug that content-only comparison misses.

## Background

> **Compare frame numbers, not just frame contents.** A frame-hash
> comparison that ignores *which* frame a hash appeared on will not notice
> that your build reached the title screen in 4 frames instead of 180.

That is exactly the `mariopaint` bug, and it is invisible to a set-based
comparison: every expected frame appeared, just far too early.

## Your Task

Implement in `timingtest.py`:

- `Timeline` -- records (frame, state) observations.
- `compare_content(a, b)` -- the weak check: same states, any order.
- `compare_timeline(a, b, tolerance)` -- the real check: same states, same
  frames, within tolerance.
- `assert_reaches(timeline, state, frame, tolerance)` -- a single milestone.

## What You Must Demonstrate

A test where `compare_content` **passes** and `compare_timeline` **fails**.
That pair is the whole point of the lab: it is the evidence that your old
check was not checking what you thought.
