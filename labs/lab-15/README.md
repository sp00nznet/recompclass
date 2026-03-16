# Lab 15: Simple Graphics Bridge

## Objective

Create an abstract graphics command buffer that translates high-level draw
commands into SDL2 draw calls. In a real recompiler, the original game's
graphics API calls (e.g., Direct3D on Xbox, GX on GameCube) must be translated
to a host graphics API. This lab introduces that concept with a simple 2D
abstraction layer.

## Background

A **graphics bridge** sits between the recompiled game code and the host
graphics API. The game issues abstract draw commands, and the bridge translates
them to whatever the host supports. This decoupling has several advantages:

- The recompiled code does not need to know about the host platform.
- You can swap backends (SDL2, OpenGL, Vulkan) without changing game code.
- You can add debugging or profiling at the bridge layer.

In this lab, the abstract API supports four commands:

1. **Clear** -- fill the screen with a solid color.
2. **DrawRect** -- draw a filled rectangle.
3. **DrawSprite** -- draw a sprite (texture) at a position (stubbed for now).
4. **Present** -- flip the back buffer to the screen.

## Files

| File                | Description                                  |
|---------------------|----------------------------------------------|
| `graphics_bridge.h` | Abstract draw command definitions            |
| `graphics_bridge.c` | SDL2 backend implementation                  |
| `main.c`            | Demo program drawing a simple scene          |
| `Makefile`           | Build with SDL2 linking                      |

## Prerequisites

- SDL2 development libraries installed.
  - Ubuntu/Debian: `sudo apt install libsdl2-dev`
  - macOS (Homebrew): `brew install sdl2`
  - Windows (MSYS2): `pacman -S mingw-w64-x86_64-SDL2`

## Building and Running

```bash
make
./graphics_demo
```

Press Escape or close the window to exit.

## Tasks

1. Read through `graphics_bridge.h` to understand the command interface.
2. Complete the SDL2 backend in `graphics_bridge.c`.
3. Run the demo and verify you see colored rectangles on screen.
4. (Stretch) Add texture loading and implement `cmd_draw_sprite`.
5. (Stretch) Add sprite batching to reduce draw call overhead.
