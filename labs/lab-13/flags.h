#ifndef FLAGS_H
#define FLAGS_H

#include <stdint.h>
#include <stdbool.h>

/*
 * flags.h -- CPU flag computation helpers for 8-bit ALU operations.
 *
 * These helpers are designed for use in a static recompiler's generated code.
 * Each function performs an operation and returns the result along with all
 * affected status flags.
 */

/* Flag bit positions (matching common convention) */
#define FLAG_Z  (1 << 0)  /* Zero        */
#define FLAG_C  (1 << 1)  /* Carry       */
#define FLAG_V  (1 << 2)  /* Overflow    */
#define FLAG_N  (1 << 3)  /* Negative    */
#define FLAG_H  (1 << 4)  /* Half-Carry  */

/*
 * FlagResult8 -- holds the 8-bit result of an operation together with
 * the flag register value produced by that operation.
 */
typedef struct {
    uint8_t  result;
    uint8_t  flags;   /* Combination of FLAG_Z, FLAG_C, etc. */
} FlagResult8;

/*
 * FlagResult16 -- 16-bit variant (for stretch goals).
 */
typedef struct {
    uint16_t result;
    uint8_t  flags;
} FlagResult16;

/* ------------------------------------------------------------------ */
/*  8-bit arithmetic                                                   */
/* ------------------------------------------------------------------ */

/* Compute result and flags for: a + b */
FlagResult8 add_flags_u8(uint8_t a, uint8_t b);

/* Compute result and flags for: a - b */
FlagResult8 sub_flags_u8(uint8_t a, uint8_t b);

/* Compute result and flags for: a + b + carry_in */
FlagResult8 adc_flags_u8(uint8_t a, uint8_t b, bool carry_in);

/* Compute result and flags for: a - b - carry_in */
FlagResult8 sbc_flags_u8(uint8_t a, uint8_t b, bool carry_in);

/* ------------------------------------------------------------------ */
/*  8-bit logic (carry and overflow are always cleared)                */
/* ------------------------------------------------------------------ */

FlagResult8 and_flags_u8(uint8_t a, uint8_t b);
FlagResult8 or_flags_u8(uint8_t a, uint8_t b);
FlagResult8 xor_flags_u8(uint8_t a, uint8_t b);

/* ------------------------------------------------------------------ */
/*  16-bit variants (TODO -- implement these as a stretch goal)        */
/* ------------------------------------------------------------------ */

/* FlagResult16 add_flags_u16(uint16_t a, uint16_t b); */
/* FlagResult16 sub_flags_u16(uint16_t a, uint16_t b); */

/* ------------------------------------------------------------------ */
/*  Utility                                                            */
/* ------------------------------------------------------------------ */

/* Return a human-readable string like "ZNCH" for the given flag byte. */
const char *flags_to_string(uint8_t flags);

#endif /* FLAGS_H */
