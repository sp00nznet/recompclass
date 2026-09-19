# Module 55: Undocumented and Unsupported Hardware

The consoles in Semester 2 all had something in common that is easy to stop noticing:
somebody else had already done the hard part. An emulator existed. Hardware registers were
documented on a wiki. A decompilation project had named the functions.

This module is about targets where none of that is true — where the first deliverable is
not a recompiler but **a measurement of whether recompilation is even the right technique
for this machine.**

---

## 1. Stop Assuming, Start Measuring

[cybikorecomp](https://github.com/sp00nznet/cybikorecomp) targets the Cybiko: a 2000
handheld with a **Hitachi H8S/2241** at 11 MHz, 512 KB of flash holding an OS called CyOS,
a 32 KB internal boot ROM, a QWERTY keyboard, and a 900 MHz packet radio that let a room
full of them form a mesh. Roughly 400 applications shipped.

Its README sets up the comparison with Module 53 explicitly, and the framing is the point
of this whole module:

> The [Tamagotchi](https://github.com/sp00nznet/tamarecomp) was recompilable *because of*
> its ISA — a 4-bit core whose only page-changing instruction took an immediate, so every
> jump target in the ROM was a build-time constant. The H8S is a general-purpose register
> machine, and its calls go through registers. **That changes what "statically
> recompilable" is even allowed to mean here, and the first job is measuring it honestly
> rather than assuming.**

Two things to take from that.

**"Statically recompilable" is a property of a specific ROM on a specific ISA**, not of the
technique. Module 53's target was recompilable because of an architectural accident. This
one may not be, and the honest move is to find out before committing.

**The first deliverable is a number.** Not a recompiler — a measurement of how much of this
binary you can resolve statically, and what the remainder looks like.

---

## 2. Analyse the Whole Machine, Not Half of It

`cybikorecomp`'s `docs/INDIRECT.md` opens with a mistake worth stealing, because everyone
makes it:

> CyOS and the boot ROM are separate files but **not separate worlds** — CyOS calls down
> into the boot ROM constantly, for `memcpy` and `memset` among others. Analysed apart,
> every such call is a "target outside the image". `tools/cyimage.py` glues them into one
> space (`0x000000` boot ROM, `0x200000` SRAM), and that alone took unresolved transfers
> from **2,533 to 227**.

A 91% reduction in the hardest problem in the field, from *assembling the address space
correctly before analysing it*. No cleverness, no solver.

And the second-order effect is better still:

> It also removed all 12 "undecodable opcodes", which were **never decoder gaps** — they
> were misaligned decodes caused by tracing into a region the other half owned.

Twelve apparent ISA gaps that were not ISA gaps. Had the project trusted that symptom, it
would have spent a day on the H8S manual looking for instructions that decode fine.

**Before you conclude anything about a binary, make sure you are looking at the whole
machine as the machine sees it.** Separate files, overlays, banked regions, a boot ROM, a
loader — if the guest sees one address space, so must your analysis.

---

## 3. Classify What Is Left

227 unresolved transfers is still a lot. The next move is not to solve them — it is to find
out what they *are*, by backward-scanning each site's basic block for the last write to the
register being called through:

| defining instruction | sites | what it is |
|---|---|---|
| `mov.l @(d:16,ERm), ERn` | 178 | a field of a struct — **C++ virtual dispatch** |
| `mov.l @aa:16, ERn` | 43 | a fixed address in on-chip RAM |
| `mov.l @ERm, ERn` | 3 | a pointer |
| `mov.l @aa:24, ERn` | 1 | `0x200004` |
| nothing in the block | 2 | argument, or set further back |

And the conclusion:

> **Three different problems, not 227.**

That sentence is the method. An undifferentiated pile of 227 unknowns is intimidating and
unactionable. Three mechanisms — vtable dispatch, a fixed dispatch table in RAM, and genuine
pointers — are three tractable pieces of work with different solutions, and you can now
estimate each.

**Classify before you solve.** It costs an afternoon of backward scanning and it converts an
unbounded problem into a scheduled one. Module 14's tiering is the same instinct applied at
runtime; this is it applied at analysis time.

---

## 4. When Your Memory Model Assumption Breaks

[vmurecomp](https://github.com/sp00nznet/vmurecomp) targets the Dreamcast VMU's **Sanyo
LC8670** — an 8-bit CPU inside a memory card, which is itself a peripheral of a console this
course already covered in Module 24.

Its `docs/CPU.md` states something that quietly invalidates an assumption baked into most of
this course:

> Two **disjoint** address spaces:
> - **ROM**, 64 KB, used for instruction fetch and by `LDC`.
> - **RAM**, 512 bytes, used for every operand and every peripheral.

Address `0x100` in ROM and address `0x100` in RAM are different locations. Every memory
model in Modules 43 and 53 assumed one address space where an address identifies a location.
Here the *instruction* determines which space you are in.

Harvard architectures are common in microcontrollers and they break:

- A single `mem[]` array.
- Module 43's "guest address plus a base offset is a host address."
- Any analysis that follows a pointer without knowing which space it points into.

None of that is hard once you know. All of it is baffling if you assume a flat space and
watch your data reads return instruction bytes.

**Read the CPU's memory model before writing the memory layer.** And note the honest framing
of that document: *"This is not a datasheet — it records the decisions the decoder and
runtime had to make, and which of them rest on published facts versus convention."*
Separating what is documented from what is convention is exactly the discipline Module 37
asks for, applied to your own understanding.

The VMU also has three clock settings (32.768 kHz, 600 kHz, 6 MHz) selectable at runtime via
`OCR`, with game mode at 600 kHz. Module 40's timing problem, where the guest changes the
clock rate underneath you.

---

## 5. Where Information Comes From When There Is No Wiki

In rough order of reliability:

**The silicon vendor's datasheet.** The CPU is usually a commodity part — Epson, Sanyo,
Hitachi — and its datasheet is often findable even when nothing about the *product* is.
This is the single highest-value search, and it is a search for the chip, not the device.

**Another implementation.** Module 53's oracle was BrickEmuPy. An emulator by someone else,
in another language, from the same datasheet, is both a reference and a cross-check.

**The boot ROM.** It is small, it runs first, and it is the most structured code on the
device. It also usually contains the routines everything else calls.

**The corpus.** Four hundred Cybiko applications, or an entire Newton software archive, tell
you which instructions and which OS calls actually matter. An encoding used by nothing can
wait.

**Homebrew and SDK documentation.** If anyone ever shipped a development kit, its headers
name the hardware registers.

**Measurement on real hardware**, when you have one. The only source that settles a
disagreement.

And the standing rule from Module 37: **record which of your facts are published and which
are inference.** Six months later you will not remember, and a guess that has hardened into
an assumption is how a project gets stuck.

---

## 6. The Radio, the Keyboard, and the Rest of the Device

A closing caution specific to unusual hardware: the CPU is often the *easy* part.

The Cybiko has a 900 MHz packet radio and a mesh protocol. The VMU is a peripheral that
talks to a Dreamcast. [nokia-recomp](https://github.com/sp00nznet/nokia-recomp) targets
**phone firmware** — a device whose entire purpose is a radio protocol stack.

Module 15's argument scales past consoles: the runtime is the hard part, and on a device
built around a communications peripheral, the communications peripheral *is* the runtime.

Decide early whether you are reproducing that behaviour or stubbing it, and say which in the
README. "Runs single-player apps; radio is stubbed" is a perfectly good scope, honestly
stated. "Recompiles Cybiko applications" without that caveat is Module 37's problem.

---

## Labs

- **Lab 93** -- Assemble the address space: given a device whose code lives in two or more
  images, build a single combined address space and measure the change in unresolved
  transfers and apparent decoder gaps before and after.
- **Lab 94** -- Classify the unknowns: backward-scan each indirect transfer site for the
  defining write to its target register, group the sites by mechanism, and produce a table.
  Estimate the work for each group separately.
- **Lab 95** -- Harvard memory model: implement a memory layer for a CPU with disjoint code
  and data spaces, and write the test that catches an implementation which conflates them.

---

**Next: [Module 56 -- Picking Your Own Frontier](../module-56-your-own-frontier/lecture.md)**
