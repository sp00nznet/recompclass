#!/usr/bin/env python3
"""Build the remaining Unit 9 labs (53, 55, 57, 58)."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 53
lab(53, "Table-Driven Lifter Generation", module="isagen",
    summary="""
    Parse a machine-readable ISA description into a decoder table, then
    generate a lifter and a matching interpreter from that one table.
    """,
    readme="""
    ## Objective

    Build the generator from Module 34: an ISA description in, a decoder table
    out, and from that table **both** a lifter and an interpreter.

    ## Background

    Hand-written `switch` trees over 256 opcodes rot. Tables are diffable against
    the ISA manual, and `tirecomp`'s decoder is one row per opcode carrying the
    mnemonic, operand kind, control-flow class and cycles:

    ```c
    /* 0xE8 */ {"RET PE",_NO,BR,0},  {"JP (HL)",_NO,JH,0},  ...
    ```

    **The control-flow class is the load-bearing column.** Your analyser needs
    "is this a branch, a call, a return, or an indirect jump" for every opcode,
    and deriving it from the mnemonic string is how you get a bug on `JP (HL)`
    specifically.

    And Module 34 section 7's design consequence: generate the lifter and the
    interpreter **from the same table**. It is a fraction of the work if you plan
    for it and a rewrite if you do not.

    ## Your Task

    Implement in `isagen.py`:

    - `parse_isa(text)` -- parse the description format below into entries.
    - `build_table(entries)` -- a 256-entry table indexed by opcode, with `None`
      for undefined opcodes.
    - `emit_lifter(table)` -- generate C, one case per opcode.
    - `emit_interpreter(table)` -- generate a Python interpreter from the *same*
      table.
    - `check_coverage(table)` -- which opcodes are undefined.

    ### Description format

    ```
    # opcode | mnemonic | operand | class | cycles | semantics
    0x00 | NOP  | none | normal | 4 | pass
    0x3E | LD_A | imm8 | normal | 8 | a = imm
    0xC3 | JP   | imm16| branch | 16| pc = imm
    0xC9 | RET  | none | return | 16| pc = pop()
    0xE9 | JP_HL| none | indirect | 4 | pc = hl
    ```

    Blank lines and `#` comments are ignored.

    ## Why This Matters

    A lifter and an interpreter that disagree cannot be used to check each other
    (Module 38 section 2). Sharing the table means a decode bug affects both
    identically -- which is a real limitation you must state -- but a *lifting*
    bug shows up immediately.
    """,
    stub='''
# Control-flow classes. Every opcode has exactly one.
CLASSES = {"normal", "branch", "cond_branch", "call", "return", "indirect"}

# Classes that end a basic block.
TERMINATORS = {"branch", "cond_branch", "call", "return", "indirect"}


class Entry:
    """One decoded opcode definition."""

    def __init__(self, opcode, mnemonic, operand, cls, cycles, semantics):
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.operand = operand        # "none", "imm8" or "imm16"
        self.cls = cls
        self.cycles = cycles
        self.semantics = semantics

    @property
    def length(self):
        """Total instruction length in bytes, including the opcode."""
        return 1 + {"none": 0, "imm8": 1, "imm16": 2}[self.operand]

    def __repr__(self):
        return f"Entry(0x{self.opcode:02X}, {self.mnemonic})"


def parse_isa(text):
    """Parse an ISA description into a list of Entry objects.

    Format, one instruction per line, fields separated by "|":

        opcode | mnemonic | operand | class | cycles | semantics

    Blank lines and lines whose first non-space character is "#" are ignored.
    Fields are stripped of surrounding whitespace. The opcode is hex ("0x3E").

    Args:
        text: the description.

    Returns:
        A list of Entry objects, in file order.

    Raises:
        ValueError: on an unknown class, a bad operand kind, or a duplicate
            opcode. Failing loudly here is the point -- a typo in an ISA
            table that silently becomes a wrong instruction is Module 38's
            worst bug class.
    """
    # TODO: Split into lines, skip blanks and comments, split each on "|",
    #       strip fields, validate class against CLASSES and operand against
    #       the length map, reject duplicate opcodes, and build Entry objects.
    pass


def build_table(entries):
    """Build a 256-entry table indexed by opcode.

    Args:
        entries: list of Entry objects.

    Returns:
        A list of length 256, each element an Entry or None.
    """
    # TODO: Allocate [None] * 256 and place each entry at its opcode.
    pass


def check_coverage(table):
    """Report which opcodes are undefined.

    Returns:
        A dict with keys:
            "defined"   - int, how many opcodes have entries
            "undefined" - sorted list of opcode ints with no entry
    """
    # TODO: Count non-None entries; collect the indices of the None ones.
    pass


def emit_lifter(table):
    """Generate C source for a lifter from the table.

    The output is a function containing a switch over the opcode. Each case
    emits the entry's cycle cost, then its semantics, then breaks.

        void lift(uint8_t op, cpu_t *c) {
            switch (op) {
            case 0x00: /* NOP */
                c->cycles += 4;
                pass;
                break;
            ...
            default:
                unknown_opcode(op);
                break;
            }
        }

    Undefined opcodes are not emitted -- they fall to `default`.

    Returns:
        A string of C source.
    """
    # TODO: Build the function text. Iterate opcodes 0..255 in order, skipping
    #       None entries. Include the mnemonic as a comment on each case.
    pass


def emit_interpreter(table):
    """Generate Python source for an interpreter from the SAME table.

    The output defines `def step(op, cpu):` with an if/elif chain mirroring
    the lifter's switch -- same cycle costs, same semantics, same order.

        def step(op, cpu):
            if op == 0x00:  # NOP
                cpu.cycles += 4
            elif ...
            else:
                raise ValueError(f"unknown opcode {op:#04x}")

    Returns:
        A string of Python source.
    """
    # TODO: Same iteration as emit_lifter, different syntax. Use "if" for the
    #       first entry and "elif" thereafter, and end with the else clause.
    pass


def terminators(table):
    """Return the sorted opcodes whose class ends a basic block."""
    return sorted(i for i, e in enumerate(table) if e and e.cls in TERMINATORS)
''',
    test='''
SAMPLE = """
# opcode | mnemonic | operand | class | cycles | semantics
0x00 | NOP   | none  | normal   | 4  | pass
0x3E | LD_A  | imm8  | normal   | 8  | cpu.a = imm
0xC3 | JP    | imm16 | branch   | 16 | cpu.pc = imm
0xC2 | JP_NZ | imm16 | cond_branch | 12 | cpu.pc = imm if not cpu.z else cpu.pc
0xCD | CALL  | imm16 | call     | 24 | cpu.push(cpu.pc); cpu.pc = imm
0xC9 | RET   | none  | return   | 16 | cpu.pc = cpu.pop()
0xE9 | JP_HL | none  | indirect | 4  | cpu.pc = cpu.hl
"""


def parsed():
    e = isagen.parse_isa(SAMPLE)
    assert e is not None, "parse_isa() returned None"
    return e


def table():
    t = isagen.build_table(parsed())
    assert t is not None, "build_table() returned None"
    return t


class TestParse:
    def test_count(self):
        assert len(parsed()) == 7

    def test_skips_comments_and_blanks(self):
        assert all(e.mnemonic != "#" for e in parsed())

    def test_fields(self):
        first = parsed()[0]
        assert first.opcode == 0x00
        assert first.mnemonic == "NOP"
        assert first.operand == "none"
        assert first.cls == "normal"
        assert first.cycles == 4

    def test_strips_whitespace(self):
        assert parsed()[1].mnemonic == "LD_A"

    def test_hex_opcode(self):
        assert parsed()[6].opcode == 0xE9

    def test_rejects_bad_class(self):
        import pytest
        with pytest.raises(ValueError):
            isagen.parse_isa("0x00 | NOP | none | teleport | 4 | pass")

    def test_rejects_bad_operand(self):
        import pytest
        with pytest.raises(ValueError):
            isagen.parse_isa("0x00 | NOP | imm32 | normal | 4 | pass")

    def test_rejects_duplicate_opcode(self):
        import pytest
        with pytest.raises(ValueError):
            isagen.parse_isa("0x00 | NOP | none | normal | 4 | pass\\n"
                             "0x00 | NOP2 | none | normal | 4 | pass")


class TestLength:
    def test_none(self):
        assert parsed()[0].length == 1

    def test_imm8(self):
        assert parsed()[1].length == 2

    def test_imm16(self):
        assert parsed()[2].length == 3


class TestTable:
    def test_size(self):
        assert len(table()) == 256

    def test_placement(self):
        assert table()[0xC3].mnemonic == "JP"

    def test_holes_are_none(self):
        assert table()[0x01] is None


class TestCoverage:
    def test_counts(self):
        c = isagen.check_coverage(table())
        assert c is not None, "check_coverage() returned None"
        assert c["defined"] == 7
        assert len(c["undefined"]) == 249

    def test_undefined_sorted(self):
        u = isagen.check_coverage(table())["undefined"]
        assert u == sorted(u)
        assert 0x01 in u
        assert 0x00 not in u


class TestEmitLifter:
    def test_is_c(self):
        src = isagen.emit_lifter(table())
        assert src is not None, "emit_lifter() returned None"
        assert "switch" in src
        assert "default:" in src

    def test_has_a_case_per_entry(self):
        src = isagen.emit_lifter(table())
        for op in (0x00, 0x3E, 0xC3, 0xE9):
            assert f"case 0x{op:02X}:" in src

    def test_no_case_for_holes(self):
        assert "case 0x01:" not in isagen.emit_lifter(table())

    def test_includes_cycles(self):
        assert "c->cycles += 24;" in isagen.emit_lifter(table())

    def test_mnemonic_in_comment(self):
        assert "JP_HL" in isagen.emit_lifter(table())


class TestEmitInterpreter:
    def test_is_python_and_runs(self):
        src = isagen.emit_interpreter(table())
        assert src is not None, "emit_interpreter() returned None"
        ns = {}
        exec(compile(src, "<generated>", "exec"), ns)
        assert "step" in ns

    def test_dispatches(self):
        ns = {}
        exec(compile(isagen.emit_interpreter(table()), "<gen>", "exec"), ns)

        class Cpu:
            cycles = 0
            a = 0
        cpu = Cpu()
        ns["step"](0x00, cpu)
        assert cpu.cycles == 4

    def test_unknown_opcode_raises(self):
        import pytest
        ns = {}
        exec(compile(isagen.emit_interpreter(table()), "<gen>", "exec"), ns)

        class Cpu:
            cycles = 0
        with pytest.raises(ValueError):
            ns["step"](0x01, Cpu())

    def test_same_cycle_costs_as_lifter(self):
        # The whole point of one table: the two backends cannot disagree.
        c_src = isagen.emit_lifter(table())
        py_src = isagen.emit_interpreter(table())
        for e in parsed():
            assert f"+= {e.cycles};" in c_src
            assert f"+= {e.cycles}" in py_src


class TestTerminators:
    def test_finds_them(self):
        t = isagen.terminators(table())
        assert 0xC3 in t and 0xC9 in t and 0xE9 in t and 0xCD in t

    def test_excludes_normal(self):
        t = isagen.terminators(table())
        assert 0x00 not in t and 0x3E not in t
''')

# ---------------------------------------------------------------------- 55
lab(55, "Synthetic Fixture Suite", module="fixtures",
    summary="""
    Hand-assembled instruction fixtures and golden-output assertions -- the
    highest-value test a recompiler can have, and legally free of the ROM.
    """,
    readme="""
    ## Objective

    Build the fixture suite from Module 35: small, hand-assembled byte sequences
    that exercise the hard cases, with golden assertions on the lifter's exact
    output.

    ## Background

    You cannot commit a game ROM (Module 45). You *can* commit a 64-byte blob of
    hand-assembled instructions that exercises every addressing mode, and assert
    on the exact C your lifter emits for it.

    This is the highest-value test a recompiler can have. It is fast, legal,
    fails loudly on any unintended semantic change, and doubles as documentation
    of what your lifter is supposed to produce. `tirecomp` ships
    `tests/test_decode.c`, `tests/test_rt.c` and `tests/test_tivar.c` for exactly
    this.

    **Build fixtures for the cases you know are hard**, not the easy ones:

    - Flag-setting arithmetic at every width
    - Delay slots, on every architecture that has them
    - Width-sensitive instructions under each mode setting
    - Mode interworking across a mode-switching branch
    - Every control-flow class, so an indirect jump cannot silently become a
      plain branch

    ## Your Task

    Implement in `fixtures.py`:

    - `Fixture` -- a named byte sequence with expected output.
    - `assemble(lines)` -- a tiny assembler so fixtures are readable.
    - `run_fixture(fixture, lifter)` -- lift and compare against the golden text.
    - `run_suite(fixtures, lifter)` -- run all, report failures with diffs.
    - `regenerate(fixtures, lifter)` -- produce updated goldens.

    ## The Trap

    Module 35 section 3: when output legitimately changes, the temptation is to
    regenerate goldens without reading the diff. **Make regeneration explicit and
    reviewable** -- a separate command, output committed as a normal change, and
    the diff read in review. A golden test you rubber-stamp is the CI equivalent
    of a job that cannot fail.
    """,
    stub='''
import difflib

# A tiny assembler vocabulary: mnemonic -> (opcode, operand_bytes)
OPCODES = {
    "nop":   (0x00, 0),
    "ld_a":  (0x3E, 1),
    "add_a": (0x87, 0),
    "jp":    (0xC3, 2),
    "jp_nz": (0xC2, 2),
    "call":  (0xCD, 2),
    "ret":   (0xC9, 0),
    "jp_hl": (0xE9, 0),
}


class Fixture:
    """A named test case: source, assembled bytes, and expected lifter output.

    Attributes:
        name: what this fixture is testing.
        source: list of assembly lines.
        expected: the golden lifter output, or None if not yet recorded.
        why: one line saying why this case is hard. Fixtures without a
             reason tend to be the easy cases nobody needed tested.
    """

    def __init__(self, name, source, expected=None, why=""):
        self.name = name
        self.source = source
        self.expected = expected
        self.why = why


def assemble(lines):
    """Assemble a list of source lines into bytes.

    Each line is a mnemonic optionally followed by a hex operand:

        nop
        ld_a 0x42
        jp 0x1234

    Blank lines and lines starting with ";" are ignored. A 1-byte operand is
    emitted as-is; a 2-byte operand is little-endian.

    Args:
        lines: list of strings.

    Returns:
        A bytes object.

    Raises:
        ValueError: on an unknown mnemonic, or a missing or extra operand.
    """
    # TODO: For each meaningful line, split into mnemonic and optional operand.
    #       Look the mnemonic up in OPCODES to get (opcode, operand_bytes).
    #       Validate that an operand is present exactly when operand_bytes > 0.
    #       Emit the opcode, then the operand little-endian in the right width.
    pass


def run_fixture(fixture, lifter):
    """Run one fixture through *lifter* and compare against its golden text.

    Args:
        fixture: a Fixture.
        lifter: callable(bytes) -> str, the lifter under test.

    Returns:
        A dict with keys:
            "name"     - the fixture name
            "status"   - "pass", "fail", or "no_golden"
            "actual"   - the lifter's output
            "diff"     - unified diff text when status is "fail", else ""

    A fixture with expected=None is "no_golden" -- not a pass. An unrecorded
    golden is an untested fixture, and counting it as a pass is how a suite
    quietly stops testing anything.
    """
    # TODO: Call lifter(assemble(fixture.source)). If fixture.expected is None,
    #       return status "no_golden". Otherwise compare, and on mismatch build
    #       a unified diff with difflib.unified_diff over splitlines().
    pass


def run_suite(fixtures, lifter):
    """Run every fixture and summarise.

    Returns:
        A dict with keys:
            "results"   - list of run_fixture dicts, in input order
            "passed"    - int
            "failed"    - int
            "no_golden" - int
    """
    # TODO: Run each fixture, collect results, count each status.
    pass


def regenerate(fixtures, lifter):
    """Produce updated golden text for every fixture.

    This deliberately does NOT modify the fixtures in place. It returns the
    new goldens so a human can review the diff before committing them.

    Returns:
        A dict mapping fixture name -> new golden text.
    """
    # TODO: Run the lifter over each fixture's assembled bytes and collect
    #       the output by name.
    pass


def format_report(summary):
    """Format a suite summary, with diffs for failures."""
    lines = [f"fixtures: {len(summary['results'])}  "
             f"passed: {summary['passed']}  "
             f"failed: {summary['failed']}  "
             f"no golden: {summary['no_golden']}"]
    for r in summary["results"]:
        if r["status"] == "fail":
            lines.append(f"\\nFAIL {r['name']}")
            lines.append(r["diff"])
        elif r["status"] == "no_golden":
            lines.append(f"\\nNO GOLDEN {r['name']} -- record it or delete it")
    return "\\n".join(lines)
''',
    test='''
def toy_lifter(data):
    """A deterministic reference lifter for testing the harness itself."""
    out = []
    i = 0
    names = {v[0]: (k, v[1]) for k, v in fixtures.OPCODES.items()}
    while i < len(data):
        mnemonic, nops = names[data[i]]
        if nops == 0:
            out.append(f"{i:04X}: {mnemonic}")
        elif nops == 1:
            out.append(f"{i:04X}: {mnemonic} 0x{data[i+1]:02X}")
        else:
            val = data[i + 1] | (data[i + 2] << 8)
            out.append(f"{i:04X}: {mnemonic} 0x{val:04X}")
        i += 1 + nops
    return "\\n".join(out)


class TestAssemble:
    def test_no_operand(self):
        assert fixtures.assemble(["nop"]) == bytes([0x00])

    def test_byte_operand(self):
        assert fixtures.assemble(["ld_a 0x42"]) == bytes([0x3E, 0x42])

    def test_word_operand_little_endian(self):
        assert fixtures.assemble(["jp 0x1234"]) == bytes([0xC3, 0x34, 0x12])

    def test_multiple(self):
        data = fixtures.assemble(["nop", "ret"])
        assert data == bytes([0x00, 0xC9])

    def test_skips_blanks_and_comments(self):
        data = fixtures.assemble(["", "; a comment", "nop"])
        assert data == bytes([0x00])

    def test_unknown_mnemonic(self):
        import pytest
        with pytest.raises(ValueError):
            fixtures.assemble(["frobnicate"])

    def test_missing_operand(self):
        import pytest
        with pytest.raises(ValueError):
            fixtures.assemble(["jp"])

    def test_unexpected_operand(self):
        import pytest
        with pytest.raises(ValueError):
            fixtures.assemble(["nop 0x12"])


class TestRunFixture:
    def test_pass(self):
        f = fixtures.Fixture("nop", ["nop"], expected="0000: nop")
        r = fixtures.run_fixture(f, toy_lifter)
        assert r is not None, "run_fixture() returned None"
        assert r["status"] == "pass"
        assert r["diff"] == ""

    def test_fail_produces_diff(self):
        f = fixtures.Fixture("nop", ["nop"], expected="0000: something else")
        r = fixtures.run_fixture(f, toy_lifter)
        assert r["status"] == "fail"
        assert "nop" in r["diff"]

    def test_no_golden_is_not_a_pass(self):
        f = fixtures.Fixture("nop", ["nop"])
        r = fixtures.run_fixture(f, toy_lifter)
        assert r["status"] == "no_golden"

    def test_records_actual(self):
        f = fixtures.Fixture("jp", ["jp 0x1234"], expected="wrong")
        r = fixtures.run_fixture(f, toy_lifter)
        assert "0x1234" in r["actual"]

    def test_records_name(self):
        f = fixtures.Fixture("my-case", ["nop"], expected="0000: nop")
        assert fixtures.run_fixture(f, toy_lifter)["name"] == "my-case"


class TestRunSuite:
    def suite(self):
        return [
            fixtures.Fixture("ok", ["nop"], expected="0000: nop"),
            fixtures.Fixture("bad", ["ret"], expected="nope"),
            fixtures.Fixture("new", ["nop"]),
        ]

    def test_counts(self):
        s = fixtures.run_suite(self.suite(), toy_lifter)
        assert s is not None, "run_suite() returned None"
        assert s["passed"] == 1
        assert s["failed"] == 1
        assert s["no_golden"] == 1

    def test_results_in_order(self):
        s = fixtures.run_suite(self.suite(), toy_lifter)
        assert [r["name"] for r in s["results"]] == ["ok", "bad", "new"]

    def test_empty_suite(self):
        s = fixtures.run_suite([], toy_lifter)
        assert s["passed"] == 0 and s["failed"] == 0


class TestRegenerate:
    def test_produces_goldens(self):
        fs = [fixtures.Fixture("a", ["nop"]), fixtures.Fixture("b", ["ret"])]
        new = fixtures.regenerate(fs, toy_lifter)
        assert new is not None, "regenerate() returned None"
        assert new["a"] == "0000: nop"
        assert new["b"] == "0000: ret"

    def test_does_not_mutate_fixtures(self):
        fs = [fixtures.Fixture("a", ["nop"])]
        fixtures.regenerate(fs, toy_lifter)
        assert fs[0].expected is None, \\
            "regenerate() must not update fixtures in place -- a human reviews the diff"
''')

# ---------------------------------------------------------------------- 57
lab(57, "Manifest-Driven Pipeline", module="manifest",
    summary="""
    Convert a pipeline driven by command-line flags into one driven by a
    declarative manifest, keeping derived state out of the source file.
    """,
    readme="""
    ## Objective

    Build the manifest layer from Module 36: every decision in one declarative
    file, nothing in your shell history, and derived state kept firmly out.

    ## Background

    A recompilation project accumulates knowledge that cannot be regenerated:
    addresses discovery missed, functions needing hand-written replacements,
    imports with a different stack purge, memory regions that must map
    somewhere specific. **That knowledge is the project.** Everything else
    rebuilds from the input in minutes.

    Look at what the ReXGlue ports commit: `worms_manifest.toml` is 8,431 bytes,
    beside four source files totalling 8.5 KB. The manifest is as large as all
    the hand-written code.

    The rule for what belongs: **if you had to *learn* it, it goes in the file.
    If the tool can read it off the binary, it does not.**

    ## Your Task

    Implement in `manifest.py`:

    - `parse_manifest(text)` -- a small INI-like format (no TOML dependency).
    - `validate(manifest)` -- reject derived state and unknown sections loudly.
    - `hints(manifest)` -- the function-entry hints, with their recorded source.
    - `resolve_overrides(manifest)` -- per-import stack purges and forced modes.
    - `derived_path(manifest, outdir)` -- where derived state goes: **not** in
      the manifest.

    ## The Rule That Matters

    Module 36 section 3: the moment generated content lives in the manifest, the
    diff stops being readable, merges become unresolvable, and you can no longer
    tell a decision from a derivation. `validate()` enforces this -- a manifest
    containing a `[discovered]` section is an error, not a convenience.

    **Comment your hints.** A bare address is worthless in six months.
    "runtime-harvested from a tolerant-dispatch boot" versus "pointer scan" is
    exactly the distinction that decided Module 14's `civrev` bring-up: 301
    scan hints made the build worse, 21 harvested ones fixed it.
    """,
    stub='''
# Sections a manifest may contain. Anything else is an error -- a typo'd
# section name that is silently ignored is a decision that quietly stopped
# applying.
KNOWN_SECTIONS = {"project", "input", "entrypoint", "imports", "memory"}

# Sections that must NEVER appear: these hold derived state, which belongs in
# the output directory as a cache, not in the manifest as a source.
FORBIDDEN_SECTIONS = {"discovered", "cache", "generated", "analysis"}


class ManifestError(Exception):
    """Raised for a manifest that cannot be trusted."""


def parse_manifest(text):
    """Parse an INI-like manifest.

        [project]
        name = worms
        base = 0x82000000

        [entrypoint.functions]
        0x82236F38 = tail-call discovery missed
        0x82E80100 = runtime-harvested (tolerant dispatch boot)

        [imports]
        XUsbcamGetState = purge:8

    Rules:
      - `[section]` starts a section; `[a.b]` is a subsection, stored under the
        key "a.b".
      - `key = value`, both stripped.
      - Blank lines and lines starting with "#" are ignored.
      - A key before any section header is an error.

    Returns:
        A dict mapping section name -> dict of key/value strings, preserving
        insertion order.

    Raises:
        ManifestError: on a key outside a section, or a malformed line.
    """
    # TODO: Walk the lines. Track the current section. Build nested dicts.
    pass


def validate(manifest):
    """Check a parsed manifest, raising on anything untrustworthy.

    Rejects:
      - any section whose top-level name is in FORBIDDEN_SECTIONS
      - any section whose top-level name is not in KNOWN_SECTIONS
      - a missing [project] section, or a [project] without a name

    Returns:
        True if the manifest is valid.

    Raises:
        ManifestError: with a message naming the offending section.
    """
    # TODO: For each section, take the part before any "." as its top-level
    #       name and check it against FORBIDDEN_SECTIONS then KNOWN_SECTIONS.
    #       Then check [project] exists and has a "name".
    pass


def hints(manifest):
    """Extract function-entry hints with their recorded provenance.

    Reads the "entrypoint.functions" section, where each key is a hex address
    and each value is a free-text note saying where the hint came from.

    Returns:
        A list of dicts with keys "addr" (int) and "source" (str), sorted by
        address. Returns [] if the section is absent.

    Raises:
        ManifestError: if a hint has an empty note. An address with no
            recorded provenance is the thing Module 14 warns about -- you
            cannot later tell a runtime-verified hint from a pointer-scan guess.
    """
    # TODO: Read the section, parse each key with int(key, 16), require a
    #       non-empty value, sort by address.
    pass


def resolve_overrides(manifest):
    """Parse the [imports] section into per-import overrides.

    Each value is a comma-separated list of `field:value` pairs:

        XUsbcamGetState = purge:8
        SomeOtherImport = purge:4, mode:stub

    Returns:
        A dict mapping import name -> dict of field -> value, with "purge"
        converted to int. Returns {} if the section is absent.

    Raises:
        ManifestError: on a malformed pair or a non-integer purge.
    """
    # TODO: Split each value on ",", then each item on ":", strip both sides,
    #       and convert purge to int.
    pass


def derived_path(manifest, outdir):
    """Return where derived state for this project should be written.

    Derived state is a cache. It goes in the output directory, named after the
    project, and it is never written back into the manifest.

    Returns:
        A path string: "<outdir>/<project name>.derived.json"
    """
    # TODO: Read the project name and build the path with os.path.join.
    pass
''',
    extra_imports="import os",
    test='''
SAMPLE = """
# worms bring-up
[project]
name = worms
base = 0x82000000

[input]
image = worms.xex

[entrypoint.functions]
0x82236F38 = tail-call discovery missed
0x82E80100 = runtime-harvested (tolerant dispatch boot)
0x82E80104 = runtime-harvested (tolerant dispatch boot)

[imports]
XUsbcamGetState = purge:8
XamLoaderLaunch = purge:4, mode:stub
"""


def m():
    parsed = manifest.parse_manifest(SAMPLE)
    assert parsed is not None, "parse_manifest() returned None"
    return parsed


class TestParse:
    def test_sections(self):
        assert set(m()) >= {"project", "input", "entrypoint.functions", "imports"}

    def test_values(self):
        assert m()["project"]["name"] == "worms"
        assert m()["project"]["base"] == "0x82000000"

    def test_subsection_key(self):
        assert "entrypoint.functions" in m()

    def test_skips_comments(self):
        assert all(not k.startswith("#") for k in m()["project"])

    def test_key_outside_section_is_error(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.parse_manifest("name = orphan")

    def test_malformed_line_is_error(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.parse_manifest("[project]\\nthis line has no equals sign")


class TestValidate:
    def test_accepts_good(self):
        assert manifest.validate(m()) is True

    def test_rejects_derived_state(self):
        import pytest
        bad = manifest.parse_manifest("[project]\\nname = x\\n[discovered]\\na = 1")
        with pytest.raises(manifest.ManifestError) as e:
            manifest.validate(bad)
        assert "discovered" in str(e.value)

    def test_rejects_unknown_section(self):
        import pytest
        bad = manifest.parse_manifest("[project]\\nname = x\\n[wibble]\\na = 1")
        with pytest.raises(manifest.ManifestError):
            manifest.validate(bad)

    def test_requires_project(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.validate(manifest.parse_manifest("[input]\\nimage = a.xex"))

    def test_requires_project_name(self):
        import pytest
        with pytest.raises(manifest.ManifestError):
            manifest.validate(manifest.parse_manifest("[project]\\nbase = 0x1"))


class TestHints:
    def test_count(self):
        h = manifest.hints(m())
        assert h is not None, "hints() returned None"
        assert len(h) == 3

    def test_addresses_are_ints(self):
        assert manifest.hints(m())[0]["addr"] == 0x82236F38

    def test_sorted(self):
        addrs = [x["addr"] for x in manifest.hints(m())]
        assert addrs == sorted(addrs)

    def test_source_recorded(self):
        sources = [x["source"] for x in manifest.hints(m())]
        assert any("runtime-harvested" in s for s in sources)

    def test_absent_section(self):
        assert manifest.hints(manifest.parse_manifest("[project]\\nname = x")) == []

    def test_empty_note_rejected(self):
        import pytest
        bad = manifest.parse_manifest(
            "[project]\\nname = x\\n[entrypoint.functions]\\n0x1000 = ")
        with pytest.raises(manifest.ManifestError):
            manifest.hints(bad)


class TestOverrides:
    def test_single_field(self):
        o = manifest.resolve_overrides(m())
        assert o is not None, "resolve_overrides() returned None"
        assert o["XUsbcamGetState"]["purge"] == 8

    def test_multiple_fields(self):
        o = manifest.resolve_overrides(m())
        assert o["XamLoaderLaunch"]["purge"] == 4
        assert o["XamLoaderLaunch"]["mode"] == "stub"

    def test_absent_section(self):
        assert manifest.resolve_overrides(
            manifest.parse_manifest("[project]\\nname = x")) == {}

    def test_bad_pair(self):
        import pytest
        bad = manifest.parse_manifest("[project]\\nname = x\\n[imports]\\nA = nocolon")
        with pytest.raises(manifest.ManifestError):
            manifest.resolve_overrides(bad)

    def test_bad_purge(self):
        import pytest
        bad = manifest.parse_manifest("[project]\\nname = x\\n[imports]\\nA = purge:many")
        with pytest.raises(manifest.ManifestError):
            manifest.resolve_overrides(bad)


class TestDerivedPath:
    def test_outside_the_manifest(self):
        p = manifest.derived_path(m(), "out")
        assert p is not None, "derived_path() returned None"
        assert "worms" in p
        assert p.endswith(".derived.json")
        assert "manifest" not in p
''')

# ---------------------------------------------------------------------- 58
lab(58, "Variant Build", module="variant",
    summary="""
    Drive two revisions of the same game from two manifests sharing one
    runtime, and report the address deltas between them.
    """,
    readme="""
    ## Objective

    Build the multi-target support from Module 36 section 4: two ROM revisions,
    two manifests, one runtime -- plus a report of how the addresses moved.

    ## Background

    The corpus does this repeatedly. `oracle-recompiled` builds *Oracle of Ages*
    and *Oracle of Seasons* from one monorepo. `Rampage` carries *World Tour*
    (3,736 functions) and *Universal Tour* (4,788) side by side.
    `pokemon-crystal` is *"the second Generation II title attempted with this
    toolchain (after pokemon-gold); same mapper, same recipe."*

    Without a manifest this is a branch you will never merge.

    The interesting part is the **address delta**. Two revisions of one game
    share almost all their code, shifted. If you can compute the shift, you can
    carry symbols, hints and mods from one revision to the other instead of
    rediscovering them -- which is Module 47 section 3's problem, since a mod
    records the revision it targets and breaks on any other.

    ## Your Task

    Implement in `variant.py`:

    - `load_variants(manifests)` -- several manifests sharing one runtime.
    - `common_functions(a, b)` -- functions present in both, matched by name.
    - `compute_deltas(a, b)` -- the address shift per matched function.
    - `dominant_shift(deltas)` -- the most common shift, and how much of the
      binary it covers.
    - `port_hints(hints, shift)` -- carry hints across using that shift.
    - `format_delta_report(...)`.

    ## What the Numbers Mean

    A single dominant shift covering most functions means one revision inserted
    code near the start and everything after moved by a fixed amount -- hints
    port mechanically. **Many small clusters means the revisions genuinely
    diverge**, and porting anything is per-function work. Knowing which you have
    before you start is the point of the lab.
    """,
    stub='''
from collections import Counter


class Variant:
    """One revision of a game.

    Attributes:
        name: revision name, e.g. "rev-a".
        functions: dict mapping function name -> address.
        hints: list of dicts with "addr" and "source" (from Lab 57).
    """

    def __init__(self, name, functions, hints=None):
        self.name = name
        self.functions = functions
        self.hints = hints or []


def load_variants(specs):
    """Build Variant objects from a list of specs.

    Args:
        specs: list of dicts with "name", "functions" and optional "hints".

    Returns:
        A list of Variant objects, in input order.

    Raises:
        ValueError: on a duplicate variant name. Two variants with the same
            name means one silently shadows the other in every report.
    """
    # TODO: Construct Variants, rejecting duplicate names.
    pass


def common_functions(a, b):
    """Return the function names present in both variants.

    Returns:
        A sorted list of names.
    """
    # TODO: Intersect the two function-name sets and sort.
    pass


def compute_deltas(a, b):
    """Compute the address shift for every function present in both.

    The shift for a function is (address in b) - (address in a). It may be
    negative if code was removed.

    Returns:
        A dict mapping function name -> shift (int), for common functions only.
    """
    # TODO: For each common function, subtract a's address from b's.
    pass


def dominant_shift(deltas):
    """Find the most common shift and how much of the binary it explains.

    Returns:
        A dict with keys:
            "shift"    - the most common delta (int), or None if deltas is empty
            "count"    - how many functions have that shift
            "total"    - how many functions were compared
            "coverage" - count / total as a float, 0.0 when total is 0

    When two shifts tie, prefer the one with the smaller absolute value: a
    small shift is the more likely explanation for a revision, and an
    arbitrary tie-break makes the report unstable between runs.
    """
    # TODO: Count the deltas. Pick the most common, tie-breaking on abs(shift).
    pass


def port_hints(hints, shift):
    """Carry hints from one revision to another by applying *shift*.

    Each ported hint keeps its original note but records that it was ported,
    because a ported hint is a *guess* until something confirms it -- exactly
    the distinction Module 14 says decides a bring-up.

    Args:
        hints: list of dicts with "addr" and "source".
        shift: int to add to each address.

    Returns:
        A new list of dicts with the shifted "addr" and a "source" of
        "ported +0xNN from <original source>" (or "-0xNN" when negative).
        The input is not modified.
    """
    # TODO: Build new dicts. Format the shift as a signed hex string.
    pass


def format_delta_report(a, b, deltas, dominant):
    """Format a comparison between two variants."""
    lines = [
        f"=== {a.name} -> {b.name} ===",
        f"  functions in {a.name}: {len(a.functions)}",
        f"  functions in {b.name}: {len(b.functions)}",
        f"  common:               {len(deltas)}",
    ]
    if dominant["shift"] is None:
        lines.append("  no common functions -- these revisions share nothing")
        return "\\n".join(lines)

    sign = "+" if dominant["shift"] >= 0 else "-"
    lines.append(f"  dominant shift:       {sign}0x{abs(dominant['shift']):X} "
                 f"({dominant['count']}/{dominant['total']}, "
                 f"{dominant['coverage'] * 100:.1f}%)")
    if dominant["coverage"] < 0.5:
        lines.append("  NOTE: low coverage -- these revisions genuinely diverge,")
        lines.append("        so porting hints is per-function work.")
    return "\\n".join(lines)
''',
    test='''
def variants():
    return variant.load_variants([
        {"name": "rev-a",
         "functions": {"main": 0x1000, "init": 0x1100, "draw": 0x1200,
                       "only_a": 0x1300},
         "hints": [{"addr": 0x1150, "source": "runtime-harvested"}]},
        {"name": "rev-b",
         "functions": {"main": 0x1040, "init": 0x1140, "draw": 0x1240,
                       "only_b": 0x1340}},
    ])


class TestLoad:
    def test_returns_variants(self):
        v = variants()
        assert v is not None, "load_variants() returned None"
        assert len(v) == 2
        assert v[0].name == "rev-a"

    def test_carries_hints(self):
        assert len(variants()[0].hints) == 1

    def test_rejects_duplicate_names(self):
        import pytest
        with pytest.raises(ValueError):
            variant.load_variants([{"name": "x", "functions": {}},
                                   {"name": "x", "functions": {}}])


class TestCommon:
    def test_finds_shared(self):
        a, b = variants()
        c = variant.common_functions(a, b)
        assert c is not None, "common_functions() returned None"
        assert c == ["draw", "init", "main"]

    def test_excludes_unique(self):
        a, b = variants()
        c = variant.common_functions(a, b)
        assert "only_a" not in c and "only_b" not in c

    def test_no_overlap(self):
        a = variant.Variant("a", {"x": 1})
        b = variant.Variant("b", {"y": 2})
        assert variant.common_functions(a, b) == []


class TestDeltas:
    def test_computes_shift(self):
        a, b = variants()
        d = variant.compute_deltas(a, b)
        assert d is not None, "compute_deltas() returned None"
        assert d["main"] == 0x40

    def test_only_common(self):
        a, b = variants()
        d = variant.compute_deltas(a, b)
        assert set(d) == {"main", "init", "draw"}

    def test_negative_shift(self):
        a = variant.Variant("a", {"f": 0x2000})
        b = variant.Variant("b", {"f": 0x1F00})
        assert variant.compute_deltas(a, b)["f"] == -0x100


class TestDominant:
    def test_uniform(self):
        a, b = variants()
        dom = variant.dominant_shift(variant.compute_deltas(a, b))
        assert dom is not None, "dominant_shift() returned None"
        assert dom["shift"] == 0x40
        assert dom["count"] == 3
        assert dom["total"] == 3
        assert dom["coverage"] == 1.0

    def test_mixed(self):
        deltas = {"a": 0x40, "b": 0x40, "c": 0x40, "d": 0x80}
        dom = variant.dominant_shift(deltas)
        assert dom["shift"] == 0x40
        assert dom["count"] == 3
        assert abs(dom["coverage"] - 0.75) < 1e-9

    def test_empty(self):
        dom = variant.dominant_shift({})
        assert dom["shift"] is None
        assert dom["coverage"] == 0.0

    def test_tie_prefers_smaller_magnitude(self):
        dom = variant.dominant_shift({"a": 0x10, "b": -0x400})
        assert dom["shift"] == 0x10


class TestPortHints:
    def test_shifts_addresses(self):
        hints = [{"addr": 0x1150, "source": "runtime-harvested"}]
        ported = variant.port_hints(hints, 0x40)
        assert ported is not None, "port_hints() returned None"
        assert ported[0]["addr"] == 0x1190

    def test_records_the_port(self):
        hints = [{"addr": 0x1150, "source": "runtime-harvested"}]
        ported = variant.port_hints(hints, 0x40)
        assert "ported" in ported[0]["source"]
        assert "runtime-harvested" in ported[0]["source"]
        assert "0x40" in ported[0]["source"]

    def test_negative_shift_formatting(self):
        ported = variant.port_hints([{"addr": 0x200, "source": "scan"}], -0x20)
        assert ported[0]["addr"] == 0x1E0
        assert "-0x20" in ported[0]["source"]

    def test_does_not_mutate(self):
        hints = [{"addr": 0x1000, "source": "x"}]
        variant.port_hints(hints, 0x10)
        assert hints[0]["addr"] == 0x1000


class TestReport:
    def test_mentions_shift(self):
        a, b = variants()
        deltas = variant.compute_deltas(a, b)
        text = variant.format_delta_report(a, b, deltas,
                                           variant.dominant_shift(deltas))
        assert "0x40" in text

    def test_warns_on_divergence(self):
        a = variant.Variant("a", {"f": 0x100, "g": 0x200, "h": 0x300})
        b = variant.Variant("b", {"f": 0x110, "g": 0x260, "h": 0x390})
        deltas = variant.compute_deltas(a, b)
        text = variant.format_delta_report(a, b, deltas,
                                           variant.dominant_shift(deltas))
        assert "diverge" in text
''')

report()
