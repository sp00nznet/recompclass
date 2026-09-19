# Module 40: Audio and Timing Accuracy

Every module so far has treated a recompiled program as a function: same input, same
output. This one is about the axis that breaks that model — **when** things happen.

Timing is where recompilation's core assumption quietly stops holding. Your lifted code is
semantically identical to the original and runs at a completely different speed, and a
surprising amount of shipped software depends on the speed rather than the semantics.

It is also where the most confusing bugs in this course live: a game that runs perfectly
and shows nothing, a title screen that flashes past in one frame, audio that is correct
but arrives in bursts.

---

## 1. The Frame Loop Is Not Where You Think It Is

Start with the bug that catches everyone, because it is the clearest possible statement of
the problem.

Module 11's [mariopaint](https://github.com/sp00nznet/mariopaint) documents it in
`src/main/main.c`:

> `$018260` is the important one. The ROM's title loop has no frame sync in it at all — it
> spins polling the mouse bytes at `$04C6`/`$04C8`/`$04CA` and bails to the demo after
> `$800` idle iterations. **On hardware an NMI drives the frame underneath it**;
> interpreted here, it burns all 2048 iterations instantly with nothing drawn and no input
> possible, so the title screen flashed past invisibly.

Read that carefully, because the shape recurs on every platform.

The ROM's loop is correct. It polls, it counts, it gives up after 2,048 tries. On a SNES
that takes several seconds, because **the loop is not what advances time** — a
vertical-blank NMI fires 60 times a second underneath it, drawing frames and updating the
mouse bytes the loop is reading.

Lift that loop to C and the NMI does not exist unless you arranged for it. The loop
completes in microseconds, reads the same unchanged mouse bytes 2,048 times, concludes the
user is idle, and moves on. Nothing was drawn. Nothing was broken, either — every
instruction executed correctly.

The fix there was to make the recompiled version of that loop drive a frame per iteration.
The general principle:

> **The original program assumed something else was advancing time. In your build, nothing
> is, unless you build it.**

The same README notes the fades have the identical problem: their loops step brightness
one step per vblank, so interpreted they finish instantly with nothing drawn.

---

## 2. Who Advances Time?

Three workable answers. Pick deliberately.

### The guest drives it

The recompiled code itself calls into your runtime often enough that you can count cycles.
This is what a cycle-cost table in your lifter buys you — each lifted instruction adds its
cost, and when the total crosses a threshold you run a frame.

`tirecomp`'s runtime does exactly this in its dispatch loop
([`src/recomp_rt.c`](https://github.com/sp00nznet/tirecomp/blob/main/src/recomp_rt.c)):

```c
uint64_t ti_cycles = 0;
void (*ti_frame_hook)(void) = 0;
...
        fn();
        ti_cycles++;
        if (ti_frame_hook) ti_frame_hook();
```

A hook called at every control transfer. Coarse — it counts blocks, not cycles — but it
guarantees the runtime gets a turn, which is the property that actually matters.

**The trap:** a tight loop with no control transfers and no memory access never calls your
runtime at all, and hangs. Pick a hook point the guest cannot avoid — every basic block,
or every backward branch.

### The host drives it

A real timer or the host's vsync drives the frame, and the guest runs until it blocks.
This is what an emulator-hosted design gives you for free, because the emulator already
has a cycle-accurate frame (`snes_runFrame` in Module 11).

### Nobody drives it, and you find out the hard way

The default, and the cause of §1.

---

## 3. Interrupts Are Timing, Not Control Flow

Interrupts are easy to think of as "a function that gets called." On the original hardware
they are **the clock**, and treating them as ordinary calls loses the thing that mattered.

Module 20's `racer` lists "Event System Wiring (VI, SI, Timer)" and "osRecvMesg Thread
Blocking Fix" as distinct milestones after the CPU was already running — the code worked
and the *scheduling* did not. `crazytaxi` registers the VBlank handler the game expects at
`VBR+0x600` and takes interrupts, and is explicit that the remaining blocker is a wait
loop it never leaves.

That failure — **"stops in a wait loop it never leaves"** — is the characteristic timing
bug, and its diagnosis is always the same question: *what was supposed to change the value
this loop is reading, and is it running?*

Usually the answer is an interrupt you have not wired, a hardware register your shim
returns a constant for, or a counter nothing increments. Module 30's `tokyojungle` parks
"in its main loop waiting on a single counter that nothing in the emulator writes."

**Build the spin watchdog from Module 30 before you need it.** A hang is otherwise
unfalsifiable; sampling the PC and resolving it through your symbol table turns it into a
named function.

---

## 4. Audio Is a Real-Time Deadline

Graphics can miss a frame and look bad. Audio that misses its deadline does not sound
slightly worse — it *clicks*, and the human ear is far less forgiving of a discontinuity
than the eye is of a dropped frame.

This changes the engineering. Video is pull-based and forgiving; audio is push-based with
a hard deadline, and the callback runs on somebody else's thread.

### The guest's audio hardware is a separate processor, usually

| Platform | Audio hardware |
|---|---|
| Game Boy | 4-channel APU, part of the CPU die |
| SNES | SPC700 with its own 64 KB and DSP — a whole second computer |
| N64 | RSP running audio microcode |
| Dreamcast | Yamaha AICA — **an ARM7 plus a 64-channel DSP** |
| GameCube | DSP running Nintendo's AX microcode |
| PS3 | SPU-based, behind `cellAudio` |

Three of those are programmable processors running code the game uploaded. That gives you
the same HLE-versus-LLE decision as Module 21's RSP microcode: reimplement what the
microcode *means*, or recompile the microcode itself.

Module 20's `diddykongracing` reports an HLE audio pipeline with "all 14 `aspMain` opcodes
active, stereo output at 22050 Hz (reverb FX disabled)" — a concrete picture of what HLE
audio costs, including the honest note about what is switched off.

### Audio often comes up before graphics

Module 20's `pokemonsnap` has audio initialised and RSP audio tasks executing while GFX
display list submission is still in progress. That ordering is common and worth planning
for: the audio task path is simpler than the graphics one, so **getting audio running is a
good early proof that your coprocessor task routing works at all** — before you take on
the display list.

---

## 5. Sample Rates and the Drift Problem

The guest produces samples at its rate. Your host consumes them at its rate. These are
never the same number, and the difference is not constant.

Naive resampling gets the pitch right and still fails, because the error accumulates. Too
slow and the buffer underruns, which clicks. Too fast and it overruns, which drops audio.
Either way it happens once every few minutes, which is exactly long enough to be hard to
reproduce.

The fix is a feedback loop, not a better conversion: **measure the buffer fill level and
adjust the consumption rate slightly** to hold it near a target. This is the same shape as
a clock discipline loop, and it is the standard answer in every emulator that sounds good.

Some latency is not negotiable — you need a buffer to absorb jitter. Aim to know your
number rather than minimise it blindly; a stable 40ms beats an unstable 15ms.

---

## 6. Deciding How Accurate You Need to Be

There is a real spectrum here and projects routinely aim at the wrong end.

| Level | What you reproduce | When you need it |
|---|---|---|
| **Semantic** | the right things happen in the right order | most game logic |
| **Frame-accurate** | the right things happen on the right frame | rendering, input feel, most games end to end |
| **Cycle-accurate** | the right things happen on the right cycle | raster tricks, audio timing, timing-based copy protection |

Most of a game needs the first. Your renderer needs the second. A small, identifiable set
of things needs the third — and if you assume you need cycle accuracy everywhere you will
build something as slow as an emulator and lose the reason you were recompiling.

Things that genuinely need cycle accuracy: mid-scanline register writes (raster bars,
split screens), audio sample timing, software that measures the CPU to detect tampering,
and anything doing bus timing tricks.

Things that do not: almost all gameplay logic, menus, AI, physics, file loading.

---

## 7. Testing Timing

Timing bugs evade the techniques of Modules 38 and 39 unless you aim at them specifically.

**Compare frame numbers, not just frame contents.** A frame-hash comparison that ignores
*which* frame a hash appeared on will not notice that your build reached the title screen
in 4 frames instead of 180. That is exactly the mariopaint bug, and it is invisible to a
set-based comparison.

**Instrument the frame counter.** The cheapest timing regression test: run a fixed input
for N frames and assert the guest's own frame counter (or game state variable) landed where
it should.

**Log a timeline, not events.** When you record a trace, record *when*. "The audio callback
ran 300 times and the guest produced 280 buffers" is a diagnosis; "audio is glitchy" is
not.

**Watch for impossible speed.** A loop completing in microseconds that should take seconds
is the §1 signature. If your runtime can count guest cycles, assert that an operation which
should take a frame actually consumed roughly a frame's worth.

**Fuzz the timing, not just the input** (Module 39 §7). Vary when interrupts arrive
relative to guest code, within the range the real hardware allowed. Divergence under that
variation means you have a race the original hardware's fixed timing was hiding.

---

## 8. Video Is Audio's Harder Cousin

If your target plays full-motion video, it has both problems at once and a synchronisation
constraint between them.

Module 28's `wormsrevolution` plays "the full intro (Team17 → publisher logos → cinematic,
all full-motion video decoding natively)." Module 13's `encarta` went further and made a
recompiled Indeo 3 decoder byte-exact over 64 of 64 frames.

Note which one of those was verifiable: the codec, because it has a defined correct output
(Module 38 §3). Playback timing does not. Decode correctness and playback correctness are
separate problems, and you should establish the first before you debug the second —
otherwise you cannot tell a decoder bug from a pacing bug.

---

## Labs

- **Lab 68** -- Frame driver: take a recompiled program whose main loop has no frame sync
  and add a cycle-counted hook that advances a frame, then demonstrate a loop that
  previously completed instantly now takes the expected wall-clock time.
- **Lab 69** -- Audio clock discipline: implement a resampler with a feedback loop that
  holds buffer fill near a target, and plot fill level over ten minutes against a
  fixed-ratio resampler to show the drift.
- **Lab 70** -- Timing regression test: assert that a fixed input sequence reaches a known
  game state on a known frame number, and show it catching an injected frame-pacing bug
  that a frame-hash-only comparison misses.

---

**Unit 10 Capstone Lab (Lab 71)**: Build a differential fuzzer that runs randomised inputs
through both an emulator and a recompiled binary, detects the first divergence, minimises
it by input bisection, then locates the responsible function by code bisection — and
produce an evidence statement for the result that would survive Module 37's ten-minute
audit.

---

**Next: Module 41 -- Profiling Recompiled Binaries** *(Unit 11, not yet written — see [SYLLABUS.md](../../../SYLLABUS.md))*
