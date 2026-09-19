"""
Tests for Lab 64: Boundary Tripwires
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import tripwire


class TestCheckStack:
    def test_intact(self):
        assert tripwire.check_stack(0x1000, 0x1000) is None

    def test_moved(self):
        d = tripwire.check_stack(0x1000, 0x0FFC)
        assert d is not None
        assert "-4" in d or "4" in d

    def test_mentions_both_values(self):
        d = tripwire.check_stack(0x1000, 0x0FFC)
        assert "1000" in d.upper() or "0X1000" in d.upper()


class TestCalleeSaved:
    def test_preserved(self):
        before = {"rbx": 1, "rbp": 2, "rax": 9}
        after = {"rbx": 1, "rbp": 2, "rax": 77}
        assert tripwire.check_callee_saved(before, after, ["rbx", "rbp"]) is None

    def test_clobbered(self):
        before = {"rbx": 1, "rbp": 2}
        after = {"rbx": 99, "rbp": 2}
        d = tripwire.check_callee_saved(before, after, ["rbx", "rbp"])
        assert d is not None
        assert "rbx" in d
        assert "rbp" not in d

    def test_several_in_order(self):
        before = {"a": 1, "b": 2}
        after = {"a": 9, "b": 8}
        d = tripwire.check_callee_saved(before, after, ["b", "a"])
        assert d.index("b") < d.index("a")

    def test_missing_register_ignored(self):
        assert tripwire.check_callee_saved({"a": 1}, {"a": 1}, ["a", "zz"]) is None


class TestGuards:
    def test_intact(self):
        assert tripwire.check_guards({10: 0xCC, 11: 0xCC}, {10: 0xCC, 11: 0xCC}) is None

    def test_overwritten(self):
        d = tripwire.check_guards({10: 0x00}, {10: 0xCC})
        assert d is not None
        assert "10" in d

    def test_unmapped_counts_as_violation(self):
        assert tripwire.check_guards({}, {10: 0xCC}) is not None

    def test_sorted(self):
        d = tripwire.check_guards({5: 0, 20: 0}, {20: 0xCC, 5: 0xCC})
        assert d.index("5") < d.index("20")


class TestGuardedCall:
    def stack_check(self):
        return ("stack", lambda b, a: tripwire.check_stack(b["sp"], a["sp"]))

    def test_clean_call_returns_value(self):
        ctx = {"sp": 0x1000}
        result = tripwire.guarded_call(lambda c: "ok", ctx, [self.stack_check()])
        assert result == "ok"

    def test_detects_stack_damage(self):
        import pytest
        ctx = {"sp": 0x1000}

        def bad(c):
            c["sp"] -= 4
            return None
        with pytest.raises(tripwire.TripwireFailure) as e:
            tripwire.guarded_call(bad, ctx, [self.stack_check()])
        assert e.value.check == "stack"

    def test_names_the_call(self):
        import pytest
        ctx = {"sp": 0x1000}

        def bad(c):
            c["sp"] -= 4
        with pytest.raises(tripwire.TripwireFailure) as e:
            tripwire.guarded_call(bad, ctx, [self.stack_check()], call_name="sub_1234")
        assert "sub_1234" in str(e.value)

    def test_first_check_wins(self):
        import pytest
        ctx = {"sp": 0x1000}

        def bad(c):
            c["sp"] -= 4
        checks = [("first", lambda b, a: "boom"), self.stack_check()]
        with pytest.raises(tripwire.TripwireFailure) as e:
            tripwire.guarded_call(bad, ctx, checks)
        assert e.value.check == "first"

    def test_snapshot_is_a_copy(self):
        # If before and after alias the same dict, this check can never fail.
        import pytest
        ctx = {"regs": {"rbx": 1}}
        checks = [("abi", lambda b, a: tripwire.check_callee_saved(
            b["regs"], a["regs"], ["rbx"]))]

        def clobber(c):
            c["regs"]["rbx"] = 99
        with pytest.raises(tripwire.TripwireFailure):
            tripwire.guarded_call(clobber, ctx, checks)
