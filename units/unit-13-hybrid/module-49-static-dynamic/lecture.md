# Module 49: Static and Dynamic, Together

Semester 1 drew a clean line: emulators translate at runtime, static recompilers translate
ahead of time. That line was useful for learning and it is not where the working systems
sit.

Almost every project in this course's reference corpus is a hybrid, and several are hybrids
whose READMEs claim they are not. This module is about the design space between the two
extremes, how to choose a point in it deliberately, and what you owe your users once you
have.

---

## 1. The Spectrum

| Design | Who executes the guest | Example |
|---|---|---|
| Pure interpreter | interpreter, always | any simple emulator |
| Dynamic recompiler (JIT) | translated code, translated on demand | most modern emulators |
| **Interception** | emulator, *except* where native code is registered | `snesrecomp`, `gbarecomp` |
| **Static + interpreter fallback** | native code, *except* unresolved targets | `gb-recompiled` |
| **Static + tolerant dispatch** | native code; misses return zero | `xboxrecomp` |
| Pure static | native code, always | `tamarecomp` |

The middle four are all "static recompilation" in ordinary conversation. They have very
different properties, and Module 37 §3 showed that the difference decides what a working
screenshot proves.

---

## 2. Interception: Start With Everything Working

The design from Modules 11 and 12. An emulator runs the game; a hook fires before each
instruction; if a native function is registered at that address, it runs instead.

`gbarecomp`'s `interception.c` hooks `ARMSetRecompHook`. `snesrecomp`'s `recomp_interp.c`
installs `g_cpuRecompHook` inside LakeSnes's timed frame. Module 11's `mk` exposes it as
`SMK_SHELLS=1`.

**Why this is a genuinely good design:**

- The game is playable on day one, which changes how a project feels for its whole life.
- Every commit still boots. There is never a six-month window where nothing runs.
- A wrong function can be deleted and the emulator covers it while you think.
- You get a per-function oracle for free (Module 38 §2).

**What it costs:**

- You keep the emulator, so you keep its licence (Module 45 §3) and its performance floor.
- The hook fires on *every instruction*, so you pay dispatch on the interpreted path.
- And the thing Module 37 insists on: **"it works" stops being evidence.** With
  `recomp_interp_set_enabled(true)`, a build with zero registered functions plays the game
  flawlessly.

**So the design owes you instrumentation.** Count registered functions, count hook hits,
count fallbacks, and publish all three. `gbarecomp`'s `interception.c` already has
`successful` and `failed` counters; they just are not in the README.

---

## 3. Static With a Fallback: Start With Nothing Working

The mirror image. Native code executes; something catches what static analysis could not
resolve.

The fallback choices, from the corpus:

**A real interpreter.** `gb-recompiled` ships a 781-line SM83 interpreter reached via
`gb_interpret(ctx, addr)` for "uncompiled code." Correct for any target, and you must write
and maintain a second implementation of the ISA — which Module 38 §2 argues you want
anyway, as your oracle.

**Return zero and continue.** `xboxrecomp`'s `RECOMP_ICALL` (Module 14): a miss pops the
dummy return address, sets `eax = 0`, and carries on. No second implementation, and it is
wrong — deliberately, on the bet that unresolved targets on that platform are mostly
garbage vtable pointers rather than real code.

**Trap loudly.** `lttp-recompiled` emits 833 trap stubs. The program links and tells you
which unresolved target actually mattered.

The choice follows from what your unresolved set *is*, which is the Module 55 §3
measurement: if they are mostly corrupted pointers, tolerance is right; if they are real
code you failed to find, you need an interpreter or better discovery.

---

## 4. Runtime Information Feeding Static Analysis

The most productive hybrid in practice is not about execution at all. It is using runtime
observation to improve the *static* result, and this course has hit it four times.

**Trace-guided discovery.** `gb-recompiled` runs the ROM under PyBoy, logs every executed
`(bank, PC)`, and feeds them back as entry points via `--use-trace`.

**Runtime-harvested hints.** Module 14's `civrev`: 301 pointer-scan hints made the build
worse; **one boot** with a tolerant dispatch scaffold that logged unregistered targets
produced 21 addresses, all real. Final count 24, down from 301.

**Liveness for pruning.** Module 44 §1: an execution trace tells you which of 88,816
functions are among the 444 that matter.

**Function ordering.** Module 44 §4, same trace.

That is four uses of one artifact. **Record a playthrough once, keep it forever, version it
with the project.** It is the highest-value file in a recompilation repository and most
projects never make one.

This is the same idea as BinRec [Altinay et al., EuroSys 2020], which uses dynamic traces to
guide static lifting. The academic framing and the practical one converge: **an observation
beats a guess** (Module 33 §3).

---

## 5. JIT as a Fallback

The option nobody in this corpus took, worth understanding so you can reject it knowingly.

Instead of interpreting unresolved targets, translate them at runtime and cache. You get
native speed on code static analysis missed, and self-modifying and dynamically generated
code becomes possible.

The costs are large: a second code generator, a host-specific backend, W^X handling, and a
substantial jump in project size. You are now maintaining a JIT *and* a static recompiler.

It becomes attractive when a meaningful fraction of execution is in code you cannot resolve
statically — dynamically generated code, heavy self-modification (Module 56 §6's
self-modifying Z80 case), or a plugin architecture. For a console game where static
discovery reaches the high nineties, it is a great deal of machinery for the last fraction
of a percent, and an interpreter is the right answer.

---

## 6. Choosing, and Then Saying So

Decide from your measurements, not your preferences:

| If | Then |
|---|---|
| A good open emulator exists with a compatible licence | interception — playable immediately |
| Unresolved targets are mostly garbage pointers | static with tolerant dispatch |
| Unresolved targets are real code | static with an interpreter |
| Nearly everything resolves statically | pure static (Module 53) |
| Significant execution is in generated code | consider a JIT, knowing the cost |

Then write it down. The corpus's clearest failure is not a bad design choice — it is a good
design choice described as something else. `gbarecomp`'s *"No emulator runs underneath"* is
the README of a perfectly reasonable interception design, claiming to be a different
architecture.

A README that says **"recompiled functions run on an mGBA host; 1,240 registered, 3 falling
back"** is both more honest and more impressive, because the numbers are real.

---

## 7. Migration Is a Design, Not an Accident

The strongest argument for hybrids is that they give you a *path*, and Module 11's `mk` is
the worked example: real-frame mode by default, `RECOMP_PATCH` functions swapped in one at a
time, auto-registering at static-init so adding one is a one-line change.

A sane progression:

1. **Interception**, with the emulator doing everything. Playable, zero native code.
2. **Move functions across**, hottest or most-interesting first. Still playable throughout.
3. **Measure the crossover** — the fraction of execution that is native. This is your real
   progress metric, and it is the number Module 37 says to publish.
4. **Flip the default** once the native path is complete enough, keeping the emulator as
   the oracle.
5. **Drop the emulator**, if you ever fully resolve discovery — and keep the interpreter.

Each stage is shippable. Compare with an all-or-nothing bring-up (Modules 27, 28, 30) where
nothing runs until nearly everything is lifted and a single bad function is a crash in a
40,000-function binary.

**If your platform has a good open emulator, there is very little reason to start any other
way.**

---

## Labs

- **Lab 99** -- Instrument a hybrid: add registered/hit/fallback counters to an
  interception-based project, display them live, and report what fraction of executed
  instructions ran as native code.
- **Lab 100** -- Migration ladder: take an interception project and move a measured 10% of
  executed instructions to native code, keeping the game playable at every commit, and plot
  the crossover metric over time.

---

**Next: [Module 50 -- Binary Rewriting and Patching](../module-50-binary-rewriting/lecture.md)**
