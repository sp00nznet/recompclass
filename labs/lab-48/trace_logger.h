#ifndef TRACE_LOGGER_H
#define TRACE_LOGGER_H

#include <stdint.h>
#include <stdio.h>

/*
 * trace_logger.h -- Register state trace logger for recompilation debugging.
 */

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

#define TRACE_MAX_ENTRIES  256
#define TRACE_FUNC_NAME_MAX 64
#define NUM_GPRS           8     /* r0-r7 */

/* ------------------------------------------------------------------ */
/*  Register state (simplified ARM-like)                               */
/* ------------------------------------------------------------------ */

typedef struct {
    uint32_t r[NUM_GPRS];   /* r0 through r7 */
    uint32_t sp;             /* stack pointer  */
    uint32_t lr;             /* link register  */
    uint32_t pc;             /* program counter */
} CpuRegs;

/* ------------------------------------------------------------------ */
/*  Trace entry                                                        */
/* ------------------------------------------------------------------ */

typedef enum {
    TRACE_DIR_ENTRY,
    TRACE_DIR_EXIT,
} TraceDirection;

typedef struct {
    uint32_t       timestamp;
    char           func_name[TRACE_FUNC_NAME_MAX];
    TraceDirection direction;
    CpuRegs        regs;
} TraceEntry;

/* ------------------------------------------------------------------ */
/*  Trace logger state                                                 */
/* ------------------------------------------------------------------ */

typedef struct {
    TraceEntry entries[TRACE_MAX_ENTRIES];
    int        count;
    uint32_t   next_timestamp;
} TraceLogger;

/* ------------------------------------------------------------------ */
/*  API                                                                */
/* ------------------------------------------------------------------ */

/* Initialize the logger (clear entries, reset timestamp). */
void trace_init(TraceLogger *logger);

/* Record a function entry with current register state. */
void trace_entry(TraceLogger *logger, const char *func_name,
                 const CpuRegs *regs);

/* Record a function exit with current register state. */
void trace_exit(TraceLogger *logger, const char *func_name,
                const CpuRegs *regs);

/* Return the number of recorded entries. */
int trace_count(const TraceLogger *logger);

/* Return a pointer to entry at index i, or NULL if out of range. */
const TraceEntry *trace_get(const TraceLogger *logger, int i);

/* Write the entire trace log to a file in CSV format.
 * Returns 0 on success, -1 on error.
 *
 * CSV columns:
 * timestamp,function,direction,r0,r1,r2,r3,r4,r5,r6,r7,sp,lr,pc
 */
int trace_write_csv(const TraceLogger *logger, const char *filename);

/* Write the trace log to an already-opened FILE* in CSV format.
 * Returns 0 on success.
 */
int trace_fwrite_csv(const TraceLogger *logger, FILE *fp);

/* ------------------------------------------------------------------ */
/*  Instrumentation macros                                             */
/* ------------------------------------------------------------------ */

#define TRACE_ENTRY(logger, name, regs) trace_entry((logger), (name), (regs))
#define TRACE_EXIT(logger, name, regs)  trace_exit((logger), (name), (regs))

#endif /* TRACE_LOGGER_H */
