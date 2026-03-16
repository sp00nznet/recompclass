"""
Tests for Lab 46: Capstone Multi-Arch Analyzer

The scoring and ranking tests work without Capstone installed.
Capstone-dependent tests are marked with pytest.mark.skipif.
"""

import pytest
import multi_arch_analyzer as maa


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

class TestComputeScore:
    def test_perfect_score(self):
        s = maa.compute_score(100, 100, 25)
        assert s["byte_ratio"] == 1.0
        assert s["num_instructions"] == 25
        assert s["decoded_bytes"] == 100

    def test_partial_score(self):
        s = maa.compute_score(50, 100, 10)
        assert s["byte_ratio"] == 0.5

    def test_zero_total(self):
        s = maa.compute_score(0, 0, 0)
        assert s["byte_ratio"] == 0.0

    def test_no_decoded(self):
        s = maa.compute_score(0, 100, 0)
        assert s["byte_ratio"] == 0.0
        assert s["num_instructions"] == 0


class TestComputeScoreFromMock:
    def test_mock_scoring(self):
        # 3 instructions of sizes 2, 3, 4 = 9 decoded out of 16
        s = maa.compute_score_from_mock([2, 3, 4], 16)
        assert s["decoded_bytes"] == 9
        assert s["num_instructions"] == 3
        assert abs(s["byte_ratio"] - 9.0 / 16.0) < 1e-6

    def test_empty(self):
        s = maa.compute_score_from_mock([], 10)
        assert s["byte_ratio"] == 0.0


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

class TestRankMockResults:
    def test_ranking_by_ratio(self):
        results = [
            ("arch_a", {"byte_ratio": 0.5, "num_instructions": 10, "decoded_bytes": 50}),
            ("arch_b", {"byte_ratio": 0.9, "num_instructions": 8,  "decoded_bytes": 90}),
            ("arch_c", {"byte_ratio": 0.3, "num_instructions": 5,  "decoded_bytes": 30}),
        ]
        ranked = maa.rank_mock_results(results)
        assert ranked[0]["name"] == "arch_b"
        assert ranked[1]["name"] == "arch_a"
        assert ranked[2]["name"] == "arch_c"

    def test_tiebreak_by_instructions(self):
        results = [
            ("arch_a", {"byte_ratio": 0.8, "num_instructions": 5,  "decoded_bytes": 80}),
            ("arch_b", {"byte_ratio": 0.8, "num_instructions": 10, "decoded_bytes": 80}),
        ]
        ranked = maa.rank_mock_results(results)
        # Same byte_ratio, more instructions wins
        assert ranked[0]["name"] == "arch_b"

    def test_empty_results(self):
        ranked = maa.rank_mock_results([])
        assert ranked == []


# ---------------------------------------------------------------------------
# Capstone integration (skipped if not installed)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not maa.HAS_CAPSTONE, reason="capstone not installed")
class TestCapstoneIntegration:
    def test_x86_nops(self):
        # 16 NOP instructions (0x90)
        blob = b"\x90" * 16
        result = maa.best_guess(blob)
        assert result is not None
        assert result["name"] == "x86_32" or result["name"] == "x86_64"
        assert result["byte_ratio"] == 1.0

    def test_arm32_blob(self):
        # ARM32 NOP: 0xE320F000 (mov r0, r0) -- big-endian encoding
        # In little-endian (as ARM is LE): 0x00, 0xF0, 0x20, 0xE3
        blob = b"\x00\xF0\x20\xE3" * 4
        result = maa.best_guess(blob)
        assert result is not None
        # Should decode well as ARM
        assert result["byte_ratio"] > 0.5

    def test_analyze_returns_all_candidates(self):
        blob = b"\x90" * 16
        results = maa.analyze(blob)
        assert len(results) == len(maa.CANDIDATES)
        # Results should be sorted by byte_ratio descending
        for i in range(len(results) - 1):
            assert results[i]["byte_ratio"] >= results[i + 1]["byte_ratio"]

    def test_try_disassemble(self):
        from capstone import CS_ARCH_X86, CS_MODE_32
        blob = b"\x90\x90\x90\x90"  # 4 NOPs
        score = maa.try_disassemble(blob, CS_ARCH_X86, CS_MODE_32)
        assert score["byte_ratio"] == 1.0
        assert score["num_instructions"] == 4
