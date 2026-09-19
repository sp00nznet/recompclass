# Module 53: Very Small Targets — 4-Bit CPUs and Whole-ROM Recompilation

Everything in Semesters 1 through 3 assumed a machine with bytes, a stack you can point
at, an address space too large to enumerate, and indirect calls you cannot fully resolve.

This module removes all four assumptions at once, and the interesting result is that
several of the field's hardest problems simply **stop existing**. Not become easier —
stop existing. Understanding exactly why is worth more than another console port, because
it tells you which of your difficulties are fundamental and which are consequences of
scale.

The worked example is [tamarecomp](https://github.com/sp00nznet/tamarecomp), which
recompiles the original Tamagotchi P1 — an **Epson E0C6S46**, a 4-bit microcontroller.

---

## 1. The Machine

```
CPU            E0C6200 core, 4-bit
ROM            6,144 words (0x1800) -- the entire address space
RAM            0x1000 nibbles, shared with display RAM and I/O
Oscillator     32,768 Hz
Registers      A, B (4-bit), X, Y (12-bit), SP
Interrupts     6 sources, two-word vectors, priority highest-address-first
```

Take a moment with "6,144 words is the entire address space." Every instruction in the
program can be enumerated. There is no dynamic loading, no bank switching, no memory
mapping, no possibility of code that is not in the ROM.

---

## 2. Nibbles, and a Design Decision Worth Copying

The first thing the guest's width changes is memory representation, and `tamarecomp`'s
header states its choice and its reasoning together:

> Nibbles are stored one per byte. The core is 4-bit; packing two per byte would save 2KB
> and cost a shift on every access, **on a machine that has gigabytes and did not have
> 2KB**.

That is Module 43's memory ladder in one sentence. The faithful representation packs two
nibbles per byte because the hardware did; the *useful* one spends 2 KB to make every
access a plain array index.

The general principle, which applies far beyond 4-bit machines: **reproduce the guest's
observable behaviour, not its storage economics.** The guest's constraints were about
1997 silicon. Yours are not.

---

## 3. One C Function for the Whole ROM

Here the small address space changes the codegen strategy completely. From the same
header:

> The recompiled ROM is one C function with a label per instruction word, so this holds
> only the architectural state — there is no instruction pointer to maintain except at a
> computed transfer, where `pc` is set and the generated dispatch takes over.

Not one C function per guest function. **One C function, 6,144 labels.** The emitter
reports `47567 lines from 6144 ROM words`.

What that buys:

```c
L_0546: /* A80  ADD A, A */
    t->cycles += 7;
    r = t->a + t->a;
    t->cf = r > 15;
    if (t->df && r > 9) { r += 6; t->cf = 1; }
    t->zf = (r & 0xF) == 0;
    t->a = r & 0xF;
    CHECK_BUDGET(0x0547);
```

- **Sequential instructions fall through with no branch at all.** No dispatch, no call, no
  return — the program counter is the C instruction pointer.
- **Direct jumps are `goto`.** A `CALL` becomes `goto L_0307;` after pushing a return
  address.
- Function boundaries — Module 34's recurring nightmare — are not needed. You never have
  to decide what a function is, because you never emit one.

And the result: *"Left to run flat out with no timers it does 64 million cycles in under a
second — roughly **2,000× the hardware's 32,768 Hz**."*

**When does this generalise?** When the whole address space fits in one C function your
compiler will accept. Thousands of labels is fine; millions is not. So this is the right
strategy for small embedded targets and arcade boards, and the wrong one for anything
Module 34 sized. Knowing both exist is the point.

---

## 4. The Paging Instruction That Compiles to Nothing

This is the module's best illustration of a guest mechanism dissolving at compile time.

The E0C6200 reaches its address space through `PSET`, which latches a page that the
*following* jump or call consumes. Classic paged-architecture design, and normally a
recompiler's problem — the target depends on runtime state.

Except the page is always an immediate. So:

> **`PSET` emits nothing at all** — all 162 of them stop being control flow and become
> compile-time facts.

```c
L_054B: /* 407  CALL 0x07 */
    ...
    goto L_0307;      /* PSET 0x03 + CALL 0x07, resolved */
```

The emitter tracks the latched page statically and folds it into the target. A hundred and
sixty-two instructions vanish, and with them the entire class of "where does this jump
go?"

The subtlety is worth reading twice:

> Not even its one-instruction interrupt hold-off survives: that exists to keep an
> interrupt out of the gap between a `PSET` and the jump consuming the page it latched,
> and **generated code has no interrupt point there**.

A hardware feature existing to protect a window that does not exist in your output. You
are allowed to drop it — *provided* the assumption holds, which is why *"every reachable
`PSET` in this ROM is immediately followed by a control transfer, which the test suite
asserts."*

**Assumptions that enable an optimisation must be asserted, not remembered.** That is the
transferable rule.

---

## 5. Validation: An Independent Implementation of the Same ISA

Module 38 argued for an oracle. This project's is unusually good, and its `VALIDATION.md`
is the best short case study in the corpus.

`tools/difftest.py` runs **BrickEmuPy's E0C6200 core** beside the recompiled output and
compares `pc, A, B, X, Y, SP, flags` on every instruction. The reasoning:

> It is a worthwhile check precisely because that core was written by someone else, from
> the same Epson documentation, in another language.

That addresses Module 38 §2's structural limit head-on. An oracle you wrote shares your
misreadings; an independent implementation from the same documentation does not.

Note the mechanism, because recompiled code has no natural observation point — *"that is
rather the point of it"* — so the emitter carries a `TAMA_TRACE` hook that compiles to
nothing unless tracing is enabled. Module 36's configurable escape hatch, at instruction
granularity.

### What it found

> **It found a real bug 1,486 instructions in.**
>
> `RST F, i` is `F <- F AND i`
>
> It *keeps* the bits named in `i` and clears the rest, which is the opposite of the
> obvious reading, and the emitter had it inverted. **Completely silent: the ROM ran, the
> screen drew, the device animated, and a comparison flag was quietly wrong.**

With it fixed, *"the boot path writes twice as many display nibbles and the sprite
resolves into a coherent creature."*

This is Module 37's whole argument in one bug. The project looked like it worked. It
animated. A human watching it would have called it done — and one instruction in 36 was
backwards.

### And two false alarms, which are just as instructive

The doc records both, because each *looked* exactly like a CPU bug:

- **Windows `stdout` is a text stream**, and it expanded every `0x0A` in the binary trace
  into `0x0D 0x0A`. The giveaway was `X = 0x0A0D` — an impossible value for a 12-bit
  register, with the culprit bytes sitting in it.
- **The reference advanced its oscillator inside every `clock()`** while the runtime only
  moves time in `tama_step`, so a read of the interrupt-factor register disagreed by one
  tick. Timers are now frozen on both sides: *"the test is about the CPU."*

Both are harness bugs, not target bugs, and both would have burned a day. Module 46 §4's
argument for writing down what you ruled out, applied to a differential harness.

---

## 6. Time Is the Only Hard Part Left

With control flow resolved statically and the ISA differentially validated, what remains
is Module 40's problem — and on a device whose entire purpose is to age in real time, it
is the *whole* problem.

The header exposes it honestly as a calibration knob:

```c
#define TAMA_OSC1_HZ   32768
#define TAMA_CPU_DIV   1
```

> Instruction cycle counts are treated as OSC1 cycles directly; `TAMA_CPU_DIV` is the knob
> for that, because the real part's CPU clock is a divided OSC1 and **the exact divider
> shows up as drift against a wall clock, not as a wrong picture. Turn it if a running
> Tamagotchi gains or loses time.**

Three things to take from that comment.

**The failure mode is named.** Not "timing may be off" but "it gains or loses time against
a wall clock" — a symptom a user can recognise and report.

**The knob is exposed rather than guessed.** The exact divider was not determined from
documentation, so rather than picking a value and hiding it, the uncertainty is a
`#define` with instructions.

**The symptom is distinguished from other symptoms.** Wrong divider produces drift, *not*
a wrong picture. So if the picture is wrong, this is not your bug — which eliminates a
suspect, the way Module 38 §6 recommends.

Hardware is never the ideal on paper. Leave the calibration knob.

---

## 7. What This Teaches About Big Targets

Run the comparison deliberately:

| Problem | On a console | On the Tamagotchi |
|---|---|---|
| Function boundaries (Module 34) | the recurring root cause | not needed — no functions emitted |
| Indirect calls (Module 14) | the hardest problem | 162 `PSET`s fold to constants |
| Memory layout (Module 43) | a ladder of tradeoffs | one nibble per byte, done |
| Dead code (Module 44) | 444 of 88,816 | the whole ROM is 6,144 words |
| Oracle (Module 38) | build one | somebody else already wrote one |
| **Timing (Module 40)** | one problem among many | **the entire remaining problem** |

The last row is the lesson. Strip away scale and the difficulty that remains is *time* —
which suggests that timing is fundamental to this technique and the rest is consequence.
That is worth knowing before you spend six months on an indirect-call solver.

---

## Labs

- **Lab 87** -- Whole-ROM emitter: for a small ISA, emit the entire address space as one C
  function with a label per instruction, falling through on sequential instructions and
  using `goto` for direct transfers. Measure it against a per-function emitter.
- **Lab 88** -- Fold a paging instruction: statically track a paged-architecture's latched
  page and resolve transfers to absolute labels, emitting nothing for the paging
  instruction itself — and assert the enabling invariant in your test suite.
- **Lab 89** -- Independent oracle: differentially test your lifter against a third-party
  implementation of the same ISA, comparing full register state per instruction. Report
  what it found, including any harness bugs that impersonated CPU bugs.

---

**Next: [Module 54 -- Bytecode Targets](../module-54-bytecode-targets/lecture.md)**
