#ifndef KERNEL_SHIM_H
#define KERNEL_SHIM_H

#include <stdint.h>
#include <stddef.h>

/*
 * kernel_shim.h -- Simplified Xbox kernel function shims.
 *
 * Each shim mirrors a kernel export but uses host-friendly types.
 * Return values use a simplified status code (0 = success, nonzero = error).
 */

/* Status codes (simplified from NTSTATUS). */
#define SHIM_STATUS_SUCCESS        0
#define SHIM_STATUS_NO_MEMORY      1
#define SHIM_STATUS_INVALID_HANDLE 2
#define SHIM_STATUS_INVALID_PARAM  3
#define SHIM_STATUS_NOT_IMPL       0xFF

/* Opaque handle type matching Xbox 360's 32-bit HANDLE. */
typedef uint32_t ShimHandle;

#define SHIM_INVALID_HANDLE  ((ShimHandle)0xFFFFFFFF)

/* ------------------------------------------------------------------ */
/*  Memory management                                                  */
/* ------------------------------------------------------------------ */

/*
 * Shim for NtAllocateVirtualMemory.
 *
 * Allocates `size` bytes of memory and writes the pointer to `*out_ptr`.
 * On Xbox 360 this would reserve/commit pages in the virtual address space.
 * Here we simply use malloc (or VirtualAlloc on Windows).
 *
 * Returns SHIM_STATUS_SUCCESS or SHIM_STATUS_NO_MEMORY.
 */
int shim_NtAllocateVirtualMemory(void **out_ptr, size_t size);

/*
 * Shim for NtFreeVirtualMemory.
 *
 * Frees memory previously allocated by shim_NtAllocateVirtualMemory.
 */
int shim_NtFreeVirtualMemory(void *ptr);

/* ------------------------------------------------------------------ */
/*  Handle management                                                  */
/* ------------------------------------------------------------------ */

/*
 * Shim for NtClose.
 *
 * Closes an opaque handle.  In this simplified version, the handle is
 * an index into an internal table.
 */
int shim_NtClose(ShimHandle handle);

/* ------------------------------------------------------------------ */
/*  Time                                                               */
/* ------------------------------------------------------------------ */

/*
 * Shim for KeQuerySystemTime.
 *
 * Returns the current system time as a 64-bit value representing
 * 100-nanosecond intervals since January 1, 1601 (Windows FILETIME epoch).
 */
int shim_KeQuerySystemTime(uint64_t *out_time);

/* ------------------------------------------------------------------ */
/*  TODO: File I/O shims                                               */
/* ------------------------------------------------------------------ */

/* int shim_NtCreateFile(ShimHandle *out_handle, const char *path, int access); */
/* int shim_NtReadFile(ShimHandle handle, void *buffer, size_t size, size_t *bytes_read); */
/* int shim_NtWriteFile(ShimHandle handle, const void *buffer, size_t size, size_t *bytes_written); */

/* ------------------------------------------------------------------ */
/*  Initialization / cleanup                                           */
/* ------------------------------------------------------------------ */

/* Initialize the shim layer (call once at startup). */
void shim_init(void);

/* Tear down the shim layer (call once at shutdown). */
void shim_shutdown(void);

#endif /* KERNEL_SHIM_H */
