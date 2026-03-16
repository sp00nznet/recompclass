/*
 * test_bridge.c -- Test suite for the Cell DMA bridge.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dma_bridge.h"

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

/* Use static to avoid stack overflow (large struct). */
static DmaBridge bridge;

static void setup(void)
{
    int err = dma_bridge_init(&bridge, 1024 * 1024);
    if (err != DMA_OK) {
        fprintf(stderr, "Failed to init DMA bridge: %s\n", dma_strerror(err));
        exit(1);
    }
}

static void teardown(void)
{
    dma_bridge_destroy(&bridge);
}

/* ------------------------------------------------------------------ */
/*  DMA PUT test                                                       */
/* ------------------------------------------------------------------ */

static void test_dma_put(void)
{
    printf("--- test_dma_put ---\n");
    setup();

    /* Write pattern to main memory. */
    for (int i = 0; i < 256; i++) {
        bridge.main_mem[i] = (uint8_t)(i & 0xFF);
    }

    int err = dma_put(&bridge, 0, 0, 0, 256);
    CHECK(err == DMA_OK, "PUT 256 bytes succeeds");

    int match = 1;
    for (int i = 0; i < 256; i++) {
        if (bridge.ls[0][i] != (uint8_t)(i & 0xFF)) {
            match = 0;
            break;
        }
    }
    CHECK(match, "LS contents match after PUT");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  DMA GET test                                                       */
/* ------------------------------------------------------------------ */

static void test_dma_get(void)
{
    printf("--- test_dma_get ---\n");
    setup();

    /* Write pattern to LS. */
    for (int i = 0; i < 128; i++) {
        bridge.ls[0][i] = (uint8_t)(0xAA ^ i);
    }

    int err = dma_get(&bridge, 0, 0, 0x1000, 128);
    CHECK(err == DMA_OK, "GET 128 bytes succeeds");

    int match = 1;
    for (int i = 0; i < 128; i++) {
        if (bridge.main_mem[0x1000 + i] != (uint8_t)(0xAA ^ i)) {
            match = 0;
            break;
        }
    }
    CHECK(match, "main memory contents match after GET");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Round-trip test                                                     */
/* ------------------------------------------------------------------ */

static void test_round_trip(void)
{
    printf("--- test_round_trip ---\n");
    setup();

    uint8_t pattern[64];
    for (int i = 0; i < 64; i++) {
        pattern[i] = (uint8_t)(i * 7 + 3);
        bridge.main_mem[0x200 + i] = pattern[i];
    }

    /* PUT: main mem -> LS */
    int err = dma_put(&bridge, 0, 0x100, 0x200, 64);
    CHECK(err == DMA_OK, "round-trip PUT succeeds");

    /* Clear main memory region. */
    memset(&bridge.main_mem[0x200], 0, 64);

    /* GET: LS -> main mem */
    err = dma_get(&bridge, 0, 0x100, 0x200, 64);
    CHECK(err == DMA_OK, "round-trip GET succeeds");

    int match = (memcmp(&bridge.main_mem[0x200], pattern, 64) == 0);
    CHECK(match, "round-trip data integrity");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Alignment enforcement                                              */
/* ------------------------------------------------------------------ */

static void test_alignment_check(void)
{
    printf("--- test_alignment_check ---\n");
    setup();

    /* Misaligned LS offset. */
    int err = dma_put(&bridge, 0, 1, 0, 16);
    CHECK(err == DMA_ERR_ALIGN, "misaligned LS offset rejected");

    /* Misaligned EA. */
    err = dma_put(&bridge, 0, 0, 3, 16);
    CHECK(err == DMA_ERR_ALIGN, "misaligned EA rejected");

    /* Aligned -- should succeed. */
    err = dma_put(&bridge, 0, 0x10, 0x20, 16);
    CHECK(err == DMA_OK, "aligned transfer accepted");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Size enforcement                                                   */
/* ------------------------------------------------------------------ */

static void test_size_check(void)
{
    printf("--- test_size_check ---\n");
    setup();

    /* Zero size. */
    int err = dma_put(&bridge, 0, 0, 0, 0);
    CHECK(err == DMA_ERR_SIZE, "zero size rejected");

    /* Invalid size (not 1,2,4,8 or multiple of 16). */
    err = dma_put(&bridge, 0, 0, 0, 17);
    CHECK(err == DMA_ERR_SIZE, "size 17 rejected");

    err = dma_put(&bridge, 0, 0, 0, 100);
    CHECK(err == DMA_ERR_SIZE, "size 100 rejected");

    /* Over max. */
    err = dma_put(&bridge, 0, 0, 0, DMA_MAX_TRANSFER + 16);
    CHECK(err == DMA_ERR_SIZE, "over-max size rejected");

    /* Valid small sizes. */
    err = dma_put(&bridge, 0, 0, 0, 16);
    CHECK(err == DMA_OK, "size 16 accepted");

    err = dma_put(&bridge, 0, 0, 0, 256);
    CHECK(err == DMA_OK, "size 256 accepted");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Bounds enforcement                                                 */
/* ------------------------------------------------------------------ */

static void test_bounds_check(void)
{
    printf("--- test_bounds_check ---\n");
    setup();

    /* LS overflow. */
    int err = dma_put(&bridge, 0, SPU_LS_SIZE - 16, 0, 32);
    CHECK(err == DMA_ERR_BOUNDS, "LS overflow rejected");

    /* At exact end of LS. */
    err = dma_put(&bridge, 0, SPU_LS_SIZE - 16, 0, 16);
    CHECK(err == DMA_OK, "transfer at end of LS accepted");

    /* Main memory overflow. */
    err = dma_put(&bridge, 0, 0, bridge.main_mem_size - 16, 32);
    CHECK(err == DMA_ERR_BOUNDS, "main memory overflow rejected");

    /* Invalid SPU ID. */
    err = dma_put(&bridge, MAX_SPUS, 0, 0, 16);
    CHECK(err == DMA_ERR_SPU_ID, "invalid SPU ID rejected");

    err = dma_put(&bridge, -1, 0, 0, 16);
    CHECK(err == DMA_ERR_SPU_ID, "negative SPU ID rejected");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Multi-SPU test                                                     */
/* ------------------------------------------------------------------ */

static void test_multi_spu(void)
{
    printf("--- test_multi_spu ---\n");
    setup();

    /* Write different patterns to two SPU local stores via main memory. */
    memset(bridge.main_mem, 0xAA, 16);
    dma_put(&bridge, 0, 0, 0, 16);

    memset(bridge.main_mem, 0xBB, 16);
    dma_put(&bridge, 1, 0, 0, 16);

    /* Verify each SPU has its own data. */
    int ok0 = 1, ok1 = 1;
    for (int i = 0; i < 16; i++) {
        if (bridge.ls[0][i] != 0xAA) ok0 = 0;
        if (bridge.ls[1][i] != 0xBB) ok1 = 0;
    }
    CHECK(ok0, "SPU 0 has correct data (0xAA)");
    CHECK(ok1, "SPU 1 has correct data (0xBB)");

    /* DMA wait should succeed for valid SPU IDs. */
    CHECK(dma_wait(&bridge, 0) == DMA_OK, "wait on SPU 0 OK");
    CHECK(dma_wait(&bridge, 5) == DMA_OK, "wait on SPU 5 OK");
    CHECK(dma_wait(&bridge, 6) == DMA_ERR_SPU_ID, "wait on SPU 6 rejected");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("Cell DMA Bridge -- Test Suite\n\n");

    test_dma_put();
    test_dma_get();
    test_round_trip();
    test_alignment_check();
    test_size_check();
    test_bounds_check();
    test_multi_spu();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
