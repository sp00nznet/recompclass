# Lab 33: N64 Display List Parser

## Objective

Parse a binary dump of N64 Fast3D display list commands. The N64's RDP
(Reality Display Processor) is driven by display lists -- streams of
64-bit commands that tell it what to draw. Understanding these is
essential for recompiling N64 graphics code.

## Background

N64 games use microcode running on the RSP (Reality Signal Processor) to
generate display lists for the RDP. The most common microcode is Fast3D
(and its successors F3DEX, F3DEX2).

Each display list command is exactly 8 bytes (64 bits). The first byte
is the command ID.

### Common Fast3D Commands

| Byte 0 | Command       | Description                           |
|--------|---------------|---------------------------------------|
| 0x01   | G_MTX         | Load a matrix                         |
| 0x03   | G_MOVEMEM     | Move memory (e.g., lights, viewport)  |
| 0x04   | G_VTX         | Load vertices into vertex buffer      |
| 0x05   | G_DL          | Branch to sub-display list            |
| 0x06   | G_TRI1        | Draw one triangle                     |
| 0xB6   | G_CLEARGEOMETRYMODE | Clear geometry mode flags       |
| 0xB7   | G_SETGEOMETRYMODE   | Set geometry mode flags         |
| 0xB8   | G_ENDDL       | End display list                      |
| 0xB9   | G_SETOTHERMODE_L | Set other modes (low)             |
| 0xBA   | G_SETOTHERMODE_H | Set other modes (high)            |
| 0xBF   | G_TRI1 (F3DEX)| Draw one triangle (F3DEX variant)     |
| 0xF5   | G_SETTILE     | Set tile descriptor                   |
| 0xF3   | G_LOADBLOCK   | Load texture block                    |
| 0xFD   | G_SETTIMG     | Set texture image source              |

### G_VTX (0x04) Word Layout

```
Byte 0: 0x04 (command ID)
Byte 1: (count << 4) | length (packed)
Bytes 2-3: unused / varies by microcode
Bytes 4-7: DRAM address of vertex data (segment address)
```

### G_TRI1 (0x06) Word Layout

```
Byte 0: 0x06 (command ID)
Bytes 1-3: padding
Byte 5: vertex index 0 (divided by 2 in some microcode versions)
Byte 6: vertex index 1
Byte 7: vertex index 2
```

## Instructions

1. Open `dlist_parser.py` and implement the TODO functions.
2. `parse_command()` -- decode a single 8-byte command.
3. `parse_display_list()` -- decode a stream of commands.
4. `summarize()` -- produce a summary of command types found.
5. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
0000: G_VTX       count=4, addr=0x06000000
0008: G_TRI1      v0=0, v1=1, v2=2
0010: G_TRI1      v0=0, v1=2, v2=3
0018: G_ENDDL
```
