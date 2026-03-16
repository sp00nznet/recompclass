"""
Tests for Lab 36: Saturn VDP1 Command Parser
"""

import struct
import vdp1_parser as vdp


# ---------------------------------------------------------------------------
# Helpers for building test command entries (big-endian, 32 bytes each)
# ---------------------------------------------------------------------------

def build_cmd(cmdctrl=0, cmdlink=0, cmdpmod=0, cmdcolr=0,
              cmdsrca=0, cmdsize=0, verts=None, gouraud=0):
    """Build a 32-byte VDP1 command table entry."""
    if verts is None:
        verts = [(0, 0)] * 4
    data = struct.pack(">HHHHHH",
                       cmdctrl, cmdlink, cmdpmod, cmdcolr, cmdsrca, cmdsize)
    for x, y in verts:
        data += struct.pack(">hh", x, y)
    data += struct.pack(">HH", gouraud, 0)
    assert len(data) == 32
    return data


# ---------------------------------------------------------------------------
# CMDCTRL parsing
# ---------------------------------------------------------------------------

class TestParseCmdctrl:
    def test_normal_sprite(self):
        end, link, cmd = vdp.parse_cmdctrl(0x0000)
        assert end is False
        assert link == 0
        assert cmd == 0

    def test_polygon(self):
        end, link, cmd = vdp.parse_cmdctrl(0x0004)
        assert cmd == vdp.CMD_POLYGON

    def test_end_flag(self):
        end, link, cmd = vdp.parse_cmdctrl(0x8000)
        assert end is True

    def test_link_assign(self):
        # bits 14-12 = 1 -> 0x1000
        end, link, cmd = vdp.parse_cmdctrl(0x1004)
        assert end is False
        assert link == vdp.LINK_JUMP_ASSIGN
        assert cmd == vdp.CMD_POLYGON

    def test_link_return_with_line(self):
        # bits 14-12 = 3 -> 0x3000
        end, link, cmd = vdp.parse_cmdctrl(0x3006)
        assert link == vdp.LINK_JUMP_RETURN
        assert cmd == vdp.CMD_LINE

    def test_end_and_link(self):
        # end flag + link assign
        end, link, cmd = vdp.parse_cmdctrl(0x9000)
        assert end is True
        assert link == vdp.LINK_JUMP_ASSIGN


# ---------------------------------------------------------------------------
# CMDSIZE parsing
# ---------------------------------------------------------------------------

class TestParseCmdsize:
    def test_16x16(self):
        # width_code=2 (2*8=16), height=16 -> 0x0210
        w, h = vdp.parse_cmdsize(0x0210)
        assert w == 16
        assert h == 16

    def test_32x32(self):
        w, h = vdp.parse_cmdsize(0x0420)
        assert w == 32
        assert h == 32

    def test_8x8(self):
        w, h = vdp.parse_cmdsize(0x0108)
        assert w == 8
        assert h == 8

    def test_64x128(self):
        w, h = vdp.parse_cmdsize(0x0880)
        assert w == 64
        assert h == 128


# ---------------------------------------------------------------------------
# Vertex parsing
# ---------------------------------------------------------------------------

class TestParseVertices:
    def test_positive_coords(self):
        data = struct.pack(">hhhhhhhh",
                           10, 20, 30, 40, 50, 60, 70, 80)
        verts = vdp.parse_vertices(data, 0)
        assert verts == [(10, 20), (30, 40), (50, 60), (70, 80)]

    def test_negative_coords(self):
        data = struct.pack(">hhhhhhhh",
                           -1, -2, -100, -200, 0, 0, 320, 224)
        verts = vdp.parse_vertices(data, 0)
        assert verts == [(-1, -2), (-100, -200), (0, 0), (320, 224)]

    def test_with_offset(self):
        prefix = b"\x00" * 12
        vert_data = struct.pack(">hhhhhhhh",
                                5, 10, 15, 20, 25, 30, 35, 40)
        data = prefix + vert_data
        verts = vdp.parse_vertices(data, 12)
        assert verts == [(5, 10), (15, 20), (25, 30), (35, 40)]


# ---------------------------------------------------------------------------
# Full command parsing
# ---------------------------------------------------------------------------

class TestParseCommand:
    def test_normal_sprite(self):
        entry = build_cmd(
            cmdctrl=0x0000,
            cmdcolr=0x0100,
            cmdsrca=0x0080,      # tex_addr = 0x80 * 8 = 0x400
            cmdsize=0x0210,      # 16x16
            verts=[(32, 64), (0, 0), (0, 0), (0, 0)],
        )
        cmd = vdp.parse_command(entry)
        assert cmd["end"] is False
        assert cmd["cmd_type"] == vdp.CMD_NORMAL_SPRITE
        assert cmd["cmd_name"] == "NormalSprite"
        assert cmd["link_mode"] == vdp.LINK_JUMP_NEXT
        assert cmd["color"] == 0x0100
        assert cmd["tex_addr"] == 0x0400
        assert cmd["width"] == 16
        assert cmd["height"] == 16
        assert cmd["vertices"][0] == (32, 64)

    def test_polygon(self):
        entry = build_cmd(
            cmdctrl=0x0004,
            cmdcolr=0x7C00,
            verts=[(0, 0), (100, 0), (100, 80), (0, 80)],
        )
        cmd = vdp.parse_command(entry)
        assert cmd["cmd_type"] == vdp.CMD_POLYGON
        assert cmd["color"] == 0x7C00
        assert cmd["vertices"] == [(0, 0), (100, 0), (100, 80), (0, 80)]

    def test_line(self):
        entry = build_cmd(
            cmdctrl=0x0006,
            cmdcolr=0x001F,
            verts=[(10, 10), (200, 150), (0, 0), (0, 0)],
        )
        cmd = vdp.parse_command(entry)
        assert cmd["cmd_type"] == vdp.CMD_LINE
        assert cmd["vertices"][0] == (10, 10)
        assert cmd["vertices"][1] == (200, 150)

    def test_local_coord(self):
        entry = build_cmd(
            cmdctrl=0x000A,
            verts=[(160, 112), (0, 0), (0, 0), (0, 0)],
        )
        cmd = vdp.parse_command(entry)
        assert cmd["cmd_type"] == vdp.CMD_LOCAL_COORD
        assert cmd["vertices"][0] == (160, 112)

    def test_end_flag(self):
        entry = build_cmd(cmdctrl=0x8000)
        cmd = vdp.parse_command(entry)
        assert cmd["end"] is True

    def test_gouraud(self):
        entry = build_cmd(cmdctrl=0x0004, gouraud=0x1234)
        cmd = vdp.parse_command(entry)
        assert cmd["gouraud"] == 0x1234

    def test_offset(self):
        padding = b"\xFF" * 16
        entry = build_cmd(cmdctrl=0x0004, cmdcolr=0xAAAA)
        cmd = vdp.parse_command(padding + entry, offset=16)
        assert cmd["cmd_type"] == vdp.CMD_POLYGON
        assert cmd["color"] == 0xAAAA


# ---------------------------------------------------------------------------
# Command table parsing
# ---------------------------------------------------------------------------

class TestParseCommandTable:
    def test_two_commands_then_end(self):
        c0 = build_cmd(cmdctrl=0x0000, cmdcolr=0x0001)
        c1 = build_cmd(cmdctrl=0x0004, cmdcolr=0x0002)
        c2 = build_cmd(cmdctrl=0x8000)  # end flag
        data = c0 + c1 + c2
        cmds = vdp.parse_command_table(data)
        assert len(cmds) == 3
        assert cmds[0]["cmd_type"] == vdp.CMD_NORMAL_SPRITE
        assert cmds[1]["cmd_type"] == vdp.CMD_POLYGON
        assert cmds[2]["end"] is True

    def test_stops_at_end(self):
        c0 = build_cmd(cmdctrl=0x8000)
        c1 = build_cmd(cmdctrl=0x0004)  # should not be parsed
        data = c0 + c1
        cmds = vdp.parse_command_table(data)
        assert len(cmds) == 1

    def test_empty_data(self):
        cmds = vdp.parse_command_table(b"")
        assert cmds == []

    def test_incomplete_entry(self):
        # only 16 bytes -- less than one full 32-byte entry
        cmds = vdp.parse_command_table(b"\x00" * 16)
        assert cmds == []


# ---------------------------------------------------------------------------
# Format helper
# ---------------------------------------------------------------------------

class TestFormat:
    def test_end_format(self):
        entry = build_cmd(cmdctrl=0x8000)
        cmd = vdp.parse_command(entry)
        assert vdp.format_command(cmd) == "END"

    def test_sprite_format(self):
        entry = build_cmd(
            cmdctrl=0x0000,
            cmdcolr=0x0100,
            cmdsrca=0x0080,
            cmdsize=0x0210,
            verts=[(32, 64), (0, 0), (0, 0), (0, 0)],
        )
        cmd = vdp.parse_command(entry)
        text = vdp.format_command(cmd)
        assert "NormalSprite" in text
        assert "32, 64" in text
        assert "0x0400" in text
