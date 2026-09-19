# Module 47: User Experience and Modding Support

Emulators can already run these games. The argument for recompilation is that once the
program is C, you can *change* it — and that argument only pays off if you actually build
the things that change it.

This module is about the affordances that turn a working recompilation into something
people use, and about the modding mechanism that falls out of the dispatch table you
already built in Module 14.

---

## 1. The Baseline Nobody Should Have to Ask For

From the corpus, the features that recur across finished ports — and therefore the ones
users expect:

`LinksAwakening`: full CGB colour with palette RAM, VRAM banking and HDMA, double-speed
mode, 4-channel audio, SRAM saves, **save states**, rebindable gamepad and keyboard, an
ImGui debug overlay and asset viewer.

`mk` (Super Mario Kart): save states, configurable keyboard and gamepad **for two
players**, and lockstep netplay.

`diddykongracing`: an ImGui overlay with a menu bar, a settings window on F1, a debug
overlay on F2, EEPROM 4K saves written to AppData.

Three things worth pulling out of that list.

**Save states are table stakes and nearly free.** Your entire guest state is a struct and
an array. Serialising it is a memcpy, and it is the single feature that most changes how
people use your build — including you, while debugging (Module 38's bisection is far
cheaper when you can jump straight to the failing scene).

**Rebindable input is not optional.** The guest's controller is not the user's. Module 11's
`mariopaint` has to implement the SNES Mouse serial protocol and drive it from a PC mouse;
`diddykongracing` maps WASD to an analog stick. Every port does this work, so build it into
the runtime once rather than per-game.

**Saves must go somewhere sensible.** Writing next to the executable breaks on any managed
install. `diddykongracing` writes to AppData; use the platform convention.

### Build it in the toolkit, not the game

There is a repository in the corpus called
[`tools`](https://github.com/sp00nznet/tools), described as a *"Reusable SDL2/ImGui toolkit
— screenshot capture, toast notifications, menu system."* That is the correct place for all
of this. Module 15's argument — the runtime is the hard part and should be shared — applies
to the user-facing layer too. Every one of these features written per-game is written four
times badly.

---

## 2. Enhancements, and Which Are Actually Cheap

Once the game is native code, some improvements are nearly free and others are research
projects. The distinction matters because people promise the second while thinking of the
first.

**Genuinely cheap:**

- **Higher internal resolution**, when rendering goes through your translation layer
  (Modules 22 and 29). You are already generating draw calls; generate them bigger.
- **Uncapped or higher frame rate**, *if* the game's logic is not tied to frame count —
  and Module 40 says that assumption is usually wrong, so verify before promising.
- **Texture replacement**, since assets already pass through your loaders.
- **Screenshot and video capture**, which is the host's problem, not the guest's.

**Not cheap, whatever it looks like:**

- **Widescreen.** The game's logic, HUD layout and culling assume an aspect ratio. Widening
  the camera reveals objects the game culled and stretches UI that was authored for 4:3.
  This is per-game work, every time.
- **Frame rate above the logic rate** when physics is frame-locked — you are changing
  gameplay, and the game will disagree.
- **Anything that changes timing.** Module 40 exists.

**And the genuinely novel ones**, which are the interesting reason to do this at all:
[`3dsnes`](https://github.com/sp00nznet/3dsnes) turns SNES tile and sprite output into 3D
voxel scenes; `vbrecomp`'s Virtual Boy work has an obvious stereoscopic angle that the
original hardware could barely deliver. Recompilation makes these possible because the
game's rendering decisions are now *data you can intercept* rather than pixels on a bus.

---

## 3. Modding: The Mechanism You Already Have

This is the part that genuinely could not be done before, and it is a direct consequence of
Module 14's dispatch table.

`snesrecomp`'s `include/snesrecomp/recomp_patch.h` defines a recompiled function and
auto-registers it at its original guest address at static-init time:

```c
RECOMP_PATCH(smk_80FF70, 0x80FF70) {
    // function body -- same shape as a regular void(void) function
}
```

And then the header documents the modding pattern in full:

> **Mod / override pattern:** link a second `.obj` that defines another `RECOMP_PATCH` at
> the same SNES address with a different function name. **The last constructor to run
> wins**, so put mod objects after the original.

That is the whole mechanism. **Overriding a shipped game function is a link-order
question.**

Think about what that gives you that a conventional mod does not. A ROM hack patches bytes
and must not change any size. An emulator cheat pokes memory from outside. Here, a modder
writes *a C function* — with types, a debugger, their own libraries, and no space
constraint — and it replaces the original at the address the game calls.

The header credits N64Recomp's macro of the same name for the idea, and N64Recomp's
ecosystem is where you can see it used at scale.

### What to build so people can use it

- **Auto-registration**, so adding an override is one file and no central list to edit.
  `RECOMP_PATCH` does this with a static constructor.
- **A documented override order.** "Last constructor wins" is only usable if you say it.
- **Stable symbol names.** If your generated names change every regeneration, every mod
  breaks. Address-derived names are stable; ordinal-derived names are not.
- **Exported guest state.** A modder needs to read the game's variables, which means
  documenting where they are — the same symbol import problem from Module 33, now
  user-facing.
- **A worked example in the repository.** One mod that does something visible is worth more
  than a page of documentation.

### The honest caveats

Overriding a function means your C must satisfy every caller's expectations — calling
convention, register effects, and any memory the original wrote. Module 38's boundary
tripwires are exactly the right tool to hand modders.

And mods will break when you regenerate against a different game revision, because the
addresses move. This is the Module 46 §2 input-verification problem again: a mod should
record which revision it was built against.

---

## 4. Debug Tooling Is User Tooling

Everything you built for yourself in Modules 38 through 40 is worth exposing, because your
power users are doing the same work you are.

`gb-recompiled`'s runtime ships an ImGui menu, an asset viewer and an `hwtrace` debugger.
`diddykongracing` puts a debug overlay on F2. `mariopaint` exposes `MP_REALFRAME` and
`MP_INTERP_FUNCS` as environment variables (Module 38 §2).

A useful set to expose:

| Tool | Who it serves |
|---|---|
| Asset viewer | modders, and you when a texture is wrong |
| State inspector | anyone reverse-engineering the game |
| Frame advance / rewind | speedrunners, TAS authors, and Module 39's minimisation |
| Trace capture | bug reports that are actionable (Module 46 §4) |
| The A/B interpreter switch | anyone reporting a divergence |

Frame advance deserves a specific mention: it converts a vague bug report into a precise
one, because the reporter can stop exactly at the bad frame.

---

## 5. What "Finished" Looks Like

Module 37's ladder ends at rung 8, verified. That is about correctness. The shipping
version of the same question is different, and worth asking explicitly:

- Can someone who is not you get it running from the README alone? (Module 46)
- Does it save, and survive a restart?
- Can they use their own controller?
- Does it fail legibly when their copy is wrong?
- Is what it *cannot* do written down?
- Can someone change something without asking you how?

A project that answers all six is finished in the way that matters to the person
downloading it, even if it is rung 6 on the correctness ladder. A project at rung 8 that
answers none of them will be used by exactly one person.

---

## Labs

- **Lab 85** -- Runtime feature set: add save states, rebindable input and platform-correct
  save file locations to a recompiled project, with an ImGui overlay exposing them.
- **Lab 86** -- Write a mod: using an auto-registering patch macro, override one function in
  a recompiled game with your own C implementation, document the link order, and record the
  game revision the mod targets.

---

**Next: [Module 48 -- Semester 3 Project: Ship a Recompiled Game](../module-48-semester3-project/lecture.md)**
