"""
Lab 33: N64 Display List Parser

Parse Fast3D display list commands from a binary dump.
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Command IDs
# ---------------------------------------------------------------------------

COMMAND_NAMES = {
    0x01: "G_MTX",
    0x03: "G_MOVEMEM",
    0x04: "G_VTX",
    0x05: "G_DL",
    0x06: "G_TRI1",
    0xB6: "G_CLEARGEOMETRYMODE",
    0xB7: "G_SETGEOMETRYMODE",
    0xB8: "G_ENDDL",
    0xB9: "G_SETOTHERMODE_L",
    0xBA: "G_SETOTHERMODE_H",
    0xBF: "G_TRI1_F3DEX",
    0xF3: "G_LOADBLOCK",
    0xF5: "G_SETTILE",
    0xFD: "G_SETTIMG",
}


# ---------------------------------------------------------------------------
# Command Parsing
# ---------------------------------------------------------------------------

def parse_command(data, offset):
    """Parse a single 8-byte display list command.

    Args:
        data: bytes of the display list binary.
        offset: byte offset of the command (must be 8-byte aligned).

    Returns:
        A dict with keys:
            "offset"   - int, byte offset in the data
            "cmd_id"   - int, the command byte (first byte)
            "cmd_name" - str, human-readable name (from COMMAND_NAMES)
            "raw"      - bytes, the full 8-byte command
            "params"   - dict, command-specific parsed parameters

        The "params" dict varies by command:

        G_VTX (0x04):
            "count" - int, number of vertices
            "addr"  - int, DRAM address (bytes 4-7 as big-endian uint32)

        G_TRI1 (0x06):
            "v0" - int, vertex index 0
            "v1" - int, vertex index 1
            "v2" - int, vertex index 2

        G_DL (0x05):
            "addr" - int, address of sub-display list

        G_SETTIMG (0xFD):
            "addr" - int, texture DRAM address

        All other commands:
            "word0" - int, first 4 bytes as big-endian uint32
            "word1" - int, last 4 bytes as big-endian uint32

        Returns None if there are fewer than 8 bytes remaining.
    """
    # TODO: 1. Check that offset + 8 <= len(data). Return None if not.
    # TODO: 2. Read the 8 bytes: data[offset:offset+8]
    # TODO: 3. The command ID is the first byte.
    # TODO: 4. Look up the command name in COMMAND_NAMES. Use "UNKNOWN"
    #          if not found.
    # TODO: 5. Parse command-specific parameters:
    #
    #   For G_VTX (0x04):
    #       count = (data[offset+1] >> 4) & 0x0F
    #       addr  = struct.unpack_from(">I", data, offset+4)[0]
    #
    #   For G_TRI1 (0x06):
    #       v0 = data[offset+5] // 2
    #       v1 = data[offset+6] // 2
    #       v2 = data[offset+7] // 2
    #
    #   For G_DL (0x05) and G_SETTIMG (0xFD):
    #       addr = struct.unpack_from(">I", data, offset+4)[0]
    #
    #   For everything else:
    #       word0 = struct.unpack_from(">I", data, offset)[0]
    #       word1 = struct.unpack_from(">I", data, offset+4)[0]
    #
    # TODO: 6. Return the dict.
    pass


def parse_display_list(data):
    """Parse a complete display list binary.

    Decodes 8-byte commands sequentially. Stops at the end of data
    or when a G_ENDDL (0xB8) command is encountered (inclusive --
    include the ENDDL in the results).

    Args:
        data: bytes of the display list.

    Returns:
        A list of parsed command dicts (from parse_command).
    """
    # TODO: Walk through data in 8-byte steps, calling parse_command().
    #       Stop after G_ENDDL or end of data.
    pass


def format_command(cmd):
    """Format a parsed command for display.

    Args:
        cmd: dict from parse_command().

    Returns:
        A string like "0000: G_VTX       count=4, addr=0x06000000"
    """
    # TODO: Format based on cmd_name.
    #       Use f"{cmd['offset']:04X}: {cmd['cmd_name']:20s}" as prefix.
    #       Append parameter details for known commands.
    pass


def summarize(commands):
    """Produce a summary counting each command type.

    Args:
        commands: list of parsed command dicts.

    Returns:
        A dict mapping command name (str) -> count (int).
    """
    # TODO: Count occurrences of each cmd_name.
    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Example display list: VTX, TRI1, TRI1, ENDDL
    dlist = bytes([
        # G_VTX: count=4, addr=0x06000000
        0x04, 0x40, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00,
        # G_TRI1: v0=0, v1=1, v2=2
        0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x04,
        # G_TRI1: v0=0, v1=2, v2=3
        0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x06,
        # G_ENDDL
        0xB8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])

    commands = parse_display_list(dlist)
    if commands is None:
        print("parse_display_list() returned None -- implement the TODO sections.")
        return

    for cmd in commands:
        line = format_command(cmd)
        if line:
            print(line)

    print()
    summary = summarize(commands)
    if summary:
        print("Summary:")
        for name, count in sorted(summary.items()):
            print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
