# Module 37: What "It Works" Means

This module is about a claim, not a technique.

Every recompilation project eventually says some version of "it works." The word is doing
an enormous amount of load-bearing work, and the field has almost no shared vocabulary for
what it covers. A project that boots to a title screen, a project whose harness draws a
title screen using the game's textures, and a project where the game's own code drives the
frame are three completely different achievements that produce the same screenshot.

This is not a module about honesty as a virtue. It is a module about **not fooling
yourself**, because the person your claims mislead first and worst is you — and then you
build three more weeks on top of them.

Everything here is drawn from real projects, including several that got it wrong and
said so.

---

## 1. The Characteristic Failure: Your Harness Produces Your Evidence

Start with the clearest case anyone has written down. The
[xboxdashboard](https://github.com/sp00nznet/xboxdashboard) project prints this at the
top of its README, permanently:

> An earlier version of this README claimed a "green orb at 60fps". That orb was ours — a
> hand-written disc drawn by scaffolding in this repo, not by the dashboard. It has been
> deleted, along with the fake scene root, hand-rolled asset loader and **2,204
> return-zero stubs** that surrounded it. Treat any screenshot from before 2026-09-02 as
> retired.

Read it twice. There was a picture on screen, at 60 frames per second, and the picture was
the project's own scaffolding. Two thousand two hundred and four stubs returning zero let
the program proceed far enough to reach code that drew something, and what it drew was
ours.

This is the characteristic failure mode of recompilation work, and it has a mechanism:

- **Stubs that return zero let a program continue.** A function that should have failed
  instead reports success, so the caller proceeds into territory it should never have
  reached.
- **Scaffolding that draws makes a window look alive.** You wrote a renderer to test the
  renderer; now it is rendering.
- **Both are necessary during bring-up.** You cannot make progress without them.

So the problem is not that the scaffolding exists. It is that **the scaffolding and the
guest produce indistinguishable-looking output**, and nothing in your build tells you
which one you are looking at.

The current README's framing is the antidote, and it is worth memorising as a sentence
shape:

> ...the stream contains **0 draws**, so no geometry has been submitted yet, and **nothing
> in this repo has ever put a pixel on screen that the dashboard did not ask for.**

Attribute every observed behaviour to *the guest* or to *your own code*, explicitly,
before you believe it.

---

## 2. Three More, From Projects That Did Not Catch It

The xboxdashboard case is unusual because it was caught and retracted. Here are three
where the README still claims more than the code supports. They are in this course
because they are *normal* — this is what the honest average looks like.

### burnout3: the menu is a hardcoded array

[burnout3](https://github.com/sp00nznet/burnout3) presents screenshots of the *Burnout 3*
main menu — logo, all five options, button prompts, scrolling chyron — as recompiled
output. `src/game/fe_menu.c` describes itself:

> Renders a functional menu UI when the game is in frontend state. Detects menu state via
> camera pointer (`0x4D4008` = menus) and renders using the D3D8→D3D11 layer with textures
> from `Global.txd`.

The menu text is a hardcoded array in the harness:

```c
static const char *g_main_menu_labels[FE_MAIN_ITEMS] = { ... };
```

Cursor movement and selection are hand-written too. The harness watches a game state
address, decides the game is "in menus," and draws its own menu using the real game's
textures. Genuine pixels, genuine assets — and the game's own frontend code is not what
put them there.

Meanwhile the parts that *are* verifiable are substantial: 22,097 functions lifted, 147
kernel imports mapped, the Xbox's 64 MB reproduced with `CreateFileMapping` mirror views.
**The real achievement is buried under a claim that overshoots it.**

### xwa: fabricated scene records, and a hand-drawn starfield

[xwa](https://github.com/sp00nznet/xwa) shows texture-mapped spacecraft in flight. Its
`src/game/main.c` is 5,037 lines, and its comments are more honest than its README:

- `xwa_native_mesh -- draw the game's own loaded OPT geometry (XWA_NATIVEDRAW)`
- a helper answering *"Is this pointer one of **OUR fabricated** stand-in scene records
  (rather than a real one the engine made)?"*
- `Starfield: without it a correct scene still reads as an empty blue void.`
- `xwa_drive_render` — the harness drives the render path

The OPT models and 1999 textures are the game's real data. `main.c` is what puts them on
screen.

### ww: caught it, said so

[ww](https://github.com/sp00nznet/ww) (*The Wind Waker*) renders real island geometry —
`Stage.arc` and `Room44.arc` read from a disc image, Yaz0-decompressed, J3D/BDL parsed,
CMPR textures decoded, shaded by HLSL generated from the game's own TEV configuration.
That is the entire GameCube asset and graphics stack working. And:

> **Honest caveat:** this is the renderer, not the game. The frame loop is being driven by
> us rather than by the title screen's own state machine, and the black spiral is a
> water/skybox texture we still map wrong.

*The renderer, not the game.* That is the distinction, in five words, written by someone
looking at a screenshot that made it very tempting not to.

### Why all three are graphics, and why that is not a coincidence

`burnout3`, `xboxdashboard` and `xwa` are all x86 PC/Xbox targets, and the cause is
structural rather than careless. On these platforms the graphics path is COM —
`com_mocks.c` in xwa is 144 KB of interface mocks — and a COM vtable call is precisely
Module 14's hardest indirect-dispatch case. When the game's own renderer will not run yet,
reading its loaded assets and drawing them yourself is the obvious way to make progress,
and it produces a screenshot that looks like success.

**Expect this on your project. Label it when it happens.**

---

## 3. When the Fallback Is Silent, "It Runs" Means Nothing

The second failure mode is worse, because there is no screenshot to interrogate — the
evidence is the program running at all.

[gbarecomp](https://github.com/sp00nznet/gbarecomp)'s README says:

> **True static recompilation.** No emulator runs underneath. The recompiled C code IS the
> CPU.

Its `src/` contains `runtime_mgba.c` (1,042 lines), which opens by saying *"Replaces the
standalone runtime with mGBA for accurate hardware emulation,"* links libmgba, and drives
frames with `core->runFrame(core)`. Recompiled functions get in via `interception.c`, which
hooks `ARMSetRecompHook` — called before every instruction — and swaps in a native function
when the PC matches.

Now read the fallback:

```c
if (crashed) {
    /* Restore state and let mGBA interpret this function */
    memcpy(cpu->gprs, saved_gprs, sizeof(saved_gprs));
    cpu->cycles = saved_cycles;
    failed++;
    if (failed <= 20) { fprintf(stderr, "[recomp] CRASH at 0x%08X ...\n", ...); }
    return false; /* Let mGBA interpret it */
}
```

Recompiled functions run inside `__try`/`__except`. If one crashes, registers roll back and
mGBA interprets the original instructions. There is a second identical rollback for a bad
return address.

**Work through the consequence.** If every single recompiled function were wrong, the game
would still play perfectly — at full speed, correct graphics, correct audio — because every
one would crash, roll back, and be interpreted. The only difference would be some lines on
stderr, and only the first twenty print.

A screenshot of a working game is therefore **zero evidence** that any recompilation
occurred.

[snesrecomp](https://github.com/sp00nznet/snesrecomp) has the same architecture, and its
`func_table.h` documents the semantics precisely:

> Otherwise, if the interpreter fallback is enabled, the original 65816 code at that
> address is executed on the LakeSnes CPU and the call **still "succeeds" (returns true)**.

A project with zero registered functions runs the game flawlessly and reports that every
dispatch succeeded.

### This is not an indictment of the technique

Incremental interception is a *good* design — Module 11 argues for it, and it is what makes
a project playable on day one instead of after nine months. The problem is only that the
usual evidence stops working, so the design owes you different evidence:

**Count and publish `successful` and `failed`.** They exist in `interception.c` already.
**Report results with the fallback off.** That is the number that is about your recompiler.
**Expose the A/B lever** — Module 38 is entirely about this, and `mariopaint`'s
`MP_INTERP_FUNCS` is the model.

---

## 4. Numbers Overshoot Too

Not all overclaiming is visual.

[tokyojungle](https://github.com/sp00nznet/tokyojungle)'s README carries this note,
unprompted:

> **A note on the function count.** Earlier builds advertised *35,208 lifted functions*.
> That number was wrong, and the current one is lower on purpose: `find_functions` was
> treating intra-function basic blocks as separate functions.

A headline metric revised **downward** because the definition behind it was wrong.

Function counts are the number every recompilation project leads with, and they are
trivially inflatable — split at every branch target and your total balloons while the work
does not change. Module 34 catalogues four projects that hit this same bug in four
different disguises.

**If your numbers only ever go up, check how you are counting.** A measurement that cannot
decrease is not a measurement.

And be precise about what a number measures. `gb-recompiled` reports **98.94%** (1,592 of
1,609 ROMs), and the very next words in that line are:

> **MOST OF THE GAMES ARE NOT FULLY PLAYABLE YET**

"Recompiles" means the tool emitted C that compiled. Quote the number with the caveat
attached, or do not quote it.

---

## 5. The Ladder of Evidence

Here is the vocabulary this field is missing. Each rung is a real, distinct achievement.
Say which one you are on.

| # | Claim | What it actually establishes |
|---|---|---|
| 0 | **Extracted** | You got a code image out of the container |
| 1 | **Translated** | The tool emitted C for every discovered function |
| 2 | **Compiles** | That C is valid and links — *gb-recompiled's 98.94% lives here* |
| 3 | **Boots** | The process starts, the runtime initialises, guest code executes |
| 4 | **Reaches guest logic** | The game's own state machine advances — *civrev, outrun* |
| 5 | **Renders, harness-driven** | Pixels appear; your code drives the frame — *ww, burnout3, xwa* |
| 6 | **Renders, guest-driven** | The game's own code submits the draws — *ydkj, wormsrevolution* |
| 7 | **Playable** | Input reaches game logic and the result is visible — *LinksAwakening, Rampage (blind!)* |
| 8 | **Verified** | Output matches a reference across a defined corpus — *encarta's byte-exact codec* |

Two things fall out of the table that are hard to see otherwise.

**Rungs 5 and 6 look identical in a screenshot and are months apart.** That gap is the
subject of this entire module.

**The rungs are not strictly ordered.** `Rampage` is at rung 7 and *below* rung 5 — the
game logic runs, controls work, you can punch and climb buildings, and the screen is black
because the display list handoff is not connected. Meanwhile `crazytaxi` has 12,750
functions lifted and never draws a frame. Your project can be genuinely playable and
invisible at the same time.

---

## 6. The Ten-Minute Audit

You can apply this to any project, including your own, in about ten minutes.

**First, know what you are allowed to see.** Recompiled output from a commercial game is a
derived work and cannot be redistributed, so most game-port repositories deliberately
gitignore it — `LinksAwakening` ignores `rom.c` and `rom_rom.c`, `oracle-recompiled` ignores
`oracle_of_ages.c`, `lttp-recompiled` ignores `recomp_out/`. That is the correct and legal
choice.

The consequence matters: **for most ports you cannot verify the headline numbers from the
repository at all.** Treat them as reports, not evidence, and say so when you repeat them.

Some projects commit everything — `diddykongracing` ships `RecompiledFuncs/funcs_0.c`
through `funcs_16.c`, megabytes of generated C, and is the most auditable port in the
corpus. When a project makes that choice its claims are checkable and worth more.

Then:

1. **Read the `.gitignore`.** It tells you whether the interesting half is even present,
   and therefore what any other observation can prove.
2. **`ls src/` for hand-written names.** `fe_menu.c`, `rw_renderer.c`, `static_textures.c`
   are harness. Generated output is thousands of `sub_XXXXXXXX` functions in numbered
   files. This is exactly how `burnout3` gives itself away — the generated code is ignored,
   but the hand-written menu is committed.
3. **`wc -l` the two groups.** A large harness beside an absent recompilation means the
   screenshots are probably from the harness. Compare `wormsrevolution`: four files, 8.5 KB
   total, `main.cpp` at 146 bytes. There is nothing there that *could* draw a menu.
4. **Audit the toolkit, not the port.** You usually cannot read the port; the toolkit is
   always public. If the toolkit is emulator-hosted, no port on it can claim more than the
   toolkit allows, whatever its README says.
5. **Find the fallback and ask if it is silent.**
6. **Ask what drives the frame loop** — the game's state machine, or your code?
7. **Look for the counters.** A project that knows how much of itself is real prints
   `successful` and `failed`. One that does not has not asked.

---

## 7. How to Write the Claim

Practical rules, all of them lifted from projects in this corpus that do it well.

**Put an "Honest scope" heading in your README.** `ydkj` and `civrev` both have one.
`ydkj`'s: *"the front-end renders and reaches the interactive title screen; input into an
actual question round hasn't been driven yet."*

**State the negative explicitly.** `crazytaxi` opens with *"This one does not draw a frame
yet"* — and then points readers at a different project that does. Pointing people away from
your own repo when it is not the best example is worth more than a good screenshot.

**Attribute every pixel.** "Nothing in this repo has ever put a pixel on screen that the
dashboard did not ask for" is the gold standard sentence.

**Distinguish states that are not done.** `pokemon-crystal`'s status table uses
`⏳ user-test` as its own row — "I believe this works but nobody has played a save
round-trip yet" is real information.

**Record ruled-out hypotheses.** `outrun`'s README documents that an early suspect, a failed
`ShaderDump` device probe, turned out to be a harmless get-file-size on another thread.
Bring-up is mostly eliminating plausible wrong answers, and writing down the ones you
eliminated is how you stop re-investigating them at 2am.

**Say how you measured.** `3dsnes` reports 340 of 375 games (91%) and specifies: an
unattended run over the whole corpus, *"not by spot-checks."* If you cannot re-derive your
figure by running one command tonight, you do not have a figure — you have an impression.

**Retract in public when you are wrong.** Both the xboxdashboard orb and `encarta`'s
`retract "it decodes" - the buffers were copies of its own code` are one-line corrections
that saved their projects from building on a false result. Module 38 follows that second one
in detail.

---

## 8. Why This Is an Engineering Concern

It would be easy to read this module as being about etiquette. It is not.

Every failure above has a direct engineering cost:

- The xboxdashboard orb meant 2,204 return-zero stubs and a fake scene root had to be
  **deleted** — weeks of work built on a misread.
- `encarta`'s false "it decodes" would have sent the project chasing output-format bugs in
  a decoder that was actually copying its own code segment.
- `civrev`'s 301 hints were added because pointer-scan output *looked* like evidence.
- `tokyojungle`'s inflated count would have made every later completion percentage wrong.

The habit that prevents all of them is the same one: **ask what your evidence would look
like if the thing you believe were false.** If a working screenshot is compatible with
nothing being recompiled, the screenshot is not evidence. Go find something that is.

That question is the whole of the next three modules.

---

## Labs

- **Lab 60** -- Audit three projects: apply the ten-minute audit to three public
  recompilation repositories (one of them your own), and write a one-paragraph evidence
  assessment for each, placing it on the ladder in section 5.
- **Lab 61** -- Attribution harness: instrument a recompiled project so every frame reports
  how many draws came from guest code versus harness code, and how many dispatches hit the
  fallback. Publish the counters in the window title.

---

**Next: [Module 38 -- Differential Testing and Oracles](../module-38-differential-testing/lecture.md)**
