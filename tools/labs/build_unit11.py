#!/usr/bin/env python3
"""Build the Unit 11 code labs (73-79)."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 73
lab(73, "Guest-Level Sampling Profiler", module="gprof",
    summary="""
    Sample the program counter and resolve each sample to a guest function,
    producing a profile in the game's own terms rather than the host's.
    """,
    readme="""
    ## Objective

    Build a profiler that reports in guest functions, which a host profiler
    cannot do.

    ## Background

    Module 41 section 4. Generated code is thousands of near-identical
    `sub_XXXXXXXX` functions, and a host profiler shows you host symbols. But
    Module 30's spin watchdog already does the useful half:

    > A built-in **spin watchdog** periodically samples the main thread's PC and
    > resolves it to a guest function, so a silent hang becomes a named address
    > to chase.

    The same mechanism is a serviceable profiler. Sample periodically, resolve
    to a *guest* function, and you get a profile in terms of the game's own
    structure.

    ## Your Task

    Implement in `gprof.py`:

    - `resolve(addr, functions)` -- address to the function containing it.
    - `Sampler` -- collects samples and counts them per function.
    - `profile()` -- ranked results with percentages.
    - `detect_spin(samples, threshold)` -- the watchdog: is one address
      dominating in a way that means we are stuck?

    ## Why Both

    A profiler and a hang detector are the same instrument read two ways. If
    90% of samples land on one address, that is either your hottest function or
    your hang -- and the difference is whether the address is *advancing*.
    """,
    stub='''
import bisect


def resolve(addr, functions):
    """Find the function containing *addr*.

    Args:
        addr: the sampled program counter.
        functions: list of (start, size, name) tuples, not necessarily sorted.

    Returns:
        The function name, or None if the address is in no known function.

    Use a binary search over the sorted starts -- a profiler that is O(n) per
    sample changes the thing it is measuring.
    """
    # TODO: Sort by start once (or accept a pre-sorted list), bisect for the
    #       last function starting at or before addr, then check that addr is
    #       actually inside its extent.
    pass


class Sampler:
    """Collects PC samples and resolves them to guest functions."""

    def __init__(self, functions):
        self.functions = sorted(functions, key=lambda f: f[0])
        self.samples = []
        self.unresolved = 0

    def sample(self, addr):
        """Record one sample.

        Samples that resolve to no function increment self.unresolved -- that
        count is itself informative, because it usually means execution left
        the recompiled image.
        """
        # TODO: Append the (addr, name) pair, or bump unresolved.
        pass

    def profile(self):
        """Return a ranked profile.

        Returns:
            A list of dicts with "name", "samples" and "percent", sorted by
            sample count descending then name ascending. Percent is of total
            samples taken, including unresolved ones -- otherwise a build that
            spends half its time outside the image looks perfectly healthy.
        """
        # TODO: Count per name, compute percentages against
        #       len(self.samples) + self.unresolved, and sort.
        pass


def detect_spin(samples, threshold=0.9):
    """Is the program stuck?

    Args:
        samples: list of (addr, name) pairs, in time order.
        threshold: fraction of samples at one address that counts as a spin.

    Returns:
        None if execution looks healthy, otherwise a detail string naming the
        address, the function and the fraction.

    An empty sample list is not a spin.
    """
    # TODO: Count addresses. If the most common exceeds threshold, report it.
    pass


def format_profile(sampler):
    """Format a profile."""
    rows = sampler.profile()
    total = len(sampler.samples) + sampler.unresolved
    lines = [f"{total} samples ({sampler.unresolved} outside the image)"]
    for r in rows:
        lines.append(f"  {r['percent']:5.1f}%  {r['samples']:6d}  {r['name']}")
    return "\\n".join(lines)
''',
    test='''
FUNCS = [(0x1000, 0x100, "main"), (0x1100, 0x080, "update"), (0x2000, 0x200, "render")]


class TestResolve:
    def test_start(self):
        assert gprof.resolve(0x1000, FUNCS) == "main"

    def test_middle(self):
        assert gprof.resolve(0x1050, FUNCS) == "main"

    def test_last_byte(self):
        assert gprof.resolve(0x10FF, FUNCS) == "main"

    def test_next_function(self):
        assert gprof.resolve(0x1100, FUNCS) == "update"

    def test_gap(self):
        assert gprof.resolve(0x1200, FUNCS) is None

    def test_before_everything(self):
        assert gprof.resolve(0x0100, FUNCS) is None


class TestSampler:
    def test_counts(self):
        s = gprof.Sampler(FUNCS)
        for a in (0x1000, 0x1010, 0x2000):
            s.sample(a)
        p = s.profile()
        assert p is not None, "profile() returned None"
        assert p[0]["name"] == "main"
        assert p[0]["samples"] == 2

    def test_unresolved(self):
        s = gprof.Sampler(FUNCS)
        s.sample(0x9999)
        assert s.unresolved == 1
        assert s.profile() == []

    def test_percent_includes_unresolved(self):
        s = gprof.Sampler(FUNCS)
        s.sample(0x1000)
        s.sample(0x9999)
        assert abs(s.profile()[0]["percent"] - 50.0) < 1e-9

    def test_sorted(self):
        s = gprof.Sampler(FUNCS)
        for a in [0x2000] * 3 + [0x1000] * 5:
            s.sample(a)
        names = [r["name"] for r in s.profile()]
        assert names == ["main", "render"]


class TestDetectSpin:
    def test_healthy(self):
        samples = [(0x1000 + i, "main") for i in range(100)]
        assert gprof.detect_spin(samples) is None

    def test_stuck(self):
        samples = [(0x1234, "update")] * 95 + [(0x1000, "main")] * 5
        d = gprof.detect_spin(samples)
        assert d is not None
        assert "1234" in d.upper() or "0X1234" in d.upper()
        assert "update" in d

    def test_empty(self):
        assert gprof.detect_spin([]) is None

    def test_threshold_respected(self):
        samples = [(0x1234, "u")] * 6 + [(0x1000, "m")] * 4
        assert gprof.detect_spin(samples, threshold=0.9) is None
        assert gprof.detect_spin(samples, threshold=0.5) is not None
''')

# ---------------------------------------------------------------------- 74
lab(74, "Vector Lifter With a Reference", module="veclift",
    summary="""
    Lift a guest vector ISA to host intrinsics, with scalar reference
    implementations, and differentially test them at the boundaries.
    """,
    readme="""
    ## Objective

    Lift vector instructions and prove them correct where it matters: NaN,
    denormal, zero and saturation boundaries.

    ## Background

    Module 42 section 4. The traps, in order of how much time they cost:

    - **Reciprocal estimates.** The guest's `vrsqrte` has an architecturally
      defined low precision. `_mm_rsqrt_ps` has *a different* low precision.
    - **Denormals.** Many consoles flush to zero in hardware. Your host may not.
    - **NaN in min/max.** The guest and the host may disagree about which
      operand wins.
    - **Saturation.** RSP and MMI integer SIMD saturate rather than wrapping.

    All of these are exactly what a differential test catches and eyeballing
    does not. Lab 39's project ships `sim_*` reference implementations alongside
    its lifters for this reason.

    ## Your Task

    Implement in `veclift.py`:

    - `saturate(value, width, signed)` -- clamping, not wrapping.
    - `vadd_sat(a, b, ...)` -- saturating elementwise add.
    - `flush_denormals(vec, enabled)` -- model the guest's FTZ mode.
    - `vmin(a, b, nan_wins)` -- min with an explicit NaN policy.
    - `differential(op_a, op_b, cases)` -- compare two implementations.

    ## The Point

    The lab is not the arithmetic. It is that **every one of these needs an
    explicit policy**, and a lifter that does not state its NaN and denormal
    behaviour has one anyway -- it just does not know what it is.
    """,
    stub='''
import math


def saturate(value, width=8, signed=False):
    """Clamp *value* into the range representable in *width* bits.

    Saturating arithmetic clamps at the boundary rather than wrapping. The RSP
    and MMI both do this, and a lifter that wraps produces plausible garbage.

    Args:
        value: the unclamped integer.
        width: bit width.
        signed: signed range if True.

    Returns:
        The clamped value.
    """
    # TODO: Compute the range for (width, signed) and clamp.
    pass


def vadd_sat(a, b, width=8, signed=False):
    """Elementwise saturating add of two equal-length vectors.

    Raises:
        ValueError: if the lengths differ. A silent zip() would truncate,
            which is the kind of quiet wrongness this whole unit is about.
    """
    # TODO: Validate lengths, then saturate each elementwise sum.
    pass


def flush_denormals(vec, enabled=True):
    """Model the guest's flush-to-zero mode.

    Many consoles flush denormals to zero in hardware; your host may not, and
    the difference is both a slowdown and a numeric difference.

    Args:
        vec: list of floats.
        enabled: whether FTZ is on.

    Returns:
        A new list, with denormals replaced by 0.0 (preserving sign) when
        enabled. Zero, infinity and NaN pass through untouched.
    """
    # TODO: A float is denormal when it is non-zero, finite, and its magnitude
    #       is below sys.float_info.min. Preserve the sign of the zero.
    pass


def vmin(a, b, nan_wins=False):
    """Elementwise minimum with an explicit NaN policy.

    Args:
        a, b: equal-length lists of floats.
        nan_wins: if True, a NaN operand propagates. If False, the non-NaN
            operand is chosen (the common hardware behaviour).

    Returns:
        A new list.

    Raises:
        ValueError: on a length mismatch.
    """
    # TODO: Handle the NaN cases explicitly before comparing. math.isnan().
    pass


def differential(op_a, op_b, cases):
    """Compare two implementations over a list of argument tuples.

    Comparison treats NaN as equal to NaN -- otherwise every case containing a
    NaN reports a spurious divergence and the real ones are lost in the noise.

    Args:
        op_a: reference callable.
        op_b: callable under test.
        cases: list of argument tuples.

    Returns:
        A dict with "total", "diverged" (count), and "failures" (list of dicts
        with "case", "expected" and "actual").
    """
    # TODO: Run both over each case, compare with NaN-aware equality, collect.
    pass


def interesting_floats():
    """Float values worth testing: zeros, denormals, infinities, NaN."""
    import sys
    tiny = sys.float_info.min
    return [0.0, -0.0, tiny, -tiny, tiny / 2, -tiny / 2,
            1.0, -1.0, float("inf"), float("-inf"), float("nan")]
''',
    test='''
import math


class TestSaturate:
    def test_unsigned_in_range(self):
        assert veclift.saturate(100, 8, False) == 100

    def test_unsigned_clamps_high(self):
        assert veclift.saturate(300, 8, False) == 255

    def test_unsigned_clamps_low(self):
        assert veclift.saturate(-5, 8, False) == 0

    def test_signed_range(self):
        assert veclift.saturate(200, 8, True) == 127
        assert veclift.saturate(-200, 8, True) == -128

    def test_does_not_wrap(self):
        # The whole point: 256 must become 255, not 0.
        assert veclift.saturate(256, 8, False) == 255


class TestVaddSat:
    def test_elementwise(self):
        assert veclift.vadd_sat([1, 2], [3, 4]) == [4, 6]

    def test_saturates(self):
        assert veclift.vadd_sat([250], [10]) == [255]

    def test_signed(self):
        assert veclift.vadd_sat([120], [50], signed=True) == [127]

    def test_length_mismatch(self):
        import pytest
        with pytest.raises(ValueError):
            veclift.vadd_sat([1, 2], [3])


class TestFlushDenormals:
    def test_flushes(self):
        import sys
        out = veclift.flush_denormals([sys.float_info.min / 2])
        assert out is not None, "flush_denormals() returned None"
        assert out[0] == 0.0

    def test_preserves_sign(self):
        import sys
        out = veclift.flush_denormals([-sys.float_info.min / 2])
        assert math.copysign(1.0, out[0]) == -1.0

    def test_disabled(self):
        import sys
        d = sys.float_info.min / 2
        assert veclift.flush_denormals([d], enabled=False)[0] == d

    def test_normals_untouched(self):
        assert veclift.flush_denormals([1.5, -2.5]) == [1.5, -2.5]

    def test_inf_and_nan_untouched(self):
        out = veclift.flush_denormals([float("inf"), float("nan")])
        assert out[0] == float("inf")
        assert math.isnan(out[1])


class TestVmin:
    def test_basic(self):
        assert veclift.vmin([1.0, 5.0], [3.0, 2.0]) == [1.0, 2.0]

    def test_nan_loses_by_default(self):
        out = veclift.vmin([float("nan")], [2.0])
        assert out[0] == 2.0

    def test_nan_wins_when_asked(self):
        out = veclift.vmin([float("nan")], [2.0], nan_wins=True)
        assert math.isnan(out[0])

    def test_both_nan(self):
        out = veclift.vmin([float("nan")], [float("nan")])
        assert math.isnan(out[0])

    def test_length_mismatch(self):
        import pytest
        with pytest.raises(ValueError):
            veclift.vmin([1.0], [1.0, 2.0])


class TestDifferential:
    def test_agreement(self):
        r = veclift.differential(lambda a, b: a + b, lambda a, b: b + a,
                                 [(1, 2), (3, 4)])
        assert r is not None, "differential() returned None"
        assert r["diverged"] == 0
        assert r["total"] == 2

    def test_finds_divergence(self):
        r = veclift.differential(lambda a, b: a + b, lambda a, b: a - b, [(1, 2)])
        assert r["diverged"] == 1
        assert r["failures"][0]["case"] == (1, 2)

    def test_nan_equals_nan(self):
        nan = float("nan")
        r = veclift.differential(lambda a: nan, lambda a: nan, [(1.0,)])
        assert r["diverged"] == 0, "NaN != NaN would drown real findings in noise"

    def test_records_both_values(self):
        r = veclift.differential(lambda a: 1, lambda a: 2, [(0,)])
        assert r["failures"][0]["expected"] == 1
        assert r["failures"][0]["actual"] == 2
''')

# ---------------------------------------------------------------------- 75
lab(75, "Lane Order and Permutes", module="lanes",
    summary="""
    Lift a big-endian guest's permute to a little-endian host correctly, and
    demonstrate the mirrored-constant bug the naive translation produces.
    """,
    readme="""
    ## Objective

    Get vector lane order right across an endianness boundary, and show what
    getting it wrong looks like.

    ## Background

    Module 42 section 4, last trap:

    > **Lane order.** Big-endian guests (Xbox 360, PS3, N64) store vectors with
    > lane 0 at the opposite end from a little-endian host. A permute constant
    > lifted literally is mirrored. Get this wrong and geometry is scrambled in
    > a way that looks like a renderer bug.

    That last clause is why this deserves a lab. The symptom appears in the
    renderer, so that is where people look.

    ## Your Task

    Implement in `lanes.py`:

    - `mirror_index(i, count)` -- the lane-order conversion.
    - `permute(vec, control)` -- apply a permute control vector.
    - `lift_permute_naive(control)` -- the wrong translation (copy it as-is).
    - `lift_permute(control, count)` -- the correct one.
    - `demonstrate_bug(vec, control)` -- run both and show the difference.

    ## What You Must Show

    `demonstrate_bug` must return a case where naive and correct differ. A test
    asserts it. Being able to *produce* the bug on demand is what makes it
    findable later.
    """,
    stub='''
def mirror_index(i, count):
    """Convert a lane index between big-endian and little-endian ordering.

    With `count` lanes, lane 0 at one end corresponds to lane `count - 1` at
    the other. The conversion is its own inverse.

    Raises:
        ValueError: if i is outside [0, count).
    """
    # TODO: Validate and return the mirrored index.
    pass


def permute(vec, control):
    """Apply a permute control vector.

    Args:
        vec: the source lanes.
        control: list of source indices, one per destination lane.

    Returns:
        A new list where result[i] = vec[control[i]].

    Raises:
        IndexError: if any control entry is out of range.
    """
    # TODO: Build the permuted list, validating each index.
    pass


def lift_permute_naive(control):
    """The WRONG translation: copy the guest's control vector unchanged.

    This is what a lifter does when nobody thought about lane order. It is
    correct only when the guest and host agree on lane numbering.

    Returns:
        The control vector, unchanged.
    """
    # TODO: Return control unchanged (a copy, so callers cannot alias it).
    pass


def lift_permute(control, count):
    """The correct translation for a big-endian guest on a little-endian host.

    Both the *position* of each control entry and the *value* it selects are
    expressed in guest lane numbering, so both must be mirrored.

    Args:
        control: the guest's control vector.
        count: the number of lanes.

    Returns:
        A control vector in host lane numbering.
    """
    # TODO: For each host destination lane i, the guest destination is
    #       mirror_index(i, count); look up the guest source there and mirror
    #       it back to host numbering.
    pass


def demonstrate_bug(vec, control):
    """Run both translations and report whether they differ.

    Returns:
        A dict with:
            "naive"   - result of permuting with the naive control
            "correct" - result of permuting with the corrected control
            "differ"  - bool
    """
    # TODO: Apply both and compare.
    pass
''',
    test='''
class TestMirrorIndex:
    def test_ends_swap(self):
        assert lanes.mirror_index(0, 4) == 3
        assert lanes.mirror_index(3, 4) == 0

    def test_middle(self):
        assert lanes.mirror_index(1, 4) == 2

    def test_self_inverse(self):
        for i in range(4):
            assert lanes.mirror_index(lanes.mirror_index(i, 4), 4) == i

    def test_out_of_range(self):
        import pytest
        with pytest.raises(ValueError):
            lanes.mirror_index(4, 4)


class TestPermute:
    def test_identity(self):
        assert lanes.permute(["a", "b", "c", "d"], [0, 1, 2, 3]) == ["a", "b", "c", "d"]

    def test_reverse(self):
        assert lanes.permute(["a", "b", "c", "d"], [3, 2, 1, 0]) == ["d", "c", "b", "a"]

    def test_broadcast(self):
        assert lanes.permute(["a", "b"], [0, 0]) == ["a", "a"]

    def test_out_of_range(self):
        import pytest
        with pytest.raises(IndexError):
            lanes.permute(["a"], [5])


class TestLift:
    def test_naive_is_unchanged(self):
        c = [0, 1, 2, 3]
        assert lanes.lift_permute_naive(c) == c

    def test_naive_returns_a_copy(self):
        c = [0, 1, 2, 3]
        out = lanes.lift_permute_naive(c)
        out[0] = 9
        assert c[0] == 0

    def test_identity_survives(self):
        # An identity permute is identity in either lane order.
        assert lanes.lift_permute([0, 1, 2, 3], 4) == [0, 1, 2, 3]

    def test_reverse_survives(self):
        assert lanes.lift_permute([3, 2, 1, 0], 4) == [3, 2, 1, 0]

    def test_asymmetric_control_changes(self):
        # Broadcasting guest lane 0 is broadcasting host lane 3.
        assert lanes.lift_permute([0, 0, 0, 0], 4) == [3, 3, 3, 3]


class TestDemonstrateBug:
    def test_produces_a_difference(self):
        d = lanes.demonstrate_bug(["a", "b", "c", "d"], [0, 0, 0, 0])
        assert d is not None, "demonstrate_bug() returned None"
        assert d["differ"] is True
        assert d["naive"] != d["correct"]

    def test_symmetric_control_agrees(self):
        d = lanes.demonstrate_bug(["a", "b", "c", "d"], [3, 2, 1, 0])
        assert d["differ"] is False

    def test_correct_matches_guest_semantics(self):
        # Guest broadcasts its lane 0, which is "a" in guest order. In host
        # order that same element sits at index 3.
        d = lanes.demonstrate_bug(["d", "c", "b", "a"], [0, 0, 0, 0])
        assert d["correct"] == ["a", "a", "a", "a"]
''')

# ---------------------------------------------------------------------- 76
lab(76, "Memory Access Ladder", module="memladder",
    summary="""
    Three rungs of guest memory access -- a switch, a flat array, and a based
    pointer -- measured on the same workload.
    """,
    readme="""
    ## Objective

    Implement Module 43's ladder and measure what each rung costs.

    ## Background

    | Rung | What it is |
    |---|---|
    | 0 | a function with a chain of range comparisons |
    | 1 | a flat array plus a base offset -- `burnout3`'s `FMEM32` |
    | 2 | the guest's own addresses via the host MMU |

    Rung 1 is the one to feel:

    ```c
    #define FMEM32(addr) (*(volatile uint32_t *)((uintptr_t)(addr) + g_xbox_mem_offset))
    ```

    A guest address plus a constant *is* a host address. No call, no branch.

    The catch is section 2: when reads are raw arithmetic, a read of a hardware
    register no longer calls you -- and the whole point of a hardware register
    is that reading it *does something*.

    ## Your Task

    Implement in `memladder.py`:

    - `SwitchBus` -- rung 0.
    - `FlatBus` -- rung 1, with an explicit I/O window check.
    - `classify_static(addr, io_range)` -- the lift-time split.
    - `benchmark(bus, accesses)` -- count the work each rung does.

    ## What to Report

    Rung 1 must be faster *and* must still call the I/O handler for
    memory-mapped addresses. A rung 1 that loses I/O is not a faster rung 1, it
    is a broken program.
    """,
    stub='''
class IOTrap(Exception):
    """Raised when a bus implementation loses a memory-mapped access."""


class SwitchBus:
    """Rung 0: a chain of range comparisons, one per access.

    Attributes:
        comparisons: how many range checks were performed. This is the cost
            being measured.
    """

    def __init__(self, regions, io_handler=None):
        # regions: list of (start, size, bytearray) in check order
        self.regions = regions
        self.io_handler = io_handler
        self.comparisons = 0

    def read(self, addr):
        """Read one byte, walking the region list in order.

        Increments self.comparisons once per region examined, including the
        one that matches.

        Returns:
            The byte value.

        Raises:
            IOTrap: if no region matches and there is no io_handler.
        """
        # TODO: Walk self.regions in order, counting comparisons. On a match,
        #       return the byte at the right offset. On no match, call the
        #       io_handler if set, else raise IOTrap.
        pass


class FlatBus:
    """Rung 1: one array plus a base offset, with an I/O window check.

    Attributes:
        checks: how many I/O window comparisons were performed -- one per
            access, which is the entire per-access cost.
    """

    def __init__(self, size, base, io_range=None, io_handler=None):
        self.memory = bytearray(size)
        self.base = base
        self.io_range = io_range        # (lo, hi) inclusive, or None
        self.io_handler = io_handler
        self.checks = 0

    def read(self, addr):
        """Read one byte by offset arithmetic, after one I/O window check.

        Returns:
            The byte value.

        Raises:
            IOTrap: if the address is in the I/O window and no handler is set.
                Silently returning RAM for a hardware register is the exact
                failure Module 43 section 2 warns about.
        """
        # TODO: Increment checks. If io_range is set and addr falls inside it,
        #       delegate to io_handler (or raise IOTrap). Otherwise index
        #       self.memory at addr - self.base.
        pass


def classify_static(addr, io_range):
    """Decide at lift time whether an access needs the slow path.

    Most guest addresses are compile-time constants, so the lifter can emit the
    fast path directly and skip the runtime check entirely.

    Args:
        addr: the constant address, or None if it is computed at runtime.
        io_range: (lo, hi) inclusive, or None.

    Returns:
        "fast"    - a constant address outside the I/O window
        "io"      - a constant address inside it
        "dynamic" - not known at lift time, needs the runtime check
    """
    # TODO: Return the three cases above.
    pass


def benchmark(bus, accesses):
    """Run a list of addresses through a bus and report its work.

    Returns:
        A dict with "accesses", "work" (the bus's own counter) and
        "work_per_access".
    """
    # TODO: Read each address, then read the counter -- `comparisons` on a
    #       SwitchBus, `checks` on a FlatBus.
    pass
''',
    test='''
def switch_bus(io_handler=None):
    return memladder.SwitchBus([
        (0x0000, 0x100, bytearray(b"\\x11" * 0x100)),
        (0x0100, 0x100, bytearray(b"\\x22" * 0x100)),
        (0x0200, 0x100, bytearray(b"\\x33" * 0x100)),
    ], io_handler=io_handler)


class TestSwitchBus:
    def test_reads_first_region(self):
        assert switch_bus().read(0x0010) == 0x11

    def test_reads_last_region(self):
        assert switch_bus().read(0x0210) == 0x33

    def test_counts_comparisons(self):
        b = switch_bus()
        b.read(0x0210)
        assert b.comparisons == 3, "a late region costs every earlier check"

    def test_first_region_is_cheap(self):
        b = switch_bus()
        b.read(0x0010)
        assert b.comparisons == 1

    def test_unmapped_traps(self):
        import pytest
        with pytest.raises(memladder.IOTrap):
            switch_bus().read(0x9999)

    def test_unmapped_goes_to_handler(self):
        seen = []
        b = switch_bus(io_handler=lambda a: seen.append(a) or 0xAB)
        assert b.read(0x9999) == 0xAB
        assert seen == [0x9999]


class TestFlatBus:
    def test_reads(self):
        b = memladder.FlatBus(0x1000, base=0x8000)
        b.memory[0x10] = 0x55
        assert b.read(0x8010) == 0x55

    def test_one_check_per_access(self):
        b = memladder.FlatBus(0x1000, base=0x8000)
        b.read(0x8000)
        b.read(0x8FFF)
        assert b.checks == 2, "the cost must not grow with the address"

    def test_io_window_traps(self):
        import pytest
        b = memladder.FlatBus(0x1000, base=0x8000, io_range=(0x8800, 0x88FF))
        with pytest.raises(memladder.IOTrap):
            b.read(0x8810)

    def test_io_window_calls_handler(self):
        seen = []
        b = memladder.FlatBus(0x1000, base=0x8000, io_range=(0x8800, 0x88FF),
                              io_handler=lambda a: seen.append(a) or 0x7F)
        assert b.read(0x8810) == 0x7F
        assert seen == [0x8810]

    def test_outside_io_window_is_ram(self):
        b = memladder.FlatBus(0x1000, base=0x8000, io_range=(0x8800, 0x88FF),
                              io_handler=lambda a: 0x7F)
        b.memory[0x10] = 0x22
        assert b.read(0x8010) == 0x22


class TestClassifyStatic:
    def test_fast(self):
        assert memladder.classify_static(0x8010, (0x8800, 0x88FF)) == "fast"

    def test_io(self):
        assert memladder.classify_static(0x8810, (0x8800, 0x88FF)) == "io"

    def test_dynamic(self):
        assert memladder.classify_static(None, (0x8800, 0x88FF)) == "dynamic"

    def test_no_io_range(self):
        assert memladder.classify_static(0x8010, None) == "fast"


class TestBenchmark:
    def test_flat_beats_switch(self):
        accesses = [0x0210] * 100
        sw = memladder.benchmark(switch_bus(), accesses)
        assert sw is not None, "benchmark() returned None"

        flat = memladder.FlatBus(0x1000, base=0x0000)
        fl = memladder.benchmark(flat, accesses)
        assert fl["work"] < sw["work"]

    def test_reports_per_access(self):
        r = memladder.benchmark(switch_bus(), [0x0210] * 10)
        assert abs(r["work_per_access"] - 3.0) < 1e-9
''')

# ---------------------------------------------------------------------- 77
lab(77, "Endianness Two Ways", module="endian",
    summary="""
    Byte-swap-on-access versus swapped storage with an address XOR, compared
    on read-heavy and write-heavy workloads.
    """,
    readme="""
    ## Objective

    Implement both endianness strategies from Module 43 section 3 and find out
    which suits your access mix.

    ## Background

    A big-endian guest on a little-endian host needs a swap on every access.
    Two ways to make it nearly free:

    **Swap on access**, using the host's byte-swap intrinsic -- a single
    instruction. Never hand-roll shifts and masks.

    **Do not swap at all.** Store guest memory byte-swapped in units of the
    guest's word size. Aligned word accesses then need no swap; only sub-word
    accesses do, and those are handled by XOR-ing the low address bits. N64Recomp
    uses exactly this -- the common case costs nothing and the uncommon case
    costs one `xor`.

    ## Your Task

    Implement in `endian.py`:

    - `swap32(value)` -- the reference swap.
    - `SwapOnAccess` -- strategy one, counting swaps.
    - `SwappedStorage` -- strategy two, counting XORs.
    - `compare(...)` -- run both over a workload.

    Both must produce identical results for every access. A test asserts it.
    """,
    stub='''
def swap32(value):
    """Byte-swap a 32-bit value.

    Returns:
        The swapped value, masked to 32 bits.
    """
    # TODO: Reverse the four bytes.
    pass


def byte_xor(addr):
    """The address XOR that selects the right byte within a swapped word.

    With 32-bit words stored byte-swapped, byte N of a guest word lives at
    host offset N ^ 3.
    """
    return addr ^ 3


class SwapOnAccess:
    """Store native, swap on every word access.

    Attributes:
        swaps: how many byte-swaps were performed.
    """

    def __init__(self, size):
        self.memory = bytearray(size)
        self.swaps = 0

    def read32(self, addr):
        """Read a big-endian 32-bit word, swapping to host order."""
        # TODO: Read four bytes little-endian from self.memory, swap, count it.
        pass

    def read8(self, addr):
        """Read one byte. No swap is needed for a single byte."""
        # TODO: Index directly.
        pass

    def write32(self, addr, value):
        """Write a 32-bit word in guest order, swapping on the way in."""
        # TODO: Swap, count it, store four bytes little-endian.
        pass


class SwappedStorage:
    """Store pre-swapped, so aligned word access is free.

    Attributes:
        xors: how many address XORs were performed (sub-word accesses only).
        swaps: how many byte-swaps were performed -- should stay at zero for
            aligned word access, which is the entire point.
    """

    def __init__(self, size):
        self.memory = bytearray(size)
        self.xors = 0
        self.swaps = 0

    def read32(self, addr):
        """Read an aligned 32-bit word. No swap, no XOR."""
        # TODO: The word is already in host order: read four bytes
        #       little-endian and return.
        pass

    def read8(self, addr):
        """Read one byte, XOR-ing the address to find it."""
        # TODO: Count the XOR and index at byte_xor(addr).
        pass

    def write32(self, addr, value):
        """Write an aligned 32-bit word. No swap, no XOR."""
        # TODO: Store four bytes little-endian.
        pass


def compare(workload, size=0x100):
    """Run a workload through both strategies and compare cost and results.

    Args:
        workload: list of ("w32", addr, value) / ("r32", addr, None) /
            ("r8", addr, None) tuples.
        size: memory size for both.

    Returns:
        A dict with:
            "agree"          - bool, did every read match?
            "mismatches"     - list of (index, op, addr, a_value, b_value)
            "swap_cost"      - swaps performed by SwapOnAccess
            "storage_cost"   - xors performed by SwappedStorage
    """
    # TODO: Build one of each, replay the workload on both, compare every
    #       read's result, and report the two counters.
    pass
''',
    test='''
class TestSwap32:
    def test_basic(self):
        assert endian.swap32(0x11223344) == 0x44332211

    def test_involutive(self):
        assert endian.swap32(endian.swap32(0xDEADBEEF)) == 0xDEADBEEF

    def test_zero(self):
        assert endian.swap32(0) == 0


class TestSwapOnAccess:
    def test_roundtrip(self):
        m = endian.SwapOnAccess(0x100)
        m.write32(0, 0x11223344)
        assert m.read32(0) == 0x11223344

    def test_counts_swaps(self):
        m = endian.SwapOnAccess(0x100)
        m.write32(0, 1)
        m.read32(0)
        assert m.swaps == 2

    def test_byte_read_needs_no_swap(self):
        m = endian.SwapOnAccess(0x100)
        m.write32(0, 0x11223344)
        before = m.swaps
        m.read8(0)
        assert m.swaps == before


class TestSwappedStorage:
    def test_roundtrip(self):
        m = endian.SwappedStorage(0x100)
        m.write32(0, 0x11223344)
        assert m.read32(0) == 0x11223344

    def test_word_access_is_free(self):
        m = endian.SwappedStorage(0x100)
        m.write32(0, 1)
        m.read32(0)
        assert m.swaps == 0, "aligned word access must not swap"
        assert m.xors == 0

    def test_byte_access_costs_an_xor(self):
        m = endian.SwappedStorage(0x100)
        m.write32(0, 0x11223344)
        m.read8(0)
        assert m.xors == 1

    def test_byte_order_matches_guest(self):
        # Guest big-endian word 0x11223344: byte 0 is 0x11.
        a = endian.SwapOnAccess(0x100)
        b = endian.SwappedStorage(0x100)
        a.write32(0, 0x11223344)
        b.write32(0, 0x11223344)
        assert a.read8(0) == b.read8(0)
        assert a.read8(3) == b.read8(3)


class TestCompare:
    def test_agreement(self):
        wl = [("w32", 0, 0x11223344), ("r32", 0, None), ("r8", 1, None)]
        r = endian.compare(wl)
        assert r is not None, "compare() returned None"
        assert r["agree"] is True
        assert r["mismatches"] == []

    def test_word_heavy_favours_storage(self):
        wl = [("w32", 0, 0x11223344)] + [("r32", 0, None)] * 100
        r = endian.compare(wl)
        assert r["storage_cost"] < r["swap_cost"]

    def test_byte_heavy_favours_swapping(self):
        wl = [("w32", 0, 0x11223344)] + [("r8", 1, None)] * 100
        r = endian.compare(wl)
        assert r["swap_cost"] < r["storage_cost"]
''')

# ---------------------------------------------------------------------- 78
lab(78, "Prune and Trap", module="prune",
    summary="""
    Compute a live function set from a trace, emit trap stubs for the rest,
    and find a function you should not have removed.
    """,
    readme="""
    ## Objective

    Build the pruning from Module 44, made safe by trap stubs.

    ## Background

    The number that drives the whole unit: `wormsrevolution` lifted **88,816**
    functions and reaches **444**. Over 99% of what you compiled never runs.

    Pruning it is the highest-leverage optimisation available -- and it is only
    safe because of `lttp-recompiled`'s pattern: **7,331 stubs plus 833 trap
    stubs** for unresolved targets, so the program links, runs, and tells you
    *which* pruned function actually mattered.

    That converts the risk from "the game crashes mysteriously in chapter four"
    into "the program prints the address of the one function I should not have
    removed."

    ## Your Task

    Implement in `prune.py`:

    - `reachable(entry, call_graph)` -- static reachability.
    - `observed(trace)` -- what actually ran.
    - `live_set(entry, call_graph, trace)` -- the conservative union.
    - `plan(all_functions, live)` -- what to keep, what to trap.
    - `TrapRegistry` -- records which trap fired.

    ## Why the Union

    Static reachability misses anything reached only through an indirect call.
    Traces miss anything the playthrough did not touch. Neither alone is safe;
    their union plus trap stubs is.
    """,
    stub='''
def reachable(entry, call_graph):
    """Statically reachable functions from *entry*.

    Args:
        entry: the entry function name.
        call_graph: dict mapping name -> list of callee names.

    Returns:
        A set including the entry itself. Callees not present in the graph are
        still included -- an unknown callee is still a call.
    """
    # TODO: Work-list traversal from the entry.
    pass


def observed(trace):
    """Functions that actually executed.

    Args:
        trace: list of function names, in execution order, possibly repeated.

    Returns:
        A set of names.
    """
    # TODO: Set of the trace.
    pass


def live_set(entry, call_graph, trace):
    """The conservative union of static reachability and observation.

    Neither source alone is safe: static analysis misses indirect calls, and a
    trace misses whatever the playthrough did not reach.

    Returns:
        A set of names.
    """
    # TODO: Union the two.
    pass


def plan(all_functions, live):
    """Decide what to keep and what to replace with a trap stub.

    Args:
        all_functions: iterable of every function name.
        live: the live set.

    Returns:
        A dict with:
            "keep"      - sorted list of live function names
            "trap"      - sorted list of names to replace with trap stubs
            "kept"      - int
            "trapped"   - int
            "reduction" - trapped / total, 0.0 if there are no functions
    """
    # TODO: Partition and count.
    pass


class TrapRegistry:
    """Records which trap stubs fired, so a bad prune names itself."""

    def __init__(self, trapped):
        self.trapped = set(trapped)
        self.fired = {}

    def call(self, name):
        """A trapped function was called.

        Returns:
            The number of times this trap has now fired.

        Raises:
            KeyError: if *name* was never trapped -- that means the caller and
                the plan disagree, which is worth knowing loudly.
        """
        # TODO: Validate membership, increment and return the count.
        pass

    def report(self):
        """Which traps fired, most frequent first.

        Returns:
            A list of (name, count) tuples, sorted by count descending then
            name ascending.
        """
        # TODO: Sort self.fired.
        pass

    @property
    def clean(self):
        """True if no trap has fired -- the prune looks safe so far."""
        return not self.fired
''',
    test='''
GRAPH = {
    "main": ["init", "loop"],
    "init": ["load"],
    "loop": ["update", "draw"],
    "update": [],
    "draw": [],
    "load": [],
    "debug_dump": ["debug_print"],
    "debug_print": [],
    "vtable_only": [],
}
ALL = list(GRAPH)


class TestReachable:
    def test_from_entry(self):
        r = reach()
        assert "main" in r and "draw" in r

    def test_excludes_unreachable(self):
        assert "debug_dump" not in reach()

    def test_unknown_callee_included(self):
        r = prune.reachable("a", {"a": ["b"]})
        assert "b" in r


def reach():
    r = prune.reachable("main", GRAPH)
    assert r is not None, "reachable() returned None"
    return r


class TestObserved:
    def test_dedupes(self):
        o = prune.observed(["main", "loop", "loop", "draw"])
        assert o == {"main", "loop", "draw"}

    def test_empty(self):
        assert prune.observed([]) == set()


class TestLiveSet:
    def test_union(self):
        # vtable_only is unreachable statically but the trace saw it.
        live = prune.live_set("main", GRAPH, ["vtable_only"])
        assert "vtable_only" in live
        assert "draw" in live

    def test_still_excludes_dead(self):
        assert "debug_dump" not in prune.live_set("main", GRAPH, [])


class TestPlan:
    def test_partitions(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert p is not None, "plan() returned None"
        assert "main" in p["keep"]
        assert "debug_dump" in p["trap"]

    def test_counts(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert p["kept"] + p["trapped"] == len(ALL)

    def test_reduction(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert 0.0 < p["reduction"] < 1.0

    def test_sorted(self):
        p = prune.plan(ALL, prune.live_set("main", GRAPH, []))
        assert p["keep"] == sorted(p["keep"])
        assert p["trap"] == sorted(p["trap"])

    def test_empty(self):
        p = prune.plan([], set())
        assert p["reduction"] == 0.0


class TestTrapRegistry:
    def test_clean_initially(self):
        assert prune.TrapRegistry(["a", "b"]).clean is True

    def test_records_a_bad_prune(self):
        r = prune.TrapRegistry(["debug_dump"])
        assert r.call("debug_dump") == 1
        assert r.clean is False

    def test_counts_repeats(self):
        r = prune.TrapRegistry(["x"])
        r.call("x")
        assert r.call("x") == 2

    def test_unknown_name_raises(self):
        import pytest
        with pytest.raises(KeyError):
            prune.TrapRegistry(["x"]).call("y")

    def test_report_sorted(self):
        r = prune.TrapRegistry(["a", "b"])
        r.call("a")
        r.call("b")
        r.call("b")
        assert r.report() == [("b", 2), ("a", 1)]
''')

# ---------------------------------------------------------------------- 79
lab(79, "Function Ordering", module="ordering",
    summary="""
    Generate a linker ordering file from an execution trace and estimate the
    change in instruction-cache behaviour.
    """,
    readme="""
    ## Objective

    Turn an execution trace into a function layout, and measure what it buys.

    ## Background

    Module 44 section 4. Cheaper than PGO and most of the benefit for the cache
    problem: given functions ranked by call count, the linker lays them out
    contiguously, so hot functions share pages and cache lines instead of being
    scattered through a multi-hundred-megabyte binary.

    And the reuse argument: the trace that feeds this also feeds entry point
    discovery (Module 33), the oracle (Module 38), and liveness (Module 44
    section 1). **One recorded playthrough feeds four different things.**

    ## Your Task

    Implement in `ordering.py`:

    - `call_counts(trace)` -- how often each function ran.
    - `order_by_heat(counts, all_functions)` -- the ordering file.
    - `layout(order, sizes)` -- assign addresses in that order.
    - `estimate_cache_misses(trace, layout, line_size)` -- a simple model.
    - `compare_layouts(...)` -- original versus reordered.

    ## The Model

    The cache model is deliberately crude: count distinct cache lines touched
    by the trace. It is not accurate in absolute terms and it does not need to
    be -- you are comparing two layouts over the same trace, and the crude model
    ranks them correctly.
    """,
    stub='''
from collections import Counter


def call_counts(trace):
    """Count how often each function appears in the trace.

    Returns:
        A dict mapping name -> count.
    """
    # TODO: Counter over the trace, as a plain dict.
    pass


def order_by_heat(counts, all_functions):
    """Produce a linker ordering: hottest first, cold functions after.

    Args:
        counts: name -> call count.
        all_functions: every function name, including ones never called.

    Returns:
        A list of names. Called functions come first, ordered by count
        descending then name ascending; never-called functions follow, sorted
        by name. The tie-break matters: an unstable ordering file produces a
        different binary on every build.
    """
    # TODO: Split into called and uncalled, sort each, concatenate.
    pass


def layout(order, sizes):
    """Assign addresses by laying functions out in *order*, starting at 0.

    Args:
        order: list of names.
        sizes: dict mapping name -> size in bytes.

    Returns:
        A dict mapping name -> start address.

    Raises:
        KeyError: if a name in *order* has no size.
    """
    # TODO: Walk the order, accumulating a cursor.
    pass


def estimate_cache_misses(trace, addresses, sizes, line_size=64):
    """Estimate distinct cache lines touched by the trace.

    For each call in the trace, the function occupies the lines spanning
    [addr, addr + size). Count the distinct lines across the whole trace --
    fewer distinct lines means better locality.

    Returns:
        The number of distinct cache lines.
    """
    # TODO: For each traced call, add every line index it spans to a set.
    pass


def compare_layouts(trace, all_functions, sizes, original_order, line_size=64):
    """Compare the original layout against a heat-ordered one.

    Returns:
        A dict with:
            "original_lines"  - distinct lines under the original order
            "ordered_lines"   - distinct lines under the heat order
            "improvement"     - fraction reduced, 0.0 if no improvement
            "order"           - the heat-ordered function list
    """
    # TODO: Build both layouts, estimate both, and compute the improvement.
    pass
''',
    test='''
SIZES = {"main": 100, "hot": 100, "warm": 100, "cold": 100, "never": 100}
TRACE = ["hot"] * 50 + ["warm"] * 10 + ["main"] * 5 + ["cold"]
ORIGINAL = ["main", "cold", "never", "warm", "hot"]


class TestCallCounts:
    def test_counts(self):
        c = ordering.call_counts(TRACE)
        assert c is not None, "call_counts() returned None"
        assert c["hot"] == 50
        assert c["cold"] == 1

    def test_absent(self):
        assert "never" not in ordering.call_counts(TRACE)

    def test_empty(self):
        assert ordering.call_counts([]) == {}


class TestOrderByHeat:
    def test_hottest_first(self):
        o = ordering.order_by_heat(ordering.call_counts(TRACE), list(SIZES))
        assert o is not None, "order_by_heat() returned None"
        assert o[0] == "hot"

    def test_uncalled_last(self):
        o = ordering.order_by_heat(ordering.call_counts(TRACE), list(SIZES))
        assert o[-1] == "never"

    def test_includes_everything(self):
        o = ordering.order_by_heat(ordering.call_counts(TRACE), list(SIZES))
        assert sorted(o) == sorted(SIZES)

    def test_deterministic(self):
        counts = {"a": 5, "b": 5}
        a = ordering.order_by_heat(counts, ["a", "b"])
        b = ordering.order_by_heat(counts, ["b", "a"])
        assert a == b, "ties must break deterministically or every build differs"


class TestLayout:
    def test_addresses(self):
        lay = ordering.layout(["a", "b"], {"a": 10, "b": 20})
        assert lay is not None, "layout() returned None"
        assert lay["a"] == 0
        assert lay["b"] == 10

    def test_missing_size(self):
        import pytest
        with pytest.raises(KeyError):
            ordering.layout(["a"], {})


class TestCacheEstimate:
    def test_counts_lines(self):
        lay = {"a": 0}
        n = ordering.estimate_cache_misses(["a"], lay, {"a": 64}, line_size=64)
        assert n == 1

    def test_spanning_function(self):
        n = ordering.estimate_cache_misses(["a"], {"a": 0}, {"a": 128}, line_size=64)
        assert n == 2

    def test_distinct_only(self):
        n = ordering.estimate_cache_misses(["a", "a", "a"], {"a": 0},
                                           {"a": 64}, line_size=64)
        assert n == 1


class TestCompare:
    def test_ordering_helps(self):
        r = ordering.compare_layouts(TRACE, list(SIZES), SIZES, ORIGINAL)
        assert r is not None, "compare_layouts() returned None"
        assert r["ordered_lines"] <= r["original_lines"]

    def test_reports_order(self):
        r = ordering.compare_layouts(TRACE, list(SIZES), SIZES, ORIGINAL)
        assert r["order"][0] == "hot"

    def test_improvement_non_negative(self):
        r = ordering.compare_layouts(TRACE, list(SIZES), SIZES, ORIGINAL)
        assert r["improvement"] >= 0.0
''')

report()
