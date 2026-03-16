/*
 * test_endian.c -- Test suite for endianness conversion utilities.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "endian_utils.h"

static int tests_run    = 0;
static int tests_passed = 0;

#define CHECK(cond, msg)                                     \
    do {                                                     \
        tests_run++;                                         \
        if (cond) {                                          \
            tests_passed++;                                  \
        } else {                                             \
            printf("  FAIL: %s\n", (msg));                   \
        }                                                    \
    } while (0)

/* ------------------------------------------------------------------ */
/*  swap16                                                             */
/* ------------------------------------------------------------------ */

static void test_swap16(void)
{
    printf("--- test_swap16 ---\n");
    CHECK(swap16(0x1234) == 0x3412, "0x1234 -> 0x3412");
    CHECK(swap16(0x0001) == 0x0100, "0x0001 -> 0x0100");
    CHECK(swap16(0xFF00) == 0x00FF, "0xFF00 -> 0x00FF");
    CHECK(swap16(0x0000) == 0x0000, "0x0000 -> 0x0000");
    CHECK(swap16(0xFFFF) == 0xFFFF, "0xFFFF -> 0xFFFF");
    CHECK(swap16(0xABCD) == 0xCDAB, "0xABCD -> 0xCDAB");
}

/* ------------------------------------------------------------------ */
/*  swap32                                                             */
/* ------------------------------------------------------------------ */

static void test_swap32(void)
{
    printf("--- test_swap32 ---\n");
    CHECK(swap32(0x12345678) == 0x78563412, "0x12345678 -> 0x78563412");
    CHECK(swap32(0x00000001) == 0x01000000, "0x00000001 -> 0x01000000");
    CHECK(swap32(0xFF000000) == 0x000000FF, "0xFF000000 -> 0x000000FF");
    CHECK(swap32(0x00000000) == 0x00000000, "zero unchanged");
    CHECK(swap32(0xDEADBEEF) == 0xEFBEADDE, "0xDEADBEEF -> 0xEFBEADDE");
}

/* ------------------------------------------------------------------ */
/*  swap64                                                             */
/* ------------------------------------------------------------------ */

static void test_swap64(void)
{
    printf("--- test_swap64 ---\n");
    CHECK(swap64(0x0123456789ABCDEFULL) == 0xEFCDAB8967452301ULL,
          "full 64-bit swap");
    CHECK(swap64(0x0000000000000001ULL) == 0x0100000000000000ULL,
          "0x01 -> high byte");
    CHECK(swap64(0) == 0, "zero unchanged");
}

/* ------------------------------------------------------------------ */
/*  Conditional swap (BE to host)                                      */
/* ------------------------------------------------------------------ */

static void test_conditional_swap(void)
{
    printf("--- test_conditional_swap ---\n");

    int is_le = host_is_little_endian();

    if (is_le) {
        /* On LE host, be_to_host should swap. */
        CHECK(be16_to_host(0x1234) == 0x3412,
              "be16_to_host swaps on LE host");
        CHECK(be32_to_host(0x12345678) == 0x78563412,
              "be32_to_host swaps on LE host");
        CHECK(be64_to_host(0x0123456789ABCDEFULL) == 0xEFCDAB8967452301ULL,
              "be64_to_host swaps on LE host");
    } else {
        /* On BE host, be_to_host should be a no-op. */
        CHECK(be16_to_host(0x1234) == 0x1234,
              "be16_to_host no-op on BE host");
        CHECK(be32_to_host(0x12345678) == 0x12345678,
              "be32_to_host no-op on BE host");
        CHECK(be64_to_host(0x0123456789ABCDEFULL) == 0x0123456789ABCDEFULL,
              "be64_to_host no-op on BE host");
    }

    printf("  (host is %s-endian)\n", is_le ? "little" : "big");
}

/* ------------------------------------------------------------------ */
/*  Buffer swap 16                                                     */
/* ------------------------------------------------------------------ */

static void test_swap_buf16(void)
{
    printf("--- test_swap_buf16 ---\n");

    uint16_t buf[] = {0x1234, 0x5678, 0xABCD};
    swap_buf16(buf, 3);
    CHECK(buf[0] == 0x3412, "buf[0] swapped");
    CHECK(buf[1] == 0x7856, "buf[1] swapped");
    CHECK(buf[2] == 0xCDAB, "buf[2] swapped");

    /* Swap back. */
    swap_buf16(buf, 3);
    CHECK(buf[0] == 0x1234, "buf[0] restored");
    CHECK(buf[1] == 0x5678, "buf[1] restored");
}

/* ------------------------------------------------------------------ */
/*  Buffer swap 32                                                     */
/* ------------------------------------------------------------------ */

static void test_swap_buf32(void)
{
    printf("--- test_swap_buf32 ---\n");

    uint32_t buf[] = {0x12345678, 0xDEADBEEF};
    swap_buf32(buf, 2);
    CHECK(buf[0] == 0x78563412, "buf[0] swapped");
    CHECK(buf[1] == 0xEFBEADDE, "buf[1] swapped");

    /* Swap back. */
    swap_buf32(buf, 2);
    CHECK(buf[0] == 0x12345678, "buf[0] restored");
}

/* ------------------------------------------------------------------ */
/*  Round-trip: swap twice = identity                                  */
/* ------------------------------------------------------------------ */

static void test_round_trip(void)
{
    printf("--- test_round_trip ---\n");

    CHECK(swap16(swap16(0x1234)) == 0x1234, "swap16 round-trip");
    CHECK(swap32(swap32(0x12345678)) == 0x12345678, "swap32 round-trip");
    CHECK(swap64(swap64(0x0123456789ABCDEFULL)) == 0x0123456789ABCDEFULL,
          "swap64 round-trip");

    uint32_t buf[] = {0xCAFEBABE, 0x01020304, 0xFFFFFFFF};
    uint32_t orig[3];
    memcpy(orig, buf, sizeof(buf));
    swap_buf32(buf, 3);
    swap_buf32(buf, 3);
    CHECK(memcmp(buf, orig, sizeof(buf)) == 0, "buf32 round-trip");
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("Endianness Utils -- Test Suite\n\n");

    test_swap16();
    test_swap32();
    test_swap64();
    test_conditional_swap();
    test_swap_buf16();
    test_swap_buf32();
    test_round_trip();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
