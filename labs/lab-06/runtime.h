/*
 * Lab 6: Mini-GB Recomp -- Runtime Header
 *
 * Defines the CPU context, memory bus interface, and flag helper macros
 * used by the generated recompiled code.
 */

#ifndef RUNTIME_H
#define RUNTIME_H

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* ------------------------------------------------------------------------ */
/* CPU Context                                                              */
/* ------------------------------------------------------------------------ */

typedef struct {
    /* 8-bit registers */
    uint8_t a;    /* Accumulator */
    uint8_t f;    /* Flags: Z N H C 0 0 0 0 */
    uint8_t b, c; /* BC register pair */
    uint8_t d, e; /* DE register pair */
    uint8_t h, l; /* HL register pair */

    /* 16-bit registers */
    uint16_t sp;  /* Stack pointer */
    uint16_t pc;  /* Program counter */

    /* Execution state */
    bool halted;
    bool ime;     /* Interrupt master enable */
    uint64_t cycles;
} cpu_t;

/* Register pair access macros */
#define REG_BC(cpu) ((uint16_t)((cpu).b << 8 | (cpu).c))
#define REG_DE(cpu) ((uint16_t)((cpu).d << 8 | (cpu).e))
#define REG_HL(cpu) ((uint16_t)((cpu).h << 8 | (cpu).l))
#define REG_AF(cpu) ((uint16_t)((cpu).a << 8 | (cpu).f))

#define SET_BC(cpu, v) do { (cpu).b = ((v)>>8)&0xFF; (cpu).c = (v)&0xFF; } while(0)
#define SET_DE(cpu, v) do { (cpu).d = ((v)>>8)&0xFF; (cpu).e = (v)&0xFF; } while(0)
#define SET_HL(cpu, v) do { (cpu).h = ((v)>>8)&0xFF; (cpu).l = (v)&0xFF; } while(0)

/* ------------------------------------------------------------------------ */
/* Flag Bits                                                                */
/* ------------------------------------------------------------------------ */

#define FLAG_Z_BIT  7
#define FLAG_N_BIT  6
#define FLAG_H_BIT  5
#define FLAG_C_BIT  4

#define FLAG_Z_MASK (1 << FLAG_Z_BIT)
#define FLAG_N_MASK (1 << FLAG_N_BIT)
#define FLAG_H_MASK (1 << FLAG_H_BIT)
#define FLAG_C_MASK (1 << FLAG_C_BIT)

/* Read individual flags */
#define FLAG_Z(f) (((f) >> FLAG_Z_BIT) & 1)
#define FLAG_N(f) (((f) >> FLAG_N_BIT) & 1)
#define FLAG_H(f) (((f) >> FLAG_H_BIT) & 1)
#define FLAG_C(f) (((f) >> FLAG_C_BIT) & 1)

/* ------------------------------------------------------------------------ */
/* Flag Helper Macros                                                       */
/*                                                                          */
/* These macros operate on cpu.f and are used by the generated code.        */
/* ------------------------------------------------------------------------ */

/* Set or clear the Zero flag based on a value */
#define SET_Z(val) \
    do { if ((val) == 0) cpu.f |= FLAG_Z_MASK; else cpu.f &= ~FLAG_Z_MASK; } while(0)

/* Set or clear the Subtract (N) flag */
#define SET_N(flag) \
    do { if (flag) cpu.f |= FLAG_N_MASK; else cpu.f &= ~FLAG_N_MASK; } while(0)

/* Set Half-carry flag for addition: carry from bit 3 */
#define SET_H_ADD(a, b) \
    do { if ((((a)&0xF) + ((b)&0xF)) > 0xF) cpu.f |= FLAG_H_MASK; \
         else cpu.f &= ~FLAG_H_MASK; } while(0)

/* Set Half-carry flag for subtraction: borrow from bit 4 */
#define SET_H_SUB(a, b) \
    do { if (((a)&0xF) < ((b)&0xF)) cpu.f |= FLAG_H_MASK; \
         else cpu.f &= ~FLAG_H_MASK; } while(0)

/* Set Carry flag for addition: carry from bit 7 */
#define SET_C_ADD(a, b) \
    do { if (((int)(a) + (int)(b)) > 0xFF) cpu.f |= FLAG_C_MASK; \
         else cpu.f &= ~FLAG_C_MASK; } while(0)

/* Set Carry flag for subtraction: borrow */
#define SET_C_SUB(a, b) \
    do { if ((a) < (b)) cpu.f |= FLAG_C_MASK; \
         else cpu.f &= ~FLAG_C_MASK; } while(0)


/* ------------------------------------------------------------------------ */
/* Memory Bus Interface                                                     */
/* ------------------------------------------------------------------------ */

/* Simple flat 64 KB memory for the mini runtime */
#define MEM_SIZE 0x10000

extern uint8_t memory[MEM_SIZE];

/* Read/write functions */
uint8_t mem_read8(uint16_t addr);
void    mem_write8(uint16_t addr, uint8_t val);
uint16_t mem_read16(uint16_t addr);
void     mem_write16(uint16_t addr, uint16_t val);

/* Load ROM data into memory starting at address 0 */
void mem_load_rom(const uint8_t *data, int size);


/* ------------------------------------------------------------------------ */
/* Runtime Functions                                                        */
/* ------------------------------------------------------------------------ */

/* Initialize CPU to post-boot state */
void cpu_init(cpu_t *cpu);

/* Print the current CPU state (for debugging) */
void cpu_dump(const cpu_t *cpu);

/* The generated recompiled code entry point (defined in output.c) */
void recompiled_main(cpu_t *cpu);

#endif /* RUNTIME_H */
