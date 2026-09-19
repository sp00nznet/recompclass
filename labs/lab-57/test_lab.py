"""
Tests for Lab 57: Manifest-Driven Pipeline
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import manifest


SAMPLE = """
# worms bring-up
[project]
name = worms
base = 0x82000000

[input]
image = worms.xex

[entrypoint.functions]
0x82236F38 = tail-call discovery missed
0x82E80100 = runtime-harvested (tolerant dispatch boot)
0x82E80104 = runtime-harvested (tolerant dispatch boot)

[imports]
XUsbcamGetState = purge:8
XamLoaderLaunch = purge:4, mode:stub
"""


def m():
    parsed = manifest.parse_manifest(SAMPLE)
    assert parsed is not None, "parse_manifest() returned None"
    return parsed


class TestParse:
    def test_sections(self):
        assert set(m()) >= {"project", "input", "entrypoint.functions", "imports"}

    def test_values(self):
        assert m()["project"]["name"] == "worms"
        assert m()["project"]["base"] == "0x82000000"

    def test_subsection_key(self):
        assert "entrypoint.functions" in m()

    def test_skips_comments(self):
        assert all(not k.startswith("#") for k in m()["project"])

    def test_key_outside_section_is_error(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.parse_manifest("name = orphan")

    def test_malformed_line_is_error(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.parse_manifest("[project]\nthis line has no equals sign")


class TestValidate:
    def test_accepts_good(self):
        assert manifest.validate(m()) is True

    def test_rejects_derived_state(self):
        import pytest
        bad = manifest.parse_manifest("[project]\nname = x\n[discovered]\na = 1")
        with pytest.raises(manifest.ManifestError) as e:
            manifest.validate(bad)
        assert "discovered" in str(e.value)

    def test_rejects_unknown_section(self):
        import pytest
        bad = manifest.parse_manifest("[project]\nname = x\n[wibble]\na = 1")
        with pytest.raises(manifest.ManifestError):
            manifest.validate(bad)

    def test_requires_project(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.validate(manifest.parse_manifest("[input]\nimage = a.xex"))

    def test_requires_project_name(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.validate(manifest.parse_manifest("[project]\nbase = 0x1"))


class TestHints:
    def test_count(self):
        h = manifest.hints(m())
        assert h is not None, "hints() returned None"
        assert len(h) == 3

    def test_addresses_are_ints(self):
        assert manifest.hints(m())[0]["addr"] == 0x82236F38

    def test_sorted(self):
        addrs = [x["addr"] for x in manifest.hints(m())]
        assert addrs == sorted(addrs)

    def test_source_recorded(self):
        sources = [x["source"] for x in manifest.hints(m())]
        assert any("runtime-harvested" in s for s in sources)

    def test_absent_section(self):
        assert manifest.hints(manifest.parse_manifest("[project]\nname = x")) == []

    def test_empty_note_rejected(self):
        import pytest
        bad = manifest.parse_manifest(
            "[project]\nname = x\n[entrypoint.functions]\n0x1000 = ")
        with pytest.raises(manifest.ManifestError):
            manifest.hints(bad)


class TestOverrides:
    def test_single_field(self):
        o = manifest.resolve_overrides(m())
        assert o is not None, "resolve_overrides() returned None"
        assert o["XUsbcamGetState"]["purge"] == 8

    def test_multiple_fields(self):
        o = manifest.resolve_overrides(m())
        assert o["XamLoaderLaunch"]["purge"] == 4
        assert o["XamLoaderLaunch"]["mode"] == "stub"

    def test_absent_section(self):
        assert manifest.resolve_overrides(
            manifest.parse_manifest("[project]\nname = x")) == {}

    def test_bad_pair(self):
        import pytest
        bad = manifest.parse_manifest("[project]\nname = x\n[imports]\nA = nocolon")
        with pytest.raises(manifest.ManifestError):
            manifest.resolve_overrides(bad)

    def test_bad_purge(self):
        import pytest
        bad = manifest.parse_manifest("[project]\nname = x\n[imports]\nA = purge:many")
        with pytest.raises(manifest.ManifestError):
            manifest.resolve_overrides(bad)


class TestDerivedPath:
    def test_outside_the_manifest(self):
        p = manifest.derived_path(m(), "out")
        assert p is not None, "derived_path() returned None"
        assert "worms" in p
        assert p.endswith(".derived.json")
        assert "manifest" not in p
