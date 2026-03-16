# Capstone Disassembly Framework Cheat Sheet

## Installation

```bash
pip install capstone
```

## Python API Quick Reference

```python
from capstone import *
```

| Class / Constant     | Purpose                              |
|----------------------|--------------------------------------|
| `Cs(arch, mode)`     | Create disassembler instance         |
| `CS_ARCH_X86`        | x86 / x86-64 architecture           |
| `CS_ARCH_ARM`        | ARM (32-bit)                         |
| `CS_ARCH_ARM64`      | AArch64                              |
| `CS_ARCH_MIPS`       | MIPS                                 |
| `CS_ARCH_PPC`        | PowerPC                              |
| `CS_MODE_32`         | 32-bit mode                          |
| `CS_MODE_64`         | 64-bit mode                          |
| `CS_MODE_LITTLE_ENDIAN` | Little-endian (default)          |
| `CS_MODE_BIG_ENDIAN` | Big-endian                           |
| `CS_OPT_SYNTAX_ATT`  | AT&T syntax (x86)                   |
| `CS_OPT_SYNTAX_INTEL` | Intel syntax (x86)                 |

## Common Usage Patterns

### Basic Disassembly (3 Lines)

```python
md = Cs(CS_ARCH_X86, CS_MODE_32)
for insn in md.disasm(code_bytes, start_address):
    print(f"0x{insn.address:08x}:  {insn.mnemonic}\t{insn.op_str}")
```

### Accessing Instruction Details

```python
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True  # MUST enable for operand/group access

for insn in md.disasm(code_bytes, 0x1000):
    # Operand access
    for op in insn.operands:
        if op.type == CS_OP_REG:
            print(f"  Register: {insn.reg_name(op.reg)}")
        elif op.type == CS_OP_IMM:
            print(f"  Immediate: 0x{op.imm:x}")
        elif op.type == CS_OP_MEM:
            print(f"  Memory: base={insn.reg_name(op.mem.base)}, "
                  f"disp=0x{op.mem.disp:x}")

    # Instruction groups (jump, call, ret, etc.)
    if insn.group(CS_GRP_JUMP):
        print("  -> This is a branch instruction")
    if insn.group(CS_GRP_CALL):
        print("  -> This is a call instruction")
```

### Architecture Switching

```python
# x86-64
md_x64 = Cs(CS_ARCH_X86, CS_MODE_64)

# ARM Thumb mode
md_thumb = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

# MIPS 32-bit big-endian (N64, PS2)
md_mips = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN)

# PowerPC 32-bit big-endian (GameCube/Wii)
md_ppc = Cs(CS_ARCH_PPC, CS_MODE_32 + CS_MODE_BIG_ENDIAN)
```

### Setting Syntax (x86 Only)

```python
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.syntax = CS_OPT_SYNTAX_INTEL   # mov eax, [ebp+0x8]
# md.syntax = CS_OPT_SYNTAX_ATT   # movl 0x8(%ebp), %eax
```

## Architecture / Mode Combinations

| Target Platform     | Arch            | Mode                                  |
|---------------------|-----------------|---------------------------------------|
| DOS / Win32 / Xbox  | `CS_ARCH_X86`   | `CS_MODE_32`                          |
| Xbox 360 (Xenon)    | `CS_ARCH_PPC`   | `CS_MODE_32 + CS_MODE_BIG_ENDIAN`     |
| GameCube / Wii      | `CS_ARCH_PPC`   | `CS_MODE_32 + CS_MODE_BIG_ENDIAN`     |
| PS2 (EE core)       | `CS_ARCH_MIPS`  | `CS_MODE_MIPS64 + CS_MODE_BIG_ENDIAN` |
| N64                 | `CS_ARCH_MIPS`  | `CS_MODE_MIPS64 + CS_MODE_BIG_ENDIAN` |
| PS3 (Cell PPU)      | `CS_ARCH_PPC`   | `CS_MODE_64 + CS_MODE_BIG_ENDIAN`     |
| Game Boy (SM83)     | Not supported   | Use custom decoder                    |
| SNES (65816)        | Not supported   | Use custom decoder                    |
| x86-64 / PC        | `CS_ARCH_X86`   | `CS_MODE_64`                          |

## Common Gotchas

- **Endianness matters.** MIPS and PPC default to little-endian. Always add `CS_MODE_BIG_ENDIAN` for consoles (N64, PS2, GC, Wii, X360, PS3).
- **`md.detail = True` is off by default.** You must enable it before you can access operands, groups, or registers. It slows disassembly, so only enable when needed.
- **`disasm()` stops at the first invalid byte.** If you get fewer instructions than expected, check alignment and mode flags.
- **Mode flags are additive.** Combine with `+`, e.g., `CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN`.
- **Capstone does not resolve symbols.** You get raw addresses -- map them to names yourself.
- **SM83 (Game Boy) and 65816 (SNES) are not supported** by Capstone. You will need a dedicated decoder for those architectures.
