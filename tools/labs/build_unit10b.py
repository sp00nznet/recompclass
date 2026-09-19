#!/usr/bin/env python3
"""Build the remaining Unit 10 code labs (66-70)."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 66
lab(66, "Divergence Minimiser", module="minimise",
    summary="""
    Shrink a long failing input to a minimal reproducer by truncation and
    backward bisection.
    """,
    readme="""
    ## Objective

    Turn a 3,600-frame recording and a frame number into a bug report.

    ## Background

    Module 39 section 4. A raw failing input is a lead, not a finding. The
    procedure:

    1. **Truncate first.** If the divergence is at frame 2,150, everything after
       it is noise. Cut there.
    2. **Bisect the input backwards.** Delete the first half; does it still
       diverge? This usually collapses thousands of frames into dozens.
    3. **Then bisect the code** (Lab 63) to find the function.

    Two nested bisections -- one over inputs, one over the address space -- is
    the standard way to go from "something is wrong in a 40,000-function binary"
    to a named function in an afternoon.

    ## Your Task

    Implement in `minimise.py`:

    - `truncate(inputs, index)` -- everything up to and including the failure.
    - `shrink_prefix(inputs, still_fails)` -- bisect away the leading inputs.
    - `shrink_elements(inputs, still_fails)` -- remove individual inputs.
    - `minimise(inputs, still_fails)` -- the whole procedure, with a log.

    `still_fails(sequence)` returns True when the sequence still reproduces.

    ## The Invariant

    Every intermediate must still reproduce. A minimiser that returns something
    which does *not* fail has produced a different bug, and you will chase it.
    Assert this.
    """,
    stub='''
def truncate(inputs, index):
    """Return inputs up to and including *index*.

    Args:
        inputs: the sequence.
        index: 0-based index of the failing step.

    Returns:
        A new list. An index beyond the end returns the whole sequence; a
        negative index returns an empty list.
    """
    # TODO: Slice the list. Clamp index into range first.
    pass


def shrink_prefix(inputs, still_fails):
    """Remove as much of the leading input as possible.

    Binary search for the largest prefix that can be dropped while the
    remainder still fails.

    Args:
        inputs: the sequence (already truncated).
        still_fails: callable(sequence) -> bool.

    Returns:
        The shortest suffix found that still fails. If dropping nothing is the
        only option, returns the input unchanged.
    """
    # TODO: Binary search over how many leading elements to drop. Keep the
    #       largest drop that still fails.
    pass


def shrink_elements(inputs, still_fails):
    """Remove individual inputs that are not needed.

    Walks from the end to the start, trying to delete each element and keeping
    the deletion when the sequence still fails. Iterating backwards keeps the
    indices of the not-yet-visited elements stable.

    Returns:
        A list with the unnecessary elements removed.
    """
    # TODO: Copy the list, walk indices in reverse, try each deletion.
    pass


def minimise(inputs, still_fails, failure_index=None):
    """Run the whole minimisation procedure.

    Order: truncate (if a failure index is given), then shrink the prefix,
    then shrink individual elements.

    Returns:
        A dict with:
            "minimal"  - the reduced sequence
            "original" - the original length
            "final"    - the reduced length
            "ratio"    - final / original, 0.0 if original was empty
            "log"      - list of (stage_name, length_after) tuples

    Raises:
        ValueError: if the input does not fail to begin with, or if any stage
            produces a sequence that no longer fails. A minimiser that loses
            the bug has produced a different one.
    """
    # TODO: Validate that still_fails(inputs) is True up front, run the three
    #       stages recording the length after each, and assert the invariant
    #       after every stage.
    pass


def format_result(result):
    """Format a minimisation result."""
    lines = [f"minimised {result['original']} -> {result['final']} "
             f"({result['ratio'] * 100:.1f}% of original)"]
    for stage, length in result["log"]:
        lines.append(f"  after {stage:16s} {length}")
    return "\\n".join(lines)
''',
    test='''
# The bug reproduces whenever the sequence contains both "a" and "z".
def needs_a_and_z(seq):
    return "a" in seq and "z" in seq


LONG = list("qqqaqqqqqqzqqqqqq")


class TestTruncate:
    def test_cuts_after_index(self):
        out = minimise.truncate([1, 2, 3, 4, 5], 2)
        assert out is not None, "truncate() returned None"
        assert out == [1, 2, 3]

    def test_index_beyond_end(self):
        assert minimise.truncate([1, 2], 99) == [1, 2]

    def test_negative_index(self):
        assert minimise.truncate([1, 2], -1) == []

    def test_does_not_mutate(self):
        data = [1, 2, 3]
        minimise.truncate(data, 1)
        assert data == [1, 2, 3]


class TestShrinkPrefix:
    def test_drops_leading_noise(self):
        out = minimise.shrink_prefix(LONG, needs_a_and_z)
        assert out is not None, "shrink_prefix() returned None"
        assert needs_a_and_z(out)
        assert len(out) < len(LONG)

    def test_keeps_failing(self):
        out = minimise.shrink_prefix(LONG, needs_a_and_z)
        assert out[0] == "a"

    def test_cannot_drop_anything(self):
        seq = list("az")
        assert minimise.shrink_prefix(seq, needs_a_and_z) == seq


class TestShrinkElements:
    def test_removes_unneeded(self):
        out = minimise.shrink_elements(list("qazq"), needs_a_and_z)
        assert out is not None, "shrink_elements() returned None"
        assert out == list("az")

    def test_keeps_failing(self):
        out = minimise.shrink_elements(LONG, needs_a_and_z)
        assert needs_a_and_z(out)

    def test_minimal_already(self):
        assert minimise.shrink_elements(list("az"), needs_a_and_z) == list("az")

    def test_does_not_mutate(self):
        data = list("qazq")
        minimise.shrink_elements(data, needs_a_and_z)
        assert data == list("qazq")


class TestMinimise:
    def test_reduces_to_two(self):
        r = minimise.minimise(LONG, needs_a_and_z)
        assert r is not None, "minimise() returned None"
        assert r["minimal"] == list("az")

    def test_reports_lengths(self):
        r = minimise.minimise(LONG, needs_a_and_z)
        assert r["original"] == len(LONG)
        assert r["final"] == 2
        assert r["ratio"] < 0.2

    def test_log_has_all_stages(self):
        r = minimise.minimise(LONG, needs_a_and_z, failure_index=len(LONG) - 1)
        stages = [s for s, _ in r["log"]]
        assert len(stages) == 3

    def test_rejects_non_failing_input(self):
        import pytest
        with pytest.raises(ValueError):
            minimise.minimise(list("qqq"), needs_a_and_z)

    def test_truncation_applied(self):
        # Everything after the last needed element should go.
        seq = list("azqqqqqqqqqq")
        r = minimise.minimise(seq, needs_a_and_z, failure_index=1)
        assert r["final"] == 2

    def test_result_still_fails(self):
        r = minimise.minimise(LONG, needs_a_and_z)
        assert needs_a_and_z(r["minimal"])
''')

# ---------------------------------------------------------------------- 67
lab(67, "Triage Tool", module="triage",
    summary="""
    Deduplicate failing reproducers by cause, then rank the surviving groups
    by how much of the program they actually affect.
    """,
    readme="""
    ## Objective

    Turn a directory of failing reproducers into a ranked work list.

    ## Background

    Module 39 section 6. A good fuzzing run produces more failures than you can
    fix, most of which are the same bug wearing different hats.

    - **Deduplicate by cause, not symptom.** Two crashes at the same address are
      one bug. The cheapest fingerprint is the first differing function address
      plus the diverging instruction.
    - **Rank by reachability, not severity.** A divergence in a function called
      every frame outranks a spectacular crash in an optional code path. Your
      existing execution traces already say which is which.
    - **Separate "diverges" from "crashes."** A crash is loud and often shallow.
      A quiet arithmetic divergence corrupts a save file two hours later.

    ## Your Task

    Implement in `triage.py`:

    - `fingerprint(report)` -- the dedup key.
    - `deduplicate(reports)` -- group by fingerprint.
    - `rank(groups, trace_counts)` -- order by reachability.
    - `triage(reports, trace_counts)` -- the whole pipeline.

    ## Why Reachability

    Module 41's number: `wormsrevolution` lifted 88,816 functions and reaches
    444. A bug in a function nothing calls is not worth your Tuesday.
    """,
    stub='''
from collections import Counter

KINDS = ("crash", "divergence")


def fingerprint(report):
    """Return a dedup key for a failure report.

    Args:
        report: dict with "func" (int address), "insn" (str) and "kind"
            (one of KINDS).

    Returns:
        A tuple (func, insn, kind). Two reports with the same fingerprint are
        the same bug.

    Raises:
        ValueError: on an unknown kind. A report you cannot classify would
            form its own group and quietly look like a distinct bug.
    """
    # TODO: Validate report["kind"] against KINDS and build the tuple.
    pass


def deduplicate(reports):
    """Group reports by fingerprint.

    Returns:
        A list of dicts, one per distinct bug, each with:
            "fingerprint" - the key
            "func"        - the function address
            "insn"        - the instruction
            "kind"        - the kind
            "count"       - how many reports collapsed into this group
            "examples"    - the reports themselves, in input order

    Groups are returned in first-seen order so the output is stable.
    """
    # TODO: Walk the reports, keying an ordered dict by fingerprint.
    pass


def rank(groups, trace_counts):
    """Order groups by how much of the program they affect.

    Sort key, highest first:
      1. execution count of the group's function (0 if it never ran)
      2. the group's report count
      3. divergences before crashes -- a quiet wrong answer is worse than a
         loud stop, because nothing tells you about it
      4. function address, so the order is deterministic

    Args:
        groups: output of deduplicate().
        trace_counts: dict mapping function address -> times executed.

    Returns:
        A new list, sorted. Each group gains a "reach" key with its execution
        count.
    """
    # TODO: Annotate each group with its reach, then sort by the key above.
    #       Remember that "divergences first" means they sort HIGHER.
    pass


def triage(reports, trace_counts):
    """Deduplicate and rank in one step.

    Returns:
        A dict with:
            "total"   - how many reports came in
            "unique"  - how many distinct bugs
            "groups"  - the ranked groups
    """
    # TODO: Chain deduplicate() and rank().
    pass


def format_triage(result):
    """Format a triage result as a work list."""
    lines = [f"{result['total']} report(s) -> {result['unique']} distinct bug(s)"]
    for i, g in enumerate(result["groups"], 1):
        lines.append(
            f"  {i}. 0x{g['func']:08X} {g['insn']:12s} {g['kind']:10s} "
            f"x{g['count']:<4d} reach={g['reach']}")
    return "\\n".join(lines)
''',
    test='''
def rep(func, insn, kind="divergence", seed=0):
    return {"func": func, "insn": insn, "kind": kind, "seed": seed}


REPORTS = [
    rep(0x1000, "add.w", seed=1),
    rep(0x1000, "add.w", seed=2),
    rep(0x1000, "add.w", seed=3),
    rep(0x2000, "ld.b", kind="crash", seed=4),
    rep(0x3000, "mul", seed=5),
]

TRACE = {0x1000: 10, 0x2000: 5000, 0x3000: 0}


class TestFingerprint:
    def test_tuple(self):
        f = triage.fingerprint(rep(0x1000, "add.w"))
        assert f is not None, "fingerprint() returned None"
        assert f == (0x1000, "add.w", "divergence")

    def test_same_bug_same_key(self):
        assert triage.fingerprint(rep(0x1000, "add.w", seed=1)) == \\
               triage.fingerprint(rep(0x1000, "add.w", seed=9))

    def test_kind_matters(self):
        assert triage.fingerprint(rep(0x1000, "add.w", "crash")) != \\
               triage.fingerprint(rep(0x1000, "add.w", "divergence"))

    def test_bad_kind(self):
        import pytest
        with pytest.raises(ValueError):
            triage.fingerprint(rep(0x1000, "add.w", "weird"))


class TestDeduplicate:
    def test_collapses(self):
        groups = triage.deduplicate(REPORTS)
        assert groups is not None, "deduplicate() returned None"
        assert len(groups) == 3

    def test_counts(self):
        groups = triage.deduplicate(REPORTS)
        by_func = {g["func"]: g for g in groups}
        assert by_func[0x1000]["count"] == 3
        assert by_func[0x2000]["count"] == 1

    def test_keeps_examples(self):
        groups = triage.deduplicate(REPORTS)
        by_func = {g["func"]: g for g in groups}
        assert len(by_func[0x1000]["examples"]) == 3
        assert by_func[0x1000]["examples"][0]["seed"] == 1

    def test_first_seen_order(self):
        groups = triage.deduplicate(REPORTS)
        assert [g["func"] for g in groups] == [0x1000, 0x2000, 0x3000]

    def test_empty(self):
        assert triage.deduplicate([]) == []


class TestRank:
    def test_reach_dominates(self):
        ranked = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert ranked is not None, "rank() returned None"
        assert ranked[0]["func"] == 0x2000      # reach 5000

    def test_unreached_last(self):
        ranked = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert ranked[-1]["func"] == 0x3000     # reach 0

    def test_adds_reach(self):
        ranked = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert ranked[0]["reach"] == 5000

    def test_missing_from_trace_is_zero(self):
        ranked = triage.rank(triage.deduplicate([rep(0x9999, "x")]), {})
        assert ranked[0]["reach"] == 0

    def test_divergence_beats_crash_at_equal_reach(self):
        reports = [rep(0x100, "a", "crash"), rep(0x200, "b", "divergence")]
        ranked = triage.rank(triage.deduplicate(reports), {0x100: 7, 0x200: 7})
        assert ranked[0]["kind"] == "divergence"

    def test_deterministic(self):
        a = triage.rank(triage.deduplicate(REPORTS), TRACE)
        b = triage.rank(triage.deduplicate(REPORTS), TRACE)
        assert [g["func"] for g in a] == [g["func"] for g in b]


class TestTriage:
    def test_counts(self):
        r = triage.triage(REPORTS, TRACE)
        assert r is not None, "triage() returned None"
        assert r["total"] == 5
        assert r["unique"] == 3

    def test_groups_ranked(self):
        r = triage.triage(REPORTS, TRACE)
        assert r["groups"][0]["func"] == 0x2000

    def test_format(self):
        text = triage.format_triage(triage.triage(REPORTS, TRACE))
        assert "3 distinct" in text
        assert "reach=5000" in text
''')

# ---------------------------------------------------------------------- 68
lab(68, "Frame Driver", module="framedrv",
    summary="""
    A cycle-counted hook that advances a frame, so a loop which assumed an
    interrupt was running underneath it no longer completes instantly.
    """,
    readme="""
    ## Objective

    Fix the bug that opens Module 40: a recompiled loop that finishes in
    microseconds because nothing is advancing time any more.

    ## Background

    From `mariopaint`'s `main.c`:

    > `$018260` is the important one. The ROM's title loop has no frame sync in
    > it at all -- it spins polling the mouse bytes and bails to the demo after
    > `$800` idle iterations. **On hardware an NMI drives the frame underneath
    > it**; interpreted here, it burns all 2048 iterations instantly with nothing
    > drawn and no input possible, so the title screen flashed past invisibly.

    The ROM's loop is correct. On real hardware it takes seconds, because a
    vertical-blank NMI fires 60 times a second underneath it. Lift that loop and
    the NMI does not exist unless you arranged for it.

    > **The original program assumed something else was advancing time. In your
    > build, nothing is, unless you build it.**

    `tirecomp` solves it with a hook in the dispatch loop:

    ```c
    uint64_t ti_cycles = 0;
    void (*ti_frame_hook)(void) = 0;
    ...
            fn();
            ti_cycles++;
            if (ti_frame_hook) ti_frame_hook();
    ```

    ## Your Task

    Implement in `framedrv.py`:

    - `CycleClock` -- accumulates cycles and fires a frame at a threshold.
    - `run_loop(...)` -- run a guest loop with the hook installed.
    - `detect_impossible_speed(...)` -- flag a loop that finished far too fast.

    ## The Trap

    A tight loop with no control transfers and no memory access never calls your
    runtime and hangs. **Pick a hook point the guest cannot avoid** -- every
    basic block, or every backward branch.
    """,
    stub='''
class CycleClock:
    """Counts guest cycles and fires a frame callback at a fixed budget.

    Attributes:
        cycles_per_frame: how many guest cycles make one frame.
        cycles: total cycles counted.
        frames: how many frames have fired.
    """

    def __init__(self, cycles_per_frame, on_frame=None):
        self.cycles_per_frame = cycles_per_frame
        self.on_frame = on_frame
        self.cycles = 0
        self.frames = 0
        self._budget = 0

    def tick(self, cycles):
        """Advance the clock by *cycles*, firing frames as the budget is crossed.

        A single tick large enough to cross several frame boundaries must fire
        the callback once per boundary -- a slow instruction does not get to
        skip frames.

        Args:
            cycles: guest cycles consumed.

        Returns:
            How many frames fired during this tick.
        """
        # TODO: Add to self.cycles and self._budget. While _budget is at least
        #       cycles_per_frame, subtract one frame's worth, bump self.frames,
        #       and call self.on_frame if set. Return the number fired.
        pass


def run_loop(iterations, cycles_per_iteration, clock, body=None):
    """Run a guest loop with the clock ticking on every iteration.

    This is the hook point: the loop body may do nothing observable, but the
    clock still advances, so frames still fire.

    Args:
        iterations: how many times the loop runs.
        cycles_per_iteration: guest cycles each iteration costs.
        clock: a CycleClock.
        body: optional callable(i) run each iteration.

    Returns:
        A dict with "iterations" and "frames" (fired during this loop).
    """
    # TODO: Loop, calling body(i) if given, then clock.tick(...), summing the
    #       frames that fired.
    pass


def detect_impossible_speed(expected_cycles, actual_cycles, tolerance=0.5):
    """Flag work that completed far faster than the guest's own timing allows.

    This is the Module 40 signature: a loop that should take a frame consumed
    almost no guest cycles, because nothing was advancing time.

    Args:
        expected_cycles: what the operation should have cost.
        actual_cycles: what it actually consumed.
        tolerance: actual below expected * tolerance is suspicious.

    Returns:
        None if the timing is plausible, otherwise a detail string naming both
        numbers and the ratio.

    An expected_cycles of 0 cannot be too fast, and returns None.
    """
    # TODO: Guard against expected_cycles == 0, compute the ratio, and return
    #       a detail string when it is below tolerance.
    pass


def format_report(clock, loop_result):
    """Format a frame-driver report."""
    return (f"iterations: {loop_result['iterations']}\\n"
            f"cycles:     {clock.cycles}\\n"
            f"frames:     {clock.frames}\\n"
            f"cycles/frame budget: {clock.cycles_per_frame}")
''',
    test='''
class TestCycleClock:
    def test_no_frame_below_budget(self):
        c = framedrv.CycleClock(100)
        fired = c.tick(50)
        assert fired is not None, "tick() returned None"
        assert fired == 0
        assert c.frames == 0

    def test_frame_at_budget(self):
        c = framedrv.CycleClock(100)
        assert c.tick(100) == 1
        assert c.frames == 1

    def test_accumulates_across_ticks(self):
        c = framedrv.CycleClock(100)
        c.tick(60)
        assert c.tick(60) == 1

    def test_large_tick_fires_several(self):
        c = framedrv.CycleClock(100)
        assert c.tick(350) == 3
        assert c.frames == 3

    def test_remainder_carries(self):
        c = framedrv.CycleClock(100)
        c.tick(150)
        assert c.tick(50) == 1

    def test_total_cycles(self):
        c = framedrv.CycleClock(100)
        c.tick(30)
        c.tick(40)
        assert c.cycles == 70

    def test_callback_fires(self):
        seen = []
        c = framedrv.CycleClock(100, on_frame=lambda: seen.append(1))
        c.tick(250)
        assert len(seen) == 2


class TestRunLoop:
    def test_the_mariopaint_bug(self):
        # A loop of 2048 iterations that the ROM expected to take seconds.
        # Without a clock it completes instantly and draws nothing.
        c = framedrv.CycleClock(cycles_per_frame=1000)
        r = framedrv.run_loop(2048, 100, c)
        assert r is not None, "run_loop() returned None"
        assert r["iterations"] == 2048
        assert r["frames"] > 200, "the loop must advance frames, not run blind"

    def test_body_runs(self):
        seen = []
        c = framedrv.CycleClock(1000)
        framedrv.run_loop(5, 10, c, body=lambda i: seen.append(i))
        assert seen == [0, 1, 2, 3, 4]

    def test_cycles_counted(self):
        c = framedrv.CycleClock(1000)
        framedrv.run_loop(10, 7, c)
        assert c.cycles == 70

    def test_zero_iterations(self):
        c = framedrv.CycleClock(1000)
        r = framedrv.run_loop(0, 10, c)
        assert r["frames"] == 0


class TestImpossibleSpeed:
    def test_plausible(self):
        assert framedrv.detect_impossible_speed(1000, 950) is None

    def test_far_too_fast(self):
        d = framedrv.detect_impossible_speed(1000, 3)
        assert d is not None
        assert "1000" in d and "3" in d

    def test_at_tolerance_boundary(self):
        assert framedrv.detect_impossible_speed(1000, 500, tolerance=0.5) is None

    def test_slower_is_fine(self):
        assert framedrv.detect_impossible_speed(1000, 5000) is None

    def test_zero_expected(self):
        assert framedrv.detect_impossible_speed(0, 0) is None
''')

# ---------------------------------------------------------------------- 69
lab(69, "Audio Clock Discipline", module="audioclock",
    summary="""
    A feedback loop that holds the audio buffer near a target fill level,
    instead of a fixed resample ratio that drifts into an underrun.
    """,
    readme="""
    ## Objective

    Fix the drift problem from Module 40 section 5 with a feedback loop rather
    than a better conversion.

    ## Background

    The guest produces samples at its rate. Your host consumes them at its rate.
    These are never the same number, and the difference is not constant.

    Naive resampling gets the pitch right and still fails, because **the error
    accumulates**. Too slow and the buffer underruns, which clicks. Too fast and
    it overruns, which drops audio. Either way it happens once every few minutes
    -- exactly long enough to be hard to reproduce.

    The fix is a feedback loop: **measure the buffer fill and adjust the
    consumption rate slightly** to hold it near a target. This is a clock
    discipline loop, and it is the standard answer in every emulator that sounds
    good.

    ## Your Task

    Implement in `audioclock.py`:

    - `Buffer` -- a ring buffer that reports underruns and overruns.
    - `ClockDiscipline` -- proportional correction toward a target fill.
    - `simulate(...)` -- run a producer/consumer mismatch over many frames.

    ## What to Measure

    Run your loop against a fixed-ratio resampler over ten simulated minutes and
    compare the fill level. The fixed ratio drifts monotonically to an underrun.
    Yours should oscillate around the target and never hit either end.

    Aim to **know** your latency rather than minimise it blindly: a stable 40ms
    beats an unstable 15ms.
    """,
    stub='''
class Buffer:
    """A fixed-capacity sample buffer that counts its own failures."""

    def __init__(self, capacity):
        self.capacity = capacity
        self.level = 0
        self.underruns = 0
        self.overruns = 0

    def write(self, count):
        """Add *count* samples, dropping any that do not fit.

        Returns:
            How many samples were actually stored. An overrun (any drop)
            increments self.overruns once per call, not once per sample.
        """
        # TODO: Clamp to capacity, count an overrun if anything was dropped.
        pass

    def read(self, count):
        """Remove up to *count* samples.

        Returns:
            How many samples were actually available. An underrun (fewer
            available than requested) increments self.underruns once per call.
        """
        # TODO: Clamp to level, count an underrun if short.
        pass

    @property
    def fill(self):
        """Fill level as a fraction of capacity, 0.0 to 1.0."""
        return self.level / self.capacity if self.capacity else 0.0


class ClockDiscipline:
    """Adjusts the consumption rate to hold a buffer near a target fill.

    The correction is proportional to the error, clamped so the pitch shift
    stays inaudible. A large correction fixes drift quickly and sounds wrong,
    which is not a trade worth making.
    """

    def __init__(self, target_fill=0.5, gain=0.05, max_correction=0.02):
        self.target_fill = target_fill
        self.gain = gain
        self.max_correction = max_correction

    def correction(self, fill):
        """Return the multiplier to apply to the nominal consumption rate.

        A fill above target means consume slightly faster (>1.0); below target,
        slightly slower (<1.0).

        The correction is `1.0 + clamp(gain * (fill - target), +/- max)`.

        Returns:
            A float near 1.0.
        """
        # TODO: Compute the error, scale by gain, clamp to +/- max_correction,
        #       and return 1.0 plus that.
        pass


def simulate(frames, produced_per_frame, nominal_consumed, capacity,
             discipline=None, drift=0.0):
    """Simulate a producer/consumer mismatch over many frames.

    Each frame: the guest writes `produced_per_frame` samples (scaled by
    `1.0 + drift` to model a clock that is slightly off), then the host reads
    `nominal_consumed` samples scaled by the discipline's correction.

    The buffer starts half full, which is what a real runtime does so there is
    slack in both directions.

    Args:
        frames: how many frames to run.
        produced_per_frame: guest sample rate per frame.
        nominal_consumed: host sample rate per frame.
        capacity: buffer size in samples.
        discipline: a ClockDiscipline, or None for a fixed ratio.
        drift: fractional clock error on the producer side.

    Returns:
        A dict with:
            "underruns" - int
            "overruns"  - int
            "fills"     - list of fill levels, one per frame
            "final_fill" - the last fill level
    """
    # TODO: Build the Buffer at half capacity, loop over frames, apply the
    #       correction when a discipline is given, and record the fill each
    #       frame.
    pass


def format_report(result):
    """Format a simulation result."""
    fills = result["fills"]
    lo = min(fills) if fills else 0.0
    hi = max(fills) if fills else 0.0
    return (f"frames:    {len(fills)}\\n"
            f"underruns: {result['underruns']}\\n"
            f"overruns:  {result['overruns']}\\n"
            f"fill:      {lo:.2f} .. {hi:.2f} (final {result['final_fill']:.2f})")
''',
    test='''
class TestBuffer:
    def test_write_and_read(self):
        b = audioclock.Buffer(100)
        assert b.write(30) == 30
        assert b.read(10) == 10
        assert b.level == 20

    def test_overrun_drops(self):
        b = audioclock.Buffer(100)
        b.write(80)
        stored = b.write(50)
        assert stored == 20
        assert b.overruns == 1
        assert b.level == 100

    def test_underrun(self):
        b = audioclock.Buffer(100)
        b.write(10)
        got = b.read(50)
        assert got == 10
        assert b.underruns == 1
        assert b.level == 0

    def test_no_spurious_counts(self):
        b = audioclock.Buffer(100)
        b.write(50)
        b.read(50)
        assert b.overruns == 0 and b.underruns == 0

    def test_fill(self):
        b = audioclock.Buffer(100)
        b.write(25)
        assert abs(b.fill - 0.25) < 1e-9


class TestDiscipline:
    def test_at_target_is_neutral(self):
        d = audioclock.ClockDiscipline(target_fill=0.5)
        c = d.correction(0.5)
        assert c is not None, "correction() returned None"
        assert abs(c - 1.0) < 1e-9

    def test_too_full_speeds_up(self):
        d = audioclock.ClockDiscipline(target_fill=0.5)
        assert d.correction(0.9) > 1.0

    def test_too_empty_slows_down(self):
        d = audioclock.ClockDiscipline(target_fill=0.5)
        assert d.correction(0.1) < 1.0

    def test_clamped(self):
        d = audioclock.ClockDiscipline(target_fill=0.5, gain=10.0, max_correction=0.02)
        assert abs(d.correction(1.0) - 1.02) < 1e-9
        assert abs(d.correction(0.0) - 0.98) < 1e-9


class TestSimulate:
    def test_fixed_ratio_drifts_into_failure(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=None, drift=0.01)
        assert r is not None, "simulate() returned None"
        assert r["overruns"] > 0, "a 1% producer drift must eventually overrun"

    def test_discipline_survives_the_same_drift(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=audioclock.ClockDiscipline(),
                                drift=0.01)
        assert r["overruns"] == 0
        assert r["underruns"] == 0

    def test_discipline_holds_near_target(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=audioclock.ClockDiscipline(target_fill=0.5),
                                drift=0.005)
        assert 0.2 < r["final_fill"] < 0.8

    def test_records_one_fill_per_frame(self):
        r = audioclock.simulate(frames=50, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000)
        assert len(r["fills"]) == 50

    def test_negative_drift_underruns_without_discipline(self):
        r = audioclock.simulate(frames=20000, produced_per_frame=800,
                                nominal_consumed=800, capacity=4000,
                                discipline=None, drift=-0.01)
        assert r["underruns"] > 0
''')

# ---------------------------------------------------------------------- 70
lab(70, "Timing Regression Test", module="timingtest",
    summary="""
    Assert that a fixed input reaches a known game state on a known frame --
    catching a pacing bug that a frame-hash comparison cannot see.
    """,
    readme="""
    ## Objective

    Build the timing check from Module 40 section 7, and demonstrate it catching
    a bug that content-only comparison misses.

    ## Background

    > **Compare frame numbers, not just frame contents.** A frame-hash
    > comparison that ignores *which* frame a hash appeared on will not notice
    > that your build reached the title screen in 4 frames instead of 180.

    That is exactly the `mariopaint` bug, and it is invisible to a set-based
    comparison: every expected frame appeared, just far too early.

    ## Your Task

    Implement in `timingtest.py`:

    - `Timeline` -- records (frame, state) observations.
    - `compare_content(a, b)` -- the weak check: same states, any order.
    - `compare_timeline(a, b, tolerance)` -- the real check: same states, same
      frames, within tolerance.
    - `assert_reaches(timeline, state, frame, tolerance)` -- a single milestone.

    ## What You Must Demonstrate

    A test where `compare_content` **passes** and `compare_timeline` **fails**.
    That pair is the whole point of the lab: it is the evidence that your old
    check was not checking what you thought.
    """,
    stub='''
class Timeline:
    """An ordered record of which state was observed on which frame."""

    def __init__(self, observations=None):
        self.observations = list(observations or [])   # list of (frame, state)

    def record(self, frame, state):
        self.observations.append((frame, state))

    def states(self):
        """Return the set of states observed."""
        return {s for _, s in self.observations}

    def frame_of(self, state):
        """Return the first frame at which *state* was observed, or None."""
        for frame, s in self.observations:
            if s == state:
                return frame
        return None


def compare_content(a, b):
    """The weak check: did both timelines see the same set of states?

    This deliberately ignores *when*. It is the comparison most projects
    actually run, and section "What You Must Demonstrate" in the README is
    about showing what it misses.

    Returns:
        A dict with:
            "match"   - bool
            "missing" - sorted states in a but not b
            "extra"   - sorted states in b but not a
    """
    # TODO: Compare the two state sets.
    pass


def compare_timeline(a, b, tolerance=0):
    """The real check: same states, reached at the same frames.

    A state reached more than *tolerance* frames away from the reference is a
    failure even though the state itself appeared.

    Args:
        a: the reference Timeline.
        b: the Timeline under test.
        tolerance: allowed absolute frame difference.

    Returns:
        A dict with:
            "match"    - bool
            "missing"  - sorted states absent from b
            "mistimed" - list of dicts with "state", "expected", "actual",
                         "delta", sorted by expected frame
    """
    # TODO: For each state in a, find its frame in b. Absent -> missing.
    #       Present but outside tolerance -> mistimed.
    pass


def assert_reaches(timeline, state, frame, tolerance=0):
    """Assert a single milestone was reached at about the right frame.

    Returns:
        None if satisfied, otherwise a detail string.
    """
    # TODO: Look up the frame, and compare against the expectation.
    pass


def format_comparison(result):
    """Format a timeline comparison."""
    if result["match"]:
        return "timeline matches"
    lines = ["timeline MISMATCH"]
    for s in result.get("missing", []):
        lines.append(f"  missing state: {s}")
    for m in result.get("mistimed", []):
        lines.append(f"  {m['state']}: expected frame {m['expected']}, "
                     f"got {m['actual']} (delta {m['delta']:+d})")
    return "\\n".join(lines)
''',
    test='''
REFERENCE = timingtest.Timeline([
    (0, "boot"), (60, "logo"), (180, "title"), (300, "menu"),
])

# Same states, far too early -- the mariopaint bug.
TOO_FAST = timingtest.Timeline([
    (0, "boot"), (1, "logo"), (4, "title"), (6, "menu"),
])

CLOSE_ENOUGH = timingtest.Timeline([
    (0, "boot"), (62, "logo"), (178, "title"), (301, "menu"),
])

MISSING_ONE = timingtest.Timeline([
    (0, "boot"), (60, "logo"), (300, "menu"),
])


class TestTimeline:
    def test_states(self):
        assert REFERENCE.states() == {"boot", "logo", "title", "menu"}

    def test_frame_of(self):
        assert REFERENCE.frame_of("title") == 180

    def test_frame_of_missing(self):
        assert REFERENCE.frame_of("credits") is None

    def test_record(self):
        t = timingtest.Timeline()
        t.record(5, "x")
        assert t.frame_of("x") == 5


class TestCompareContent:
    def test_identical(self):
        r = timingtest.compare_content(REFERENCE, REFERENCE)
        assert r is not None, "compare_content() returned None"
        assert r["match"] is True

    def test_the_weak_check_passes_the_bug(self):
        # This is the point: content comparison cannot see a pacing bug.
        assert timingtest.compare_content(REFERENCE, TOO_FAST)["match"] is True

    def test_detects_missing(self):
        r = timingtest.compare_content(REFERENCE, MISSING_ONE)
        assert r["match"] is False
        assert r["missing"] == ["title"]

    def test_detects_extra(self):
        extra = timingtest.Timeline(REFERENCE.observations + [(400, "credits")])
        r = timingtest.compare_content(REFERENCE, extra)
        assert r["extra"] == ["credits"]


class TestCompareTimeline:
    def test_identical(self):
        assert timingtest.compare_timeline(REFERENCE, REFERENCE)["match"] is True

    def test_catches_what_content_missed(self):
        r = timingtest.compare_timeline(REFERENCE, TOO_FAST)
        assert r is not None, "compare_timeline() returned None"
        assert r["match"] is False
        assert len(r["mistimed"]) >= 3

    def test_tolerance(self):
        assert timingtest.compare_timeline(REFERENCE, CLOSE_ENOUGH,
                                           tolerance=5)["match"] is True

    def test_outside_tolerance(self):
        assert timingtest.compare_timeline(REFERENCE, CLOSE_ENOUGH,
                                           tolerance=1)["match"] is False

    def test_reports_delta(self):
        r = timingtest.compare_timeline(REFERENCE, TOO_FAST)
        title = [m for m in r["mistimed"] if m["state"] == "title"][0]
        assert title["expected"] == 180
        assert title["actual"] == 4
        assert title["delta"] == -176

    def test_missing_state(self):
        r = timingtest.compare_timeline(REFERENCE, MISSING_ONE)
        assert "title" in r["missing"]

    def test_mistimed_sorted_by_expected(self):
        r = timingtest.compare_timeline(REFERENCE, TOO_FAST)
        frames = [m["expected"] for m in r["mistimed"]]
        assert frames == sorted(frames)


class TestAssertReaches:
    def test_exact(self):
        assert timingtest.assert_reaches(REFERENCE, "title", 180) is None

    def test_within_tolerance(self):
        assert timingtest.assert_reaches(REFERENCE, "title", 178, tolerance=5) is None

    def test_too_early(self):
        d = timingtest.assert_reaches(TOO_FAST, "title", 180, tolerance=5)
        assert d is not None
        assert "180" in d and "4" in d

    def test_never_reached(self):
        d = timingtest.assert_reaches(MISSING_ONE, "title", 180)
        assert d is not None
''')

report()
