# Module 44: Whole-Program Optimization

This module closes Unit 11 with the techniques that work on the program as a whole rather
than on individual functions — and with the one that matters most in recompilation and
almost nowhere else: **not compiling the majority of your program at all.**

---

## 1. Compile Less

The number from Module 28, restated because it drives everything here:
`wormsrevolution` lifted **88,816 functions**; the reachable game needs **444**.

Over 99% of the compiled output is never executed. That is not a quirk of one title — it
is the normal shape of a commercial binary, which carries statically linked libraries, dead
branches, unshipped debug paths, and content the build never reaches.

The consequences compound:

| Cost | Why it hurts |
|---|---|
| Compile time | Module 41 §5 — 30 minutes for 114 MB of C, or 2 GB that may not build at all |
| Binary size | `ducktales` at **1.65 GB** |
| Instruction cache | hot functions scattered through a binary sized for 200× the live code |
| Link time | the linker resolves every one of them |
| Your attention | every generated function is something you might debug |

### How to find the live set

**Reachability from the entry point.** Lab 32's algorithm: walk the call graph from the
entry point and keep what you reach. Sound in principle and defeated in practice by
indirect calls — you cannot statically know every target (Module 14), so a naive
reachability pass will prune something the game reaches through a vtable.

**Runtime observation.** Run the game, log which functions executed, keep those. Exactly
Module 33's argument that a logged branch target is an *observation* while a pointer-shaped
integer is a *guess*. `gb-recompiled`'s trace capture already produces this data.

**Both, conservatively.** Union of statically-reachable and observed, and keep a trap stub
for everything else so that a mistake is loud rather than silent.

### Trap stubs make pruning safe

Module 34's pattern, and it is what makes aggressive pruning a reasonable thing to do.
`lttp-recompiled` emits **7,331 stubs plus 833 trap stubs** for unresolved targets, so the
program links, runs, and tells you *which* pruned function actually mattered.

That converts the risk from "the game crashes mysteriously six months later" into "the
program prints the address of the one function I should not have removed." Prune
aggressively, trap loudly, iterate.

---

## 2. Link-Time Optimization

LTO lets the optimiser work across translation units, which matters here because your
generated code is split into many files for build-time reasons (Module 34) and the
resulting boundaries are arbitrary.

What it buys on recompiled code:

- **Inlining memory accessors across files.** The big one. Your `bus_read8` lives in the
  runtime and is called from every generated file; without LTO it stays a call.
- **Cross-file dead code elimination**, which is §1 done by the toolchain.
- **Constant propagation into the runtime**, so a shim called only with one argument value
  specialises.

The cost is brutal at this scale. LTO on 231 MB of C++ can take hours and a lot of memory.

**The pragmatic answer: LTO the runtime, not the generated code.** The runtime is where
the hot hand-written code lives (Module 41 §3), it is small, and it is where
cross-function optimisation pays. Compile the generated code with modest optimisation and
let the memory accessors be inlined via headers rather than via LTO.

---

## 3. Profile-Guided Optimization

PGO is a better fit for recompiled code than LTO, because the property it exploits — a tiny
hot fraction and a vast cold remainder — is exactly §1's 444-of-88,816.

With a profile, the compiler will lay out branches for the common case, group hot functions
together, and stop wasting effort on cold ones. The layout effect is the valuable part
here, for the cache reason in Module 43 §4.

**Getting a representative profile is the hard part**, and it is the same problem as
Module 39's: whatever you happened to play becomes what the compiler optimises for. A
recorded playthrough that touches menus, gameplay, loading and pause screens is worth far
more than a boot-and-quit.

**Re-generate the profile when the game changes**, or you are optimising for a build that
no longer exists.

---

## 4. Function Ordering

Cheaper than PGO and most of the benefit for the cache problem.

Given a list of functions in the order they were first executed, or ranked by call count,
pass it to the linker as an ordering file and it will lay them out contiguously. Hot
functions end up on the same pages and in the same cache lines instead of scattered through
a multi-hundred-megabyte binary.

You already have the data: it is the same execution trace that Module 33 uses for entry
point discovery, Module 38 uses as an oracle, and §1 uses for liveness. **One recorded
playthrough feeds four different things** — record it once, keep it forever, and version it
with the project.

---

## 5. What the C Compiler Already Does for You

A reminder before you build anything clever, because generated code makes people
over-estimate how much hand-optimisation it needs.

**Dead flag computation disappears.** The standard worry about lifted code is that every
instruction computes flags nobody reads. Within a basic block the compiler sees the flag
variable written twice with no read between, and deletes the first. This is why Module 7
argues an IR is not worth building *for optimisation* — the C compiler is already a very
good optimiser and your verbose output is exactly the kind of input it handles well.

**Redundant loads fold**, provided you have not made every access `volatile` (Module 43
§5).

**Register allocation works**, including on `vr[128]`-style arrays, within a function.

What it cannot do:

- See across your memory layer, unless the accessor is inlined.
- Know that two guest addresses never alias.
- Remove work that is dead across a whole *function*, when the flag is a global.

That last one is the argument for keeping CPU state in a struct passed by pointer rather
than in globals: it gives the optimiser a scope to reason within.

---

## 6. Measuring, and Not Fooling Yourself

Every technique here should be justified by a measurement, and Module 37's standard applies
unchanged: **a speedup you cannot re-derive by running one command is not a speedup.**

Specific traps in this area:

**Benchmark a real workload.** A boot-to-title benchmark measures loading, not gameplay,
and the two have entirely different hot sets.

**Report the percentile, not the average.** For a game the question is not mean frame time,
it is whether any frame missed its deadline. A build with a better average and a worse 99th
percentile is a worse build.

**Check correctness after every optimisation.** Everything in this module changes what code
exists and where it lives. Module 38's differential test and Module 39's regression corpus
are what make aggressive optimisation safe, and pruning without trap stubs and a regression
suite is how you ship a game that crashes in chapter four.

---

## Labs

- **Lab 78** -- Prune and trap: compute a live function set from an execution trace, emit
  trap stubs for everything else, and report the reduction in function count, binary size
  and build time. Then find a pruned-but-needed function by running the game until a trap
  fires.
- **Lab 79** -- Function ordering: generate a linker ordering file from an execution trace,
  rebuild, and measure the change in instruction cache misses and frame time percentiles.

---

**Unit 11 Capstone Lab (Lab 80)**: Profile a recompiled title, identify its ten hottest
functions, apply the targeted optimisations this unit describes, and produce a before/after
report with a re-runnable measurement command and a differential test showing behaviour did
not change.

---

**Next: [Module 45 -- Legal Considerations](../../unit-12-shipping/module-45-legal/lecture.md)**
