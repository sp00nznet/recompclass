# Lab 36: Saturn VDP1 Command Parser

## Objective

Parse Sega Saturn VDP1 command table entries from raw binary data. The VDP1
is the Saturn's sprite/polygon processor and operates by reading a linked
list of 32-byte command table entries from VRAM.

By the end of this lab you will be able to:

- Decode VDP1 command types (sprite draw, polygon, polyline, line, etc.)
- Extract coordinate, color, and texture fields from command words
- Reconstruct draw parameters from packed binary formats

## Background

The Sega Saturn's VDP1 is a 2D sprite and polygon engine. It reads a
**command table** from VRAM -- a linked list of 32-byte entries that
describe what to draw. Each command entry contains:

| Offset | Size    | Field                     |
|--------|---------|---------------------------|
| 0x00   | 2 bytes | Control word (CMDCTRL)     |
| 0x02   | 2 bytes | Link specification (CMDLINK) |
| 0x04   | 2 bytes | Draw mode (CMDPMOD)        |
| 0x06   | 2 bytes | Color bank/table (CMDCOLR) |
| 0x08   | 2 bytes | Character address (CMDSRCA) |
| 0x0A   | 2 bytes | Character size (CMDSIZE)   |
| 0x0C   | 4 bytes | Vertex A: X (2), Y (2)    |
| 0x10   | 4 bytes | Vertex B: X (2), Y (2)    |
| 0x14   | 4 bytes | Vertex C: X (2), Y (2)    |
| 0x18   | 4 bytes | Vertex D: X (2), Y (2)    |
| 0x1C   | 2 bytes | Gouraud shading table      |
| 0x1E   | 2 bytes | Reserved                   |

### Command Types (bits 3-0 of CMDCTRL)

| Value | Command              |
|-------|----------------------|
| 0x0   | Normal Sprite Draw   |
| 0x1   | Scaled Sprite Draw   |
| 0x2   | Distorted Sprite Draw|
| 0x4   | Polygon Draw         |
| 0x5   | Polyline Draw        |
| 0x6   | Line Draw            |
| 0x8   | User Clipping Set    |
| 0x9   | System Clipping Set  |
| 0xA   | Local Coord Set      |

### Link Modes (bits 14-12 of CMDCTRL)

| Value | Meaning              |
|-------|----------------------|
| 0     | Jump Next            |
| 1     | Jump Assign (CMDLINK)|
| 2     | Jump Call            |
| 3     | Jump Return          |

Bit 15 of CMDCTRL is the **end flag** -- if set, the command table ends.

Coordinates are **signed 16-bit** values (two's complement). The character
address in CMDSRCA is multiplied by 8 to get the actual VRAM byte address.
CMDSIZE encodes width in the upper byte (value x 8 pixels) and height in
the lower byte.

## Files

| File              | Description                            |
|-------------------|----------------------------------------|
| `vdp1_parser.py`  | VDP1 command parser (starter code)    |
| `test_lab.py`      | Pytest test suite                     |

## Instructions

1. Open `vdp1_parser.py` and read the starter code.
2. Complete each function marked with a `TODO` comment.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
Cmd 0: NormalSprite  link=JumpNext  pos=(32, 64)  tex=0x0400  size=16x16  color=0x0100
Cmd 1: Polygon       link=JumpNext  verts=(0,0)(100,0)(100,80)(0,80)  color=0x7C00
Cmd 2: Line          link=JumpNext  A=(10, 10) B=(200, 150)  color=0x001F
Cmd 3: LocalCoord    link=JumpNext  origin=(160, 112)
Cmd 4: END
```

## References

- Sega Saturn VDP1 User's Manual
- Charles MacDonald's Saturn VDP1 documentation
