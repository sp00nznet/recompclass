"""
Tests for Lab 51: Pipeline Driver with Content-Hash Caching
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import pipeline


import tempfile
import os


def _write(d, name, content):
    p = os.path.join(d, name)
    with open(p, "w") as f:
        f.write(content)
    return p


def _copy_stage(name, version, suffix):
    """A stage that copies each input to outdir with a suffix appended."""
    def run(inputs, outdir):
        outs = []
        for i, src in enumerate(inputs):
            dst = os.path.join(outdir, f"{name}_{i}{suffix}")
            with open(src) as fi, open(dst, "w") as fo:
                fo.write(fi.read() + f"\n[{name}]")
            outs.append(dst)
        return outs
    return pipeline.Stage(name, version, run)


class TestHashFile:
    def test_returns_hex(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "a.txt", "hello")
            h = pipeline.hash_file(p)
            assert h is not None, "hash_file() returned None"
            assert len(h) == 64
            int(h, 16)

    def test_same_content_same_hash(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "a.txt", "same")
            b = _write(d, "b.txt", "same")
            assert pipeline.hash_file(a) == pipeline.hash_file(b)

    def test_different_content_differs(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "a.txt", "one")
            b = _write(d, "b.txt", "two")
            assert pipeline.hash_file(a) != pipeline.hash_file(b)


class TestStageKey:
    def test_stable(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "a.txt", "x")
            st = _copy_stage("lift", "1.0", ".c")
            assert pipeline.stage_key(st, [a]) == pipeline.stage_key(st, [a])

    def test_version_changes_key(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "a.txt", "x")
            k1 = pipeline.stage_key(_copy_stage("lift", "1.0", ".c"), [a])
            k2 = pipeline.stage_key(_copy_stage("lift", "2.0", ".c"), [a])
            assert k1 != k2, "tool version must be part of the cache key"

    def test_content_changes_key(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "a.txt", "x")
            st = _copy_stage("lift", "1.0", ".c")
            k1 = pipeline.stage_key(st, [a])
            _write(d, "a.txt", "y")
            assert k1 != pipeline.stage_key(st, [a])

    def test_input_order_does_not_matter(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "a.txt", "x")
            b = _write(d, "b.txt", "y")
            st = _copy_stage("lift", "1.0", ".c")
            assert pipeline.stage_key(st, [a, b]) == pipeline.stage_key(st, [b, a])


class TestPipeline:
    def test_runs_all_stages_first_time(self):
        with tempfile.TemporaryDirectory() as d:
            src = _write(d, "in.txt", "rom")
            out = os.path.join(d, "out")
            os.makedirs(out)
            p = pipeline.Pipeline(
                [_copy_stage("extract", "1", ".img"), _copy_stage("lift", "1", ".c")], out)
            result = p.run([src])
            assert result is not None, "run() returned None"
            assert p.ran == ["extract", "lift"]
            assert p.skipped == []

    def test_second_run_is_fully_cached(self):
        with tempfile.TemporaryDirectory() as d:
            src = _write(d, "in.txt", "rom")
            out = os.path.join(d, "out")
            os.makedirs(out)
            p = pipeline.Pipeline(
                [_copy_stage("extract", "1", ".img"), _copy_stage("lift", "1", ".c")], out)
            p.run([src])
            p.run([src])
            assert p.ran == []
            assert p.skipped == ["extract", "lift"]

    def test_changed_input_reruns_everything(self):
        with tempfile.TemporaryDirectory() as d:
            src = _write(d, "in.txt", "rom")
            out = os.path.join(d, "out")
            os.makedirs(out)
            p = pipeline.Pipeline([_copy_stage("extract", "1", ".img")], out)
            p.run([src])
            _write(d, "in.txt", "different rom")
            p.run([src])
            assert p.ran == ["extract"]

    def test_output_threads_into_next_stage(self):
        with tempfile.TemporaryDirectory() as d:
            src = _write(d, "in.txt", "rom")
            out = os.path.join(d, "out")
            os.makedirs(out)
            p = pipeline.Pipeline(
                [_copy_stage("extract", "1", ".img"), _copy_stage("lift", "1", ".c")], out)
            result = p.run([src])
            with open(result[0]) as f:
                text = f.read()
            assert "[extract]" in text and "[lift]" in text


class TestProvenance:
    def test_records_stages(self):
        with tempfile.TemporaryDirectory() as d:
            src = _write(d, "in.txt", "rom")
            out = os.path.join(d, "out")
            os.makedirs(out)
            p = pipeline.Pipeline([_copy_stage("extract", "1.2", ".img")], out)
            p.run([src])
            rec = p.provenance()
            assert rec is not None, "provenance() returned None"
            assert len(rec["stages"]) == 1
            assert rec["stages"][0]["name"] == "extract"
            assert rec["stages"][0]["version"] == "1.2"
            assert rec["stages"][0]["cached"] is False

    def test_records_input_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            src = _write(d, "in.txt", "rom")
            out = os.path.join(d, "out")
            os.makedirs(out)
            p = pipeline.Pipeline([_copy_stage("extract", "1", ".img")], out)
            p.run([src])
            rec = p.provenance()
            assert len(rec["inputs"]) == 1
            assert len(rec["inputs"][0][1]) == 64

    def test_marks_cached_on_second_run(self):
        with tempfile.TemporaryDirectory() as d:
            src = _write(d, "in.txt", "rom")
            out = os.path.join(d, "out")
            os.makedirs(out)
            p = pipeline.Pipeline([_copy_stage("extract", "1", ".img")], out)
            p.run([src])
            p.run([src])
            assert p.provenance()["stages"][0]["cached"] is True
