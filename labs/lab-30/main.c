/*
 * Lab 30: Main harness for the recomp project.
 *
 * This file is complete -- do not modify it.
 * It calls into both the shim library and the generated library.
 */

#include <stdio.h>
#include "stub_shim.h"

/* Declared in generated/sample_lifted.c */
extern int sample_function(void);

int main(void) {
    /* Initialize hardware stubs */
    stub_hw_init();

    /* Call a lifted function */
    int result = sample_function();
    printf("Lifted: sample_function() returned %d\n", result);

    printf("Recomp runner finished successfully.\n");
    return (result == 42) ? 0 : 1;
}
