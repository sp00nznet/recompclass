# Lab 25: Hand-Lift Z80 Subroutine

## Objective

Given a Z80 assembly listing, manually translate ("lift") each instruction
into equivalent C code. This is exactly what an automated lifter does, but
doing it by hand first builds the intuition you need to write or debug one.

## Background

The subroutine in this lab computes a simple additive checksum over a range
of memory bytes. In Z80 assembly it looks like:

```
; checksum(HL=start, B=count) -> A=checksum
checksum:
    XOR A           ; A = 0
.loop:
    ADD A, (HL)     ; A += memory[HL]
    INC HL          ; HL++
    DEC B           ; B--
    JR NZ, .loop    ; if B != 0, goto .loop
    RET
```

Your job is to translate each instruction into C code that operates on a
register struct and a memory array, matching the Z80's behavior exactly.

### Z80 Registers Used

| Register | Size   | Purpose in this routine        |
|----------|--------|-------------------------------|
| A        | 8-bit  | Accumulator (checksum result) |
| B        | 8-bit  | Loop counter                  |
| HL       | 16-bit | Memory pointer                |
| F.Z      | 1-bit  | Zero flag                     |

## Instructions

1. Review `z80_runtime.h` -- it defines the register struct and memory array.
2. Open `lifted.c` -- each Z80 instruction is shown as a comment, with a
   `// TODO:` marker where you write the C equivalent.
3. Fill in the C code for each instruction.
4. Build and test:
   ```
   make
   make test
   ```
   Or without make:
   ```
   gcc -o test_lifted test_lifted.c lifted.c -I. && ./test_lifted
   ```

## Expected Output

```
Test 1 PASSED: checksum([1,2,3,4,5]) = 15
Test 2 PASSED: checksum([0xFF]) = 255
Test 3 PASSED: checksum([0,0,0]) = 0
All tests passed!
```
