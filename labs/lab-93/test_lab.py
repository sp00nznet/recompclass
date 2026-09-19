"""
Tests for Lab 93: Assemble the Address Space
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import addrspace


IMAGES = [("bootrom", 0x000000, 0x8000), ("cyos", 0x200000, 0x80000)]

TRANSFERS = [
    {"site": 0x200100, "target": 0x000400},   # cyos -> bootrom (memcpy)
    {"site": 0x200200, "target": 0x000500},   # cyos -> bootrom (memset)
    {"site": 0x200300, "target": 0x200800},   # cyos -> cyos
    {"site": 0x000100, "target": 0x000200},   # bootrom -> bootrom
    {"site": 0x200400, "target": 0x900000},   # genuinely outside
]


def space():
    s = addrspace.AddressSpace()
    for name, base, size in IMAGES:
        s.add(name, base, size)
    return s


class TestAddressSpace:
    def test_contains(self):
        s = space()
        assert s.contains(0x000400) is True
        assert s.contains(0x200800) is True

    def test_outside(self):
        assert space().contains(0x900000) is False

    def test_gap_between_images(self):
        assert space().contains(0x100000) is False

    def test_image_of(self):
        s = space()
        assert s.image_of(0x000400) == "bootrom"
        assert s.image_of(0x200800) == "cyos"

    def test_image_of_outside(self):
        assert space().image_of(0x900000) is None

    def test_overlap_rejected(self):
        import pytest
        s = space()
        with pytest.raises(addrspace.Overlap):
            s.add("dup", 0x000100, 0x100)


class TestAnalyse:
    def test_counts(self):
        r = addrspace.analyse(TRANSFERS, space())
        assert r is not None, "analyse() returned None"
        assert r["total"] == 5
        assert r["resolved"] == 4
        assert r["unresolved"] == 1

    def test_lists_outside(self):
        r = addrspace.analyse(TRANSFERS, space())
        assert r["outside"] == [0x900000]

    def test_empty(self):
        r = addrspace.analyse([], space())
        assert r["total"] == 0 and r["unresolved"] == 0


class TestCompareAssembly:
    def test_assembly_recovers_transfers(self):
        r = addrspace.compare_assembly(IMAGES, TRANSFERS)
        assert r is not None, "compare_assembly() returned None"
        assert r["separate"] > r["combined"]

    def test_the_cybiko_shape(self):
        # Two cross-image calls look unresolved until the images are glued.
        r = addrspace.compare_assembly(IMAGES, TRANSFERS)
        assert r["separate"] == 3
        assert r["combined"] == 1
        assert r["recovered"] == 2

    def test_ratio(self):
        r = addrspace.compare_assembly(IMAGES, TRANSFERS)
        assert abs(r["ratio"] - (1 / 3)) < 1e-9

    def test_no_transfers(self):
        r = addrspace.compare_assembly(IMAGES, [])
        assert r["ratio"] == 0.0
