"""
Tests for Lab 92: Encoding Traps
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import encoding


# push-handlers escape: 07 00 07 -> opcode 0, a == 7, operand 0x0007
ESCAPED = bytes([0x07, 0x00, 0x07])
# opcode 0, a = 0 -> "pop"
SIMPLE_POP = bytes([0x00])
# opcode 3 (push), a = 2 -> b = 2
PUSH2 = bytes([(3 << 3) | 2])


class TestDecodeOne:
    def test_simple(self):
        i = encoding.decode_one(SIMPLE_POP, 0)
        assert i is not None, "decode_one() returned None"
        assert i["name"] == "pop"
        assert i["length"] == 1

    def test_operand_in_low_bits(self):
        i = encoding.decode_one(PUSH2, 0)
        assert i["name"] == "push"
        assert i["b"] == 2

    def test_escape_is_three_bytes(self):
        i = encoding.decode_one(ESCAPED, 0)
        assert i["length"] == 3
        assert i["b"] == 7
        assert i["name"] == "pop-handlers"

    def test_truncated_escape(self):
        import pytest
        with pytest.raises(encoding.DecodeError):
            encoding.decode_one(bytes([0x07, 0x00]), 0)

    def test_unknown_opcode(self):
        import pytest
        with pytest.raises(encoding.DecodeError):
            encoding.decode_one(bytes([(30 << 3) | 0]), 0)


class TestDecodeAll:
    def test_sequence(self):
        out = encoding.decode_all(SIMPLE_POP + PUSH2)
        assert out is not None, "decode_all() returned None"
        assert [i["name"] for i in out] == ["pop", "push"]

    def test_escape_consumes_three(self):
        out = encoding.decode_all(ESCAPED + SIMPLE_POP)
        assert len(out) == 2
        assert out[1]["name"] == "pop"


class TestNaive:
    def test_misreads_the_escape(self):
        naive = encoding.decode_naive(ESCAPED)
        assert naive is not None, "decode_naive() returned None"
        # Three "instructions" instead of one -- and none of them crash.
        assert len(naive) == 3

    def test_agrees_without_escapes(self):
        data = SIMPLE_POP + PUSH2
        assert [i["name"] for i in encoding.decode_naive(data)] == \
               [i["name"] for i in encoding.decode_all(data)]

    def test_does_not_raise_on_unknown(self):
        out = encoding.decode_naive(bytes([(30 << 3) | 0]))
        assert out[0]["name"] == "?"


class TestCorpusCheck:
    def corpus(self):
        return {
            "clean_a": SIMPLE_POP + PUSH2,
            "clean_b": PUSH2 * 4,
            "has_try": SIMPLE_POP + ESCAPED + PUSH2,
            "also_try": ESCAPED + ESCAPED,
        }

    def test_counts(self):
        r = encoding.corpus_check(self.corpus())
        assert r is not None, "corpus_check() returned None"
        assert r["total"] == 4
        assert r["disagree"] == 2

    def test_names_affected(self):
        r = encoding.corpus_check(self.corpus())
        assert r["affected"] == ["also_try", "has_try"]

    def test_counts_escapes(self):
        r = encoding.corpus_check(self.corpus())
        assert r["escapes"] == 3

    def test_errors_separate(self):
        c = self.corpus()
        c["broken"] = bytes([0x07, 0x00])       # truncated escape
        r = encoding.corpus_check(c)
        assert r["errors"] == ["broken"]
        assert "broken" not in r["affected"]
