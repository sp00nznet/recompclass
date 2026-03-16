# Lab 27: ARM/Thumb Disassembler

## Objective

Use the Capstone disassembly library to disassemble binary blobs
containing both ARM (32-bit) and Thumb (16-bit) instructions. GBA code
switches between these modes constantly, so any GBA recompiler needs to
handle both.

## Background

The ARM7TDMI in the GBA supports two instruction sets:

- **ARM mode**: 32-bit fixed-width instructions, aligned to 4 bytes.
- **Thumb mode**: 16-bit fixed-width instructions, aligned to 2 bytes.

Mode switching happens via the `BX` (Branch and Exchange) instruction.
The target address's lowest bit determines the mode:

- Bit 0 = 0 -> switch to ARM mode
- Bit 0 = 1 -> switch to Thumb mode

(The actual branch target is the address with bit 0 masked off.)

### Capstone Setup

```python
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB

arm_cs = Cs(CS_ARCH_ARM, CS_MODE_ARM)        # ARM mode
thumb_cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)     # Thumb mode
```

## Instructions

1. Open `arm_disasm.py` and implement the TODO functions.
2. `disasm_arm()` -- disassemble a blob as ARM instructions.
3. `disasm_thumb()` -- disassemble a blob as Thumb instructions.
4. `detect_mode_switches()` -- scan disassembly for BX instructions and
   report what mode the target would switch to.
5. `disasm_auto()` -- disassemble with automatic ARM/Thumb mode tracking.
6. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
[ARM]   0x08000000: mov   r0, #0x42
[ARM]   0x08000004: bx    r1
[THUMB] 0x08000008: movs  r0, #0
[THUMB] 0x0800000a: adds  r0, #1
```
