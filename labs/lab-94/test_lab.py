"""
Tests for Lab 94: Classify the Unknowns
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import classify


def i(op, dst=None, mode=None, reg=None):
    d = {"op": op, "dst": dst, "mode": mode}
    if reg is not None:
        d["reg"] = reg
    return d


VTABLE_BLOCK = [
    i("mov.l", dst="er0", mode="displacement"),
    i("add", dst="er1"),
    i("jsr", reg="er0"),
]

TABLE_BLOCK = [
    i("mov.l", dst="er2", mode="absolute16"),
    i("jsr", reg="er2"),
]

POINTER_BLOCK = [
    i("mov.l", dst="er3", mode="indirect"),
    i("jsr", reg="er3"),
]

NO_DEF_BLOCK = [
    i("nop"),
    i("jsr", reg="er5"),
]


class TestFindDefinition:
    def test_finds_it(self):
        d = classify.find_definition(VTABLE_BLOCK, 2, "er0")
        assert d is not None
        assert d["mode"] == "displacement"

    def test_takes_the_last_write(self):
        block = [i("mov.l", dst="er0", mode="indirect"),
                 i("mov.l", dst="er0", mode="displacement"),
                 i("jsr", reg="er0")]
        assert classify.find_definition(block, 2, "er0")["mode"] == "displacement"

    def test_ignores_other_registers(self):
        assert classify.find_definition(VTABLE_BLOCK, 2, "er9") is None

    def test_does_not_look_forward(self):
        block = [i("jsr", reg="er0"), i("mov.l", dst="er0", mode="indirect")]
        assert classify.find_definition(block, 0, "er0") is None


class TestClassifySite:
    def test_vtable(self):
        assert classify.classify_site(VTABLE_BLOCK, 2) == "displacement"

    def test_table(self):
        assert classify.classify_site(TABLE_BLOCK, 1) == "absolute16"

    def test_pointer(self):
        assert classify.classify_site(POINTER_BLOCK, 1) == "indirect"

    def test_unknown(self):
        assert classify.classify_site(NO_DEF_BLOCK, 1) == classify.UNKNOWN


class TestClassifyAll:
    def sites(self):
        return ([(VTABLE_BLOCK, 2)] * 178 + [(TABLE_BLOCK, 1)] * 43 +
                [(POINTER_BLOCK, 1)] * 3 + [(NO_DEF_BLOCK, 1)] * 2)

    def test_the_cybiko_numbers(self):
        g = classify.classify_all(self.sites())
        assert g is not None, "classify_all() returned None"
        assert g["displacement"] == 178
        assert g["absolute16"] == 43
        assert g["indirect"] == 3
        assert g[classify.UNKNOWN] == 2

    def test_total(self):
        g = classify.classify_all(self.sites())
        assert sum(g.values()) == 226

    def test_summary_names_the_real_size(self):
        g = classify.classify_all(self.sites())
        line = classify.summary_line(g)
        assert "226" in line and "4 different" in line


class TestReport:
    def test_sorted(self):
        g = {"indirect": 3, "displacement": 178, "absolute16": 43}
        r = classify.report(g)
        assert r is not None, "report() returned None"
        assert [x["mechanism"] for x in r] == ["displacement", "absolute16", "indirect"]

    def test_attaches_meaning(self):
        r = classify.report({"displacement": 1})
        assert "virtual dispatch" in r[0]["means"]

    def test_unknown_mechanism_passes_through(self):
        r = classify.report({classify.UNKNOWN: 2})
        assert r[0]["means"] == classify.UNKNOWN
