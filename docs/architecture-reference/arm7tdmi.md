# ARM7TDMI (GBA / Dreamcast Sound) Quick Reference

## Overview

The ARM7TDMI is a 32-bit RISC processor used as the main CPU in the Game Boy Advance (16.78 MHz) and as the AICA sound processor in the Sega Dreamcast. It supports two instruction sets: ARM (32-bit) and Thumb (16-bit compressed), and features a 3-stage pipeline.

- Clock: 16.78 MHz (GBA), 45 MHz (Dreamcast AICA)
- 32-bit data bus, 32-bit address bus (4 GB addressable)
- Bi-endian (GBA uses little-endian)
- Von Neumann architecture (shared code/data bus on GBA)

The "TDMI" stands for: **T**humb + **D**ebug + **M**ultiplier + **I**CE (in-circuit emulation).

---

## Registers

### ARM Mode

| Register   | Alias    | Description                          |
|------------|----------|--------------------------------------|
| r0 - r12   | --       | General purpose                      |
| r13        | SP       | Stack pointer (by convention)        |
| r14        | LR       | Link register (return address)       |
| r15        | PC       | Program counter                      |
| CPSR       | --       | Current Program Status Register      |

r15 (PC) reads as current instruction address + 8 in ARM mode, + 4 in Thumb mode (due to pipeline).

### Banked Registers

Each processor mode has its own r13 (SP) and r14 (LR). FIQ mode additionally banks r8-r12 for fast interrupt handling.

| Mode        | Banked Registers          | Trigger                  |
|-------------|---------------------------|--------------------------|
| User (USR)  | (base set)                | Normal execution         |
| FIQ         | r8-r14, SPSR              | Fast interrupt           |
| IRQ         | r13-r14, SPSR             | Normal interrupt         |
| Supervisor  | r13-r14, SPSR             | SWI / reset              |
| Abort       | r13-r14, SPSR             | Memory fault             |
| Undefined   | r13-r14, SPSR             | Undefined instruction    |
| System      | (shares User registers)   | Privileged user-mode     |

### CPSR (Current Program Status Register)

| Bits    | Name      | Description                              |
|---------|-----------|------------------------------------------|
| 31      | N         | Negative (sign bit of result)            |
| 30      | Z         | Zero                                     |
| 29      | C         | Carry                                    |
| 28      | V         | Overflow                                 |
| 7       | I         | IRQ disable                              |
| 6       | F         | FIQ disable                              |
| 5       | T         | Thumb state (0=ARM, 1=Thumb)             |
| 4:0     | Mode      | Processor mode (USR=0x10, FIQ=0x11, IRQ=0x12, SVC=0x13, ABT=0x17, UND=0x1B, SYS=0x1F) |

---

## ARM Mode (32-bit Instructions)

All instructions are 32 bits, aligned to 4-byte boundaries.

### Conditional Execution

Every ARM instruction has a 4-bit condition field (bits 31:28). Any instruction can be made conditional:

| Suffix | Condition        | Flags Tested      |
|--------|------------------|--------------------|
| EQ     | Equal            | Z=1                |
| NE     | Not equal        | Z=0                |
| CS/HS  | Carry set / >=   | C=1                |
| CC/LO  | Carry clear / <  | C=0                |
| MI     | Minus (negative) | N=1                |
| PL     | Plus (positive)  | N=0                |
| VS     | Overflow         | V=1                |
| VC     | No overflow      | V=0                |
| HI     | Unsigned >       | C=1 and Z=0        |
| LS     | Unsigned <=      | C=0 or Z=1         |
| GE     | Signed >=        | N=V                |
| LT     | Signed <         | N!=V               |
| GT     | Signed >         | Z=0 and N=V        |
| LE     | Signed <=        | Z=1 or N!=V        |
| AL     | Always (default) | (unconditional)    |

Example: `ADDNE r0, r1, r2` -- only adds if Z=0.

### Barrel Shifter

The second operand of most data-processing instructions can be shifted for free:

| Shift     | Syntax         | Operation           |
|-----------|----------------|----------------------|
| LSL       | Rm, LSL #imm   | Logical shift left   |
| LSR       | Rm, LSR #imm   | Logical shift right  |
| ASR       | Rm, ASR #imm   | Arithmetic shift right |
| ROR       | Rm, ROR #imm   | Rotate right         |
| RRX       | Rm, RRX        | Rotate right through carry (1-bit) |

Shift amount can also come from a register: `Rm, LSL Rs`.

### Key ARM Instructions

| Category     | Instructions                                    | Notes                              |
|--------------|-------------------------------------------------|------------------------------------|
| Data Proc    | ADD, ADC, SUB, SBC, RSB, RSC                    | RSB = reverse subtract             |
| Logic        | AND, ORR, EOR, BIC, MOV, MVN                    | BIC = bit clear (AND NOT)          |
| Compare      | CMP, CMN, TST, TEQ                              | Set flags only, no result stored   |
| Multiply     | MUL, MLA, UMULL, UMLAL, SMULL, SMLAL            | MLA = multiply-accumulate          |
| Load/Store   | LDR, LDRB, LDRH, LDRSB, LDRSH, STR, STRB, STRH | Signed/unsigned byte/halfword      |
| Multi-Load   | LDM, STM                                        | Load/store multiple registers      |
| Branch       | B, BL, BX                                       | BL = branch and link; BX = exchange|
| Swap         | SWP, SWPB                                       | Atomic read-modify-write           |
| Status       | MRS, MSR                                        | Read/write CPSR/SPSR               |
| Software Int | SWI                                              | System call (BIOS call on GBA)     |

**S suffix:** Adding 'S' to data-processing instructions updates CPSR flags: `ADDS r0, r1, r2`.

**LDM/STM addressing modes:** IA (increment after), IB (increment before), DA (decrement after), DB (decrement before). Common idiom: `STMFD SP!, {r4-r11, LR}` to push registers; `LDMFD SP!, {r4-r11, PC}` to pop and return.

---

## Thumb Mode (16-bit Instructions)

Thumb instructions are 16 bits, aligned to 2-byte boundaries. They provide better code density but with restrictions:

- Most instructions can only access r0-r7 (low registers)
- No conditional execution (except conditional branches)
- No barrel shifter on most instructions
- Reduced immediate ranges
- Flag-setting is implicit (no S suffix choice)

### Key Thumb Instructions

| Category     | Instructions                              | Notes                                |
|--------------|-------------------------------------------|--------------------------------------|
| Data Proc    | ADD, SUB, MOV, CMP, NEG                  | 3-operand and 2-operand forms        |
| Logic        | AND, ORR, EOR, BIC, MVN, TST             |                                      |
| Shift        | LSL, LSR, ASR                             | Separate instructions (not modifier) |
| Multiply     | MUL                                       | Rd = Rd * Rm                         |
| Load/Store   | LDR, LDRB, LDRH, LDRSB, LDRSH, STR, STRB, STRH | SP-relative and PC-relative forms |
| Multi-Load   | LDMIA, STMIA                              | Only increment-after                 |
| Stack        | PUSH, POP                                 | PUSH {r0-r7, LR}, POP {r0-r7, PC}   |
| Branch       | B, BL, BX                                 | BL is a 2-instruction pair           |
| Hi-Reg       | MOV, ADD, CMP, BX                         | Can access r8-r15                    |
| PC-relative  | LDR Rd, [PC, #imm]                        | Constant pool loads                  |
| SP-relative  | LDR/STR Rd, [SP, #imm]                    | Stack frame access                   |
| Address Gen  | ADD Rd, PC/SP, #imm                       | Compute addresses                    |
| Software Int | SWI imm8                                  | BIOS call                            |

---

## ARM/Thumb Interworking

The BX (Branch and Exchange) instruction switches between ARM and Thumb modes:

```
BX Rm        ; Branch to address in Rm
             ; If bit 0 of Rm is 1 -> switch to Thumb
             ; If bit 0 of Rm is 0 -> switch to ARM
```

The T bit in CPSR reflects the current state. BL in Thumb mode does NOT exchange; to call an ARM function from Thumb, you must use BX with LR set manually (or use a veneer).

---

## GBA BIOS SWI Calls

The GBA BIOS provides functions via the SWI instruction. In ARM mode, the function number is in the SWI immediate (bits 16-23). In Thumb mode, it is the full 8-bit immediate.

| SWI# (Thumb) | Function            | Description                          |
|---------------|---------------------|--------------------------------------|
| 0x00          | SoftReset           | Reset to ROM entry point             |
| 0x01          | RegisterRamReset    | Clear selected memory regions        |
| 0x02          | Halt                | Low-power halt until interrupt       |
| 0x05          | VBlankIntrWait      | Wait for VBlank interrupt            |
| 0x06          | Div                 | Signed division (r0/r1)             |
| 0x08          | Sqrt                | Square root                          |
| 0x09          | ArcTan              | Arctangent                           |
| 0x0A          | ArcTan2             | Arctangent2                          |
| 0x0B          | CpuSet              | Memory fill/copy (word/halfword)     |
| 0x0C          | CpuFastSet          | Fast memory copy (32-byte blocks)    |
| 0x0E          | BgAffineSet         | Calculate BG affine parameters       |
| 0x0F          | ObjAffineSet        | Calculate sprite affine parameters   |
| 0x10          | BitUnPack           | Bit-depth expansion                  |
| 0x11          | LZ77UnCompWram      | LZ77 decompress to WRAM             |
| 0x12          | LZ77UnCompVram      | LZ77 decompress to VRAM             |
| 0x13          | HuffUnComp          | Huffman decompress                   |
| 0x14          | RLUnCompWram        | Run-length decompress to WRAM       |
| 0x15          | RLUnCompVram        | Run-length decompress to VRAM       |

Recompilers often HLE (high-level emulate) these BIOS calls rather than recompiling the BIOS ROM.

---

## GBA Memory Map (Key Regions)

| Address Range         | Size    | Width   | Description                |
|-----------------------|---------|---------|----------------------------|
| 0x00000000-0x00003FFF | 16 KB   | 32-bit  | BIOS ROM                   |
| 0x02000000-0x0203FFFF | 256 KB  | 16-bit  | EWRAM (external work RAM)  |
| 0x03000000-0x03007FFF | 32 KB   | 32-bit  | IWRAM (internal work RAM)  |
| 0x04000000-0x040003FF | 1 KB    | varies  | I/O registers              |
| 0x05000000-0x050003FF | 1 KB    | 16-bit  | Palette RAM                |
| 0x06000000-0x06017FFF | 96 KB   | 16-bit  | VRAM                       |
| 0x07000000-0x070003FF | 1 KB    | 32-bit  | OAM (sprite attributes)    |
| 0x08000000-0x09FFFFFF | 32 MB   | 16-bit  | Game Pak ROM (wait state 0)|
| 0x0A000000-0x0BFFFFFF | 32 MB   | 16-bit  | Game Pak ROM (wait state 1)|
| 0x0C000000-0x0DFFFFFF | 32 MB   | 16-bit  | Game Pak ROM (wait state 2)|
| 0x0E000000-0x0E00FFFF | 64 KB   | 8-bit   | Game Pak SRAM/Flash        |

**Bus width matters:** Code in IWRAM (32-bit bus) runs ARM instructions at full speed. Code in ROM (16-bit bus) benefits from Thumb mode since each instruction is one bus read instead of two.

---

## Recompiler Pain Points

- **Dual instruction sets:** The recompiler must decode both ARM (32-bit) and Thumb (16-bit) instructions and handle interworking transitions via BX at any point.
- **Conditional execution (ARM):** Nearly every ARM instruction can be conditional. Naively emitting a branch for each condition is expensive; recognizing common patterns (e.g., conditional MOV as a select) is key.
- **Barrel shifter operands:** The second operand of data-processing instructions includes a free shift. This means a single ARM instruction like `ADD r0, r1, r2, LSL #3` combines a shift and add. The recompiler must decompose or pattern-match these.
- **PC as general-purpose register:** r15 is both the PC and a general-purpose register. Reading PC in a data-processing instruction yields PC+8 (ARM) or PC+4 (Thumb). Writing PC is a branch. Instructions like `ADD PC, PC, r0` create computed jumps.
- **LDM/STM with PC:** `LDM {..., PC}` is both a load and a branch. `STM {..., PC}` stores PC+12 (implementation-defined). These are common in function epilogues and context switches.
- **BIOS calls (SWI):** Most recompilers HLE BIOS functions rather than recompiling the BIOS ROM. The decompression routines (LZ77, Huffman, RLE) are called frequently.
- **Bus width and timing:** GBA code in 16-bit ROM runs Thumb efficiently but ARM slowly (2 fetches per instruction). Some games mix modes strategically, and cycle-accurate recompilation must account for bus width.
- **Banked registers:** Mode switches (via MSR or exceptions) swap the active SP, LR, and (in FIQ) r8-r12. The recompiler must maintain separate register storage per mode.
