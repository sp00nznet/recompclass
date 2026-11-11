# Toolchain Matrix: Which Toolchain for Which Machine

> **Hand-written for now.** This page will later be generated from the routing data of
> recomp-guide, a companion tool that walks you to the right toolchain for your machine and goal.
> Until then, treat it as a snapshot (November 2026) and check each project's own README.

Four goals:

- **Port** -- a native build you can play.
- **Mod** -- a base you can change.
- **Preserve** -- a faithful, reproducible build plus verified inputs.
- **Study** -- a decomp workspace to read and learn from.

"Ours" means a toolkit from the sp00nznet collection (MIT). "Outside" means someone else's
project; it is listed with its licence and you should use its own docs and community. "Experimental"
means it gets in-game on some titles but no game has been released with it yet. "Boots only" means
it reaches a title screen at best. A "--" means there is no good answer yet, and we say so rather
than point you at something that will not get you there.

## The matrix

| Machine | Port | Mod | Preserve | Study |
|---|---|---|---|---|
| **PC (DOS / Win16 / Win32)** | [pcrecomp](https://github.com/sp00nznet/pcrecomp) (ours): 11+ released games, best docs | pcrecomp and its hook/patch layer | pcrecomp build + input hashes | Ghidra (outside) |
| **Xbox** | [xboxrecomp](https://github.com/sp00nznet/xboxrecomp) (ours): released | xboxrecomp | same | Ghidra (outside) |
| **Xbox 360** | If the title is already covered: [360tools](https://github.com/sp00nznet/360tools) (ours, built on the outside XenonRecomp/ReXGlue lineage); otherwise XenonRecomp or ReXGlue (outside) directly | XenonRecomp (outside): its ports are the mod bases people use | same | Ghidra + XenonAnalyse (outside) |
| **N64** | N64Recomp (outside): the reference tool; we are users, not authors | N64Recomp mod API (outside) | N64Recomp | splat + m2c + decomp.me (outside), the standard N64 decomp path |
| **Neo Geo** | [neogeorecomp](https://github.com/sp00nznet/neogeorecomp) (ours): released | ours | ours | Ghidra (outside) |
| **Arcade: Midway / Sega Model 2** | [MidwayRecomp](https://github.com/sp00nznet/MidwayRecomp) (ours, released) / [model2recomp](https://github.com/sp00nznet/model2recomp) (ours, in-game, 3D incomplete) | ours | ours | Ghidra (outside) |
| **PS3** | [ps3recomp](https://github.com/sp00nznet/ps3recomp) (ours): **experimental**, no released game yet. The only public PS3 recompiler we know of | ours, experimental | -- (no faithful-enough build yet) | Ghidra (outside) |
| **PSP, Genesis, GBA, CPS1, Virtual Boy, Android, iOS, .NET** | our kit for each, **experimental** (in-game, no release) | ours, experimental | -- | Ghidra (outside); GBA: pret-style decomp tooling (outside) |
| **PS2** | PS2Recomp (outside, by ran-j), work in progress | outside | -- | splat + m2c + Ghidra (outside) |
| **PS1** | RecompOne (outside) for the one game it covers; otherwise no good port path yet | -- | -- | splat + m2c + decomp.me (outside) |
| **Game Boy / GBC** | gb-recompiled (outside, by arcanite24) | outside | -- | pret-style tooling (outside) |
| **GameCube / Wii** | **no good port toolchain yet** (our gcrecomp is a scaffold) | -- | -- | decomp-toolkit + objdiff + decomp.me (outside), the mature path |
| **SNES, NES, NDS** | early outside recompilers; ours is a stub. **Early** | -- | -- | Ghidra / pret-style (outside) |
| **Vita, Model 3, Lindbergh, Dreamcast, Mac, small handhelds and computers** | ours, **boots only**: a research preview, not a port | -- | -- | Ghidra (outside) |
| **Saturn, 3DS, Switch, PS5** | **no good toolchain yet.** Switch: early outside work only | -- | -- | Ghidra (outside), study only |

A few rules sit behind the table:

- A cell offers **Port** only when that toolkit has at least one released game. Everything else is
  labelled experimental, early or boots only.
- Outside projects are not ours. We link you to them because they are the right answer, not to take
  credit for them.
- By target-platform count the sp00nznet collection is broad; by maturity and use, the
  single-platform leaders (N64Recomp, XenonRecomp, PS2Recomp) are far more proven.

## Outside tools and their licences

Licences as read at each project's source in November 2026; "unverified" means we did not confirm it.

| Tool | Role | Licence |
|---|---|---|
| N64Recomp / N64ModernRuntime | N64 static recompiler / runtime | MIT / **GPL-3.0** |
| XenonRecomp + XenosRecomp (hedge-dev) | Xbox 360 recompiler | MIT |
| ReXGlue SDK | Xbox 360 recompiler | BSD-3-Clause |
| PS2Recomp (ran-j) | PS2 recompiler | **GPL-3.0** |
| RecompOne | PS1 recompiler (one game) | MIT |
| gb-recompiled (arcanite24) | GB/GBC recompiler | MIT |
| nesrecomp; RetroPortingToolKit (snes/nds/psx) | early recompilers | unverified |
| kirikae | early Switch work | Apache-2.0 |
| Ghidra | disassembler / decompiler | Apache-2.0 |
| splat | split a ROM into asm + assets | MIT |
| decomp-toolkit (dtk) | GC/Wii decomp scaffold | Apache-2.0 |
| m2c | asm to C (MIPS/PPC) | **GPL-3.0** |
| objdiff | matching diff | Apache-2.0 |
| decomp.me | shared matching scratches (website) | MIT (site code) |
| pret projects | finished matching decomps | mostly no licence |

See [Module 58](../units/unit-15-tooling/module-58-toolkit-design/) for what separates a toolkit
from a one-game port, and [Module 37](../units/unit-10-quality-correctness/module-37-what-it-works-means/)
for what "released" and "works" should mean.
