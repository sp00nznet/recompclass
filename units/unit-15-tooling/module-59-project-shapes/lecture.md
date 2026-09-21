# Module 59: Project Shapes

Not every recompilation project is trying to be a playable port, and a great deal of
frustration in this field comes from judging one shape by another's criteria.

This module names the shapes the corpus actually contains. The practical value is in
choosing one **before** you start, because the shape determines what "done" means, what you
should measure, and what the README should claim.

---

## 1. The Toolkit

**Goal:** make a platform recompilable.
**Done when:** a second, different game works on it.
**Measure:** how thin the per-game code is (Module 58 §1).

`lynxrecomp`, `apple2recomp`, `tirecomp`, `zxrecomp`, `vic20recomp`, `newtonrecomp`,
`tamarecomp`, `gcrecomp`, `dcrecomp`, `psprecomp`, `vitarecomp`, `iparecomp`,
`androidrecomp`, `model2recomp`, `model3recomp`, `lindberghrecomp`, `systemes3recomp`.

The most valuable shape and the least glamorous, because the screenshots belong to the
ports. Module 57 §2 is the compensation: every fix benefits everything downstream.

---

## 2. The First Game

**Goal:** prove the toolkit on the smallest honest instance of the platform.
**Done when:** it runs, and the toolkit needed no game-specific hacks to make it.
**Measure:** what fraction is recompiled code.

`chipschallenge-lynx-recomp` (*"the first game on the lynxrecomp toolkit"*),
`newtris-newton-recomp`, `blockdude-ti-recomp`, `manicminer-zx-recomp`,
`jellymonsters-vic20-recomp`, `oregontrail-apple2-recomp`, `pacman-arcade-recomp`.

Module 16's selection rule applies: pick something **missing the hardest problem on the
platform**. `missileattack` is the purest statement of it — one code segment, 21 KB, *"does
not have segmentation at all"*, in a collection where El-Fish has 121 segments.

---

## 3. The Second Game

**Goal:** prove the toolkit is a toolkit.
**Done when:** it works and the toolkit absorbed the differences.
**Measure:** what you had to change upstream.

`crystalmines2-lynx-recomp` (*"the second game on the lynxrecomp toolkit"*),
`pokemon-crystal` after `pokemon-gold`, `choplifter` and `oregontrail` together, `Rampage`'s
two titles.

Underrated, and the only shape that actually tests generality (Module 58 §2).

---

## 4. The Flagship Port

**Goal:** one game, as far as it will go.
**Done when:** you pick a rung on Module 37's ladder and reach it.
**Measure:** the rung, honestly.

`LinksAwakening` (playable), `wormsrevolution` (playable, no text), `mk` (playable),
`burnout3`, `civrev`, `flow`, `tokyojungle`, `crazytaxi`, `xwa`.

The shape with the most ways to overclaim, which is why Modules 27, 30 and 37 spend so long
on it. Most of the corpus's honest-scope discipline exists because of this shape.

---

## 5. The Stress Target

**Goal:** find where the toolkit breaks by driving something too big through it.
**Done when:** you stop finding bugs, whether or not the game runs.
**Measure:** upstream fixes produced.

`lttp-recompiled` is the corpus's clearest instance: no code, eighteen documentation
commits, **ten upstream fixes to gbarecomp**. Module 57 §1.

Legitimate and valuable, and it *only* looks like failure if nobody said that was the goal.
If you take this shape, say so in the first paragraph of the README — a status table that
looks like a port in progress invites the wrong reading of honest work.

---

## 6. The Research Log

**Goal:** answer a question about a machine.
**Done when:** the question is answered, including "no."
**Measure:** whether someone else can now skip the work.

`cybikorecomp`'s `INDIRECT.md` is this shape inside a toolkit: *"the first job is measuring
it honestly rather than assuming"*, producing 2,533 → 227 unresolved transfers and a
classification into three mechanisms. `recomp-ideas` is the corpus's explicit home for
*"recompilation targets, argued about before they get a repo."*

Module 56's feasibility report is this shape as a deliverable. **A well-documented "this is
not worth doing, here is why" is a real contribution**, and almost nobody publishes one.

---

## 7. The Preservation Case

**Goal:** the game is disappearing; get it out.
**Done when:** it runs, or the method is documented well enough for someone else to finish.
**Measure:** the same as a flagship port, but urgency changes prioritisation.

`outrun` (delisted 2011), `afterburner` (delisted 2015), `tokyojungle` (digital-only, both
developers dissolved), `encarta`, `prodigy-revival`, `wholeearth`.

Module 45 §5 is the caution: a strong motivation is not a legal argument. But the
prioritisation logic is real — a title with no legal route to purchase and no surviving
developer is a different risk profile from one on three storefronts.

---

## 8. The Novel Capability

**Goal:** do something the original hardware could not.
**Done when:** it does the new thing.
**Measure:** does it work, and is the novelty real?

`3dsnes` (SNES output as 3D voxel scenes, 340 of 375 games),
`linksawakening-portable` (one recompiled Game Boy game on PS4, PS3, 3DS, Wii, **Dreamcast**,
Android and WebAssembly), `honyaku` (LLM translation that recompilation makes insertable),
and the stereoscopic angle `vbrecomp` opens up.

The best argument for the technique, because none of these is achievable by emulation. If
you want to convince someone why recompilation matters, show them a Game Boy game running
natively on a Dreamcast.

---

## 9. The Harness

**Goal:** make working on many projects tractable.
**Done when:** a batch run is one command.
**Measure:** projects covered, failures categorised.

`recomp-harness-mcp`, `ida-recomp-toolkit`, `tools` (*"Reusable SDL2/ImGui toolkit —
screenshot capture, toast notifications, menu system"*), `pcrecomp`'s `tools/`.

Module 33's batch harness and Module 39's corpus runs both live here. Invisible until it
exists, and then everything else gets faster.

---

## 10. Choosing, and Saying Which

The practical advice.

**Pick before you start.** The work differs, and so does the honest README.

**Say which in the first paragraph.** Most misread projects in this corpus are shapes
described as other shapes.

**A shape can change — announce it.** A flagship port that becomes a stress target is fine.
Silently becoming one is how a project looks abandoned.

**Match your measurement to your shape.** Function counts for a toolkit, rung on the ladder
for a port, upstream fixes for a stress target, categorised failures for a harness. Module
37's complaint is not that projects measure the wrong things — it is that they measure
whatever goes up.

And the observation worth ending on: **most shapes on this list do not require a playable
game.** Seven of the nine can succeed completely without one. If you have been treating
"playable" as the only success condition, you have been ignoring most of the useful work
available to you.

---

## Labs

- **Lab 113** -- Classify the corpus: take fifteen public recompilation repositories, assign
  each a shape, and note where the README's framing and the repository's contents disagree.
- **Lab 114** -- Declare a shape: write the first paragraph of a README for your own project
  stating its shape, its "done" condition, and the metric it will be judged by — then check
  whether your last month of work was aimed at that metric.

---

**Next: [Module 60 -- Documentation and Community](../module-60-docs-community/lecture.md)**
