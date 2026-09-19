# Module 41: Profiling Recompiled Binaries

Static recompilation's headline claim is performance: native code, no interpreter, no
dispatch overhead. That claim is usually true and it is not automatic, and the ways it
fails are specific to generated code.

This module is about measuring before optimising, which matters more here than in ordinary
software for one reason: **your intuitions about where the time goes were formed on
hand-written code, and this is not hand-written code.**

---

## 1. The Shape of Generated Code

Three properties change what a profile looks like.

**It is enormous.** Module 34's numbers: `civrev` produces 231 MB of C++ from 40,067
functions; `ducktales` produces roughly 2 GB and a **1.65 GB executable**;
`LinksAwakening` is about 4.2 million lines. A binary that size has consequences for
instruction cache and page faults that a 5 MB program never has.

**Most of it never runs.** This is the number to internalise, from Module 28's
`wormsrevolution`: codegen lifted **88,816 functions**, and the entire reachable game
needs **444 registered functions**.

Sit with that ratio. Over 99% of what you compiled is never executed — unreferenced
library code, dead branches, content paths this build never touches. Your optimiser's
effort is almost entirely wasted, your binary is almost entirely ballast, and your profile
will be concentrated in a tiny fraction of the code.

**It is uniform.** Hand-written code has hot loops and structure a profiler's call graph
makes sense of. Generated code is thousands of near-identical functions with mechanical
names. `sub_0082A1C0` tells you nothing, which is why Module 33 argues so hard for
importing symbols from a decompilation project — it is a debugging *and* a profiling
concern.

---

## 2. Measure the Right Baseline

Before optimising, decide what "fast enough" means. There are three defensible baselines
and they give very different answers.

| Baseline | Question it answers |
|---|---|
| Original hardware | does it run at the speed the game was designed for? |
| A good emulator | did recompiling actually buy anything? |
| Wall-clock target (60 fps) | is it playable? |

The second is the one that tests the premise. If your recompiled build is not
comfortably faster than a mature emulator of the same system, something is wrong with
your design, not your optimiser — you have probably reintroduced per-instruction
dispatch somewhere (Modules 11 and 12 show exactly how that happens by accident).

The first is worth stating because it bounds the problem. A Game Boy game needs a 4 MHz
CPU's worth of work per frame. Your host does roughly a thousand times that. You have
enormous headroom, and the right response to "it is slow" on an 8-bit target is to find
the mistake rather than to micro-optimise.

---

## 3. Where the Time Actually Goes

In practice, in rough order of how often they dominate:

**The runtime, not the lifted code.** Your memory access functions, your graphics
translation, your audio mixing. Module 15's point — the runtime is the hard part — is also
a performance claim. A `bus_read8` that does a switch over address ranges on every access
will outweigh all your lifted arithmetic combined.

**Memory access indirection.** Every guest load and store goes through your function. That
is Module 43.

**Indirect call dispatch.** Module 14's table lookup, on every indirect call.
`xboxrecomp`'s own doc does this arithmetic honestly: binary search over 22,097 entries is
at most 15 comparisons, and *"at ~120 ICALLs per second, this is negligible overhead."*
**Measure your call rate before optimising your dispatch** — 120 per second and 120,000
per second are different problems, and the first one is not a problem.

**Flag computation.** Every lifted instruction computing flags nobody reads. Module 19
covers why the C compiler deletes most of this for you, and Module 44 covers when it
cannot.

**Graphics translation.** Usually dominant once the game actually renders. `3dsnes` is
blunt that *"the renderer is a CPU rasterizer, so framerate is the main cost."*

Note that only two of those five live in the generated code. **Profile the whole program,
not the lifted half.**

---

## 4. Tooling, and Its One Real Problem

`perf` on Linux, VTune, Instruments on macOS, and the Visual Studio profiler all work
normally on a recompiled binary — it is just a native executable. The friction is symbols.

**Make the generator emit real symbol names.** If you imported symbols (Module 33),
`Player_Init` beats `sub_80056780` in every profile you will ever read. If you did not,
emit at least the guest address consistently so you can map back.

**Keep frame pointers on for profiling builds.** Deep generated call chains produce
useless stacks without them, and "the time is in `bus_read8`" is not actionable when you
cannot see who called it.

**Consider sampling your own frame loop.** Module 30's spin watchdog samples the PC and
resolves it through the guest symbol table. The same mechanism is a serviceable profiler:
sample periodically, resolve to a *guest* function, and you get a profile in terms the
game's own structure — which a host profiler cannot give you.

**Beware attributing everything to one inlined helper.** `MEM_W`-style macros inline into
thousands of call sites; profilers may fold them together or scatter them, and both are
misleading. Check with a build that keeps them out of line.

---

## 5. Build Time Is a Performance Problem Too

Unusually for a performance module, the cost that will actually slow your project down is
the build.

`lttp-recompiled` reports ~30 minutes for 114 MB of C under MSVC `/O1 /MP`. `ducktales`
produces 2 GB of C++. At that scale:

- A full rebuild for a one-line shim change is unacceptable, so **the runtime and the
  generated code must be separate compilation domains** (Module 35).
- Module 34's "keep the translation unit split stable" is a performance requirement: an
  unstable split means every incremental build is a full build.
- `/O2` on 2 GB of generated C++ may simply not finish. Consider optimising the runtime
  aggressively and the generated code modestly — which is close to the right answer anyway,
  given §3.

---

## 6. A Workable Order

1. **Check the premise.** Are you slower than an emulator? If so, stop and find the
   structural mistake.
2. **Profile the whole binary**, runtime included, on a real workload.
3. **Fix the runtime hot spots first.** They are hand-written, comprehensible, and usually
   dominant.
4. **Only then look at generated code**, and expect the answer to be memory access
   (Module 43) or SIMD (Module 42) rather than anything subtle.
5. **Reduce what you compile at all.** Given 444 of 88,816, dead function elimination is
   the highest-leverage thing in Unit 11, and it is Module 44.

And measure after every step. Module 37's standard applies to performance claims too: a
speedup you cannot re-derive by running one command is not a speedup, it is an impression.

---

## Labs

- **Lab 72** -- Profile a recompiled binary: build with symbols and frame pointers, profile
  a real workload, and produce a ranked breakdown separating runtime, generated code,
  dispatch, and graphics. Report what fraction of lifted functions executed at all.
- **Lab 73** -- Guest-level sampling profiler: sample the PC periodically, resolve each
  sample to a guest function through your symbol table, and produce a profile in the
  game's own terms rather than the host's.

---

**Next: [Module 42 -- SIMD for Lifted Code](../module-42-simd/lecture.md)**
