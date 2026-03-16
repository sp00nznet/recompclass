# Lab 6: Mini-GB Recomp

## Objective

Recompile a tiny homebrew Game Boy ROM end-to-end. This is the culminating
lab for Unit 2's Game Boy content, bringing together ROM parsing,
disassembly, instruction lifting, and runtime generation into a complete
static recompilation pipeline.

By the end of this lab you will be able to:

- Describe the full static recompilation pipeline from ROM to executable
- Implement each pipeline stage as a discrete, testable function
- Generate compilable C code from Game Boy machine code
- Link generated code against a minimal runtime to produce a working binary

## Pipeline Overview

The recompilation pipeline has four stages:

```
  .gb ROM file
       |
       v
  [1. DECODE] -- Read ROM, decode SM83 instructions
       |
       v
  [2. LIFT]   -- Translate each SM83 instruction to C code
       |
       v
  [3. EMIT]   -- Write the C code to an output .c file
       |
       v
  [4. BUILD]  -- Compile the generated C + runtime into an executable
```

### Stage 1: Decode

Read the ROM binary and walk through the code section, decoding each byte
(or multi-byte sequence) into a structured instruction representation. The
decoder must handle variable-length SM83 instructions (1-3 bytes).

### Stage 2: Lift

Convert each decoded instruction into one or more lines of C code. The
generated C code operates on a `cpu_t` struct and calls memory bus functions
from the runtime library.

### Stage 3: Emit

Wrap the lifted C code in a proper C source file with includes, a function
signature, and a dispatch loop. Write the result to disk.

### Stage 4: Build

Compile the generated .c file together with the runtime (runtime.c) using
gcc to produce a final executable.

## Instructions

1. Study `runtime.h` and `runtime.c` to understand the runtime interface.
2. Open `mini_recomp.py` and read through the pipeline stages.
3. Complete the TODO sections in each stage function.
4. Run the recompiler on the built-in sample ROM:
   ```
   python mini_recomp.py
   ```
   This generates `output.c` in the current directory.
5. Build and run the result:
   ```
   make
   ./mini_gb
   ```

## Files

| File           | Purpose                                      |
|----------------|----------------------------------------------|
| mini_recomp.py | The recompilation pipeline script            |
| runtime.h      | C header: CPU struct, memory bus, flag macros |
| runtime.c      | C implementation of the runtime              |
| Makefile        | Builds runtime + generated code              |
| output.c       | Generated file (created by mini_recomp.py)   |

## Sample ROM

The script includes a small built-in ROM as a byte array. It performs a
simple computation: load values into registers, add them, and store the
result. This is enough to exercise the full pipeline without needing an
external ROM file.
