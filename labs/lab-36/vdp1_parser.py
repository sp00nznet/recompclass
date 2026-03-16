"""
Lab 36: Saturn VDP1 Command Parser

Parse VDP1 command table entries from raw binary data.  Each entry is
32 bytes and describes a drawing operation (sprite, polygon, line, etc.).

All multi-byte fields are **big-endian** (Saturn is big-endian SH-2).
"""

import struct

# ---------------------------------------------------------------------------
# Command type constants (bits 3-0 of CMDCTRL)
# ---------------------------------------------------------------------------

CMD_NORMAL_SPRITE   = 0x0
CMD_SCALED_SPRITE   = 0x1
CMD_DISTORTED_SPRITE = 0x2
CMD_POLYGON         = 0x4
CMD_POLYLINE        = 0x5
CMD_LINE            = 0x6
CMD_USER_CLIP       = 0x8
CMD_SYS_CLIP        = 0x9
CMD_LOCAL_COORD     = 0xA

COMMAND_NAMES = {
    CMD_NORMAL_SPRITE:    "NormalSprite",
    CMD_SCALED_SPRITE:    "ScaledSprite",
    CMD_DISTORTED_SPRITE: "DistortedSprite",
    CMD_POLYGON:          "Polygon",
    CMD_POLYLINE:         "Polyline",
    CMD_LINE:             "Line",
    CMD_USER_CLIP:        "UserClip",
    CMD_SYS_CLIP:         "SysClip",
    CMD_LOCAL_COORD:      "LocalCoord",
}

# ---------------------------------------------------------------------------
# Link mode constants (bits 14-12 of CMDCTRL)
# ---------------------------------------------------------------------------

LINK_JUMP_NEXT   = 0
LINK_JUMP_ASSIGN = 1
LINK_JUMP_CALL   = 2
LINK_JUMP_RETURN = 3

LINK_NAMES = {
    LINK_JUMP_NEXT:   "JumpNext",
    LINK_JUMP_ASSIGN: "JumpAssign",
    LINK_JUMP_CALL:   "JumpCall",
    LINK_JUMP_RETURN: "JumpReturn",
}

# ---------------------------------------------------------------------------
# Helper: read big-endian 16-bit values
# ---------------------------------------------------------------------------

def read_be16(data, offset):
    """Read an unsigned big-endian 16-bit value."""
    return struct.unpack_from(">H", data, offset)[0]


def read_be16_signed(data, offset):
    """Read a signed big-endian 16-bit value."""
    return struct.unpack_from(">h", data, offset)[0]


# ---------------------------------------------------------------------------
# Parsing functions -- complete the TODOs
# ---------------------------------------------------------------------------

def parse_cmdctrl(cmdctrl):
    """Parse the CMDCTRL word and return (end_flag, link_mode, cmd_type).

    Parameters
    ----------
    cmdctrl : int
        The 16-bit CMDCTRL value.

    Returns
    -------
    tuple of (bool, int, int)
        end_flag  -- True if bit 15 is set (end of command table).
        link_mode -- Bits 14-12 (0-7).
        cmd_type  -- Bits 3-0 (0-0xF).
    """
    # TODO: extract the three fields from cmdctrl
    #   end_flag  = bit 15
    #   link_mode = bits 14-12
    #   cmd_type  = bits 3-0
    pass


def parse_cmdsize(cmdsize):
    """Parse the CMDSIZE word and return (width, height) in pixels.

    The upper byte encodes width / 8, the lower byte encodes height.
    For example, CMDSIZE = 0x0210 means width = 2*8 = 16, height = 16.

    Returns
    -------
    tuple of (int, int)
        (width_pixels, height_pixels)
    """
    # TODO: decode width and height from cmdsize
    pass


def parse_vertices(data, offset):
    """Parse four vertices starting at *offset* in *data*.

    Each vertex is 4 bytes: signed-16 X then signed-16 Y, big-endian.
    There are four vertices (A, B, C, D) = 16 bytes total starting at
    offset 0x0C within a command entry.

    Parameters
    ----------
    data : bytes
        Raw command data (at least offset + 16 bytes).
    offset : int
        Byte offset of vertex A's X coordinate.

    Returns
    -------
    list of (int, int)
        Four (x, y) tuples.
    """
    # TODO: read four (x, y) pairs of signed big-endian 16-bit values
    pass


def parse_command(data, offset=0):
    """Parse one 32-byte VDP1 command table entry.

    Parameters
    ----------
    data : bytes
        Raw data containing at least 32 bytes from *offset*.
    offset : int
        Starting byte offset of the command entry.

    Returns
    -------
    dict with keys:
        "end"        : bool   -- True if this is the last command.
        "link_mode"  : int    -- Link mode enum value.
        "link_name"  : str    -- Human-readable link mode name.
        "cmd_type"   : int    -- Command type enum value.
        "cmd_name"   : str    -- Human-readable command name.
        "cmd_link"   : int    -- CMDLINK value (jump target).
        "draw_mode"  : int    -- CMDPMOD value.
        "color"      : int    -- CMDCOLR value.
        "tex_addr"   : int    -- Character VRAM address (CMDSRCA * 8).
        "width"      : int    -- Texture width in pixels.
        "height"     : int    -- Texture height in pixels.
        "vertices"   : list   -- Four (x, y) tuples.
        "gouraud"    : int    -- Gouraud shading table address.
    """
    # TODO: use read_be16 / read_be16_signed and the helpers above to
    # build and return the dict described in the docstring.
    #
    # Steps:
    #   1. Read CMDCTRL at offset+0x00 and parse with parse_cmdctrl().
    #   2. Read CMDLINK at offset+0x02.
    #   3. Read CMDPMOD at offset+0x04.
    #   4. Read CMDCOLR at offset+0x06.
    #   5. Read CMDSRCA at offset+0x08, multiply by 8 for tex_addr.
    #   6. Read CMDSIZE at offset+0x0A and parse with parse_cmdsize().
    #   7. Parse vertices starting at offset+0x0C.
    #   8. Read gouraud table at offset+0x1C.
    #   9. Build and return the dict.
    pass


def parse_command_table(data):
    """Parse an entire VDP1 command table from *data*.

    Reads 32-byte entries sequentially until an end flag is found or
    data runs out.

    Returns
    -------
    list of dict
        Each dict is the result of parse_command().
    """
    # TODO: iterate through data in 32-byte steps, calling
    # parse_command() on each.  Stop when end_flag is True or when
    # there are fewer than 32 bytes remaining.
    pass


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def format_command(cmd):
    """Return a one-line human-readable string for a parsed command."""
    name = cmd["cmd_name"]
    link = cmd["link_name"]

    if cmd["end"]:
        return "END"

    if cmd["cmd_type"] in (CMD_NORMAL_SPRITE, CMD_SCALED_SPRITE,
                            CMD_DISTORTED_SPRITE):
        vx, vy = cmd["vertices"][0]
        return (f"{name:<16s} link={link}  pos=({vx}, {vy})  "
                f"tex=0x{cmd['tex_addr']:04X}  "
                f"size={cmd['width']}x{cmd['height']}  "
                f"color=0x{cmd['color']:04X}")

    if cmd["cmd_type"] == CMD_POLYGON:
        vs = cmd["vertices"]
        vstr = "".join(f"({x},{y})" for x, y in vs)
        return (f"{name:<16s} link={link}  verts={vstr}  "
                f"color=0x{cmd['color']:04X}")

    if cmd["cmd_type"] in (CMD_LINE, CMD_POLYLINE):
        a = cmd["vertices"][0]
        b = cmd["vertices"][1]
        return (f"{name:<16s} link={link}  "
                f"A=({a[0]}, {a[1]}) B=({b[0]}, {b[1]})  "
                f"color=0x{cmd['color']:04X}")

    if cmd["cmd_type"] == CMD_LOCAL_COORD:
        vx, vy = cmd["vertices"][0]
        return f"{name:<16s} link={link}  origin=({vx}, {vy})"

    return f"{name:<16s} link={link}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python vdp1_parser.py <binary_file>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        raw = f.read()

    cmds = parse_command_table(raw)
    for i, cmd in enumerate(cmds):
        print(f"Cmd {i}: {format_command(cmd)}")
