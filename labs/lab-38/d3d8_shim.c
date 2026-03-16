/*
 * d3d8_shim.c -- Skeleton shim for Direct3D 8 functions.
 *
 * Each function logs its call into the global log buffer and returns
 * D3D_OK.  Complete the TODO sections.
 */

#include <string.h>
#include <stdio.h>
#include "d3d8_shim.h"

/* ------------------------------------------------------------------ */
/*  Global log state                                                   */
/* ------------------------------------------------------------------ */

ShimLogEntry g_shim_log[SHIM_LOG_MAX];
int          g_shim_log_count = 0;

/* ------------------------------------------------------------------ */
/*  Internal: append a log entry                                       */
/* ------------------------------------------------------------------ */

/*
 * Record a function call in the log.
 *
 * If the log is full (g_shim_log_count == SHIM_LOG_MAX), wrap around
 * to index 0 (ring buffer), but keep incrementing g_shim_log_count so
 * callers know how many total calls have been made.
 *
 * Parameters:
 *   name      -- function name (copied into entry, truncated if needed)
 *   args      -- pointer to an array of up to 4 uint32_t values
 *   arg_count -- how many args are valid (0-4)
 */
static void log_call(const char *name, const uint32_t *args, int arg_count)
{
    /* TODO: calculate the ring-buffer index from g_shim_log_count.
     *
     * Steps:
     *   1. Compute idx = g_shim_log_count % SHIM_LOG_MAX.
     *   2. Copy *name* into g_shim_log[idx].func_name (use strncpy,
     *      make sure it is null-terminated).
     *   3. Zero out the args array, then copy arg_count values from
     *      *args* into g_shim_log[idx].args.
     *   4. Set g_shim_log[idx].arg_count = arg_count.
     *   5. Increment g_shim_log_count.
     */
}

/* ------------------------------------------------------------------ */
/*  Log management                                                     */
/* ------------------------------------------------------------------ */

void shim_log_reset(void)
{
    /* TODO: zero out g_shim_log and reset g_shim_log_count to 0. */
}

const ShimLogEntry *shim_log_last(void)
{
    /* TODO: return a pointer to the most recent entry, or NULL if
     * the log is empty.
     *
     * Hint: the most recent entry is at index
     *       (g_shim_log_count - 1) % SHIM_LOG_MAX.
     */
    return NULL;
}

const ShimLogEntry *shim_log_get(int i)
{
    /* TODO: return a pointer to entry *i*, or NULL if i is out of
     * range [0, min(g_shim_log_count, SHIM_LOG_MAX)).
     */
    return NULL;
}

/* ------------------------------------------------------------------ */
/*  Shimmed functions                                                  */
/* ------------------------------------------------------------------ */

int shim_CreateDevice(int adapter, int device_type, void *window)
{
    /* TODO: log this call with name "CreateDevice" and two args:
     *   args[0] = adapter
     *   args[1] = device_type
     * (We skip the window pointer for logging simplicity.)
     * Return D3D_OK.
     */
    return D3D_OK;
}

int shim_Clear(int count, int flags, uint32_t color, float z)
{
    /* TODO: log this call with name "Clear" and three args:
     *   args[0] = count
     *   args[1] = flags
     *   args[2] = color
     * (We skip the float z for simplicity.)
     * Return D3D_OK.
     */
    return D3D_OK;
}

int shim_BeginScene(void)
{
    /* TODO: log with name "BeginScene", 0 args.  Return D3D_OK. */
    return D3D_OK;
}

int shim_EndScene(void)
{
    /* TODO: log with name "EndScene", 0 args.  Return D3D_OK. */
    return D3D_OK;
}

int shim_Present(void)
{
    /* TODO: log with name "Present", 0 args.  Return D3D_OK. */
    return D3D_OK;
}

int shim_SetTexture(int stage, uint32_t texture_handle)
{
    /* TODO: log with name "SetTexture" and two args:
     *   args[0] = stage
     *   args[1] = texture_handle
     * Return D3D_OK.
     */
    return D3D_OK;
}
