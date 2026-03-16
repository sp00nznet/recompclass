/*
 * Lab 30: Hardware abstraction shim header.
 *
 * Declares stub functions that replace direct hardware access
 * in the lifted code. This file is complete -- do not modify it.
 */

#ifndef STUB_SHIM_H
#define STUB_SHIM_H

#include <stdint.h>

/* Initialize the hardware stubs (called once at startup). */
void stub_hw_init(void);

/* Write a 16-bit value to a hardware register address. */
void stub_hw_write(uint32_t address, uint16_t value);

/* Read a 16-bit value from a hardware register address. */
uint16_t stub_hw_read(uint32_t address);

#endif /* STUB_SHIM_H */
