#include "flags.h"
#include <stdio.h>

/*
 * flags.c -- Implementation of CPU flag computation helpers.
 *
 * STUDENT TASK: Fill in the function bodies below. Each function should
 * perform the specified operation, compute all relevant flags, and return
 * a FlagResult8 with both the result and the flags field populated.
 *
 * Hints:
 *   - To detect carry on 8-bit addition, promote operands to uint16_t
 *     and check bit 8 of the wide result.
 *   - Overflow occurs when two operands of the same sign produce a result
 *     of a different sign.
 *   - Half-carry checks the carry from bit 3 to bit 4.
 */

/* ------------------------------------------------------------------ */
/*  Internal helpers                                                   */
/* ------------------------------------------------------------------ */

/* Compute the common Z and N flags from an 8-bit result. */
static uint8_t zn_flags(uint8_t result)
{
    uint8_t f = 0;
    if (result == 0)
        f |= FLAG_Z;
    if (result & 0x80)
        f |= FLAG_N;
    return f;
}

/* ------------------------------------------------------------------ */
/*  8-bit arithmetic                                                   */
/* ------------------------------------------------------------------ */

FlagResult8 add_flags_u8(uint8_t a, uint8_t b)
{
    FlagResult8 r;

    /* Perform the addition in a wider type so we can observe the carry. */
    uint16_t wide = (uint16_t)a + (uint16_t)b;
    r.result = (uint8_t)wide;
    r.flags  = zn_flags(r.result);

    /* Carry: bit 8 of the wide result. */
    if (wide & 0x100)
        r.flags |= FLAG_C;

    /* Overflow: both operands same sign, result different sign. */
    if (~(a ^ b) & (a ^ r.result) & 0x80)
        r.flags |= FLAG_V;

    /* Half-carry: carry from bit 3 to bit 4. */
    if (((a & 0x0F) + (b & 0x0F)) & 0x10)
        r.flags |= FLAG_H;

    return r;
}

FlagResult8 sub_flags_u8(uint8_t a, uint8_t b)
{
    FlagResult8 r;

    r.result = a - b;
    r.flags  = zn_flags(r.result);

    /* Carry (borrow): set if b > a (unsigned). */
    if (b > a)
        r.flags |= FLAG_C;

    /* Overflow: operands of different sign, result sign differs from a. */
    if ((a ^ b) & (a ^ r.result) & 0x80)
        r.flags |= FLAG_V;

    /* Half-carry (half-borrow): borrow from bit 4. */
    if ((a & 0x0F) < (b & 0x0F))
        r.flags |= FLAG_H;

    return r;
}

FlagResult8 adc_flags_u8(uint8_t a, uint8_t b, bool carry_in)
{
    FlagResult8 r;
    uint16_t c  = carry_in ? 1 : 0;
    uint16_t wide = (uint16_t)a + (uint16_t)b + c;
    r.result = (uint8_t)wide;
    r.flags  = zn_flags(r.result);

    if (wide & 0x100)
        r.flags |= FLAG_C;

    if (~(a ^ b) & (a ^ r.result) & 0x80)
        r.flags |= FLAG_V;

    if (((a & 0x0F) + (b & 0x0F) + (uint8_t)c) & 0x10)
        r.flags |= FLAG_H;

    return r;
}

FlagResult8 sbc_flags_u8(uint8_t a, uint8_t b, bool carry_in)
{
    FlagResult8 r;
    uint16_t c  = carry_in ? 1 : 0;
    uint16_t wide = (uint16_t)a - (uint16_t)b - c;
    r.result = (uint8_t)wide;
    r.flags  = zn_flags(r.result);

    /* Carry (borrow). */
    if (wide & 0x100)
        r.flags |= FLAG_C;

    if ((a ^ b) & (a ^ r.result) & 0x80)
        r.flags |= FLAG_V;

    if ((a & 0x0F) < (b & 0x0F) + c)
        r.flags |= FLAG_H;

    return r;
}

/* ------------------------------------------------------------------ */
/*  8-bit logic                                                        */
/* ------------------------------------------------------------------ */

/*
 * For logic operations, carry and overflow are always cleared.
 * Only Z and N are meaningful.
 */

FlagResult8 and_flags_u8(uint8_t a, uint8_t b)
{
    FlagResult8 r;
    r.result = a & b;
    r.flags  = zn_flags(r.result);
    /* Some architectures (e.g., Z80) set half-carry on AND.  We leave it
     * cleared here; adjust if your target architecture differs. */
    return r;
}

FlagResult8 or_flags_u8(uint8_t a, uint8_t b)
{
    FlagResult8 r;
    r.result = a | b;
    r.flags  = zn_flags(r.result);
    return r;
}

FlagResult8 xor_flags_u8(uint8_t a, uint8_t b)
{
    FlagResult8 r;
    r.result = a ^ b;
    r.flags  = zn_flags(r.result);
    return r;
}

/* ------------------------------------------------------------------ */
/*  16-bit variants (TODO)                                             */
/* ------------------------------------------------------------------ */

/*
 * TODO: Implement add_flags_u16 and sub_flags_u16.  The logic is identical
 * to the 8-bit versions but operates on 16-bit values and checks bit 15
 * for sign/overflow and bit 16 for carry.  Use uint32_t as the wide type.
 */

/* ------------------------------------------------------------------ */
/*  Utility                                                            */
/* ------------------------------------------------------------------ */

const char *flags_to_string(uint8_t flags)
{
    /* Static buffer -- not thread-safe, but fine for educational use. */
    static char buf[6];
    int i = 0;
    buf[i++] = (flags & FLAG_Z) ? 'Z' : '.';
    buf[i++] = (flags & FLAG_C) ? 'C' : '.';
    buf[i++] = (flags & FLAG_V) ? 'V' : '.';
    buf[i++] = (flags & FLAG_N) ? 'N' : '.';
    buf[i++] = (flags & FLAG_H) ? 'H' : '.';
    buf[i]   = '\0';
    return buf;
}
