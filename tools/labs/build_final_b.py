#!/usr/bin/env python3
"""Build the last labs: 103, 104, 106, 107, 112, 119, 121."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 103
lab(103, "Symbol Importer", module="symimport",
    summary="""
    Convert a decompilation project's symbols into your function-set file,
    record which upstream commit they came from, and report what changed.
    """,
    readme="""
    ## Objective

    Build the importer from Module 51 section 3 -- and make it an importer, not
    a copy.

    ## Background

    Decompilation projects improve continuously. A symbol file you pasted into
    your repository in March is stale in April, and you will not notice.

    ```
    decomp repo --> import script --> your function-set file --> recompiler
      (upstream)      (yours)          (committed)
    ```

    Module 33's provenance rule applies: **record which upstream commit you
    imported from**, or you cannot tell whether an upstream fix has reached you.

    And Module 51 section 7's caution: symbol files are human work in progress.
    A misnamed or mis-sized function propagates straight into your discovery, so
    imported boundaries deserve the same checks as discovered ones.

    ## Your Task

    Implement in `symimport.py`:

    - `parse_symbols(text)` -- the upstream format.
    - `to_function_set(symbols, commit)` -- your format, with provenance.
    - `diff_imports(old, new)` -- what changed since last time.
    - `validate_symbols(symbols)` -- overlaps and zero sizes.

    ## What the Diff Is For

    Running the importer should tell you *what moved*, not just succeed.
    Upstream renaming a function or correcting a size is exactly the kind of
    change that silently invalidates your hints.
    """,
    stub='''
def parse_symbols(text):
    """Parse an upstream symbol file.

    Format, one symbol per line:

        80056780 Player_Init 0x120
        80056900 Player_Update 0x80

    Fields are whitespace-separated: hex address, name, hex size. Blank lines
    and lines starting with "#" are ignored.

    Returns:
        A list of dicts with "addr", "name" and "size", in file order.

    Raises:
        ValueError: on a malformed line. A symbol file you half-parsed is
            worse than one you rejected.
    """
    # TODO: Split lines, skip blanks and comments, split each into three
    #       fields, and parse the two hex numbers.
    pass


def validate_symbols(symbols):
    """Check imported symbols before trusting them.

    Returns:
        A list of problem strings. Empty means they look sane.

    Checks:
      - zero or negative size
      - duplicate addresses
      - overlapping extents (sorted by address, each must end at or before the
        next one starts)
    """
    # TODO: Run the three checks, reporting each problem with its symbol name.
    pass


def to_function_set(symbols, commit):
    """Convert symbols into a function set with provenance.

    Args:
        symbols: output of parse_symbols.
        commit: the upstream commit these came from.

    Returns:
        A dict with:
            "source_commit" - the commit string
            "count"         - how many symbols
            "functions"     - dict mapping name -> {"addr", "size"}

    Raises:
        ValueError: on a duplicate *name*. Two functions with one name means
            one silently shadows the other everywhere downstream.
    """
    # TODO: Build the dict, rejecting duplicate names.
    pass


def diff_imports(old, new):
    """Report what changed between two imports.

    Args:
        old, new: function sets from to_function_set. `old` may be None for a
            first import.

    Returns:
        A dict with:
            "added"    - sorted names only in new
            "removed"  - sorted names only in old
            "moved"    - sorted list of dicts with "name", "from", "to" for
                         functions whose address changed
            "resized"  - sorted list of dicts with "name", "from", "to" for
                         functions whose size changed
            "from_commit" / "to_commit"
    """
    # TODO: Handle old being None as an all-added first import, then compare.
    pass


def format_diff(diff):
    """Format an import diff."""
    lines = [f"import {diff['from_commit'] or '(first)'} -> {diff['to_commit']}"]
    for name in diff["added"]:
        lines.append(f"  + {name}")
    for name in diff["removed"]:
        lines.append(f"  - {name}")
    for m in diff["moved"]:
        lines.append(f"  ~ {m['name']} moved 0x{m['from']:X} -> 0x{m['to']:X}")
    for r in diff["resized"]:
        lines.append(f"  ~ {r['name']} resized 0x{r['from']:X} -> 0x{r['to']:X}")
    return "\\n".join(lines)
''',
    test='''
V1 = """
# upstream symbols
80056780 Player_Init 0x120
800568A0 Player_Update 0x80
80056920 Enemy_Init 0x40
"""

V2 = """
80056780 Player_Init 0x140
800568C0 Player_Update 0x80
80056960 Boss_Init 0x60
"""


class TestParse:
    def test_count(self):
        s = symimport.parse_symbols(V1)
        assert s is not None, "parse_symbols() returned None"
        assert len(s) == 3

    def test_fields(self):
        s = symimport.parse_symbols(V1)
        assert s[0]["addr"] == 0x80056780
        assert s[0]["name"] == "Player_Init"
        assert s[0]["size"] == 0x120

    def test_skips_comments(self):
        assert all(not x["name"].startswith("#") for x in symimport.parse_symbols(V1))

    def test_malformed(self):
        import pytest
        with pytest.raises(ValueError):
            symimport.parse_symbols("80056780 OnlyTwoFields")


class TestValidate:
    def test_clean(self):
        p = symimport.validate_symbols(symimport.parse_symbols(V1))
        assert p is not None, "validate_symbols() returned None"
        assert p == []

    def test_zero_size(self):
        p = symimport.validate_symbols([{"addr": 0x100, "name": "A", "size": 0}])
        assert len(p) == 1 and "A" in p[0]

    def test_duplicate_address(self):
        syms = [{"addr": 0x100, "name": "A", "size": 0x10},
                {"addr": 0x100, "name": "B", "size": 0x10}]
        assert symimport.validate_symbols(syms)

    def test_overlap(self):
        syms = [{"addr": 0x100, "name": "A", "size": 0x100},
                {"addr": 0x180, "name": "B", "size": 0x10}]
        p = symimport.validate_symbols(syms)
        assert any("overlap" in x.lower() for x in p)


class TestToFunctionSet:
    def test_provenance(self):
        fs = symimport.to_function_set(symimport.parse_symbols(V1), "abc123")
        assert fs is not None, "to_function_set() returned None"
        assert fs["source_commit"] == "abc123"
        assert fs["count"] == 3

    def test_lookup(self):
        fs = symimport.to_function_set(symimport.parse_symbols(V1), "abc123")
        assert fs["functions"]["Player_Init"]["addr"] == 0x80056780

    def test_duplicate_name(self):
        import pytest
        syms = [{"addr": 1, "name": "A", "size": 1}, {"addr": 2, "name": "A", "size": 1}]
        with pytest.raises(ValueError):
            symimport.to_function_set(syms, "x")


class TestDiff:
    def sets(self):
        a = symimport.to_function_set(symimport.parse_symbols(V1), "v1")
        b = symimport.to_function_set(symimport.parse_symbols(V2), "v2")
        return a, b

    def test_added_and_removed(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        assert d is not None, "diff_imports() returned None"
        assert d["added"] == ["Boss_Init"]
        assert d["removed"] == ["Enemy_Init"]

    def test_moved(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        moved = {m["name"] for m in d["moved"]}
        assert "Player_Update" in moved

    def test_resized(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        resized = {r["name"]: r for r in d["resized"]}
        assert resized["Player_Init"]["from"] == 0x120
        assert resized["Player_Init"]["to"] == 0x140

    def test_commits_recorded(self):
        a, b = self.sets()
        d = symimport.diff_imports(a, b)
        assert d["from_commit"] == "v1" and d["to_commit"] == "v2"

    def test_first_import(self):
        _, b = self.sets()
        d = symimport.diff_imports(None, b)
        assert len(d["added"]) == 3
        assert d["from_commit"] is None
''')

# ---------------------------------------------------------------------- 104
lab(104, "Matching Decomp as Oracle", module="decomporacle",
    summary="""
    Function-level differential testing against a matching decompilation, with
    honest coverage reporting.
    """,
    readme="""
    ## Objective

    Use a matching decompilation as the specification, and report how much of
    your output it actually covers.

    ## Background

    Module 51 section 5. A fully matching decompilation compiles to a
    byte-identical binary, so **the decomp's C *is* the specification.** Your
    recompiled output should behave identically, and you can compare at function
    granularity with known-correct expected behaviour.

    If your target is one of the N64 or GameCube games with a matching decomp --
    Super Mario 64, Ocarina of Time, Wind Waker, Metroid Prime, Melee -- Module
    38's oracle problem is already solved, and you should build the harness
    before writing a lifter.

    ## Your Task

    Implement in `decomporacle.py`:

    - `compare_function(name, cases, decomp_fn, recomp_fn)` -- one function.
    - `run_suite(...)` -- all of them.
    - `coverage(suite_result, all_functions)` -- how much is actually tested.
    - `honest_report(...)`.

    ## The Coverage Number Is the Point

    A suite that tests 40 of 4,000 functions and passes is not evidence the
    build is correct. `coverage` makes that visible, and `honest_report` refuses
    to describe a low-coverage pass as validation.
    """,
    stub='''
def compare_function(name, cases, decomp_fn, recomp_fn):
    """Differentially test one function against the decomp's version.

    Args:
        name: function name.
        cases: list of argument tuples.
        decomp_fn: the decompiled reference.
        recomp_fn: your recompiled version.

    Returns:
        A dict with:
            "name"      - the function name
            "cases"     - how many cases ran
            "status"    - "pass", "fail" or "error"
            "failures"  - list of dicts with "case", "expected", "actual"
            "message"   - detail for "error"

    A function that raises on some case is "error" -- distinct from a wrong
    answer, because the two send you to different places.
    """
    # TODO: Run both over every case inside a try. Collect mismatches. An
    #       exception from either implementation makes the whole function
    #       "error" with the message.
    pass


def run_suite(suite, decomp, recomp):
    """Run every function in the suite.

    Args:
        suite: dict mapping function name -> list of argument tuples.
        decomp: dict mapping name -> reference callable.
        recomp: dict mapping name -> callable under test.

    Returns:
        A dict with:
            "results"  - list of compare_function dicts, sorted by name
            "passed" / "failed" / "errors" - counts
            "missing"  - sorted names in the suite with no implementation on
                         one side or the other
    """
    # TODO: Skip names missing from either side into "missing"; run the rest.
    pass


def coverage(suite_result, all_functions):
    """How much of the program is actually covered?

    Args:
        suite_result: output of run_suite.
        all_functions: every function in the binary.

    Returns:
        A dict with:
            "tested"   - how many functions the suite exercised
            "total"    - len(all_functions)
            "fraction" - tested / total, 0.0 when total is 0
            "untested" - sorted names with no test
    """
    # TODO: Count the tested names from the results and compare against the
    #       full list.
    pass


def honest_report(suite_result, cov):
    """A report that refuses to describe low coverage as validation.

    Rules:
      - any failures or errors -> "N function(s) diverge from the decomp."
      - all passed and coverage >= 0.8 -> "All N tested functions match the
        decomp (P% coverage)."
      - all passed and coverage < 0.8  -> "All N tested functions match, but
        only P% of the binary is covered -- this is not validation of the
        build."

    Returns:
        A string.
    """
    # TODO: Implement the three cases. Percentages to one decimal place.
    pass
''',
    test='''
def add(a, b):
    return (a + b) & 0xFF


def add_broken(a, b):
    return (a + b) & 0xFFFF      # forgot the mask width


def sub(a, b):
    return (a - b) & 0xFF


def explodes(a, b):
    raise ValueError("unimplemented")


CASES = [(1, 2), (0xFF, 1), (0x80, 0x80)]


class TestCompareFunction:
    def test_pass(self):
        r = decomporacle.compare_function("add", CASES, add, add)
        assert r is not None, "compare_function() returned None"
        assert r["status"] == "pass"
        assert r["cases"] == 3

    def test_fail(self):
        r = decomporacle.compare_function("add", CASES, add, add_broken)
        assert r["status"] == "fail"
        assert len(r["failures"]) >= 1

    def test_failure_detail(self):
        r = decomporacle.compare_function("add", [(0xFF, 1)], add, add_broken)
        f = r["failures"][0]
        assert f["expected"] == 0 and f["actual"] == 0x100

    def test_error(self):
        r = decomporacle.compare_function("add", CASES, add, explodes)
        assert r["status"] == "error"
        assert "unimplemented" in r["message"]


class TestRunSuite:
    def suite(self):
        return {"add": CASES, "sub": CASES}

    def test_all_pass(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": add, "sub": sub})
        assert r is not None, "run_suite() returned None"
        assert r["passed"] == 2 and r["failed"] == 0

    def test_counts_failures(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": add_broken, "sub": sub})
        assert r["failed"] == 1 and r["passed"] == 1

    def test_counts_errors(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": explodes, "sub": sub})
        assert r["errors"] == 1

    def test_missing_implementation(self):
        r = decomporacle.run_suite(self.suite(), {"add": add}, {"add": add})
        assert r["missing"] == ["sub"]

    def test_sorted(self):
        r = decomporacle.run_suite(self.suite(), {"add": add, "sub": sub},
                                   {"add": add, "sub": sub})
        assert [x["name"] for x in r["results"]] == ["add", "sub"]


class TestCoverage:
    def test_fraction(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add", "sub", "mul", "div"])
        assert c is not None, "coverage() returned None"
        assert c["tested"] == 1
        assert abs(c["fraction"] - 0.25) < 1e-9

    def test_untested_listed(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add", "sub"])
        assert c["untested"] == ["sub"]

    def test_empty(self):
        r = decomporacle.run_suite({}, {}, {})
        assert decomporacle.coverage(r, [])["fraction"] == 0.0


class TestHonestReport:
    def test_reports_divergence(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add_broken})
        c = decomporacle.coverage(r, ["add"])
        text = decomporacle.honest_report(r, c)
        assert text is not None, "honest_report() returned None"
        assert "diverge" in text

    def test_high_coverage_pass(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add"])
        assert "match the decomp" in decomporacle.honest_report(r, c)

    def test_low_coverage_is_not_validation(self):
        r = decomporacle.run_suite({"add": CASES}, {"add": add}, {"add": add})
        c = decomporacle.coverage(r, ["add"] + [f"f{i}" for i in range(99)])
        text = decomporacle.honest_report(r, c)
        assert "not validation" in text
''')

# ---------------------------------------------------------------------- 106
lab(106, "Propose and Check", module="proposecheck",
    summary="""
    Take function-boundary proposals from any hypothesis generator and accept
    or reject each one with structural and trace-based checkers.
    """,
    readme="""
    ## Objective

    Build the pipeline Module 52 argues is the only usable shape: a hypothesis
    generator whose output is **mechanically checked**.

    ## Background

    > An ML technique is usable in a recompilation pipeline exactly when its
    > output is **mechanically checkable**. Where it is, the model is a
    > productivity tool and the checker is the source of truth.

    The generator can be anything -- a model, a heuristic, a pointer scan.
    Module 14's `civrev` is the cautionary case: 301 pointer-scan proposals made
    the build *worse*, 21 runtime-harvested ones fixed it. The difference was
    not the generator; it was that one set had been checked against execution.

    ## Your Task

    Implement in `proposecheck.py`:

    - `check_alignment(proposal, alignment)`.
    - `check_in_range(proposal, code_range)`.
    - `check_not_mid_function(proposal, known)` -- the jump-table trap.
    - `check_observed(proposal, trace)` -- the strongest check.
    - `evaluate(proposals, ...)` -- accept, reject with reasons, and rank.

    ## The Check That Caught civrev

    `check_not_mid_function` is the one that matters. A pointer scan cannot tell
    a vtable slot from a switch-table entry, and switch-table entries point into
    the *middle* of functions. Hinting those splits real functions in half.
    """,
    stub='''
def check_alignment(proposal, alignment):
    """Is the proposed address correctly aligned?

    Returns:
        None if fine, otherwise a reason string.
    """
    # TODO: addr % alignment must be 0.
    pass


def check_in_range(proposal, code_range):
    """Is the address inside the code region?

    Args:
        proposal: dict with "addr".
        code_range: (lo, hi) inclusive.

    Returns:
        None if fine, otherwise a reason string.
    """
    # TODO: Inclusive range test.
    pass


def check_not_mid_function(proposal, known):
    """Does this address fall inside a function we already know about?

    This is the check that caught civrev's over-hinting: a switch-table entry
    points into the middle of a real function, and hinting it splits that
    function in half.

    Args:
        proposal: dict with "addr".
        known: list of (start, size) tuples for functions already established.

    Returns:
        None if the address is not interior to any known function, otherwise a
        reason string. An address exactly at a known function's *start* is
        fine -- that is agreement, not a conflict.
    """
    # TODO: For each known function, reject when start < addr < start + size.
    pass


def check_observed(proposal, trace):
    """Did execution actually branch to this address?

    The strongest available evidence: a logged branch target is an observation,
    a pointer-shaped integer is a guess.

    Args:
        proposal: dict with "addr".
        trace: set or list of addresses execution actually reached.

    Returns:
        None if observed, otherwise a reason string. Not being observed is a
        weak signal, not proof of wrongness -- the caller decides how to weigh
        it, which is why this returns a reason rather than a verdict.
    """
    # TODO: Membership test.
    pass


def evaluate(proposals, code_range, known, trace, alignment=4):
    """Run every check over every proposal.

    Args:
        proposals: list of dicts with "addr" and "source".
        code_range: (lo, hi) inclusive.
        known: list of (start, size) tuples.
        trace: observed addresses.
        alignment: required alignment.

    Returns:
        A dict with:
            "accepted"  - proposals passing every hard check, sorted by addr
            "rejected"  - list of dicts with "addr", "source" and "reasons"
            "observed"  - how many accepted proposals were also observed
            "by_source" - dict mapping source -> {"accepted", "rejected"}

    Alignment, range and mid-function are **hard** checks: failing any one
    rejects the proposal. Being unobserved is recorded but does not reject.
    """
    # TODO: Run the three hard checks, collecting reasons. Record the observed
    #       count separately, and tally per source.
    pass


def format_evaluation(result):
    """Format an evaluation, per source."""
    lines = [f"accepted {len(result['accepted'])}, "
             f"rejected {len(result['rejected'])}, "
             f"{result['observed']} of the accepted were observed"]
    for source in sorted(result["by_source"]):
        counts = result["by_source"][source]
        lines.append(f"  {source:24s} +{counts['accepted']} -{counts['rejected']}")
    return "\\n".join(lines)
''',
    test='''
CODE = (0x1000, 0x2000)
KNOWN = [(0x1000, 0x100), (0x1200, 0x80)]
TRACE = {0x1400, 0x1500}


def prop(addr, source="scan"):
    return {"addr": addr, "source": source}


class TestIndividualChecks:
    def test_alignment_ok(self):
        assert proposecheck.check_alignment(prop(0x1004), 4) is None

    def test_alignment_bad(self):
        assert proposecheck.check_alignment(prop(0x1002), 4) is not None

    def test_in_range(self):
        assert proposecheck.check_in_range(prop(0x1500), CODE) is None

    def test_out_of_range(self):
        assert proposecheck.check_in_range(prop(0x9000), CODE) is not None

    def test_mid_function_rejected(self):
        # 0x1050 is inside the function at 0x1000 of size 0x100.
        assert proposecheck.check_not_mid_function(prop(0x1050), KNOWN) is not None

    def test_function_start_is_fine(self):
        assert proposecheck.check_not_mid_function(prop(0x1000), KNOWN) is None

    def test_outside_known_is_fine(self):
        assert proposecheck.check_not_mid_function(prop(0x1400), KNOWN) is None

    def test_observed(self):
        assert proposecheck.check_observed(prop(0x1400), TRACE) is None

    def test_unobserved(self):
        assert proposecheck.check_observed(prop(0x1404), TRACE) is not None


class TestEvaluate:
    def proposals(self):
        return [
            prop(0x1400, "runtime"),      # good and observed
            prop(0x1404, "scan"),         # good, unobserved
            prop(0x1050, "scan"),         # mid-function: the civrev trap
            prop(0x9000, "scan"),         # out of range
            prop(0x1402, "scan"),         # misaligned
        ]

    def result(self):
        r = proposecheck.evaluate(self.proposals(), CODE, KNOWN, TRACE)
        assert r is not None, "evaluate() returned None"
        return r

    def test_accepts_the_good_ones(self):
        addrs = [p["addr"] for p in self.result()["accepted"]]
        assert addrs == [0x1400, 0x1404]

    def test_rejects_mid_function(self):
        rejected = {r["addr"] for r in self.result()["rejected"]}
        assert 0x1050 in rejected

    def test_rejection_gives_reasons(self):
        r = [x for x in self.result()["rejected"] if x["addr"] == 0x1050][0]
        assert any("function" in reason.lower() for reason in r["reasons"])

    def test_unobserved_is_not_rejected(self):
        addrs = [p["addr"] for p in self.result()["accepted"]]
        assert 0x1404 in addrs

    def test_observed_counted(self):
        assert self.result()["observed"] == 1

    def test_by_source(self):
        by = self.result()["by_source"]
        assert by["runtime"]["accepted"] == 1
        assert by["runtime"]["rejected"] == 0
        assert by["scan"]["rejected"] == 3

    def test_the_civrev_lesson(self):
        # Runtime-sourced proposals survive; scan-sourced ones mostly do not.
        by = self.result()["by_source"]
        assert by["runtime"]["rejected"] == 0
        assert by["scan"]["rejected"] > by["scan"]["accepted"]
''')

# ---------------------------------------------------------------------- 107
lab(107, "Equivalence Gate", module="eqgate",
    summary="""
    A gate that accepts candidate implementations only if they behave
    identically to the original, and refuses everything else.
    """,
    readme="""
    ## Objective

    Build the checker from Module 52 section 3 -- the piece that makes any
    hypothesis generator usable.

    ## Background

    ```
    binary --> generator --> candidate C --> compile --> differential test --> accept/reject
                                                              ^
                                                       this is the product
    ```

    The checker is the contribution. Without it you have a plausible-text
    generator pointed at something where plausibility is the failure mode.

    ## Your Task

    Implement in `eqgate.py`:

    - `Gate` -- holds the reference and the test cases.
    - `submit(candidate)` -- accept or reject, with a reason.
    - `stats()` -- acceptance rate and rejection reasons.

    ## What It Must Reject

    A candidate that fails on any case. A candidate that raises. A candidate
    that is *correct on the given cases but wrong on a boundary case the gate
    adds itself* -- because a generator that has seen your test cases will
    happily fit them.

    That last one is why `Gate` owns a set of mandatory probes the submitter
    does not choose.
    """,
    stub='''
class Gate:
    """Accepts a candidate only if it matches the reference on every case.

    Attributes:
        reference: the known-good callable.
        cases: the caller-supplied argument tuples.
        probes: mandatory extra cases the gate always adds. A submitter who
            has seen `cases` can fit them; probes are what catch that.
    """

    def __init__(self, reference, cases, probes=None):
        self.reference = reference
        self.cases = list(cases)
        self.probes = list(probes or [])
        self.accepted = 0
        self.rejected = 0
        self.reasons = {}

    def all_cases(self):
        """Every case a candidate must satisfy: supplied cases plus probes."""
        return self.cases + self.probes

    def submit(self, candidate):
        """Test a candidate against the reference.

        Returns:
            A dict with:
                "accepted" - bool
                "reason"   - "" when accepted, otherwise one of
                             "raised", "mismatch"
                "detail"   - explanation
                "case"     - the first failing case, or None

        A candidate that raises on any case is rejected with "raised" -- an
        exception is not a near miss.

        Records the outcome in self.accepted / self.rejected / self.reasons.
        """
        # TODO: Walk all_cases(). Call the reference and the candidate inside
        #       a try. On an exception from the candidate, reject as "raised".
        #       On a mismatch, reject as "mismatch". Otherwise accept.
        pass

    def stats(self):
        """Return acceptance statistics.

        Returns:
            A dict with "submitted", "accepted", "rejected", "rate"
            (accepted / submitted, 0.0 when none) and "reasons".
        """
        # TODO: Assemble from the counters.
        pass


def make_boundary_probes(width=8):
    """Standard probes for an 8-bit two-operand function.

    Returns:
        A list of (a, b) tuples covering the values where flag and width bugs
        live: 0, 1, the nibble boundary, the signed boundary, and the maximum.
    """
    mask = (1 << width) - 1
    signed = 1 << (width - 1)
    edges = [0, 1, 0x0F, 0x10, signed - 1, signed, mask]
    return [(a, b) for a in edges for b in edges]
''',
    test='''
def ref_add(a, b):
    return (a + b) & 0xFF


def good(a, b):
    return (a + b) % 256


def overfit(a, b):
    # Correct only on the three cases the submitter was shown.
    table = {(1, 2): 3, (2, 3): 5, (3, 4): 7}
    return table.get((a, b), 0)


def raises(a, b):
    raise ValueError("boom")


VISIBLE = [(1, 2), (2, 3), (3, 4)]


class TestGate:
    def gate(self, probes=None):
        return eqgate.Gate(ref_add, VISIBLE, probes)

    def test_accepts_correct(self):
        r = self.gate().submit(good)
        assert r is not None, "submit() returned None"
        assert r["accepted"] is True
        assert r["reason"] == ""

    def test_rejects_wrong(self):
        r = self.gate().submit(lambda a, b: 0)
        assert r["accepted"] is False
        assert r["reason"] == "mismatch"

    def test_rejects_raising(self):
        r = self.gate().submit(raises)
        assert r["reason"] == "raised"
        assert "boom" in r["detail"]

    def test_reports_failing_case(self):
        r = self.gate().submit(lambda a, b: 0)
        assert r["case"] in VISIBLE

    def test_overfit_passes_without_probes(self):
        # The gate is only as strong as its cases.
        assert self.gate().submit(overfit)["accepted"] is True

    def test_probes_catch_overfitting(self):
        g = self.gate(probes=eqgate.make_boundary_probes())
        assert g.submit(overfit)["accepted"] is False

    def test_probes_pass_a_correct_candidate(self):
        g = self.gate(probes=eqgate.make_boundary_probes())
        assert g.submit(good)["accepted"] is True


class TestStats:
    def test_counts(self):
        g = eqgate.Gate(ref_add, VISIBLE)
        g.submit(good)
        g.submit(lambda a, b: 0)
        s = g.stats()
        assert s is not None, "stats() returned None"
        assert s["submitted"] == 2
        assert s["accepted"] == 1
        assert abs(s["rate"] - 0.5) < 1e-9

    def test_reasons_tallied(self):
        g = eqgate.Gate(ref_add, VISIBLE)
        g.submit(raises)
        g.submit(lambda a, b: 0)
        assert g.stats()["reasons"]["raised"] == 1
        assert g.stats()["reasons"]["mismatch"] == 1

    def test_no_submissions(self):
        assert eqgate.Gate(ref_add, VISIBLE).stats()["rate"] == 0.0


class TestProbes:
    def test_covers_boundaries(self):
        probes = eqgate.make_boundary_probes()
        flat = {a for a, _ in probes}
        for v in (0, 1, 0x0F, 0x10, 0x7F, 0x80, 0xFF):
            assert v in flat
''')

# ---------------------------------------------------------------------- 112
lab(112, "Auto-Registration", module="autoreg",
    summary="""
    A self-registering function table where adding a function is one line and
    an override is a link-order question.
    """,
    readme="""
    ## Objective

    Build the ergonomic decision Module 58 section 4 calls the best in the
    corpus, and get the modding hook for free.

    ## Background

    `snesrecomp`'s `recomp_patch.h`:

    ```c
    RECOMP_PATCH(smk_80FF70, 0x80FF70) { ... }
    ```

    > auto-registers it in the snesrecomp dispatch table at its original SNES
    > 24-bit bank:address, before `main()` runs. **No central registration list
    > needed.**

    A central list is a merge conflict on every contribution, a thing to forget,
    and a reason for a newcomer's first patch not to work.

    And the bonus, from Module 47 section 3:

    > **Mod / override pattern:** link a second `.obj` that defines another
    > `RECOMP_PATCH` at the same address with a different function name. **The
    > last constructor to run wins**, so put mod objects after the original.

    ## Your Task

    Implement in `autoreg.py`:

    - `Registry` -- registration, lookup, and override tracking.
    - `register(addr, name, func)` -- last registration wins.
    - `overrides()` -- which addresses were overridden, and by what.
    - `emit_registration(name, addr)` -- the generated C.

    ## Why Track Overrides

    "Last wins" is only usable if you can see it happened. A silent override is
    a debugging session where your breakpoint never fires.
    """,
    stub='''
class Registry:
    """A self-registering function table. Last registration at an address wins."""

    def __init__(self):
        self.table = {}      # addr -> (name, func)
        self.history = {}    # addr -> list of names, in registration order

    def register(self, addr, name, func):
        """Register a function at a guest address.

        A later registration at the same address replaces the earlier one --
        that is the override mechanism, not a bug. Both are recorded in the
        history so the override is visible.

        Returns:
            True if this registration overrode an earlier one, False if it was
            the first at that address.
        """
        # TODO: Record in history, note whether the address was already
        #       occupied, then set the table entry.
        pass

    def lookup(self, addr):
        """Return the callable registered at *addr*, or None."""
        # TODO: Return the function half of the table entry.
        pass

    def name_at(self, addr):
        """Return the name registered at *addr*, or None."""
        # TODO: Return the name half.
        pass

    def overrides(self):
        """Which addresses were overridden?

        Returns:
            A list of dicts with "addr", "active" (the winning name) and
            "shadowed" (the names it replaced, in registration order), sorted
            by address. Addresses registered once are not included.
        """
        # TODO: Walk history for entries with more than one name.
        pass

    def call(self, addr, *args):
        """Dispatch to the registered function.

        Raises:
            KeyError: if nothing is registered at that address.
        """
        func = self.lookup(addr)
        if func is None:
            raise KeyError(f"nothing registered at 0x{addr:X}")
        return func(*args)


def emit_registration(name, addr):
    """Emit the C that makes a function self-register.

    Produces a constructor-attributed registrar so the function is in the table
    before main() runs, with no central list to edit:

        void name(void);
        static void __attribute__((constructor)) register_name(void) {
            recomp_register(0xNNNNNN, "name", name);
        }

    Returns:
        A string of C source.
    """
    # TODO: Build the three lines, formatting the address as six hex digits.
    pass


def emit_link_order_note(registry):
    """Explain the override situation in a form a modder can act on."""
    overrides = registry.overrides() or []
    if not overrides:
        return "No overrides: every address is registered exactly once."
    lines = ["Overrides in effect (last registration wins):"]
    for o in overrides:
        shadowed = ", ".join(o["shadowed"])
        lines.append(f"  0x{o['addr']:06X}: {o['active']} (shadows {shadowed})")
    return "\\n".join(lines)
''',
    test='''
def f_original():
    return "original"


def f_mod():
    return "mod"


def f_other():
    return "other"


class TestRegistry:
    def test_first_registration(self):
        r = autoreg.Registry()
        first = r.register(0x80FF70, "smk_80FF70", f_original)
        assert first is False, "the first registration is not an override"
        assert r.lookup(0x80FF70) is f_original

    def test_override_reported(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "smk_80FF70", f_original)
        assert r.register(0x80FF70, "mod_80FF70", f_mod) is True

    def test_last_wins(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "smk_80FF70", f_original)
        r.register(0x80FF70, "mod_80FF70", f_mod)
        assert r.call(0x80FF70) == "mod"

    def test_name_tracked(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "smk_80FF70", f_original)
        assert r.name_at(0x80FF70) == "smk_80FF70"

    def test_unregistered(self):
        assert autoreg.Registry().lookup(0x1234) is None

    def test_call_unregistered_raises(self):
        import pytest
        with pytest.raises(KeyError):
            autoreg.Registry().call(0x1234)

    def test_independent_addresses(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        r.register(0x200, "b", f_other)
        assert r.call(0x100) == "original"
        assert r.call(0x200) == "other"


class TestOverrides:
    def test_none_initially(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        o = r.overrides()
        assert o is not None, "overrides() returned None"
        assert o == []

    def test_records_shadowed(self):
        r = autoreg.Registry()
        r.register(0x100, "original", f_original)
        r.register(0x100, "mod", f_mod)
        o = r.overrides()
        assert len(o) == 1
        assert o[0]["active"] == "mod"
        assert o[0]["shadowed"] == ["original"]

    def test_chain(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        r.register(0x100, "b", f_mod)
        r.register(0x100, "c", f_other)
        o = r.overrides()[0]
        assert o["active"] == "c"
        assert o["shadowed"] == ["a", "b"]

    def test_sorted(self):
        r = autoreg.Registry()
        for addr in (0x300, 0x100):
            r.register(addr, "a", f_original)
            r.register(addr, "b", f_mod)
        assert [o["addr"] for o in r.overrides()] == [0x100, 0x300]

    def test_note_is_actionable(self):
        r = autoreg.Registry()
        r.register(0x80FF70, "original", f_original)
        r.register(0x80FF70, "mod", f_mod)
        note = autoreg.emit_link_order_note(r)
        assert "mod" in note and "original" in note

    def test_note_when_clean(self):
        r = autoreg.Registry()
        r.register(0x100, "a", f_original)
        assert "No overrides" in autoreg.emit_link_order_note(r)


class TestEmitRegistration:
    def test_has_constructor(self):
        src = autoreg.emit_registration("smk_80FF70", 0x80FF70)
        assert src is not None, "emit_registration() returned None"
        assert "constructor" in src

    def test_mentions_address_and_name(self):
        src = autoreg.emit_registration("smk_80FF70", 0x80FF70)
        assert "0x80FF70" in src
        assert "smk_80FF70" in src

    def test_no_central_list(self):
        src = autoreg.emit_registration("smk_80FF70", 0x80FF70)
        assert "table[" not in src
''')

# ---------------------------------------------------------------------- 119
lab(119, "Verified Lifting Rules", module="verifylift",
    summary="""
    Prove a lifting rule correct over its entire input space, and find what
    a sampled differential test missed.
    """,
    readme="""
    ## Objective

    Do what Module 61 section 3 says nobody has done properly: **prove** a
    lifting rule rather than sampling it.

    ## Background

    > A differential test over a million instructions found a real bug in
    > `tamarecomp` at instruction 1,486. It cannot tell you there is not another
    > at ten million.

    For *instruction lifting rules* the input space is often small enough to
    enumerate outright. An 8-bit two-operand ALU op has 65,536 inputs, times a
    few flag states. That is not a sampling problem; it is a loop.

    > the payoff is permanent: a verified rule never needs retesting.

    ## Your Task

    Implement in `verifylift.py`:

    - `exhaustive_verify(reference, candidate, width, arity)` -- every input.
    - `sampled_verify(...)` -- the usual approach, for comparison.
    - `compare_approaches(...)` -- what sampling missed.

    ## The Result to Report

    Construct a rule that is wrong on a *single* input pair, and show that
    sampling misses it while exhaustive verification finds it every time. That
    contrast is the argument for the technique.
    """,
    stub='''
import itertools
import random


def exhaustive_verify(reference, candidate, width=8, arity=2, flag_states=(False,)):
    """Check *candidate* against *reference* over the entire input space.

    Args:
        reference: known-good callable(*operands, flag) -> result.
        candidate: the implementation under test, same signature.
        width: operand width in bits.
        arity: number of operands.
        flag_states: incoming flag values to try.

    Returns:
        A dict with:
            "verified"   - bool, True only if every input matched
            "checked"    - how many input combinations were tested
            "first_bad"  - the first failing (operands..., flag) tuple, or None
            "expected" / "actual" - values at that input, or None

    Stops at the first failure: once a rule is wrong, it is wrong.
    """
    # TODO: itertools.product over range(1 << width) repeated `arity` times,
    #       crossed with flag_states. Compare, counting as you go.
    pass


def sampled_verify(reference, candidate, width=8, arity=2, trials=10000,
                   seed=0, flag_states=(False,)):
    """Check a random sample -- the usual approach.

    Returns:
        The same shape as exhaustive_verify, plus "seed".
    """
    # TODO: Seed a random.Random, draw `trials` random input tuples, compare.
    pass


def compare_approaches(reference, candidate, width=8, arity=2, trials=10000,
                       seed=0):
    """Run both and report what sampling missed.

    Returns:
        A dict with:
            "exhaustive"  - the exhaustive result
            "sampled"     - the sampled result
            "missed"      - True if sampling passed while exhaustive failed
            "space_size"  - total inputs in the space
            "sampled_fraction" - trials / space_size, capped at 1.0
    """
    # TODO: Run both, compare their verdicts, and compute the coverage.
    pass
''',
    test='''
def ref_add(a, b, flag=False):
    total = a + b + (1 if flag else 0)
    return {"result": total & 0xFF, "carry": total > 0xFF,
            "half": (a & 0xF) + (b & 0xF) + (1 if flag else 0) > 0xF}


def good_add(a, b, flag=False):
    carry_in = 1 if flag else 0
    total = a + b + carry_in
    return {"result": total % 256, "carry": total >= 256,
            "half": ((a & 0xF) + (b & 0xF) + carry_in) >= 16}


def one_bad_input(a, b, flag=False):
    # Wrong for exactly one pair out of 65,536.
    d = ref_add(a, b, flag)
    if a == 0x7F and b == 0x01:
        d = dict(d, half=not d["half"])
    return d


class TestExhaustive:
    def test_verifies_correct(self):
        r = verifylift.exhaustive_verify(ref_add, good_add, width=4)
        assert r is not None, "exhaustive_verify() returned None"
        assert r["verified"] is True
        assert r["checked"] == 256

    def test_finds_the_single_bad_input(self):
        r = verifylift.exhaustive_verify(ref_add, one_bad_input, width=8)
        assert r["verified"] is False
        assert r["first_bad"][:2] == (0x7F, 0x01)

    def test_reports_values(self):
        r = verifylift.exhaustive_verify(ref_add, one_bad_input, width=8)
        assert r["expected"] != r["actual"]

    def test_flag_states(self):
        r = verifylift.exhaustive_verify(ref_add, good_add, width=4,
                                         flag_states=(False, True))
        assert r["checked"] == 512

    def test_arity_one(self):
        inc = lambda a, flag=False: {"result": (a + 1) & 0xFF}
        r = verifylift.exhaustive_verify(inc, inc, width=8, arity=1)
        assert r["verified"] is True
        assert r["checked"] == 256


class TestSampled:
    def test_passes_correct(self):
        r = verifylift.sampled_verify(ref_add, good_add, trials=1000, seed=1)
        assert r is not None, "sampled_verify() returned None"
        assert r["verified"] is True

    def test_deterministic(self):
        a = verifylift.sampled_verify(ref_add, one_bad_input, trials=500, seed=7)
        b = verifylift.sampled_verify(ref_add, one_bad_input, trials=500, seed=7)
        assert a["first_bad"] == b["first_bad"]

    def test_records_seed(self):
        assert verifylift.sampled_verify(ref_add, good_add, trials=10, seed=3)["seed"] == 3


class TestCompare:
    def test_sampling_misses_the_needle(self):
        r = verifylift.compare_approaches(ref_add, one_bad_input,
                                          trials=1000, seed=1)
        assert r is not None, "compare_approaches() returned None"
        assert r["exhaustive"]["verified"] is False
        assert r["missed"] is True

    def test_space_size(self):
        r = verifylift.compare_approaches(ref_add, good_add, trials=10, seed=1)
        assert r["space_size"] == 65536

    def test_sampled_fraction(self):
        r = verifylift.compare_approaches(ref_add, good_add, trials=6554, seed=1)
        assert abs(r["sampled_fraction"] - 0.1) < 0.01

    def test_no_miss_when_both_pass(self):
        r = verifylift.compare_approaches(ref_add, good_add, trials=100, seed=1)
        assert r["missed"] is False
''')

# ---------------------------------------------------------------------- 121
lab(121, "Harness Validation", module="harnessval",
    summary="""
    Inject known bugs into a measurement harness and confirm it detects each
    one -- because a check that cannot fail is not a check.
    """,
    readme="""
    ## Objective

    Prove your measurement works before you trust what it measures.

    ## Background

    Module 62 section 5: **expect your harness to be the bug.** `tamarecomp`'s
    validation hit two before the real one, each looking exactly like a CPU bug.

    And Module 35 section 1's rule, from a real defect in this repository: a CI
    job that ran `python test_lab.py` passed for months and tested nothing.

    > **A CI step that cannot fail is worse than no CI step**, because it
    > converts "untested" into "tested" in every reader's head, including yours.

    So: before believing a clean run, **inject a bug you understand and confirm
    the harness goes red.**

    ## Your Task

    Implement in `harnessval.py`:

    - `Mutation` -- a named, reversible defect.
    - `validate_harness(harness, subject, mutations)` -- inject each, check.
    - `report(results)` -- which mutations were caught, which escaped.

    ## The Finding

    A mutation the harness does **not** catch is the result. It tells you
    precisely which class of bug your measurement is blind to -- and Module 62
    section 6 says a negative result is a result.
    """,
    stub='''
class Mutation:
    """A named defect that can be applied to a subject and undone.

    Attributes:
        name: what this mutation breaks.
        apply: callable(subject) -> mutated subject.
        should_detect: whether a competent harness ought to catch it. A
            mutation marked False is a control -- if the harness "catches" it,
            the harness is reporting noise.
    """

    def __init__(self, name, apply, should_detect=True):
        self.name = name
        self.apply = apply
        self.should_detect = should_detect


def validate_harness(harness, subject, mutations):
    """Inject each mutation and check whether the harness notices.

    Args:
        harness: callable(subject) -> bool, True when the subject looks healthy.
        subject: the unmutated subject.
        mutations: list of Mutation.

    Returns:
        A dict with:
            "baseline"  - bool, did the harness pass the unmutated subject?
            "results"   - list of dicts with "name", "detected",
                          "should_detect" and "outcome"
            "caught"    - how many should-detect mutations were caught
            "escaped"   - sorted names of should-detect mutations that were not
            "false_alarms" - sorted names of control mutations wrongly flagged

    "outcome" is one of:
        "caught"      - should detect, and did
        "escaped"     - should detect, did not          <- the finding
        "correctly_ignored" - should not detect, did not
        "false_alarm" - should not detect, but did

    If the baseline fails, the harness is broken before any mutation and the
    rest of the results mean nothing -- report the baseline first.
    """
    # TODO: Run the harness on the unmutated subject for the baseline, then on
    #       each mutated copy, classifying by the table above.
    pass


def report(result):
    """Format a harness validation."""
    lines = []
    if not result["baseline"]:
        lines.append("BASELINE FAILED: the harness rejects a healthy subject. "
                     "Nothing below is meaningful.")
    lines.append(f"caught {result['caught']} of "
                 f"{result['caught'] + len(result['escaped'])} "
                 f"detectable mutation(s)")
    for name in result["escaped"]:
        lines.append(f"  ESCAPED: {name} -- the harness is blind to this")
    for name in result["false_alarms"]:
        lines.append(f"  FALSE ALARM: {name} -- the harness flags healthy code")
    return "\\n".join(lines)
''',
    test='''
# The subject is a small "build": a dict describing a recompiled program.
def subject():
    return {"functions": 100, "checksum": 0xABCD, "fallbacks": 0, "comment": "ok"}


def strict_harness(s):
    """Healthy when the checksum matches and nothing fell back."""
    return s["checksum"] == 0xABCD and s["fallbacks"] == 0


def vacuous_harness(s):
    """The Module 35 bug: always passes."""
    return True


MUTATIONS = [
    harnessval.Mutation("corrupt_checksum",
                        lambda s: dict(s, checksum=0x1234)),
    harnessval.Mutation("silent_fallbacks",
                        lambda s: dict(s, fallbacks=37)),
    harnessval.Mutation("cosmetic_comment",
                        lambda s: dict(s, comment="changed"),
                        should_detect=False),
]


class TestValidateHarness:
    def test_baseline(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        assert r is not None, "validate_harness() returned None"
        assert r["baseline"] is True

    def test_catches_real_defects(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        assert r["caught"] == 2
        assert r["escaped"] == []

    def test_control_correctly_ignored(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        outcomes = {x["name"]: x["outcome"] for x in r["results"]}
        assert outcomes["cosmetic_comment"] == "correctly_ignored"

    def test_vacuous_harness_exposed(self):
        r = harnessval.validate_harness(vacuous_harness, subject(), MUTATIONS)
        assert r["caught"] == 0
        assert r["escaped"] == ["corrupt_checksum", "silent_fallbacks"]

    def test_false_alarm_detected(self):
        paranoid = lambda s: s["comment"] == "ok" and strict_harness(s)
        r = harnessval.validate_harness(paranoid, subject(), MUTATIONS)
        assert r["false_alarms"] == ["cosmetic_comment"]

    def test_broken_baseline_reported(self):
        r = harnessval.validate_harness(lambda s: False, subject(), MUTATIONS)
        assert r["baseline"] is False

    def test_results_have_all_fields(self):
        r = harnessval.validate_harness(strict_harness, subject(), MUTATIONS)
        for x in r["results"]:
            assert set(x) == {"name", "detected", "should_detect", "outcome"}

    def test_subject_not_mutated_in_place(self):
        s = subject()
        harnessval.validate_harness(strict_harness, s, MUTATIONS)
        assert s["checksum"] == 0xABCD


class TestReport:
    def test_names_escapes(self):
        r = harnessval.validate_harness(vacuous_harness, subject(), MUTATIONS)
        text = harnessval.report(r)
        assert "ESCAPED" in text
        assert "corrupt_checksum" in text

    def test_flags_broken_baseline(self):
        r = harnessval.validate_harness(lambda s: False, subject(), MUTATIONS)
        assert "BASELINE FAILED" in harnessval.report(r)
''')

report()
