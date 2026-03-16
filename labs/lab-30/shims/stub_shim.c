/*
 * Lab 30: Hardware abstraction shim implementation.
 *
 * Provides stub implementations that log hardware accesses
 * instead of touching real hardware. This file is complete --
 * do not modify it.
 */

#include <stdio.h>
#include "stub_shim.h"

void stub_hw_init(void) {
    printf("Shim: stub_hw_init() called\n");
}

void stub_hw_write(uint32_t address, uint16_t value) {
    /* In a real recomp project, this might route to SDL or
     * a software renderer. Here we just log it. */
    (void)address;
    (void)value;
}

uint16_t stub_hw_read(uint32_t address) {
    (void)address;
    return 0;
}
