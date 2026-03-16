/*
 * test_bios.c -- Test suite for GBA BIOS HLE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "bios_hle.h"

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

/* Static to avoid stack overflow (GbaCpu is large). */
static GbaCpu cpu;

static void reset_cpu(void)
{
    memset(&cpu, 0, sizeof(cpu));
}

/* ------------------------------------------------------------------ */
/*  Div tests                                                          */
/* ------------------------------------------------------------------ */

static void test_div(void)
{
    printf("--- test_div ---\n");
    reset_cpu();

    /* 100 / 7 = 14 remainder 2 */
    cpu.r[0] = 100;
    cpu.r[1] = 7;
    bios_div(&cpu);
    CHECK(cpu.r[0] == 14,  "100/7 quotient is 14");
    CHECK(cpu.r[1] == 2,   "100/7 remainder is 2");
    CHECK(cpu.r[3] == 14,  "abs(quotient) is 14");

    /* Exact division: 20 / 5 = 4 remainder 0 */
    reset_cpu();
    cpu.r[0] = 20;
    cpu.r[1] = 5;
    bios_div(&cpu);
    CHECK(cpu.r[0] == 4,   "20/5 quotient is 4");
    CHECK(cpu.r[1] == 0,   "20/5 remainder is 0");

    /* Divide by zero: should set all to 0 */
    reset_cpu();
    cpu.r[0] = 42;
    cpu.r[1] = 0;
    bios_div(&cpu);
    CHECK(cpu.r[0] == 0, "div by zero: r0 = 0");
    CHECK(cpu.r[1] == 0, "div by zero: r1 = 0");
    CHECK(cpu.r[3] == 0, "div by zero: r3 = 0");
}

static void test_div_negative(void)
{
    printf("--- test_div_negative ---\n");
    reset_cpu();

    /* -100 / 7 = -14 remainder -2 (C truncation) */
    cpu.r[0] = (uint32_t)(-100);
    cpu.r[1] = 7;
    bios_div(&cpu);
    CHECK((int32_t)cpu.r[0] == -14,  "-100/7 quotient is -14");
    CHECK((int32_t)cpu.r[1] == -2,   "-100/7 remainder is -2");
    CHECK(cpu.r[3] == 14,            "abs(quotient) is 14");

    /* 100 / -3 = -33 remainder 1 */
    reset_cpu();
    cpu.r[0] = 100;
    cpu.r[1] = (uint32_t)(-3);
    bios_div(&cpu);
    CHECK((int32_t)cpu.r[0] == -33,  "100/-3 quotient is -33");
    CHECK((int32_t)cpu.r[1] == 1,    "100/-3 remainder is 1");
    CHECK(cpu.r[3] == 33,            "abs(quotient) is 33");
}

/* ------------------------------------------------------------------ */
/*  Sqrt tests                                                         */
/* ------------------------------------------------------------------ */

static void test_sqrt(void)
{
    printf("--- test_sqrt ---\n");
    reset_cpu();

    cpu.r[0] = 0;
    bios_sqrt(&cpu);
    CHECK(cpu.r[0] == 0, "sqrt(0) = 0");

    cpu.r[0] = 1;
    bios_sqrt(&cpu);
    CHECK(cpu.r[0] == 1, "sqrt(1) = 1");

    cpu.r[0] = 4;
    bios_sqrt(&cpu);
    CHECK(cpu.r[0] == 2, "sqrt(4) = 2");

    cpu.r[0] = 9;
    bios_sqrt(&cpu);
    CHECK(cpu.r[0] == 3, "sqrt(9) = 3");

    cpu.r[0] = 10;
    bios_sqrt(&cpu);
    CHECK(cpu.r[0] == 3, "sqrt(10) = 3 (floor)");

    cpu.r[0] = 65536;
    bios_sqrt(&cpu);
    CHECK(cpu.r[0] == 256, "sqrt(65536) = 256");

    cpu.r[0] = 100000;
    bios_sqrt(&cpu);
    CHECK(cpu.r[0] == 316, "sqrt(100000) = 316 (floor)");
}

/* ------------------------------------------------------------------ */
/*  CpuSet copy test                                                   */
/* ------------------------------------------------------------------ */

static void test_cpuset_copy(void)
{
    printf("--- test_cpuset_copy ---\n");
    reset_cpu();

    /* Write source data: 4 x 32-bit words at address 0x100. */
    uint32_t src_addr = 0x100;
    uint32_t dst_addr = 0x200;
    for (int i = 0; i < 4; i++) {
        uint32_t val = 0xDEAD0000 | i;
        cpu.mem[src_addr + i*4 + 0] = (uint8_t)(val);
        cpu.mem[src_addr + i*4 + 1] = (uint8_t)(val >> 8);
        cpu.mem[src_addr + i*4 + 2] = (uint8_t)(val >> 16);
        cpu.mem[src_addr + i*4 + 3] = (uint8_t)(val >> 24);
    }

    cpu.r[0] = src_addr;
    cpu.r[1] = dst_addr;
    /* count=4, 32-bit mode, copy mode */
    cpu.r[2] = 4 | CPUSET_WORD_SIZE_BIT;
    bios_cpuset(&cpu);

    /* Verify destination. */
    int match = 1;
    for (int i = 0; i < 4; i++) {
        uint32_t expected = 0xDEAD0000 | i;
        uint32_t got = (uint32_t)(
            cpu.mem[dst_addr + i*4] |
            (cpu.mem[dst_addr + i*4 + 1] << 8) |
            (cpu.mem[dst_addr + i*4 + 2] << 16) |
            (cpu.mem[dst_addr + i*4 + 3] << 24));
        if (got != expected) { match = 0; break; }
    }
    CHECK(match, "CpuSet 32-bit copy data matches");
}

/* ------------------------------------------------------------------ */
/*  CpuSet fill test                                                   */
/* ------------------------------------------------------------------ */

static void test_cpuset_fill(void)
{
    printf("--- test_cpuset_fill ---\n");
    reset_cpu();

    uint32_t src_addr = 0x100;
    uint32_t dst_addr = 0x300;
    uint32_t fill_val = 0xCAFEBABE;

    /* Write fill value at source. */
    cpu.mem[src_addr + 0] = (uint8_t)(fill_val);
    cpu.mem[src_addr + 1] = (uint8_t)(fill_val >> 8);
    cpu.mem[src_addr + 2] = (uint8_t)(fill_val >> 16);
    cpu.mem[src_addr + 3] = (uint8_t)(fill_val >> 24);

    cpu.r[0] = src_addr;
    cpu.r[1] = dst_addr;
    /* count=8, 32-bit mode, fixed source (fill) */
    cpu.r[2] = 8 | CPUSET_WORD_SIZE_BIT | CPUSET_FIXED_SRC_BIT;
    bios_cpuset(&cpu);

    /* All 8 words at dst should be 0xCAFEBABE. */
    int match = 1;
    for (int i = 0; i < 8; i++) {
        uint32_t got = (uint32_t)(
            cpu.mem[dst_addr + i*4] |
            (cpu.mem[dst_addr + i*4 + 1] << 8) |
            (cpu.mem[dst_addr + i*4 + 2] << 16) |
            (cpu.mem[dst_addr + i*4 + 3] << 24));
        if (got != fill_val) { match = 0; break; }
    }
    CHECK(match, "CpuSet 32-bit fill all words match");
}

/* ------------------------------------------------------------------ */
/*  CpuFastSet copy test                                               */
/* ------------------------------------------------------------------ */

static void test_cpufastset_copy(void)
{
    printf("--- test_cpufastset_copy ---\n");
    reset_cpu();

    uint32_t src_addr = 0x1000;
    uint32_t dst_addr = 0x2000;

    /* Write 10 words at source (will be rounded up to 16). */
    for (int i = 0; i < 16; i++) {
        uint32_t val = 0xBEEF0000 | i;
        cpu.mem[src_addr + i*4 + 0] = (uint8_t)(val);
        cpu.mem[src_addr + i*4 + 1] = (uint8_t)(val >> 8);
        cpu.mem[src_addr + i*4 + 2] = (uint8_t)(val >> 16);
        cpu.mem[src_addr + i*4 + 3] = (uint8_t)(val >> 24);
    }

    cpu.r[0] = src_addr;
    cpu.r[1] = dst_addr;
    /* count=10 -> rounds up to 16, copy mode */
    cpu.r[2] = 10;
    bios_cpufastset(&cpu);

    /* Verify first 10 words copied, and that rounding didn't cause issues. */
    int match = 1;
    for (int i = 0; i < 10; i++) {
        uint32_t expected = 0xBEEF0000 | i;
        uint32_t got = (uint32_t)(
            cpu.mem[dst_addr + i*4] |
            (cpu.mem[dst_addr + i*4 + 1] << 8) |
            (cpu.mem[dst_addr + i*4 + 2] << 16) |
            (cpu.mem[dst_addr + i*4 + 3] << 24));
        if (got != expected) { match = 0; break; }
    }
    CHECK(match, "CpuFastSet copy first 10 words correct");
}

/* ------------------------------------------------------------------ */
/*  CpuFastSet fill test                                               */
/* ------------------------------------------------------------------ */

static void test_cpufastset_fill(void)
{
    printf("--- test_cpufastset_fill ---\n");
    reset_cpu();

    uint32_t src_addr = 0x1000;
    uint32_t dst_addr = 0x3000;
    uint32_t fill_val = 0x12345678;

    cpu.mem[src_addr + 0] = (uint8_t)(fill_val);
    cpu.mem[src_addr + 1] = (uint8_t)(fill_val >> 8);
    cpu.mem[src_addr + 2] = (uint8_t)(fill_val >> 16);
    cpu.mem[src_addr + 3] = (uint8_t)(fill_val >> 24);

    cpu.r[0] = src_addr;
    cpu.r[1] = dst_addr;
    /* count=5 -> rounds to 8, fill mode */
    cpu.r[2] = 5 | CPUSET_FIXED_SRC_BIT;
    bios_cpufastset(&cpu);

    /* All 8 words at dst should be fill_val. */
    int match = 1;
    for (int i = 0; i < 8; i++) {
        uint32_t got = (uint32_t)(
            cpu.mem[dst_addr + i*4] |
            (cpu.mem[dst_addr + i*4 + 1] << 8) |
            (cpu.mem[dst_addr + i*4 + 2] << 16) |
            (cpu.mem[dst_addr + i*4 + 3] << 24));
        if (got != fill_val) { match = 0; break; }
    }
    CHECK(match, "CpuFastSet fill 8 words (rounded from 5) match");
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("GBA BIOS HLE -- Test Suite\n\n");

    test_div();
    test_div_negative();
    test_sqrt();
    test_cpuset_copy();
    test_cpuset_fill();
    test_cpufastset_copy();
    test_cpufastset_fill();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
