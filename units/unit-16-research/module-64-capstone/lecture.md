# Module 64: Capstone

Four semesters. You can take a binary apart, lift it, shim the hardware around it, build a
pipeline that does it repeatably, produce evidence for what you claim, make it fast enough
to use, package it so a stranger can run it, and tell the difference between a project that
works and one that looks like it does.

This is the last module. It asks you to do one thing properly and say something true about
it.

---

## 1. Choose One

Four shapes, all legitimate, all complete answers to this module. Pick by what you want to
exist afterwards.

### A. Bring a new architecture up

Module 56's feasibility report, then the toolkit, then the first game.

**Done when:** a second, different program runs on the toolkit (Module 58 §2).

The most valuable and the least glamorous. The corpus has thirty of these and there are
hundreds of machines left — and Module 61 §9 has a shovel-ready one in Palm OS.

### B. Ship a port

Take a target to a rung on Module 37's ladder that you name in advance, and take it all the
way through Unit 12 — verified input, legible failures, save states, rebindable input, a
README a stranger can follow.

**Done when:** someone else runs it from the README without asking you anything.

### C. Answer an open question

Module 61's list, Module 62's method. A number nobody has, with a corpus and a published
method.

**Done when:** the number exists, the method is reproducible, and you would have published
the opposite answer.

The cheapest of the four in wall-clock time and the one most likely to be cited.

### D. Make a real contribution to someone else's project

Module 57. A fix with a regression test, a named gap filled, a Vulkan backend, a second game
on somebody's toolkit, a decomp fed the traces it needs.

**Done when:** it is merged, or clearly rejected for a stated reason.

---

## 2. What Every Shape Must Produce

Whatever you choose:

**A falsifiable claim.** One sentence stating what you did, in terms that could be checked.
"Recompiles Jelly Monsters to native C, ~100% of executed instructions, verified against a
VIC-20 interpreter over a 3,600-frame trace" — not "recompiles VIC-20 games."

**Evidence proportionate to the claim.** Module 37's ladder, stated explicitly. If you are at
rung 5, say rung 5.

**A method someone can repeat.** One command (Module 62 §8).

**An honest scope section.** What it does not do.

**Attribution.** Every toolkit, emulator, decomp and person you built on, by name.

**A negative result.** At least one thing you tried that did not work, written where the next
person will look. Module 60 §1 — this is the single most under-supplied artifact in the
field, and the one you can produce for free.

---

## 3. Audit Your Own Work

Before you call it finished, run Module 37's ten-minute audit on your own repository as
though you had never seen it:

1. What does the `.gitignore` say is missing, and what does that do to your claims?
2. `ls src/` — how much is hand-written harness?
3. `wc -l` both halves.
4. **Is your fallback silent? Would your project "work" if every recompiled function were
   wrong?**
5. What drives the frame loop — the game, or your code?
6. Do you print `successful` and `failed`?
7. Could a reader re-derive any number in your README?

Question 4 is the one. Modules 11, 12 and 37 exist because several real projects would have
answered it badly, and two of them said so publicly and were better for it.

If the audit finds something, **fix the claim before you fix the code.** A project described
accurately is finished; a project described inaccurately is a liability regardless of how
good the code is.

---

## 4. Then Give It Away

The last step, and the one this course has been arguing for since Module 1.

**Publish it** where the platform's community already is (Module 63 §5).

**Write down what you ruled out.** Your dead ends are somebody's saved week.

**Answer the boring questions in writing.** The fifth person to ask is a documentation bug.

**Make your open work visible.** A status file with "Not Started" rows is how a project gets
contributors (Module 57 §4).

**Credit generously and specifically.** Name the person and the artifact, and say what it
gave you.

---

## 5. What This Course Was Actually About

Not any particular architecture. Those were examples, and half of them will be superseded.

The through-line, stated plainly now that you have the whole thing:

**Deciding what counts as a function is the hardest unglamorous problem in this field.** It
showed up as N64 fallthrough splits, an inflated PS3 count, 301 hints making a build worse,
and codegen emitting more functions than discovery found. Four architectures, one bug.

**An observation beats a guess.** A pointer-shaped integer in read-only data is a guess; a
logged branch target is an observation. 301 versus 21. This is the whole argument for
trace-guided everything.

**The runtime is the hard part.** The lifter is bounded mechanical work. The OS, the GPU, the
audio and the timing are unbounded, and that is where the months go.

**Your harness can produce the evidence you were hoping to see.** A green orb at 60fps drawn
by 2,204 return-zero stubs. A menu drawn from hardcoded strings. A game that plays perfectly
because an emulator is underneath it. Ask what your evidence would look like if you were
wrong.

**Say what is true.** The projects in this corpus that retracted a claim — a screenshot, a
function count, a decoder that turned out to be copying its own code — are better projects
for it, and they are the ones this course could learn the most from.

That last one is not a moral point. It is the engineering one. Every hour this field spends
rediscovering something somebody already knew is an hour lost to a claim that was too
optimistic to be useful, or a dead end nobody wrote down.

---

## 6. Deliverables

- [ ] One shape from §1, chosen in advance and stated in the README
- [ ] A falsifiable claim, in one sentence
- [ ] Your rung on Module 37's ladder, stated
- [ ] Evidence proportionate to the claim, re-derivable by one command
- [ ] An honest scope section
- [ ] At least one documented negative result
- [ ] Attribution, by name, for everything you built on
- [ ] The ten-minute audit, run on yourself, with anything it found either fixed or disclosed
- [ ] Published where the relevant community will find it

---

## 7. Go and Do Something Strange

A closing note, in the spirit of the corpus this course was built from.

The consoles are well covered. The interesting work is at the edges — a 4-bit Tamagotchi
whose paging instruction compiles to nothing, a Newton whose "machine code" is bytecode for
a stack VM, a Dreamcast memory card with its own CPU, a Game Boy game running natively on a
Dreamcast, a PS3 firmware emulator recompiled so it can keep emulating.

None of those were obvious. Several were argued about in a repository called `recomp-ideas`
before they got one of their own. Most of the machines ever built have never had anything
recompiled from them at all.

Pick one nobody has done. Measure it honestly before you commit. Write down what you find,
including the parts that did not work.

---

**Course complete.** Semesters 1-4, 64 modules.

If you build something, the community is at the [sp00nznet recomp
Discord](https://discord.gg/CRpzGWZFcu). If you find an error in this course — and there will
be errors — [open an issue](../../../../../issues). Module 37 applies here too.
