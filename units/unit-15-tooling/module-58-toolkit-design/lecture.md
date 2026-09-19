# Module 58: Designing a Toolkit Others Can Use

There is a moment in most recompilation projects where you notice you have built the same
thing twice. That is when a project becomes a toolkit — or fails to, and becomes two
projects that share a lineage and nothing else.

This module is about the structural decisions that make the difference, drawn from a corpus
that contains roughly thirty toolkits and several hundred ports built on them.

---

## 1. The Split, and Where the Line Goes

The pattern is consistent across every family in the corpus:

```
<thing>recomp/          the toolkit -- decoder, analyzer, emitter, runtime, docs
<game>-<thing>-recomp/  the port    -- a manifest and a few files
```

`lynxrecomp` + `chipschallenge-lynx-recomp`. `apple2recomp` + `choplifter-apple2-recomp`.
`tirecomp` + `blockdude-ti-recomp`. `newtonrecomp` + `newtris-newton-recomp`.

**The line goes at "is this true of the machine, or of this program?"**

| Toolkit | Port |
|---|---|
| ISA decoder and lifter | the manifest |
| Hardware runtime and shims | hints discovery missed |
| Platform container parsing | per-game stubs |
| The interpreter oracle | functions needing hand-written replacements |
| Build system and presets | game-specific patches |
| Docs about the machine | docs about this bring-up |

Module 28 measured how far this can go: `wormsrevolution`'s entire hand-written surface is
four files, 8.5 KB, of which `main.cpp` is **146 bytes**. `ydkj` is three files under 3 KB.

And Module 37 §6 draws the consequence that matters: when the per-title code is three files,
**"the game runs" means something**, because there is nowhere else for the behaviour to come
from. A thin port is an evidentiary property, not just a tidy one.

---

## 2. The Second Game Is the Test

A toolkit with one port is one project with delusions of generality. You cannot tell which
decisions are general until something else has to live with them.

The corpus makes this explicit. `crystalmines2-lynx-recomp` is described as *"the second game
on the lynxrecomp toolkit."* `oracle-recompiled` builds two sister games from one runtime.
`Rampage` carries *World Tour* (3,736 functions) and *Universal Tour* (4,788) side by side.
`pokemon-crystal` is *"the second Generation II title attempted with this toolchain (after
pokemon-gold); same mapper, same recipe."*

**Pick the second game to be different in one specific way** — a different mapper, a
different compiler, a different peripheral. Same-again proves nothing.

Expect it to hurt. The second game finds every place you hardcoded an address, assumed a
memory size, or put a game-specific quirk in the runtime. That is the point, and it is
cheaper now than after five ports.

---

## 3. Organise by Subsystem

Module 17 compared layouts. `gcrecomp`'s `src/`:

```
src/
├── gx/          GPU -> D3D11, TEV stage translation
├── audio/       DSP ADPCM decode, voice mixing
├── input/       controller mapping
├── os/          OS HLE: heap, DVD, threads, timing
├── runtime/     the glue the recompiled code links against
└── example/     a worked example project
```

Two things to take from that tree.

**There is no `codegen/` or `analysis/` directory**, and that is not an oversight. Almost all
of a mature toolkit is runtime. The parts that feel like the interesting engineering — the
disassembler, the lifter, the emitter — are a minority of the code by a wide margin. Module
15 argues this; the directory listing proves it.

**`example/` is load-bearing.** A toolkit with a worked example in the tree is one somebody
else can adopt. `xboxrecomp` goes further with `templates/`, `tests/`, `tools/`, a
`Dockerfile` and 25 files of `docs/`. That is what "reusable" costs, and it is mostly not the
recompiler.

---

## 4. Make Registration Automatic

The single best ergonomic decision in the corpus, and it recurs independently.

`snesrecomp`'s `recomp_patch.h`:

```c
RECOMP_PATCH(smk_80FF70, 0x80FF70) {
    // body
}
```

*"auto-registers it in the snesrecomp dispatch table at its original SNES 24-bit
bank:address, before main() runs. **No central registration list needed.**"* The header
credits N64Recomp's macro of the same name.

`tirecomp` has `ti_register_func(addr, fn)`. ReXGlue has `REX_DEFINE_APP`.

Why it matters more than it sounds: a central registration list is a merge conflict on every
contribution, a thing to forget, and a reason for a newcomer's first patch not to work.
Auto-registration makes adding a function a **one-file, one-line change** — which is the
difference between a toolkit people extend and one they fork.

And Module 47 §3 showed the bonus: the same mechanism becomes your modding interface, for
free, because "last registration wins" is a link-order question.

---

## 5. Give People the Escape Hatches

Modules 36 and 38 argued for switches that change what executes without a rebuild. In a
*toolkit* they are not a debugging convenience — they are the interface your users debug
through, and they should be documented.

The ones worth shipping:

| Hatch | Example |
|---|---|
| Ground-truth mode | `MP_REALFRAME=1` — run the original, unmodified |
| Per-function fallback | `MP_INTERP_FUNCS="018000,0087EE"` |
| Range bisection | `LIFT_LO` / `LIFT_HI` |
| Tolerance | `--protect_zero=false`, dispatch overrides |
| Tracing | `TAMA_TRACE`, compiled out unless enabled |
| Counters | registered / hit / fallback (Module 49 §2) |

Two design rules from the corpus. **Make them loud** — `mariopaint` prints
`mp: $%06lX handed to the interpreter` for each override, because a silent switch is a future
mystery. And **make them free when off** — `tamarecomp`'s trace hook *"compiles to nothing
unless the build asks for a trace."*

---

## 6. Documentation That Earns Its Place

The toolkits people actually adopt are the documented ones. What the good ones contain:

**A machine document that separates fact from inference.** `vmurecomp`'s CPU notes: *"This is
not a datasheet — it records the decisions the decoder and runtime had to make, and which of
them rest on published facts versus convention."* Six months on, you will not remember which
was which.

**A document per hard problem.** `tamarecomp` has `RECOMPILER.md` (how 6,144 words become one
C function *and why that is sound*) and `VALIDATION.md` (the differential campaign and what
it found). `cybikorecomp` has `INDIRECT.md` — a measurement, not a description.

**A status file with categories.** `ps3recomp`'s `MODULE_STATUS.md`, which Module 57 §4 shows
doubles as a contribution roadmap.

**A porting guide.** `ps3recomp`'s `GAME_PORTING_GUIDE.md`. The document that turns a toolkit
into something a stranger can start with.

**The numbers, with their provenance.** Module 37 §7.

---

## 7. Licence and Attribution, Structurally

Module 45's material, as a toolkit design concern rather than an afterthought.

Your toolkit's licence is constrained by what it links. `snesrecomp` can be permissive
because LakeSnes is **MIT**; had it been GPL, every port would inherit that. **Decide before
you build**, because retrofitting means replacing the emulator.

Ship `LICENSE`, and once you have more than one dependency, `NOTICE` and `LICENSES/` the way
`xboxrecomp` does.

And name your lineage prominently. `gb-recompiled` credits arcanite24 in every downstream
README. `snesrecomp` names LakeSnes and angelo-wf. `recomp_patch.h` credits N64Recomp for the
macro. This is a licence obligation under most permissive terms and, per this course's
standing position, the right thing regardless.

---

## 8. A Checklist

- [ ] Toolkit and ports are separate repositories
- [ ] A second, deliberately *different* game exists
- [ ] `src/` is organised by subsystem
- [ ] A worked example lives in the tree
- [ ] Registration is automatic — no central list
- [ ] Escape hatches exist, are documented, are loud, and are free when off
- [ ] Counters are exposed so users can report real numbers
- [ ] A machine document separates published fact from convention
- [ ] A status file uses categories, not booleans
- [ ] A porting guide exists
- [ ] Licence is compatible with everything linked, and notices are preserved
- [ ] Lineage is credited by name

---

## Labs

- **Lab 111** -- Extract a toolkit: take a single-game recompilation project and split it
  into a toolkit and a port, then bring up a second, deliberately different game on it.
  Report every place the split forced a change.
- **Lab 112** -- Auto-registration: replace a central registration list with a
  self-registering macro, and demonstrate that adding a function is now a one-file change
  and that override-by-link-order works.

---

**Next: [Module 59 -- Project Shapes](../module-59-project-shapes/lecture.md)**
