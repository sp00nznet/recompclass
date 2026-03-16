/*
 * Tests for Lab 25: Hand-Lifted Z80 Subroutine
 *
 * Verifies that lifted_checksum() produces the same results
 * as the original Z80 code would.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "z80_runtime.h"

/* Defined in lifted.c */
extern void lifted_checksum(z80_regs_t *regs);

static int tests_passed = 0;
static int tests_total = 0;

static void run_checksum_test(const char *name,
                              const uint8_t *input, int count,
                              uint8_t expected) {
    z80_regs_t regs;
    uint16_t start_addr = 0x1000;

    z80_init(&regs);

    /* Load input data into memory */
    memcpy(&z80_mem[start_addr], input, count);

    /* Set up registers: HL = start address, B = count */
    z80_set_HL(&regs, start_addr);
    regs.B = (uint8_t)count;

    /* Run the lifted function */
    lifted_checksum(&regs);

    tests_total++;
    if (regs.A == expected) {
        printf("Test %s PASSED: checksum = %u\n", name, regs.A);
        tests_passed++;
    } else {
        printf("Test %s FAILED: expected %u, got %u\n",
               name, expected, regs.A);
    }
}

int main(void) {
    /* Test 1: Simple sequence [1,2,3,4,5] -> 15 */
    {
        uint8_t data[] = {1, 2, 3, 4, 5};
        run_checksum_test("1", data, 5, 15);
    }

    /* Test 2: Single byte [0xFF] -> 255 */
    {
        uint8_t data[] = {0xFF};
        run_checksum_test("2", data, 1, 255);
    }

    /* Test 3: All zeros [0,0,0] -> 0 */
    {
        uint8_t data[] = {0, 0, 0};
        run_checksum_test("3", data, 3, 0);
    }

    /* Test 4: Overflow wrapping [0x80, 0x80] -> 0x00 */
    {
        uint8_t data[] = {0x80, 0x80};
        run_checksum_test("4", data, 2, 0x00);
    }

    /* Test 5: Mixed values [0x10, 0x20, 0x30] -> 0x60 */
    {
        uint8_t data[] = {0x10, 0x20, 0x30};
        run_checksum_test("5", data, 3, 0x60);
    }

    /* Test 6: Verify HL advanced past the data */
    {
        z80_regs_t regs;
        uint16_t start = 0x2000;
        uint8_t data[] = {0x01, 0x02, 0x03};

        z80_init(&regs);
        memcpy(&z80_mem[start], data, 3);
        z80_set_HL(&regs, start);
        regs.B = 3;
        lifted_checksum(&regs);

        tests_total++;
        if (z80_get_HL(&regs) == start + 3) {
            printf("Test 6 PASSED: HL advanced correctly to 0x%04X\n",
                   z80_get_HL(&regs));
            tests_passed++;
        } else {
            printf("Test 6 FAILED: HL should be 0x%04X, got 0x%04X\n",
                   start + 3, z80_get_HL(&regs));
        }
    }

    /* Test 7: Verify B is zero after loop */
    {
        z80_regs_t regs;
        uint8_t data[] = {1, 2};

        z80_init(&regs);
        memcpy(&z80_mem[0x3000], data, 2);
        z80_set_HL(&regs, 0x3000);
        regs.B = 2;
        lifted_checksum(&regs);

        tests_total++;
        if (regs.B == 0) {
            printf("Test 7 PASSED: B == 0 after loop\n");
            tests_passed++;
        } else {
            printf("Test 7 FAILED: B should be 0, got %u\n", regs.B);
        }
    }

    /* Summary */
    printf("\n%d/%d tests passed", tests_passed, tests_total);
    if (tests_passed == tests_total) {
        printf(" -- All tests passed!\n");
    } else {
        printf(" -- SOME TESTS FAILED\n");
    }

    return (tests_passed == tests_total) ? 0 : 1;
}
