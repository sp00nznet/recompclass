/*
 * Lab 5: Game Boy Memory Bus
 *
 * Header file declaring the memory bus data structure and interface.
 */

#ifndef MEMORY_BUS_H
#define MEMORY_BUS_H

#include <stdint.h>
#include <stdbool.h>

/* ------------------------------------------------------------------------ */
/* Memory Region Sizes                                                      */
/* ------------------------------------------------------------------------ */

#define ROM_BANK_SIZE    0x4000   /* 16 KB per ROM bank */
#define VRAM_SIZE        0x2000   /* 8 KB  */
#define EXTRAM_SIZE      0x2000   /* 8 KB  */
#define WRAM_SIZE        0x2000   /* 8 KB  */
#define OAM_SIZE         0x00A0   /* 160 bytes */
#define IO_SIZE          0x0080   /* 128 bytes */
#define HRAM_SIZE        0x007F   /* 127 bytes */

/* Maximum number of ROM banks (for MBC1: up to 128 banks = 2 MB) */
#define MAX_ROM_BANKS    128

/* Maximum number of external RAM banks (for MBC1: up to 4 banks = 32 KB) */
#define MAX_EXTRAM_BANKS 4

/* ------------------------------------------------------------------------ */
/* Memory Bus Structure                                                     */
/* ------------------------------------------------------------------------ */

typedef struct {
    /* ROM data -- bank 0 is always mapped at 0x0000-0x3FFF,
       the switchable bank is mapped at 0x4000-0x7FFF */
    uint8_t rom[MAX_ROM_BANKS][ROM_BANK_SIZE];
    uint8_t current_rom_bank;   /* Currently selected ROM bank (1-127) */
    int     num_rom_banks;      /* Total number of ROM banks loaded */

    /* Video RAM (0x8000-0x9FFF) */
    uint8_t vram[VRAM_SIZE];

    /* External (cartridge) RAM (0xA000-0xBFFF) */
    uint8_t extram[MAX_EXTRAM_BANKS][EXTRAM_SIZE];
    uint8_t current_extram_bank;
    bool    extram_enabled;

    /* Work RAM (0xC000-0xDFFF) */
    uint8_t wram[WRAM_SIZE];

    /* OAM - Object Attribute Memory (0xFE00-0xFE9F) */
    uint8_t oam[OAM_SIZE];

    /* I/O Registers (0xFF00-0xFF7F) */
    uint8_t io[IO_SIZE];

    /* High RAM (0xFF80-0xFFFE) */
    uint8_t hram[HRAM_SIZE];

    /* Interrupt Enable register (0xFFFF) */
    uint8_t ie_register;

} memory_bus_t;


/* ------------------------------------------------------------------------ */
/* Function Declarations                                                    */
/* ------------------------------------------------------------------------ */

/*
 * Initialize the memory bus to a clean state.
 * All memory is zeroed. ROM bank is set to 1. External RAM is disabled.
 */
void mem_init(memory_bus_t *bus);

/*
 * Load ROM data into the bus.
 *
 * Parameters:
 *   bus      - Pointer to the memory bus.
 *   rom_data - Pointer to raw ROM bytes.
 *   rom_size - Size of the ROM data in bytes.
 *
 * Returns:
 *   0 on success, -1 on error (e.g., ROM too large).
 */
int mem_load_rom(memory_bus_t *bus, const uint8_t *rom_data, int rom_size);

/*
 * Read a byte from the memory bus.
 *
 * Routes the read to the appropriate memory region based on the address.
 *
 * Parameters:
 *   bus  - Pointer to the memory bus.
 *   addr - 16-bit address to read from.
 *
 * Returns:
 *   The byte at the given address.
 */
uint8_t mem_read8(memory_bus_t *bus, uint16_t addr);

/*
 * Write a byte to the memory bus.
 *
 * Routes the write to the appropriate memory region based on the address.
 * Writes to ROM regions may trigger bank switching (if implemented).
 *
 * Parameters:
 *   bus  - Pointer to the memory bus.
 *   addr - 16-bit address to write to.
 *   val  - Byte value to write.
 */
void mem_write8(memory_bus_t *bus, uint16_t addr, uint8_t val);

/*
 * Read a 16-bit little-endian word from the memory bus.
 * Convenience wrapper around two mem_read8 calls.
 */
uint16_t mem_read16(memory_bus_t *bus, uint16_t addr);

/*
 * Write a 16-bit little-endian word to the memory bus.
 * Convenience wrapper around two mem_write8 calls.
 */
void mem_write16(memory_bus_t *bus, uint16_t addr, uint16_t val);

#endif /* MEMORY_BUS_H */
