# Module 54: Bytecode Targets — When the "Machine Code" Is a VM

Every target so far shipped machine code for a physical CPU. A large amount of software
does not. It ships **bytecode for an interpreter**, and that changes the first question you
have to answer.

There are two programs in front of you — the application's bytecode and the interpreter
that runs it — and "recompile this" could mean either. They are different projects with
different costs, and choosing wrong costs you months.

---

## 1. First, Notice That You Have One

The failure mode here is not choosing badly. It is not realising there is a choice, pointing
a machine-code recompiler at the binary, and spending two weeks lifting an interpreter loop
while wondering why nothing resembles the game.

[worldempire](https://github.com/sp00nznet/worldempire) is the diagnostic worked example —
*World Empire* (1994), a Visual Basic 3 title, described as *"a `pcrecomp` target — but not
the target you would first point it at."*

```
EMPIRE.EXE   411,785 bytes   NE, Microsoft linker 5.10, Windows
             15 segments, 114,025 bytes of "code"
             imported modules: VBRUN300     <- and nothing else
             relocations: 14 total, 13 of them internal
```

Two numbers settle it, and both are cheap to compute on any binary:

**One imported module.** *"A native Windows program cannot draw a pixel or open a window
without KERNEL, USER and GDI. This one never calls them."* If a program's only import is
somebody's runtime DLL, the program is not doing the work — the runtime is.

**Fourteen relocations across 114 KB.** *"Native 16-bit code of that size carries thousands;
The Even More Incredible Machine has 4,743 across 197 KB in the folder next door. Fourteen
means almost nothing in those segments is machine code at all."*

That comparison — against a known-native binary of similar size from the same era — is the
technique. **Relocation density is a proxy for "is this really code."** Machine code is full
of absolute addresses that need fixing up at load time; a blob of p-code is not.

And the entry point confirms it in nine bytes: a single call to `VBRUN300.100`
(`THUNRTMAIN`), handing the whole program to the runtime.

### Other signatures worth knowing

| Signature | Suggests |
|---|---|
| One import, and it is a runtime DLL | bytecode for that runtime |
| Very low relocation density | the "code" segments are data |
| A tiny entry point that immediately calls out | a hosted program |
| A large table of short, uniform records | a literal or frame pool |
| `.class`, `.jar`, `.dex`, `.pkg` containers | JVM, Dalvik, NewtonScript |

---

## 2. The Three Strategies

### Recompile the interpreter

Treat the runtime as your target and the bytecode as data. You get *every* program for that
runtime at once, and you get the interpreter's semantics for free because you did not have
to understand them.

You also keep the interpreter's dispatch overhead — you have made the interpreter native,
not the program. And it is only worth it when the runtime is the redistributable part.

Module 30's `twistedmetal-psn` is the most extreme instance in the corpus: it recompiles the
PS3 firmware's own **PS1 emulator** (`ps1_netemu`) in order to run a PSOne Classic. You
statically recompile an emulator so it can keep emulating. Sit with that one.

### Recompile the bytecode

Translate the application's bytecode to C and reimplement the runtime's primitives as
native functions. Now the program is genuinely native, and you pay for it by having to
understand the VM's semantics exactly — and by doing it again for every application.

This is what [newtonrecomp](https://github.com/sp00nznet/newtonrecomp) does, and §3 is about
how.

### Reimplement the runtime and keep the bytecode

Write a fresh, fast interpreter or JIT. Not recompilation at all, but sometimes the right
answer, and worth naming so you reject it deliberately.

### Choosing

| Ask | Leans toward |
|---|---|
| Do you want one program or all of them? | one → bytecode; all → interpreter |
| Is the VM documented? | no → interpreter (its semantics come free) |
| Is the runtime huge? | yes → bytecode |
| Do you need native speed for the app's own logic? | yes → bytecode |
| Is the bytecode a thin wrapper over native code? | yes → neither; find the real target |

That last row matters. Module 30's `metalslug2` is a PS3 shell around a Neo Geo emulator;
the PS3 layer is not where the game is.

---

## 3. A Stack VM Without a Stack

`newtonrecomp` targets **NewtonScript bytecode** — *"A Newton application is not machine
code. It is a graph of frames, and the functions inside it are NewtonScript bytecode for a
small stack VM."*

Its central design decision is the one to take away from this module:

> NewtonScript is a stack VM, but **a recompiler that emits a runtime stack array and a `sp`
> is just an interpreter with extra steps.** The stack depth at every pc is statically
> determined, so each stack slot becomes a plain C local (`s[0]`, `s[1]`, …) with no pushing
> or popping at run time.

That is the whole trick, and it generalises to every stack VM — JVM, CLR, p-code, Forth.
**Stack depth is a static property.** Walk the bytecode, track the depth at each pc, and
every "push" becomes an assignment to a numbered local that the C compiler will put in a
register.

The output:

```c
/*   46: find-var 0                  ; 'GameBoard */
s[0] = newt_find_var(cx, lit[0]);
/*   47: get-var 5                   ; ix */
s[1] = v[5];
/*   48: freq.aref 2                  */
s[0] = newt_aref(cx, s[0], s[1]);
/*   50: freq.aref 2                  */
s[0] = newt_aref(cx, s[0], s[1]);
/*   52: freq.not-equals 6            */
s[0] = newt_not_equals(cx, s[0], s[1]);
/*   53: branch-if-false 84           */
if (!newt_truthy(s[0])) goto L_84;
```

That is `if GameBoard[ix][iy] <> 0 then …` from *Newtris* — **and the C says so.**

Two more decisions worth copying:

**The output is meant to be read.** *"every line carries its bytecode pc and disassembly,
literals appear by name, locals by name."* Bytecode carries symbol information that machine
code lost at compile time — names of locals, names of slots, literal values. Use it.
Bytecode recompilation can produce genuinely readable C, which machine-code recompilation
essentially never can.

**Hot built-ins lower to direct calls.** The `freq-func` built-ins are *11% of all
instructions in the archive* and become direct calls rather than a dispatch.

---

## 4. Where Bytecode Bites You

Bytecode is friendlier than machine code in every way except one: **the encoding is
bespoke, undocumented, and has traps that fail silently.**

`newtonrecomp`'s `BYTECODE.md` records two.

**The gap.** *"**Opcodes 1 and 2 are unused** — that gap is what makes the table look
'shifted' if you guess at it."* Guess the table from examples and everything after opcode 2
is off by two.

**The escape.** The encoding is `opcode:5 | a:3`, and `a == 7` means a 16-bit operand
follows. That applies to the simple-op set too:

> `pop-handlers` is simple-op 7, and 7 cannot fit in the 3-bit field, so it is encoded
> **`07 00 07`** — three bytes. Read it as one and the two operand bytes masquerade as a
> `pop` and another `pop-handlers`, which **silently corrupts every function containing a
> `try` block**. Across the archive the escape occurs **10,818 times** and its operand is
> always 7.

Read that failure mode carefully, because it is characteristic of bytecode work. The
misparse does not crash. It produces *plausible instructions*, and only in functions with
exception handlers. Your recompiler works on most of the corpus and quietly mangles a
subset.

The defence is the same one Module 39 §5 argues for: **verify against a corpus, not an
example.** `newtcc` has a mode for precisely this — `python tools/newtcc.py check unna.zip`
stack-verifies a whole archive. If your depth tracking is wrong anywhere, the stack will not
balance, and the corpus tells you where.

That is a stronger check than it first appears. A stack VM has an invariant — depth must
balance at every merge point and at return — that you can verify **without running
anything**, across thousands of programs.

---

## 5. Other Bytecode Targets in the Corpus

[doomrpgrecomp](https://github.com/sp00nznet/doomrpgrecomp) recompiles *Doom RPG* (2005),
a **J2ME** title. Java bytecode is the best-documented VM you will ever target, and the work
shifts almost entirely to reimplementing the phone runtime — MIDP, the display, key handling.

Contrast that with NewtonScript, where the VM was the hard part and the runtime is small.
**The balance between "understand the VM" and "reimplement the runtime" flips** depending on
how well-documented the VM is, and that ratio should drive how you schedule the work.

[tstorecomp](https://github.com/sp00nznet/tstorecomp) is the inverse case again: *The
Simpsons: Tapped Out* ships a native ARM64 engine with scripting on top, so the native engine
is the target and the scripts are data.

---

## 6. A Method

1. **Check the imports and the relocation density** against a known-native binary of similar
   size. Two numbers, ten minutes.
2. **Find the entry point and see how far it gets** before handing off.
3. **Decide which program you are recompiling**, explicitly, and write down why.
4. **If it is the bytecode:** get the encoding exactly right, including escapes and gaps,
   and verify against a corpus rather than an example.
5. **Compute static stack depth** and turn the stack into locals.
6. **Use the symbol information** the bytecode retained. The output can be readable.
7. **Reimplement the runtime's primitives** as native functions, hot ones as direct calls.

---

## Labs

- **Lab 90** -- Is it bytecode? Given several binaries, compute import counts and relocation
  density, compare against known-native references, and classify each. Justify each
  verdict with numbers.
- **Lab 91** -- Stack-to-locals: for a small stack VM, compute static stack depth at every
  pc, emit C with numbered locals instead of a runtime stack, and verify depth balances at
  every merge point across a corpus.
- **Lab 92** -- Encoding traps: implement a bytecode decoder with a multi-byte escape, then
  write the corpus check that catches a misparse which produces plausible-but-wrong
  instructions rather than an error.

---

**Next: [Module 55 -- Undocumented and Unsupported Hardware](../module-55-undocumented-hardware/lecture.md)**
