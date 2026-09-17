# Module 36: Configuration-Driven Recompilation

The last module in this unit is about a small file that turns out to be the most valuable
artifact your project produces.

Every recompilation project accumulates knowledge that cannot be regenerated: the
addresses discovery missed, the functions that need hand-written replacements, the imports
that need a different stack purge, the memory region that has to be mapped somewhere
specific. That knowledge is the project. Everything else -- the disassembly, the lifted C,
the binary -- can be rebuilt from the input in minutes.

So the design goal is: **get all of it into one declarative file, and keep nothing in your
shell history.**

---

## 1. The Manifest Is the Project

Look at what the ReXGlue-based ports actually commit:

```
project/
  CMakeLists.txt
  CMakePresets.json
  worms_manifest.toml      8,431 bytes
  src/
    main.cpp                 146 bytes
    worms_app.h            1,589 bytes
    stubs.cpp              3,942 bytes
    dispatch_tolerance.cpp 2,785 bytes
  generated/               (gitignored)
```

The manifest is larger than all the hand-written code combined. `ydkj_manifest.toml` is
5,912 bytes beside three source files totalling under 3 KB.

That ratio is not an accident, and it is the goal. When the per-title code is three files
and a manifest, a new contributor can read the entire delta between "the toolkit" and
"this game" in ten minutes -- and, as Module 28 notes, the claim "the game runs" means
something, because there is nowhere else for the behaviour to come from.

### What belongs in it

Everything that is a *decision*, and nothing that is a *derivation*.

| Belongs in the manifest | Does not |
|---|---|
| Image base and size from triage | The disassembly |
| Function entries discovery missed | The full function list |
| Addresses to force to the interpreter or a stub | Generated dispatch tables |
| Per-import stack purges that differ from the SDK | The import list itself |
| Memory regions and where they must map | Anything computable from the header |
| Known-bad functions and why | Compiler flags that never change |

The rule of thumb: if you had to *learn* it, it goes in the file. If the tool can read it
off the binary, it does not.

---

## 2. Anatomy of a Real Config

N64Recomp's `.recomp.toml` is the widely-copied shape, and the course ships an annotated
one at [`labs/lab-16/example.recomp.toml`](../../../labs/lab-16/example.recomp.toml):

```toml
[input]
rom = "game.z64"
symbol_file = "syms.txt"          # address -> name, hugely improves readability
# func_sizes_file = "func_sizes.txt"   # when boundaries can't be determined

[output]
# one .c per ROM section
```

Three things to notice in a config that small.

**It takes a symbol file rather than embedding symbols.** Symbols come from a decomp
project that keeps improving (Module 33). Referencing the file means re-importing is free;
pasting the symbols in means they are stale the day you do it.

**`func_sizes_file` exists at all.** This is the escape hatch for Module 34's recurring
bug -- when automatic boundary detection is wrong, you state the boundary. Every mature
recompiler grows this option, because "the tool cannot always tell" is a permanent truth,
not a temporary defect.

**The output is a directory, not a file.** Module 34's volume problem is baked into the
interface.

### The hint section is where the war stories live

ReXGlue manifests carry an `[entrypoint.functions]` table, and the counts tell the story
of each bring-up:

| Project | Functions | Hints | What the hints were |
|---|---|---|---|
| [ydkj](https://github.com/sp00nznet/ydkj) | 14,781 | **1** | one tail-call to `0x82236F38` discovery never placed |
| [outrun](https://github.com/sp00nznet/outrun) | -- | **0** | clean first pass |
| [afterburner](https://github.com/sp00nznet/afterburner) | -- | 4 | function entries |
| [civrev](https://github.com/sp00nznet/civrev) | 40,067 | **24** | 3 codegen-required + 21 runtime-harvested |

`civrev`'s 24 is the interesting one, because the first attempt used **301** and was worse
for it (Module 14). The manifest is where that judgement is recorded, permanently, for
whoever picks the project up next.

**Comment your hints.** A bare address in a config file is worthless in six months. Write
down where it came from -- "runtime-harvested from a tolerant-dispatch boot" versus
"pointer scan" is exactly the distinction that decided that project.

---

## 3. Declarative Beats Imperative, For One Specific Reason

The argument is not elegance. It is that **a config file is a diff**.

When a bring-up regresses, "what changed" has a precise answer: `git diff` on the
manifest. When you hand a project to someone else, the manifest is the handover document.
When you want to know why a decision was made, it is in version control next to the commit
that explains it.

None of that is true of flags typed into a terminal, and the bug you will actually hit is
subtler than forgetting a flag: it is *two people running slightly different commands and
comparing results*. Module 33's provenance record and this module's manifest are the same
idea at two scales.

### Keep the derived state out

A temptation, once a manifest works, is to let the tool write back into it -- caching the
discovered function list, the import table, the computed layout. Resist it.

The moment generated content lives in the manifest, the diff stops being readable, merge
conflicts become unresolvable, and you can no longer tell a decision from a derivation.
Write derived state to a separate file in the output directory. That file is a cache; the
manifest is a source.

---

## 4. Multi-Target Builds

Once configuration is declarative, several things become easy that were previously
projects.

**Two games sharing a runtime.** [oracle-recompiled](https://github.com/sp00nznet/oracle-recompiled)
builds *Oracle of Ages* and *Oracle of Seasons* from one monorepo -- same engine, two
manifests, two binaries, one runtime. `Rampage` does the same for *World Tour* (3,736
functions) and *Universal Tour* (4,788), with separate `RecompiledFuncs_WT` and
`RecompiledFuncs_R2` trees.

**One game, many platforms.** [linksawakening-portable](https://github.com/sp00nznet/linksawakening-portable)
runs the same recompiled *Link's Awakening* on PS4, PS3, 3DS, Wii, Dreamcast, Android and
WebAssembly. Each platform supplies a backend implementing one shared interface; the
recompiled game does not change. Module 9 calls this the strongest argument for lifting to
C, and it is only practical because the platform choice is configuration rather than a
fork.

**Regional or revision variants.** Same engine, different ROM, a handful of address deltas.
Without a manifest this is a branch you will never merge.

### Presets, so nobody guesses flags

`CMakePresets.json` appears in every ReXGlue project at 5,396 bytes -- identical across
them, because the build configuration is a property of the *toolkit*, not the game. A
contributor runs:

```bash
rexglue codegen
cmake --preset win-amd64-release
cmake --build out/build/win-amd64-release
```

Three commands, no flags to get wrong, and the same three in the README, the CI job and
your own shell. Module 35's caching depends on this: a cache keyed on inputs is useless if
everyone's inputs differ by an optimisation flag.

---

## 5. Configuring the Escape Hatches

Modules 11, 12 and 18 showed that the most valuable debugging affordances are the ones that
let you move a function between execution modes without rebuilding. Those belong in your
configuration surface too.

`mariopaint` exposes them as environment variables:

| Lever | Effect |
|---|---|
| `MP_REALFRAME=1` | run the genuine ROM through the emulator -- ground truth for diffing |
| `MP_INTERP_FUNCS="018000,0087EE"` | hand specific recompiled functions back to the interpreter |

`encarta` does the same at build configuration level with `LIFT_LO` / `LIFT_HI`, bisecting
which address range runs lifted versus original. `360`-era projects gate tolerance with
`--protect_zero=false` and an indirect-call override; `wormsrevolution` gates its image
dump behind `REX_DUMP_IMAGE`.

The pattern across all of them: **a switch that changes what executes, not what is built.**
Rebuilding 231 MB of C++ to test a hypothesis is how a five-minute question becomes an
afternoon.

Two design notes:

- **Make them loud.** `mariopaint` prints `mp: $%06lX handed to the interpreter` for each
  address. A silent override is a future mystery.
- **Make them temporary by construction.** `wormsrevolution`'s dump hook carries its own
  removal condition in a comment. Module 39 is about the ones that do not.

---

## 6. When Configuration Becomes a Program

A warning to close the unit on.

Config files grow conditionals. First a flag, then a flag that only applies on one
platform, then a value computed from two others, and eventually you have invented a
programming language with no debugger and terrible error messages.

The line to hold: **configuration describes facts about the target; code makes decisions.**
`image_base = 0x82000000` is a fact. "If the title ID starts with BLUS and the SDK version
is below 3.55, use the alternate heap layout" is a program, and it belongs in your tooling
where it can have tests and a stack trace.

When you feel the urge to add an `if` to a manifest, the honest move is usually a
per-project source file -- which is what `dispatch_tolerance.cpp` and `stubs.cpp` are in
those four-file ReXGlue projects. Small, real, debuggable C++, sitting right next to the
manifest, doing the thing the manifest should not.

---

## Labs

- **Lab 57** -- Manifest-driven driver: convert a shell-script pipeline into a TOML-driven
  one, with a hint table, per-import overrides, and derived state written outside the
  manifest.
- **Lab 58** -- Variant build: drive two ROM revisions of the same game from two manifests
  sharing one runtime, and produce a report of the address deltas between them.

---

**Unit 9 Capstone Lab (Lab 59)**: Build a CI pipeline that takes a ROM, runs extraction,
discovery, lifting, compilation and regression testing, and produces a native binary plus
a machine-readable test report with failure categories. Then break it on purpose at each
stage and confirm every gate goes red.

---

**Next: [Module 37 -- What "It Works" Means](../../unit-10-quality-correctness/module-37-what-it-works-means/lecture.md)**
