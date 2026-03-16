#ifndef BIOS_HLE_H
#define BIOS_HLE_H

#include <stdint.h>
#include <stddef.h>

/*
 * bios_hle.h -- GBA BIOS high-level emulation for recompilation.
 */

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

#define GBA_MEM_SIZE    (256 * 1024)   /* 256 KB simulated memory */

/* CpuSet control word bit positions. */
#define CPUSET_FIXED_SRC_BIT   (1 << 24)
#define CPUSET_WORD_SIZE_BIT   (1 << 26)
#define CPUSET_COUNT_MASK      0x001FFFFF

/* ------------------------------------------------------------------ */
/*  CPU state                                                          */
/* ------------------------------------------------------------------ */

typedef struct {
    uint32_t r[16];    /* r0-r15 (r13=sp, r14=lr, r15=pc) */
    uint8_t  mem[GBA_MEM_SIZE];
} GbaCpu;

/* ------------------------------------------------------------------ */
/*  BIOS HLE functions                                                 */
/* ------------------------------------------------------------------ */

/*
 * SWI 0x06: Integer Division
 *
 * Input:  r0 = numerator, r1 = denominator
 * Output: r0 = quotient (signed), r1 = remainder (signed),
 *         r3 = abs(quotient)
 *
 * If denominator is 0, behavior is undefined (set r0=0, r1=0, r3=0).
 */
void bios_div(GbaCpu *cpu);

/*
 * SWI 0x08: Square Root
 *
 * Input:  r0 = unsigned value
 * Output: r0 = floor(sqrt(value))
 */
void bios_sqrt(GbaCpu *cpu);

/*
 * SWI 0x0B: CpuSet
 *
 * Input:
 *   r0 = source address
 *   r1 = destination address
 *   r2 = control word:
 *     bits 20-0: count (number of copies)
 *     bit 24:    fixed source (fill mode)
 *     bit 26:    0 = 16-bit, 1 = 32-bit
 *
 * Copies or fills *count* units from src to dst in cpu->mem.
 */
void bios_cpuset(GbaCpu *cpu);

/*
 * SWI 0x0C: CpuFastSet
 *
 * Input: same as CpuSet, but always 32-bit.
 *   The count is rounded up to a multiple of 8.
 *   bit 24 controls fill mode.
 *
 * Copies or fills (rounded-up count) 32-bit words.
 */
void bios_cpufastset(GbaCpu *cpu);

/*
 * Dispatch a SWI call by number.
 * Returns 0 on success, -1 if the SWI number is not implemented.
 */
int bios_swi(GbaCpu *cpu, int swi_number);

#endif /* BIOS_HLE_H */
