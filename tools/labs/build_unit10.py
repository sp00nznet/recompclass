#!/usr/bin/env python3
"""Build the Unit 10 code labs (61-70)."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 61
lab(61, "Attribution Harness", module="attribution",
    summary="""
    Count what the guest did and what your harness did, separately, so a
    screenshot stops being the only evidence you have.
    """,
    readme="""
    ## Objective

    Instrument a recompiled project so every frame reports how many draws came
    from guest code versus harness code, and how many dispatches hit the
    fallback.

    ## Background

    Module 37's characteristic failure: your harness produces your evidence. A
    green orb at 60fps drawn by 2,204 return-zero stubs. A menu drawn from
    hardcoded strings. A game that plays perfectly because an emulator is
    underneath it.

    `xboxdashboard`'s corrected README is the standard to aim at:

    > ...the stream contains **0 draws**, so no geometry has been submitted yet,
    > and **nothing in this repo has ever put a pixel on screen that the
    > dashboard did not ask for.**

    You cannot say that without counting. This lab builds the counter.

    ## Your Task

    Implement in `attribution.py`:

    - `Attribution` -- records events tagged `guest` or `harness`.
    - `record_draw`, `record_dispatch` -- the two things worth attributing.
    - `frame_summary()` -- per-frame counts, reset each frame.
    - `session_summary()` -- totals, plus the ratio that matters.
    - `honest_claim()` -- a sentence you could put in a README, which refuses to
      overstate.

    ## The Part That Matters

    `honest_claim()` must return something *weaker* when the evidence is weak.
    If every draw came from the harness, it has to say so. A reporting function
    that always sounds good is the thing this whole unit exists to prevent.
    """,
    stub='''
GUEST = "guest"
HARNESS = "harness"
SOURCES = (GUEST, HARNESS)


class Attribution:
    """Counts draws and dispatches, tagged by who caused them."""

    def __init__(self):
        self.frame = {"draws": {GUEST: 0, HARNESS: 0},
                      "dispatch": {"native": 0, "fallback": 0}}
        self.session = {"draws": {GUEST: 0, HARNESS: 0},
                        "dispatch": {"native": 0, "fallback": 0},
                        "frames": 0}

    def record_draw(self, source, count=1):
        """Record *count* draw calls attributed to *source*.

        Args:
            source: GUEST or HARNESS.
            count: how many draws.

        Raises:
            ValueError: on an unknown source. A draw you cannot attribute is
                worse than one you did not count -- it is the exact ambiguity
                this harness exists to remove.
        """
        # TODO: Validate source against SOURCES, then add to both the frame
        #       and session counters.
        pass

    def record_dispatch(self, native):
        """Record one dispatch.

        Args:
            native: True if a recompiled function ran, False if it fell back
                to an interpreter, emulator, or stub.
        """
        # TODO: Increment "native" or "fallback" in both frame and session.
        pass

    def end_frame(self):
        """Close the current frame and return its summary.

        Returns:
            A dict with "draws" and "dispatch" sub-dicts for this frame only.

        The frame counters reset afterwards; the session counters do not.
        """
        # TODO: Snapshot the frame counters, bump session["frames"], reset the
        #       frame counters, and return the snapshot.
        pass

    def session_summary(self):
        """Return session totals plus the derived ratios.

        Returns:
            A dict with:
                "frames"          - int
                "draws"           - {GUEST: int, HARNESS: int}
                "dispatch"        - {"native": int, "fallback": int}
                "guest_draw_ratio" - guest draws / total draws, 0.0 if none
                "native_ratio"     - native / total dispatches, 0.0 if none
        """
        # TODO: Copy the session counters and compute the two ratios, guarding
        #       against division by zero.
        pass


def honest_claim(summary):
    """Return a claim about the evidence that refuses to overstate it.

    Rules, checked in this order:

      - No draws at all            -> "Nothing has been drawn."
      - No guest draws             -> "All N draws came from the harness; the
                                       guest has not drawn anything."
      - Some guest draws           -> "X of N draws came from guest code
                                       (P%); the rest are harness."
      - All draws from guest       -> "All N draws came from guest code."

    Then, if any dispatches were recorded, append one sentence:

      - fallback == 0  -> " All N dispatches ran native code."
      - otherwise      -> " F of N dispatches fell back."

    Returns:
        A string.
    """
    # TODO: Implement the rules above. Percentages are rounded to whole
    #       numbers. The point of the ordering is that the weakest true
    #       statement wins.
    pass
''',
    test='''
def a():
    return attribution.Attribution()


class TestRecording:
    def test_draw_counts(self):
        t = a()
        t.record_draw(attribution.GUEST, 3)
        t.record_draw(attribution.HARNESS)
        s = t.session_summary()
        assert s is not None, "session_summary() returned None"
        assert s["draws"][attribution.GUEST] == 3
        assert s["draws"][attribution.HARNESS] == 1

    def test_bad_source_rejected(self):
        import pytest
        with pytest.raises(ValueError):
            a().record_draw("somewhere")

    def test_dispatch_counts(self):
        t = a()
        t.record_dispatch(True)
        t.record_dispatch(False)
        t.record_dispatch(True)
        s = t.session_summary()
        assert s["dispatch"]["native"] == 2
        assert s["dispatch"]["fallback"] == 1


class TestFrames:
    def test_frame_summary_isolated(self):
        t = a()
        t.record_draw(attribution.GUEST, 2)
        f1 = t.end_frame()
        assert f1 is not None, "end_frame() returned None"
        assert f1["draws"][attribution.GUEST] == 2
        t.record_draw(attribution.GUEST, 5)
        f2 = t.end_frame()
        assert f2["draws"][attribution.GUEST] == 5

    def test_session_accumulates(self):
        t = a()
        t.record_draw(attribution.GUEST)
        t.end_frame()
        t.record_draw(attribution.GUEST)
        t.end_frame()
        s = t.session_summary()
        assert s["draws"][attribution.GUEST] == 2
        assert s["frames"] == 2


class TestRatios:
    def test_guest_ratio(self):
        t = a()
        t.record_draw(attribution.GUEST, 3)
        t.record_draw(attribution.HARNESS, 1)
        assert abs(t.session_summary()["guest_draw_ratio"] - 0.75) < 1e-9

    def test_no_draws_is_zero_not_error(self):
        assert a().session_summary()["guest_draw_ratio"] == 0.0

    def test_native_ratio(self):
        t = a()
        t.record_dispatch(True)
        t.record_dispatch(True)
        t.record_dispatch(False)
        assert abs(t.session_summary()["native_ratio"] - (2 / 3)) < 1e-9


class TestHonestClaim:
    def claim(self, guest=0, harness=0, native=0, fallback=0):
        t = a()
        if guest:
            t.record_draw(attribution.GUEST, guest)
        if harness:
            t.record_draw(attribution.HARNESS, harness)
        for _ in range(native):
            t.record_dispatch(True)
        for _ in range(fallback):
            t.record_dispatch(False)
        c = attribution.honest_claim(t.session_summary())
        assert c is not None, "honest_claim() returned None"
        return c

    def test_nothing_drawn(self):
        assert "Nothing has been drawn" in self.claim()

    def test_all_harness_says_so(self):
        c = self.claim(harness=10)
        assert "harness" in c
        assert "has not drawn" in c

    def test_all_guest(self):
        c = self.claim(guest=10)
        assert "All 10 draws came from guest code" in c

    def test_mixed_reports_both(self):
        c = self.claim(guest=3, harness=1)
        assert "3 of 4" in c
        assert "75" in c

    def test_mentions_clean_dispatch(self):
        c = self.claim(guest=1, native=5)
        assert "5 dispatches ran native" in c

    def test_mentions_fallbacks(self):
        c = self.claim(guest=1, native=5, fallback=2)
        assert "2 of 7 dispatches fell back" in c

    def test_no_dispatch_sentence_when_none(self):
        c = self.claim(guest=1)
        assert "dispatch" not in c.lower()
''')

# ---------------------------------------------------------------------- 62
lab(62, "Interpreter Oracle", module="oracle",
    summary="""
    Run a lifter and an interpreter over the same instruction stream and
    report the first divergence with full state.
    """,
    readme="""
    ## Objective

    Build the differential harness from Module 38: two implementations, one
    input, and a report of exactly where and how they first disagree.

    ## Background

    Module 38 section 1: *"You cannot differentially test without a reference,
    and the reference you want is the original binary running -- not your beliefs
    about it."*

    And Module 53's project got this as right as it can be got: `difftest.py`
    runs BrickEmuPy's E0C6200 core beside the recompiled output and compares
    `pc, A, B, X, Y, SP, flags` **on every instruction** -- *"precisely because
    that core was written by someone else, from the same Epson documentation, in
    another language."*

    It found a real bug 1,486 instructions in: `RST F, i` was inverted.
    Completely silent -- the ROM ran, the screen drew, the device animated.

    ## Your Task

    Implement in `oracle.py`:

    - `State` -- a comparable register snapshot.
    - `diff_states(a, b)` -- which fields differ.
    - `run_differential(program, impl_a, impl_b, limit)` -- step both, stop at
      the first divergence.
    - `format_divergence(result)` -- a report naming the step, the instruction,
      and every differing field.

    ## The Limitation to State

    If your lifter and your interpreter share a decode table, this tests your
    *lifting*, not your *decoding* -- a decode bug affects both identically and
    is invisible. Say so when you report results. Module 38 section 2 grades
    oracle strength, and "my own implementation sharing the decode table" is the
    weak end.
    """,
    stub='''
FIELDS = ("pc", "a", "b", "x", "y", "sp", "flags")


class State:
    """A register snapshot, comparable field by field."""

    def __init__(self, **kwargs):
        for f in FIELDS:
            setattr(self, f, kwargs.get(f, 0))

    def as_dict(self):
        return {f: getattr(self, f) for f in FIELDS}

    def __eq__(self, other):
        return isinstance(other, State) and self.as_dict() == other.as_dict()

    def __repr__(self):
        return "State(" + ", ".join(
            f"{f}=0x{getattr(self, f):X}" for f in FIELDS) + ")"


def diff_states(a, b):
    """Return the names of fields that differ between two states.

    Args:
        a, b: State objects.

    Returns:
        A list of field names, in FIELDS order. Empty if identical.
    """
    # TODO: Compare each field in FIELDS and collect the names that differ.
    pass


def run_differential(program, impl_a, impl_b, limit=100000):
    """Step two implementations over *program* until they disagree.

    Each implementation is a callable(program, step_index, state) -> State,
    returning the state after executing one instruction. Both start from a
    zeroed State.

    Args:
        program: the instruction stream (opaque -- passed to both).
        impl_a: the reference (the oracle).
        impl_b: the implementation under test.
        limit: maximum steps before giving up.

    Returns:
        A dict with:
            "diverged"  - bool
            "step"      - the 0-based step at which they differ, or None
            "expected"  - impl_a's State at that step, or None
            "actual"    - impl_b's State at that step, or None
            "fields"    - list of differing field names, or []
            "steps_run" - how many steps completed

    An implementation raising StopIteration means the program ended; that is
    not a divergence, and the run stops cleanly.
    """
    # TODO: Loop up to `limit`. Advance both from their own previous state
    #       (they must not share one). Catch StopIteration from either to end
    #       the run. Compare with diff_states after each step.
    pass


def format_divergence(result):
    """Format a run_differential result as a report."""
    if not result["diverged"]:
        return (f"No divergence in {result['steps_run']} step(s).\\n"
                f"Note: a clean run proves the two agree, not that either is "
                f"correct -- see Module 38 section 6.")

    lines = [f"Diverged at step {result['step']} after "
             f"{result['steps_run']} step(s):"]
    for f in result["fields"]:
        exp = getattr(result["expected"], f)
        act = getattr(result["actual"], f)
        lines.append(f"  {f:6s} expected 0x{exp:X}, got 0x{act:X}")
    return "\\n".join(lines)
''',
    test='''
def make_impl(behaviour):
    """behaviour(step, state) -> dict of field updates, or raises StopIteration."""
    def impl(program, step, state):
        new = oracle.State(**state.as_dict())
        for k, v in behaviour(step, state).items():
            setattr(new, k, v)
        return new
    return impl


def counting(step, state):
    return {"pc": state.pc + 1, "a": (state.a + 1) & 0xFF}


def counting_wrong_at(n):
    def b(step, state):
        d = counting(step, state)
        if step == n:
            d["a"] = (d["a"] + 1) & 0xFF
        return d
    return b


def stops_after(n):
    def b(step, state):
        if step >= n:
            raise StopIteration
        return counting(step, state)
    return b


class TestDiffStates:
    def test_identical(self):
        s = oracle.State(pc=1, a=2)
        d = oracle.diff_states(s, oracle.State(pc=1, a=2))
        assert d is not None, "diff_states() returned None"
        assert d == []

    def test_one_field(self):
        assert oracle.diff_states(oracle.State(a=1), oracle.State(a=2)) == ["a"]

    def test_several_in_field_order(self):
        d = oracle.diff_states(oracle.State(pc=1, flags=1), oracle.State(pc=2, flags=2))
        assert d == ["pc", "flags"]


class TestRunDifferential:
    def test_no_divergence(self):
        r = oracle.run_differential(None, make_impl(counting), make_impl(counting), limit=50)
        assert r is not None, "run_differential() returned None"
        assert r["diverged"] is False
        assert r["steps_run"] == 50

    def test_finds_first_divergence(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(7)), limit=50)
        assert r["diverged"] is True
        assert r["step"] == 7

    def test_reports_fields(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(3)), limit=50)
        assert r["fields"] == ["a"]

    def test_reports_states(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(2)), limit=50)
        assert r["expected"].a != r["actual"].a

    def test_stops_at_end_of_program(self):
        r = oracle.run_differential(None, make_impl(stops_after(5)),
                                    make_impl(stops_after(5)), limit=100)
        assert r["diverged"] is False
        assert r["steps_run"] == 5

    def test_implementations_do_not_share_state(self):
        # If both advanced the same object, a divergence could never be seen.
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(1)), limit=10)
        assert r["diverged"] is True


class TestFormat:
    def test_clean_run_is_not_overstated(self):
        r = oracle.run_differential(None, make_impl(counting), make_impl(counting), limit=5)
        text = oracle.format_divergence(r)
        assert "No divergence" in text
        assert "not that either is" in text

    def test_names_step_and_field(self):
        r = oracle.run_differential(None, make_impl(counting),
                                    make_impl(counting_wrong_at(4)), limit=20)
        text = oracle.format_divergence(r)
        assert "step 4" in text
        assert "a " in text
''')

# ---------------------------------------------------------------------- 63
lab(63, "Bisect Harness", module="bisect_lift",
    summary="""
    A LIFT_LO/LIFT_HI style range switch, and a binary search that isolates
    one bad function out of thousands.
    """,
    readme="""
    ## Objective

    Build the single most transferable technique in this course: `git bisect`,
    applied to the address space.

    ## Background

    From `encarta`'s commit log:

    ```
    Add LIFT_LO/LIFT_HI: bisect the lifted set to find a bad lift
    ```

    A range filter. Functions inside `[LIFT_LO, LIFT_HI]` run lifted; everything
    else runs as the original. Then binary search the range. Roughly a dozen runs
    isolates one bad function out of thousands, and **each run requires no
    thought** -- only "did the symptom happen?"

    The prerequisite, from Module 38 section 4: both implementations must be
    simultaneously available and switchable **at runtime**. If switching needs a
    30-minute rebuild you will not do it, and you will read generated assembly
    instead.

    ## Your Task

    Implement in `bisect_lift.py`:

    - `in_range(addr, lo, hi)` -- the filter itself.
    - `run_with_range(addrs, lo, hi, oracle_fn, lifted_fn)` -- run a program
      with that range lifted.
    - `bisect(addrs, test)` -- binary search for the lowest address whose
      inclusion makes `test` fail.
    - `bisect_log(addrs, test)` -- the same, returning every range tried.

    `test(lo, hi)` returns True when the symptom is **absent** (the run is good).

    ## Why the Log Matters

    Module 62 section 8: a result you cannot re-derive is an impression.
    `bisect_log` is what turns "we found the bad function" into a record someone
    else can check -- and it tells you immediately if your test is
    non-deterministic, because the search will not converge.
    """,
    stub='''
def in_range(addr, lo, hi):
    """Is *addr* inside the inclusive range [lo, hi]?

    A range where lo > hi is empty -- nothing is lifted. That is the "all
    original" baseline and must be representable.
    """
    # TODO: Return the inclusive range test.
    pass


def run_with_range(addrs, lo, hi, oracle_fn, lifted_fn):
    """Execute each address with the lifted or the original implementation.

    Args:
        addrs: list of addresses, in execution order.
        lo, hi: inclusive range of addresses to run lifted.
        oracle_fn: callable(addr) -> value, the known-good implementation.
        lifted_fn: callable(addr) -> value, the implementation under test.

    Returns:
        A list of the values produced, in order.
    """
    # TODO: For each address, call lifted_fn if in_range, else oracle_fn.
    pass


def bisect(addrs, test):
    """Find the lowest address whose inclusion in the lifted range fails *test*.

    `test(lo, hi)` returns True when running [lo, hi] lifted is GOOD.

    The search assumes monotonicity: if lifting up to address X is bad, lifting
    up to anything beyond X is also bad. That holds when exactly one function is
    broken, which is the case this technique is for.

    Args:
        addrs: sorted list of candidate addresses.
        test: callable(lo, hi) -> bool.

    Returns:
        The offending address, or None if test(all) is already good.
    """
    # TODO: First check whether lifting everything is good -- if so, return None.
    #       Then binary search over the *index* into addrs for the smallest
    #       prefix [addrs[0], addrs[i]] that is bad, and return addrs[i].
    pass


def bisect_log(addrs, test):
    """Like bisect(), but also return every range tried.

    Returns:
        A tuple (found_addr_or_None, log), where log is a list of dicts with
        "lo", "hi" and "good".
    """
    # TODO: Wrap `test` so each call appends to a log, then run the same search.
    pass


def format_log(found, log):
    """Format a bisection log."""
    lines = [f"bisection: {len(log)} run(s)"]
    for entry in log:
        tag = "good" if entry["good"] else "BAD "
        lines.append(f"  [0x{entry['lo']:X}, 0x{entry['hi']:X}] {tag}")
    lines.append(f"  => {'0x%X' % found if found is not None else 'no bad function'}")
    return "\\n".join(lines)
''',
    test='''
ADDRS = [0x1000, 0x1010, 0x1020, 0x1030, 0x1040, 0x1050, 0x1060, 0x1070]
BAD = 0x1040


def good_test(lo, hi):
    """Lifting is good as long as BAD is not in the range."""
    return not bisect_lift.in_range(BAD, lo, hi)


def always_good(lo, hi):
    return True


class TestInRange:
    def test_inside(self):
        assert bisect_lift.in_range(5, 0, 10) is True

    def test_boundaries_inclusive(self):
        assert bisect_lift.in_range(0, 0, 10) is True
        assert bisect_lift.in_range(10, 0, 10) is True

    def test_outside(self):
        assert bisect_lift.in_range(11, 0, 10) is False

    def test_empty_range(self):
        assert bisect_lift.in_range(5, 10, 0) is False


class TestRunWithRange:
    def test_all_original(self):
        out = bisect_lift.run_with_range(ADDRS, 1, 0, lambda a: "o", lambda a: "l")
        assert out is not None, "run_with_range() returned None"
        assert set(out) == {"o"}

    def test_all_lifted(self):
        out = bisect_lift.run_with_range(ADDRS, 0, 0xFFFF, lambda a: "o", lambda a: "l")
        assert set(out) == {"l"}

    def test_partial(self):
        out = bisect_lift.run_with_range(ADDRS, 0x1000, 0x1020,
                                         lambda a: "o", lambda a: "l")
        assert out[:3] == ["l", "l", "l"]
        assert out[3:] == ["o"] * 5

    def test_preserves_order(self):
        out = bisect_lift.run_with_range(ADDRS, 0, 0xFFFF, lambda a: a, lambda a: a)
        assert out == ADDRS


class TestBisect:
    def test_finds_the_bad_one(self):
        assert bisect_lift.bisect(ADDRS, good_test) == BAD

    def test_returns_none_when_clean(self):
        assert bisect_lift.bisect(ADDRS, always_good) is None

    def test_first_address_bad(self):
        def t(lo, hi):
            return not bisect_lift.in_range(ADDRS[0], lo, hi)
        assert bisect_lift.bisect(ADDRS, t) == ADDRS[0]

    def test_last_address_bad(self):
        def t(lo, hi):
            return not bisect_lift.in_range(ADDRS[-1], lo, hi)
        assert bisect_lift.bisect(ADDRS, t) == ADDRS[-1]


class TestBisectLog:
    def test_returns_pair(self):
        found, log = bisect_lift.bisect_log(ADDRS, good_test)
        assert found == BAD
        assert isinstance(log, list)

    def test_log_is_logarithmic(self):
        # 8 addresses should take far fewer than 8 runs.
        _, log = bisect_lift.bisect_log(ADDRS, good_test)
        assert len(log) <= 6, f"took {len(log)} runs, expected a binary search"

    def test_log_records_outcomes(self):
        _, log = bisect_lift.bisect_log(ADDRS, good_test)
        assert all(set(e) == {"lo", "hi", "good"} for e in log)
        assert any(e["good"] is False for e in log)

    def test_format(self):
        found, log = bisect_lift.bisect_log(ADDRS, good_test)
        text = bisect_lift.format_log(found, log)
        assert "0x1040" in text
''')

# ---------------------------------------------------------------------- 64
lab(64, "Boundary Tripwires", module="tripwire",
    summary="""
    Assertions at every original-to-lifted boundary crossing, so silent
    corruption surfaces at the call that caused it.
    """,
    readme="""
    ## Objective

    Build the tripwires from Module 38 section 5, so a lifted function that
    corrupts state is caught at the call that did it rather than three minutes
    later somewhere unrelated.

    ## Background

    From `encarta`'s log:

    ```
    Add R2L_HEAPCHECK diagnostic (HeapValidate after each real->lifted call)
    ```

    Validate the heap after *every* call from original code into lifted code.
    The bugs this catches are the ones Module 38's taxonomy is full of:

    | Bug | Tripwire that catches it |
    |---|---|
    | `KERNEL.197 was skewing the caller's stack` | stack pointer restored |
    | ABI mismatch at the boundary | callee-saved registers preserved |
    | `the decode thunk writes pixels over its own plane table` | guard bytes |
    | heap corruption from a bad write | heap validation |

    These are expensive and that is fine -- they run under a debug flag, all the
    time, until the project stabilises.

    ## Your Task

    Implement in `tripwire.py`:

    - `check_stack(before, after)` -- stack pointer restored?
    - `check_callee_saved(before, after, saved_regs)` -- ABI honoured?
    - `check_guards(memory, guards)` -- guard bytes intact?
    - `guarded_call(fn, ctx, checks)` -- run a call with every check, and report
      which fired.

    ## The Design Rule

    A tripwire must name **which** invariant broke and **at which call**. A
    check that reports "something is wrong" has moved the problem, not solved
    it -- and Module 46 section 4 makes the same point about user-facing errors.
    """,
    stub='''
class TripwireFailure(Exception):
    """Raised when an invariant was violated across a boundary crossing."""

    def __init__(self, check, detail, call=None):
        super().__init__(f"{check}: {detail}" + (f" (call {call})" if call else ""))
        self.check = check
        self.detail = detail
        self.call = call


def check_stack(before, after):
    """Was the stack pointer restored across the call?

    Args:
        before, after: the stack pointer value before and after.

    Returns:
        None if the stack is intact, otherwise a detail string naming the
        delta -- e.g. "sp moved by -4 (0x1000 -> 0x0FFC)".
    """
    # TODO: Compare the two. On a mismatch return a string naming the delta
    #       and both values. Return None when they match.
    pass


def check_callee_saved(before, after, saved_regs):
    """Were the callee-saved registers preserved?

    Args:
        before, after: dicts mapping register name -> value.
        saved_regs: iterable of register names the ABI says must be preserved.

    Returns:
        None if all preserved, otherwise a detail string listing every
        clobbered register and its before/after values, comma separated,
        in *saved_regs* order.

    A register absent from either dict is not checked -- the caller decides
    what it recorded, and inventing a failure for a missing observation is
    how a tripwire starts crying wolf.
    """
    # TODO: Walk saved_regs, compare where both dicts have the register,
    #       and build the detail string.
    pass


def check_guards(memory, guards):
    """Are the guard bytes around protected regions intact?

    Args:
        memory: dict mapping address -> byte value.
        guards: dict mapping address -> expected byte value.

    Returns:
        None if every guard matches, otherwise a detail string naming each
        violated address in ascending order with expected and actual values.
        A guard address missing from memory counts as a violation -- something
        unmapped it.
    """
    # TODO: Compare each guard address against memory, in sorted order.
    pass


def guarded_call(fn, ctx, checks, call_name=None):
    """Run *fn* with tripwires around it.

    Args:
        fn: callable(ctx) -> value, the lifted function.
        ctx: a dict the checks read before and after. It must contain whatever
            the supplied checks need.
        checks: list of (name, callable(before_ctx, after_ctx) -> detail_or_None).
        call_name: optional identifier for the error message.

    Returns:
        The value fn returned.

    Raises:
        TripwireFailure: naming the FIRST check that fired, in list order.

    The before-snapshot must be a copy: if a check compares ctx against itself
    it can never fail, which is Module 35's "a check that cannot fail" in
    miniature.
    """
    # TODO: Deep-ish copy the context (a dict of dicts/ints is enough here),
    #       call fn, then run each check in order and raise on the first detail.
    pass
''',
    extra_imports="import copy",
    test='''
class TestCheckStack:
    def test_intact(self):
        assert tripwire.check_stack(0x1000, 0x1000) is None

    def test_moved(self):
        d = tripwire.check_stack(0x1000, 0x0FFC)
        assert d is not None
        assert "-4" in d or "4" in d

    def test_mentions_both_values(self):
        d = tripwire.check_stack(0x1000, 0x0FFC)
        assert "1000" in d.upper() or "0X1000" in d.upper()


class TestCalleeSaved:
    def test_preserved(self):
        before = {"rbx": 1, "rbp": 2, "rax": 9}
        after = {"rbx": 1, "rbp": 2, "rax": 77}
        assert tripwire.check_callee_saved(before, after, ["rbx", "rbp"]) is None

    def test_clobbered(self):
        before = {"rbx": 1, "rbp": 2}
        after = {"rbx": 99, "rbp": 2}
        d = tripwire.check_callee_saved(before, after, ["rbx", "rbp"])
        assert d is not None
        assert "rbx" in d
        assert "rbp" not in d

    def test_several_in_order(self):
        before = {"a": 1, "b": 2}
        after = {"a": 9, "b": 8}
        d = tripwire.check_callee_saved(before, after, ["b", "a"])
        assert d.index("b") < d.index("a")

    def test_missing_register_ignored(self):
        assert tripwire.check_callee_saved({"a": 1}, {"a": 1}, ["a", "zz"]) is None


class TestGuards:
    def test_intact(self):
        assert tripwire.check_guards({10: 0xCC, 11: 0xCC}, {10: 0xCC, 11: 0xCC}) is None

    def test_overwritten(self):
        d = tripwire.check_guards({10: 0x00}, {10: 0xCC})
        assert d is not None
        assert "10" in d

    def test_unmapped_counts_as_violation(self):
        assert tripwire.check_guards({}, {10: 0xCC}) is not None

    def test_sorted(self):
        d = tripwire.check_guards({5: 0, 20: 0}, {20: 0xCC, 5: 0xCC})
        assert d.index("5") < d.index("20")


class TestGuardedCall:
    def stack_check(self):
        return ("stack", lambda b, a: tripwire.check_stack(b["sp"], a["sp"]))

    def test_clean_call_returns_value(self):
        ctx = {"sp": 0x1000}
        result = tripwire.guarded_call(lambda c: "ok", ctx, [self.stack_check()])
        assert result == "ok"

    def test_detects_stack_damage(self):
        import pytest
        ctx = {"sp": 0x1000}

        def bad(c):
            c["sp"] -= 4
            return None
        with pytest.raises(tripwire.TripwireFailure) as e:
            tripwire.guarded_call(bad, ctx, [self.stack_check()])
        assert e.value.check == "stack"

    def test_names_the_call(self):
        import pytest
        ctx = {"sp": 0x1000}

        def bad(c):
            c["sp"] -= 4
        with pytest.raises(tripwire.TripwireFailure) as e:
            tripwire.guarded_call(bad, ctx, [self.stack_check()], call_name="sub_1234")
        assert "sub_1234" in str(e.value)

    def test_first_check_wins(self):
        import pytest
        ctx = {"sp": 0x1000}

        def bad(c):
            c["sp"] -= 4
        checks = [("first", lambda b, a: "boom"), self.stack_check()]
        with pytest.raises(tripwire.TripwireFailure) as e:
            tripwire.guarded_call(bad, ctx, checks)
        assert e.value.check == "first"

    def test_snapshot_is_a_copy(self):
        # If before and after alias the same dict, this check can never fail.
        import pytest
        ctx = {"regs": {"rbx": 1}}
        checks = [("abi", lambda b, a: tripwire.check_callee_saved(
            b["regs"], a["regs"], ["rbx"]))]

        def clobber(c):
            c["regs"]["rbx"] = 99
        with pytest.raises(tripwire.TripwireFailure):
            tripwire.guarded_call(clobber, ctx, checks)
''')

# ---------------------------------------------------------------------- 65
lab(65, "Instruction Fuzzer", module="insnfuzz",
    summary="""
    Random operands and register state through both a lifter and an
    interpreter, weighted toward the values where flag bugs live.
    """,
    readme="""
    ## Objective

    Build the cheapest thing in Module 39: an instruction fuzzer that needs no
    game and no runtime, and finds wrong-width arithmetic and bad-flag bugs
    before they ever reach a target.

    ## Background

    Module 39 section 2: *"If you build one thing from this module, build this."*

    1. Pick an instruction from your decode table.
    2. Generate random operands and random starting register state.
    3. Execute it in your interpreter and in your lifted code.
    4. Compare all registers and flags.

    And the detail that makes it work:

    > **Weight the generator toward the edges.** Uniform random operands almost
    > never produce `0x00`, `0xFF`, `0x7F`, `0x80`, or exact nibble boundaries
    > -- which is where flag bugs live. Half your inputs should come from a
    > table of interesting values.

    ## Your Task

    Implement in `insnfuzz.py`:

    - `interesting_values(width)` -- the boundary table.
    - `gen_operand(rng, width, edge_bias)` -- biased generation.
    - `fuzz_instruction(...)` -- run one instruction many times through both.
    - `shrink_case(case, still_fails)` -- reduce a failing case to a minimal one.

    ## Determinism

    Every run takes a seed and must reproduce exactly (Module 39 section 3). A
    failing case you cannot replay is not a finding.
    """,
    stub='''
import random

# Widths in bits -> mask
MASKS = {8: 0xFF, 16: 0xFFFF, 32: 0xFFFFFFFF}


def interesting_values(width):
    """Return the boundary values worth over-sampling for *width* bits.

    These are where flag bugs live: zero, all-ones, the signed boundaries,
    the nibble boundaries, and one either side of each.

    For 8 bits that is:
        0x00, 0x01, 0x0F, 0x10, 0x7F, 0x80, 0x81, 0xFE, 0xFF

    For wider widths, the same shape scaled: 0, 1, the low-nibble boundary
    (0x0F/0x10), the signed boundary (0x7F/0x80 scaled to the width), and the
    top two values.

    Returns:
        A sorted list of ints, no duplicates.
    """
    # TODO: Build the list for the given width using MASKS[width], the signed
    #       boundary (1 << (width - 1)), and the nibble boundary. Deduplicate
    #       and sort.
    pass


def gen_operand(rng, width, edge_bias=0.5):
    """Generate one operand, biased toward interesting values.

    Args:
        rng: a random.Random.
        width: bit width.
        edge_bias: probability of drawing from interesting_values() rather
            than uniformly. 0.0 is pure uniform, 1.0 is edges only.

    Returns:
        An int in [0, MASKS[width]].
    """
    # TODO: With probability edge_bias, choose from interesting_values(width);
    #       otherwise rng.randint over the full range.
    pass


def fuzz_instruction(name, impl_a, impl_b, width=8, trials=1000, seed=0,
                     edge_bias=0.5, arity=2):
    """Run one instruction through two implementations many times.

    Both implementations are callable(*operands) -> dict of results (registers,
    flags -- whatever the instruction produces). They are compared by equality.

    Args:
        name: instruction name, for the report.
        impl_a: reference implementation.
        impl_b: implementation under test.
        width: operand width in bits.
        trials: how many cases to run.
        seed: RNG seed. The same seed must produce the same cases.
        edge_bias: passed to gen_operand.
        arity: how many operands the instruction takes.

    Returns:
        A dict with:
            "name"      - the instruction name
            "trials"    - how many ran (stops early on first failure)
            "failed"    - bool
            "operands"  - the failing operand tuple, or None
            "expected"  - impl_a's result for it, or None
            "actual"    - impl_b's result for it, or None
            "seed"      - the seed, so the run can be replayed
    """
    # TODO: Seed a random.Random. Generate `arity` operands per trial, call
    #       both implementations, compare, and stop at the first mismatch.
    pass


def shrink_case(operands, still_fails, width=8):
    """Reduce a failing operand tuple to a simpler one that still fails.

    Tries, for each operand in turn, replacing it with each interesting value
    (smallest first) and keeping the change if the case still fails. Repeats
    until a full pass makes no change.

    Args:
        operands: the failing tuple.
        still_fails: callable(tuple) -> bool.
        width: operand width.

    Returns:
        A simpler failing tuple. If *still_fails* is False for the input, the
        input is returned unchanged.
    """
    # TODO: Loop until stable. For each position, try each candidate from
    #       interesting_values(width) and keep the first that still fails.
    pass


def format_result(result):
    """Format a fuzz result."""
    if not result["failed"]:
        return (f"{result['name']}: {result['trials']} trials, no divergence "
                f"(seed {result['seed']})")
    ops = ", ".join(f"0x{v:X}" for v in result["operands"])
    return (f"{result['name']}: FAILED after {result['trials']} trials "
            f"(seed {result['seed']})\\n"
            f"  operands: {ops}\\n"
            f"  expected: {result['expected']}\\n"
            f"  actual:   {result['actual']}")
''',
    test='''
def add_ref(a, b):
    r = (a + b) & 0xFF
    return {"result": r, "carry": a + b > 0xFF,
            "half": (a & 0xF) + (b & 0xF) > 0xF, "zero": r == 0}


def add_bad_half(a, b):
    d = add_ref(a, b)
    d["half"] = (a & 0xF) + (b & 0xF) >= 0xF   # off by one
    return d


class TestInterestingValues:
    def test_includes_boundaries_8bit(self):
        v = insnfuzz.interesting_values(8)
        assert v is not None, "interesting_values() returned None"
        for expected in (0x00, 0x0F, 0x10, 0x7F, 0x80, 0xFF):
            assert expected in v, f"missing 0x{expected:02X}"

    def test_sorted_unique(self):
        v = insnfuzz.interesting_values(8)
        assert v == sorted(set(v))

    def test_within_range(self):
        assert all(0 <= x <= 0xFFFF for x in insnfuzz.interesting_values(16))

    def test_16bit_signed_boundary(self):
        v = insnfuzz.interesting_values(16)
        assert 0x8000 in v and 0x7FFF in v


class TestGenOperand:
    def test_in_range(self):
        rng = __import__("random").Random(1)
        for _ in range(200):
            assert 0 <= insnfuzz.gen_operand(rng, 8) <= 0xFF

    def test_pure_edges(self):
        rng = __import__("random").Random(1)
        edges = set(insnfuzz.interesting_values(8))
        for _ in range(50):
            assert insnfuzz.gen_operand(rng, 8, edge_bias=1.0) in edges

    def test_uniform_reaches_non_edges(self):
        rng = __import__("random").Random(7)
        edges = set(insnfuzz.interesting_values(8))
        drawn = {insnfuzz.gen_operand(rng, 8, edge_bias=0.0) for _ in range(200)}
        assert drawn - edges, "edge_bias=0.0 should produce non-edge values"


class TestFuzzInstruction:
    def test_no_divergence_when_same(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=200, seed=1)
        assert r is not None, "fuzz_instruction() returned None"
        assert r["failed"] is False
        assert r["trials"] == 200

    def test_finds_the_half_carry_bug(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half,
                                      trials=2000, seed=1, edge_bias=0.5)
        assert r["failed"] is True
        assert r["operands"] is not None

    def test_deterministic(self):
        a = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=42)
        b = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=42)
        assert a["operands"] == b["operands"]

    def test_different_seeds_differ(self):
        a = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=10, seed=1)
        b = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=10, seed=2)
        assert a["seed"] != b["seed"]

    def test_reports_both_results(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=3)
        assert r["expected"] != r["actual"]

    def test_arity_one(self):
        r = insnfuzz.fuzz_instruction("inc", lambda a: {"r": (a + 1) & 0xFF},
                                      lambda a: {"r": (a + 1) & 0xFF},
                                      trials=50, seed=1, arity=1)
        assert r["failed"] is False


class TestShrink:
    def test_shrinks_to_boundary(self):
        # Fails whenever the low nibbles sum to exactly 0x0F + 1.
        def fails(ops):
            a, b = ops
            return (a & 0xF) + (b & 0xF) == 0x10
        small = insnfuzz.shrink_case((0x3F, 0xA1), fails)
        assert small is not None, "shrink_case() returned None"
        assert fails(small)
        assert sum(small) <= 0x3F + 0xA1

    def test_returns_input_when_not_failing(self):
        assert insnfuzz.shrink_case((1, 2), lambda ops: False) == (1, 2)

    def test_terminates(self):
        def fails(ops):
            return True
        result = insnfuzz.shrink_case((0xAB, 0xCD), fails)
        assert result == (0x00, 0x00)


class TestFormat:
    def test_clean(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_ref, trials=10, seed=5)
        assert "no divergence" in insnfuzz.format_result(r)

    def test_failure_mentions_seed(self):
        r = insnfuzz.fuzz_instruction("add", add_ref, add_bad_half, trials=2000, seed=9)
        assert "seed 9" in insnfuzz.format_result(r)
''')

report()
