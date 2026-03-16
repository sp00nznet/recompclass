#ifndef D3D8_SHIM_H
#define D3D8_SHIM_H

#include <stdint.h>

/*
 * d3d8_shim.h -- Skeleton shim for Direct3D 8 functions.
 *
 * Each shimmed function logs its call into a global ring buffer so that
 * test code (and eventually a debugger UI) can inspect what the
 * recompiled game is doing.
 */

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

#define D3D_OK            0
#define SHIM_LOG_MAX      64   /* Maximum log entries before wrapping. */
#define SHIM_NAME_MAX     32   /* Max function name length.            */

/* ------------------------------------------------------------------ */
/*  Log entry                                                          */
/* ------------------------------------------------------------------ */

/*
 * Each call to a shimmed function produces one ShimLogEntry.
 * The args array stores up to 4 integer-width arguments; unused
 * slots are zero.
 */
typedef struct {
    char     func_name[SHIM_NAME_MAX];
    uint32_t args[4];
    int      arg_count;
} ShimLogEntry;

/* ------------------------------------------------------------------ */
/*  Global log state                                                   */
/* ------------------------------------------------------------------ */

extern ShimLogEntry g_shim_log[SHIM_LOG_MAX];
extern int          g_shim_log_count;

/* ------------------------------------------------------------------ */
/*  Log management                                                     */
/* ------------------------------------------------------------------ */

/* Reset the log (clear all entries and set count to 0). */
void shim_log_reset(void);

/* Return the most recent log entry, or NULL if the log is empty. */
const ShimLogEntry *shim_log_last(void);

/* Return log entry at index *i*, or NULL if out of range. */
const ShimLogEntry *shim_log_get(int i);

/* ------------------------------------------------------------------ */
/*  Shimmed D3D8 functions                                             */
/* ------------------------------------------------------------------ */

int shim_CreateDevice(int adapter, int device_type, void *window);
int shim_Clear(int count, int flags, uint32_t color, float z);
int shim_BeginScene(void);
int shim_EndScene(void);
int shim_Present(void);
int shim_SetTexture(int stage, uint32_t texture_handle);

#endif /* D3D8_SHIM_H */
