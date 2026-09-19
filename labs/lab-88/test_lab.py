"""
Tests for Lab 88: Fold a Paging Instruction
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import paging


def insn(addr, op, page=None, offset=None):
    return {"addr": addr, "op": op, "page": page, "offset": offset}


GOOD = [
    insn(0x0000, "NOP"),
    insn(0x0001, "PSET", page=0x03),
    insn(0x0002, "CALL", offset=0x07),
    insn(0x0003, "PSET", page=0x07),
    insn(0x0004, "JP", offset=0xE8),
    insn(0x0307, "NOP"),
]

BAD = [
    insn(0x0000, "PSET", page=0x03),
    insn(0x0001, "NOP"),                 # not a transfer -- invariant broken
    insn(0x0002, "JP", offset=0x10),
]


class TestResolveTargets:
    def test_call_target(self):
        out = paging.resolve_targets(GOOD)
        assert out is not None, "resolve_targets() returned None"
        assert out[2]["target"] == 0x0307

    def test_jp_target(self):
        out = paging.resolve_targets(GOOD)
        assert out[4]["target"] == 0x07E8

    def test_non_transfer_is_none(self):
        out = paging.resolve_targets(GOOD)
        assert out[0]["target"] is None

    def test_page_persists(self):
        prog = [insn(0, "PSET", page=0x02), insn(1, "JP", offset=0x10),
                insn(2, "JP", offset=0x20)]
        out = paging.resolve_targets(prog)
        assert out[2]["target"] == 0x0220

    def test_transfer_without_page(self):
        import pytest
        with pytest.raises(paging.PagingError):
            paging.resolve_targets([insn(0, "JP", offset=0x10)])

    def test_does_not_mutate(self):
        paging.resolve_targets(GOOD)
        assert "target" not in GOOD[0]


class TestInvariant:
    def test_holds(self):
        v = paging.check_pset_invariant(GOOD)
        assert v is not None, "check_pset_invariant() returned None"
        assert v == []

    def test_detects_violation(self):
        assert paging.check_pset_invariant(BAD) == [0x0000]

    def test_trailing_pset_is_a_violation(self):
        prog = [insn(0, "NOP"), insn(1, "PSET", page=1)]
        assert paging.check_pset_invariant(prog) == [1]


class TestEmit:
    def test_pset_emits_no_code(self):
        lines = paging.emit(GOOD)
        assert lines is not None, "emit() returned None"
        joined = "\n".join(lines)
        # The PSET at 0x0001 gets a label and a comment, and nothing else.
        after = joined.split("L_0001:")[1].split("L_0002:")[0]
        assert "goto" not in after

    def test_transfer_uses_resolved_label(self):
        joined = "\n".join(paging.emit(GOOD))
        assert "goto L_0307;" in joined

    def test_every_instruction_labelled(self):
        joined = "\n".join(paging.emit(GOOD))
        for i in GOOD:
            assert f"L_{i['addr']:04X}:" in joined

    def test_refuses_when_invariant_broken(self):
        import pytest
        with pytest.raises(paging.PagingError):
            paging.emit(BAD)


class TestReport:
    def test_counts(self):
        r = paging.folding_report(GOOD)
        assert r["psets"] == 2
        assert r["folded"] == 2
        assert r["transfers"] == 2
