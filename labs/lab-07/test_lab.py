"""
Lab 7 Tests: M/X Flag Tracker for the 65816

Tests that the flag tracker correctly identifies register widths
as SEP and REP instructions modify the M and X flags.
"""

import unittest
from flag_tracker import (
    FlagValue,
    RegisterState,
    parse_instructions,
    track_flags_linear,
    apply_sep,
    apply_rep,
    merge_states,
    M_BIT,
    X_BIT,
)


class TestFlagValues(unittest.TestCase):
    """Test basic flag state properties."""

    def test_default_state_is_8bit(self):
        """Default state (emulation mode) should be 8-bit for both."""
        state = RegisterState()
        self.assertEqual(state.m_flag, FlagValue.SET)
        self.assertEqual(state.x_flag, FlagValue.SET)
        self.assertEqual(state.acc_width, "8-bit")
        self.assertEqual(state.index_width, "8-bit")

    def test_16bit_state(self):
        state = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        self.assertEqual(state.acc_width, "16-bit")
        self.assertEqual(state.index_width, "16-bit")

    def test_unknown_state(self):
        state = RegisterState(m_flag=FlagValue.UNKNOWN, x_flag=FlagValue.UNKNOWN)
        self.assertEqual(state.acc_width, "unknown")
        self.assertEqual(state.index_width, "unknown")

    def test_copy_is_independent(self):
        original = RegisterState()
        copy = original.copy()
        copy.m_flag = FlagValue.CLEAR
        self.assertEqual(original.m_flag, FlagValue.SET)


class TestSepRep(unittest.TestCase):
    """Test SEP and REP instruction effects."""

    def test_sep_sets_m_flag(self):
        state = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        result = apply_sep(state, M_BIT)
        self.assertEqual(result.m_flag, FlagValue.SET)
        self.assertEqual(result.x_flag, FlagValue.CLEAR)  # Unchanged

    def test_sep_sets_x_flag(self):
        state = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        result = apply_sep(state, X_BIT)
        self.assertEqual(result.m_flag, FlagValue.CLEAR)  # Unchanged
        self.assertEqual(result.x_flag, FlagValue.SET)

    def test_sep_sets_both(self):
        state = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        result = apply_sep(state, M_BIT | X_BIT)
        self.assertEqual(result.m_flag, FlagValue.SET)
        self.assertEqual(result.x_flag, FlagValue.SET)

    def test_rep_clears_m_flag(self):
        state = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.SET)
        result = apply_rep(state, M_BIT)
        self.assertEqual(result.m_flag, FlagValue.CLEAR)
        self.assertEqual(result.x_flag, FlagValue.SET)  # Unchanged

    def test_rep_clears_x_flag(self):
        state = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.SET)
        result = apply_rep(state, X_BIT)
        self.assertEqual(result.m_flag, FlagValue.SET)  # Unchanged
        self.assertEqual(result.x_flag, FlagValue.CLEAR)

    def test_rep_clears_both(self):
        state = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.SET)
        result = apply_rep(state, M_BIT | X_BIT)
        self.assertEqual(result.m_flag, FlagValue.CLEAR)
        self.assertEqual(result.x_flag, FlagValue.CLEAR)

    def test_sep_does_not_modify_original(self):
        state = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        apply_sep(state, M_BIT | X_BIT)
        self.assertEqual(state.m_flag, FlagValue.CLEAR)

    def test_sep_irrelevant_bits_ignored(self):
        """SEP with bits that are not M or X should not change flags."""
        state = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        result = apply_sep(state, 0x0F)  # Lower 4 bits only
        self.assertEqual(result.m_flag, FlagValue.CLEAR)
        self.assertEqual(result.x_flag, FlagValue.CLEAR)


class TestMergeStates(unittest.TestCase):
    """Test state merging at control flow join points."""

    def test_merge_identical_states(self):
        a = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.CLEAR)
        b = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.CLEAR)
        merged = merge_states(a, b)
        self.assertEqual(merged.m_flag, FlagValue.SET)
        self.assertEqual(merged.x_flag, FlagValue.CLEAR)

    def test_merge_divergent_m_flag(self):
        a = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.SET)
        b = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.SET)
        merged = merge_states(a, b)
        self.assertEqual(merged.m_flag, FlagValue.UNKNOWN)
        self.assertEqual(merged.x_flag, FlagValue.SET)

    def test_merge_divergent_both(self):
        a = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.SET)
        b = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        merged = merge_states(a, b)
        self.assertEqual(merged.m_flag, FlagValue.UNKNOWN)
        self.assertEqual(merged.x_flag, FlagValue.UNKNOWN)

    def test_merge_with_unknown_stays_unknown(self):
        a = RegisterState(m_flag=FlagValue.UNKNOWN, x_flag=FlagValue.SET)
        b = RegisterState(m_flag=FlagValue.SET, x_flag=FlagValue.SET)
        merged = merge_states(a, b)
        self.assertEqual(merged.m_flag, FlagValue.UNKNOWN)
        self.assertEqual(merged.x_flag, FlagValue.SET)


class TestLinearTracking(unittest.TestCase):
    """Test the linear flag tracker on instruction sequences."""

    def test_simple_sep_sequence(self):
        """SEP #$30 should put us in 8-bit mode for both."""
        text = """\
0000: SEP #$30
0002: LDA #$42
"""
        instructions = parse_instructions(text)
        results = track_flags_linear(instructions)

        # Before SEP: default 8-bit
        self.assertEqual(results[0][1].m_flag, FlagValue.SET)
        self.assertEqual(results[0][1].x_flag, FlagValue.SET)

        # After SEP, before LDA: still 8-bit (SEP #$30 sets M and X)
        self.assertEqual(results[1][1].m_flag, FlagValue.SET)
        self.assertEqual(results[1][1].x_flag, FlagValue.SET)

    def test_rep_switches_to_16bit(self):
        """REP #$20 should switch accumulator to 16-bit."""
        text = """\
0000: SEP #$30
0002: REP #$20
0004: LDA #$1234
"""
        instructions = parse_instructions(text)
        results = track_flags_linear(instructions)

        # After REP #$20 (before LDA): M cleared, X still set
        self.assertEqual(results[2][1].m_flag, FlagValue.CLEAR)
        self.assertEqual(results[2][1].x_flag, FlagValue.SET)
        self.assertEqual(results[2][1].acc_width, "16-bit")
        self.assertEqual(results[2][1].index_width, "8-bit")

    def test_full_flag_sequence(self):
        """Walk through a complete flag change sequence."""
        text = """\
0000: SEP #$30
0002: LDA #$42
0004: REP #$30
0006: LDA #$5678
0009: SEP #$10
000B: LDX #$99
"""
        instructions = parse_instructions(text)
        results = track_flags_linear(instructions)

        # Before instruction at 0004 (REP #$30): 8-bit everything
        self.assertEqual(results[2][1].m_flag, FlagValue.SET)
        self.assertEqual(results[2][1].x_flag, FlagValue.SET)

        # Before instruction at 0006 (after REP #$30): 16-bit everything
        self.assertEqual(results[3][1].m_flag, FlagValue.CLEAR)
        self.assertEqual(results[3][1].x_flag, FlagValue.CLEAR)

        # Before instruction at 000B (after SEP #$10): M=16-bit, X=8-bit
        self.assertEqual(results[5][1].m_flag, FlagValue.CLEAR)
        self.assertEqual(results[5][1].x_flag, FlagValue.SET)

    def test_starting_in_16bit_mode(self):
        """Can provide a custom initial state."""
        text = """\
0000: LDA #$1234
"""
        instructions = parse_instructions(text)
        initial = RegisterState(m_flag=FlagValue.CLEAR, x_flag=FlagValue.CLEAR)
        results = track_flags_linear(instructions, initial_state=initial)

        self.assertEqual(results[0][1].acc_width, "16-bit")
        self.assertEqual(results[0][1].index_width, "16-bit")

    def test_comments_and_blank_lines_skipped(self):
        text = """\
; This is a comment
0000: NOP

; Another comment
0002: NOP
"""
        instructions = parse_instructions(text)
        self.assertEqual(len(instructions), 2)

    def test_non_flag_instructions_preserve_state(self):
        """Instructions other than SEP/REP should not change flags."""
        text = """\
0000: REP #$30
0002: LDA #$1234
0005: STA $7E0000
0008: LDX #$ABCD
"""
        instructions = parse_instructions(text)
        results = track_flags_linear(instructions)

        # All instructions after REP #$30 should see 16-bit mode
        for i in range(1, len(results)):
            self.assertEqual(results[i][1].m_flag, FlagValue.CLEAR)
            self.assertEqual(results[i][1].x_flag, FlagValue.CLEAR)


if __name__ == "__main__":
    unittest.main()
