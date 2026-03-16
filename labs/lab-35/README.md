# Lab 35: SH-2 Delay Slot Lifter

## Objective

Implement a lifter for a subset of SH-2 instructions with proper delay
slot handling. The Hitachi SH-2 (used in the Sega Saturn and Sega 32X)
has a pipelined architecture where the instruction immediately after a
branch is always executed *before* the branch takes effect. Getting this
wrong is one of the most common bugs in Saturn recompilation.

## Background

### What Is a Delay Slot?

On the SH-2, branch instructions (BT, BF, BRA, JSR, RTS) have a
**delay slot**: the instruction at PC+2 is executed before the branch
target is loaded into the program counter. This is a pipeline artifact --
the CPU has already fetched the next instruction by the time it knows
it needs to branch.

Example:
```
    CMP/EQ R0, R1     ; compare R0 and R1, set T flag
    BT     target      ; if T==1, branch to target
    ADD    R2, R3      ; <-- delay slot: ALWAYS executes
    ...                ; execution continues here if T==0
```

If T==1, the CPU executes ADD R2,R3 and *then* jumps to `target`.
If T==0, the CPU executes ADD R2,R3 and continues to the next instruction.

### SH-2 Instructions in This Lab

All SH-2 instructions are 16 bits (fixed width).

| Encoding Pattern  | Mnemonic         | Behavior                        |
|-------------------|------------------|---------------------------------|
| 0110_nnnn_mmmm_0011 | MOV Rm, Rn     | Rn = Rm                        |
| 0011_nnnn_mmmm_1100 | ADD Rm, Rn     | Rn = Rn + Rm                   |
| 0011_nnnn_mmmm_0000 | CMP/EQ Rm, Rn  | T = (Rn == Rm)                 |
| 1000_1001_dddd_dddd | BT disp        | if T: PC = PC+4+disp*2         |
| 1000_1011_dddd_dddd | BF disp        | if !T: PC = PC+4+disp*2        |
| 1010_dddd_dddd_dddd | BRA disp       | PC = PC+4+disp*2 (always)      |
| 0100_mmmm_0000_1011 | JSR @Rm        | PR=PC+4, PC=Rm (has delay slot)|
| 0000_0000_0000_1011 | RTS            | PC = PR (has delay slot)        |

- `disp` for BT/BF is 8-bit signed.
- `disp` for BRA is 12-bit signed.
- JSR and RTS both have delay slots.
- BT and BF have delay slots in this lab (matching SH-2 behavior).

## Instructions

1. Open `sh2_lifter.py` and implement the TODO functions.
2. `decode_sh2()` -- decode a single 16-bit SH-2 instruction.
3. `lift_block()` -- lift a sequence of SH-2 instructions to pseudo-C,
   handling delay slots correctly.
4. The key rule: when you encounter a branch, lift the *next* instruction
   (the delay slot) first, then emit the branch.
5. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

For the sequence `MOV R0,R1 ; BRA label ; ADD R2,R3`:

```
// 0x1000: MOV R0, R1
regs[1] = regs[0];
// 0x1002: BRA 0x100A  (delay slot: ADD R2, R3)
regs[3] = regs[3] + regs[2];   // delay slot
goto label_0000100A;
```

Note how the ADD (delay slot) is emitted *before* the goto.
