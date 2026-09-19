# Module 46: Packaging and Distribution

Module 45 established the constraint: you ship the tool, the user brings the game. This
module is about making that workflow something a person who is not you can complete.

It is the least glamorous unit in the course and it is where most projects quietly fail —
not because the recompilation was wrong, but because nobody else could ever run it.

---

## 1. The Shape of the Workflow

Every user has to traverse the same path:

```
their own copy  ──▶ extract ──▶ recompile ──▶ build ──▶ run
   (disc, ROM,       (assets +    (generate     (compile   (with their
    package)          binary)       C code)      + link)     assets)
```

Your job is to make each arrow a documented command that either works or says exactly why
it did not. Module 36's manifest is what makes this possible: the knowledge that used to be
in your shell history is in a file the user already has.

The standard the corpus converges on is three commands. `afterburner`'s README:

```bash
rexglue codegen
cmake --preset win-amd64-release
cmake --build out/build/win-amd64-release
```

No flags to get wrong, identical to what CI runs and to what the maintainer runs. Module 36
§4 argues for presets on cache-correctness grounds; this is the user-facing reason.

---

## 2. Verify the Input Before You Use It

The single highest-value thing you can add, and most projects add it only after the tenth
confused bug report.

Users will bring the wrong region, a bad dump, a different revision, a re-release, or a
file that is not the game at all. If your pipeline consumes that silently, they get a
crash a thousand lines later and file an issue about your recompiler.

**Hash the input and say what you found.** Module 33's provenance record is the same idea:
*"which binary produced this result?"* is the most common cause of an irreproducible
report. `pcrecomp`'s PE tooling computes section hashes for exactly this reason.

A good check tells the user three things:

```
Expected: Rev A (US), SHA-256 3f9a...
Found:    Rev B (EU), SHA-256 71c4...
This project targets Rev A. Rev B has different function addresses
and the manifest hints will not apply.
```

That is not the same as refusing to proceed. Accept the input, warn loudly, and record what
you used — an unknown revision is often worth trying, and the user should know that is what
they are doing.

Module 35's CI lesson applies here too: **a check that never fires is not a check.** Test
yours against a deliberately wrong file.

---

## 3. Extraction Is Where Users Get Stuck

Module 33 catalogued the container formats. From a packaging perspective what matters is
that each one has a step the user may not know how to do.

| Source | What the user has | What they must do |
|---|---|---|
| Cartridge ROM | a file | nothing |
| Disc image | an ISO/GCM/XGD | extract a filesystem |
| XBLA / GoD | a package | extract STFS, then decrypt the XEX |
| PS3 | a disc or PKG | decrypt SELF to ELF |
| Floppy | `.do`/`.dsk`/`.woz` | reconstruct what the loader puts in memory |
| Protected PC binary | an installed game | run it and dump memory (Module 27) |

**Automate every step you legally can, and document the ones you cannot.** Where a step
needs keys or tools you cannot distribute, say so plainly and name what is required rather
than leaving the user to guess.

`flow`'s repository structure shows the convention: an `extracted/` directory the user
populates, gitignored, with the expected layout documented. The user knows exactly what
goes where and your tooling knows exactly where to look.

---

## 4. Make Failure Legible

Your users are debugging a pipeline they did not write, against a binary you have and they
may not, on a platform you did not test. Almost everything they experience will be a
failure, so failures are your main user interface.

Borrow directly from the corpus:

**Categorise, do not just fail.** Module 33 §4's failure categories are a user-facing
feature: "extraction failed" and "linked but crashed" send the user to completely different
parts of your documentation.

**Name the address.** Module 30's spin watchdog turns a hang into `func_009653C0`. A bug
report containing an address is actionable; "it freezes" is not.

**Say what you ruled out.** `outrun`'s README documents a red herring — an early suspect
that turned out to be a harmless call on another thread. Users hit the same red herrings
you did; writing them down stops the same issue being filed five times.

**Log the environment.** Tool versions, input hash, manifest hash, host OS. Module 33's
provenance record, printed at startup, resolves a large share of reports without a single
follow-up question.

---

## 5. Documenting Where the Project Actually Is

Module 37's argument, applied to the README that a stranger reads first.

Status tables work well because they are specific about partial progress.
`pokemon-crystal` uses `⏳ user-test` as a distinct state — "I believe this works, nobody
has played through a save round-trip." `ydkj` and `civrev` both carry an **Honest scope**
heading. `crazytaxi` opens by saying it does not draw a frame yet and points readers at a
different project that does.

The packaging-specific version of this: **tell the user what they will see if it works.**
"You should reach the title screen; the menus are not driven yet" prevents an entire
category of issue, because the user can tell success from failure without asking you.

And keep it current. A README claiming more than the build delivers is the same failure
Module 37 catalogues, experienced by someone who trusted you enough to spend an evening on
it.

---

## 6. Distribution, Within the Constraint

You cannot ship a build containing recompiled game code (Module 45 §5). You *can* ship
everything else, and the more of it you ship as binaries the fewer users bounce off a
toolchain.

- **The recompiler and tools** — prebuilt binaries remove "install a C++ toolchain" from
  the critical path. `3dsnes` ships Windows builds from CI on tagged releases.
- **The runtime as a library**, so the final link is fast.
- **A project template** the user drops their generated code into. `xboxrecomp` ships
  `templates/`; the ReXGlue projects are four files plus a manifest precisely because the
  template carries everything else.
- **CI-built artifacts** so "does it build on a clean machine" is answered continuously
  rather than by your users.

For updates, the thing that matters most is that **the user's regenerated code stays
valid**. If a runtime change requires regenerating, say so in the release notes and version
the manifest format. A user who updates the runtime and gets a link error against last
month's generated code has no way to diagnose that.

---

## 7. Multi-Platform, If You Went That Way

Module 9's `linksawakening-portable` runs the same recompiled game on PlayStation 4, PS3,
3DS, Wii, Dreamcast, Android and WebAssembly. Each platform supplies a backend implementing
one shared interface; the recompiled game does not change.

From a packaging standpoint that multiplies everything — toolchains, packaging formats,
signing, testing. The thing that makes it tractable is that it is *configuration*
(Module 36 §4), not a fork. One build system, one interface, N backends, and the porting
instructions in one place: that project keeps them in `docs/BUILDING.md`.

If you are not going to maintain a platform, do not list it. A backend nobody has built in
a year is a bug report waiting to happen, and Module 37's honesty standard covers platform
support claims too.

---

## Labs

- **Lab 83** -- Input verification: add hash-based identification that names the revision
  and region it found, warns clearly on a mismatch without refusing to proceed, and prints
  a provenance record. Test it against a wrong file and confirm the message is useful.
- **Lab 84** -- Fresh-machine run: on a machine that has never seen the project, follow only
  your own README. Record every point you had to know something undocumented, then fix the
  documentation until the run is clean.

---

**Next: [Module 47 -- User Experience and Modding Support](../module-47-ux-modding/lecture.md)**
