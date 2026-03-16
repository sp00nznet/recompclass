#ifndef ENDIAN_UTILS_H
#define ENDIAN_UTILS_H

#include <stdint.h>
#include <stddef.h>

/*
 * endian_utils.h -- Byte-swap utilities for big-endian / little-endian
 * conversion in recompilation projects.
 */

/* ------------------------------------------------------------------ */
/*  Host endianness detection                                          */
/* ------------------------------------------------------------------ */

/*
 * Returns 1 if the host is little-endian, 0 if big-endian.
 * Uses a runtime check (union trick).
 */
int host_is_little_endian(void);

/* ------------------------------------------------------------------ */
/*  Unconditional byte swaps                                           */
/* ------------------------------------------------------------------ */

uint16_t swap16(uint16_t x);
uint32_t swap32(uint32_t x);
uint64_t swap64(uint64_t x);

/* ------------------------------------------------------------------ */
/*  Conditional swaps (big-endian to host)                             */
/* ------------------------------------------------------------------ */

/*
 * Convert a big-endian value to host byte order.
 * If host is little-endian, swaps bytes.
 * If host is big-endian, returns unchanged.
 */
uint16_t be16_to_host(uint16_t x);
uint32_t be32_to_host(uint32_t x);
uint64_t be64_to_host(uint64_t x);

/* ------------------------------------------------------------------ */
/*  Buffer swaps (in-place)                                            */
/* ------------------------------------------------------------------ */

/*
 * Swap *count* 16-bit values starting at *buf* in-place.
 * buf must point to at least count * 2 bytes.
 */
void swap_buf16(void *buf, size_t count);

/*
 * Swap *count* 32-bit values starting at *buf* in-place.
 * buf must point to at least count * 4 bytes.
 */
void swap_buf32(void *buf, size_t count);

#endif /* ENDIAN_UTILS_H */
