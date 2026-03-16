"""
Tests for Lab 31: Trace Comparator
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import trace_compare


# ---------------------------------------------------------------------------
# Test traces (as CSV strings)
# ---------------------------------------------------------------------------

TRACE_A = """\
address,a,b,c,flags
0x0100,0x00,0x00,0x00,0x00
0x0102,0x42,0x00,0x00,0x00
0x0104,0x42,0x10,0x00,0x00
0x0106,0x42,0x10,0x05,0x00
0x0108,0x42,0x10,0x05,0x80
"""

TRACE_B_MATCH = """\
address,a,b,c,flags
0x0100,0x00,0x00,0x00,0x00
0x0102,0x42,0x00,0x00,0x00
0x0104,0x42,0x10,0x00,0x00
0x0106,0x42,0x10,0x05,0x00
0x0108,0x42,0x10,0x05,0x80
"""

TRACE_B_DIVERGE = """\
address,a,b,c,flags
0x0100,0x00,0x00,0x00,0x00
0x0102,0x42,0x00,0x00,0x00
0x0104,0x42,0x10,0x00,0x00
0x0106,0x42,0x10,0x05,0x00
0x0108,0x43,0x10,0x05,0x00
"""

TRACE_SHORT = """\
address,a,b,c,flags
0x0100,0x00,0x00,0x00,0x00
0x0102,0x42,0x00,0x00,0x00
"""

TRACE_NO_PREFIX = """\
address,a,b,c,flags
0100,00,00,00,00
0102,42,00,00,00
"""


# ---------------------------------------------------------------------------
# load_trace_from_string
# ---------------------------------------------------------------------------

class TestLoadTrace:
    def test_returns_list(self):
        result = trace_compare.load_trace_from_string(TRACE_A)
        assert result is not None, "load_trace_from_string() returned None"
        assert isinstance(result, list)

    def test_correct_count(self):
        result = trace_compare.load_trace_from_string(TRACE_A)
        assert len(result) == 5

    def test_values_are_ints(self):
        result = trace_compare.load_trace_from_string(TRACE_A)
        assert isinstance(result[0]["address"], int)
        assert isinstance(result[0]["a"], int)

    def test_first_row_values(self):
        result = trace_compare.load_trace_from_string(TRACE_A)
        assert result[0]["address"] == 0x0100
        assert result[0]["a"] == 0x00

    def test_hex_values(self):
        result = trace_compare.load_trace_from_string(TRACE_A)
        assert result[1]["a"] == 0x42

    def test_no_prefix_hex(self):
        result = trace_compare.load_trace_from_string(TRACE_NO_PREFIX)
        assert result is not None
        assert result[0]["address"] == 0x0100
        assert result[1]["a"] == 0x42


# ---------------------------------------------------------------------------
# compare_traces
# ---------------------------------------------------------------------------

class TestCompareTraces:
    def test_matching_traces(self):
        a = trace_compare.load_trace_from_string(TRACE_A)
        b = trace_compare.load_trace_from_string(TRACE_B_MATCH)
        result = trace_compare.compare_traces(a, b)
        assert result is None, "Matching traces should return None"

    def test_divergent_traces(self):
        a = trace_compare.load_trace_from_string(TRACE_A)
        b = trace_compare.load_trace_from_string(TRACE_B_DIVERGE)
        result = trace_compare.compare_traces(a, b)
        assert result is not None, "Should detect divergence"
        assert result["step"] == 4  # 0-based index of last row

    def test_divergence_details(self):
        a = trace_compare.load_trace_from_string(TRACE_A)
        b = trace_compare.load_trace_from_string(TRACE_B_DIVERGE)
        result = trace_compare.compare_traces(a, b)
        assert "a" in result["differs"]
        assert "flags" in result["differs"]
        assert result["expected"]["a"] == 0x42
        assert result["got"]["a"] == 0x43

    def test_shorter_trace(self):
        a = trace_compare.load_trace_from_string(TRACE_A)
        b = trace_compare.load_trace_from_string(TRACE_SHORT)
        # Should only compare up to the shorter trace length
        result = trace_compare.compare_traces(a, b)
        assert result is None  # first 2 steps match


# ---------------------------------------------------------------------------
# format_divergence
# ---------------------------------------------------------------------------

class TestFormatDivergence:
    def test_matching_message(self):
        result = trace_compare.format_divergence(None)
        assert result is not None, "format_divergence() returned None"
        assert "match" in result.lower()

    def test_divergence_message(self):
        a = trace_compare.load_trace_from_string(TRACE_A)
        b = trace_compare.load_trace_from_string(TRACE_B_DIVERGE)
        div = trace_compare.compare_traces(a, b)
        msg = trace_compare.format_divergence(div)
        assert msg is not None
        assert "diverge" in msg.lower() or "differ" in msg.lower() \
            or "mismatch" in msg.lower() or "step" in msg.lower()
