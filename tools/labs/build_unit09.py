#!/usr/bin/env python3
"""Build the Unit 9 labs (51-59)."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 51
lab(51, "Pipeline Driver with Content-Hash Caching", module="pipeline",
    summary="""
    A stage-based pipeline driver. Each stage is a pure function over files,
    so a stage whose inputs have not changed does not need to run again.
    """,
    readme="""
    ## Objective

    Build the pipeline driver from Module 33: a sequence of stages, each taking
    files and producing files, with a content-hash cache so unchanged stages are
    skipped.

    ## Background

    A recompilation pipeline is a chain of file transformations:

    ```
    container --> image --> function set --> disassembly --> lifted C --> binary
    ```

    Treating each stage as a pure function over files buys three things:
    caching (unchanged inputs mean no rerun), inspection (every intermediate is
    a file you can diff), and bisection (rerun one stage in isolation).

    The cache key for a stage is the hash of its inputs **plus the version of
    the tool that produced them**. Leaving the tool version out is the classic
    mistake: you change the lifter, the inputs are identical, and the cache
    serves you yesterday's output.

    ## Your Task

    Implement in `pipeline.py`:

    - `hash_file(path)` -- SHA-256 of a file's contents, as hex.
    - `stage_key(stage, inputs)` -- a cache key combining the stage name, its
      tool version, and the hashes of every input file.
    - `Pipeline.run(...)` -- execute stages in order, skipping any whose key is
      already in the cache, and record what ran versus what was skipped.
    - `Pipeline.provenance()` -- a record of inputs, tool versions and outputs
      for the last run (Module 33 section 6).

    ## Why This Matters

    Module 37's standard is that a number you cannot re-derive is an impression.
    A pipeline you cannot re-run from scratch cannot produce re-derivable
    numbers, so this is the foundation everything in Semester 3 sits on.
    """,
    stub='''
import hashlib
import json


class Stage:
    """One pipeline stage.

    Attributes:
        name: stage name, used in the cache key.
        version: tool version string. Changing it invalidates the cache.
        func: callable(inputs: list[str], outdir: str) -> list[str].
              Returns the paths it produced.
    """

    def __init__(self, name, version, func):
        self.name = name
        self.version = version
        self.func = func


def hash_file(path):
    """Return the SHA-256 hex digest of a file's contents.

    Args:
        path: path to the file.

    Returns:
        A 64-character lowercase hex string.
    """
    # TODO: Read the file in binary mode and return hashlib.sha256(data).hexdigest().
    pass


def stage_key(stage, inputs):
    """Compute a cache key for running *stage* over *inputs*.

    The key must change if any of these change:
      - the stage name
      - the stage's tool version
      - the contents of any input file

    Args:
        stage: a Stage.
        inputs: list of input file paths.

    Returns:
        A hex string.
    """
    # TODO: Build a stable string from stage.name, stage.version and the
    #       sorted (path, hash_file(path)) pairs, then hash it.
    #       Sorting matters: the same inputs in a different order are the
    #       same inputs, and must produce the same key.
    pass


class Pipeline:
    """Runs stages in order, skipping those whose inputs are unchanged."""

    def __init__(self, stages, outdir):
        self.stages = stages
        self.outdir = outdir
        self.cache = {}        # stage_key -> list of output paths
        self.ran = []          # names of stages that executed this run
        self.skipped = []      # names of stages served from cache
        self._provenance = {}

    def run(self, inputs):
        """Run every stage in order, threading outputs into the next stage.

        For each stage:
          - compute its key from the current inputs
          - if the key is in self.cache, record a skip and reuse the outputs
          - otherwise run it, store the outputs under the key, record a run

        Args:
            inputs: list of paths feeding the first stage.

        Returns:
            The final stage's output paths.
        """
        # TODO: Implement the loop described above. Reset self.ran and
        #       self.skipped at the start so repeated runs report correctly,
        #       and record provenance as you go (see provenance()).
        pass

    def provenance(self):
        """Return a record of the last run.

        Returns:
            A dict with keys:
                "inputs"  - list of (path, hash) pairs for the initial inputs
                "stages"  - list of dicts, one per stage, each with
                            "name", "version", "key", "cached" (bool),
                            "outputs" (list of paths)
        """
        # TODO: Return the provenance record built during run().
        pass


def format_provenance(record):
    """Format a provenance record as human-readable lines."""
    lines = ["=== Provenance ==="]
    for path, digest in record.get("inputs", []):
        lines.append(f"  input  {path}  {digest[:12]}")
    for st in record.get("stages", []):
        tag = "CACHED" if st["cached"] else "RAN   "
        lines.append(f"  {tag} {st['name']:20s} v{st['version']:8s} {st['key'][:12]}")
    return "\\n".join(lines)
''',
    test='''
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
                fo.write(fi.read() + f"\\n[{name}]")
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
''')

# ---------------------------------------------------------------------- 52
lab(52, "Batch Harness with Failure Categories", module="batch",
    summary="""
    Run many targets through a pipeline unattended, isolating failures and
    reporting them by category rather than as a single pass rate.
    """,
    readme="""
    ## Objective

    Build the batch harness from Module 33 section 4: run a directory of targets
    through a pipeline without supervision, and produce a machine-readable report
    that separates failures by *kind*.

    ## Background

    Single-target work cannot tell you whether your recompiler is robust. Corpus
    runs can -- `gb-recompiled` reports 1,592 of 1,609 ROMs recompiling, and
    `3dsnes` reports 340 of 375 games rendering, *"verified by an unattended run
    of the whole corpus rather than by spot-checks."*

    A harness needs four properties:

    - **Isolation.** One target's crash must not stop the run.
    - **A timeout.** Some inputs hang. Assume it.
    - **Machine-readable output.** One row per target, diffable between runs.
    - **Failure categories, not a pass/fail bit.** "extraction failed",
      "codegen failed", "compile failed", "linked but crashed" are four
      different engineering problems whose counts move independently.

    That last one is the point of the lab. A single percentage hides the fact
    that you fixed six compile failures and introduced three crashes.

    ## Your Task

    Implement in `batch.py`:

    - `run_target(target, stages, timeout)` -- run one target through the stages,
      catching exceptions and timeouts, returning a result dict with a category.
    - `run_batch(targets, stages, timeout)` -- run all of them, isolated.
    - `summarize(results)` -- counts per category.
    - `format_report(summary)` and `to_json(results)`.

    ## Why This Matters

    Module 39 calls corpus runs "fuzzing the toolkit". They find the mapper you
    never implemented and the header variant you assumed away -- and they give
    you a number that moves, which Module 37 says is the only kind worth
    publishing.
    """,
    stub='''
import json

# Failure categories, in pipeline order. A target is assigned the category of
# the first stage that failed.
CATEGORIES = ["ok", "extract_failed", "codegen_failed", "compile_failed",
              "crashed", "timeout", "error"]


class StageFailure(Exception):
    """Raised by a stage to report a categorised failure."""

    def __init__(self, category, message=""):
        super().__init__(message)
        self.category = category
        self.message = message


class Timeout(Exception):
    """Raised when a target exceeds its time budget."""


def run_target(target, stages, timeout=30):
    """Run one target through *stages*, catching everything.

    Each stage is a callable taking the value produced by the previous stage
    (the first receives *target*) and returning a value.

    A stage signals a categorised failure by raising StageFailure. A stage that
    raises Timeout is recorded as "timeout". Any other exception is "error" --
    an unexpected failure, which is itself useful information.

    Args:
        target: the target identifier (a path or name).
        stages: list of (stage_name, callable) pairs.
        timeout: seconds budget, passed through for the caller's use.

    Returns:
        A dict with keys:
            "target"   - the target
            "category" - one of CATEGORIES
            "stage"    - the stage name that failed, or None if ok
            "message"  - failure detail, or ""
    """
    # TODO: Walk the stages in order, passing each result to the next.
    #       Catch StageFailure -> use its category and the current stage name.
    #       Catch Timeout      -> category "timeout".
    #       Catch Exception    -> category "error", message = str(exc).
    #       If every stage completes, category "ok", stage None.
    pass


def run_batch(targets, stages, timeout=30):
    """Run every target, isolated from the others.

    One target failing -- for any reason, including a crash in your own
    harness code -- must not prevent the remaining targets from running.

    Returns:
        A list of result dicts from run_target, in target order.
    """
    # TODO: Call run_target for each target and collect the results.
    pass


def summarize(results):
    """Count results per category.

    Returns:
        A dict mapping category name -> count. Categories with no results
        are omitted. Also includes "total".
    """
    # TODO: Count each result's category, and add a "total" key.
    pass


def format_report(summary):
    """Format a summary as human-readable lines, most common category first."""
    total = summary.get("total", 0)
    lines = [f"=== Batch report: {total} target(s) ==="]
    for cat, count in sorted(
            ((k, v) for k, v in summary.items() if k != "total"),
            key=lambda kv: (-kv[1], kv[0])):
        pct = (100.0 * count / total) if total else 0.0
        lines.append(f"  {cat:16s} {count:5d}  {pct:5.1f}%")
    return "\\n".join(lines)


def to_json(results):
    """Serialise results as JSON, one object per target, stably ordered."""
    return json.dumps(results, indent=2, sort_keys=True)
''',
    test='''
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
''')

# ---------------------------------------------------------------------- 54
lab(54, "Fallthrough Detector", module="fallthrough",
    summary="""
    Find functions that end without a terminator -- the signature of the
    single most common discovery bug in static recompilation.
    """,
    readme="""
    ## Objective

    Detect incorrectly split functions statically, before running anything, and
    emit an automated repair.

    ## Background

    Module 34 catalogues this bug in four disguises across four architectures:

    | Project | Fixes needed |
    |---|---|
    | racer | 143 |
    | Rampage (World Tour) | 418 |
    | pokemonsnap | ~390 |
    | Rampage 2 | ~879 outstanding |

    The cause, from pokemonsnap's README: *"The N64Recomp tool incorrectly
    splits functions that lack standard prologues."* When discovery does not
    recognise a prologue, it treats an internal branch target as a new function
    -- so the first half runs off the end of its own body and falls through
    into nothing.

    The saving grace is that it is **statically detectable**. A function whose
    last instruction is neither a return nor an unconditional branch is
    suspicious on its face, and you can find every one of them without
    executing a single instruction.

    ## Your Task

    Given a function list (address, size, and decoded instructions), implement:

    - `ends_with_terminator(func)` -- does this function end in a return or an
      unconditional branch?
    - `find_fallthroughs(functions)` -- every function that does not.
    - `propose_merges(functions)` -- for each fallthrough, if another function
      starts exactly where it ends, propose merging them.
    - `apply_merges(functions, merges)` -- produce the repaired function list.

    ## Why This Matters

    Module 34's advice is to automate the fix, because nobody hand-edits 418
    functions twice. Rampage 2's honest note -- *"~879 potential 2-instruction
    fallthrough functions need systematic fixing"* -- is the right way to hold
    it: a counted, categorised debt rather than an unknown number of future
    mystery crashes.
    """,
    stub='''
# A tiny instruction model. Each instruction is a dict:
#   {"addr": int, "size": int, "mnemonic": str}
#
# Control-flow classes, by mnemonic:
RETURNS = {"ret", "rts", "jr_ra"}
UNCONDITIONAL_BRANCHES = {"jmp", "bra", "b", "j"}
CONDITIONAL_BRANCHES = {"beq", "bne", "bcc", "bcs", "jne", "je"}


def ends_with_terminator(func):
    """Does *func* end with a return or an unconditional branch?

    A function that ends any other way -- with arithmetic, a load, or a
    *conditional* branch -- runs off the end of its own body, which is the
    fallthrough signature.

    Args:
        func: dict with "addr", "size" and "instructions" (list of dicts).

    Returns:
        True if the last instruction terminates control flow.
        Returns False for a function with no instructions.
    """
    # TODO: Look at the last instruction's mnemonic. It terminates if it is in
    #       RETURNS or UNCONDITIONAL_BRANCHES. A conditional branch does NOT
    #       terminate -- control can fall through it.
    pass


def find_fallthroughs(functions):
    """Return every function that does not end with a terminator.

    Args:
        functions: list of function dicts.

    Returns:
        A list of the suspicious functions, in input order.
    """
    # TODO: Filter with ends_with_terminator().
    pass


def end_address(func):
    """Return the address just past the end of *func*."""
    return func["addr"] + func["size"]


def propose_merges(functions):
    """Propose merges that would repair fallthroughs.

    A fallthrough function whose end address is exactly the start address of
    another function was almost certainly split from it. Merging them restores
    the original.

    Args:
        functions: list of function dicts.

    Returns:
        A list of (first_addr, second_addr) tuples, sorted by first_addr.
        A function that falls through into nothing (no function starts where
        it ends) is NOT proposed -- that is a different problem, and the
        caller should be told about it separately via find_fallthroughs().
    """
    # TODO: Build an address -> function index. For each fallthrough function,
    #       check whether end_address(func) is the start of another function.
    #       If so, propose the pair.
    pass


def apply_merges(functions, merges):
    """Return a new function list with the proposed merges applied.

    A merged function starts at the first function's address, has the combined
    size, and has both instruction lists concatenated.

    Merges chain: if A merges into B and B merges into C, the result is one
    function spanning all three.

    Args:
        functions: list of function dicts.
        merges: list of (first_addr, second_addr) tuples.

    Returns:
        A new list, sorted by address. The input is not modified.
    """
    # TODO: Follow the merge chains. Start from each function that is not the
    #       *second* element of any merge, then keep absorbing successors while
    #       a merge exists from the current end.
    pass


def format_report(functions):
    """Summarise the fallthrough situation for a function list."""
    bad = find_fallthroughs(functions) or []
    merges = propose_merges(functions) or []
    lines = [
        f"functions:      {len(functions)}",
        f"fallthroughs:   {len(bad)}",
        f"repairable:     {len(merges)}",
        f"unexplained:    {len(bad) - len(merges)}",
    ]
    return "\\n".join(lines)
''',
    test='''
def fn(addr, mnemonics, size=None):
    instructions = []
    a = addr
    for m in mnemonics:
        instructions.append({"addr": a, "size": 4, "mnemonic": m})
        a += 4
    return {"addr": addr, "size": size if size is not None else a - addr,
            "instructions": instructions}


class TestEndsWithTerminator:
    def test_ret_terminates(self):
        assert ends(fn(0, ["add", "ret"])) is True

    def test_unconditional_branch_terminates(self):
        assert ends(fn(0, ["add", "jmp"])) is True

    def test_arithmetic_does_not(self):
        assert ends(fn(0, ["add", "sub"])) is False

    def test_conditional_branch_does_not(self):
        assert ends(fn(0, ["cmp", "beq"])) is False

    def test_empty_function(self):
        assert ends({"addr": 0, "size": 0, "instructions": []}) is False


def ends(f):
    r = fallthrough.ends_with_terminator(f)
    assert r is not None, "ends_with_terminator() returned None"
    return r


class TestFindFallthroughs:
    def test_finds_the_bad_one(self):
        funcs = [fn(0x100, ["add", "ret"]), fn(0x200, ["add", "sub"])]
        bad = fallthrough.find_fallthroughs(funcs)
        assert bad is not None, "find_fallthroughs() returned None"
        assert len(bad) == 1
        assert bad[0]["addr"] == 0x200

    def test_none_when_all_clean(self):
        funcs = [fn(0x100, ["ret"]), fn(0x200, ["jmp"])]
        assert fallthrough.find_fallthroughs(funcs) == []

    def test_preserves_order(self):
        funcs = [fn(0x300, ["add"]), fn(0x100, ["add"])]
        bad = fallthrough.find_fallthroughs(funcs)
        assert [f["addr"] for f in bad] == [0x300, 0x100]


class TestProposeMerges:
    def test_adjacent_split(self):
        # 0x100 is 8 bytes and falls through into 0x108.
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["add", "ret"])]
        merges = fallthrough.propose_merges(funcs)
        assert merges is not None, "propose_merges() returned None"
        assert merges == [(0x100, 0x108)]

    def test_no_merge_when_terminated(self):
        funcs = [fn(0x100, ["add", "ret"]), fn(0x108, ["add", "ret"])]
        assert fallthrough.propose_merges(funcs) == []

    def test_no_merge_into_gap(self):
        # Falls through, but nothing starts at 0x108.
        funcs = [fn(0x100, ["add", "sub"]), fn(0x200, ["ret"])]
        assert fallthrough.propose_merges(funcs) == []

    def test_sorted(self):
        funcs = [fn(0x300, ["add", "sub"]), fn(0x308, ["ret"]),
                 fn(0x100, ["add", "sub"]), fn(0x108, ["ret"])]
        merges = fallthrough.propose_merges(funcs)
        assert merges == [(0x100, 0x108), (0x300, 0x308)]


class TestApplyMerges:
    def test_merges_two(self):
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["add", "ret"])]
        merged = fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert merged is not None, "apply_merges() returned None"
        assert len(merged) == 1
        assert merged[0]["addr"] == 0x100
        assert merged[0]["size"] == 16
        assert len(merged[0]["instructions"]) == 4

    def test_merged_function_now_terminates(self):
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["add", "ret"])]
        merged = fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert fallthrough.ends_with_terminator(merged[0]) is True

    def test_chain_of_three(self):
        funcs = [fn(0x100, ["add"]), fn(0x104, ["sub"]), fn(0x108, ["ret"])]
        merged = fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert len(merged) == 1
        assert merged[0]["size"] == 12
        assert len(merged[0]["instructions"]) == 3

    def test_leaves_clean_functions_alone(self):
        funcs = [fn(0x100, ["ret"]), fn(0x200, ["ret"])]
        merged = fallthrough.apply_merges(funcs, [])
        assert len(merged) == 2

    def test_does_not_mutate_input(self):
        funcs = [fn(0x100, ["add", "sub"]), fn(0x108, ["ret"])]
        before = len(funcs)
        fallthrough.apply_merges(funcs, fallthrough.propose_merges(funcs))
        assert len(funcs) == before

    def test_result_is_sorted(self):
        funcs = [fn(0x300, ["ret"]), fn(0x100, ["ret"])]
        merged = fallthrough.apply_merges(funcs, [])
        assert [f["addr"] for f in merged] == [0x100, 0x300]
''')

report()
