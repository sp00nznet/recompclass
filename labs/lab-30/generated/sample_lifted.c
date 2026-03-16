/*
 * Lab 30: Sample lifted code (auto-generated).
 *
 * In a real project, this file would be produced by the lifter.
 * This file is complete -- do not modify it.
 */

#include "stub_shim.h"

int sample_function(void) {
    /* This represents a lifted function that calls into a shim.
     * The original code would have done a hardware register write;
     * our shim just logs it. */
    stub_hw_write(0x04000000, 0x0040);  /* Hypothetical DISPCNT write */

    return 42;  /* The "correct" return value for testing */
}
