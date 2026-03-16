# Lab 38: DirectX 8 Shim Skeleton

## Objective

Build a skeleton shim layer for Direct3D 8 functions. In Xbox recompilation
projects, the original game calls D3D8 functions expecting the Xbox GPU.
A shim layer intercepts those calls and translates them to a modern
graphics API -- but first you need the scaffolding.

By the end of this lab you will be able to:

- Implement stub functions that match a target API's calling convention
- Log function calls with their arguments for debugging
- Build a shim layer that can be linked against recompiled code

## Background

When recompiling an original Xbox game, the game's code calls Direct3D 8
functions like `CreateDevice`, `Clear`, `BeginScene`, `EndScene`,
`Present`, and `SetTexture`. On the original hardware these talk to the
NV2A GPU. In a recomp project, we replace these with shims that:

1. **Log** the call and its arguments (invaluable for debugging).
2. **Translate** the call to a modern API (OpenGL, Vulkan, etc.).
3. **Return** a plausible success code so the game continues.

In this lab you build step 1: the logging shim skeleton. Each function
records its call into a global log buffer that the test harness can
inspect.

### Functions to Shim

| Function       | Signature (simplified)                                  |
|----------------|---------------------------------------------------------|
| `CreateDevice` | `int (int adapter, int device_type, void* window)`     |
| `Clear`        | `int (int count, int flags, uint32_t color, float z)`  |
| `BeginScene`   | `int (void)`                                            |
| `EndScene`     | `int (void)`                                            |
| `Present`      | `int (void)`                                            |
| `SetTexture`   | `int (int stage, uint32_t texture_handle)`              |

All functions return 0 on success (simulating `D3D_OK`).

## Files

| File           | Description                                |
|----------------|--------------------------------------------|
| `d3d8_shim.h`  | Shim API declarations and log structures  |
| `d3d8_shim.c`  | Shim implementation (starter code)        |
| `test_shim.c`  | Test suite                                 |
| `Makefile`      | Build and test targets                    |

## Instructions

1. Read `d3d8_shim.h` to understand the log entry structure.
2. Complete the `TODO` sections in `d3d8_shim.c`.
3. Build and test:
   ```bash
   make
   make test
   ```

## Expected Output

```
D3D8 Shim -- Test Suite

--- test_create_device ---
--- test_clear ---
--- test_scene_lifecycle ---
--- test_set_texture ---
--- test_log_overflow ---

5 / 5 tests passed.
```

## References

- Microsoft Direct3D 8 SDK documentation
- Xbox Development Kit (XDK) D3D8 headers
