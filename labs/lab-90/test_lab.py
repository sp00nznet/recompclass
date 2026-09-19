"""
Tests for Lab 90: Is It Bytecode?
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import bytecheck


EMPIRE = {"name": "EMPIRE.EXE", "imports": ["VBRUN300"],
          "relocations": 14, "code_bytes": 114025}

TIM = {"name": "TIM.EXE", "imports": ["KERNEL", "USER", "GDI"],
       "relocations": 4743, "code_bytes": 197000}

NO_IMPORTS = {"name": "ROM.BIN", "imports": [], "relocations": 0, "code_bytes": 32768}


class TestDensity:
    def test_native(self):
        d = bytecheck.relocation_density(TIM)
        assert d is not None, "relocation_density() returned None"
        assert d > 20

    def test_bytecode(self):
        assert bytecheck.relocation_density(EMPIRE) < 1.0

    def test_zero_code(self):
        assert bytecheck.relocation_density(
            {"relocations": 5, "code_bytes": 0}) == 0.0


class TestRuntimeOnly:
    def test_vbrun(self):
        assert bytecheck.is_runtime_only(EMPIRE) is True

    def test_native_imports(self):
        assert bytecheck.is_runtime_only(TIM) is False

    def test_no_imports_is_not_runtime_only(self):
        assert bytecheck.is_runtime_only(NO_IMPORTS) is False

    def test_case_and_extension_insensitive(self):
        assert bytecheck.is_runtime_only(
            {"imports": ["kernel.dll", "user.dll"]}) is False


class TestClassify:
    def test_empire_is_bytecode(self):
        r = bytecheck.classify(EMPIRE, reference=TIM)
        assert r is not None, "classify() returned None"
        assert r["verdict"] == "bytecode"

    def test_tim_is_native(self):
        assert bytecheck.classify(TIM, reference=TIM)["verdict"] == "native"

    def test_gives_reasons(self):
        r = bytecheck.classify(EMPIRE, reference=TIM)
        assert len(r["reasons"]) >= 2
        assert any("VBRUN300" in x or "runtime" in x.lower() for x in r["reasons"])

    def test_one_signal_is_uncertain(self):
        # Native-looking imports but a suspiciously low density.
        odd = {"name": "ODD.EXE", "imports": ["KERNEL", "USER"],
               "relocations": 5, "code_bytes": 100000}
        assert bytecheck.classify(odd, reference=TIM)["verdict"] == "uncertain"

    def test_absolute_threshold_without_reference(self):
        assert bytecheck.classify(EMPIRE)["verdict"] == "bytecode"

    def test_format(self):
        text = bytecheck.format_classification(bytecheck.classify(EMPIRE, TIM))
        assert "BYTECODE" in text
