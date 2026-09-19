# Module 60: Documentation and Community

This field runs almost entirely on oral tradition. Techniques live in scattered blog posts,
Discord scrollback, and the heads of people who worked something out and moved on. This
course exists because that was true and it did not need to be.

This module is about the part of the work that outlasts your project.

---

## 1. Write Down What You Ruled Out

The most under-supplied form of documentation in this field, and the cheapest.

Bring-up is mostly eliminating plausible wrong answers. You will spend a day proving
something is *not* the cause, feel like you achieved nothing, and move on — and then someone
else will spend the same day on the same wrong answer, and so will you, in four months.

The corpus does this well in places:

`outrun` documents a ruled-out red herring: an early suspect — a failed `ShaderDump` device
probe — turned out to be *"a harmless get-file-size on a different thread."*

`tamarecomp`'s validation doc records two harness bugs that impersonated CPU bugs: Windows
`stdout` expanding `0x0A` into `0x0D 0x0A` in a binary trace (giveaway: `X = 0x0A0D`, an
impossible value for a 12-bit register), and the reference advancing its oscillator inside
`clock()` while the runtime only moved time in `tama_step`.

`encarta`'s `differential-test the 16-bit half too; instruction semantics are clean`
eliminated a whole layer and found no bug at all — which Module 38 §6 argues is the most
valuable kind of result.

**A negative result is a result.** Record it where the next person will look.

---

## 2. Commit Messages Are the Documentation

Something this course discovered while being written: the best material in the corpus is not
in the READMEs. It is in the commit logs.

READMEs describe a current state, get edited, and lose their history. A commit log is a
narrative with timestamps that nobody rewrites — which is why Module 18 reads `encarta`'s
`IR32:` sequence commit by commit, and why `lttp-recompiled`'s ten upstream fixes are
visible at all.

Compare two ways of saying the same thing:

```
fix decoder bug
```
```
IR32: 16-bit addresses wrap, they do not sign-extend - fault fixed
```

The second tells you the class of bug, the wrong assumption, and the symptom. It is
searchable by anyone hitting the same thing on any platform.

Some patterns worth stealing, all real:

- **State the finding, not the action.** `the decode core is 32-bit; measure bitness instead
  of guessing`
- **Record the correction.** `correct the decode-gap diagnosis - it was FS/GS prefixes`
- **Retract explicitly.** `retract "it decodes" - the buffers were copies of its own code`
- **Give partial results honestly.** `segment 3 to 92.5%, and stop reporting unhandled as zero`
- **Name what is still broken.** `the pipeline runs clean; the values are still wrong`

---

## 3. Document the Machine Separately From the Project

Two different lifespans, so two different files.

**Project documentation** — status, how to build, what works — is current-state and will be
wrong next month.

**Machine documentation** — the ISA, the memory model, the peripherals — is what you learned
about hardware, and it outlives your project entirely. Someone writing an emulator, a
disassembler, or a completely different recompiler wants it.

`vmurecomp`'s `docs/CPU.md` sets the standard, in its opening lines:

> This is not a datasheet — it records the decisions the decoder and runtime had to make,
> and **which of them rest on published facts versus convention**.

That distinction is the single most useful thing a machine document can carry. Six months on
you will not remember which of your facts came from a datasheet and which from watching a
program behave. An inference that has hardened into an assumption is how a project gets
stuck, and how a wrong fact propagates into everyone who reads your notes.

Mark them. `<!-- inferred -->` costs nothing.

---

## 4. Publish Numbers With Their Method

Module 37's standard, stated as a documentation rule.

`3dsnes`: 340 of 375 games (91%) draw a real 3D scene, *"verified by an unattended run of
the whole corpus rather than by spot-checks."*

`gb-recompiled`: 98.94%, 1,592 of 1,609 — with *"most of the games are not fully playable
yet"* attached in the same line.

`tokyojungle`: a function count revised **downward**, with the reason.

The rule: **a number without a method is an impression.** If you cannot re-derive it by
running one command tonight, either build the command or stop publishing the number.

---

## 5. Credit By Name

This course's standing position, and it is both a licence obligation (Module 45 §3) and
simply correct.

The corpus does it consistently: `gb-recompiled` credits arcanite24 in every downstream
README; `snesrecomp` names LakeSnes and angelo-wf; `recomp_patch.h` credits N64Recomp for
the macro; `luigismansion` credits the Yasiki decompilation that made it viable; this
course's README names Mr-Wiseguy, Dario Samo, Skyth, Sajid, rexdex and arcanite24.

Three things that make attribution actually useful rather than ceremonial:

**Name the person and the artifact.** "Thanks to the community" credits nobody.

**Say what it gave you.** "Yasiki is 100% complete, so there were no unknown functions to
discover" tells a reader why it mattered.

**Keep it where people look.** The README, not a `CREDITS` file nobody opens.

And its inverse, from the same principle: **do not claim firsts you cannot verify.** "The
first X" is a claim about everyone else's work, and it is usually wrong because somebody did
it quietly in 2009. Describe what you did.

---

## 6. Writing for the Person Who Arrives Confused

Most readers of your documentation are stuck, not curious. Optimise for that.

**Lead with what the project is and is not.** `crazytaxi` opens by saying it does not draw a
frame yet — and points at a different project that does. Pointing people away from your own
repository when it is not the best example is worth more than a good screenshot.

**Say what success looks like.** "You should reach the title screen; the menus are not driven
yet" prevents an entire category of issue, because the reader can tell success from failure
without asking you (Module 46 §5).

**Put the numbers where they can be checked.** Link the file, name the commit.

**Assume they have a different dump than you.** Module 46 §2's input verification is a
documentation problem as much as a code one.

---

## 7. Community

The practical part, briefly.

**A place to ask.** This corpus has the [sp00nznet recomp
Discord](https://discord.gg/CRpzGWZFcu). The value is not the chat — it is that people find
out what others are stuck on before duplicating a month of work. `ps3recomp`'s README says
exactly that: a good place *"to find out what people are stuck on before you duplicate the
effort."*

**Make the open work visible.** Module 57 §4: `ps3recomp`'s `MODULE_STATUS.md` doubles as a
contribution roadmap because it names what is Not Started. A project with no visible gaps
gets no contributors.

**Answer the boring questions in writing.** The fifth person to ask the same thing is a
documentation bug.

**Be generous with the unglamorous artifacts.** Execution traces, symbol files, feasibility
reports, "this does not work and here is why." These are cheap for you and expensive for
everyone else to reproduce.

---

## 8. Why This Unit Exists

Static recompilation's history is a series of people independently rediscovering the same
things: that a basic block is not a function, that a working screenshot proves less than it
seems, that the runtime is the hard part, that an observation beats a guess.

Every one of those is in this course because somebody wrote it down in a commit message or a
README, and it was still there years later to be found.

That is the whole argument. **Write it down where it will still be when you have moved on.**

---

## Labs

- **Lab 115** -- Machine document: write the ISA and memory-model notes for a target you
  have worked on, explicitly marking every statement as published fact or inference, and
  have someone who has not worked on it try to use the document.
- **Lab 116** -- Negative results: go through a project's history, find three things you
  ruled out, and write them up where the next person will look. Include at least one harness
  bug that impersonated a target bug.

---

**Unit 15 Capstone (Lab 117)**: Contribute something real to a project you did not write —
an upstream fix with a regression test, a documented named gap filled, a second game on
someone's toolkit, or a feasibility report that saves the next person the work — and write
up what it took.

---

**Next: [Module 61 -- Open Problems](../../unit-16-research/module-61-open-problems/lecture.md)**
