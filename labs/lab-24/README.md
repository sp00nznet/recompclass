# Lab 24: Flag Computation Library

## Objective

Implement flag computation functions that match Z80 behavior for the four
main arithmetic flags: Z (Zero), N (Subtract), H (Half-Carry), and
C (Carry). Getting flags right is one of the most tedious but critical
parts of lifting -- if your flags are wrong, every conditional branch in
the recompiled code will be wrong too.

## Background

The Z80 has a flags register (F) where individual bits track the result
of the last arithmetic operation:

| Bit | Flag | Name       | Set when...                              |
|-----|------|------------|------------------------------------------|
| 7   | Z    | Zero       | Result is zero                           |
| 6   | N    | Subtract   | Last operation was a subtraction         |
| 5   | H    | Half-Carry | Carry from bit 3 to bit 4 occurred       |
| 4   | C    | Carry      | Carry out of bit 7 (or borrow for SUB)   |

### How Half-Carry Works

Half-carry tracks the carry between the low nibble (bits 0-3) and the
high nibble (bits 4-7). For ADD:

    H = ((a & 0x0F) + (b & 0x0F)) > 0x0F

For SUB:

    H = ((a & 0x0F) - (b & 0x0F)) < 0

### Flag Behavior by Operation

| Operation | Z          | N   | H              | C              |
|-----------|------------|-----|----------------|----------------|
| ADD a, b  | result==0  | 0   | nibble carry   | byte carry     |
| SUB a, b  | result==0  | 1   | nibble borrow  | byte borrow    |
| AND a, b  | result==0  | 0   | 1 (always)     | 0 (always)     |
| INC a     | result==0  | 0   | nibble carry   | unchanged      |
| DEC a     | result==0  | 1   | nibble borrow  | unchanged      |

## Instructions

1. Open `flags.py` and implement each TODO function.
2. All values are 8-bit unsigned (0-255).
3. Each function returns a dict with keys "Z", "N", "H", "C" (each bool).
4. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Results

```python
>>> compute_add_flags(0x0F, 0x01)
{"Z": False, "N": False, "H": True, "C": False}

>>> compute_sub_flags(0x10, 0x10)
{"Z": True, "N": True, "H": False, "C": False}
```
