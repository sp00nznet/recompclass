# Module 33: Automated Disassembly Pipelines

Semester 1 and 2 taught you to recompile one program. This module is about the moment
that stops being enough: when you have a toolkit, several targets, and you are tired of
running six commands in order and remembering which flags you used last time.

The shift is not technical sophistication. It is **repeatability**. A pipeline you can
re-run from scratch is the difference between a project and a pile of build artifacts,
and it is the precondition for everything in Semester 3 -- you cannot test what you
cannot rebuild, and you cannot claim a number you cannot re-derive.

---

## 1. What a Pipeline Actually Is

Strip away the tooling and a recompilation pipeline is a sequence of pure-ish functions
over files:

```
container  ──▶ image  ──▶ function set  ──▶ disassembly  ──▶ lifted C  ──▶ binary
 (ISO/XEX/    (PE/ELF/   (addresses +     (instructions)   (.c files)    (.exe)
  ROM/pkg)     flat)      names)
```

Every stage takes files and produces files. That property is worth protecting, because
it gives you three things for free:

- **Caching.** If the image did not change, you do not re-extract it.
- **Inspection.** Every intermediate is a file you can diff, hash, and commit.
- **Bisection.** When output goes wrong, you can re-run one stage in isolation.

The corpus makes this concrete. `pcrecomp` exists precisely because the same stages kept
being rewritten per project -- it collects "every tool, runtime, and hard-won trick from
our PC static recompilation projects into one place." Its `tools/pe/` is a pipeline stage
library: import and export analysis, section hashes, delay-import handling, protection
detection, a recursive binary catalog, and `stdcall_argc.py`.

### The stage boundary that matters most

Between **function set** and **disassembly** is where projects live or die, and it is the
only stage whose output you should treat as a first-class, version-controlled artifact.

Everything downstream is mechanical. The function set is a *decision*, it is where every
hard problem in Modules 6, 14 and 20 lands, and it is the thing you will iterate on
fifty times. Give it a file format, commit it, and diff it.

---

## 2. Container Extraction

The first stage is almost always unglamorous format work, and it is worth budgeting for
honestly because it is pure overhead before any recompilation begins.

| Platform | Container | What extraction involves |
|---|---|---|
| N64 | `.z64` / `.n64` / `.v64` | byte-order normalisation, header parse |
| Game Boy / GBA | flat ROM | cartridge header, mapper detection |
| Xbox | XBE | section table, the SDK libraries baked into every binary |
| Xbox 360 (disc) | XGD → XDVDFS → XEX2 | filesystem extract, then decrypt + decompress |
| Xbox 360 (XBLA) | STFS / GoD package | package extract, then the same XEX2 path |
| GameCube / Wii | GCM / ISO → DOL | apploader, REL modules |
| PS3 | SELF → ELF | decryption, then OPD table parsing |
| PS2 | ISO → ELF | straightforward by comparison |
| DOS / Windows | MZ / NE / LE / PE | often wrapped in an installer, sometimes protected |
| Apple II | DOS 3.3 floppy image | **sector-by-sector reconstruction of what ends up in RAM** |

That last row is the one to think about. `apple2recomp` has no cartridge to dump: the
program arrives off a 5.25" floppy "one 256-byte sector at a time," so the extraction
stage has to *simulate enough of the loader* to know what memory looks like before any
code exists to disassemble.

### Protected binaries: let the program do the work

Module 27 covered this and it belongs in your pipeline design, not your heroics budget.
When a binary is encrypted or packed, the loader's job is to produce plaintext code in
memory. Your job is to be there when it does.

`xwa` does exactly this with SafeDisc: Phase 1 of its pipeline is "SafeDisc decryption,
memory dump from runtime." `wormsrevolution` does it for a different reason -- its LZX
variant defeated the static extractor, so its app subclass dumps the image straight out
of mapped guest memory:

```cpp
// ponytail: one-shot bring-up scaffold. Dump the runtime-decompressed image
// straight out of mapped guest memory (extract_pe.py can't handle this title's
// LZX variant) ... Enabled only when REX_DUMP_IMAGE is set; remove after the sweep.
void OnPostLoadXexImage() override { ... }
```

Note the discipline in that comment: the hack is gated behind an environment variable,
labelled as temporary, and its removal condition is stated. **A pipeline accumulates
these.** Mark them or they become permanent.

---

## 3. Function Discovery as a Committed Artifact

Function discovery deserves its own file because it is the stage you will re-run most
and trust least.

### Where entry points come from

In rough order of reliability:

1. **A completed decompilation project.** Module 22's `luigismansion` was chosen because
   [Yasiki](https://github.com/Moddimation/Yasiki) is 100% complete -- every function
   named, every structure documented, nothing to discover heuristically. This is not a
   small advantage; it removes the entire problem.
2. **Symbol tables and exception tables.** Present in some ELF and XEX2 files. Free and
   correct when they exist.
3. **The entry point plus recursive descent.** Follow every direct call and branch. This
   is the workhorse and Module 6 covered it.
4. **Prologue pattern matching.** Reliable on compiler-generated code from a known
   toolchain, unreliable on hand-written assembly and on functions that the compiler
   decided did not need a standard prologue -- which is exactly where N64Recomp's split
   bug in Module 20 comes from.
5. **Runtime observation.** Boot the program and log where it actually branched.
6. **Pointer scanning.** Look for code-shaped integers in read-only data.

### Ranks 5 and 6 are not the same rank

This is the lesson Module 14 drew from `civrev`, and it belongs in your pipeline
architecture rather than your debugging technique.

A pointer-shaped integer in read-only data is a **guess**. A logged branch target is an
**observation**. `civrev`'s vtable scan produced 301 candidates and made the build
*worse*, because the scanner could not distinguish a vtable slot from a switch-table
entry, and switch-table entries point into the middle of functions. One boot with a
tolerant dispatch scaffold produced 21 addresses, every one guaranteed real.

Final hint count: 24, down from 301, and an entire class of bug disappeared.

**So build the tolerant-dispatch scaffold early and treat it as a pipeline stage**, not
as an emergency measure. Its job description is: run the program, do not die on an
unknown indirect target, log it, continue. Module 14 has the implementations.

### Give it a file format

Whatever your discovery produces, write it to a file your recompiler reads, and commit
that file. Two real examples of the shape:

- N64Recomp-style TOML config with explicit function entries
- ReXGlue manifests -- `worms_manifest.toml` is 8.4 KB, `ydkj_manifest.toml` 5.9 KB,
  both committed alongside three files of code

That second one is instructive. `ydkj` needed exactly **one** hand-added function entry
for a 14,781-function binary; `civrev` needed 24 for 40,067. Those manifests are small,
they are the accumulated knowledge of the entire bring-up, and they are the only part of
the project that could not be regenerated.

---

## 4. Batch Processing and What It Buys

Once one target runs unattended, running fifty is a loop. That is when you learn things
that single-target work cannot show you.

`gb-recompiled` reports **98.94%** of a 1,609-ROM library recompiling successfully. Note
what that number is and is not: it is a *batch* result, and it measures "the tool emitted
C that compiled" -- the README is explicit that most of those games are not playable. But
as a measure of *the recompiler's robustness across inputs*, it is exactly right, and you
cannot get it without a batch harness.

`3dsnes` reports 340 of 375 games (91%) drawing a real 3D scene, and its README is careful
about provenance: an unattended run over the whole corpus, **"not by spot-checks."**

That phrase is the standard to hold yourself to. If you cannot re-derive your
compatibility figure by running one command tonight, you do not have a figure -- you have
an impression. Module 37 is entirely about this distinction.

### What a batch harness needs

- **Isolation.** One target's crash must not stop the run.
- **A timeout.** Some inputs hang. Assume it.
- **Machine-readable output.** One row per target, so results are diffable between runs.
- **Failure categories, not a pass/fail bit.** "Extraction failed," "codegen failed,"
  "compile failed," and "linked but crashed" are four different engineering problems and
  the counts move independently.

The corpus has a tool for driving exactly this:
[recomp-harness-mcp](https://github.com/sp00nznet/recomp-harness-mcp), an MCP server that
lets agents "discover, build, recompile, and run a collection of static-recompilation
projects." Whatever drives it, the shape is the same -- a machine-readable inventory of
targets and a uniform way to build and run each one.

---

## 5. Automated Symbol Import

When your target has a decompilation project, importing its symbols is the single highest
leverage automation you can write.

What a decomp gives you:

- Function boundaries -- which deletes the hardest problem in Module 6
- Function names -- which makes generated C readable and diffs meaningful
- Data structure definitions -- which Module 19 needs for signature recovery
- Sometimes matching C, which is ground truth for differential testing

The N64 and GameCube scenes are rich here (Super Mario 64, Ocarina of Time, Wind Waker,
Twilight Princess, Metroid Prime, Melee, Paper Mario). `Rampage` and `pokemonsnap` commit
`symbols/` and `PokemonSnapSyms/` directories for exactly this reason.

Write the importer as a stage that converts the decomp's symbol format into your own
function-set file, and **re-run it** rather than copying results by hand. Decomp projects
keep improving; a manual import is stale the day you do it.

---

## 6. Caching, Hashing and Honesty

Give every stage a cache key: the hash of its inputs plus the version of the tool that
produced it. Then two useful properties fall out.

**Incremental re-runs.** Change the function set, and extraction does not re-run.

**Provenance.** You can answer "which binary produced this result?" -- which matters more
than it sounds, because the most common cause of an irreproducible bug report is two
people using different dumps of the "same" game. `pcrecomp`'s PE tooling computes section
hashes for precisely this reason.

Record, per run: the input hash, every tool version, the full command line, and the
output hash. When you publish a number, publish that record with it.

---

## 7. What Not to Automate Yet

A caution, because this module is the beginning of a semester about engineering and the
failure mode of that semester is building infrastructure instead of recompiling things.

Automate a step when you have done it by hand three times and it was the same three
times. Before that you do not yet know what the step is. The corpus is full of one-off
`dump_*.py` scripts -- `burnout3/tools/` alone has a dozen (`dump_awd.py`,
`dump_textures.py`, `dump_vertex_colors.py`, `dump_strip_transitions.py`) -- and that is
the correct state for exploratory work. They became tools when they stopped changing.

The pipeline is for the path you have already walked. Keep a scratch directory for the
path you are still finding.

---

## Labs

- **Lab 51** -- Pipeline driver: build a stage-based driver with content-hash caching that
  takes a ROM to generated C, skipping stages whose inputs are unchanged.
- **Lab 52** -- Batch harness: run a directory of ROMs through the pipeline unattended,
  with per-target timeouts and isolation, emitting a machine-readable report with failure
  categories.

---

**Next: [Module 34 -- Automated Lifting at Scale](../module-34-lifting-at-scale/lecture.md)**
