# Module 39: Fuzzing and Divergence Detection

Module 38 gave you an oracle and a way to compare against it. This module is about the
input side of that equation: where the test cases come from.

The honest answer for most recompilation projects is "whatever the developer happened to
do while testing," and that is a bad answer for a specific reason — **you test the paths
you already believe work.** The bug is in the path you did not think of, and you will not
think of it by trying harder.

---

## 1. Why Fuzzing Fits This Problem Unusually Well

Fuzzing normally has a weak oracle. You feed a program random bytes and the only thing
you can detect is a crash, because nobody knows what the correct output was supposed to
be.

Recompilation inverts that. **You have a perfect oracle** (Module 38), so any input
where the two implementations disagree is a bug — no crash required, no specification
needed, no judgement call. That makes differential fuzzing far more productive here than
in most software, and it is badly under-used in this field.

The three ingredients:

| | |
|---|---|
| **Input** | something you can vary and replay deterministically |
| **Oracle** | the original binary, an interpreter, or an emulator |
| **Comparison** | a level at which both are supposed to agree exactly (Module 38 §3) |

---

## 2. What "Input" Means for a Game

This is the part people get stuck on. A game is not a function taking bytes. Its inputs
are:

**Controller state per frame.** The obvious one, and the most valuable. A sequence of
button states is a compact, replayable, deterministic input.

**Save data and settings.** A save file selects which code paths exist at all. Half the
game may be unreachable from a fresh save.

**Timing and interrupt arrival.** Usually the real source of divergence, and the hardest
to vary deliberately. Module 40 is about this.

**The ROM itself.** For *toolkit* testing rather than game testing, the input is the whole
binary — which is what makes corpus runs (§5) work.

**Synthetic instruction streams.** For lifter testing, generate random valid instruction
sequences and compare execution against your interpreter. This finds semantic bugs
directly and is the cheapest thing in this module to build.

### Start with synthetic instruction fuzzing

If you build one thing from this module, build this. It needs no game and no runtime:

1. Pick an instruction from your decode table.
2. Generate random operands and random starting register state.
3. Execute it in your interpreter and in your lifted code.
4. Compare all registers and flags.

That is a loop of maybe forty lines, and it will find the wrong-width arithmetic and
bad-flag bugs from Module 38's bug taxonomy before they ever reach a game. `vic20recomp`
and `apple2recomp` carry their "interpreter oracle" precisely so this is possible.

**Weight the generator toward the edges.** Uniform random operands almost never produce
`0x00`, `0xFF`, `0x7F`, `0x80`, or exact nibble boundaries — which is where flag bugs
live. Half your inputs should come from a table of interesting values.

---

## 3. Differential Fuzzing Against an Emulator

For whole-program testing, the emulator-hosted designs in Modules 11 and 12 hand you the
setup for free. `mariopaint`'s `MP_REALFRAME=1` runs the genuine ROM; without it, the
recompiled path runs. Same input, two implementations, one process.

A workable loop:

```
for seed in range(N):
    inputs = random_input_sequence(seed, frames=3600)
    a = run(mode="oracle",    inputs=inputs)      # emulator / interpreter
    b = run(mode="recompiled", inputs=inputs)
    if a.hashes != b.hashes:
        record(seed, first_differing_frame)
```

Three requirements, all of which have to be designed in rather than retrofitted:

**Determinism.** Same seed, same result, every run. If your runtime seeds a random number
generator from the clock, reads real time, or races two threads, you cannot fuzz it.
`encarta`'s commit `Make the leaf sweep deterministic` is the same requirement at a
smaller scale — a non-deterministic comparison cannot distinguish a regression from noise.

**A cheap comparison signal.** Hashing the framebuffer every frame is usually enough and
costs almost nothing. Add audio buffer hashes and the guest's own RAM if you can afford
it.

**Replay.** A failing seed must reproduce exactly, or you have found nothing.

### Random input is dumber and better than you expect

`gb-recompiled`'s ground-truth capture tool takes a `--random` flag and runs for a frame
count:

```
python3 tools/capture_ground_truth.py roms/game.gb --frames 3600 --random -o game.trace
```

Random button mashing for a minute reaches menus, pause screens, and state transitions
that a developer testing "does the game boot" never touches. It is not a substitute for
directed play, but it is close to free and it runs while you sleep.

---

## 4. Minimising a Divergence

A raw failing input is a 3,600-frame recording and a frame number. That is a lead, not a
bug report. Minimisation turns it into one.

**Truncate first.** If the divergence is at frame 2,150, everything after it is noise.
Cut there.

**Then bisect the input backwards.** Delete the first half of the input; does it still
diverge? This is the same move as `LIFT_LO`/`LIFT_HI` in Module 38, applied to inputs
rather than code, and it usually collapses thousands of frames into dozens.

**Then bisect the code.** Once the input is short, switch to Module 38's technique and
find *which function* diverges. Two nested bisections — one over inputs, one over the
address space — is the standard way to go from "something is wrong in a 40,000-function
binary" to a named function in an afternoon.

**Then narrow the comparison level.** Frame hashes tell you *that* something differs.
Re-run the minimised input comparing at function level (Module 38 §3) to find where.

---

## 5. Corpus Runs: Fuzzing the Toolkit

Everything above tests one program against one oracle. The other axis is running *many
inputs through the toolkit* — which is what Module 33's batch harness is for.

Two real examples of the shape:

- `gb-recompiled`: **1,592 of 1,609 ROMs** recompile successfully (98.94%). That number is
  about the recompiler's robustness across inputs, and you cannot get it without a corpus.
- `3dsnes`: **340 of 375 games (91%)** draw a real 3D scene, verified by an unattended run
  over the whole corpus, *"not by spot-checks."*

A corpus run finds a category of bug that single-target work cannot: the mapper you never
implemented, the header variant you assumed away, the instruction encoding only one game
uses. It also gives you a number that moves — and Module 37 argues that a number you can
re-derive tonight is the only kind worth publishing.

**Categorise the failures** (Module 33 §4). "17 ROMs failed" is not actionable. "11 failed
at codegen, 4 at compile, 2 linked but crashed" is three different tasks.

---

## 6. Triage: Ranking What You Found

A good fuzzing run produces more failures than you can fix, most of which are the same bug
wearing different hats.

**Deduplicate by cause, not by symptom.** Two crashes at the same address are one bug. The
cheapest fingerprint is the first differing function address plus the instruction that
diverged.

**Rank by reachability, not severity.** A divergence in a function the game calls every
frame outranks a spectacular crash in a code path reached by one optional item. Your
existing execution traces already tell you which is which.

**Separate "diverges" from "crashes."** They feel different and they are not equally
informative. A crash is loud and often shallow — a null vtable, a bad return address. A
quiet divergence in arithmetic is the one that corrupts a save file two hours later.

**Keep every reproducer forever.** Each minimised failing input becomes a regression test
(Module 35). This is how a fuzzing campaign compounds instead of evaporating: `encarta`'s
`Differential validation: 818 -> 974 functions` is a count of accumulated, permanently
re-checkable results.

---

## 7. What Fuzzing Will Not Find

Worth stating plainly so you do not over-trust a green run.

**Anything your oracle also gets wrong.** If you fuzz your lifter against your own
interpreter and both share a decode table, a decode bug is invisible to both. Module 38
§2 flags this; it is the main structural limit of a self-built oracle.

**Bugs behind an environment check.** Module 20's Diddy Kong Racing DRM reads hardware
registers that fail identically on every run, so no amount of input variation changes the
outcome. Fuzzing varies inputs; it does not vary the *environment*.

**Anything reached only through content you do not have.** A save file from late in the
game, a peripheral you have not implemented, a multiplayer session.

**Timing-dependent divergence, unless you fuzz timing.** Which is Module 40.

---

## Labs

- **Lab 65** -- Instruction fuzzer: generate random operands and register state for one
  ISA, execute in both your lifter and your interpreter, and report the first divergence
  with full state. Weight the generator toward boundary values and show that it finds
  bugs uniform random does not.
- **Lab 66** -- Divergence minimiser: take a long failing input sequence and shrink it to
  a minimal reproducer by truncation and backward bisection, then report the reduction
  ratio.
- **Lab 67** -- Triage tool: given a directory of failing reproducers, deduplicate them by
  first-divergence fingerprint and rank the surviving groups by how often the implicated
  function appears in a reference execution trace.

---

**Next: [Module 40 -- Audio and Timing Accuracy](../module-40-audio-timing/lecture.md)**
