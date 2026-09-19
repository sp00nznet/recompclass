"""
Tests for Lab 83: Input Verification
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import verify


REV_A = b"the rev A image"
REV_B = b"the rev B image"
JUNK = b"not a game at all"


def known():
    return {
        verify.hash_data(REV_A): "Rev A (US)",
        verify.hash_data(REV_B): "Rev B (EU)",
    }


class TestHash:
    def test_hex(self):
        h = verify.hash_data(b"x")
        assert h is not None, "hash_data() returned None"
        assert len(h) == 64
        int(h, 16)

    def test_stable(self):
        assert verify.hash_data(b"x") == verify.hash_data(b"x")


class TestIdentify:
    def test_known(self):
        assert verify.identify(REV_A, known()) == "Rev A (US)"

    def test_other(self):
        assert verify.identify(REV_B, known()) == "Rev B (EU)"

    def test_unknown(self):
        assert verify.identify(JUNK, known()) is None


class TestCheck:
    def test_match(self):
        r = verify.check(REV_A, known(), "Rev A (US)")
        assert r is not None, "check() returned None"
        assert r["verdict"] == "match"
        assert r["found"] == "Rev A (US)"

    def test_known_mismatch(self):
        r = verify.check(REV_B, known(), "Rev A (US)")
        assert r["verdict"] == "known_mismatch"
        assert "Rev B (EU)" in r["message"]
        assert "Rev A (US)" in r["message"]

    def test_mismatch_explains_the_consequence(self):
        r = verify.check(REV_B, known(), "Rev A (US)")
        assert "hint" in r["message"].lower() or "address" in r["message"].lower()

    def test_unknown(self):
        r = verify.check(JUNK, known(), "Rev A (US)")
        assert r["verdict"] == "unknown"

    def test_every_message_carries_the_digest(self):
        for data in (REV_A, REV_B, JUNK):
            r = verify.check(data, known(), "Rev A (US)")
            assert r["digest"][:16] in r["message"]

    def test_never_refuses(self):
        # All three verdicts are advisory. None of them is a refusal.
        for data in (REV_A, REV_B, JUNK):
            r = verify.check(data, known(), "Rev A (US)")
            assert r["verdict"] in ("match", "known_mismatch", "unknown")


class TestProvenance:
    def test_fields(self):
        p = verify.provenance(REV_A, known(), "Rev A (US)",
                              {"lifter": "1.2", "runtime": "0.9"})
        assert p is not None, "provenance() returned None"
        assert p["identified"] == "Rev A (US)"
        assert p["verdict"] == "match"

    def test_tools_sorted(self):
        p = verify.provenance(REV_A, known(), "Rev A (US)",
                              {"zzz": "1", "aaa": "2"})
        assert p["tools"] == ["aaa=2", "zzz=1"]

    def test_format(self):
        p = verify.provenance(REV_A, known(), "Rev A (US)", {"lifter": "1.2"})
        text = verify.format_provenance(p)
        assert "Rev A (US)" in text and "lifter=1.2" in text
