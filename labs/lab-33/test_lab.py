"""
Tests for Lab 33: N64 Display List Parser
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import dlist_parser


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

def make_vtx_cmd(count, addr):
    """Build a G_VTX command."""
    cmd = bytearray(8)
    cmd[0] = 0x04
    cmd[1] = (count << 4) & 0xF0
    struct.pack_into(">I", cmd, 4, addr)
    return bytes(cmd)


def make_tri1_cmd(v0, v1, v2):
    """Build a G_TRI1 command."""
    cmd = bytearray(8)
    cmd[0] = 0x06
    cmd[5] = v0 * 2
    cmd[6] = v1 * 2
    cmd[7] = v2 * 2
    return bytes(cmd)


def make_enddl_cmd():
    """Build a G_ENDDL command."""
    cmd = bytearray(8)
    cmd[0] = 0xB8
    return bytes(cmd)


def make_settimg_cmd(addr):
    """Build a G_SETTIMG command."""
    cmd = bytearray(8)
    cmd[0] = 0xFD
    struct.pack_into(">I", cmd, 4, addr)
    return bytes(cmd)


SIMPLE_DLIST = (
    make_vtx_cmd(4, 0x06000000) +
    make_tri1_cmd(0, 1, 2) +
    make_tri1_cmd(0, 2, 3) +
    make_enddl_cmd()
)


# ---------------------------------------------------------------------------
# parse_command
# ---------------------------------------------------------------------------

class TestParseCommand:
    def test_returns_dict(self):
        result = dlist_parser.parse_command(SIMPLE_DLIST, 0)
        assert result is not None, "parse_command() returned None"
        assert isinstance(result, dict)

    def test_vtx_command(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 0)
        assert cmd["cmd_id"] == 0x04
        assert cmd["cmd_name"] == "G_VTX"
        assert cmd["params"]["count"] == 4
        assert cmd["params"]["addr"] == 0x06000000

    def test_tri1_command(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 8)
        assert cmd["cmd_id"] == 0x06
        assert cmd["cmd_name"] == "G_TRI1"
        assert cmd["params"]["v0"] == 0
        assert cmd["params"]["v1"] == 1
        assert cmd["params"]["v2"] == 2

    def test_tri1_second(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 16)
        assert cmd["params"]["v0"] == 0
        assert cmd["params"]["v1"] == 2
        assert cmd["params"]["v2"] == 3

    def test_enddl_command(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 24)
        assert cmd["cmd_name"] == "G_ENDDL"

    def test_settimg(self):
        data = make_settimg_cmd(0x80100000)
        cmd = dlist_parser.parse_command(data, 0)
        assert cmd["cmd_name"] == "G_SETTIMG"
        assert cmd["params"]["addr"] == 0x80100000

    def test_too_short(self):
        result = dlist_parser.parse_command(bytes(4), 0)
        assert result is None

    def test_raw_bytes(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 0)
        assert len(cmd["raw"]) == 8

    def test_unknown_command(self):
        data = bytearray(8)
        data[0] = 0xFF  # not in table
        cmd = dlist_parser.parse_command(bytes(data), 0)
        assert cmd is not None
        assert "UNKNOWN" in cmd["cmd_name"].upper()


# ---------------------------------------------------------------------------
# parse_display_list
# ---------------------------------------------------------------------------

class TestParseDisplayList:
    def test_returns_list(self):
        result = dlist_parser.parse_display_list(SIMPLE_DLIST)
        assert result is not None, "parse_display_list() returned None"
        assert isinstance(result, list)

    def test_correct_count(self):
        result = dlist_parser.parse_display_list(SIMPLE_DLIST)
        assert len(result) == 4  # VTX, TRI1, TRI1, ENDDL

    def test_stops_at_enddl(self):
        # Add extra bytes after ENDDL -- should not be parsed
        extended = SIMPLE_DLIST + make_vtx_cmd(8, 0x07000000)
        result = dlist_parser.parse_display_list(extended)
        assert len(result) == 4

    def test_empty_data(self):
        result = dlist_parser.parse_display_list(b"")
        assert result is not None
        assert len(result) == 0


# ---------------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------------

class TestSummarize:
    def test_returns_dict(self):
        commands = dlist_parser.parse_display_list(SIMPLE_DLIST)
        result = dlist_parser.summarize(commands)
        assert result is not None, "summarize() returned None"
        assert isinstance(result, dict)

    def test_counts(self):
        commands = dlist_parser.parse_display_list(SIMPLE_DLIST)
        result = dlist_parser.summarize(commands)
        assert result["G_VTX"] == 1
        assert result["G_TRI1"] == 2
        assert result["G_ENDDL"] == 1


# ---------------------------------------------------------------------------
# format_command
# ---------------------------------------------------------------------------

class TestFormatCommand:
    def test_returns_string(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 0)
        result = dlist_parser.format_command(cmd)
        assert result is not None, "format_command() returned None"
        assert isinstance(result, str)

    def test_contains_cmd_name(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 0)
        result = dlist_parser.format_command(cmd)
        assert "G_VTX" in result

    def test_contains_offset(self):
        cmd = dlist_parser.parse_command(SIMPLE_DLIST, 8)
        result = dlist_parser.format_command(cmd)
        assert "0008" in result
