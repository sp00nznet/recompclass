/*
 * Lab 5: Game Boy Memory Bus -- Implementation
 *
 * Implements the memory bus interface declared in memory_bus.h.
 * Students must complete the TODO sections to handle all memory regions.
 */

#include "memory_bus.h"
#include <string.h>
#include <stdio.h>


/* ------------------------------------------------------------------------ */
/* Initialization                                                           */
/* ------------------------------------------------------------------------ */

void mem_init(memory_bus_t *bus)
{
    memset(bus, 0, sizeof(memory_bus_t));
    bus->current_rom_bank = 1;
    bus->current_extram_bank = 0;
    bus->extram_enabled = false;
}


int mem_load_rom(memory_bus_t *bus, const uint8_t *rom_data, int rom_size)
{
    if (rom_size <= 0) {
        return -1;
    }

    int num_banks = (rom_size + ROM_BANK_SIZE - 1) / ROM_BANK_SIZE;
    if (num_banks > MAX_ROM_BANKS) {
        fprintf(stderr, "Error: ROM too large (%d banks, max %d)\n",
                num_banks, MAX_ROM_BANKS);
        return -1;
    }

    bus->num_rom_banks = num_banks;

    /* Copy ROM data into bank arrays */
    for (int bank = 0; bank < num_banks; bank++) {
        int offset = bank * ROM_BANK_SIZE;
        int remaining = rom_size - offset;
        int copy_size = remaining < ROM_BANK_SIZE ? remaining : ROM_BANK_SIZE;
        memcpy(bus->rom[bank], rom_data + offset, copy_size);
    }

    return 0;
}


/* ------------------------------------------------------------------------ */
/* Read                                                                     */
/* ------------------------------------------------------------------------ */

uint8_t mem_read8(memory_bus_t *bus, uint16_t addr)
{
    /* ROM Bank 0: 0x0000 - 0x3FFF */
    if (addr < 0x4000) {
        return bus->rom[0][addr];
    }

    /* ROM Bank N (switchable): 0x4000 - 0x7FFF */
    if (addr < 0x8000) {
        return bus->rom[bus->current_rom_bank][addr - 0x4000];
    }

    /* VRAM: 0x8000 - 0x9FFF */
    if (addr < 0xA000) {
        return bus->vram[addr - 0x8000];
    }

    /* External RAM: 0xA000 - 0xBFFF */
    if (addr < 0xC000) {
        if (!bus->extram_enabled) {
            return 0xFF;  /* Open bus when RAM is disabled */
        }
        return bus->extram[bus->current_extram_bank][addr - 0xA000];
    }

    /* Work RAM: 0xC000 - 0xDFFF */
    if (addr < 0xE000) {
        return bus->wram[addr - 0xC000];
    }

    /* Echo RAM: 0xE000 - 0xFDFF (mirrors WRAM) */
    if (addr < 0xFE00) {
        /* TODO: Implement echo RAM.
         * This region mirrors Work RAM. A read from 0xE000 should return
         * the same value as a read from 0xC000, and so on.
         *
         * Hint: subtract 0x2000 from the address and read from WRAM.
         * For now, return 0xFF as a placeholder. */
        return 0xFF;
    }

    /* OAM: 0xFE00 - 0xFE9F */
    if (addr < 0xFEA0) {
        /* TODO: Add OAM access restrictions.
         * During certain PPU modes (modes 2 and 3), OAM should not be
         * readable by the CPU. For now, always allow access.
         * In the future, check the PPU mode before returning data. */
        return bus->oam[addr - 0xFE00];
    }

    /* Unusable region: 0xFEA0 - 0xFEFF */
    if (addr < 0xFF00) {
        return 0xFF;
    }

    /* I/O Registers: 0xFF00 - 0xFF7F */
    if (addr < 0xFF80) {
        return bus->io[addr - 0xFF00];
    }

    /* High RAM: 0xFF80 - 0xFFFE */
    if (addr < 0xFFFF) {
        return bus->hram[addr - 0xFF80];
    }

    /* Interrupt Enable Register: 0xFFFF */
    return bus->ie_register;
}


/* ------------------------------------------------------------------------ */
/* Write                                                                    */
/* ------------------------------------------------------------------------ */

void mem_write8(memory_bus_t *bus, uint16_t addr, uint8_t val)
{
    /* ROM region: 0x0000 - 0x7FFF */
    if (addr < 0x8000) {
        /* TODO: Implement bank switching.
         *
         * Writes to the ROM region do not modify ROM data. Instead,
         * they control the memory bank controller (MBC). For MBC1:
         *
         *   0x0000 - 0x1FFF: RAM enable (0x0A enables, others disable)
         *   0x2000 - 0x3FFF: ROM bank number (lower 5 bits)
         *   0x4000 - 0x5FFF: RAM bank number OR upper ROM bank bits
         *   0x6000 - 0x7FFF: Banking mode select
         *
         * For now, just ignore writes to this region.
         * Implement MBC1 bank switching as a stretch goal. */
        return;
    }

    /* VRAM: 0x8000 - 0x9FFF */
    if (addr < 0xA000) {
        bus->vram[addr - 0x8000] = val;
        return;
    }

    /* External RAM: 0xA000 - 0xBFFF */
    if (addr < 0xC000) {
        if (bus->extram_enabled) {
            bus->extram[bus->current_extram_bank][addr - 0xA000] = val;
        }
        return;
    }

    /* Work RAM: 0xC000 - 0xDFFF */
    if (addr < 0xE000) {
        bus->wram[addr - 0xC000] = val;
        return;
    }

    /* Echo RAM: 0xE000 - 0xFDFF */
    if (addr < 0xFE00) {
        /* TODO: Implement echo RAM writes.
         * Writes here should also go to the corresponding WRAM address.
         * Hint: subtract 0x2000 from the address. */
        return;
    }

    /* OAM: 0xFE00 - 0xFE9F */
    if (addr < 0xFEA0) {
        /* TODO: Add OAM access restrictions (same as in read). */
        bus->oam[addr - 0xFE00] = val;
        return;
    }

    /* Unusable region: 0xFEA0 - 0xFEFF */
    if (addr < 0xFF00) {
        return;  /* Writes here are ignored */
    }

    /* I/O Registers: 0xFF00 - 0xFF7F */
    if (addr < 0xFF80) {
        bus->io[addr - 0xFF00] = val;
        return;
    }

    /* High RAM: 0xFF80 - 0xFFFE */
    if (addr < 0xFFFF) {
        bus->hram[addr - 0xFF80] = val;
        return;
    }

    /* Interrupt Enable Register: 0xFFFF */
    bus->ie_register = val;
}


/* ------------------------------------------------------------------------ */
/* 16-bit convenience wrappers                                              */
/* ------------------------------------------------------------------------ */

uint16_t mem_read16(memory_bus_t *bus, uint16_t addr)
{
    uint8_t lo = mem_read8(bus, addr);
    uint8_t hi = mem_read8(bus, addr + 1);
    return (uint16_t)(lo | (hi << 8));
}

void mem_write16(memory_bus_t *bus, uint16_t addr, uint16_t val)
{
    mem_write8(bus, addr, (uint8_t)(val & 0xFF));
    mem_write8(bus, addr + 1, (uint8_t)((val >> 8) & 0xFF));
}
