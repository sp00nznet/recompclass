# Lab 39: PPC VMX128 Lifter

## Objective

Lift a small set of Xbox 360 VMX128 (vector/SIMD) instructions into C code
that uses SSE intrinsics. The Xbox 360's Xenon CPU has a custom extension of
Altivec called VMX128 with 128 vector registers. Recompilation projects
must translate these into x86 SSE equivalents.

By the end of this lab you will be able to:

- Decode simplified VMX128 instruction representations
- Map PPC vector operations to SSE intrinsic equivalents
- Emit C source code that performs the same vector math

## Background

The Xbox 360 CPU (Xenon) is a PowerPC with VMX128 extensions -- an expanded
version of Altivec with 128 vector registers (vr0-vr127) instead of the
standard 32. Each register holds four 32-bit floats.

For recompilation we need to "lift" these instructions into C code that uses
x86 SSE intrinsics (`__m128` type from `<xmmintrin.h>`).

### Instructions to Lift

| VMX128 Mnemonic | Operation                        | SSE Equivalent              |
|-----------------|----------------------------------|-----------------------------|
| `vaddps`        | vD = vA + vB (per-element add)  | `_mm_add_ps(a, b)`         |
| `vmulps`        | vD = vA * vB (per-element mul)  | `_mm_mul_ps(a, b)`         |
| `vdot3`         | vD.xyzw = dot3(vA, vB)          | See notes below             |
| `vperm`         | vD = permute(vA, vB, vC)        | Simplified byte shuffle     |

### Dot Product (vdot3)

SSE does not have a single dot-product intrinsic before SSE4.1. For this
lab, use the multiply-and-horizontal-add pattern:

```c
// dot3(a, b) -> result broadcast to all lanes
__m128 t = _mm_mul_ps(a, b);                    // [ax*bx, ay*by, az*bz, aw*bw]
// mask out W component
__m128 mask = _mm_castsi128_ps(_mm_set_epi32(0, ~0, ~0, ~0));
t = _mm_and_ps(t, mask);                        // [ax*bx, ay*by, az*bz, 0]
__m128 s1 = _mm_shuffle_ps(t, t, 0x4E);         // swap pairs
__m128 s2 = _mm_add_ps(t, s1);
__m128 s3 = _mm_shuffle_ps(s2, s2, 0x11);
__m128 dot = _mm_add_ps(s2, s3);                // broadcast dot result
```

### Permute (vperm) -- Simplified

For this lab, `vperm` takes a permutation control vector (vC) where each
byte selects a byte from the concatenation of vA and vB (32 bytes total).
We simplify this to element-level (4 floats from A, 4 from B = 8 source
elements), with each control element being 0-7.

### Instruction Format

Instructions are provided as dicts:

```python
{"op": "vaddps", "vD": 10, "vA": 1, "vB": 2}
{"op": "vdot3",  "vD": 5,  "vA": 3, "vB": 4}
{"op": "vperm",  "vD": 6,  "vA": 1, "vB": 2, "vC": 3}
```

## Files

| File                | Description                          |
|---------------------|--------------------------------------|
| `vmx128_lifter.py`  | VMX128-to-SSE lifter (starter code) |
| `test_lab.py`        | Pytest test suite                   |

## Instructions

1. Open `vmx128_lifter.py` and read the starter code.
2. Complete each lifter function marked with `TODO`.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output (lifted C code)

```c
vr[10] = _mm_add_ps(vr[1], vr[2]);
vr[5] = vdot3_sse(vr[3], vr[4]);
vr[6] = vperm_sse(vr[1], vr[2], vr[3]);
```

## References

- Xbox 360 Programming and Performance (Microsoft)
- IBM VMX128 extensions documentation
- Intel Intrinsics Guide (SSE)
