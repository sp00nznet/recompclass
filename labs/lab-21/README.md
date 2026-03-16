# Lab 21: 6502 Instruction Decoder

## Objective

Write a Python decoder for 6502 instructions that maps raw bytes to
mnemonics, addressing modes, and operand sizes. This is a foundational
skill for NES recompilation work -- before you can lift 6502 code, you
need to understand what each byte means.

## Background

The MOS 6502 uses variable-length instructions (1 to 3 bytes). The first
byte is always the opcode, which determines the mnemonic, addressing mode,
and how many additional bytes (0, 1, or 2) to read as the operand.

There are roughly 56 official mnemonics (151 valid opcode byte values when
you count all addressing mode variants). This lab covers the most common
subset.

### Addressing Modes

| Mode          | Syntax         | Operand Size |
|---------------|----------------|--------------|
| Implied       | `CLC`          | 0 bytes      |
| Accumulator   | `ASL A`        | 0 bytes      |
| Immediate     | `LDA #$nn`     | 1 byte       |
| Zero Page     | `LDA $nn`      | 1 byte       |
| Zero Page,X   | `LDA $nn,X`   | 1 byte       |
| Zero Page,Y   | `LDX $nn,Y`   | 1 byte       |
| Absolute      | `LDA $nnnn`    | 2 bytes      |
| Absolute,X    | `LDA $nnnn,X` | 2 bytes      |
| Absolute,Y    | `LDA $nnnn,Y` | 2 bytes      |
| Indirect      | `JMP ($nnnn)`  | 2 bytes      |
| (Indirect,X)  | `LDA ($nn,X)`  | 1 byte       |
| (Indirect),Y  | `LDA ($nn),Y`  | 1 byte       |
| Relative      | `BEQ $nnnn`    | 1 byte       |

## Instructions

1. Open `decoder_6502.py` and review the provided `OPCODE_TABLE`.
2. Implement `decode_instruction()` -- read the opcode byte, look it up,
   read the operand bytes (if any), and return a dict with the decoded info.
3. Implement `format_instruction()` -- turn the decoded dict into a
   human-readable string using the correct syntax for each addressing mode.
4. Implement `disassemble()` -- walk through a byte stream, decoding each
   instruction and collecting the formatted strings.
5. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
$8000: LDA #$42
$8002: STA $0200
$8005: INX
$8006: BNE $8002
$8008: RTS
```
