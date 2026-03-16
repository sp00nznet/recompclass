#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "spu_sim.h"

/*
 * test_spu.c -- Test suite for the SPU DMA simulator.
 *
 * Tests cover:
 *   - Basic DMA GET and PUT transfers.
 *   - Alignment enforcement.
 *   - Size constraint enforcement.
 *   - Bounds checking.
 *   - DMA list (scatter-gather) transfers.
 *   - Round-trip data integrity.
 */

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

/* Shared context -- large struct, so static to avoid stack overflow. */
static SpuContext ctx;

/* ------------------------------------------------------------------ */
/*  Setup / teardown                                                   */
/* ------------------------------------------------------------------ */

static void setup(void)
{
    /* 1 MB of simulated main memory. */
    int err = spu_init(&ctx, 1024 * 1024);
    if (err != SPU_OK) {
        fprintf(stderr, "Failed to init SPU context: %s\n", spu_strerror(err));
        exit(1);
    }
}

static void teardown(void)
{
    spu_destroy(&ctx);
}

/* ------------------------------------------------------------------ */
/*  Basic DMA GET test                                                 */
/* ------------------------------------------------------------------ */

static void test_dma_get_basic(void)
{
    printf("--- test_dma_get_basic ---\n");
    setup();

    /* Write a known pattern into main memory. */
    for (int i = 0; i < 256; i++) {
        ctx.main_mem[i] = (uint8_t)(i & 0xFF);
    }

    /* DMA GET 256 bytes from main memory offset 0 to LS offset 0. */
    int err = spu_dma_get(&ctx, 0, 0, 256, 0);
    CHECK(err == SPU_OK, "DMA GET 256 bytes succeeds");

    /* Verify local store contents match. */
    int match = 1;
    for (int i = 0; i < 256; i++) {
        if (ctx.ls[i] != (uint8_t)(i & 0xFF)) {
            match = 0;
            break;
        }
    }
    CHECK(match, "LS contents match main memory after GET");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Basic DMA PUT test                                                 */
/* ------------------------------------------------------------------ */

static void test_dma_put_basic(void)
{
    printf("--- test_dma_put_basic ---\n");
    setup();

    /* Write a pattern into the local store. */
    for (int i = 0; i < 128; i++) {
        ctx.ls[i] = (uint8_t)(0xAA ^ i);
    }

    /* DMA PUT 128 bytes from LS offset 0 to main memory offset 0x100. */
    int err = spu_dma_put(&ctx, 0, 0x100, 128, 1);
    CHECK(err == SPU_OK, "DMA PUT 128 bytes succeeds");

    /* Verify main memory contents. */
    int match = 1;
    for (int i = 0; i < 128; i++) {
        if (ctx.main_mem[0x100 + i] != (uint8_t)(0xAA ^ i)) {
            match = 0;
            break;
        }
    }
    CHECK(match, "main memory contents match LS after PUT");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Round-trip test (PUT then GET)                                     */
/* ------------------------------------------------------------------ */

static void test_round_trip(void)
{
    printf("--- test_round_trip ---\n");
    setup();

    /* Write data to LS, PUT to main memory, clear LS, GET back. */
    uint8_t pattern[64];
    for (int i = 0; i < 64; i++) {
        pattern[i] = (uint8_t)(i * 3 + 7);
        ctx.ls[i] = pattern[i];
    }

    int err;
    err = spu_dma_put(&ctx, 0, 0x200, 64, 2);
    CHECK(err == SPU_OK, "round-trip PUT succeeds");

    /* Clear the LS region. */
    memset(ctx.ls, 0, 64);

    err = spu_dma_get(&ctx, 0, 0x200, 64, 2);
    CHECK(err == SPU_OK, "round-trip GET succeeds");

    int match = (memcmp(ctx.ls, pattern, 64) == 0);
    CHECK(match, "round-trip data integrity preserved");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Alignment enforcement                                              */
/* ------------------------------------------------------------------ */

static void test_alignment(void)
{
    printf("--- test_alignment ---\n");
    setup();

    /* Misaligned LS offset. */
    int err = spu_dma_get(&ctx, 1, 0, 16, 0);
    CHECK(err == SPU_ERR_ALIGN, "misaligned LS offset rejected");

    /* Misaligned EA. */
    err = spu_dma_get(&ctx, 0, 3, 16, 0);
    CHECK(err == SPU_ERR_ALIGN, "misaligned EA rejected");

    /* Both aligned -- should succeed. */
    err = spu_dma_get(&ctx, 0x10, 0x20, 16, 0);
    CHECK(err == SPU_OK, "aligned offsets accepted");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Size constraint enforcement                                        */
/* ------------------------------------------------------------------ */

static void test_size_constraints(void)
{
    printf("--- test_size_constraints ---\n");
    setup();

    /* Zero size. */
    int err = spu_dma_get(&ctx, 0, 0, 0, 0);
    CHECK(err == SPU_ERR_SIZE, "zero size rejected");

    /* Non-multiple of 16. */
    err = spu_dma_get(&ctx, 0, 0, 17, 0);
    CHECK(err == SPU_ERR_SIZE, "size 17 (not multiple of 16) rejected");

    err = spu_dma_get(&ctx, 0, 0, 100, 0);
    CHECK(err == SPU_ERR_SIZE, "size 100 (not multiple of 16) rejected");

    /* Exceeds max single transfer size. */
    err = spu_dma_get(&ctx, 0, 0, SPU_DMA_MAX_SIZE + 16, 0);
    CHECK(err == SPU_ERR_SIZE, "size exceeding 16KB rejected");

    /* Valid sizes. */
    err = spu_dma_get(&ctx, 0, 0, 16, 0);
    CHECK(err == SPU_OK, "size 16 accepted");

    err = spu_dma_get(&ctx, 0, 0, 256, 0);
    CHECK(err == SPU_OK, "size 256 accepted");

    err = spu_dma_get(&ctx, 0, 0, SPU_DMA_MAX_SIZE, 0);
    CHECK(err == SPU_OK, "max size (16KB) accepted");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Bounds checking                                                    */
/* ------------------------------------------------------------------ */

static void test_bounds(void)
{
    printf("--- test_bounds ---\n");
    setup();

    /* LS overflow. */
    int err = spu_dma_get(&ctx, SPU_LS_SIZE - 16, 0, 32, 0);
    CHECK(err == SPU_ERR_BOUNDS, "LS overflow rejected");

    /* At exact end of LS. */
    err = spu_dma_get(&ctx, SPU_LS_SIZE - 16, 0, 16, 0);
    CHECK(err == SPU_OK, "transfer at end of LS accepted");

    /* Main memory overflow. */
    err = spu_dma_get(&ctx, 0, ctx.main_mem_size - 16, 32, 0);
    CHECK(err == SPU_ERR_BOUNDS, "main memory overflow rejected");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Tag validation                                                     */
/* ------------------------------------------------------------------ */

static void test_tags(void)
{
    printf("--- test_tags ---\n");
    setup();

    /* Valid tags. */
    int err = spu_dma_get(&ctx, 0, 0, 16, 0);
    CHECK(err == SPU_OK, "tag 0 accepted");

    err = spu_dma_get(&ctx, 0, 0, 16, 31);
    CHECK(err == SPU_OK, "tag 31 accepted");

    /* Invalid tag. */
    err = spu_dma_get(&ctx, 0, 0, 16, 32);
    CHECK(err == SPU_ERR_TAG, "tag 32 rejected");

    err = spu_dma_get(&ctx, 0, 0, 16, 100);
    CHECK(err == SPU_ERR_TAG, "tag 100 rejected");

    /* Wait for tag. */
    err = spu_dma_wait_tag(&ctx, 0);
    CHECK(err == SPU_OK, "wait on tag 0 succeeds");

    err = spu_dma_wait_tag(&ctx, 32);
    CHECK(err == SPU_ERR_TAG, "wait on tag 32 rejected");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  DMA list (scatter-gather) test                                     */
/* ------------------------------------------------------------------ */

static void test_dma_list(void)
{
    printf("--- test_dma_list ---\n");
    setup();

    /* Set up two regions in main memory with different data. */
    memset(&ctx.main_mem[0x000], 0xAA, 32);
    memset(&ctx.main_mem[0x100], 0xBB, 48);

    /* Build a DMA list that gathers both regions into contiguous LS. */
    SpuDmaListEntry list[2];
    list[0].ea   = 0x000;
    list[0].size = 32;
    list[1].ea   = 0x100;
    list[1].size = 48;

    int err = spu_dma_list_get(&ctx, 0, list, 2, 5);
    CHECK(err == SPU_OK, "DMA list GET succeeds");

    /* Verify: LS[0..31] should be 0xAA, LS[32..79] should be 0xBB. */
    int match_aa = 1, match_bb = 1;
    for (int i = 0; i < 32; i++) {
        if (ctx.ls[i] != 0xAA) { match_aa = 0; break; }
    }
    for (int i = 32; i < 80; i++) {
        if (ctx.ls[i] != 0xBB) { match_bb = 0; break; }
    }
    CHECK(match_aa, "first list segment data correct (0xAA)");
    CHECK(match_bb, "second list segment data correct (0xBB)");

    /* Test list PUT. */
    memset(ctx.ls, 0xCC, 32);
    SpuDmaListEntry put_list[1];
    put_list[0].ea   = 0x300;
    put_list[0].size = 32;

    err = spu_dma_list_put(&ctx, 0, put_list, 1, 6);
    CHECK(err == SPU_OK, "DMA list PUT succeeds");

    int match_cc = 1;
    for (int i = 0; i < 32; i++) {
        if (ctx.main_mem[0x300 + i] != 0xCC) { match_cc = 0; break; }
    }
    CHECK(match_cc, "list PUT data written correctly");

    /* Invalid: too many list entries. */
    SpuDmaListEntry big_list[SPU_DMA_LIST_MAX + 1];
    err = spu_dma_list_get(&ctx, 0, big_list, SPU_DMA_LIST_MAX + 1, 0);
    CHECK(err == SPU_ERR_LIST_SIZE, "oversized list rejected");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Large transfer test                                                */
/* ------------------------------------------------------------------ */

static void test_large_transfer(void)
{
    printf("--- test_large_transfer ---\n");
    setup();

    /* Fill main memory with a pattern and transfer a full 16KB block. */
    for (int i = 0; i < SPU_DMA_MAX_SIZE; i++) {
        ctx.main_mem[i] = (uint8_t)(i % 251);  /* Prime modulus for variety. */
    }

    int err = spu_dma_get(&ctx, 0, 0, SPU_DMA_MAX_SIZE, 10);
    CHECK(err == SPU_OK, "16KB GET succeeds");

    int match = 1;
    for (int i = 0; i < SPU_DMA_MAX_SIZE; i++) {
        if (ctx.ls[i] != (uint8_t)(i % 251)) {
            match = 0;
            break;
        }
    }
    CHECK(match, "16KB transfer data integrity");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  DMA log test                                                       */
/* ------------------------------------------------------------------ */

static void test_dma_log(void)
{
    printf("--- test_dma_log ---\n");
    setup();

    spu_dma_get(&ctx, 0, 0, 16, 0);
    spu_dma_put(&ctx, 0, 0, 16, 1);

    CHECK(ctx.dma_log_count == 2, "DMA log recorded 2 transfers");
    CHECK(ctx.dma_log[0].direction == SPU_DMA_GET, "first transfer is GET");
    CHECK(ctx.dma_log[1].direction == SPU_DMA_PUT, "second transfer is PUT");

    teardown();
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("SPU DMA Simulator -- Test Suite\n\n");

    test_dma_get_basic();
    test_dma_put_basic();
    test_round_trip();
    test_alignment();
    test_size_constraints();
    test_bounds();
    test_tags();
    test_dma_list();
    test_large_transfer();
    test_dma_log();

    printf("\n");
    spu_dump_dma_log(&ctx);  /* Show log from last test for demonstration. */

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
