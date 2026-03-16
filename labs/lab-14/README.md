# Lab 14: Kernel Shim

## Objective

Implement a small set of Xbox kernel function shims that translate Xbox kernel
API calls into their Win32 or POSIX equivalents. In a real static recompiler
for the Xbox 360, every kernel import that the original game calls must be
intercepted and re-implemented on the host platform. This lab gives you
hands-on experience with that translation layer.

## Background

Xbox 360 executables import functions from the kernel (`xboxkrnl.exe`) and
other system modules. These functions cover memory management, file I/O,
threading, synchronization, and more. When recompiling an Xbox 360 binary
to run on a PC, each imported kernel function must be replaced with a **shim**
-- a wrapper that provides equivalent behavior using the host OS API.

Key challenges include:

- **Calling convention differences**: Xbox 360 uses the PowerPC ABI; the host
  uses x86-64 calling conventions.
- **Pointer size**: Xbox 360 is 32-bit (ILP32); the host may be 64-bit.
- **Semantic mismatches**: Some kernel functions have no direct equivalent and
  require creative reimplementation.

This lab focuses on the semantic translation, ignoring calling convention
details for simplicity.

## Files

| File              | Description                                |
|-------------------|--------------------------------------------|
| `kernel_shim.h`   | Shim function declarations                |
| `kernel_shim.c`   | Shim implementations                      |
| `test_shim.c`     | Basic functional tests                    |
| `Makefile`         | Build target                              |

## Tasks

1. Read through `kernel_shim.h` to understand the shim interface.
2. Complete the implementations in `kernel_shim.c`.
3. Run the tests to verify basic behavior.
4. (Stretch) Add shims for NtCreateFile, NtReadFile, and NtWriteFile.

## Building and Testing

```bash
make
make test
```

## Notes

- The shims intentionally simplify the real kernel API. Real Xbox kernel
  functions take NTSTATUS return codes, use OBJECT_ATTRIBUTES structures, etc.
  We use simplified signatures here to focus on the concept.
- On Windows, the shims call Win32 functions. On Linux/macOS, they call POSIX
  equivalents. The code uses `#ifdef _WIN32` to select the right path.
