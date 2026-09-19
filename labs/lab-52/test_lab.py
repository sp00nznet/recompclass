"""
Tests for Lab 52: Batch Harness with Failure Categories
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import batch


def _ok(name):
    return (name, lambda x: x)


def _fails(name, category):
    def stage(x):
        raise batch.StageFailure(category, f"{name} blew up")
    return (name, stage)


def _hangs(name):
    def stage(x):
        raise batch.Timeout()
    return (name, stage)


def _explodes(name):
    def stage(x):
        raise ValueError("unexpected")
    return (name, stage)


class TestRunTarget:
    def test_all_stages_pass(self):
        r = batch.run_target("game.rom", [_ok("extract"), _ok("codegen")])
        assert r is not None, "run_target() returned None"
        assert r["category"] == "ok"
        assert r["stage"] is None

    def test_categorised_failure(self):
        r = batch.run_target("game.rom",
                             [_ok("extract"), _fails("codegen", "codegen_failed")])
        assert r["category"] == "codegen_failed"
        assert r["stage"] == "codegen"

    def test_first_failure_wins(self):
        r = batch.run_target("game.rom",
                             [_fails("extract", "extract_failed"),
                              _fails("codegen", "codegen_failed")])
        assert r["category"] == "extract_failed"

    def test_timeout(self):
        r = batch.run_target("game.rom", [_hangs("extract")])
        assert r["category"] == "timeout"

    def test_unexpected_exception_is_error(self):
        r = batch.run_target("game.rom", [_explodes("codegen")])
        assert r["category"] == "error"
        assert "unexpected" in r["message"]

    def test_records_target(self):
        r = batch.run_target("game.rom", [_ok("extract")])
        assert r["target"] == "game.rom"

    def test_stages_are_threaded(self):
        seen = []

        def capture(name):
            def stage(x):
                seen.append(x)
                return x + "!"
            return (name, stage)

        batch.run_target("a", [capture("one"), capture("two")])
        assert seen == ["a", "a!"]


class TestRunBatch:
    def test_returns_one_result_per_target(self):
        results = batch.run_batch(["a", "b", "c"], [_ok("extract")])
        assert results is not None, "run_batch() returned None"
        assert len(results) == 3

    def test_isolation(self):
        # The middle target explodes; the others must still be attempted.
        def stage(x):
            if x == "b":
                raise ValueError("boom")
            return x
        results = batch.run_batch(["a", "b", "c"], [("extract", stage)])
        cats = [r["category"] for r in results]
        assert cats == ["ok", "error", "ok"]

    def test_preserves_order(self):
        results = batch.run_batch(["z", "y", "x"], [_ok("extract")])
        assert [r["target"] for r in results] == ["z", "y", "x"]


class TestSummarize:
    def test_counts(self):
        results = batch.run_batch(["a", "b"], [_ok("extract")])
        s = batch.summarize(results)
        assert s is not None, "summarize() returned None"
        assert s["ok"] == 2
        assert s["total"] == 2

    def test_mixed(self):
        def stage(x):
            if x == "b":
                raise batch.StageFailure("compile_failed")
            return x
        results = batch.run_batch(["a", "b", "c"], [("compile", stage)])
        s = batch.summarize(results)
        assert s["ok"] == 2
        assert s["compile_failed"] == 1
        assert s["total"] == 3

    def test_absent_categories_omitted(self):
        results = batch.run_batch(["a"], [_ok("extract")])
        s = batch.summarize(results)
        assert "timeout" not in s


class TestReporting:
    def test_format_mentions_counts(self):
        results = batch.run_batch(["a", "b"], [_ok("extract")])
        text = batch.format_report(batch.summarize(results))
        assert "ok" in text
        assert "2" in text

    def test_json_roundtrip(self):
        import json as _json
        results = batch.run_batch(["a"], [_ok("extract")])
        parsed = _json.loads(batch.to_json(results))
        assert parsed[0]["target"] == "a"
