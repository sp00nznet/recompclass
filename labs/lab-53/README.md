# Lab 53: Table-Driven Lifter Generation

## Objective

Build the generator from Module 34: an ISA description in, a decoder table
out, and from that table **both** a lifter and an interpreter.

## Background

Hand-written `switch` trees over 256 opcodes rot. Tables are diffable against
the ISA manual, and `tirecomp`'s decoder is one row per opcode carrying the
mnemonic, operand kind, control-flow class and cycles:

```c
/* 0xE8 */ {"RET PE",_NO,BR,0},  {"JP (HL)",_NO,JH,0},  ...
```

**The control-flow class is the load-bearing column.** Your analyser needs
"is this a branch, a call, a return, or an indirect jump" for every opcode,
and deriving it from the mnemonic string is how you get a bug on `JP (HL)`
specifically.

And Module 34 section 7's design consequence: generate the lifter and the
interpreter **from the same table**. It is a fraction of the work if you plan
for it and a rewrite if you do not.

## Your Task

Implement in `isagen.py`:

- `parse_isa(text)` -- parse the description format below into entries.
- `build_table(entries)` -- a 256-entry table indexed by opcode, with `None`
  for undefined opcodes.
- `emit_lifter(table)` -- generate C, one case per opcode.
- `emit_interpreter(table)` -- generate a Python interpreter from the *same*
  table.
- `check_coverage(table)` -- which opcodes are undefined.

### Description format

```
# opcode | mnemonic | operand | class | cycles | semantics
0x00 | NOP  | none | normal | 4 | pass
0x3E | LD_A | imm8 | normal | 8 | a = imm
0xC3 | JP   | imm16| branch | 16| pc = imm
0xC9 | RET  | none | return | 16| pc = pop()
0xE9 | JP_HL| none | indirect | 4 | pc = hl
```

Blank lines and `#` comments are ignored.

## Why This Matters

A lifter and an interpreter that disagree cannot be used to check each other
(Module 38 section 2). Sharing the table means a decode bug affects both
identically -- which is a real limitation you must state -- but a *lifting*
bug shows up immediately.
