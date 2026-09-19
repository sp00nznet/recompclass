# Module 61: Open Problems

This course has spent sixty modules on what is known. This one is about what is not.

Everything below is genuinely unsolved, in the specific sense that the corpus works around
it rather than through it. Each entry states the problem, what is currently done instead,
and what a real contribution would look like — because "open problem" without that last part
is just a complaint.

---

## 1. Deciding What Counts as a Function

**The recurring root cause of this entire course.**

Module 34 catalogued four projects hitting it in four disguises: N64 fallthrough splits
(racer 143, Rampage 418, Rampage 2 ~879, pokemonsnap ~390), an inflated PS3 function count
revised downward, `civrev`'s 301 pointer-scan hints making a build *worse*, and `xwa`'s
codegen emitting more functions than discovery found.

**What is done instead:** heuristics plus automated fallthrough repair plus runtime
observation. It works, and every project pays the same tax.

**What would be a contribution:** a boundary detector with a published evaluation on a
*corpus* rather than examples, reporting false splits and missed functions separately.
`rev.ng` [Di Federico et al., CC 2017] attacks this academically; nobody has evaluated it on
game binaries, which have different properties from the server software these tools are
usually measured on.

This is the highest-value open problem in the field, because everything downstream inherits
it.

---

## 2. Self-Modifying Code

**The case that defeats static recompilation outright.**

Hand-written Z80 on home computers and calculators does this routinely — patching operands,
building jump targets in RAM, executing data. `tirecomp` and `zxrecomp` exist and work;
programs that self-modify are the known hard set.

**What is done instead:** interpret those regions, or do not support those programs.

**What would be a contribution:** first, a *measurement* — how common is it, really, across
a large corpus of ZX Spectrum or TI-83 programs? Nobody has published that number, and the
field's intuition may be badly wrong in either direction. Second, a hybrid that recompiles
the static majority and falls back precisely (Module 49), with the boundary detected rather
than hand-annotated.

---

## 3. Verified Equivalence

**Everything in Modules 38 and 39 is testing. None of it is proof.**

A differential test over a million instructions found a real bug in `tamarecomp` at
instruction 1,486. It cannot tell you there is not another at ten million.

**What is done instead:** differential testing, corpus runs, and accepting residual risk.

**What would be a contribution:** SMT-based equivalence checking for *instruction lifting
rules* — not whole programs, which is intractable, but "does this C statement implement this
opcode's semantics for all inputs?" That is a bounded, checkable question, the lifting rules
are small, and the payoff is permanent: a verified rule never needs retesting.

The flag-computation rules are the obvious target. Module 53's bug was `RST F, i` inverted;
Module 38's taxonomy is mostly width and flag semantics. These are exactly the properties an
SMT solver handles well.

---

## 4. Cycle Accuracy Without Cycle Cost

Module 40's spectrum: most code needs semantic accuracy, rendering needs frame accuracy, and
a small identifiable set needs cycle accuracy. Build everything cycle-accurate and you have
rebuilt an emulator; build nothing that way and raster tricks break.

**What is done instead:** guess, then add cycle counting where something visibly breaks.

**What would be a contribution:** *identifying statically which code needs what.* A pass
that finds the regions whose behaviour depends on timing — mid-scanline register writes,
polling loops with no other exit, timing-based checks — so you can pay for accuracy only
there. Nobody has published this and everyone does it by hand, badly.

---

## 5. Automated Shim Generation

Module 15's claim that the runtime is the hard part is also an admission: the largest part of
the work is hand-written per platform.

Some of it is mechanically derivable and already is — import thunks, dispatch tables, stub
bundles, `pcrecomp`'s `stdcall_argc.py` deriving stack purges from SDK headers.

**What would be a contribution:** pushing that further. Given an SDK's headers and a
platform's ABI, how much of a shim layer can be generated? For well-documented platforms
with real SDKs — Xbox, PS3, Windows — the function signatures are *right there*. Generating
correctly-typed stubs that log and return plausible values would collapse the first week of
every bring-up.

---

## 6. A Retargetable Framework

Every toolkit in this corpus is per-platform. There are roughly thirty of them and they share
a great deal of structure that is reimplemented each time.

Module 34 §3 shows the ceiling reached so far: `apple2recomp` and `vic20recomp` share an
entire 6502 front end; four Z80 machines share another.

**What would be a contribution:** the layer above that. The v2 course paper notes N64Recomp
maps instructions to abstract `BinaryOp`/`UnaryOp` types before its `CGenerator` emits C, and
*"a different generator backend could target LLVM IR, Rust, or any other language."*

The honest question is whether a general framework would be good enough at anything. Module
53's whole-ROM-as-one-function strategy and Module 30's 50,000-function chunked output cannot
share a backend. A framework that handles both may be worse at both — and *establishing that*
would itself be a useful result.

---

## 7. Measuring Recompilability

Module 56 asks you to assess a target before committing, and gives a procedure. It does not
give a **metric**, because none exists.

There is no accepted answer to "how statically recompilable is this ROM?" `cybikorecomp`'s
INDIRECT.md is the closest thing in the corpus: unresolved transfers before and after
assembling the address space (2,533 → 227), classified by defining instruction.

**What would be a contribution:** formalise that into something comparable across
architectures, and publish it for a large corpus. A number that lets someone say "this ROM
scores 0.94, that one 0.31" would change how targets are chosen — and would let the field
argue about whether the metric predicts anything, which is how metrics get good.

---

## 8. Coprocessors and Microcode

Module 42 §5's decision — recompile the microcode, HLE it, or interpret it — is made per
project with no general guidance.

Module 20's `diddykongracing` had to write a custom interpreter because its `f3ddkr`
microcode was unsupported by the standard renderer. The PS3's SPUs, the PS2's VUs and the
N64's RSP all pose it differently.

**What would be a contribution:** microcode *identification* — recognising which known
microcode a game uploaded, so HLE can be selected automatically and fall back to
recompilation for anything unrecognised. This is a code-similarity problem (Module 52 §2),
it is mechanically checkable, and it is the kind of thing that could work well.

---

## 9. Palm OS

Named because it is the clearest shovel-ready target in the corpus's research notes and
nobody has built it.

68K, which is well tooled and already in this corpus. **PumpkinOS** reimplements roughly 800
Palm OS system traps natively — most of a runtime, already written. Every OS call goes
through `TRAP #15`, which is an unusually clean single interception point. **CloudpilotEmu**
provides the oracle.

No Palm OS static recompiler has ever been built. The obstacle is not difficulty; it is that
the application library is enormous and no single title is the obvious first target
(Module 56 §4's "first game" problem).

---

## 10. The Concrete One

Not research, but the highest-impact unglamorous work available: **`ps3recomp` has no Vulkan
RSX backend.** D3D12 renders real titles, Metal covers macOS, and Vulkan is unwritten — which
means Linux and Android cannot run any of it.

Module 57 §4. A named gap, a working reference implementation to match, and an entire
platform unblocked by it.

---

## Choosing Something

Three filters, in order:

**Is it measurable?** Several problems above are open mainly because nobody has counted
anything. A measurement is a complete contribution and the cheapest kind to make.

**Is it checkable?** Module 52 §1's rule. Work whose output can be mechanically verified
against an oracle is worth more than work that requires trusting your judgement.

**Would anyone use it?** The Vulkan backend would be used immediately. A retargetable
framework might never be. Both are legitimate; know which you are choosing.

---

## Labs

- **Lab 118** -- Measure an open problem: pick one where the honest state is "nobody has
  counted," build the corpus and the measurement, and publish the number with its method.
- **Lab 119** -- Verified lifting rules: encode the flag semantics of one instruction group
  as SMT constraints, prove your C implementation equivalent for all inputs, and report what
  the proof caught that your differential test had not.

---

**Next: [Module 62 -- Research Methods](../module-62-research-methods/lecture.md)**
