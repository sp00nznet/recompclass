"""
Tests for Lab 75: Lane Order and Permutes
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import lanes


class TestMirrorIndex:
    def test_ends_swap(self):
        assert lanes.mirror_index(0, 4) == 3
        assert lanes.mirror_index(3, 4) == 0

    def test_middle(self):
        assert lanes.mirror_index(1, 4) == 2

    def test_self_inverse(self):
        for i in range(4):
            assert lanes.mirror_index(lanes.mirror_index(i, 4), 4) == i

    def test_out_of_range(self):
        import pytest
        with pytest.raises(ValueError):
            lanes.mirror_index(4, 4)


class TestPermute:
    def test_identity(self):
        assert lanes.permute(["a", "b", "c", "d"], [0, 1, 2, 3]) == ["a", "b", "c", "d"]

    def test_reverse(self):
        assert lanes.permute(["a", "b", "c", "d"], [3, 2, 1, 0]) == ["d", "c", "b", "a"]

    def test_broadcast(self):
        assert lanes.permute(["a", "b"], [0, 0]) == ["a", "a"]

    def test_out_of_range(self):
        import pytest
        with pytest.raises(IndexError):
            lanes.permute(["a"], [5])


class TestLift:
    def test_naive_is_unchanged(self):
        c = [0, 1, 2, 3]
        assert lanes.lift_permute_naive(c) == c

    def test_naive_returns_a_copy(self):
        c = [0, 1, 2, 3]
        out = lanes.lift_permute_naive(c)
        out[0] = 9
        assert c[0] == 0

    def test_identity_survives(self):
        # An identity permute is identity in either lane order.
        assert lanes.lift_permute([0, 1, 2, 3], 4) == [0, 1, 2, 3]

    def test_reverse_survives(self):
        assert lanes.lift_permute([3, 2, 1, 0], 4) == [3, 2, 1, 0]

    def test_asymmetric_control_changes(self):
        # Broadcasting guest lane 0 is broadcasting host lane 3.
        assert lanes.lift_permute([0, 0, 0, 0], 4) == [3, 3, 3, 3]


class TestDemonstrateBug:
    def test_produces_a_difference(self):
        d = lanes.demonstrate_bug(["a", "b", "c", "d"], [0, 0, 0, 0])
        assert d is not None, "demonstrate_bug() returned None"
        assert d["differ"] is True
        assert d["naive"] != d["correct"]

    def test_symmetric_control_agrees(self):
        d = lanes.demonstrate_bug(["a", "b", "c", "d"], [3, 2, 1, 0])
        assert d["differ"] is False

    def test_correct_matches_guest_semantics(self):
        # Guest broadcasts its lane 0, which is "a" in guest order. In host
        # order that same element sits at index 3.
        d = lanes.demonstrate_bug(["d", "c", "b", "a"], [0, 0, 0, 0])
        assert d["correct"] == ["a", "a", "a", "a"]
