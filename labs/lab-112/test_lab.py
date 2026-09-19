"""
Tests for Lab 112: Auto-Registration
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import autoreg


def f_original():
    return "original"


def f_mod():
    return "mod"


def f_other():
    return "other"


class TestRegistry:
    def test_first_registration(self):
        r = autoreg.Registry()
        first = r.register(0x80FF70, "smk_80FF70", f_original)
        assert first is False, "the first registration is not an override"
        assert r.lookup(0x80FF70) is f_original

    def test_override_reported(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "smk_80FF70", f_original)
        assert r.register(0x80FF70, "mod_80FF70", f_mod) is True

    def test_last_wins(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "smk_80FF70", f_original)
        r.register(0x80FF70, "mod_80FF70", f_mod)
        assert r.call(0x80FF70) == "mod"

    def test_name_tracked(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "smk_80FF70", f_original)
        assert r.name_at(0x80FF70) == "smk_80FF70"

    def test_unregistered(self):
        assert autoreg.Registry().lookup(0x1234) is None

    def test_call_unregistered_raises(self):
        import pytest
        with pytest.raises(KeyError):
            autoreg.Registry().call(0x1234)

    def test_independent_addresses(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        r.register(0x200, "b", f_other)
        assert r.call(0x100) == "original"
        assert r.call(0x200) == "other"


class TestOverrides:
    def test_none_initially(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        o = r.overrides()
        assert o is not None, "overrides() returned None"
        assert o == []

    def test_records_shadowed(self):
        r = autoreg.Registry()
        r.register(0x100, "original", f_original)
        r.register(0x100, "mod", f_mod)
        o = r.overrides()
        assert len(o) == 1
        assert o[0]["active"] == "mod"
        assert o[0]["shadowed"] == ["original"]

    def test_chain(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        r.register(0x100, "b", f_mod)
        r.register(0x100, "c", f_other)
        o = r.overrides()[0]
        assert o["active"] == "c"
        assert o["shadowed"] == ["a", "b"]

    def test_sorted(self):
        r = autoreg.Registry()
        for addr in (0x300, 0x100):
            r.register(addr, "a", f_original)
            r.register(addr, "b", f_mod)
        assert [o["addr"] for o in r.overrides()] == [0x100, 0x300]

    def test_note_is_actionable(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "original", f_original)
        r.register(0x80FF70, "mod", f_mod)
        note = autoreg.emit_link_order_note(r)
        assert "mod" in note and "original" in note

    def test_note_when_clean(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        assert "No overrides" in autoreg.emit_link_order_note(r)


class TestEmitRegistration:
    def test_has_constructor(self):
        src = autoreg.emit_registration("smk_80FF70", 0x80FF70)
        assert src is not None, "emit_registration() returned None"
        assert "constructor" in src

    def test_mentions_address_and_name(self):
        src = autoreg.emit_registration("smk_80FF70", 0x80FF70)
        assert "0x80FF70" in src
        assert "smk_80FF70" in src

    def test_no_central_list(self):
        src = autoreg.emit_registration("smk_80FF70", 0x80FF70)
        assert "table[" not in src
