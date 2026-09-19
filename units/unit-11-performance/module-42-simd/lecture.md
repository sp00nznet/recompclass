# Module 42: SIMD for Lifted Code

Every console from the fifth generation onward has a vector unit, and games use them for
the work that dominates a frame: vertex transforms, skinning, physics, audio mixing.
Lifting that code scalar-by-scalar is correct and can be an order of magnitude slower than
the original hardware — the one place where a recompiled build can genuinely lose to the
machine it came from.

This module is about mapping guest vector units onto host SIMD, and about the two places
that mapping is not a simple substitution.

---

## 1. The Landscape

| Guest | Unit | Shape | Host analogue |
|---|---|---|---|
| Xbox 360 | VMX128 | 128 registers, 4×float32 | SSE/AVX, 16 registers |
| PS3 PPU | AltiVec/VMX | 32 registers, 4×float32 | SSE/AVX |
| PS3 SPU | SPU ISA | 128 registers, everything is a vector | SSE/AVX |
| PS2 | VU0/VU1 | 32×128-bit, own instruction set and memory | SSE, but see §5 |
| PS2 EE | MMI | 128-bit integer SIMD | SSE2 integer |
| N64 | RSP | 8×16-bit lanes, saturating | SSE2 integer |
| GBA/DS/PSP | none / VFPU | — | — |

Two structural mismatches show up immediately and shape everything else.

**Register pressure.** VMX128 has 128 vector registers; SSE has 16. Your lifted code keeps
guest vector registers in a `__m128 vr[128]` array (as Lab 39 does), and the host compiler
decides which ones live in registers at any moment. Usually it does a good job within a
basic block and spills across calls.

**Lane semantics.** The guest's rules for saturation, rounding, NaN handling and
denormals are *not* the host's. This is where correctness goes wrong quietly.

---

## 2. The Easy Case, and Why It Is Genuinely Easy

Most vector instructions in most games are elementwise float arithmetic, and these map
one-to-one:

```c
// vaddps vD, vA, vB
vr[vD] = _mm_add_ps(vr[vA], vr[vB]);

// vmulps vD, vA, vB
vr[vD] = _mm_mul_ps(vr[vA], vr[vB]);
```

That is Lab 39, and it is not a simplification — it is what a production lifter emits.
Both architectures are IEEE-754 4-lane single precision, both do the same thing, and the
host compiler keeps the values in registers.

**Emit intrinsics, not inline assembly.** Intrinsics let the compiler allocate registers,
schedule, and fold adjacent operations. Inline assembly forbids all three and you will lose
more than you gain.

**Use a portability layer if you want more than one host.** Module 28 mentions SIMDE, which
maps SSE intrinsics onto NEON and others. A recompiled Xbox 360 game running on an ARM
laptop goes through two translations — VMX to SSE to NEON — and it works.

---

## 3. The Awkward Middle: Permutes and Dot Products

Operations with no single host instruction need a helper, and the helper is where the
per-architecture knowledge lives:

```c
// vdot3 vD, vA, vB   -- 3-lane dot product
vr[vD] = vdot3_sse(vr[vA], vr[vB]);
```

Two rules for these.

**Write the helper once, in a header, and call it.** Module 34's argument for an op kit
applies with extra force here — a hand-written `vperm_sse` that is correct is worth a great
deal, and inlining it at 4,000 call sites as raw intrinsics is how you get 4,000 chances to
be subtly wrong.

**Let the compiler inline it.** `static inline` in a header, and check the disassembly once
to confirm it actually did.

The specific operations that need helpers, on most guests: arbitrary byte permutes, dot
products, horizontal adds, saturating pack/unpack, and reciprocal estimates.

---

## 4. Where Correctness Goes Wrong

The traps, roughly in order of how much time they cost people.

**Reciprocal estimates.** Guests love `vrsqrte`-style instructions with architecturally
defined, low precision. `_mm_rsqrt_ps` also has low precision — *a different* low precision.
A normalised vector that is slightly off usually looks fine, until it accumulates in a
physics integrator and something drifts through a wall. If a game depends on the exact
result, you must reproduce the guest's estimate table, not approximate it.

**Denormals.** Many consoles flush denormals to zero in hardware. Your host may not, and
the difference is a large slowdown *and* a numeric difference. Set the host's
flush-to-zero and denormals-are-zero modes to match the guest, once, at startup.

**NaN propagation and min/max.** `_mm_min_ps` and the guest's minimum may disagree about
which operand wins when one is NaN. Rare, and unfalsifiable once it bites.

**Saturation.** Integer SIMD on the N64 RSP and PS2 MMI saturates rather than wrapping.
SSE2 has saturating pack instructions, but check the width and signedness match exactly.

**Lane order.** Big-endian guests (Xbox 360, PS3, N64) store vectors with lane 0 at the
opposite end from a little-endian host. Module 28 flags this; it means a permute constant
lifted literally is mirrored. Get this wrong and geometry is scrambled in a way that looks
like a renderer bug.

### Test this with Module 38's oracle

All of the above are exactly what a differential test catches and eyeballing does not.
Lab 39 ships `sim_*` reference implementations alongside the lifters for this reason: run
both over random inputs, compare bit patterns, and weight the generator toward NaN, zero,
denormal and saturation boundaries (Module 39 §2).

---

## 5. When the Vector Unit Is a Separate Computer

VMX128 is a set of instructions in the CPU's stream. The PS2's VU1 and the N64's RSP are
not — they are **separate processors running their own programs**, uploaded at runtime.

That is a different problem, and it is the Module 21 HLE-versus-LLE decision again:

- **Recompile the microcode** as its own program, and schedule it against the main CPU
  (Module 31's territory).
- **Recognise it and reimplement what it means.** If the microcode is a known,
  widely-shared library — which N64 graphics microcode usually is — HLE is dramatically
  faster and dramatically less general.
- **Interpret it**, when it is small, unusual, or you are still working out what it does.

Module 20's `diddykongracing` is the cautionary case: its `f3ddkr` microcode was not
supported by the standard renderer, so the project wrote a custom interpreter. **Your
microcode strategy is decided by your specific game, not by the platform.**

---

## 6. Auto-Vectorising Scalar Lifts

A tempting idea: lift scalar guest code and let the host compiler vectorise it.

In practice this rarely fires on generated code, for a structural reason. Auto-vectorisers
need to prove loops are independent and memory does not alias — and your lifted code
routes every access through `bus_read`/`bus_write` functions over a shared array, which
defeats alias analysis almost completely. Module 43 covers making those accesses cheaper;
making them *vectorisable* is a much harder problem.

Do not plan around it. Where the guest used vectors, lift to vectors. Where it did not,
scalar is fine — §3 of Module 41 says the time is elsewhere anyway.

---

## Labs

- **Lab 74** -- Vector lifter with a reference: lift a guest vector ISA subset to host
  intrinsics, write scalar reference implementations of each, and differentially test them
  over inputs weighted toward NaN, denormal, zero and saturation boundaries.
- **Lab 75** -- Lane order and permutes: lift a big-endian guest's permute instruction to a
  little-endian host correctly, and demonstrate the mirrored-constant bug that the naive
  translation produces.

---

**Next: [Module 43 -- Memory Access Optimization](../module-43-memory-access/lecture.md)**
