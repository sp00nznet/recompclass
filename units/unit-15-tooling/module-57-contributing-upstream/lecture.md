# Module 57: Contributing Upstream

By now you have used other people's toolkits extensively. This module is about the return
trip — and it is in the course because the corpus demonstrates something counterintuitive:
**the contribution is often worth more than the port.**

---

## 1. The Clearest Example in the Corpus

Module 12 examined [lttp-recompiled](https://github.com/sp00nznet/lttp-recompiled), a GBA
project whose repository contains exactly two files — a README and a `.gitignore`. No code.
Eighteen commits, all documentation.

Judged as a port, it is nothing. Read the commit subjects:

```
ARM MSR/MRS fix: IRQ handler runs clean, 600+ frames, forced-blank parity
Document IRQ-table-uninitialized root cause + 3rd gbarecomp fix
EEPROM_V (8KB) emulation - sixth upstream gbarecomp fix
Diagnose Four Swords link-cable state-machine gate (7th gbarecomp fix)
Eighth upstream gbarecomp fix: minimal SIO transfer sim
README: 10th upstream fix (Thumb MOV pc, rN fall-through) + state-machine progress
```

**Ten upstream fixes to the toolkit**, each found by driving one hard game through it until
it stopped.

Every one of those fixes now benefits every future GBA project. The port did not ship. The
toolkit got materially better. That is a good outcome, and it is invisible unless somebody
names it.

---

## 2. Why Bring-Up Finds Toolkit Bugs

There is a structural reason a serious port is the best bug-finder a toolkit can have, and
it is worth understanding so you expect it rather than resenting it.

A toolkit is developed against its author's targets. Those targets exercise the instructions
they use, the peripherals they touch, and the code patterns their compiler emitted. A
toolkit that works on three games is a toolkit that works on the union of three games.

Your target uses a different subset. It has a different compiler's idioms, a peripheral
nobody tried, an instruction encoding the author never hit. So:

| Your symptom | Usually |
|---|---|
| One instruction behaves wrong | a lifter bug — yours or theirs |
| A peripheral never responds | unimplemented in the runtime |
| A whole class of function mis-splits | a discovery bug (Module 34) |
| It works except in one mode | an unhandled configuration |

Three of those four are upstream bugs, not yours. The `lttp` list is exactly this
distribution: an ARM `MSR`/`MRS` fix, a Thumb `MOV pc, rN` fall-through, an `STRH`
interpreter bug, EEPROM emulation, SIO simulation.

**Assume a fraction of your blockers are upstream.** Not all of them — Module 38's
discipline exists because "it's their bug" is a comfortable and often wrong conclusion — but
enough that you should be checking.

---

## 3. Making a Contribution That Gets Merged

The difference between a report that lands and one that sits is almost entirely about
reproducibility, and every technique you need is already in this course.

**Minimise it.** Module 39 §4's nested bisection: shrink the input, then bisect the code.
A maintainer who receives "this 8 MB ROM crashes" has a project; one who receives "this
four-instruction sequence produces the wrong flag" has a fix.

**Isolate it from your project.** If it reproduces with a synthetic fixture (Module 35 §2),
the maintainer does not need your game, your assets, or your build.

**Bring the differential evidence.** "Our lifter emits X, the interpreter produces Y, here
is the register state at divergence" is a bug report nobody can argue with. Module 38 is how
you get it.

**Bring a test.** A synthetic fixture that fails before and passes after is the single
highest-value thing you can attach, because it is what stops the bug returning.

**State what you ruled out.** Module 46 §4's argument. "It is not endianness — the 16-bit
half tests clean" saves the maintainer the hour you already spent.

**Say what you cannot share.** If it only reproduces on a copyrighted binary you cannot
attach, say so up front and describe the shape instead.

---

## 4. Where the Open Work Actually Is

Module 32 pointed at [`ps3recomp`'s `MODULE_STATUS.md`](https://github.com/sp00nznet/ps3recomp/blob/main/docs/MODULE_STATUS.md),
which tracks every HLE module as Not Started / Stubbed / Partial / Complete. **Check it
before starting**, because it moves — but the shape of what it exposes is stable and worth
studying as a model.

The gaps it named at the time of writing:

| Gap | Why it is open |
|---|---|
| **Vulkan RSX backend** | D3D12 renders real titles, Metal covers macOS, Vulkan is unwritten — and it is what Linux and Android need |
| `cellVdec` | callbacks and AU submission work; no actual H.264/MPEG-2 decode |
| `cellAdec` | same shape — AAC/ATRAC3+ decode missing behind working plumbing |
| `cellSpurs` | management APIs and event flags real; **no actual SPU execution** |

Three of those share a shape worth naming: **the plumbing is done and the payload is
missing.** That is an unusually good contribution target, because the interface is already
pinned down by a working caller, so you can tell immediately whether your implementation is
right — which is Module 52 §1's rule about mechanically checkable work, applied to choosing
what to build.

The Vulkan backend is the one to take if you want your work used. "Linux and Android cannot
run any of this" is a real limitation with a named cause.

### Other kinds of contribution that are undervalued

**Documentation.** Most toolkits in this corpus are under-documented relative to what they
do. `xboxrecomp` ships 25 files and is the exception; several ship none.

**A second game.** Module 56 §4: the second title on a toolkit is what proves it is a
toolkit. It finds every place the code was accidentally specific to the first game.

**A corpus run.** Module 39 §5: running a toolkit over hundreds of inputs and reporting
categorised failures is work most authors have never done on their own tool.

**Honest status.** Filing "this README claims X, the code does Y" is a real contribution.
Module 37 exists because somebody did that.

---

## 5. When to Fork and When Not To

Forking is sometimes correct and usually premature.

**Contribute upstream when** the fix is general, the project is maintained, and your target
is not unusual.

**Fork when** your target needs behaviour that conflicts with theirs, the project is
unmaintained, or you need a different licence and the licence allows it.

The corpus does both openly. `gb-recompiled` is *"a fork of arcanite24/gb-recompiled"* with
upstream credited in every README that touches it. `mxo-hd-recomp` is *"Private fork of
hdneo/mxo-hd (MIT)."* `LakeSnes` is forked from angelo-wf, and `snesrecomp` names it.

**If you fork, say what you changed and why**, and keep the upstream link prominent. A fork
that hides its origin is both a licence problem (Module 45 §3) and the attribution failure
this course has been arguing against throughout.

---

## 6. Contributing to Decompilation Projects

Module 51 §6 covered the artifacts; this is the practical note.

Decomp projects want: discovered function boundaries they have not reached, execution traces
ranking their unmatched functions by how often they actually run, and divergence reports
when your output and their matching C disagree.

That last one is the most valuable and the least offered. If a matching decompilation exists
and your recompiled build behaves differently, exactly one of you is wrong, and finding out
is worth a great deal to both projects.

**Approach it as a peer, not a consumer.** Their work deleted an entire phase of yours
(Module 51 §2). Leading with what you can give back is both accurate and effective.

---

## Labs

- **Lab 109** -- Upstream a fix: find a genuine bug in a toolkit you use, minimise it to a
  synthetic fixture with no dependency on your target, write the differential evidence and
  a regression test, and submit it.
- **Lab 110** -- Fill a named gap: pick an explicitly documented gap in a project's status
  file, implement it against the interface its existing callers already define, and report
  how you verified it.

---

**Next: [Module 58 -- Designing a Toolkit Others Can Use](../module-58-toolkit-design/lecture.md)**
