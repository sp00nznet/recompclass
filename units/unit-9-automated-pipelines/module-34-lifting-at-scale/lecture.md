# Module 34: Automated Lifting at Scale

Module 7 taught you to write lifting rules by hand, one instruction at a time. That
approach works, and every lifter in this course's reference corpus started that way. It
stops working for two reasons: the tenth architecture, and the gigabyte of output.

This module is about both -- how to stop hand-writing the same lifter, and what happens
to your build when the generated C outgrows the machine.

---

## 1. Where Instruction Semantics Should Live

The first structural decision is where the meaning of `ADC` lives. There are three honest
answers, and the corpus contains all three.

### Option A: in the emitter

The straightforward approach from Module 7 -- a `switch` on opcode, each case writing C
text. `tirecomp/tools/z80recomp/emit.c` does this, and for a 64KB Z80 target it is
correct and boring, which is the right combination.

The cost is that semantics and output format are welded together. Wanting a second
backend, or a static analysis that needs to know what an instruction *does*, means
rewriting.

### Option B: in a runtime header

`snesrecomp/include/snesrecomp/cpu_ops.h` puts one macro or inline function per 65816
instruction into a header, over a global CPU state:

```c
#define OP_SEI()  (g_cpu.flag_I = true)

static inline void op_rep(uint8_t val) {   /* REP #imm -- clear specified flags */
    uint8_t p = cpu_get_p();
    p &= ~val;
    cpu_set_p(p);
}
```

The emitter's job collapses to choosing *which* op with *which* operand. The semantics --
including every flag rule you would otherwise get subtly wrong -- are written once,
tested once, and reused by every project on the platform. Its comment says exactly that:
*"game-agnostic. Any recomp project targeting a SNES ROM can use it as a starting set."*

This is the highest leverage-per-line option and it is underused. Your generated code gets
smaller too, because `OP_ADC(x)` is shorter than eight lines of inline flag arithmetic,
and the C compiler inlines it back anyway.

### Option C: in an IR

`gb-recompiled` goes instruction → IR → C:

```
recompiler/include/recompiler/ir/ir.h            the IR opcode set
recompiler/include/recompiler/ir/ir_builder.h    SM83 -> IR
recompiler/include/recompiler/ir/ir_optimizer.h  passes over the IR
recompiler/include/recompiler/codegen/c_emitter.h IR -> C
```

Its header states the motivation: *"The IR layer decouples instruction semantics from
code generation, enabling optimization passes and future backend support (e.g., LLVM)."*

Note what kind of IR it is. Not a generic compiler IR -- SM83 semantics named honestly.
`LD_HL_SP_N` gets its own opcode "for LD HL,SP+n" because that one instruction sets H and
C in a way nothing else does, and calling it an `ADD` loses that. `JUMP_REG` exists
separately because `JP HL` is the hard case and analyses need to find it.

**Choose deliberately.** An IR is worth building when you want more than one backend, or
when you have analyses that need to see the program as structure rather than text.
It is *not* worth building to optimise the output -- the C compiler already deletes your
dead flag writes, which is the main thing an IR pass would catch.

---

## 2. Table-Driven Decoding

Whatever you choose above, the decoder should be a table. Hand-written `switch` trees over
256 opcodes rot; tables are diffable against the ISA manual.

`tirecomp/tools/z80recomp/decode.c` is a clean example -- one row per opcode carrying the
mnemonic, operand kind, control-flow class, and cycles:

```c
/* 0xE8 */ {"RET PE",_NO,BR,0},  {"JP (HL)",_NO,JH,0},  {"JP PE,%s",_A16,BR,0},  {"EX DE,HL",_NO,N,0},
```

The control-flow class (`BR`, `JH`, `N`) is the load-bearing column. Your analyser needs
"is this a branch, a call, a return, or an indirect jump" for every opcode, and deriving
it from the mnemonic string is how you end up with a bug on `JP (HL)` specifically.

**Generate the table from a machine-readable ISA description where one exists.** Ghidra's
**SLEIGH** files cover a remarkable range of architectures and are already written; so are
various JSON opcode tables maintained by homebrew communities. Parsing SLEIGH to emit your
decoder table is a weekend, and it is a weekend you spend once for every architecture you
will ever target.

---

## 3. The Reuse Payoff: One Front End, Many Machines

The strongest argument for separating the CPU front end from the machine around it is in
`vic20recomp`, whose README states it plainly: the decoder, the flag-correct ALU, the
analyzer, the C emitter and the **interpreter oracle** are *the same battle-tested 6502
front-end* that recompiled Apple II games. Only the machine changed.

Look at what that bought:

| Toolkit | CPU | What was new |
|---|---|---|
| [apple2recomp](https://github.com/sp00nznet/apple2recomp) | NMOS 6502 | DOS 3.3 sector loading, hi-res RAM scan-out, speaker soft-switch |
| [vic20recomp](https://github.com/sp00nznet/vic20recomp) | MOS 6502 | cartridge cold-start vector, VIC screen RAM |
| [pacrecomp](https://github.com/sp00nznet/pacrecomp) / [galaxrecomp](https://github.com/sp00nznet/galaxrecomp) | Z80 | arcade tile grid, coin/DIP inputs |
| [tirecomp](https://github.com/sp00nznet/tirecomp) | Z80 | TI-OS traps, LCD driver, keypad |
| [zxrecomp](https://github.com/sp00nznet/zxrecomp) | Z80 | `.z80` snapshot format, ULA attributes |

Two CPU front ends, five platforms. The screen in three of these is *a region of RAM the
hardware scans*, which is why the toolkits look so similar -- and noticing that is what
makes the reuse possible.

**The design rule that enables this:** your lifter must not know what a memory address
means. It emits `bus_read8(addr)` and stops. Everything platform-specific lives behind
that call. The moment your lifter special-cases `0xD020` because that is the border
colour, you have welded it to one machine.

---

## 4. Output Volume Is an Engineering Problem

At scale, generated C stops being text and starts being a build problem. Real numbers from
the corpus:

| Project | Functions | Generated source | Binary |
|---|---|---|---|
| [xwa](https://github.com/sp00nznet/xwa) | 2,701 | 606,424 lines | -- |
| [lttp-recompiled](https://github.com/sp00nznet/lttp-recompiled) | 15,264 | 153 files, 114 MB | 20.8 MB (~30 min build) |
| [civrev](https://github.com/sp00nznet/civrev) | 40,067 | 231 MB C++ | 80 MB |
| [ducktales](https://github.com/sp00nznet/ducktales) | 50,077 | ~2 GB C++ | **1.65 GB** |
| [LinksAwakening](https://github.com/sp00nznet/LinksAwakening) | -- | ~4.2M lines | -- |

A 1.65 GB executable from a PS3 game is not a mistake; it is what literal translation
costs. Plan for it:

**Split into many translation units.** `lttp-recompiled` emits 153 files, `flow` uses 49
chunks. One file per thousand functions is a reasonable default. This is what makes
parallel compilation possible and what keeps any single compiler invocation from running
out of memory.

**Make the split stable.** If adding one function reshuffles which functions land in which
file, every incremental build is a full build. Partition by address range, not by
discovery order.

**Expect the compiler to be the bottleneck, not your lifter.** `lttp` reports ~30 minutes
under MSVC `/O1 /MP` for 114 MB. Your lifter generating that took seconds. Module 41 has
more on this, and Module 35 is about not paying it more often than necessary.

**Do not optimise the generated text for beauty.** Verbose, obviously-correct output that
the C compiler folds away beats clever output you cannot debug. Module 19 covers which
optimisations actually pay.

---

## 5. Deciding What Counts as a Function

This is the recurring root cause in this course, and at scale it stops being a bug and
becomes a *policy* you have to state.

The failures all trace to one mistake -- treating a basic block as a function -- and they
look completely different downstream:

| Symptom | Where | Cause |
|---|---|---|
| 143 / 418 / ~390 / ~879 "fallthrough" fixes | racer, Rampage, pokemonsnap, Rampage 2 | N64Recomp splits functions lacking a standard prologue; the first half runs off its own end |
| Function count inflated, then revised **down** | [tokyojungle](https://github.com/sp00nznet/tokyojungle) | `find_functions` counted intra-function basic blocks |
| Fatal unresolved call after *adding* analysis | [civrev](https://github.com/sp00nznet/civrev) | 301 pointer-scan hints included jump-table entries pointing mid-function |
| Codegen emits more functions than discovery found | [xwa](https://github.com/sp00nznet/xwa) | 2,674 discovered → 2,701 emitted, split at branch targets |

Four projects, four architectures, one bug.

### What to do about it at scale

**Make it detectable.** A function whose last instruction is neither a return nor an
unconditional branch is suspicious on its face. You can find these statically, before
running anything, and every project above eventually wrote that check. Write it first.

**Automate the repair.** racer, Rampage and pokemonsnap all describe *automated*
fallthrough patching. Nobody hand-edits 418 functions twice.

**Count the outstanding ones.** Rampage 2's note -- *"~879 potential 2-instruction
fallthrough functions need systematic fixing"* -- is the right way to hold this: a
counted, categorised debt rather than an unknown number of future mystery crashes.

**Watch the direction of your function count.** If it only ever goes up, check how you are
counting. A number that can only increase is not a measurement.

---

## 6. Generating the Runtime Too

An underrated automation: the parts of the runtime that are mechanically derivable from
the binary should be generated, not written.

- **Import thunks.** You know every import, its ordinal and its name from the import
  table. `pcrecomp`'s `stdcall_argc.py` goes further and derives each import's **stack
  purge from the SDK headers** -- a property of the callee that is not in the binary at
  all and that corrupts the stack on every call if you guess wrong.
- **Dispatch tables.** Module 14's 22,097-entry table is generated from the function set.
- **Stub bundles.** `lttp` emits 7,331 stubs plus 833 trap stubs for unresolved targets,
  so the program links and *tells you* which unresolved target mattered.
- **Build files.** If the translation unit split is generated, the CMake listing them is
  too.

The trap-stub pattern is the one to internalise. An unresolved target does not have to
block the build. Emit something that links and traps loudly, and convert a static unknown
into a runtime observation -- the same move as Module 33's tolerant dispatch.

---

## 7. Knowing When Your Lifter Is Right

Scale makes hand-verification impossible, so you need a mechanical answer, and the corpus
has the same one three times: **keep an interpreter and diff against it.**

`vic20recomp` and `apple2recomp` ship an "interpreter oracle" as a first-class front-end
component. `encarta` ran `differential-test the lifted code against real x86` and the
follow-up `differential-test the 16-bit half too; instruction semantics are clean`. That
second commit is the valuable one -- it did not find a bug, it **eliminated a whole layer
from the search**, proving the remaining fault had to be in addressing and memory layout.

Module 38 builds this properly. For now, the design consequence: when you write the
lifter, write the interpreter for the same ISA from the same decode table. It is a
fraction of the work if you plan for it and a rewrite if you do not.

---

## Labs

- **Lab 53** -- Table-driven lifter generation: parse a machine-readable ISA description
  into a decoder table with control-flow classes, and generate both a lifter and a
  matching interpreter from the same table.
- **Lab 54** -- Fallthrough detector: scan a generated function set for functions that end
  without a terminator, report them, and emit an automated repair.

---

**Next: [Module 35 -- CI/CD for Recompilation Projects](../module-35-ci-for-recomp/lecture.md)**
