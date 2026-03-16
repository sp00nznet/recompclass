# Lab 30: CMake Recomp Project

## Objective

Complete a CMakeLists.txt that builds a realistic recompilation project
structure. Real recomp projects have three components that need to be
compiled and linked together:

1. **Generated code** -- the lifted C files produced by the lifter
2. **Shims** -- hand-written C code that replaces hardware/OS calls
3. **Main harness** -- the entry point that ties everything together

## Background

A typical recomp project directory looks like:

```
project/
  CMakeLists.txt
  main.c                      # entry point
  generated/
    sample_lifted.c            # auto-generated lifted code
  shims/
    stub_shim.c                # hardware abstraction stubs
    stub_shim.h
```

The CMake build should:

1. Compile the generated sources into a static library (`recomp_generated`).
2. Compile the shim sources into a static library (`recomp_shims`).
3. Build the main executable, linking both libraries.

### CMake Concepts You Will Use

- `cmake_minimum_required()`
- `project()`
- `add_library(... STATIC ...)`
- `target_include_directories()`
- `add_executable()`
- `target_link_libraries()`

## Instructions

1. Review the provided source files to understand what they expect.
2. Open `CMakeLists.txt` and fill in the TODO sections.
3. Build the project:
   ```
   mkdir build && cd build
   cmake .. && cmake --build .
   ```
4. Run the resulting executable to verify it works.

## Expected Output

```
$ cmake --build build
...
[100%] Built target recomp_runner

$ ./build/recomp_runner
Shim: stub_hw_init() called
Lifted: sample_function() returned 42
Recomp runner finished successfully.
```
