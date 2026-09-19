#!/usr/bin/env python3
"""Build the Unit 14 code labs (87-95)."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 87
lab(87, "Whole-ROM Emitter", module="wholerom",
    summary="""
    Emit an entire address space as one C function with a label per
    instruction, falling through on sequential code.
    """,
    readme="""
    ## Objective

    Build Module 53's codegen strategy: not one C function per guest function,
    but **one C function, thousands of labels**.

    ## Background

    From `tamarecomp`'s header:

    > The recompiled ROM is one C function with a label per instruction word, so
    > this holds only the architectural state -- there is no instruction pointer
    > to maintain except at a computed transfer.

    The emitter reports `47567 lines from 6144 ROM words`, and:

    - **Sequential instructions fall through with no branch at all.**
    - **Direct jumps are `goto`.**
    - Function boundaries -- Module 34's recurring nightmare -- are never needed,
      because you never emit a function.

    This works when the whole address space fits in one C function your compiler
    will accept. Right for small embedded targets and arcade boards; wrong for
    anything Module 34 sized.

    ## Your Task

    Implement in `wholerom.py`:

    - `emit_label(addr)` / `emit_instruction(...)`.
    - `emit_rom(program)` -- the whole function.
    - `count_gotos(source)` -- how many transfers survived as branches.
    - `reachable_labels(program)` -- which labels anything targets.

    ## What to Notice

    Most labels are never targeted. Emitting them all is wasteful but harmless,
    and `reachable_labels` tells you how many you could drop -- which is the
    same liveness question as Module 44, at instruction granularity.
    """,
    stub='''
# An instruction is a dict:
#   {"addr": int, "mnemonic": str, "cycles": int,
#    "kind": "normal" | "jump" | "call" | "return",
#    "target": int or None}


def emit_label(addr):
    """Return the C label for *addr*, e.g. "L_0546"."""
    # TODO: Format as L_ plus four uppercase hex digits.
    pass


def emit_instruction(insn):
    """Emit the C for one instruction, without its label.

    Every instruction accumulates its cycle cost. Then:

      normal  -> nothing further
      jump    -> "goto L_XXXX;"
      call    -> "push_return(0xNNNN);" then "goto L_XXXX;" where the pushed
                 address is the instruction AFTER this one (addr + 1)
      return  -> "goto *pop_return();"

    Returns:
        A list of C statement strings, already indented four spaces.
    """
    # TODO: Build the list. Start with the cycles line, then the kind-specific
    #       statements.
    pass


def emit_rom(program):
    """Emit the whole ROM as a single C function.

    Structure:

        void run_rom(cpu_t *c) {
        L_0000: /* NOP */
            c->cycles += 4;
        L_0001: /* JP 0x0010 */
            c->cycles += 12;
            goto L_0010;
        ...
        }

    Sequential instructions simply fall through -- no dispatch, no branch.

    Args:
        program: list of instruction dicts, sorted by address.

    Returns:
        A string of C source.
    """
    # TODO: Open the function, emit a label and body per instruction with the
    #       mnemonic as a comment, then close.
    pass


def count_gotos(source):
    """Count `goto` statements in emitted source.

    Returns:
        An int. Computed transfers (`goto *`) count too -- they are still
        transfers, just not resolvable ones.
    """
    # TODO: Count occurrences of "goto".
    pass


def reachable_labels(program):
    """Which labels are actually targeted by something?

    A label is reachable-by-branch if some instruction jumps or calls to it.
    Fallthrough does not count: the point is to find labels that could be
    dropped entirely.

    Returns:
        A sorted list of addresses.
    """
    # TODO: Collect every non-None target from jump and call instructions.
    pass


def label_savings(program):
    """How many labels could be dropped?

    Returns:
        A dict with "total", "targeted" and "droppable".
    """
    total = len(program)
    targeted = len(reachable_labels(program) or [])
    return {"total": total, "targeted": targeted, "droppable": total - targeted}
''',
    test='''
PROGRAM = [
    {"addr": 0x0000, "mnemonic": "NOP", "cycles": 4, "kind": "normal", "target": None},
    {"addr": 0x0001, "mnemonic": "ADD", "cycles": 7, "kind": "normal", "target": None},
    {"addr": 0x0002, "mnemonic": "JP 0x0005", "cycles": 12, "kind": "jump", "target": 0x0005},
    {"addr": 0x0003, "mnemonic": "CALL 0x0006", "cycles": 14, "kind": "call", "target": 0x0006},
    {"addr": 0x0004, "mnemonic": "RET", "cycles": 10, "kind": "return", "target": None},
    {"addr": 0x0005, "mnemonic": "NOP", "cycles": 4, "kind": "normal", "target": None},
    {"addr": 0x0006, "mnemonic": "NOP", "cycles": 4, "kind": "normal", "target": None},
]


class TestLabel:
    def test_format(self):
        assert wholerom.emit_label(0x546) == "L_0546"

    def test_uppercase(self):
        assert wholerom.emit_label(0xABC) == "L_0ABC"


class TestEmitInstruction:
    def test_normal_only_cycles(self):
        out = wholerom.emit_instruction(PROGRAM[0])
        assert out is not None, "emit_instruction() returned None"
        assert len(out) == 1
        assert "cycles" in out[0]

    def test_jump_emits_goto(self):
        out = wholerom.emit_instruction(PROGRAM[2])
        assert any("goto L_0005;" in line for line in out)

    def test_call_pushes_next_address(self):
        out = wholerom.emit_instruction(PROGRAM[3])
        joined = "".join(out)
        assert "0x0004" in joined
        assert "goto L_0006;" in joined

    def test_return_is_computed(self):
        out = wholerom.emit_instruction(PROGRAM[4])
        assert any("goto *" in line for line in out)

    def test_indented(self):
        out = wholerom.emit_instruction(PROGRAM[0])
        assert out[0].startswith("    ")


class TestEmitRom:
    def test_is_one_function(self):
        src = wholerom.emit_rom(PROGRAM)
        assert src is not None, "emit_rom() returned None"
        assert src.count("void run_rom") == 1

    def test_label_per_instruction(self):
        src = wholerom.emit_rom(PROGRAM)
        for insn in PROGRAM:
            assert f"L_{insn['addr']:04X}:" in src

    def test_sequential_falls_through(self):
        # Two adjacent normal instructions must have no branch between them.
        src = wholerom.emit_rom(PROGRAM)
        between = src.split("L_0000:")[1].split("L_0001:")[0]
        assert "goto" not in between

    def test_mnemonic_as_comment(self):
        assert "NOP" in wholerom.emit_rom(PROGRAM)


class TestCountGotos:
    def test_counts(self):
        src = wholerom.emit_rom(PROGRAM)
        n = wholerom.count_gotos(src)
        assert n is not None, "count_gotos() returned None"
        assert n == 3      # jump, call, return

    def test_zero(self):
        assert wholerom.count_gotos("no branches here") == 0


class TestReachable:
    def test_targets(self):
        r = wholerom.reachable_labels(PROGRAM)
        assert r is not None, "reachable_labels() returned None"
        assert r == [0x0005, 0x0006]

    def test_fallthrough_not_counted(self):
        assert 0x0001 not in wholerom.reachable_labels(PROGRAM)

    def test_savings(self):
        s = wholerom.label_savings(PROGRAM)
        assert s["total"] == 7
        assert s["targeted"] == 2
        assert s["droppable"] == 5
''')

# ---------------------------------------------------------------------- 88
lab(88, "Fold a Paging Instruction", module="paging",
    summary="""
    Statically track a paged architecture's latched page so the paging
    instruction emits nothing at all -- and assert the invariant that allows it.
    """,
    readme="""
    ## Objective

    Make 162 instructions disappear at compile time, and prove you were allowed
    to.

    ## Background

    Module 53 section 4. The E0C6200 reaches its address space through `PSET`,
    which latches a page that the *following* jump or call consumes. Normally a
    recompiler's problem -- the target depends on runtime state.

    Except the page is always an immediate. So:

    > **`PSET` emits nothing at all** -- all 162 of them stop being control flow
    > and become compile-time facts.

    And the subtlety worth reading twice:

    > Not even its one-instruction interrupt hold-off survives: that exists to
    > keep an interrupt out of the gap between a `PSET` and the jump consuming
    > the page it latched, and **generated code has no interrupt point there**.

    You are allowed to drop it *provided* the assumption holds -- which is why
    *"every reachable `PSET` in this ROM is immediately followed by a control
    transfer, which the test suite asserts."*

    ## Your Task

    Implement in `paging.py`:

    - `resolve_targets(program)` -- fold each `PSET` into the transfer after it.
    - `check_pset_invariant(program)` -- is every `PSET` followed by a transfer?
    - `emit(program)` -- generate code, emitting nothing for `PSET`.
    - `folding_report(program)`.

    ## The Rule

    **An assumption that enables an optimisation must be asserted, not
    remembered.** `check_pset_invariant` is not optional politeness; it is what
    makes the fold sound.
    """,
    stub='''
class PagingError(Exception):
    """Raised when the folding assumption does not hold."""


def resolve_targets(program):
    """Fold each PSET's page into the transfer instruction that follows it.

    An instruction is a dict:
        {"addr": int, "op": "PSET"|"JP"|"CALL"|"NOP"|...,
         "page": int or None, "offset": int or None}

    A transfer's absolute target is `(latched_page << 8) | offset`.

    Args:
        program: list of instruction dicts, in address order.

    Returns:
        A new list where every transfer has an added "target" key holding its
        resolved absolute address, and non-transfers have "target": None.
        PSET instructions are left in place -- emit() decides to drop them.

    Raises:
        PagingError: if a transfer is reached with no page ever latched. That
            is a genuinely unresolvable target, not something to guess at.
    """
    # TODO: Walk the program carrying the latched page. On PSET, update it.
    #       On JP/CALL, compute the target. Raise if no page has been latched.
    pass


def check_pset_invariant(program):
    """Is every PSET immediately followed by a control transfer?

    This is the assumption that lets PSET be folded away entirely, including
    its interrupt hold-off.

    Returns:
        A list of addresses of PSET instructions that are NOT followed by a
        transfer, sorted. Empty means the fold is sound.
    """
    # TODO: For each PSET, look at the next instruction in the list.
    #       A PSET as the final instruction is also a violation.
    pass


def emit(program):
    """Emit C, dropping PSET entirely.

    Every instruction still gets a label, so a computed transfer can reach it.
    A PSET's body is empty -- a comment recording what was folded, nothing else.

    Returns:
        A list of source lines.

    Raises:
        PagingError: if the invariant does not hold. Emitting a fold whose
            precondition is unchecked is how a silent bug ships.
    """
    # TODO: Call check_pset_invariant first and raise if it reports anything.
    #       Then resolve targets and emit: label, comment, and for transfers a
    #       goto to the resolved label.
    pass


def folding_report(program):
    """Summarise what folding achieved.

    Returns:
        A dict with:
            "instructions" - total
            "psets"        - how many PSETs
            "folded"       - how many emitted nothing (same as psets when the
                             invariant holds)
            "transfers"    - how many resolved transfers
    """
    psets = sum(1 for i in program if i["op"] == "PSET")
    transfers = sum(1 for i in program if i["op"] in ("JP", "CALL"))
    violations = check_pset_invariant(program) or []
    return {"instructions": len(program), "psets": psets,
            "folded": psets - len(violations), "transfers": transfers}
''',
    test='''
def insn(addr, op, page=None, offset=None):
    return {"addr": addr, "op": op, "page": page, "offset": offset}


GOOD = [
    insn(0x0000, "NOP"),
    insn(0x0001, "PSET", page=0x03),
    insn(0x0002, "CALL", offset=0x07),
    insn(0x0003, "PSET", page=0x07),
    insn(0x0004, "JP", offset=0xE8),
    insn(0x0307, "NOP"),
]

BAD = [
    insn(0x0000, "PSET", page=0x03),
    insn(0x0001, "NOP"),                 # not a transfer -- invariant broken
    insn(0x0002, "JP", offset=0x10),
]


class TestResolveTargets:
    def test_call_target(self):
        out = paging.resolve_targets(GOOD)
        assert out is not None, "resolve_targets() returned None"
        assert out[2]["target"] == 0x0307

    def test_jp_target(self):
        out = paging.resolve_targets(GOOD)
        assert out[4]["target"] == 0x07E8

    def test_non_transfer_is_none(self):
        out = paging.resolve_targets(GOOD)
        assert out[0]["target"] is None

    def test_page_persists(self):
        prog = [insn(0, "PSET", page=0x02), insn(1, "JP", offset=0x10),
                insn(2, "JP", offset=0x20)]
        out = paging.resolve_targets(prog)
        assert out[2]["target"] == 0x0220

    def test_transfer_without_page(self):
        import pytest
        with pytest.raises(paging.PagingError):
            paging.resolve_targets([insn(0, "JP", offset=0x10)])

    def test_does_not_mutate(self):
        paging.resolve_targets(GOOD)
        assert "target" not in GOOD[0]


class TestInvariant:
    def test_holds(self):
        v = paging.check_pset_invariant(GOOD)
        assert v is not None, "check_pset_invariant() returned None"
        assert v == []

    def test_detects_violation(self):
        assert paging.check_pset_invariant(BAD) == [0x0000]

    def test_trailing_pset_is_a_violation(self):
        prog = [insn(0, "NOP"), insn(1, "PSET", page=1)]
        assert paging.check_pset_invariant(prog) == [1]


class TestEmit:
    def test_pset_emits_no_code(self):
        lines = paging.emit(GOOD)
        assert lines is not None, "emit() returned None"
        joined = "\\n".join(lines)
        # The PSET at 0x0001 gets a label and a comment, and nothing else.
        after = joined.split("L_0001:")[1].split("L_0002:")[0]
        assert "goto" not in after

    def test_transfer_uses_resolved_label(self):
        joined = "\\n".join(paging.emit(GOOD))
        assert "goto L_0307;" in joined

    def test_every_instruction_labelled(self):
        joined = "\\n".join(paging.emit(GOOD))
        for i in GOOD:
            assert f"L_{i['addr']:04X}:" in joined

    def test_refuses_when_invariant_broken(self):
        import pytest
        with pytest.raises(paging.PagingError):
            paging.emit(BAD)


class TestReport:
    def test_counts(self):
        r = paging.folding_report(GOOD)
        assert r["psets"] == 2
        assert r["folded"] == 2
        assert r["transfers"] == 2
''')

# ---------------------------------------------------------------------- 89
lab(89, "Independent Oracle", module="indoracle",
    summary="""
    Differentially validate against a third-party implementation, and tell a
    genuine target bug from a harness bug wearing its costume.
    """,
    readme="""
    ## Objective

    Run a full-state comparison against an implementation you did not write,
    and survive the false alarms.

    ## Background

    Module 53 section 5. `tamarecomp` compares `pc, A, B, X, Y, SP, flags`
    against BrickEmuPy's core on every instruction -- *"precisely because that
    core was written by someone else, from the same Epson documentation, in
    another language."*

    It found `RST F, i` inverted 1,486 instructions in. **Completely silent.**

    And two false alarms arrived first, each looking exactly like a CPU bug:

    - Windows `stdout` is a **text stream** and expanded every `0x0A` in the
      binary trace into `0x0D 0x0A`. The giveaway was the value of `X`, with
      *"the culprit bytes sitting right there in it"* -- a register
      holding something its own width cannot explain.
    - The reference advanced its oscillator inside every `clock()` while the
      runtime only moved time in `tama_step`, so one register read disagreed by
      a tick. Timers are now frozen on both sides: *"the test is about the CPU."*

    ## Your Task

    Implement in `indoracle.py`:

    - `REGISTER_WIDTHS` / `validate_state(state)` -- can this value even exist?
    - `compare_step(a, b)` -- full-state diff with plausibility checking.
    - `run_validation(...)` -- step both, classify the first disagreement.

    ## The Classification

    A disagreement is one of: `target_bug`, `impossible_value` (a register
    holding something its width cannot represent -- your harness is corrupting
    data), or `timing` (only timing-derived fields differ). Getting this triage
    right is the difference between a day and a week.
    """,
    stub='''
# Register widths in bits. A value wider than its register cannot come from
# the target -- it can only come from the harness.
REGISTER_WIDTHS = {"pc": 12, "a": 4, "b": 4, "x": 12, "y": 12, "sp": 8, "flags": 4}

# Fields whose value depends on how each side advances time, not on the CPU.
TIMING_FIELDS = {"cycles", "timer"}


def validate_state(state):
    """Check every register holds a value its width can represent.

    Returns:
        A list of (field, value, width) tuples for impossible values, sorted by
        field name. Empty means the state is at least representable.

    Fields not in REGISTER_WIDTHS are not checked.
    """
    # TODO: For each field in REGISTER_WIDTHS present in state, check
    #       0 <= value < (1 << width).
    pass


def compare_step(a, b):
    """Compare two states and classify any disagreement.

    Args:
        a: the reference (oracle) state dict.
        b: the state under test.

    Returns:
        A dict with:
            "agree"     - bool
            "fields"    - sorted list of differing field names
            "kind"      - None when they agree, otherwise one of
                          "impossible_value", "timing", "target_bug"
            "detail"    - a human-readable explanation, or ""

    Classification order matters:
      1. If either state holds an impossible value -> "impossible_value".
         Your harness is corrupting data; nothing else can be trusted.
      2. Else if every differing field is timing-derived -> "timing".
         Freeze the clocks and re-run; the test is about the CPU.
      3. Else -> "target_bug".
    """
    # TODO: Run validate_state on both, then diff the union of their keys,
    #       then classify in the order above.
    pass


def run_validation(steps, oracle_fn, target_fn, limit=1000000):
    """Step both implementations until they disagree.

    Args:
        steps: opaque program handle passed to both.
        oracle_fn: callable(steps, i) -> state dict.
        target_fn: callable(steps, i) -> state dict.
        limit: max steps.

    Returns:
        A dict with:
            "diverged"  - bool
            "step"      - index of the first disagreement, or None
            "kind"      - the classification, or None
            "fields"    - differing fields, or []
            "detail"    - explanation, or ""
            "steps_run" - how many steps completed

    A StopIteration from either side ends the run cleanly.
    """
    # TODO: Loop, call both, compare_step, and return on the first
    #       disagreement.
    pass


def format_validation(result):
    """Format a validation result, with advice keyed to the classification."""
    if not result["diverged"]:
        return f"no divergence in {result['steps_run']} step(s)"

    advice = {
        "impossible_value":
            "Your harness is corrupting data before the comparison. "
            "Check the trace transport (binary mode?) before the CPU.",
        "timing":
            "Only timing-derived fields differ. Freeze the clocks on both "
            "sides -- the test is about the CPU.",
        "target_bug":
            "A genuine semantic difference. Minimise it (Lab 66) and bisect "
            "(Lab 63).",
    }
    return (f"diverged at step {result['step']} [{result['kind']}]\\n"
            f"  fields: {', '.join(result['fields'])}\\n"
            f"  {result['detail']}\\n"
            f"  -> {advice.get(result['kind'], '')}")
''',
    test='''
def st(**kw):
    base = {"pc": 0, "a": 0, "b": 0, "x": 0, "y": 0, "sp": 0, "flags": 0}
    base.update(kw)
    return base


class TestValidateState:
    def test_ok(self):
        v = indoracle.validate_state(st(a=0xF, pc=0xFFF))
        assert v is not None, "validate_state() returned None"
        assert v == []

    def test_too_wide(self):
        v = indoracle.validate_state(st(a=0x10))
        assert len(v) == 1
        assert v[0][0] == "a"

    def test_the_real_giveaway(self):
        # A trace corrupted by CRLF translation injects a stray 0x0D,
        # pushing the value past what the register can hold.
        v = indoracle.validate_state(st(x=0x1A0D))
        assert any(f == "x" for f, _, _ in v)

    def test_unknown_field_ignored(self):
        assert indoracle.validate_state(st(cycles=999999)) == []

    def test_sorted(self):
        v = indoracle.validate_state(st(a=0x10, b=0x10))
        assert [f for f, _, _ in v] == ["a", "b"]


class TestCompareStep:
    def test_agree(self):
        r = indoracle.compare_step(st(), st())
        assert r is not None, "compare_step() returned None"
        assert r["agree"] is True
        assert r["kind"] is None

    def test_target_bug(self):
        r = indoracle.compare_step(st(flags=0x1), st(flags=0x2))
        assert r["kind"] == "target_bug"
        assert r["fields"] == ["flags"]

    def test_impossible_value_wins(self):
        # Even though flags also differ, the impossible X dominates.
        r = indoracle.compare_step(st(), st(x=0x1A0D, flags=1))
        assert r["kind"] == "impossible_value"

    def test_timing_only(self):
        a = dict(st(), cycles=100)
        b = dict(st(), cycles=101)
        r = indoracle.compare_step(a, b)
        assert r["kind"] == "timing"

    def test_timing_plus_register_is_a_bug(self):
        a = dict(st(a=1), cycles=100)
        b = dict(st(a=2), cycles=101)
        assert indoracle.compare_step(a, b)["kind"] == "target_bug"


class TestRunValidation:
    def test_clean(self):
        f = lambda s, i: st(pc=i)
        r = indoracle.run_validation(None, f, f, limit=100)
        assert r is not None, "run_validation() returned None"
        assert r["diverged"] is False
        assert r["steps_run"] == 100

    def test_finds_bug_at_step(self):
        def oracle(s, i):
            return st(pc=i, flags=0)

        def target(s, i):
            return st(pc=i, flags=1 if i == 42 else 0)

        r = indoracle.run_validation(None, oracle, target, limit=100)
        assert r["step"] == 42
        assert r["kind"] == "target_bug"

    def test_stops_at_end(self):
        def f(s, i):
            if i >= 10:
                raise StopIteration
            return st(pc=i)
        r = indoracle.run_validation(None, f, f, limit=100)
        assert r["steps_run"] == 10

    def test_format_gives_advice(self):
        def oracle(s, i):
            return st()

        def target(s, i):
            return st(x=0x1A0D)
        r = indoracle.run_validation(None, oracle, target, limit=5)
        assert "binary mode" in indoracle.format_validation(r)
''')

# ---------------------------------------------------------------------- 90
lab(90, "Is It Bytecode?", module="bytecheck",
    summary="""
    Classify binaries as native code or bytecode from import count and
    relocation density, against a known-native reference.
    """,
    readme="""
    ## Objective

    Answer Module 54's first question -- *which program am I recompiling?* --
    in ten minutes, from two numbers.

    ## Background

    `worldempire` is the worked example:

    ```
    EMPIRE.EXE   411,785 bytes   NE, 15 segments, 114,025 bytes of "code"
                 imported modules: VBRUN300     <- and nothing else
                 relocations: 14 total, 13 of them internal
    ```

    **One imported module.** *"A native Windows program cannot draw a pixel or
    open a window without KERNEL, USER and GDI. This one never calls them."*

    **Fourteen relocations across 114 KB.** *"The Even More Incredible Machine
    has 4,743 across 197 KB in the folder next door. Fourteen means almost
    nothing in those segments is machine code at all."*

    **Relocation density is a proxy for "is this really code."** Machine code is
    full of absolute addresses needing fixup; a blob of p-code is not.

    ## Your Task

    Implement in `bytecheck.py`:

    - `relocation_density(binary)` -- relocations per KB of code.
    - `is_runtime_only(binary, system_modules)` -- imports nothing but a runtime.
    - `classify(binary, reference)` -- native / bytecode / uncertain, with
      reasons.

    ## Report Reasons, Not Just a Verdict

    `classify` must return **why**. A verdict you cannot argue with is a verdict
    you cannot check, and Module 37 is unambiguous about that.
    """,
    stub='''
# Modules a native Windows program of this era cannot avoid.
SYSTEM_MODULES = {"KERNEL", "USER", "GDI", "KRNL386", "KERNEL32", "USER32", "GDI32"}


def relocation_density(binary):
    """Relocations per kilobyte of code.

    Args:
        binary: dict with "relocations" (int) and "code_bytes" (int).

    Returns:
        A float. A binary with no code has density 0.0 rather than raising --
        it is a degenerate input, not an error.
    """
    # TODO: relocations / (code_bytes / 1024), guarding zero.
    pass


def is_runtime_only(binary, system_modules=None):
    """Does this binary import nothing but somebody's runtime?

    Args:
        binary: dict with "imports" (list of module name strings).
        system_modules: the set a native program cannot avoid.

    Returns:
        True if the imports include no system module and at least one
        non-system module. A binary with no imports at all is not
        runtime-only -- it is something else, and saying so is more honest
        than guessing.

    Module names are compared case-insensitively and without any extension.
    """
    # TODO: Normalise the names, then apply the rule above.
    pass


def classify(binary, reference=None):
    """Classify a binary as native code, bytecode, or uncertain.

    Args:
        binary: dict with "name", "imports", "relocations", "code_bytes".
        reference: a known-native binary dict to compare density against, or
            None to use an absolute threshold.

    Returns:
        A dict with:
            "name"     - the binary's name
            "verdict"  - "native", "bytecode" or "uncertain"
            "density"  - its relocation density
            "reasons"  - list of human-readable strings

    Rules:
      - Runtime-only imports is strong evidence for bytecode.
      - Density below 10% of the reference (or below 1.0 per KB with no
        reference) is strong evidence for bytecode.
      - Both -> "bytecode". Neither -> "native". Exactly one -> "uncertain",
        because one signal is a hint and two are a finding.
    """
    # TODO: Compute both signals, build the reasons list, and apply the rules.
    pass


def format_classification(result):
    """Format a classification."""
    lines = [f"{result['name']}: {result['verdict'].upper()} "
             f"(density {result['density']:.2f}/KB)"]
    for r in result["reasons"]:
        lines.append(f"  - {r}")
    return "\\n".join(lines)
''',
    test='''
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
''')

# ---------------------------------------------------------------------- 91
lab(91, "Stack to Locals", module="stacklocals",
    summary="""
    Compute static stack depth for a stack VM and emit numbered C locals
    instead of a runtime stack.
    """,
    readme="""
    ## Objective

    Implement Module 54's central trick, and the corpus check that proves it.

    ## Background

    From `newtonrecomp`:

    > NewtonScript is a stack VM, but **a recompiler that emits a runtime stack
    > array and a `sp` is just an interpreter with extra steps.** The stack depth
    > at every pc is statically determined, so each stack slot becomes a plain C
    > local (`s[0]`, `s[1]`, ...) with no pushing or popping at run time.

    It generalises to every stack VM -- JVM, CLR, p-code, Forth. **Stack depth
    is a static property.**

    And the verification is free: a stack VM has an invariant -- depth must
    balance at every merge point and at return -- that you can check **without
    running anything**, across thousands of programs.

    ## Your Task

    Implement in `stacklocals.py`:

    - `compute_depths(program)` -- depth at every pc, following branches.
    - `verify_balance(program)` -- the corpus check.
    - `emit(program)` -- C using numbered locals.
    - `max_depth(depths)` -- how many locals to declare.

    ## Where This Earns Its Keep

    `verify_balance` is what catches Module 54's `07 00 07` escape bug: a
    misparse produces *plausible instructions*, so the code looks fine and the
    stack does not balance.
    """,
    stub='''
class StackError(Exception):
    """Raised when the stack does not balance."""


# An instruction is a dict:
#   {"pc": int, "op": str, "pops": int, "pushes": int,
#    "target": int or None}   # branch target, if any
#   Ops "branch" (unconditional) and "branch_if" (conditional) use target.
#   Op "return" ends a path.


def compute_depths(program):
    """Compute the stack depth on entry to every instruction.

    Starts at pc 0 with depth 0 and follows both fallthrough and branch edges.
    Unreachable instructions get no entry.

    Args:
        program: list of instruction dicts, indexed by position; each "pc" is
            its index.

    Returns:
        A dict mapping pc -> depth on entry.

    Raises:
        StackError: if two paths reach the same pc with different depths --
            that is the misparse signature, and guessing which is right would
            hide it.
    """
    # TODO: Work-list traversal from pc 0. For each instruction compute the
    #       depth after it (depth - pops + pushes), then propagate to the
    #       fallthrough and/or branch successors, checking for conflicts.
    pass


def verify_balance(program):
    """Check the stack invariant across a whole program.

    Returns:
        A list of human-readable problem strings. Empty means it balances.

    Checks:
      - depth never goes negative (an instruction popped more than existed)
      - every "return" is reached at depth 0
      - compute_depths raises no conflict (reported as a problem, not an
        exception, so a corpus run can continue to the next program)
    """
    # TODO: Call compute_depths inside a try. Then walk the instructions with
    #       known depths, checking the two conditions above.
    pass


def max_depth(depths):
    """The most locals any point in the program needs."""
    return max(depths.values()) if depths else 0


def emit(program, depths):
    """Emit C using numbered locals instead of a runtime stack.

    Each instruction consumes its operands from the top slots and writes its
    result to the slot at its entry depth minus its pops.

        /*   46: find-var 0 */
        s[0] = op_find_var();
        /*   47: get-var 5  */
        s[1] = op_get_var();

    Args:
        program: the instructions.
        depths: output of compute_depths.

    Returns:
        A list of source lines, starting with the local declaration.
    """
    # TODO: Emit a declaration sized by max_depth, then one commented line per
    #       reachable instruction assigning to s[depth - pops] when it pushes,
    #       or a bare call when it does not.
    pass
''',
    test='''
def ins(pc, op, pops=0, pushes=0, target=None):
    return {"pc": pc, "op": op, "pops": pops, "pushes": pushes, "target": target}


STRAIGHT = [
    ins(0, "push", pushes=1),
    ins(1, "push", pushes=1),
    ins(2, "add", pops=2, pushes=1),
    ins(3, "pop", pops=1),
    ins(4, "return"),
]

BRANCHING = [
    ins(0, "push", pushes=1),
    ins(1, "branch_if", pops=1, target=3),
    ins(2, "branch", target=3),
    ins(3, "return"),
]

UNBALANCED = [
    ins(0, "push", pushes=1),
    ins(1, "branch_if", pops=1, target=3),
    ins(2, "push", pushes=1),      # leaves depth 1 at pc 3
    ins(3, "return"),
]

UNDERFLOW = [
    ins(0, "pop", pops=1),
    ins(1, "return"),
]


class TestComputeDepths:
    def test_straight_line(self):
        d = stacklocals.compute_depths(STRAIGHT)
        assert d is not None, "compute_depths() returned None"
        assert d[0] == 0 and d[1] == 1 and d[2] == 2 and d[3] == 1 and d[4] == 0

    def test_branches_converge(self):
        d = stacklocals.compute_depths(BRANCHING)
        assert d[3] == 0

    def test_conflict_raises(self):
        import pytest
        with pytest.raises(stacklocals.StackError):
            stacklocals.compute_depths(UNBALANCED)

    def test_unreachable_absent(self):
        prog = [ins(0, "branch", target=2), ins(1, "push", pushes=1), ins(2, "return")]
        d = stacklocals.compute_depths(prog)
        assert 1 not in d


class TestVerifyBalance:
    def test_clean(self):
        p = stacklocals.verify_balance(STRAIGHT)
        assert p is not None, "verify_balance() returned None"
        assert p == []

    def test_reports_conflict_without_raising(self):
        p = stacklocals.verify_balance(UNBALANCED)
        assert len(p) >= 1

    def test_detects_underflow(self):
        p = stacklocals.verify_balance(UNDERFLOW)
        assert any("negative" in x.lower() or "underflow" in x.lower() for x in p)

    def test_return_not_at_zero(self):
        prog = [ins(0, "push", pushes=1), ins(1, "return")]
        p = stacklocals.verify_balance(prog)
        assert any("return" in x.lower() for x in p)


class TestMaxDepth:
    def test_value(self):
        assert stacklocals.max_depth(stacklocals.compute_depths(STRAIGHT)) == 2

    def test_empty(self):
        assert stacklocals.max_depth({}) == 0


class TestEmit:
    def test_declares_locals(self):
        d = stacklocals.compute_depths(STRAIGHT)
        lines = stacklocals.emit(STRAIGHT, d)
        assert lines is not None, "emit() returned None"
        assert any("s[" in line and ";" in line for line in lines[:1])

    def test_no_runtime_stack(self):
        d = stacklocals.compute_depths(STRAIGHT)
        joined = chr(10).join(stacklocals.emit(STRAIGHT, d))
        for marker in ("sp++", "sp--", "stack[", "->sp"):
            assert marker not in joined, \
                f"{marker} means a runtime stack survived"

    def test_assigns_by_depth(self):
        d = stacklocals.compute_depths(STRAIGHT)
        joined = "\\n".join(stacklocals.emit(STRAIGHT, d))
        assert "s[0] =" in joined and "s[1] =" in joined

    def test_comments_carry_pc(self):
        d = stacklocals.compute_depths(STRAIGHT)
        joined = "\\n".join(stacklocals.emit(STRAIGHT, d))
        assert "2:" in joined
''')

# ---------------------------------------------------------------------- 92
lab(92, "Encoding Traps", module="encoding",
    summary="""
    A bytecode decoder with a multi-byte escape, and the corpus check that
    catches a misparse producing plausible-but-wrong instructions.
    """,
    readme="""
    ## Objective

    Decode an encoding with an escape hatch, and build the check that catches
    getting it wrong -- because getting it wrong does not crash.

    ## Background

    Module 54 section 4, from `newtonrecomp`'s `BYTECODE.md`:

    > `pop-handlers` is simple-op 7, and 7 cannot fit in the 3-bit field, so it
    > is encoded **`07 00 07`** -- three bytes. Read it as one and the two
    > operand bytes masquerade as a `pop` and another `pop-handlers`, which
    > **silently corrupts every function containing a `try` block**. Across the
    > archive the escape occurs **10,818 times** and its operand is always 7.

    And the gap: *"Opcodes 1 and 2 are unused -- that gap is what makes the
    table look 'shifted' if you guess at it."*

    The misparse does not crash. It produces *plausible instructions*, and only
    in functions with exception handlers. Your decoder works on most of the
    corpus and quietly mangles a subset.

    ## Your Task

    Implement in `encoding.py`:

    - `decode_one(data, pos)` -- one instruction, handling the escape.
    - `decode_all(data)` -- a whole stream.
    - `decode_naive(data)` -- the buggy version that ignores the escape.
    - `corpus_check(programs)` -- find where the two disagree.

    ## The Deliverable

    `corpus_check` must find programs where naive and correct decoders disagree
    and report **how many** and **where**. That count is the argument: 10,818 is
    persuasive, one example is not.
    """,
    stub='''
# Encoding: one byte, opcode:5 | a:3.
# If a == 7, a 16-bit big-endian operand follows; otherwise B = a.
# Opcode 0 is the "simple" set, where B selects the instruction.
ESCAPE = 7

SIMPLE_OPS = {0: "pop", 1: "dup", 2: "return", 3: "push-self",
              4: "set-lex-scope", 5: "iter-next", 6: "iter-done",
              7: "pop-handlers"}

# Opcodes 1 and 2 are unused: the gap that makes a guessed table look shifted.
OPCODES = {0: "simple", 3: "push", 4: "push-const", 5: "call", 6: "invoke",
           7: "send", 11: "branch", 12: "branch-if-true", 13: "branch-if-false"}


class DecodeError(Exception):
    """Raised when a byte stream cannot be decoded."""


def decode_one(data, pos):
    """Decode one instruction at *pos*.

    Returns:
        A dict with:
            "pos"    - where it started
            "opcode" - the 5-bit opcode
            "name"   - the instruction name
            "b"      - the operand value
            "length" - 1 or 3

    For opcode 0, "name" comes from SIMPLE_OPS[b].

    Raises:
        DecodeError: on a truncated escape, or an unknown opcode or simple-op.
    """
    # TODO: Read the byte. opcode = byte >> 3, a = byte & 7. If a == ESCAPE,
    #       read a 16-bit big-endian operand from the next two bytes (length 3);
    #       otherwise b = a (length 1). Then resolve the name, remembering that
    #       opcode 0 resolves through SIMPLE_OPS.
    pass


def decode_all(data):
    """Decode a whole byte stream.

    Returns:
        A list of instruction dicts.

    Raises:
        DecodeError: propagated from decode_one.
    """
    # TODO: Walk the stream, advancing by each instruction's length.
    pass


def decode_naive(data):
    """The BUGGY decoder: treats every instruction as one byte.

    This is what you get if you miss the escape. It does not crash -- it
    produces plausible instructions, which is exactly why the bug survives.

    Returns:
        A list of instruction dicts, all with length 1. Unknown opcodes and
        simple-ops become "?" rather than raising, because the whole point is
        that this decoder does not complain.
    """
    # TODO: One byte per instruction, b = byte & 7, names looked up leniently.
    pass


def corpus_check(programs):
    """Find programs where the naive and correct decoders disagree.

    Args:
        programs: dict mapping program name -> bytes.

    Returns:
        A dict with:
            "total"      - programs checked
            "disagree"   - how many differ
            "escapes"    - total escape sequences found across the corpus
            "affected"   - sorted names of the differing programs
            "errors"     - sorted names that failed to decode at all

    A program the correct decoder cannot decode is counted in "errors" and not
    in "disagree" -- those are different problems.
    """
    # TODO: For each program, decode both ways (guarding DecodeError), compare
    #       the instruction-name sequences, and count escapes (length == 3).
    pass
''',
    test='''
# push-handlers escape: 07 00 07 -> opcode 0, a == 7, operand 0x0007
ESCAPED = bytes([0x07, 0x00, 0x07])
# opcode 0, a = 0 -> "pop"
SIMPLE_POP = bytes([0x00])
# opcode 3 (push), a = 2 -> b = 2
PUSH2 = bytes([(3 << 3) | 2])


class TestDecodeOne:
    def test_simple(self):
        i = encoding.decode_one(SIMPLE_POP, 0)
        assert i is not None, "decode_one() returned None"
        assert i["name"] == "pop"
        assert i["length"] == 1

    def test_operand_in_low_bits(self):
        i = encoding.decode_one(PUSH2, 0)
        assert i["name"] == "push"
        assert i["b"] == 2

    def test_escape_is_three_bytes(self):
        i = encoding.decode_one(ESCAPED, 0)
        assert i["length"] == 3
        assert i["b"] == 7
        assert i["name"] == "pop-handlers"

    def test_truncated_escape(self):
        import pytest
        with pytest.raises(encoding.DecodeError):
            encoding.decode_one(bytes([0x07, 0x00]), 0)

    def test_unknown_opcode(self):
        import pytest
        with pytest.raises(encoding.DecodeError):
            encoding.decode_one(bytes([(30 << 3) | 0]), 0)


class TestDecodeAll:
    def test_sequence(self):
        out = encoding.decode_all(SIMPLE_POP + PUSH2)
        assert out is not None, "decode_all() returned None"
        assert [i["name"] for i in out] == ["pop", "push"]

    def test_escape_consumes_three(self):
        out = encoding.decode_all(ESCAPED + SIMPLE_POP)
        assert len(out) == 2
        assert out[1]["name"] == "pop"


class TestNaive:
    def test_misreads_the_escape(self):
        naive = encoding.decode_naive(ESCAPED)
        assert naive is not None, "decode_naive() returned None"
        # Three "instructions" instead of one -- and none of them crash.
        assert len(naive) == 3

    def test_agrees_without_escapes(self):
        data = SIMPLE_POP + PUSH2
        assert [i["name"] for i in encoding.decode_naive(data)] == \\
               [i["name"] for i in encoding.decode_all(data)]

    def test_does_not_raise_on_unknown(self):
        out = encoding.decode_naive(bytes([(30 << 3) | 0]))
        assert out[0]["name"] == "?"


class TestCorpusCheck:
    def corpus(self):
        return {
            "clean_a": SIMPLE_POP + PUSH2,
            "clean_b": PUSH2 * 4,
            "has_try": SIMPLE_POP + ESCAPED + PUSH2,
            "also_try": ESCAPED + ESCAPED,
        }

    def test_counts(self):
        r = encoding.corpus_check(self.corpus())
        assert r is not None, "corpus_check() returned None"
        assert r["total"] == 4
        assert r["disagree"] == 2

    def test_names_affected(self):
        r = encoding.corpus_check(self.corpus())
        assert r["affected"] == ["also_try", "has_try"]

    def test_counts_escapes(self):
        r = encoding.corpus_check(self.corpus())
        assert r["escapes"] == 3

    def test_errors_separate(self):
        c = self.corpus()
        c["broken"] = bytes([0x07, 0x00])       # truncated escape
        r = encoding.corpus_check(c)
        assert r["errors"] == ["broken"]
        assert "broken" not in r["affected"]
''')

report()
