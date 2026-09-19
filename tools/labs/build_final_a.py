#!/usr/bin/env python3
"""Build labs 93, 94, 95, 83, 99, 100."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

# ---------------------------------------------------------------------- 93
lab(93, "Assemble the Address Space", module="addrspace",
    summary="""
    Glue a device's separate images into one address space, and measure what
    that alone does to the unresolved-transfer count.
    """,
    readme="""
    ## Objective

    Reproduce the single cheapest win in Module 55: analysing the whole machine
    instead of half of it.

    ## Background

    From `cybikorecomp`'s `INDIRECT.md`:

    > CyOS and the boot ROM are separate files but **not separate worlds** --
    > CyOS calls down into the boot ROM constantly, for `memcpy` and `memset`
    > among others. Analysed apart, every such call is a "target outside the
    > image". `tools/cyimage.py` glues them into one space (`0x000000` boot ROM,
    > `0x200000` SRAM), and that alone took unresolved transfers from **2,533 to
    > 227**.

    And the second-order effect:

    > It also removed all 12 "undecodable opcodes", which were **never decoder
    > gaps** -- they were misaligned decodes caused by tracing into a region the
    > other half owned.

    ## Your Task

    Implement in `addrspace.py`:

    - `AddressSpace` -- several images mapped at their own bases.
    - `contains(addr)` / `image_of(addr)`.
    - `analyse(transfers, space)` -- resolved versus unresolved.
    - `compare_assembly(images, transfers)` -- per-image versus combined.

    ## The Number to Report

    `compare_assembly` returns the unresolved count both ways. That ratio is
    the finding, and it costs an afternoon to produce.
    """,
    stub='''
class Overlap(Exception):
    """Raised when two images would occupy the same addresses."""


class AddressSpace:
    """Several images mapped into one flat space."""

    def __init__(self):
        self.images = []        # list of (base, size, name)

    def add(self, name, base, size):
        """Map an image.

        Raises:
            Overlap: if it would collide with one already mapped. Silently
                allowing an overlap means every later lookup is a coin flip.
        """
        # TODO: Check every existing image for an overlapping range, then
        #       append and keep self.images sorted by base.
        pass

    def contains(self, addr):
        """Is *addr* inside any mapped image?"""
        # TODO: Any image whose range covers addr.
        pass

    def image_of(self, addr):
        """Which image owns *addr*?

        Returns:
            The image name, or None.
        """
        # TODO: Return the name of the covering image.
        pass


def analyse(transfers, space):
    """Classify transfer targets against an address space.

    Args:
        transfers: list of dicts with "site" and "target" addresses.
        space: an AddressSpace.

    Returns:
        A dict with:
            "total"      - how many transfers
            "resolved"   - targets inside the space
            "unresolved" - targets outside it
            "outside"    - sorted list of the unresolved target addresses
    """
    # TODO: Count each transfer by whether the space contains its target.
    pass


def compare_assembly(images, transfers):
    """Compare analysing each image alone against analysing them together.

    Args:
        images: list of (name, base, size) tuples.
        transfers: list of transfer dicts.

    Returns:
        A dict with:
            "separate"   - unresolved count when each image is analysed alone
            "combined"   - unresolved count with everything mapped together
            "recovered"  - separate - combined
            "ratio"      - combined / separate, 0.0 when separate is 0

    Analysing "alone" means: for each image, build a space containing only that
    image, and count the transfers whose *site* is in that image but whose
    target is not.
    """
    # TODO: Build the per-image spaces and the combined space, and count.
    pass
''',
    test='''
IMAGES = [("bootrom", 0x000000, 0x8000), ("cyos", 0x200000, 0x80000)]

TRANSFERS = [
    {"site": 0x200100, "target": 0x000400},   # cyos -> bootrom (memcpy)
    {"site": 0x200200, "target": 0x000500},   # cyos -> bootrom (memset)
    {"site": 0x200300, "target": 0x200800},   # cyos -> cyos
    {"site": 0x000100, "target": 0x000200},   # bootrom -> bootrom
    {"site": 0x200400, "target": 0x900000},   # genuinely outside
]


def space():
    s = addrspace.AddressSpace()
    for name, base, size in IMAGES:
        s.add(name, base, size)
    return s


class TestAddressSpace:
    def test_contains(self):
        s = space()
        assert s.contains(0x000400) is True
        assert s.contains(0x200800) is True

    def test_outside(self):
        assert space().contains(0x900000) is False

    def test_gap_between_images(self):
        assert space().contains(0x100000) is False

    def test_image_of(self):
        s = space()
        assert s.image_of(0x000400) == "bootrom"
        assert s.image_of(0x200800) == "cyos"

    def test_image_of_outside(self):
        assert space().image_of(0x900000) is None

    def test_overlap_rejected(self):
        import pytest
        s = space()
        with pytest.raises(addrspace.Overlap):
            s.add("dup", 0x000100, 0x100)


class TestAnalyse:
    def test_counts(self):
        r = addrspace.analyse(TRANSFERS, space())
        assert r is not None, "analyse() returned None"
        assert r["total"] == 5
        assert r["resolved"] == 4
        assert r["unresolved"] == 1

    def test_lists_outside(self):
        r = addrspace.analyse(TRANSFERS, space())
        assert r["outside"] == [0x900000]

    def test_empty(self):
        r = addrspace.analyse([], space())
        assert r["total"] == 0 and r["unresolved"] == 0


class TestCompareAssembly:
    def test_assembly_recovers_transfers(self):
        r = addrspace.compare_assembly(IMAGES, TRANSFERS)
        assert r is not None, "compare_assembly() returned None"
        assert r["separate"] > r["combined"]

    def test_the_cybiko_shape(self):
        # Two cross-image calls look unresolved until the images are glued.
        r = addrspace.compare_assembly(IMAGES, TRANSFERS)
        assert r["separate"] == 3
        assert r["combined"] == 1
        assert r["recovered"] == 2

    def test_ratio(self):
        r = addrspace.compare_assembly(IMAGES, TRANSFERS)
        assert abs(r["ratio"] - (1 / 3)) < 1e-9

    def test_no_transfers(self):
        r = addrspace.compare_assembly(IMAGES, [])
        assert r["ratio"] == 0.0
''')

# ---------------------------------------------------------------------- 94
lab(94, "Classify the Unknowns", module="classify",
    summary="""
    Backward-scan each indirect transfer for the write that defined its target
    register, and group the sites by mechanism.
    """,
    readme="""
    ## Objective

    Turn an undifferentiated pile of unresolved transfers into a small number of
    tractable problems.

    ## Background

    Module 55 section 3. After assembling the address space, `cybikorecomp` had
    227 genuinely indirect transfers. Backward-scanning each site's basic block
    for the last write to the register it calls through gave:

    | defining instruction | sites | what it is |
    |---|---|---|
    | `mov.l @(d:16,ERm), ERn` | 178 | a field of a struct -- **C++ virtual dispatch** |
    | `mov.l @aa:16, ERn` | 43 | a fixed address in on-chip RAM |
    | `mov.l @ERm, ERn` | 3 | a pointer |
    | `mov.l @aa:24, ERn` | 1 | `0x200004` |
    | nothing in the block | 2 | argument, or set further back |

    > **Three different problems, not 227.**

    ## Your Task

    Implement in `classify.py`:

    - `find_definition(block, site_index, register)` -- the backward scan.
    - `classify_site(block, site_index)` -- the mechanism.
    - `classify_all(sites)` -- grouped counts.
    - `report(groups)` -- sorted, with the interpretation attached.

    ## Why Grouping Beats Solving

    227 unknowns is unactionable. Three mechanisms are three pieces of work you
    can estimate separately -- and vtable dispatch, a fixed dispatch table and
    genuine pointers each need a different approach.
    """,
    stub='''
# An instruction is a dict: {"op": str, "dst": reg or None, "mode": str or None}
#
# Addressing modes that define a register, and what each implies:
MECHANISMS = {
    "displacement": "C++ virtual dispatch (a field of a struct)",
    "absolute16": "a fixed address in on-chip RAM (a dispatch table)",
    "indirect": "a genuine pointer",
    "absolute24": "a fixed far address",
}

UNKNOWN = "no definition in this block"


def find_definition(block, site_index, register):
    """Scan backwards for the last write to *register* before *site_index*.

    Args:
        block: list of instruction dicts, in order.
        site_index: index of the indirect transfer.
        register: the register it calls through.

    Returns:
        The defining instruction dict, or None if nothing in this block
        writes that register.
    """
    # TODO: Walk indices site_index-1 down to 0, returning the first
    #       instruction whose "dst" is the register.
    pass


def classify_site(block, site_index):
    """Classify one indirect transfer by what defined its target.

    Args:
        block: the basic block containing the site.
        site_index: index of the transfer, whose dict has a "reg" key.

    Returns:
        The addressing mode string of the defining instruction, or UNKNOWN.
    """
    # TODO: Read the site's "reg", call find_definition, and return the
    #       defining instruction's "mode" (or UNKNOWN when there is none).
    pass


def classify_all(sites):
    """Classify a list of (block, site_index) pairs.

    Returns:
        A dict mapping mechanism -> count.
    """
    # TODO: Classify each and tally.
    pass


def report(groups):
    """Format grouped counts, largest first, with the interpretation.

    Returns:
        A list of dicts with "mechanism", "count" and "means", sorted by count
        descending then mechanism ascending.
    """
    # TODO: Build and sort, looking each mechanism up in MECHANISMS and
    #       falling back to the mechanism string itself.
    pass


def summary_line(groups):
    """One line stating the real size of the problem."""
    total = sum(groups.values())
    return f"{total} indirect transfer(s) -- {len(groups)} different problem(s)"
''',
    test='''
def i(op, dst=None, mode=None, reg=None):
    d = {"op": op, "dst": dst, "mode": mode}
    if reg is not None:
        d["reg"] = reg
    return d


VTABLE_BLOCK = [
    i("mov.l", dst="er0", mode="displacement"),
    i("add", dst="er1"),
    i("jsr", reg="er0"),
]

TABLE_BLOCK = [
    i("mov.l", dst="er2", mode="absolute16"),
    i("jsr", reg="er2"),
]

POINTER_BLOCK = [
    i("mov.l", dst="er3", mode="indirect"),
    i("jsr", reg="er3"),
]

NO_DEF_BLOCK = [
    i("nop"),
    i("jsr", reg="er5"),
]


class TestFindDefinition:
    def test_finds_it(self):
        d = classify.find_definition(VTABLE_BLOCK, 2, "er0")
        assert d is not None
        assert d["mode"] == "displacement"

    def test_takes_the_last_write(self):
        block = [i("mov.l", dst="er0", mode="indirect"),
                 i("mov.l", dst="er0", mode="displacement"),
                 i("jsr", reg="er0")]
        assert classify.find_definition(block, 2, "er0")["mode"] == "displacement"

    def test_ignores_other_registers(self):
        assert classify.find_definition(VTABLE_BLOCK, 2, "er9") is None

    def test_does_not_look_forward(self):
        block = [i("jsr", reg="er0"), i("mov.l", dst="er0", mode="indirect")]
        assert classify.find_definition(block, 0, "er0") is None


class TestClassifySite:
    def test_vtable(self):
        assert classify.classify_site(VTABLE_BLOCK, 2) == "displacement"

    def test_table(self):
        assert classify.classify_site(TABLE_BLOCK, 1) == "absolute16"

    def test_pointer(self):
        assert classify.classify_site(POINTER_BLOCK, 1) == "indirect"

    def test_unknown(self):
        assert classify.classify_site(NO_DEF_BLOCK, 1) == classify.UNKNOWN


class TestClassifyAll:
    def sites(self):
        return ([(VTABLE_BLOCK, 2)] * 178 + [(TABLE_BLOCK, 1)] * 43 +
                [(POINTER_BLOCK, 1)] * 3 + [(NO_DEF_BLOCK, 1)] * 2)

    def test_the_cybiko_numbers(self):
        g = classify.classify_all(self.sites())
        assert g is not None, "classify_all() returned None"
        assert g["displacement"] == 178
        assert g["absolute16"] == 43
        assert g["indirect"] == 3
        assert g[classify.UNKNOWN] == 2

    def test_total(self):
        g = classify.classify_all(self.sites())
        assert sum(g.values()) == 226

    def test_summary_names_the_real_size(self):
        g = classify.classify_all(self.sites())
        line = classify.summary_line(g)
        assert "226" in line and "4 different" in line


class TestReport:
    def test_sorted(self):
        g = {"indirect": 3, "displacement": 178, "absolute16": 43}
        r = classify.report(g)
        assert r is not None, "report() returned None"
        assert [x["mechanism"] for x in r] == ["displacement", "absolute16", "indirect"]

    def test_attaches_meaning(self):
        r = classify.report({"displacement": 1})
        assert "virtual dispatch" in r[0]["means"]

    def test_unknown_mechanism_passes_through(self):
        r = classify.report({classify.UNKNOWN: 2})
        assert r[0]["means"] == classify.UNKNOWN
''')

# ---------------------------------------------------------------------- 95
lab(95, "Harvard Memory Model", module="harvard",
    summary="""
    A memory layer for a CPU with disjoint code and data spaces, and the test
    that catches an implementation which conflates them.
    """,
    readme="""
    ## Objective

    Implement a memory model that breaks the flat-space assumption baked into
    most of this course.

    ## Background

    Module 55 section 4. `vmurecomp`'s `docs/CPU.md` on the Sanyo LC8670:

    > Two **disjoint** address spaces:
    > - **ROM**, 64 KB, used for instruction fetch and by `LDC`.
    > - **RAM**, 512 bytes, used for every operand and every peripheral.

    Address `0x100` in ROM and address `0x100` in RAM are different locations.
    **The instruction determines which space you are in**, not the address.

    This breaks a single `mem[]` array, Module 43's "guest address plus a base
    offset is a host address", and any analysis that follows a pointer without
    knowing which space it points into.

    ## Your Task

    Implement in `harvard.py`:

    - `HarvardMemory` -- two independent spaces.
    - `fetch(addr)` / `load(addr)` / `store(addr, value)` / `ldc(addr)`.
    - `detect_conflation(memory)` -- the test that catches a flat model.

    ## The Test That Matters

    `detect_conflation` writes distinguishable values to the same address in
    both spaces and checks they stay distinct. A flat implementation fails it
    immediately; a correct one cannot.
    """,
    stub='''
class SpaceError(Exception):
    """Raised on an access outside a space."""


class HarvardMemory:
    """Two disjoint address spaces sharing no addresses.

    Attributes:
        rom: instruction space, read-only.
        ram: data and peripheral space.
    """

    def __init__(self, rom_size=0x10000, ram_size=0x200):
        self.rom = bytearray(rom_size)
        self.ram = bytearray(ram_size)
        self.io_handlers = {}     # ram address -> callable(value_or_None)

    def fetch(self, addr):
        """Fetch an instruction byte from ROM.

        Raises:
            SpaceError: if addr is outside ROM.
        """
        # TODO: Bounds-check against len(self.rom) and index it.
        pass

    def ldc(self, addr):
        """Read a data byte from ROM -- the one instruction that crosses over.

        Raises:
            SpaceError: if addr is outside ROM.
        """
        # TODO: Same as fetch. It is a separate method because the *reason*
        #       differs, and a reader needs to see which accesses are LDC.
        pass

    def load(self, addr):
        """Read an operand byte from RAM, honouring any I/O handler.

        Raises:
            SpaceError: if addr is outside RAM.
        """
        # TODO: Bounds-check, then call the handler if one is registered for
        #       this address, else index self.ram.
        pass

    def store(self, addr, value):
        """Write an operand byte to RAM, honouring any I/O handler.

        Raises:
            SpaceError: if addr is outside RAM.
        """
        # TODO: Bounds-check, then dispatch to the handler or write the byte.
        pass

    def map_io(self, addr, handler):
        """Register an I/O handler at a RAM address.

        The handler is called as handler(None) for a read and handler(value)
        for a write; its return value is used for reads.
        """
        self.io_handlers[addr] = handler


def detect_conflation(memory):
    """Check that the two spaces really are disjoint.

    Writes distinguishable values at the same numeric address in each space and
    verifies both survive. A flat implementation cannot pass this.

    Args:
        memory: a HarvardMemory.

    Returns:
        None if the spaces are disjoint, otherwise a detail string.
    """
    # TODO: Pick an address valid in both spaces. Put one value in rom
    #       directly, store a different one via store(), then compare what
    #       ldc() and load() return.
    pass
''',
    test='''
def mem():
    return harvard.HarvardMemory(rom_size=0x1000, ram_size=0x200)


class TestSpaces:
    def test_fetch(self):
        m = mem()
        m.rom[0x100] = 0xAB
        assert m.fetch(0x100) == 0xAB

    def test_load_and_store(self):
        m = mem()
        m.store(0x100, 0xCD)
        assert m.load(0x100) == 0xCD

    def test_same_address_different_values(self):
        m = mem()
        m.rom[0x100] = 0xAA
        m.store(0x100, 0xBB)
        assert m.fetch(0x100) == 0xAA
        assert m.load(0x100) == 0xBB

    def test_ldc_reads_rom(self):
        m = mem()
        m.rom[0x100] = 0x77
        m.store(0x100, 0x88)
        assert m.ldc(0x100) == 0x77

    def test_rom_bounds(self):
        import pytest
        with pytest.raises(harvard.SpaceError):
            mem().fetch(0x2000)

    def test_ram_bounds(self):
        import pytest
        with pytest.raises(harvard.SpaceError):
            mem().load(0x300)

    def test_ram_address_valid_in_rom_is_still_rejected(self):
        # 0x300 is a fine ROM address and an invalid RAM one.
        import pytest
        m = mem()
        assert m.fetch(0x300) == 0
        with pytest.raises(harvard.SpaceError):
            m.load(0x300)


class TestIO:
    def test_read_handler(self):
        m = mem()
        m.map_io(0x50, lambda v: 0x5A)
        assert m.load(0x50) == 0x5A

    def test_write_handler(self):
        seen = []
        m = mem()
        m.map_io(0x50, lambda v: seen.append(v))
        m.store(0x50, 0x99)
        assert seen == [0x99]

    def test_handler_does_not_touch_ram(self):
        m = mem()
        m.map_io(0x50, lambda v: 0x5A)
        m.store(0x50, 0x99)
        assert m.ram[0x50] == 0


class TestDetectConflation:
    def test_correct_model_passes(self):
        assert harvard.detect_conflation(mem()) is None

    def test_flat_model_caught(self):
        class Flat(harvard.HarvardMemory):
            def __init__(self):
                super().__init__(rom_size=0x1000, ram_size=0x200)
                self.ram = self.rom        # the bug: one array for both
        d = harvard.detect_conflation(Flat())
        assert d is not None
''')

# ---------------------------------------------------------------------- 83
lab(83, "Input Verification", module="verify",
    summary="""
    Identify the user's copy by hash, name the revision it found, warn clearly
    on a mismatch, and print a provenance record.
    """,
    readme="""
    ## Objective

    Build the check from Module 46 section 2, and stop a whole category of
    confused bug report.

    ## Background

    Users will bring the wrong region, a bad dump, a different revision, a
    re-release, or a file that is not the game. If your pipeline consumes that
    silently, they get a crash a thousand lines later and file an issue about
    your recompiler.

    A good check tells them three things:

    ```
    Expected: Rev A (US), SHA-256 3f9a...
    Found:    Rev B (EU), SHA-256 71c4...
    This project targets Rev A. Rev B has different function addresses
    and the manifest hints will not apply.
    ```

    **And it does not refuse to proceed.** Accept the input, warn loudly, and
    record what you used -- an unknown revision is often worth trying, and the
    user should know that is what they are doing.

    ## Your Task

    Implement in `verify.py`:

    - `hash_data(data)` -- SHA-256.
    - `identify(data, known)` -- which known revision is this?
    - `check(data, known, target)` -- the verdict plus a message.
    - `provenance(...)` -- the record Module 33 section 6 asks for.

    ## The Design Rule

    `check` returns a verdict of `match`, `known_mismatch` or `unknown`, and a
    message. **None of them is a refusal.** A tool that refuses to run on an
    unrecognised dump cannot be used to investigate an unrecognised dump.
    """,
    stub='''
import hashlib


def hash_data(data):
    """Return the SHA-256 hex digest of *data*."""
    # TODO: hashlib.sha256(data).hexdigest()
    pass


def identify(data, known):
    """Identify which known revision *data* is.

    Args:
        data: the bytes.
        known: dict mapping sha256 hex -> revision label.

    Returns:
        The label, or None if unrecognised.
    """
    # TODO: Hash and look up.
    pass


def check(data, known, target):
    """Verify the user's copy against the revision this project targets.

    Args:
        data: the bytes they supplied.
        known: dict mapping sha256 hex -> label.
        target: the label this project targets.

    Returns:
        A dict with:
            "verdict" - "match", "known_mismatch" or "unknown"
            "found"   - the identified label, or None
            "digest"  - the hash of what they gave you
            "message" - what to tell them

    The message must always name the digest, so a bug report carries it even
    when the revision is unrecognised. No verdict refuses to proceed.
    """
    # TODO: Identify, compare against target, and build the message for each
    #       of the three cases. For a known mismatch, say what it means:
    #       different addresses, hints will not apply.
    pass


def provenance(data, known, target, tool_versions):
    """Build the provenance record for a run.

    Args:
        data: the input bytes.
        known: the revision table.
        target: the targeted label.
        tool_versions: dict mapping tool name -> version string.

    Returns:
        A dict with "digest", "identified", "target", "verdict" and "tools"
        (a sorted list of "name=version" strings, so the record is stable
        between runs and diffable).
    """
    # TODO: Reuse check(), then add the sorted tool list.
    pass


def format_provenance(record):
    """Format a provenance record for printing at startup."""
    lines = ["=== Provenance ==="]
    lines.append(f"  input:      {record['digest'][:16]}...")
    lines.append(f"  identified: {record['identified'] or '(unrecognised)'}")
    lines.append(f"  target:     {record['target']}")
    lines.append(f"  verdict:    {record['verdict']}")
    for t in record["tools"]:
        lines.append(f"  tool:       {t}")
    return "\\n".join(lines)
''',
    test='''
REV_A = b"the rev A image"
REV_B = b"the rev B image"
JUNK = b"not a game at all"


def known():
    return {
        verify.hash_data(REV_A): "Rev A (US)",
        verify.hash_data(REV_B): "Rev B (EU)",
    }


class TestHash:
    def test_hex(self):
        h = verify.hash_data(b"x")
        assert h is not None, "hash_data() returned None"
        assert len(h) == 64
        int(h, 16)

    def test_stable(self):
        assert verify.hash_data(b"x") == verify.hash_data(b"x")


class TestIdentify:
    def test_known(self):
        assert verify.identify(REV_A, known()) == "Rev A (US)"

    def test_other(self):
        assert verify.identify(REV_B, known()) == "Rev B (EU)"

    def test_unknown(self):
        assert verify.identify(JUNK, known()) is None


class TestCheck:
    def test_match(self):
        r = verify.check(REV_A, known(), "Rev A (US)")
        assert r is not None, "check() returned None"
        assert r["verdict"] == "match"
        assert r["found"] == "Rev A (US)"

    def test_known_mismatch(self):
        r = verify.check(REV_B, known(), "Rev A (US)")
        assert r["verdict"] == "known_mismatch"
        assert "Rev B (EU)" in r["message"]
        assert "Rev A (US)" in r["message"]

    def test_mismatch_explains_the_consequence(self):
        r = verify.check(REV_B, known(), "Rev A (US)")
        assert "hint" in r["message"].lower() or "address" in r["message"].lower()

    def test_unknown(self):
        r = verify.check(JUNK, known(), "Rev A (US)")
        assert r["verdict"] == "unknown"

    def test_every_message_carries_the_digest(self):
        for data in (REV_A, REV_B, JUNK):
            r = verify.check(data, known(), "Rev A (US)")
            assert r["digest"][:16] in r["message"]

    def test_never_refuses(self):
        # All three verdicts are advisory. None of them is a refusal.
        for data in (REV_A, REV_B, JUNK):
            r = verify.check(data, known(), "Rev A (US)")
            assert r["verdict"] in ("match", "known_mismatch", "unknown")


class TestProvenance:
    def test_fields(self):
        p = verify.provenance(REV_A, known(), "Rev A (US)",
                              {"lifter": "1.2", "runtime": "0.9"})
        assert p is not None, "provenance() returned None"
        assert p["identified"] == "Rev A (US)"
        assert p["verdict"] == "match"

    def test_tools_sorted(self):
        p = verify.provenance(REV_A, known(), "Rev A (US)",
                              {"zzz": "1", "aaa": "2"})
        assert p["tools"] == ["aaa=2", "zzz=1"]

    def test_format(self):
        p = verify.provenance(REV_A, known(), "Rev A (US)", {"lifter": "1.2"})
        text = verify.format_provenance(p)
        assert "Rev A (US)" in text and "lifter=1.2" in text
''')

# ---------------------------------------------------------------------- 99
lab(99, "Instrument a Hybrid", module="hybrid",
    summary="""
    Count registered functions, hook hits and fallbacks, and report the
    crossover metric -- what fraction of execution is actually native.
    """,
    readme="""
    ## Objective

    Make an interception-based project able to say something true about itself.

    ## Background

    Module 49 section 2. Interception is a good design, and it costs you your
    usual evidence: with the interpreter fallback enabled, **a build with zero
    registered functions plays the game flawlessly.**

    > So the design owes you instrumentation. Count registered functions, count
    > hook hits, count fallbacks, and publish all three.

    `gbarecomp`'s `interception.c` already has `successful` and `failed`
    counters. They just are not in the README.

    ## Your Task

    Implement in `hybrid.py`:

    - `Interceptor` -- a registry plus counters.
    - `dispatch(addr)` -- native if registered, else fallback.
    - `crossover()` -- the fraction of *executed instructions* that ran native.
    - `honest_summary()` -- a claim that refuses to overstate.

    ## Instructions, Not Calls

    `crossover` weights by instructions executed, not by call count. A native
    function called once that runs 10,000 instructions matters more than a
    one-instruction stub called 500 times, and a call-count metric would say
    the opposite.
    """,
    stub='''
class Interceptor:
    """An interception registry with the counters the design owes you."""

    def __init__(self, fallback=None):
        self.registry = {}          # addr -> (callable, instruction_count)
        self.fallback = fallback    # callable(addr) -> instruction_count
        self.native_calls = 0
        self.fallback_calls = 0
        self.native_instructions = 0
        self.fallback_instructions = 0
        self.crashes = 0

    def register(self, addr, func, instructions=1):
        """Register a recompiled function at a guest address."""
        self.registry[addr] = (func, instructions)

    def dispatch(self, addr):
        """Run the recompiled function if there is one, else fall back.

        A registered function that raises is counted as a crash and falls back,
        which is what the real implementations do -- and is exactly why the
        counters matter.

        Returns:
            The number of instructions executed.

        Raises:
            RuntimeError: if nothing is registered and there is no fallback.
        """
        # TODO: Look up the address. On a hit, call it inside a try; on success
        #       count a native call and its instructions, on an exception count
        #       a crash and fall through. On a miss (or after a crash), use the
        #       fallback and count it, or raise if there is none.
        pass

    def crossover(self):
        """The fraction of executed instructions that ran as native code.

        Returns:
            A float in [0.0, 1.0]. Zero executed instructions gives 0.0.
        """
        # TODO: native_instructions / (native + fallback), guarding zero.
        pass

    def stats(self):
        """Return every counter, plus the crossover."""
        return {
            "registered": len(self.registry),
            "native_calls": self.native_calls,
            "fallback_calls": self.fallback_calls,
            "native_instructions": self.native_instructions,
            "fallback_instructions": self.fallback_instructions,
            "crashes": self.crashes,
            "crossover": self.crossover(),
        }


def honest_summary(stats):
    """A claim about a hybrid build that does not overstate it.

    Rules, in order:
      - no instructions executed -> "Nothing has executed."
      - crossover == 0.0         -> "N functions registered, but 0% of executed
                                     instructions ran native -- the fallback is
                                     running this program."
      - crossover == 1.0         -> "All executed instructions ran native code
                                     (N functions registered)."
      - otherwise                -> "P% of executed instructions ran native
                                     (N functions registered)."

    Then, if crashes > 0, append " C recompiled function(s) crashed and fell
    back."

    Returns:
        A string.
    """
    # TODO: Implement the rules. Percentages rounded to one decimal place.
    pass
''',
    test='''
def interp(addr):
    return 5      # the fallback runs five instructions


class TestDispatch:
    def test_native(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=20)
        assert h.dispatch(0x100) == 20
        assert h.native_calls == 1

    def test_fallback(self):
        h = hybrid.Interceptor(fallback=interp)
        assert h.dispatch(0x200) == 5
        assert h.fallback_calls == 1

    def test_crash_falls_back(self):
        def boom():
            raise ValueError("bad lift")
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, boom, instructions=20)
        assert h.dispatch(0x100) == 5
        assert h.crashes == 1
        assert h.fallback_calls == 1
        assert h.native_calls == 0

    def test_no_fallback_raises(self):
        import pytest
        with pytest.raises(RuntimeError):
            hybrid.Interceptor().dispatch(0x999)


class TestCrossover:
    def test_all_native(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=10)
        h.dispatch(0x100)
        assert h.crossover() == 1.0

    def test_all_fallback(self):
        h = hybrid.Interceptor(fallback=interp)
        h.dispatch(0x200)
        assert h.crossover() == 0.0

    def test_weighted_by_instructions(self):
        # One big native call outweighs many tiny fallbacks.
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=100)
        h.dispatch(0x100)
        for _ in range(10):
            h.dispatch(0x200)
        assert h.crossover() > 0.6

    def test_nothing_executed(self):
        assert hybrid.Interceptor().crossover() == 0.0


class TestHonestSummary:
    def test_nothing(self):
        s = hybrid.honest_summary(hybrid.Interceptor().stats())
        assert s is not None, "honest_summary() returned None"
        assert "Nothing has executed" in s

    def test_zero_crossover_is_called_out(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None)
        h.dispatch(0x200)
        s = hybrid.honest_summary(h.stats())
        assert "0%" in s
        assert "fallback is running this program" in s

    def test_full_crossover(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=10)
        h.dispatch(0x100)
        assert "All executed instructions ran native" in hybrid.honest_summary(h.stats())

    def test_partial(self):
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, lambda: None, instructions=5)
        h.dispatch(0x100)
        h.dispatch(0x200)
        assert "50.0%" in hybrid.honest_summary(h.stats())

    def test_mentions_crashes(self):
        def boom():
            raise ValueError
        h = hybrid.Interceptor(fallback=interp)
        h.register(0x100, boom, instructions=5)
        h.dispatch(0x100)
        assert "crashed and fell back" in hybrid.honest_summary(h.stats())
''')

# ---------------------------------------------------------------------- 100
lab(100, "Migration Ladder", module="migration",
    summary="""
    Move functions from the emulator to native code one at a time, keeping the
    program runnable at every step, and plot the crossover.
    """,
    readme="""
    ## Objective

    Build the migration path from Module 49 section 7, and measure it.

    ## Background

    > A sane progression:
    >
    > 1. **Interception**, with the emulator doing everything. Playable, zero
    >    native code.
    > 2. **Move functions across**, hottest or most-interesting first. Still
    >    playable throughout.
    > 3. **Measure the crossover** -- the fraction of execution that is native.
    >    This is your real progress metric.
    > 4. **Flip the default** once the native path is complete enough.
    > 5. **Drop the emulator**, if you ever fully resolve discovery.
    >
    > Each stage is shippable.

    ## Your Task

    Implement in `migration.py`:

    - `plan_migration(profile)` -- what order to port functions in.
    - `simulate_migration(profile, order)` -- crossover after each step.
    - `steps_to_reach(curve, target)` -- how many ports to hit a threshold.
    - `verify_runnable(...)` -- the invariant: every step still runs.

    ## The Invariant

    `verify_runnable` asserts that at every point in the migration, every
    function is either ported *or* available in the emulator. That is what makes
    each stage shippable, and it is the property an all-or-nothing bring-up
    lacks.
    """,
    stub='''
def plan_migration(profile):
    """Decide what order to port functions in.

    Hottest first: porting the function that executes most instructions moves
    the crossover furthest per unit of work.

    Args:
        profile: dict mapping function name -> instructions executed.

    Returns:
        A list of names, sorted by instruction count descending then name
        ascending. The tie-break keeps the plan stable between runs.
    """
    # TODO: Sort the profile.
    pass


def simulate_migration(profile, order):
    """Compute the crossover after each porting step.

    Args:
        profile: name -> instructions executed.
        order: the porting order.

    Returns:
        A list of floats, length len(order) + 1. Index 0 is 0.0 (nothing
        ported); index i is the crossover after porting order[:i].
    """
    # TODO: Accumulate instructions as functions are ported, dividing by the
    #       total each time. Guard a zero total.
    pass


def steps_to_reach(curve, target):
    """How many ports are needed to reach *target* crossover?

    Args:
        curve: output of simulate_migration.
        target: the crossover to reach, 0.0 to 1.0.

    Returns:
        The number of functions that must be ported, or None if the curve
        never reaches the target.
    """
    # TODO: Find the first index whose value is >= target; that index is the
    #       number of ports.
    pass


def verify_runnable(all_functions, ported, emulated):
    """Check the invariant that makes every migration step shippable.

    Every function must be either ported to native code or available in the
    emulator. A function that is neither means the program cannot run.

    Args:
        all_functions: every function the program needs.
        ported: set of names ported to native.
        emulated: set of names the emulator can run.

    Returns:
        A sorted list of names that are neither. Empty means runnable.
    """
    # TODO: Return the names in neither set.
    pass


def format_curve(curve, order):
    """Format a migration curve."""
    lines = ["ported | crossover | function"]
    for i, value in enumerate(curve):
        name = order[i - 1] if i > 0 else "(none)"
        lines.append(f"{i:6d} | {value * 100:8.1f}% | {name}")
    return "\\n".join(lines)
''',
    test='''
PROFILE = {"render": 5000, "update": 3000, "input": 1500, "audio": 400, "menu": 100}
ALL = set(PROFILE)


class TestPlan:
    def test_hottest_first(self):
        o = migration.plan_migration(PROFILE)
        assert o is not None, "plan_migration() returned None"
        assert o[0] == "render"
        assert o[-1] == "menu"

    def test_includes_everything(self):
        assert sorted(migration.plan_migration(PROFILE)) == sorted(PROFILE)

    def test_stable_on_ties(self):
        tied = {"b": 10, "a": 10}
        assert migration.plan_migration(tied) == ["a", "b"]


class TestSimulate:
    def test_starts_at_zero(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert c is not None, "simulate_migration() returned None"
        assert c[0] == 0.0

    def test_ends_at_one(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert abs(c[-1] - 1.0) < 1e-9

    def test_monotonic(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert all(b >= a for a, b in zip(c, c[1:]))

    def test_length(self):
        order = migration.plan_migration(PROFILE)
        assert len(migration.simulate_migration(PROFILE, order)) == len(order) + 1

    def test_first_port_is_the_biggest_jump(self):
        order = migration.plan_migration(PROFILE)
        c = migration.simulate_migration(PROFILE, order)
        jumps = [b - a for a, b in zip(c, c[1:])]
        assert jumps[0] == max(jumps)


class TestStepsToReach:
    def test_half(self):
        order = migration.plan_migration(PROFILE)
        c = migration.simulate_migration(PROFILE, order)
        # render alone is 5000 of 10000.
        assert migration.steps_to_reach(c, 0.5) == 1

    def test_ninety_percent(self):
        order = migration.plan_migration(PROFILE)
        c = migration.simulate_migration(PROFILE, order)
        assert migration.steps_to_reach(c, 0.9) == 3

    def test_zero_needs_nothing(self):
        c = migration.simulate_migration(PROFILE, migration.plan_migration(PROFILE))
        assert migration.steps_to_reach(c, 0.0) == 0

    def test_unreachable(self):
        assert migration.steps_to_reach([0.0, 0.5], 0.9) is None


class TestVerifyRunnable:
    def test_all_emulated_is_runnable(self):
        v = migration.verify_runnable(ALL, set(), ALL)
        assert v is not None, "verify_runnable() returned None"
        assert v == []

    def test_partially_ported_still_runnable(self):
        assert migration.verify_runnable(ALL, {"render"}, ALL) == []

    def test_all_ported_runnable(self):
        assert migration.verify_runnable(ALL, ALL, set()) == []

    def test_gap_detected(self):
        v = migration.verify_runnable(ALL, {"render"}, ALL - {"menu"})
        assert v == ["menu"]

    def test_sorted(self):
        v = migration.verify_runnable(ALL, set(), set())
        assert v == sorted(ALL)
''')

report()
