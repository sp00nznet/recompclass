/*
 * Lab 9: Dispatch Table Interface
 *
 * Defines the types and interface for dispatch tables used to handle
 * indirect jumps in statically recompiled code.
 */

#ifndef DISPATCH_H
#define DISPATCH_H

#include <stdint.h>

/* ---------------------------------------------------------------------------
 * Types
 * --------------------------------------------------------------------------- */

/* Recompiled function signature: takes a CPU context pointer, returns void. */
typedef struct cpu_state cpu_state_t;
typedef void (*recomp_func_t)(cpu_state_t *ctx);

/* A dispatch entry maps an original address to a recompiled function. */
typedef struct {
    uint32_t original_addr;
    recomp_func_t func;
} dispatch_entry_t;

/* ---------------------------------------------------------------------------
 * Dispatch function prototypes
 *
 * Each dispatch function takes an original address and returns the
 * corresponding recompiled function pointer, or NULL if not found.
 * --------------------------------------------------------------------------- */

/* Strategy 1: Switch/case dispatch */
recomp_func_t dispatch_switch(uint32_t addr);

/* Strategy 2: Binary search dispatch */
recomp_func_t dispatch_bsearch(uint32_t addr);

/* Strategy 3: Hash table dispatch */
recomp_func_t dispatch_hash(uint32_t addr);

/* ---------------------------------------------------------------------------
 * Fallback handler
 *
 * Called when no dispatch entry matches the target address.
 * In a full implementation, this might invoke an interpreter.
 * --------------------------------------------------------------------------- */

void dispatch_fallback(cpu_state_t *ctx, uint32_t addr);

#endif /* DISPATCH_H */
