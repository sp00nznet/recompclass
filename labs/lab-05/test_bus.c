/*
 * Lab 5: Memory Bus -- Test Program
 *
 * Writes to and reads from various memory regions to verify the
 * memory bus implementation.
 */

#include "memory_bus.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static int tests_passed = 0;
static int tests_failed = 0;

#define ASSERT_EQ(actual, expected, msg)                                     \
    do {                                                                     \
        if ((actual) == (expected)) {                                        \
            tests_passed++;                                                  \
        } else {                                                             \
            tests_failed++;                                                  \
            printf("  FAIL: %s -- expected 0x%02X, got 0x%02X\n",           \
                   (msg), (int)(expected), (int)(actual));                    \
        }                                                                    \
    } while (0)


/* ---- Test: ROM reads -------------------------------------------------- */

static void test_rom_read(memory_bus_t *bus)
{
    printf("Test: ROM read\n");

    /* Create a small 32 KB ROM (2 banks) */
    uint8_t rom[0x8000];
    memset(rom, 0, sizeof(rom));
    rom[0x0000] = 0xAA;         /* Bank 0, address 0x0000 */
    rom[0x3FFF] = 0xBB;         /* Bank 0, last byte */
    rom[0x4000] = 0xCC;         /* Bank 1, first byte */
    rom[0x7FFF] = 0xDD;         /* Bank 1, last byte */

    mem_load_rom(bus, rom, sizeof(rom));

    ASSERT_EQ(mem_read8(bus, 0x0000), 0xAA, "ROM bank 0 start");
    ASSERT_EQ(mem_read8(bus, 0x3FFF), 0xBB, "ROM bank 0 end");
    ASSERT_EQ(mem_read8(bus, 0x4000), 0xCC, "ROM bank 1 start");
    ASSERT_EQ(mem_read8(bus, 0x7FFF), 0xDD, "ROM bank 1 end");
}


/* ---- Test: VRAM read/write -------------------------------------------- */

static void test_vram(memory_bus_t *bus)
{
    printf("Test: VRAM read/write\n");

    mem_write8(bus, 0x8000, 0x11);
    mem_write8(bus, 0x9FFF, 0x22);

    ASSERT_EQ(mem_read8(bus, 0x8000), 0x11, "VRAM start");
    ASSERT_EQ(mem_read8(bus, 0x9FFF), 0x22, "VRAM end");
}


/* ---- Test: Work RAM read/write ---------------------------------------- */

static void test_wram(memory_bus_t *bus)
{
    printf("Test: Work RAM read/write\n");

    mem_write8(bus, 0xC000, 0x33);
    mem_write8(bus, 0xDFFF, 0x44);

    ASSERT_EQ(mem_read8(bus, 0xC000), 0x33, "WRAM start");
    ASSERT_EQ(mem_read8(bus, 0xDFFF), 0x44, "WRAM end");
}


/* ---- Test: HRAM read/write -------------------------------------------- */

static void test_hram(memory_bus_t *bus)
{
    printf("Test: HRAM read/write\n");

    mem_write8(bus, 0xFF80, 0x55);
    mem_write8(bus, 0xFFFE, 0x66);

    ASSERT_EQ(mem_read8(bus, 0xFF80), 0x55, "HRAM start");
    ASSERT_EQ(mem_read8(bus, 0xFFFE), 0x66, "HRAM end");
}


/* ---- Test: I/O registers ---------------------------------------------- */

static void test_io(memory_bus_t *bus)
{
    printf("Test: I/O registers\n");

    mem_write8(bus, 0xFF00, 0x77);
    mem_write8(bus, 0xFF7F, 0x88);

    ASSERT_EQ(mem_read8(bus, 0xFF00), 0x77, "I/O start");
    ASSERT_EQ(mem_read8(bus, 0xFF7F), 0x88, "I/O end");
}


/* ---- Test: OAM read/write --------------------------------------------- */

static void test_oam(memory_bus_t *bus)
{
    printf("Test: OAM read/write\n");

    mem_write8(bus, 0xFE00, 0x99);
    mem_write8(bus, 0xFE9F, 0xAA);

    ASSERT_EQ(mem_read8(bus, 0xFE00), 0x99, "OAM start");
    ASSERT_EQ(mem_read8(bus, 0xFE9F), 0xAA, "OAM end");
}


/* ---- Test: Interrupt Enable register ---------------------------------- */

static void test_ie(memory_bus_t *bus)
{
    printf("Test: Interrupt Enable register\n");

    mem_write8(bus, 0xFFFF, 0x1F);
    ASSERT_EQ(mem_read8(bus, 0xFFFF), 0x1F, "IE register");
}


/* ---- Test: 16-bit read/write ------------------------------------------ */

static void test_16bit(memory_bus_t *bus)
{
    printf("Test: 16-bit read/write\n");

    mem_write16(bus, 0xC000, 0xBEEF);
    uint16_t val = mem_read16(bus, 0xC000);
    ASSERT_EQ(val & 0xFF, 0xEF, "16-bit low byte");
    ASSERT_EQ((val >> 8) & 0xFF, 0xBE, "16-bit high byte");
}


/* ---- Test: Echo RAM (stretch goal) ------------------------------------ */

static void test_echo_ram(memory_bus_t *bus)
{
    printf("Test: Echo RAM (stretch goal)\n");

    /* Write to WRAM, then read via echo RAM address */
    mem_write8(bus, 0xC000, 0xEE);
    uint8_t echo_val = mem_read8(bus, 0xE000);

    if (echo_val == 0xEE) {
        printf("  Echo RAM is implemented -- reads mirror WRAM correctly.\n");
        tests_passed++;
    } else if (echo_val == 0xFF) {
        printf("  Echo RAM not yet implemented (returning 0xFF placeholder).\n");
        printf("  This is expected if you have not completed the stretch goal.\n");
        tests_passed++;  /* Not a failure -- it's a stretch goal */
    } else {
        tests_failed++;
        printf("  FAIL: Echo RAM returned unexpected value 0x%02X\n", echo_val);
    }
}


/* ---- Main ------------------------------------------------------------- */

int main(void)
{
    memory_bus_t bus;

    printf("=== Lab 5: Memory Bus Tests ===\n\n");

    mem_init(&bus);

    test_rom_read(&bus);
    mem_init(&bus);  /* Reset between tests */

    test_vram(&bus);
    mem_init(&bus);

    test_wram(&bus);
    mem_init(&bus);

    test_hram(&bus);
    mem_init(&bus);

    test_io(&bus);
    mem_init(&bus);

    test_oam(&bus);
    mem_init(&bus);

    test_ie(&bus);
    mem_init(&bus);

    test_16bit(&bus);
    mem_init(&bus);

    test_echo_ram(&bus);

    printf("\n=== Results: %d passed, %d failed ===\n",
           tests_passed, tests_failed);

    return tests_failed > 0 ? 1 : 0;
}
