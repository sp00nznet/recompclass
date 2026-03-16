"""
Lab 39: PPC VMX128 Lifter

Lift Xbox 360 VMX128 SIMD instructions into C code with SSE intrinsics.
Each instruction is represented as a dict with op, vD, vA, vB, and
optionally vC fields.  Register numbers range from 0 to 127.
"""


# ---------------------------------------------------------------------------
# Helper function templates
# ---------------------------------------------------------------------------

# These are C helper functions that would be #included in the output.
# The lifter emits calls to them.

HELPER_FUNCTIONS = r"""
// --- VMX128 SSE helper functions ---
#include <xmmintrin.h>
#include <emmintrin.h>

static inline __m128 vdot3_sse(__m128 a, __m128 b) {
    __m128 t = _mm_mul_ps(a, b);
    __m128 mask = _mm_castsi128_ps(_mm_set_epi32(0, ~0, ~0, ~0));
    t = _mm_and_ps(t, mask);
    __m128 s1 = _mm_shuffle_ps(t, t, 0x4E);
    __m128 s2 = _mm_add_ps(t, s1);
    __m128 s3 = _mm_shuffle_ps(s2, s2, 0x11);
    return _mm_add_ps(s2, s3);
}

static inline __m128 vperm_sse(__m128 a, __m128 b, __m128 ctrl) {
    // Simplified element-level permute: ctrl lanes contain indices 0-7
    // 0-3 select from a, 4-7 select from b
    float sa[4], sb[4], sc[4], result[4];
    _mm_storeu_ps(sa, a);
    _mm_storeu_ps(sb, b);
    _mm_storeu_ps(sc, ctrl);
    float src[8];
    for (int i = 0; i < 4; i++) { src[i] = sa[i]; src[i+4] = sb[i]; }
    for (int i = 0; i < 4; i++) {
        int idx = (int)sc[i] & 7;
        result[i] = src[idx];
    }
    return _mm_loadu_ps(result);
}
"""


# ---------------------------------------------------------------------------
# Lifter functions -- complete the TODOs
# ---------------------------------------------------------------------------

def lift_vaddps(insn):
    """Lift a vaddps instruction to a C statement.

    Parameters
    ----------
    insn : dict
        {"op": "vaddps", "vD": int, "vA": int, "vB": int}

    Returns
    -------
    str
        C statement, e.g.: "vr[10] = _mm_add_ps(vr[1], vr[2]);"
    """
    # TODO: format and return the C statement using insn["vD"],
    # insn["vA"], insn["vB"].
    pass


def lift_vmulps(insn):
    """Lift a vmulps instruction to a C statement.

    Returns
    -------
    str
        C statement using _mm_mul_ps.
    """
    # TODO: same pattern as lift_vaddps but with _mm_mul_ps
    pass


def lift_vdot3(insn):
    """Lift a vdot3 instruction to a C statement.

    Uses the vdot3_sse helper function.

    Returns
    -------
    str
        C statement, e.g.: "vr[5] = vdot3_sse(vr[3], vr[4]);"
    """
    # TODO: emit a call to vdot3_sse(vr[vA], vr[vB])
    pass


def lift_vperm(insn):
    """Lift a vperm instruction to a C statement.

    Uses the vperm_sse helper function.  vperm has three source
    registers: vA, vB, vC.

    Returns
    -------
    str
        C statement, e.g.: "vr[6] = vperm_sse(vr[1], vr[2], vr[3]);"
    """
    # TODO: emit a call to vperm_sse(vr[vA], vr[vB], vr[vC])
    pass


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

LIFTERS = {
    "vaddps": lift_vaddps,
    "vmulps": lift_vmulps,
    "vdot3":  lift_vdot3,
    "vperm":  lift_vperm,
}


def lift_instruction(insn):
    """Lift a single VMX128 instruction to a C statement.

    Parameters
    ----------
    insn : dict
        Instruction with "op" and register fields.

    Returns
    -------
    str
        A single C statement string.

    Raises
    ------
    ValueError
        If the opcode is not recognized.
    """
    # TODO: look up insn["op"] in the LIFTERS dict and call the
    # corresponding function.  If the opcode is not found, raise
    # ValueError with a message like "Unknown opcode: xyz".
    pass


def lift_block(instructions):
    """Lift a list of instructions to a list of C statements.

    Parameters
    ----------
    instructions : list of dict

    Returns
    -------
    list of str
        One C statement per instruction.
    """
    # TODO: call lift_instruction on each item and collect results
    pass


def emit_function(name, instructions):
    """Emit a complete C function wrapping lifted instructions.

    The function signature is:
        void <name>(__m128 vr[128])

    Parameters
    ----------
    name : str
        Function name.
    instructions : list of dict
        Instructions to lift.

    Returns
    -------
    str
        Complete C function source.
    """
    # TODO: build a string containing:
    #   - The function signature
    #   - Opening brace
    #   - Each lifted statement indented with 4 spaces
    #   - Closing brace
    pass


# ---------------------------------------------------------------------------
# Vector math simulation (for testing)
# ---------------------------------------------------------------------------

def sim_vaddps(a, b):
    """Simulate vaddps: element-wise addition of two 4-float vectors."""
    return tuple(a[i] + b[i] for i in range(4))


def sim_vmulps(a, b):
    """Simulate vmulps: element-wise multiplication."""
    return tuple(a[i] * b[i] for i in range(4))


def sim_vdot3(a, b):
    """Simulate vdot3: dot product of xyz components, broadcast."""
    d = a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    return (d, d, d, d)


def sim_vperm(a, b, ctrl):
    """Simulate vperm: element-level permute from concat(a, b).

    ctrl elements are indices 0-7 (0-3 from a, 4-7 from b).
    """
    src = list(a) + list(b)
    return tuple(src[int(ctrl[i]) & 7] for i in range(4))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = [
        {"op": "vaddps", "vD": 10, "vA": 1, "vB": 2},
        {"op": "vmulps", "vD": 11, "vA": 3, "vB": 4},
        {"op": "vdot3",  "vD": 5,  "vA": 3, "vB": 4},
        {"op": "vperm",  "vD": 6,  "vA": 1, "vB": 2, "vC": 3},
    ]
    print(HELPER_FUNCTIONS)
    print(emit_function("vmx_block_0", sample))
