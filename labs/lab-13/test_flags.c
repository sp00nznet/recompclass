#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "flags.h"

/*
 * test_flags.c -- Test suite for the flag helper library.
 *
 * Each test checks that a specific operation produces the correct result
 * value AND the correct set of flags.  Pay close attention to the edge
 * cases -- these are exactly the situations that cause bugs in real
 * recompilers.
 */

static int tests_run    = 0;
static int tests_passed = 0;

#define CHECK(cond, msg)                                              \
    do {                                                              \
        tests_run++;                                                  \
        if (cond) {                                                   \
            tests_passed++;                                           \
        } else {                                                      \
            printf("  FAIL: %s\n", msg);                              \
        }                                                             \
    } while (0)

#define CHECK_RESULT(fr, exp_result, exp_flags, label)                \
    do {                                                              \
        CHECK((fr).result == (exp_result),                            \
              label ": expected result 0x" #exp_result);              \
        CHECK((fr).flags == (exp_flags),                              \
              label ": expected flags " #exp_flags                    \
              " got " );                                              \
    } while (0)

/* ------------------------------------------------------------------ */
/*  Addition tests                                                     */
/* ------------------------------------------------------------------ */

static void test_add(void)
{
    FlagResult8 r;

    printf("--- add_flags_u8 ---\n");

    /* Simple addition, no flags. */
    r = add_flags_u8(0x01, 0x02);
    CHECK(r.result == 0x03, "1+2 result");
    CHECK(r.flags == 0,     "1+2 no flags");

    /* 0xFF + 0x01 = 0x00 with carry, zero, half-carry. */
    r = add_flags_u8(0xFF, 0x01);
    CHECK(r.result == 0x00,               "FF+01 result=00");
    CHECK(r.flags & FLAG_Z,               "FF+01 zero set");
    CHECK(r.flags & FLAG_C,               "FF+01 carry set");
    CHECK(r.flags & FLAG_H,               "FF+01 half-carry set");

    /* 0x7F + 0x01 = 0x80: signed overflow (positive -> negative). */
    r = add_flags_u8(0x7F, 0x01);
    CHECK(r.result == 0x80,               "7F+01 result=80");
    CHECK(r.flags & FLAG_V,               "7F+01 overflow set");
    CHECK(r.flags & FLAG_N,               "7F+01 negative set");
    CHECK(r.flags & FLAG_H,               "7F+01 half-carry set");
    CHECK(!(r.flags & FLAG_C),            "7F+01 no carry");

    /* 0x0F + 0x01 = 0x10: half-carry only. */
    r = add_flags_u8(0x0F, 0x01);
    CHECK(r.result == 0x10,               "0F+01 result=10");
    CHECK(r.flags & FLAG_H,               "0F+01 half-carry set");
    CHECK(!(r.flags & FLAG_C),            "0F+01 no carry");
    CHECK(!(r.flags & FLAG_Z),            "0F+01 no zero");

    /* 0x00 + 0x00 = 0x00: zero flag. */
    r = add_flags_u8(0x00, 0x00);
    CHECK(r.result == 0x00,               "00+00 result=00");
    CHECK(r.flags & FLAG_Z,               "00+00 zero set");
    CHECK(!(r.flags & FLAG_C),            "00+00 no carry");

    /* 0x80 + 0x80 = 0x00: carry + overflow + zero. */
    r = add_flags_u8(0x80, 0x80);
    CHECK(r.result == 0x00,               "80+80 result=00");
    CHECK(r.flags & FLAG_Z,               "80+80 zero set");
    CHECK(r.flags & FLAG_C,               "80+80 carry set");
    CHECK(r.flags & FLAG_V,               "80+80 overflow set");
}

/* ------------------------------------------------------------------ */
/*  Subtraction tests                                                  */
/* ------------------------------------------------------------------ */

static void test_sub(void)
{
    FlagResult8 r;

    printf("--- sub_flags_u8 ---\n");

    /* Simple subtraction, no flags. */
    r = sub_flags_u8(0x05, 0x03);
    CHECK(r.result == 0x02, "5-3 result");
    CHECK(r.flags == 0,     "5-3 no flags");

    /* 0x00 - 0x01 = 0xFF: carry (borrow), negative. */
    r = sub_flags_u8(0x00, 0x01);
    CHECK(r.result == 0xFF,               "00-01 result=FF");
    CHECK(r.flags & FLAG_C,               "00-01 carry/borrow set");
    CHECK(r.flags & FLAG_N,               "00-01 negative set");
    CHECK(r.flags & FLAG_H,               "00-01 half-carry set");

    /* 0x80 - 0x01 = 0x7F: signed overflow (negative -> positive). */
    r = sub_flags_u8(0x80, 0x01);
    CHECK(r.result == 0x7F,               "80-01 result=7F");
    CHECK(r.flags & FLAG_V,               "80-01 overflow set");
    CHECK(!(r.flags & FLAG_N),            "80-01 not negative");

    /* 0x05 - 0x05 = 0x00: zero. */
    r = sub_flags_u8(0x05, 0x05);
    CHECK(r.result == 0x00,               "5-5 result=00");
    CHECK(r.flags & FLAG_Z,               "5-5 zero set");
    CHECK(!(r.flags & FLAG_C),            "5-5 no borrow");

    /* 0x10 - 0x01: half-borrow from nibble. */
    r = sub_flags_u8(0x10, 0x01);
    CHECK(r.result == 0x0F,               "10-01 result=0F");
    CHECK(r.flags & FLAG_H,               "10-01 half-carry set");
}

/* ------------------------------------------------------------------ */
/*  Logic tests                                                        */
/* ------------------------------------------------------------------ */

static void test_logic(void)
{
    FlagResult8 r;

    printf("--- logic flags ---\n");

    /* AND producing zero. */
    r = and_flags_u8(0xF0, 0x0F);
    CHECK(r.result == 0x00, "F0&0F result=00");
    CHECK(r.flags & FLAG_Z, "F0&0F zero set");

    /* AND producing negative. */
    r = and_flags_u8(0xFF, 0x80);
    CHECK(r.result == 0x80,    "FF&80 result=80");
    CHECK(r.flags & FLAG_N,    "FF&80 negative set");
    CHECK(!(r.flags & FLAG_C), "FF&80 no carry");
    CHECK(!(r.flags & FLAG_V), "FF&80 no overflow");

    /* OR. */
    r = or_flags_u8(0x00, 0x00);
    CHECK(r.result == 0x00, "00|00 result=00");
    CHECK(r.flags & FLAG_Z, "00|00 zero set");

    r = or_flags_u8(0xA0, 0x05);
    CHECK(r.result == 0xA5, "A0|05 result=A5");
    CHECK(r.flags & FLAG_N, "A0|05 negative set");

    /* XOR. */
    r = xor_flags_u8(0xFF, 0xFF);
    CHECK(r.result == 0x00, "FF^FF result=00");
    CHECK(r.flags & FLAG_Z, "FF^FF zero set");

    r = xor_flags_u8(0x0F, 0xF0);
    CHECK(r.result == 0xFF,    "0F^F0 result=FF");
    CHECK(r.flags & FLAG_N,    "0F^F0 negative set");
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("Flag Helper Library -- Test Suite\n\n");

    test_add();
    test_sub();
    test_logic();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
