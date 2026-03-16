/*
 * endian_utils.c -- Byte-swap utilities for recompilation.
 *
 * Complete the TODO sections.
 */

#include "endian_utils.h"

/* ------------------------------------------------------------------ */
/*  Host endianness detection                                          */
/* ------------------------------------------------------------------ */

int host_is_little_endian(void)
{
    /* TODO: use the union trick to detect host endianness.
     *
     * union { uint16_t u; uint8_t b[2]; } test;
     * test.u = 1;
     * return test.b[0] == 1;   // LE: LSB is at lowest address
     */
    return 0;
}

/* ------------------------------------------------------------------ */
/*  Unconditional byte swaps                                           */
/* ------------------------------------------------------------------ */

uint16_t swap16(uint16_t x)
{
    /* TODO: swap the two bytes of a 16-bit value.
     *
     * Example: 0x1234 -> 0x3412
     *
     * Use bit shifts and OR:
     *   (x >> 8) | (x << 8)
     */
    return 0;
}

uint32_t swap32(uint32_t x)
{
    /* TODO: swap the four bytes of a 32-bit value.
     *
     * Example: 0x12345678 -> 0x78563412
     *
     * Use bit shifts, masks, and OR:
     *   ((x >> 24) & 0xFF)
     * | ((x >>  8) & 0xFF00)
     * | ((x <<  8) & 0xFF0000)
     * | ((x << 24) & 0xFF000000)
     */
    return 0;
}

uint64_t swap64(uint64_t x)
{
    /* TODO: swap the eight bytes of a 64-bit value.
     *
     * Example: 0x0123456789ABCDEF -> 0xEFCDAB8967452301
     *
     * One approach: swap the two 32-bit halves, then swap bytes
     * within each half:
     *   uint32_t hi = swap32((uint32_t)(x >> 32));
     *   uint32_t lo = swap32((uint32_t)(x & 0xFFFFFFFF));
     *   return ((uint64_t)lo << 32) | hi;
     */
    return 0;
}

/* ------------------------------------------------------------------ */
/*  Conditional swaps                                                  */
/* ------------------------------------------------------------------ */

uint16_t be16_to_host(uint16_t x)
{
    /* TODO: if host is little-endian, return swap16(x).
     * Otherwise return x unchanged.
     */
    return x;
}

uint32_t be32_to_host(uint32_t x)
{
    /* TODO: same pattern for 32-bit */
    return x;
}

uint64_t be64_to_host(uint64_t x)
{
    /* TODO: same pattern for 64-bit */
    return x;
}

/* ------------------------------------------------------------------ */
/*  Buffer swaps                                                       */
/* ------------------------------------------------------------------ */

void swap_buf16(void *buf, size_t count)
{
    /* TODO: treat buf as a uint16_t array.  Swap each element
     * in-place using swap16().
     */
}

void swap_buf32(void *buf, size_t count)
{
    /* TODO: treat buf as a uint32_t array.  Swap each element
     * in-place using swap32().
     */
}
