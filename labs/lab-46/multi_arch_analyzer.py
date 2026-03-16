"""
Lab 46: Capstone Multi-Arch Analyzer

Auto-detect the CPU architecture of a binary blob by trying multiple
Capstone disassembly configurations.
"""

try:
    from capstone import (
        Cs, CS_ARCH_X86, CS_ARCH_ARM, CS_ARCH_ARM64, CS_ARCH_MIPS,
        CS_ARCH_PPC, CS_MODE_32, CS_MODE_64, CS_MODE_ARM, CS_MODE_THUMB,
        CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN, CS_MODE_LITTLE_ENDIAN,
    )
    HAS_CAPSTONE = True
except ImportError:
    HAS_CAPSTONE = False

# ---------------------------------------------------------------------------
# Architecture candidates
# ---------------------------------------------------------------------------

# Each candidate is (name, arch_const, mode_const).
# Used when Capstone is available.
CANDIDATES = []
if HAS_CAPSTONE:
    CANDIDATES = [
        ("x86_32",    CS_ARCH_X86,   CS_MODE_32),
        ("x86_64",    CS_ARCH_X86,   CS_MODE_64),
        ("arm32",     CS_ARCH_ARM,   CS_MODE_ARM),
        ("arm_thumb", CS_ARCH_ARM,   CS_MODE_THUMB),
        ("arm64",     CS_ARCH_ARM64, CS_MODE_ARM),
        ("mips32_be", CS_ARCH_MIPS,  CS_MODE_MIPS32 | CS_MODE_BIG_ENDIAN),
        ("mips32_le", CS_ARCH_MIPS,  CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN),
        ("ppc32_be",  CS_ARCH_PPC,   CS_MODE_32 | CS_MODE_BIG_ENDIAN),
    ]


# ---------------------------------------------------------------------------
# Scoring functions -- complete the TODOs
# ---------------------------------------------------------------------------

def compute_score(decoded_bytes, total_bytes, num_instructions):
    """Compute a disassembly quality score.

    Parameters
    ----------
    decoded_bytes : int
        Total bytes that were part of valid instructions.
    total_bytes : int
        Total bytes in the input blob.
    num_instructions : int
        Number of successfully decoded instructions.

    Returns
    -------
    dict with keys:
        "byte_ratio"      : float  -- decoded_bytes / total_bytes (0.0 if total is 0)
        "num_instructions" : int
        "decoded_bytes"    : int
    """
    # TODO: compute and return the score dict
    pass


def try_disassemble(data, arch, mode):
    """Try disassembling *data* with the given Capstone arch/mode.

    Parameters
    ----------
    data : bytes
        Raw binary data.
    arch : int
        Capstone architecture constant (e.g. CS_ARCH_X86).
    mode : int
        Capstone mode constant (e.g. CS_MODE_32).

    Returns
    -------
    dict
        Score dict from compute_score.

    Requires Capstone to be installed.
    """
    # TODO:
    # 1. Create a Capstone disassembler: Cs(arch, mode)
    # 2. Disassemble all of data: list(md.disasm(data, 0))
    # 3. Sum up the sizes of decoded instructions (insn.size).
    # 4. Return compute_score(decoded_bytes, len(data), num_instructions).
    pass


def analyze(data, candidates=None):
    """Analyze a binary blob and return ranked architecture guesses.

    Parameters
    ----------
    data : bytes
        Raw binary data to analyze.
    candidates : list of tuple, optional
        Override the default CANDIDATES list.  Each tuple is
        (name, arch, mode).

    Returns
    -------
    list of dict
        Sorted by byte_ratio descending (then num_instructions desc).
        Each dict has:
            "name"             : str
            "byte_ratio"       : float
            "num_instructions" : int
            "decoded_bytes"    : int
    """
    # TODO:
    # 1. If candidates is None, use CANDIDATES.
    # 2. For each candidate, call try_disassemble and collect results.
    # 3. Sort results by (-byte_ratio, -num_instructions).
    # 4. Return the sorted list.
    pass


def best_guess(data, candidates=None):
    """Return the best architecture guess for *data*.

    Returns
    -------
    dict or None
        The top-ranked result from analyze(), or None if no candidates.
    """
    # TODO: call analyze() and return the first result
    pass


# ---------------------------------------------------------------------------
# Mock disassembly (for testing without Capstone)
# ---------------------------------------------------------------------------

def compute_score_from_mock(insn_sizes, total_bytes):
    """Compute a score from a list of instruction sizes.

    This allows testing the scoring logic without Capstone.

    Parameters
    ----------
    insn_sizes : list of int
        Size of each decoded instruction.
    total_bytes : int
        Total input size.

    Returns
    -------
    dict
        Score dict.
    """
    decoded = sum(insn_sizes)
    return compute_score(decoded, total_bytes, len(insn_sizes))


def rank_mock_results(results):
    """Rank a list of (name, score_dict) tuples.

    Parameters
    ----------
    results : list of (str, dict)

    Returns
    -------
    list of dict
        Sorted by (-byte_ratio, -num_instructions), with "name" added.
    """
    # TODO: build result dicts with "name" key, sort, return
    pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python multi_arch_analyzer.py <binary_file>")
        sys.exit(1)

    if not HAS_CAPSTONE:
        print("Error: capstone package not installed (pip install capstone)")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        blob = f.read()

    results = analyze(blob)
    print(f"Analyzing {len(blob)} bytes...\n")
    for i, r in enumerate(results):
        print(f"  {i+1}. {r['name']:<12s}  "
              f"ratio={r['byte_ratio']:.3f}  "
              f"insns={r['num_instructions']}  "
              f"decoded={r['decoded_bytes']}")
    if results:
        print(f"\nBest guess: {results[0]['name']}")
