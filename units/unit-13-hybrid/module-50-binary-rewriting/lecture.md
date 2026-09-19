# Module 50: Binary Rewriting and Patching

Static recompilation is not the only way to change a program you do not have the source to.
There is an adjacent family of techniques — **binary rewriting** — that modifies the binary
in place rather than translating it to another language, and it is worth knowing well for
three reasons.

It solves some problems better than recompilation does. It shares infrastructure you can
borrow. And the research community around it is far larger than the game preservation one,
so a great deal of relevant work is published under names you would not search for.

---

## 1. The Distinction

| | Recompilation | Rewriting |
|---|---|---|
| Output | C or LLVM IR, then a new binary | a modified binary of the same format |
| Runs on | the host architecture | the original architecture |
| You can | change anything, retarget anything | insert, patch, and instrument |
| Needs | full lifting and a runtime | only the parts you touch |
| Fails when | discovery is incomplete | a patch disturbs layout or a computed address |

The load-bearing difference: **rewriting keeps the original architecture.** It is for
instrumenting, hardening or fixing a program that already runs somewhere, not for moving it
somewhere new. If your goal is "run this Xbox game on a PC," rewriting cannot help. If it is
"fix a bug in this shipped binary" or "measure what this program does," it is often the
better tool.

---

## 2. The Research You Should Know

Four projects that share infrastructure and vocabulary with this field, from the course's
own reference list.

**RetroWrite** [Dinesh, Burow, Xu & Payer, IEEE S&P 2020] statically rewrites
commercial-off-the-shelf binaries to insert fuzzing and sanitizer instrumentation — giving
you AddressSanitizer-style checking on a binary you have no source for. The interesting
part for us is what makes it work: it recovers enough *relocation* information to move code
without breaking references, which is exactly the problem Module 54 §1 used relocation
density to diagnose.

**rev.ng** [Di Federico, Payer & Agosta, CC 2017] lifts binaries to **LLVM IR** and recovers
control flow graphs and function boundaries. That second half is Module 34's recurring root
cause, attacked as a research problem with published evaluation. If you are building
discovery, this literature is directly applicable.

**BinRec** [Altinay et al., EuroSys 2020] combines **dynamic traces with static lifting** —
runtime information guiding recompilation. Module 49 §4 is the practical version of the same
idea; BinRec is the formal treatment, and worth reading before you convince yourself
trace-guided discovery is a hack.

**LeanBin** [Wodiany, Pop & Luján, arXiv 2024] lifts and recompiles specifically to
**debloat** — removing code to shrink attack surface. Module 44 §1's problem, from a
security motivation: `wormsrevolution` reaches 444 of 88,816 functions, and debloating asks
exactly which code is live.

These communities do not usually talk to each other, and the vocabulary differs — "lifting"
is shared, but preservation people say "recompilation" where security people say "rewriting"
or "binary analysis." Searching the other field's terms is a cheap way to find solved
problems.

---

## 3. LLVM IR as a Common Target

Three of those four go to LLVM IR rather than C. Worth taking seriously, because this
course has emitted C throughout.

**What LLVM buys:** a mature optimiser, a retargetable backend, and existing analysis
infrastructure. Module 7's `gb-recompiled` IR exists partly to enable *"future backend
support (e.g., LLVM)."*

**What C buys, and why the corpus chose it:**

- **Readability.** Module 54's `newtcc` output is meant to be read, with the original
  source line recoverable. LLVM IR is not read by people.
- **Portability by default.** Module 9's `linksawakening-portable` runs on PS3, 3DS, Wii and
  Dreamcast — platforms whose toolchains are C compilers, not LLVM versions you control.
- **Debuggability.** You can step through generated C in an ordinary debugger.
- **Nothing to install.** Every platform has a C compiler.

The v2 course paper notes the natural extension point: N64Recomp maps instructions to
abstract `BinaryOp`/`UnaryOp` types before its `CGenerator` emits C, and *"a different
generator backend could target LLVM IR, Rust, or any other language."*

**If you build an IR, keep the backend swappable.** That is the real argument for the IR
layer in Module 34 — not optimisation, which the C compiler already does, but the option to
emit something else later.

---

## 4. Patching: The Smallest Useful Version

Sometimes you do not want to translate the program at all. You want to change six bytes.

The corpus does this constantly, and it is worth recognising as a distinct technique rather
than a hack:

- **Module 20's DRM bypass.** `diddykongracing`'s three `IO_READ` anti-piracy checks read
  hardware registers that fail under recompilation. The fix is to neutralise the checks —
  patching, not lifting.
- **Module 30's tolerance flags.** `--protect_zero=false` and an indirect-call override
  change behaviour without changing code.
- **Module 47's mod overrides.** `RECOMP_PATCH` at the same address, last constructor wins.

The last one is the interesting inversion: **once a program is recompiled, patching gets
easier, not harder.** A ROM hack must not change any size; a recompiled program's "patch" is
a C function with no space constraint and a debugger.

So the pipeline `recompile → patch in C` is often better than `patch the binary` even when
patching was the whole goal, and it is a legitimate reason to recompile something you never
intend to port.

---

## 5. Instrumentation Without Recompiling

Rewriting's home ground, and you should reach for it when you need to *understand* a binary
rather than move it.

Module 38 §2's oracles are all instrumentation problems. `encarta`'s `DECO_32 oracle` loads
the real DLL and drives its exports — no rewriting needed, because the binary already runs
on the host. But if your target binary runs on the host and you need per-function
observation, inserting instrumentation is a smaller job than lifting.

`ida-recomp-toolkit` in the corpus is described as a *"headless IDA Pro toolkit for
cross-validating static recompilation projects (PSX/N64)"* — using a commercial analysis tool
as an independent check on recompiler output. Same instinct as Module 53's third-party
oracle: **somebody else's implementation is worth more than another of yours.**

---

## 6. When Rewriting Beats Recompiling

Be honest about this, because "I know how to recompile" is a bad reason to recompile.

**Rewriting wins when:**
- The program already runs where you need it.
- You only want to change a small part.
- The change is measurement, not behaviour.
- Full discovery is infeasible but the region you care about is clear.

**Recompiling wins when:**
- You are moving to a different architecture. (The reason it exists.)
- You want the program in a language people can read and modify.
- You want to retarget many platforms from one source (Module 9's seven).
- The point is preservation — a C source tree outlives a binary and its rewriter.

**Neither wins when** what you actually want is a reimplementation. The corpus contains
clean-room reimplementations alongside recompilations (Module 45 §4) because they are
different activities. If the goal is a maintainable modern codebase rather than a faithful
port, recompilation may be the wrong technique entirely.

---

## Labs

- **Lab 101** -- Patch versus recompile: take a behaviour you want to change in a shipped
  binary, implement it both as a byte patch and as a recompiled override, and compare the
  effort, the fragility, and what each approach lets you do next.
- **Lab 102** -- Read the adjacent literature: pick one of RetroWrite, rev.ng, BinRec or
  LeanBin, read the paper, and write a page on which of its techniques transfer to a
  recompilation project in this course and which do not, with reasons.

---

**Next: [Module 51 -- Decompilation-Assisted Recompilation](../module-51-decomp-assisted/lecture.md)**
