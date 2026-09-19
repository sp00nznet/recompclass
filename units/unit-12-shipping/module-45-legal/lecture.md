# Module 45: Legal Considerations

**This module is not legal advice.** It is a description of what practitioners in this
field actually do and why, written by people who are not lawyers. Copyright law varies by
country, the specifics of your situation matter, and if anything here is load-bearing for
a decision you are about to make, talk to someone qualified.

What this module *can* usefully do is explain the structural choices the corpus makes with
remarkable consistency, because those choices shape your architecture. The legal position
is not a disclaimer you add at the end — it determines what your repository contains, how
your build works, and what your users have to do.

---

## 1. The One Rule Everything Follows

Every port in this corpus says a version of the same sentence:

> Bring your own disc; **no game files included**.

> **No game data here.** Disk images (`.do`/`.dsk`/`.woz`) are `.gitignore`d. This repo is
> the recompiler, the runtime, and docs — bring your own floppy.

> This repo is the recompiler, the runtime and docs — bring your own dump **that you
> legally own**.

And the architectural consequence, from Module 37's audit:

```
LinksAwakening/.gitignore      rom.c, rom_rom.c
oracle-recompiled/.gitignore   ages/oracle_of_ages.c, ...
lttp-recompiled/.gitignore     recomp_out/, *.gba
ducktales/.gitignore           src/recomp/, game/
flow/.gitignore                src/recomp/*.c, game/EBOOT.*, game/USRDIR/
```

**The recompiled output is gitignored too, not just the ROM.** That is the part people miss
and it is the important one.

The reasoning practitioners give: recompiled code is mechanically derived from the
copyrighted original. Translating a work does not create a new work free of the original's
rights — a translated novel is still the novelist's. So the generated `rom.c` is treated as
carrying the same restrictions as the ROM it came from, and is not redistributed.

**Ship the tool, not the output.** The recompiler, the runtime, the shims, the manifest and
the documentation are your work. The user supplies their own copy and generates the rest
locally.

---

## 2. What This Costs You, and Why It Is Worth Saying

Module 37 §6 draws the consequence for evidence: **for most ports you cannot verify the
headline numbers from the repository at all**, because the interesting half is not there.
"4.2 million lines of C" and "99.8% native" are claims about files that were never
committed.

That is the correct trade and it has a cost, so state it. When you publish a figure, say
whether a reader could check it. Some projects choose otherwise —
`diddykongracing` commits `RecompiledFuncs/funcs_0.c` through `funcs_16.c`, megabytes of
generated C, and `bolo` commits its whole `src/recomp/gen/` tree. Both are older or
smaller-rightsholder titles, and both are consequently the most auditable ports in the
corpus.

There is a real tension here between verifiability and caution, and different projects
resolve it differently. Notice which one you are choosing rather than drifting into it.

---

## 3. Your Own Licence, and Other People's

Your toolkit and runtime are your work and you choose their licence. This course and most
of the corpus use MIT.

Where it gets interesting is **what you linked**.

Module 11's `snesrecomp` does not reimplement the SNES — it wraps
[LakeSnes](https://github.com/sp00nznet/LakeSnes), and the README is specific that LakeSnes
is **MIT licensed**. That is not incidental detail; it is why the wrapping is possible
under a permissive licence at all. Had the chosen emulator been GPL, `snesrecomp` and
everything linking it would have to be GPL too.

This decides real architectural questions:

| If your hardware reference is | Then |
|---|---|
| MIT / BSD / zlib | link it, keep your licence, preserve their notices |
| GPL | your combined work is GPL — fine if you intend that, fatal if you do not |
| LGPL | dynamic linking keeps you separate; static linking has conditions |
| No licence at all | you have no permission; "it's on GitHub" is not a licence |

**Check before you build on it, not after.** Retrofitting a licence change onto a project
that already links a GPL emulator means replacing the emulator.

`xboxrecomp` carries a `LICENSES/` directory and a `NOTICE` file alongside its own
`LICENSE` — the standard way to handle a project with several third-party components, and
worth copying.

### Forks inherit

`mxo-hd-recomp` describes itself as a *"Private fork of hdneo/mxo-hd (MIT)"*. When you fork,
you take the upstream licence with you and you keep its notices. Attribution is both a
legal obligation under most permissive licences and, per this course's general position,
the right thing regardless.

---

## 4. Clean-Room and What It Actually Means

"Clean room" gets used loosely. The strict version is two teams: one reads the original and
writes a specification containing no expression from it, the other implements only from
that specification and never sees the original.

**Static recompilation is not clean room and does not pretend to be.** You are
deliberately, mechanically deriving from the original binary. That is the whole technique.

The corpus contains both approaches and keeps them separate — alongside the recomp
projects there are clean-room reimplementations (OpenSaints, `catzng`, `fallout1-re`,
`fallout2-re`), which are a different activity with a different legal posture.

Do not describe a recompilation as clean room. It is inaccurate, and inaccuracy about the
method is the fastest way to lose the benefit of the doubt.

---

## 5. Things That Change the Picture

**Distributing a build.** Handing someone a compiled executable containing recompiled game
code is distributing the derived work — a different act from publishing a tool. This is the
line most projects deliberately do not cross, and the reason the standard workflow makes
the *user* run the recompiler.

**Circumventing protection.** Module 27's `xwa` dumps memory after SafeDisc decrypts
itself; Module 33 describes this as the general technique. Anti-circumvention rules exist
in many jurisdictions and are separate from copyright, and this is an area where the answer
genuinely depends on where you are.

**Delisted and abandoned titles.** Several projects in the corpus exist because the game is
gone — `outrun` pulled in 2011, `afterburner` in 2015, `tokyojungle` digital-only with both
developers dissolved. That is a strong *motivation* argument and it is not a legal one.
Copyright does not lapse because a storefront closed.

**Firmware and system libraries.** Module 30's `flow` decrypts and recompiles Sony's real
`libsre.prx`. Module 20's `diddykongracing` documents bypassing three anti-piracy checks.
Both are technically interesting and both extend past the game binary into the platform
holder's code.

**Assets versus code.** Your recompiled code needs the user's assets. A screenshot in your
README shows the rightsholder's art. Most projects include screenshots; some credit them
(`pokemon-crystal` captions one *"Suicune silhouette, ©2001 GAME FREAK"*). Marking them is
cheap.

---

## 6. Practical Checklist

What the corpus does, in a form you can copy:

- [ ] **`.gitignore` the ROM, the assets, and the generated output.** Not just the ROM.
- [ ] **Say "bring your own copy" in the README**, in the first paragraph.
- [ ] **Licence your own work explicitly.** No licence means nobody may use it.
- [ ] **Audit what you link** before you build on it, and preserve every notice.
- [ ] **Keep a `NOTICE` / `LICENSES/` directory** once you have more than one dependency.
- [ ] **Do not distribute builds** containing recompiled game code.
- [ ] **Do not call it clean room.**
- [ ] **Describe your method accurately**, including the parts that sound worse.
- [ ] **Credit prior work by name.** Module 1's acknowledgements exist for this reason.

That last pair is the theme of this whole course. Module 37 argues for honesty about what
your project *does*; this module argues for honesty about what it *is*. The same
discipline, applied to a different kind of claim.

---

## Labs

- **Lab 81** -- Dependency audit: for a recompilation project, enumerate every third-party
  component, its licence, and how it is linked. Produce a `NOTICE` file and state whether
  the project's declared licence is compatible with everything it uses.
- **Lab 82** -- Ship-the-tool workflow: restructure a project so a user with their own copy
  can go from binary to running build with documented commands, and confirm a fresh clone
  contains no copyrighted material.

---

**Next: [Module 46 -- Packaging and Distribution](../module-46-packaging/lecture.md)**
