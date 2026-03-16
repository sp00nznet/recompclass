/*
 * dma_bridge.c -- DMA bridge between PPU main memory and SPU local stores.
 *
 * Complete the TODO sections.
 */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "dma_bridge.h"

/* ------------------------------------------------------------------ */
/*  Internal: validate transfer parameters                             */
/* ------------------------------------------------------------------ */

/*
 * Validate common DMA transfer parameters.
 *
 * Returns DMA_OK if all checks pass, or an error code.
 *
 * Checks:
 *   1. bridge is not NULL.
 *   2. spu_id is in range [0, MAX_SPUS).
 *   3. ls_offset is 16-byte aligned.
 *   4. ea is 16-byte aligned.
 *   5. size is valid: 1, 2, 4, 8, or a multiple of 16 up to DMA_MAX_TRANSFER.
 *   6. ls_offset + size <= SPU_LS_SIZE.
 *   7. ea + size <= bridge->main_mem_size.
 */
static int validate_params(const DmaBridge *bridge, int spu_id,
                           uint32_t ls_offset, uint64_t ea, uint32_t size)
{
    /* TODO: implement all validation checks listed above.
     *
     * For size validation:
     *   - sizes 1, 2, 4, 8 are allowed (sub-qword transfers)
     *   - sizes that are multiples of 16 up to DMA_MAX_TRANSFER are allowed
     *   - all other sizes are invalid (return DMA_ERR_SIZE)
     *   - size == 0 is invalid
     *
     * For alignment: only check alignment for sizes >= 16.
     * Sizes 1, 2, 4, 8 require alignment to their own size.
     */
    return DMA_OK;
}

/* ------------------------------------------------------------------ */
/*  Internal: record a transfer in the log                             */
/* ------------------------------------------------------------------ */

static void log_transfer(DmaBridge *bridge, DmaDirection dir, int spu_id,
                         uint32_t ls_offset, uint64_t ea, uint32_t size)
{
    /* TODO: record this transfer in bridge->log at index
     * (bridge->log_count % DMA_LOG_MAX), then increment log_count.
     */
}

/* ------------------------------------------------------------------ */
/*  Lifecycle                                                          */
/* ------------------------------------------------------------------ */

int dma_bridge_init(DmaBridge *bridge, size_t main_mem_size)
{
    /* TODO:
     * 1. If bridge is NULL, return DMA_ERR_NULL.
     * 2. Zero out all local stores.
     * 3. Allocate main_mem_size bytes for bridge->main_mem (calloc).
     * 4. If allocation fails, return DMA_ERR_NULL.
     * 5. Set bridge->main_mem_size.
     * 6. Set bridge->log_count to 0.
     * 7. Return DMA_OK.
     */
    return DMA_ERR_NULL;
}

void dma_bridge_destroy(DmaBridge *bridge)
{
    /* TODO: free bridge->main_mem and set it to NULL. */
}

/* ------------------------------------------------------------------ */
/*  DMA transfers                                                      */
/* ------------------------------------------------------------------ */

int dma_put(DmaBridge *bridge, int spu_id,
            uint32_t ls_offset, uint64_t ea, uint32_t size)
{
    /* TODO:
     * 1. Validate parameters with validate_params().
     * 2. If valid, copy `size` bytes from bridge->main_mem[ea] into
     *    bridge->ls[spu_id][ls_offset].
     * 3. Log the transfer with DMA_DIR_PUT.
     * 4. Return DMA_OK (or the error from validation).
     */
    return DMA_ERR_NULL;
}

int dma_get(DmaBridge *bridge, int spu_id,
            uint32_t ls_offset, uint64_t ea, uint32_t size)
{
    /* TODO:
     * 1. Validate parameters.
     * 2. Copy `size` bytes from bridge->ls[spu_id][ls_offset] into
     *    bridge->main_mem[ea].
     * 3. Log the transfer with DMA_DIR_GET.
     * 4. Return DMA_OK (or error).
     */
    return DMA_ERR_NULL;
}

int dma_wait(DmaBridge *bridge, int spu_id)
{
    /* TODO:
     * 1. If bridge is NULL, return DMA_ERR_NULL.
     * 2. If spu_id is out of range, return DMA_ERR_SPU_ID.
     * 3. Return DMA_OK (transfers are synchronous in this sim).
     */
    return DMA_ERR_NULL;
}

/* ------------------------------------------------------------------ */
/*  Utility                                                            */
/* ------------------------------------------------------------------ */

const char *dma_strerror(int err)
{
    switch (err) {
    case DMA_OK:        return "OK";
    case DMA_ERR_ALIGN: return "alignment violation";
    case DMA_ERR_SIZE:  return "invalid transfer size";
    case DMA_ERR_BOUNDS:return "out-of-bounds access";
    case DMA_ERR_SPU_ID:return "invalid SPU ID";
    case DMA_ERR_NULL:  return "null pointer";
    default:            return "unknown error";
    }
}

void dma_dump_log(const DmaBridge *bridge)
{
    if (!bridge) return;
    int n = bridge->log_count < DMA_LOG_MAX ? bridge->log_count : DMA_LOG_MAX;
    printf("DMA Transfer Log (%d entries):\n", bridge->log_count);
    for (int i = 0; i < n; i++) {
        const DmaRecord *r = &bridge->log[i];
        printf("  [%d] %s  SPU%d  LS=0x%04X  EA=0x%08llX  Size=%u\n",
               i,
               r->direction == DMA_DIR_PUT ? "PUT" : "GET",
               r->spu_id,
               r->ls_offset,
               (unsigned long long)r->ea,
               r->size);
    }
}
