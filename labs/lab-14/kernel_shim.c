#include "kernel_shim.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#else
#  include <time.h>
#  include <unistd.h>
#  include <sys/mman.h>
#endif

/*
 * kernel_shim.c -- Implementations of Xbox kernel shims.
 *
 * This file provides host-platform equivalents for a handful of Xbox 360
 * kernel functions.  Each function logs what it does so you can trace
 * the translation at runtime.
 */

/* ------------------------------------------------------------------ */
/*  Internal handle table                                              */
/* ------------------------------------------------------------------ */

/*
 * A very simple handle table.  Real implementations would use a hash map
 * or growable array.  We limit to 64 simultaneous handles for simplicity.
 */

#define MAX_HANDLES 64

typedef struct {
    int   in_use;
    void *host_object;   /* Pointer to whatever the handle represents. */
    int   type;          /* 0 = unused, 1 = memory, 2 = file, ... */
} HandleEntry;

static HandleEntry g_handle_table[MAX_HANDLES];

static ShimHandle handle_alloc(void *obj, int type)
{
    for (int i = 0; i < MAX_HANDLES; i++) {
        if (!g_handle_table[i].in_use) {
            g_handle_table[i].in_use      = 1;
            g_handle_table[i].host_object  = obj;
            g_handle_table[i].type         = type;
            return (ShimHandle)i;
        }
    }
    return SHIM_INVALID_HANDLE;
}

static int handle_free(ShimHandle h)
{
    if (h >= MAX_HANDLES || !g_handle_table[h].in_use)
        return SHIM_STATUS_INVALID_HANDLE;
    g_handle_table[h].in_use     = 0;
    g_handle_table[h].host_object = NULL;
    g_handle_table[h].type        = 0;
    return SHIM_STATUS_SUCCESS;
}

/* ------------------------------------------------------------------ */
/*  shim_init / shim_shutdown                                          */
/* ------------------------------------------------------------------ */

void shim_init(void)
{
    memset(g_handle_table, 0, sizeof(g_handle_table));
    printf("[shim] Kernel shim layer initialized.\n");
}

void shim_shutdown(void)
{
    /* Close any leaked handles. */
    for (int i = 0; i < MAX_HANDLES; i++) {
        if (g_handle_table[i].in_use) {
            printf("[shim] Warning: handle %d still open at shutdown.\n", i);
            g_handle_table[i].in_use = 0;
        }
    }
    printf("[shim] Kernel shim layer shut down.\n");
}

/* ------------------------------------------------------------------ */
/*  NtAllocateVirtualMemory                                            */
/* ------------------------------------------------------------------ */

int shim_NtAllocateVirtualMemory(void **out_ptr, size_t size)
{
    if (!out_ptr || size == 0)
        return SHIM_STATUS_INVALID_PARAM;

#ifdef _WIN32
    /*
     * On Windows, use VirtualAlloc to more closely match the Xbox kernel
     * behavior of reserving and committing virtual memory pages.
     */
    void *p = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
#else
    /*
     * On POSIX systems, a simple malloc suffices for this lab.
     * A more accurate shim would use mmap with MAP_ANONYMOUS.
     */
    void *p = malloc(size);
#endif

    if (!p) {
        printf("[shim] NtAllocateVirtualMemory: failed to allocate %zu bytes.\n", size);
        return SHIM_STATUS_NO_MEMORY;
    }

    /* Zero the memory (Xbox kernel guarantees zeroed pages). */
    memset(p, 0, size);

    printf("[shim] NtAllocateVirtualMemory: allocated %zu bytes at %p.\n", size, p);
    *out_ptr = p;
    return SHIM_STATUS_SUCCESS;
}

/* ------------------------------------------------------------------ */
/*  NtFreeVirtualMemory                                                */
/* ------------------------------------------------------------------ */

int shim_NtFreeVirtualMemory(void *ptr)
{
    if (!ptr)
        return SHIM_STATUS_INVALID_PARAM;

#ifdef _WIN32
    VirtualFree(ptr, 0, MEM_RELEASE);
#else
    free(ptr);
#endif

    printf("[shim] NtFreeVirtualMemory: freed %p.\n", ptr);
    return SHIM_STATUS_SUCCESS;
}

/* ------------------------------------------------------------------ */
/*  NtClose                                                            */
/* ------------------------------------------------------------------ */

int shim_NtClose(ShimHandle handle)
{
    int status = handle_free(handle);
    if (status == SHIM_STATUS_SUCCESS) {
        printf("[shim] NtClose: closed handle %u.\n", handle);
    } else {
        printf("[shim] NtClose: invalid handle %u.\n", handle);
    }
    return status;
}

/* ------------------------------------------------------------------ */
/*  KeQuerySystemTime                                                  */
/* ------------------------------------------------------------------ */

int shim_KeQuerySystemTime(uint64_t *out_time)
{
    if (!out_time)
        return SHIM_STATUS_INVALID_PARAM;

#ifdef _WIN32
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    /* FILETIME is already in 100ns intervals since 1601-01-01. */
    *out_time = ((uint64_t)ft.dwHighDateTime << 32) | ft.dwLowDateTime;
#else
    /*
     * On POSIX, get the time and convert to Windows FILETIME epoch.
     * The difference between the Unix epoch (1970-01-01) and the
     * FILETIME epoch (1601-01-01) is 11644473600 seconds.
     */
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);

    /* Convert to 100-nanosecond intervals. */
    uint64_t unix_100ns = (uint64_t)ts.tv_sec * 10000000ULL
                        + (uint64_t)ts.tv_nsec / 100ULL;
    /* Shift to FILETIME epoch. */
    *out_time = unix_100ns + 116444736000000000ULL;
#endif

    printf("[shim] KeQuerySystemTime: returned 0x%016llx.\n",
           (unsigned long long)*out_time);
    return SHIM_STATUS_SUCCESS;
}

/* ------------------------------------------------------------------ */
/*  TODO: NtCreateFile, NtReadFile, NtWriteFile                        */
/* ------------------------------------------------------------------ */

/*
 * TODO: Implement file I/O shims.
 *
 * NtCreateFile should:
 *   - Open or create a file using fopen (POSIX) or CreateFileA (Win32).
 *   - Allocate a handle via handle_alloc() and return it.
 *
 * NtReadFile / NtWriteFile should:
 *   - Look up the handle in the handle table.
 *   - Call fread/fwrite (or ReadFile/WriteFile on Win32).
 *   - Return the number of bytes transferred.
 */
