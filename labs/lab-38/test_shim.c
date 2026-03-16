/*
 * test_shim.c -- Test suite for the D3D8 shim skeleton.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "d3d8_shim.h"

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
/*  Tests                                                              */
/* ------------------------------------------------------------------ */

static void test_create_device(void)
{
    printf("--- test_create_device ---\n");
    shim_log_reset();

    int ret = shim_CreateDevice(0, 1, NULL);
    CHECK(ret == D3D_OK, "CreateDevice returns D3D_OK");
    CHECK(g_shim_log_count == 1, "log count is 1");

    const ShimLogEntry *e = shim_log_last();
    CHECK(e != NULL, "log entry exists");
    CHECK(strcmp(e->func_name, "CreateDevice") == 0, "func name is CreateDevice");
    CHECK(e->arg_count == 2, "arg_count is 2");
    CHECK(e->args[0] == 0, "adapter is 0");
    CHECK(e->args[1] == 1, "device_type is 1");
}

static void test_clear(void)
{
    printf("--- test_clear ---\n");
    shim_log_reset();

    int ret = shim_Clear(1, 0x03, 0xFF0000FF, 1.0f);
    CHECK(ret == D3D_OK, "Clear returns D3D_OK");

    const ShimLogEntry *e = shim_log_last();
    CHECK(e != NULL, "log entry exists");
    CHECK(strcmp(e->func_name, "Clear") == 0, "func name is Clear");
    CHECK(e->arg_count == 3, "arg_count is 3");
    CHECK(e->args[0] == 1, "count is 1");
    CHECK(e->args[1] == 0x03, "flags is 0x03");
    CHECK(e->args[2] == 0xFF0000FF, "color is 0xFF0000FF");
}

static void test_scene_lifecycle(void)
{
    printf("--- test_scene_lifecycle ---\n");
    shim_log_reset();

    CHECK(shim_BeginScene() == D3D_OK, "BeginScene returns D3D_OK");
    CHECK(shim_EndScene() == D3D_OK, "EndScene returns D3D_OK");
    CHECK(shim_Present() == D3D_OK, "Present returns D3D_OK");
    CHECK(g_shim_log_count == 3, "log count is 3");

    const ShimLogEntry *e0 = shim_log_get(0);
    const ShimLogEntry *e1 = shim_log_get(1);
    const ShimLogEntry *e2 = shim_log_get(2);

    CHECK(e0 != NULL && strcmp(e0->func_name, "BeginScene") == 0,
          "entry 0 is BeginScene");
    CHECK(e1 != NULL && strcmp(e1->func_name, "EndScene") == 0,
          "entry 1 is EndScene");
    CHECK(e2 != NULL && strcmp(e2->func_name, "Present") == 0,
          "entry 2 is Present");

    CHECK(e0->arg_count == 0, "BeginScene has 0 args");
    CHECK(e1->arg_count == 0, "EndScene has 0 args");
    CHECK(e2->arg_count == 0, "Present has 0 args");
}

static void test_set_texture(void)
{
    printf("--- test_set_texture ---\n");
    shim_log_reset();

    int ret = shim_SetTexture(2, 0xDEADBEEF);
    CHECK(ret == D3D_OK, "SetTexture returns D3D_OK");

    const ShimLogEntry *e = shim_log_last();
    CHECK(e != NULL, "log entry exists");
    CHECK(strcmp(e->func_name, "SetTexture") == 0, "func name is SetTexture");
    CHECK(e->args[0] == 2, "stage is 2");
    CHECK(e->args[1] == 0xDEADBEEF, "texture_handle is 0xDEADBEEF");
}

static void test_log_overflow(void)
{
    printf("--- test_log_overflow ---\n");
    shim_log_reset();

    /* Fill the log past capacity. */
    for (int i = 0; i < SHIM_LOG_MAX + 10; i++) {
        shim_BeginScene();
    }

    CHECK(g_shim_log_count == SHIM_LOG_MAX + 10,
          "log count tracks total calls");

    /* The last entry should still be valid. */
    const ShimLogEntry *e = shim_log_last();
    CHECK(e != NULL && strcmp(e->func_name, "BeginScene") == 0,
          "last entry after overflow is valid");

    /* shim_log_get with index >= SHIM_LOG_MAX should return NULL. */
    CHECK(shim_log_get(SHIM_LOG_MAX) == NULL,
          "out-of-range index returns NULL");
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("D3D8 Shim -- Test Suite\n\n");

    test_create_device();
    test_clear();
    test_scene_lifecycle();
    test_set_texture();
    test_log_overflow();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
