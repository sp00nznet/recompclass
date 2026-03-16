/*
 * Lab 25: Z80 Runtime Environment
 *
 * Provides the register struct and memory array used by lifted Z80 code.
 * This file is complete -- do not modify it.
 */

#ifndef Z80_RUNTIME_H
#define Z80_RUNTIME_H

#include <stdint.h>
#include <string.h>

/* 64 KB address space, same as the real Z80 */
#define Z80_MEM_SIZE 65536

/* Z80 CPU state */
typedef struct {
    uint8_t  A;     /* Accumulator */
    uint8_t  B;     /* General-purpose register B */
    uint8_t  C;     /* General-purpose register C */
    uint8_t  D;     /* General-purpose register D */
    uint8_t  E;     /* General-purpose register E */
    uint8_t  H;     /* High byte of HL pair */
    uint8_t  L;     /* Low byte of HL pair */

    /* Flags */
    uint8_t  F_Z;   /* Zero flag (1 = result was zero) */
    uint8_t  F_N;   /* Subtract flag */
    uint8_t  F_H;   /* Half-carry flag */
    uint8_t  F_C;   /* Carry flag */
} z80_regs_t;

/* Memory */
extern uint8_t z80_mem[Z80_MEM_SIZE];

/* Helper: get the 16-bit HL register pair */
static inline uint16_t z80_get_HL(const z80_regs_t *regs) {
    return ((uint16_t)regs->H << 8) | regs->L;
}

/* Helper: set the 16-bit HL register pair */
static inline void z80_set_HL(z80_regs_t *regs, uint16_t val) {
    regs->H = (uint8_t)(val >> 8);
    regs->L = (uint8_t)(val & 0xFF);
}

/* Helper: initialize CPU state to all zeros */
static inline void z80_init(z80_regs_t *regs) {
    memset(regs, 0, sizeof(z80_regs_t));
    memset(z80_mem, 0, Z80_MEM_SIZE);
}

#endif /* Z80_RUNTIME_H */
