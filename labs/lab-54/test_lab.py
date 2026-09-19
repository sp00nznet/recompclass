"""
Tests for Lab 54: Fallthrough Detector
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import fallthrough


def fn(addr, mnemonics, size=None):
    instructions = []
    a = addr
    for m in mnemonics:
        instructions.append({"addr": a, "size": 4, "mnemonic": m})
        a += 4
    return {"addr": addr, "size": size if size is not None else a - addr,
            "instructions": instructions}


class TestEndsWithTerminator:
    def test_ret_terminates(self):
        assert ends(fn(0, ["add", "ret"])) is True

    def test_unconditional_branch_terminates(self):
        assert ends(fn(0, ["add", "jmp"])) is True

    def test_arithmetic_does_not(self):
        assert ends(fn(0, ["add", "sub"])) is False

    def test_conditional_branch_does_not(self):
        assert ends(fn(0, ["cmp", "beq"])) is False

    def test_empty_function(self):
        assert ends({"addr": 0, "size": 0, "instructions": []}) is False


def ends(f):
    r = fallthrough.ends_with_terminator(f)
    assert r is not None, "ends_with_terminator() returned None"
    return r


class TestFindFallthroughs:
    def test_finds_the_bad_one(self):
        funcs = [fn(0x100, ["add", "ret"]), fn(0x200, ["add", "sub"])]
        bad = fallthrough.find_fallthroughs(funcs)
        assert bad is not None, "find_fallthroughs() returned None"
        assert len(bad) == 1
        assert bad[0]["addr"] == 0x200

    def test_none_when_all_clean(self):
        funcs = [fn(0x100, ["ret"]), fn(0x200, ["jmp"])]
        assert fallthrough.find_fallthroughs(funcs) == []

    def test_preserves_order(self):
        funcs = [fn(0x300, ["add"]), fn(0x100, ["add"])]
        bad = fallthrough.find_fallthroughs(funcs)
        assert [f["addr"] for f in bad] == [0x300, 0x100]


class TestProposeMerges:
    def test_adjacent_split(self):
        # 0x100 is 8 bytes and falls through into 0x108.
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["add", "ret"])]
        merges = fallthrough.propose_merges(funcs)
        assert merges is not None, "propose_merges() returned None"
        assert merges == [(0x100, 0x108)]

    def test_no_merge_when_terminated(self):
        funcs = [fn(0x100, ["add", "ret"]), fn(0x108, ["add", "ret"])]
        assert fallthrough.propose_merges(funcs) == []

    def test_no_merge_into_gap(self):
        # Falls through, but nothing starts at 0x108.
        funcs = [fn(0x100, ["add", "sub"]), fn(0x200, ["ret"])]
        assert fallthrough.propose_merges(funcs) == []

    def test_sorted(self):
        funcs = [fn(0x300, ["add", "sub"]), fn(0x308, ["ret"]),
                 fn(0x100, ["add", "sub"]), fn(0x108, ["ret"])]
        merges = fallthrough.propose_merges(funcs)
        assert merges == [(0x100, 0x108), (0x300, 0x308)]


class TestApplyMerges:
    def test_merges_two(self):
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["add", "ret"])]
        merged = fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert merged is not None, "apply_merges() returned None"
        assert len(merged) == 1
        assert merged[0]["addr"] == 0x100
        assert merged[0]["size"] == 16
        assert len(merged[0]["instructions"]) == 4

    def test_merged_function_now_terminates(self):
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["add", "ret"])]
        merged = fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert fallthrough.ends_with_terminator(merged[0]) is True

    def test_chain_of_three(self):
        funcs = [fn(0x100, ["add"]), fn(0x104, ["sub"]), fn(0x108, ["ret"])]
        merged = fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert len(merged) == 1
        assert merged[0]["size"] == 12
        assert len(merged[0]["instructions"]) == 3

    def test_leaves_clean_functions_alone(self):
        funcs = [fn(0x100, ["ret"]), fn(0x200, ["ret"])]
        merged = fallthrough.apply_merges(funcs, [])
        assert len(merged) == 2

    def test_does_not_mutate_input(self):
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["ret"])]
        before = len(funcs)
        fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert len(funcs) == before

    def test_result_is_sorted(self):
        funcs = [fn(0x300, ["ret"]), fn(0x100, ["ret"])]
        merged = fallthrough.apply_merges(funcs, [])
        assert [f["addr"] for f in merged] == [0x100, 0x300]
