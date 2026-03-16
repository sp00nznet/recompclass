/*
 * bios_hle.c -- GBA BIOS high-level emulation.
 *
 * Complete the TODO sections.
 */

#include <string.h>
#include <math.h>
#include "bios_hle.h"

/* ------------------------------------------------------------------ */
/*  Internal helpers                                                   */
/* ------------------------------------------------------------------ */

/* Read a 16-bit value from cpu->mem at the given address. */
static uint16_t mem_read16(const GbaCpu *cpu, uint32_t addr)
{
    if (addr + 1 >= GBA_MEM_SIZE) return 0;
    return (uint16_t)(cpu->mem[addr] | (cpu->mem[addr + 1] << 8));
}

/* Write a 16-bit value to cpu->mem at the given address. */
static void mem_write16(GbaCpu *cpu, uint32_t addr, uint16_t val)
{
    if (addr + 1 >= GBA_MEM_SIZE) return;
    cpu->mem[addr]     = (uint8_t)(val & 0xFF);
    cpu->mem[addr + 1] = (uint8_t)((val >> 8) & 0xFF);
}

/* Read a 32-bit value from cpu->mem at the given address. */
static uint32_t mem_read32(const GbaCpu *cpu, uint32_t addr)
{
    if (addr + 3 >= GBA_MEM_SIZE) return 0;
    return (uint32_t)(cpu->mem[addr]
         | (cpu->mem[addr + 1] << 8)
         | (cpu->mem[addr + 2] << 16)
         | (cpu->mem[addr + 3] << 24));
}

/* Write a 32-bit value to cpu->mem at the given address. */
static void mem_write32(GbaCpu *cpu, uint32_t addr, uint32_t val)
{
    if (addr + 3 >= GBA_MEM_SIZE) return;
    cpu->mem[addr]     = (uint8_t)(val & 0xFF);
    cpu->mem[addr + 1] = (uint8_t)((val >> 8) & 0xFF);
    cpu->mem[addr + 2] = (uint8_t)((val >> 16) & 0xFF);
    cpu->mem[addr + 3] = (uint8_t)((val >> 24) & 0xFF);
}

/* ------------------------------------------------------------------ */
/*  SWI 0x06: Div                                                      */
/* ------------------------------------------------------------------ */

void bios_div(GbaCpu *cpu)
{
    /* TODO:
     * 1. Read numerator from r0 and denominator from r1.
     *    Treat both as signed 32-bit (cast to int32_t).
     * 2. If denominator is 0, set r0=r1=r3=0 and return.
     * 3. Compute quotient  = numerator / denominator.
     * 4. Compute remainder = numerator % denominator.
     * 5. Store quotient in r0, remainder in r1.
     * 6. Store abs(quotient) in r3.
     */
}

/* ------------------------------------------------------------------ */
/*  SWI 0x08: Sqrt                                                     */
/* ------------------------------------------------------------------ */

void bios_sqrt(GbaCpu *cpu)
{
    /* TODO:
     * 1. Read the unsigned value from r0.
     * 2. Compute floor(sqrt(value)).
     *    You can use: (uint32_t)sqrt((double)value)
     *    or an integer square root algorithm.
     * 3. Store the result back in r0.
     */
}

/* ------------------------------------------------------------------ */
/*  SWI 0x0B: CpuSet                                                   */
/* ------------------------------------------------------------------ */

void bios_cpuset(GbaCpu *cpu)
{
    /* TODO:
     * 1. Read src (r0), dst (r1), control (r2).
     * 2. Extract count     = control & CPUSET_COUNT_MASK.
     * 3. Extract fixed_src = control & CPUSET_FIXED_SRC_BIT.
     * 4. Extract word_size = control & CPUSET_WORD_SIZE_BIT.
     * 5. If word_size (32-bit mode):
     *    - For each of count iterations:
     *      a. Read a 32-bit value from src (using mem_read32).
     *      b. Write it to dst (using mem_write32).
     *      c. Advance dst by 4.
     *      d. If not fixed_src, advance src by 4.
     *    Else (16-bit mode):
     *    - Same but using mem_read16 / mem_write16, advancing by 2.
     */
}

/* ------------------------------------------------------------------ */
/*  SWI 0x0C: CpuFastSet                                               */
/* ------------------------------------------------------------------ */

void bios_cpufastset(GbaCpu *cpu)
{
    /* TODO:
     * 1. Read src (r0), dst (r1), control (r2).
     * 2. Extract count     = control & CPUSET_COUNT_MASK.
     * 3. Round count up to a multiple of 8:
     *    count = (count + 7) & ~7;
     * 4. Extract fixed_src = control & CPUSET_FIXED_SRC_BIT.
     * 5. Always 32-bit mode:
     *    - For each of count iterations:
     *      a. Read 32 bits from src.
     *      b. Write to dst.
     *      c. Advance dst by 4.
     *      d. If not fixed_src, advance src by 4.
     */
}

/* ------------------------------------------------------------------ */
/*  SWI dispatcher                                                     */
/* ------------------------------------------------------------------ */

int bios_swi(GbaCpu *cpu, int swi_number)
{
    /* TODO: dispatch to the appropriate function based on swi_number.
     *   0x06 -> bios_div
     *   0x08 -> bios_sqrt
     *   0x0B -> bios_cpuset
     *   0x0C -> bios_cpufastset
     * Return 0 on success, -1 if swi_number is unknown.
     */
    return -1;
}
