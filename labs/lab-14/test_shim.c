#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "kernel_shim.h"

/*
 * test_shim.c -- Basic tests for the kernel shim layer.
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

/* ------------------------------------------------------------------ */
/*  Memory allocation tests                                            */
/* ------------------------------------------------------------------ */

static void test_alloc_free(void)
{
    printf("--- NtAllocateVirtualMemory / NtFreeVirtualMemory ---\n");

    void *ptr = NULL;
    int status;

    /* Basic allocation. */
    status = shim_NtAllocateVirtualMemory(&ptr, 4096);
    CHECK(status == SHIM_STATUS_SUCCESS, "alloc 4096 bytes succeeds");
    CHECK(ptr != NULL,                   "alloc returns non-NULL");

    /* Memory should be zeroed. */
    unsigned char *bytes = (unsigned char *)ptr;
    int all_zero = 1;
    for (int i = 0; i < 4096; i++) {
        if (bytes[i] != 0) { all_zero = 0; break; }
    }
    CHECK(all_zero, "allocated memory is zeroed");

    /* Write and read back. */
    memset(ptr, 0xAB, 4096);
    CHECK(bytes[0] == 0xAB && bytes[4095] == 0xAB, "can write to allocated memory");

    /* Free. */
    status = shim_NtFreeVirtualMemory(ptr);
    CHECK(status == SHIM_STATUS_SUCCESS, "free succeeds");

    /* Edge case: NULL pointer. */
    status = shim_NtAllocateVirtualMemory(NULL, 4096);
    CHECK(status == SHIM_STATUS_INVALID_PARAM, "alloc with NULL out_ptr fails");

    /* Edge case: zero size. */
    status = shim_NtAllocateVirtualMemory(&ptr, 0);
    CHECK(status == SHIM_STATUS_INVALID_PARAM, "alloc with zero size fails");
}

/* ------------------------------------------------------------------ */
/*  Handle / NtClose tests                                             */
/* ------------------------------------------------------------------ */

static void test_close(void)
{
    printf("--- NtClose ---\n");

    /* Closing an invalid handle should fail. */
    int status = shim_NtClose(SHIM_INVALID_HANDLE);
    CHECK(status == SHIM_STATUS_INVALID_HANDLE, "close invalid handle fails");

    /* Closing a handle that was never opened should also fail. */
    status = shim_NtClose(0);
    CHECK(status == SHIM_STATUS_INVALID_HANDLE, "close unused handle fails");
}

/* ------------------------------------------------------------------ */
/*  Time query tests                                                   */
/* ------------------------------------------------------------------ */

static void test_time(void)
{
    printf("--- KeQuerySystemTime ---\n");

    uint64_t t1 = 0, t2 = 0;
    int status;

    status = shim_KeQuerySystemTime(&t1);
    CHECK(status == SHIM_STATUS_SUCCESS, "query time succeeds");
    CHECK(t1 > 0, "time value is nonzero");

    /* Query again -- should be >= t1. */
    status = shim_KeQuerySystemTime(&t2);
    CHECK(status == SHIM_STATUS_SUCCESS, "second query succeeds");
    CHECK(t2 >= t1, "time is monotonically non-decreasing");

    /* NULL pointer. */
    status = shim_KeQuerySystemTime(NULL);
    CHECK(status == SHIM_STATUS_INVALID_PARAM, "query with NULL fails");
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("Kernel Shim -- Test Suite\n\n");

    shim_init();

    test_alloc_free();
    test_close();
    test_time();

    shim_shutdown();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
