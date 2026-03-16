/*
 * test_trace.c -- Test suite for the register trace logger.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "trace_logger.h"

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

/* Static to avoid stack overflow -- TraceLogger is large. */
static TraceLogger logger;

static CpuRegs make_regs(uint32_t base)
{
    CpuRegs r;
    for (int i = 0; i < NUM_GPRS; i++) {
        r.r[i] = base + i;
    }
    r.sp = base + 0x100;
    r.lr = base + 0x200;
    r.pc = base + 0x300;
    return r;
}

/* ------------------------------------------------------------------ */
/*  trace_entry test                                                   */
/* ------------------------------------------------------------------ */

static void test_trace_entry(void)
{
    printf("--- test_trace_entry ---\n");
    trace_init(&logger);

    CpuRegs regs = make_regs(0);
    trace_entry(&logger, "func_a", &regs);

    CHECK(trace_count(&logger) == 1, "count is 1 after entry");

    const TraceEntry *e = trace_get(&logger, 0);
    CHECK(e != NULL, "entry 0 exists");
    CHECK(e->timestamp == 0, "timestamp is 0");
    CHECK(strcmp(e->func_name, "func_a") == 0, "func_name is func_a");
    CHECK(e->direction == TRACE_DIR_ENTRY, "direction is entry");
    CHECK(e->regs.r[0] == 0, "r0 is 0");
    CHECK(e->regs.sp == 0x100, "sp is 0x100");
}

/* ------------------------------------------------------------------ */
/*  trace_exit test                                                    */
/* ------------------------------------------------------------------ */

static void test_trace_exit(void)
{
    printf("--- test_trace_exit ---\n");
    trace_init(&logger);

    CpuRegs regs = make_regs(10);
    trace_exit(&logger, "func_b", &regs);

    const TraceEntry *e = trace_get(&logger, 0);
    CHECK(e != NULL, "entry exists");
    CHECK(e->direction == TRACE_DIR_EXIT, "direction is exit");
    CHECK(strcmp(e->func_name, "func_b") == 0, "func_name is func_b");
    CHECK(e->regs.r[0] == 10, "r0 is 10");
}

/* ------------------------------------------------------------------ */
/*  CSV output test                                                    */
/* ------------------------------------------------------------------ */

static void test_csv_output(void)
{
    printf("--- test_csv_output ---\n");
    trace_init(&logger);

    CpuRegs entry_regs = make_regs(0);
    CpuRegs exit_regs  = make_regs(100);

    trace_entry(&logger, "test_fn", &entry_regs);
    trace_exit(&logger, "test_fn", &exit_regs);

    /* Write to a temp buffer via tmpfile. */
    FILE *fp = tmpfile();
    CHECK(fp != NULL, "tmpfile created");

    int ret = trace_fwrite_csv(&logger, fp);
    CHECK(ret == 0, "fwrite_csv returns 0");

    /* Read back and verify. */
    fseek(fp, 0, SEEK_SET);
    char line[512];

    /* Header line. */
    char *got = fgets(line, sizeof(line), fp);
    CHECK(got != NULL, "header line read");
    CHECK(strstr(line, "timestamp") != NULL, "header has timestamp");
    CHECK(strstr(line, "function") != NULL, "header has function");
    CHECK(strstr(line, "r0") != NULL, "header has r0");

    /* Data line 1. */
    got = fgets(line, sizeof(line), fp);
    CHECK(got != NULL, "data line 1 read");
    CHECK(strstr(line, "test_fn") != NULL, "line 1 has func name");
    CHECK(strstr(line, "entry") != NULL, "line 1 has entry");

    /* Data line 2. */
    got = fgets(line, sizeof(line), fp);
    CHECK(got != NULL, "data line 2 read");
    CHECK(strstr(line, "exit") != NULL, "line 2 has exit");

    fclose(fp);
}

/* ------------------------------------------------------------------ */
/*  Multiple functions test                                            */
/* ------------------------------------------------------------------ */

static void test_multiple_functions(void)
{
    printf("--- test_multiple_functions ---\n");
    trace_init(&logger);

    CpuRegs r1 = make_regs(0);
    CpuRegs r2 = make_regs(50);
    CpuRegs r3 = make_regs(100);

    TRACE_ENTRY(&logger, "outer", &r1);
    TRACE_ENTRY(&logger, "inner", &r2);
    TRACE_EXIT(&logger, "inner", &r2);
    TRACE_EXIT(&logger, "outer", &r3);

    CHECK(trace_count(&logger) == 4, "count is 4");

    const TraceEntry *e0 = trace_get(&logger, 0);
    const TraceEntry *e1 = trace_get(&logger, 1);
    const TraceEntry *e2 = trace_get(&logger, 2);
    const TraceEntry *e3 = trace_get(&logger, 3);

    CHECK(e0->timestamp == 0, "timestamps increment: 0");
    CHECK(e1->timestamp == 1, "timestamps increment: 1");
    CHECK(e2->timestamp == 2, "timestamps increment: 2");
    CHECK(e3->timestamp == 3, "timestamps increment: 3");

    CHECK(strcmp(e0->func_name, "outer") == 0, "e0 is outer");
    CHECK(strcmp(e1->func_name, "inner") == 0, "e1 is inner");
    CHECK(e2->direction == TRACE_DIR_EXIT, "e2 is exit");
}

/* ------------------------------------------------------------------ */
/*  Buffer capacity test                                               */
/* ------------------------------------------------------------------ */

static void test_buffer_capacity(void)
{
    printf("--- test_buffer_capacity ---\n");
    trace_init(&logger);

    CpuRegs regs = make_regs(0);
    for (int i = 0; i < TRACE_MAX_ENTRIES + 10; i++) {
        trace_entry(&logger, "flood", &regs);
    }

    CHECK(trace_count(&logger) == TRACE_MAX_ENTRIES,
          "count capped at TRACE_MAX_ENTRIES");
    CHECK(trace_get(&logger, TRACE_MAX_ENTRIES) == NULL,
          "out-of-range returns NULL");
    CHECK(trace_get(&logger, TRACE_MAX_ENTRIES - 1) != NULL,
          "last valid entry accessible");
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("Register Trace Logger -- Test Suite\n\n");

    test_trace_entry();
    test_trace_exit();
    test_csv_output();
    test_multiple_functions();
    test_buffer_capacity();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
