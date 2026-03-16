/*
 * Lab 6: Mini-GB Recomp -- Runtime Implementation
 *
 * Provides the memory bus and CPU initialization used by the
 * generated recompiled code.
 */

#include "runtime.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>


/* ------------------------------------------------------------------------ */
/* Memory                                                                   */
/* ------------------------------------------------------------------------ */

uint8_t memory[MEM_SIZE];


void mem_load_rom(const uint8_t *data, int size)
{
    if (size > MEM_SIZE) {
        fprintf(stderr, "Error: ROM size (%d) exceeds memory size (%d)\n",
                size, MEM_SIZE);
        size = MEM_SIZE;
    }
    memset(memory, 0, MEM_SIZE);
    memcpy(memory, data, size);
}


uint8_t mem_read8(uint16_t addr)
{
    return memory[addr];
}


void mem_write8(uint16_t addr, uint8_t val)
{
    /* Prevent writes to ROM area (0x0000-0x7FFF) in this simple runtime */
    if (addr < 0x8000) {
        return;
    }
    memory[addr] = val;
}


uint16_t mem_read16(uint16_t addr)
{
    return (uint16_t)(mem_read8(addr) | (mem_read8(addr + 1) << 8));
}


void mem_write16(uint16_t addr, uint16_t val)
{
    mem_write8(addr, (uint8_t)(val & 0xFF));
    mem_write8(addr + 1, (uint8_t)((val >> 8) & 0xFF));
}


/* ------------------------------------------------------------------------ */
/* CPU                                                                      */
/* ------------------------------------------------------------------------ */

void cpu_init(cpu_t *cpu)
{
    memset(cpu, 0, sizeof(cpu_t));

    /* Post-boot register values (as set by the original Game Boy boot ROM) */
    cpu->a  = 0x01;
    cpu->f  = 0xB0;  /* Z=1, N=0, H=1, C=1 */
    cpu->b  = 0x00;
    cpu->c  = 0x13;
    cpu->d  = 0x00;
    cpu->e  = 0xD8;
    cpu->h  = 0x01;
    cpu->l  = 0x4D;
    cpu->sp = 0xFFFE;
    cpu->pc = 0x0100;  /* Entry point after boot ROM */
    cpu->halted = false;
    cpu->ime = true;
    cpu->cycles = 0;
}


void cpu_dump(const cpu_t *cpu)
{
    printf("CPU State:\n");
    printf("  A=%02X  F=%02X  (AF=%04X)\n", cpu->a, cpu->f, REG_AF(*cpu));
    printf("  B=%02X  C=%02X  (BC=%04X)\n", cpu->b, cpu->c, REG_BC(*cpu));
    printf("  D=%02X  E=%02X  (DE=%04X)\n", cpu->d, cpu->e, REG_DE(*cpu));
    printf("  H=%02X  L=%02X  (HL=%04X)\n", cpu->h, cpu->l, REG_HL(*cpu));
    printf("  SP=%04X  PC=%04X\n", cpu->sp, cpu->pc);
    printf("  Flags: Z=%d N=%d H=%d C=%d\n",
           FLAG_Z(cpu->f), FLAG_N(cpu->f),
           FLAG_H(cpu->f), FLAG_C(cpu->f));
    printf("  Cycles: %llu\n", (unsigned long long)cpu->cycles);
}


/* ------------------------------------------------------------------------ */
/* Main -- Entry Point                                                      */
/* ------------------------------------------------------------------------ */

/*
 * The ROM data is embedded in the generated output.c file. This main()
 * initializes the runtime, loads the ROM, calls the recompiled code,
 * and prints the final CPU state.
 */
int main(void)
{
    cpu_t cpu;

    printf("=== Mini-GB Recomp Runtime ===\n\n");

    cpu_init(&cpu);

    printf("Initial state:\n");
    cpu_dump(&cpu);
    printf("\nRunning recompiled code...\n\n");

    recompiled_main(&cpu);

    printf("Final state:\n");
    cpu_dump(&cpu);

    return 0;
}
