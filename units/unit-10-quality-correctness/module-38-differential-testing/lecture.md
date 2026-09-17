# Module 38: Differential Testing and Oracles

Module 37 ended on a question: what would your evidence look like if the thing you believe
were false?

Differential testing is the systematic answer. You have two implementations of the same
program — the original and yours — and any disagreement between them is a bug with a known
location. It is the single most powerful technique in this field, and the reason is
structural: **recompilation is the one kind of software engineering where a perfect
reference implementation always exists.** The original binary runs. You can watch it.

Most projects reach for this far too late. This module is about reaching for it first.

---

## 1. Build the Oracle Before the Lifter

The instinct is to write the recompiler, get something running, and then figure out how to
check it. Invert that.

Look at the first commits of [encarta](https://github.com/sp00nznet/encarta), the
best-documented debugging campaign in this corpus. They are not lifting work:

```
Add DECO_32 oracle: perfect FTC color decode + golden trace harness
Add recomp runtime (cpu.h) + first validated lift (VLC reader)
Add automated x86->C lifter (lift.py), validated on VLC reader
```

The oracle came first. The original DLL is loaded and driven directly to produce
known-correct output and a golden trace, and only then does a lifter appear — validated
against one function, a bitstream reader small enough to check by hand.

Two rules, in order:

**You cannot differentially test without a reference, and the reference you want is the
original binary running — not your beliefs about it.** Documentation is wrong, your
reading of the disassembly is wrong, and the hardware does what it does.

**Prove the lifter on one function before pointing it at thousands.** `encarta` validated
on a VLC reader before running at 7,326 functions. If the mechanism is broken you want to
find out at a scale where you can still read the output.

---

## 2. Four Kinds of Oracle

### The interpreter you wrote yourself

The cheapest and most controllable. `vic20recomp` lists the "interpreter oracle" as one of
its core front-end components, alongside the decoder, the flag-correct ALU, the analyzer
and the C emitter — the same battle-tested 6502 front end shared with `apple2recomp`.

The design consequence from Module 34 bears repeating: **generate the lifter and the
interpreter from the same decode table.** It is a fraction of the work if you plan for it
and a rewrite if you do not. It also means a decode bug affects both identically and will
not show up as a divergence, which is a real limitation — this oracle tests your *lifting*,
not your *decoding*.

### The emulator you are hosted on

If your design is emulator-hosted (Modules 11 and 12), the oracle is already linked into
your process and you get instruction-level granularity for free.

`mariopaint` exposes it as two environment variables:

| Lever | Effect |
|---|---|
| `MP_REALFRAME=1` | run the genuine ROM through LakeSnes's cycle-accurate frame — no recompiled code participates |
| `MP_INTERP_FUNCS="018000,0087EE"` | hand *specific* recompiled functions back to the interpreter |

The first is a whole-program oracle: *"capture the same frame both ways and diff."* The
second is a per-function A/B switch, and its own comment names the use case exactly:
*"This is the A/B lever for 'is our translation of X wrong?': run it interpreted and see if
the symptom goes away."*

Note the implementation cost. `MP_INTERP_FUNCS` works by registering `NULL` at an address
so the dispatch lookup misses and falls through to the original code. That is a few lines,
it needs no rebuild, and it turns "something in our 8,000 lines is wrong" into a bisection
you drive from a shell.

**If your design has an interpreter or emulator anywhere in it, you already have an
oracle — you just have to expose the switch.** This is the compensation owed for the
evidence problems in Module 37.

### The original binary, running

For PC targets the original executable runs on your machine. `encarta`'s `DECO_32 oracle`
loads the real DLL and drives its exports directly. `xwa` dumps process memory after
SafeDisc decrypts itself. You are not emulating anything — you are calling the real thing
and recording what it returns.

### A third-party emulator

`gb-recompiled` captures ground truth under **PyBoy**: run the ROM, log every `(bank, PC)`
that actually executes (`tools/capture_ground_truth.py`), and use that two ways — as entry
points to seed the recompiler (`--use-trace`), and as a coverage audit showing which
executed instructions your build never lifted. The recompiled binary emits a matching
trace with `--trace-entries`, so the two are directly diffable.

N64Recomp compares against **Ares** at the frame level rather than the instruction level.

---

## 3. Choosing Your Comparison Point

The single most important design decision, because it determines what you can find and
what it costs.

| Level | Compare | Good for | Cost |
|---|---|---|---|
| Instruction | register + flag state per instruction | lifter semantics | enormous traces, only viable on simple CPUs |
| Function | args in / return + memory writes out | isolating one bad lift | needs a call boundary you can intercept |
| API | the sequence of shim calls | runtime and OS bugs | cheap, and catches a lot |
| Frame | framebuffer hash | end-to-end regression | says *that* something broke, not *what* |
| Output artifact | decoded bytes | codecs, decompressors, parsers | exact, when your target has one |

### Instruction level is only for simple CPUs

`gb-recompiled` can do full state comparison because the SM83 has no pipeline, no
out-of-order execution and no caches. Same input, same trace, every time.

N64Recomp explicitly does **not**, and the reasoning generalises: the N64's MIPS pipeline
and the recompiled x86 have fundamentally different execution patterns, so the traces
*always* differ. Comparing them produces noise, not signal.

The rule: **compare at the highest level where the two implementations are supposed to
agree exactly.** Above that you get false negatives; below it you get false positives.

### The output-artifact level is underrated

If any part of your target decodes something — a video codec, an audio decoder, a
decompressor, a file parser — that component has a *byte-exact* correctness criterion, and
it is the best test you will ever get.

`encarta` ended its codec campaign with:

```
IR32: the recompiled Indeo 3 decoder is byte-exact - 64 of 64 frames
```

preceded by the partial result `100% byte-exact over 168 of 216 columns`. That is rung 8
on Module 37's ladder, and it is available because a codec has a defined answer. Look for
these components in your target and attack them first — they will validate your lifter far
more sharply than any amount of watching a title screen.

---

## 4. Bisecting the Lifted Set

Here is the single most transferable technique in this course.

When the program misbehaves and you have thousands of lifted functions, you do not read
generated code looking for the bug. `encarta`:

```
Add LIFT_LO/LIFT_HI: bisect the lifted set to find a bad lift
```

A range filter. Functions inside `[LIFT_LO, LIFT_HI]` run lifted; everything else runs as
the original. Then binary search the range. **`git bisect`, applied to the address space.**
Roughly a dozen runs isolates one bad function out of thousands, and each run requires no
thought — only "did the symptom happen?"

This works at every granularity:

- **Range-based** (`LIFT_LO`/`LIFT_HI`) — needs a global switch in your dispatch
- **Per-function** (`MP_INTERP_FUNCS`) — needs a function table you can poke `NULL` into
- **Per-module** — if your generated code is split into translation units, link some from
  lifted output and some from the original

The prerequisite is that **both implementations must be simultaneously available and
switchable at runtime.** Design for that from the first commit. If switching requires a
30-minute rebuild of 231 MB of C++, you will not do it, and you will read generated
assembly instead.

---

## 5. Tripwires for Silent Corruption

Divergence you can see is the easy case. The dangerous bugs corrupt state and surface
somewhere else, minutes later.

`encarta` again:

```
Add R2L_HEAPCHECK diagnostic (HeapValidate after each real->lifted call)
```

Validate the heap after *every* call from original code into lifted code. If a lifted
function corrupts the heap, you find out at the call that did it — not three minutes later
in an unrelated allocator.

Generalise: after each boundary crossing, assert whatever invariant is cheap and total.

- Heap integrity (`HeapValidate`, or your allocator's own check)
- Stack pointer returned to its expected value — catches Module 18's `KERNEL.197 was
  skewing the caller's stack` class of bug directly
- Callee-saved registers preserved per the ABI
- Guard bytes around guest memory regions intact

These are expensive and that is fine. Run them under a debug flag, all the time, until the
project stabilises.

### The related discipline: stop failures from being silent

Two `encarta` commits, both the same bug class:

```
IR32: segment 3 to 92.5%, and stop reporting unhandled as zero
IR32: segment 3 to 81% - stop trusting the linear sweep
IR32: the decode core is 32-bit; measure bitness instead of guessing
```

Returning zero for an unhandled case makes a broken decoder look like a working one that
produces black frames. **Any time your harness has a default, ask what it is hiding.**

This is the same mechanism as Module 37's 2,204 return-zero stubs, seen from the testing
side rather than the claims side.

---

## 6. A Campaign, Start to Finish

The `IR32` commit run in `encarta` — statically recompiling the Indeo 3 video codec from a
16-bit NE DLL until it was byte-exact — is worth reading in full. Here is its arc.

**Reconnaissance, and correcting the first diagnosis:**

```
indeo: IR32.DLL lift feasibility - 99.21% decode coverage
indeo: correct the decode-gap diagnosis - it was FS/GS prefixes
indeo: classify segments before lifting - segment 40 is a table
indeo: resolve segment 3 jump tables - reachable code 5.8% -> 19.3%
```

**Getting it to run at all:**

```
IR32: a code segment returns - segment 13 is data
IR32: an NE 32-bit runtime, and the lifted decode core runs
IR32: lift the 16-bit half and link both together
IR32: the driver loads - DRV_LOAD, DRV_ENABLE and DRV_OPEN all succeed
IR32: ICM_DECOMPRESS runs against a real frame; no pixels yet
```

**The false victory, and the retraction one commit later:**

```
IR32: the lifted codec decodes - and the output format was the wrong question
IR32: retract "it decodes" - the buffers were copies of its own code
```

**Symptom-chasing — a week of it:**

```
IR32: string ops had no segment base; the fault is a far pointer used flat
IR32: the codec calls a copy of its own code segment
IR32: carry the caller's registers across the bridge
IR32: one working buffer is intact, the other is carpet-filled with 0x04
IR32: the 0x04 is decoded pixels, not a fill - and the loop overwrites state
IR32: caught it - the decode thunk writes pixels over its own plane table
IR32: 16-bit addresses wrap, they do not sign-extend - fault fixed
```

**The turn — differential testing enters, and the search space collapses:**

```
IR32: differential-test the lifted code against real x86
IR32: differential-test the 16-bit half too; instruction semantics are clean
IR32: the values are right, the addressing is wrong
IR32: KERNEL.197 was skewing the caller's stack, and locate the write path
```

**Done, precisely:**

```
IR32: the recompiled decoder decodes - 100% byte-exact over 168 of 216 columns
IR32: the recompiled Indeo 3 decoder is byte-exact - 64 of 64 frames
IR32: __AHINCR was never patched - the codec's own output is now the picture
```

### The lesson in the shape

Differential testing arrives *after* a week of symptom-chasing, and the commit that
matters most found no bug at all:

> `differential-test the 16-bit half too; **instruction semantics are clean**`

It **eliminated a whole layer from the search**. Proving the lifter correct meant the fault
had to be in addressing and memory layout — and the next three commits found it.

**Use differential testing to eliminate layers, not just to find bugs.** A clean result is
not a wasted run; it is the most valuable kind, because it permanently removes suspects.

The bug taxonomy that campaign produced is a checklist worth keeping:

| Bug | Class |
|---|---|
| string ops had no segment base | segmentation dropped during lifting |
| 16-bit addresses wrap, they do not sign-extend | wrong-width arithmetic semantics |
| carry the caller's registers across the bridge | ABI mismatch at the lifted/native boundary |
| KERNEL.197 was skewing the caller's stack | a shim with the wrong stack purge |
| decode thunk writes over its own plane table | correct code, wrong memory layout |
| `__AHINCR` was never patched | an unresolved loader fixup |

---

## 7. Make Re-Verification One Command

A late `encarta` commit, and the one that makes everything above durable:

```
One command that re-checks everything that works
```

Plus:

```
Differential validation: 818 -> 974 functions, and the new ones check memory
Make the leaf sweep deterministic; measure the callee policy
```

Three things in there worth naming.

**One command.** If re-verifying your claims is not a single command, your claims will rot.
This is Module 35's regression gate and Module 37's "can you re-derive it tonight" as the
same requirement.

**The validated set is a number that goes up, and it is the honest one.** 818 → 974
functions differentially validated is a completion metric that actually means something —
unlike a function count, which Module 37 showed is trivially inflatable.

**Determinism is a prerequisite.** "Make the leaf sweep deterministic" is not polish. A
non-deterministic validation run cannot distinguish a regression from noise, so it cannot
gate anything.

---

## Labs

- **Lab 62** -- Interpreter oracle: generate a lifter and a matching interpreter from one
  decode table, run both over a synthetic instruction stream, and report the first
  divergence with full register and flag state.
- **Lab 63** -- Bisect harness: add a `LIFT_LO`/`LIFT_HI`-style range switch to a
  recompiled project, then write a script that binary-searches the range to isolate a
  deliberately-broken function.
- **Lab 64** -- Boundary tripwires: instrument every original↔lifted call with heap
  validation, stack-pointer checks and callee-saved register assertions, and demonstrate
  each one catching an injected fault.

---

**Next: Module 39 -- Fuzzing and Divergence Detection** *(not yet written -- see [SYLLABUS.md](../../../SYLLABUS.md) for the outline)*
