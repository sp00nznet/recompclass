/*
 * trace_logger.c -- Register state trace logger.
 *
 * Complete the TODO sections.
 */

#include <string.h>
#include "trace_logger.h"

/* ------------------------------------------------------------------ */
/*  Internal: record a trace entry                                     */
/* ------------------------------------------------------------------ */

static void record(TraceLogger *logger, const char *func_name,
                   TraceDirection direction, const CpuRegs *regs)
{
    /* TODO:
     * 1. If logger->count >= TRACE_MAX_ENTRIES, return (buffer full).
     * 2. Get a pointer to logger->entries[logger->count].
     * 3. Set the entry's timestamp to logger->next_timestamp.
     * 4. Copy func_name into the entry (use strncpy, ensure null-term).
     * 5. Set the entry's direction.
     * 6. Copy *regs into the entry's regs field.
     * 7. Increment logger->count and logger->next_timestamp.
     */
}

/* ------------------------------------------------------------------ */
/*  API                                                                */
/* ------------------------------------------------------------------ */

void trace_init(TraceLogger *logger)
{
    /* TODO: zero out the entries array, set count and next_timestamp to 0. */
}

void trace_entry(TraceLogger *logger, const char *func_name,
                 const CpuRegs *regs)
{
    /* TODO: call record() with TRACE_DIR_ENTRY. */
}

void trace_exit(TraceLogger *logger, const char *func_name,
                const CpuRegs *regs)
{
    /* TODO: call record() with TRACE_DIR_EXIT. */
}

int trace_count(const TraceLogger *logger)
{
    /* TODO: return logger->count. */
    return 0;
}

const TraceEntry *trace_get(const TraceLogger *logger, int i)
{
    /* TODO: return &logger->entries[i] if 0 <= i < count, else NULL. */
    return NULL;
}

int trace_fwrite_csv(const TraceLogger *logger, FILE *fp)
{
    /* TODO:
     * 1. Write the CSV header line:
     *    "timestamp,function,direction,r0,r1,r2,r3,r4,r5,r6,r7,sp,lr,pc\n"
     * 2. For each entry (0 to count-1):
     *    a. Print timestamp.
     *    b. Print func_name.
     *    c. Print "entry" or "exit" based on direction.
     *    d. Print each register as 0x%08X.
     *    e. End with newline.
     * 3. Return 0.
     */
    return 0;
}

int trace_write_csv(const TraceLogger *logger, const char *filename)
{
    /* TODO:
     * 1. Open filename for writing.
     * 2. If open fails, return -1.
     * 3. Call trace_fwrite_csv().
     * 4. Close the file.
     * 5. Return 0.
     */
    return -1;
}
