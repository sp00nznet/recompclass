# Module 51: Decompilation-Assisted Recompilation

Decompilation and recompilation are usually described as alternatives. In practice the most
productive projects in this corpus use both, and the reason is simple arithmetic: a
decompilation project has already solved, by hand, the problem your recompiler is worst at.

---

## 1. Two Communities, One Artifact

**Decompilation** aims to recover source code — ideally *matching* source, which recompiles
byte-for-byte to the original binary. It is enormous manual effort and produces something a
human can read and maintain.

**Recompilation** aims for functional equivalence, automatically, without caring what the
original source looked like.

The artifact they share is the **symbol file**: a mapping of addresses to names, sizes and
types. The decomp community produces it as a by-product of the work. Your recompiler wants
it more than almost anything else.

---

## 2. What It Actually Buys

Module 22's comparison is the clearest in the corpus, and worth restating as an
argument rather than a fact.

[luigismansion](https://github.com/sp00nznet/luigismansion) was chosen deliberately because
the [Yasiki](https://github.com/Moddimation/Yasiki) decompilation is **100% complete**:

- Every function has a known name and signature
- All data structures are documented
- A complete symbol map exists
- **No unknown functions to discover heuristically**

Module 20's [racer](https://github.com/sp00nznet/racer), same era, comparable console:

- No decompilation exists — *"we're flying blind"*
- 878+ functions discovered by the tool
- **143 functions hand-fixed** after discovery split them incorrectly

Same technique, same class of machine, and one project deleted an entire phase of work.

Concretely, a decomp removes or reduces:

| Problem | Module | Effect |
|---|---|---|
| Function boundary detection | 6, 34 | gone — boundaries are given |
| Fallthrough splits | 20, 34 | gone — the recurring root cause disappears |
| Which addresses are code | 33 | gone |
| Readable generated output | 41 | `Player_Init`, not `sub_80056780` |
| Signature recovery | 19 | types are documented |
| Understanding what a function does | all of it | somebody wrote it down |

That fifth row matters more than it looks. Module 19's optimisation work depends on knowing
argument types; Module 47's modding support depends on being able to name guest state. Both
come free.

---

## 3. Import It, Do Not Copy It

Module 33 §5's rule, stated as a workflow.

Decompilation projects improve continuously. A symbol file you pasted into your repository
in March is stale in April, and you will not notice.

**Write an importer**, not a copy:

```
decomp repo ──▶ import script ──▶ your function-set file ──▶ recompiler
   (upstream)     (yours)           (committed)
```

Module 36's argument applies: the *imported result* is derived state and belongs in your
output directory; the *import script and its configuration* are decisions and belong in
version control.

The corpus does commit the results — `Rampage` ships a `symbols/` directory,
`pokemonsnap` a `PokemonSnapSyms/` — which is reasonable when the upstream moves slowly.
Commit them if you like, but keep the script that regenerates them, and record which
upstream commit you imported from. That last part is Module 33's provenance requirement,
and it is what lets you tell whether an upstream fix has reached you.

---

## 4. Partial Decompilations Are Still Worth a Lot

The instinct is that a 30% decomp is not worth using. It is, and Module 23's Wii material
says why: *"Even partial decompilation results are useful — a 30% matched decomp still gives
you thousands of function names."*

Because the value is not uniformly distributed. Decompilation projects work outward from
the engine core and the most-called routines, so the *first* 30% is disproportionately the
code your profile is concentrated in (Module 41 §1) and the code your modders want to touch.

**Use what exists, fall back to heuristics for the rest**, and mark which is which — a
function named `Player_Init` from a decomp and a function named `sub_80056780` from your
analyser have different trustworthiness, and your generated code should show that.

---

## 5. Matching Decomps as Ground Truth

A fully matching decompilation compiles to a byte-identical binary. That is a much stronger
artifact than a symbol file, and it gives you something Module 38 spent a whole module
constructing: **a second implementation you can differentially test against.**

If the decomp's C, compiled with the original toolchain, produces the original binary, then
the decomp's C *is* the specification. Your recompiled output should behave identically, and
you can compare at function granularity with known-correct expected behaviour.

The N64 and GameCube scenes have several of these — Super Mario 64, Ocarina of Time, Wind
Waker, Twilight Princess, Metroid Prime, Melee, Paper Mario. If your target is one of them,
Module 38's oracle problem is already solved and you should build the harness before writing
a lifter.

---

## 6. Feeding Back

The relationship goes both ways, and this is the part most recompilation projects miss.

Your recompiler produces things a decomp project wants:

**Discovered function boundaries** the decomp has not reached yet. Your recursive descent
covers the whole binary; their hand work covers the part they have got to.

**Execution traces.** Module 49 §4's recorded playthrough tells a decomp team which of their
unmatched functions actually run, which is a prioritisation they otherwise guess at.

**Divergence reports.** If your recompiled output and their matching C disagree, one of you
is wrong, and finding out is valuable to both.

**Confirmation that a behaviour is real.** "This looks like a bug in the original" is easier
to believe when two independent implementations reproduce it.

Module 15's `Rampage` ships a `symbols/` directory; Module 12's `lttp-recompiled` produced
ten upstream fixes to the toolkit it stressed. **Contributing back is Unit 15's subject**,
and decompilation projects are the most natural place to start because the artifact you have
is exactly the one they want.

---

## 7. The Honest Limits

**A decomp does not give you a port.** It gives you names and boundaries. Everything in
Modules 15, 40 and 43 — runtime, timing, memory — is still yours.

**Matching decomps constrain the compiler.** The original toolchain, flags and sometimes
the exact compiler build. That is their problem, not yours, but it means their source is not
necessarily buildable with what you have.

**Licences differ.** A decompilation project has its own licence and its own legal posture
(Module 45), and importing its symbols is using its work. Check, and attribute by name.

**Symbol files can be wrong.** They are human work in progress. A misnamed or mis-sized
function propagates straight into your discovery, and Module 34's fallthrough detector is
worth running over imported boundaries too.

---

## Labs

- **Lab 103** -- Symbol importer: write a script that converts a decompilation project's
  symbol format into your recompiler's function-set file, records the upstream commit it
  imported from, and reports what changed since the last import.
- **Lab 104** -- Matching decomp as oracle: for a target with a matching decompilation,
  build a function-level differential test comparing your recompiled output against the
  decomp's compiled C, and report coverage and any divergences.
- **Lab 105** -- Feed back: produce an artifact useful to a decompilation project — an
  execution trace ranking their unmatched functions by how often they run, or a list of
  boundaries your discovery found that their map lacks — and offer it upstream.

---

**Next: [Module 52 -- Machine Learning for Binary Analysis](../module-52-ml-binary-analysis/lecture.md)**
