#include "spu_sim.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * spu_sim.c -- SPU Local Store and DMA transfer simulator implementation.
 *
 * All DMA transfers in this simulation are **synchronous** -- the data is
 * copied immediately during the spu_dma_get/put call.  A real SPU's DMA
 * engine is asynchronous; the SPU program would issue the transfer and
 * continue executing while the DMA engine moves data in the background.
 * The synchronous approach simplifies this lab while preserving the
 * essential semantics (alignment, size constraints, local store addressing).
 */

/* ------------------------------------------------------------------ */
/*  Internal helpers                                                   */
/* ------------------------------------------------------------------ */

/* Check alignment to SPU_DMA_ALIGN. */
static int check_align(uint64_t value)
{
    return (value & (SPU_DMA_ALIGN - 1)) == 0;
}

/* Validate common DMA parameters.  Returns SPU_OK or an error code. */
static int validate_dma_params(
    const SpuContext *ctx,
    uint32_t ls_offset,
    uint64_t ea,
    uint32_t size,
    uint32_t tag)
{
    if (!ctx || !ctx->main_mem)
        return SPU_ERR_NULL;

    if (tag >= SPU_DMA_MAX_TAGS)
        return SPU_ERR_TAG;

    if (!check_align(ls_offset))
        return SPU_ERR_ALIGN;

    if (!check_align(ea))
        return SPU_ERR_ALIGN;

    /* Size must be a multiple of 16 and at most SPU_DMA_MAX_SIZE. */
    if (size == 0 || (size & (SPU_DMA_ALIGN - 1)) != 0)
        return SPU_ERR_SIZE;

    if (size > SPU_DMA_MAX_SIZE)
        return SPU_ERR_SIZE;

    /* Bounds checks. */
    if ((uint64_t)ls_offset + size > SPU_LS_SIZE)
        return SPU_ERR_BOUNDS;

    if (ea + size > ctx->main_mem_size)
        return SPU_ERR_BOUNDS;

    return SPU_OK;
}

/* Log a DMA transfer for debugging. */
static void log_dma(SpuContext *ctx, SpuDmaDirection dir,
                    uint32_t ls_offset, uint64_t ea, uint32_t size,
                    uint32_t tag)
{
    int idx = ctx->dma_log_count % 64;
    ctx->dma_log[idx].direction = dir;
    ctx->dma_log[idx].ls_offset = ls_offset;
    ctx->dma_log[idx].ea        = ea;
    ctx->dma_log[idx].size      = size;
    ctx->dma_log[idx].tag       = tag;
    ctx->dma_log[idx].completed = 1;  /* Synchronous: always complete. */
    ctx->dma_log_count++;
}

/* ------------------------------------------------------------------ */
/*  Lifecycle                                                          */
/* ------------------------------------------------------------------ */

int spu_init(SpuContext *ctx, size_t main_mem_size)
{
    if (!ctx)
        return SPU_ERR_NULL;

    /* Zero the local store. */
    memset(ctx->ls, 0, SPU_LS_SIZE);

    /* Allocate and zero simulated main memory. */
    ctx->main_mem = (uint8_t *)calloc(1, main_mem_size);
    if (!ctx->main_mem)
        return SPU_ERR_NULL;

    ctx->main_mem_size = main_mem_size;
    ctx->dma_log_count = 0;
    memset(ctx->tag_pending, 0, sizeof(ctx->tag_pending));

    return SPU_OK;
}

void spu_destroy(SpuContext *ctx)
{
    if (!ctx)
        return;
    free(ctx->main_mem);
    ctx->main_mem = NULL;
    ctx->main_mem_size = 0;
}

/* ------------------------------------------------------------------ */
/*  DMA GET (main memory -> local store)                               */
/* ------------------------------------------------------------------ */

int spu_dma_get(SpuContext *ctx, uint32_t ls_offset, uint64_t ea,
                uint32_t size, uint32_t tag)
{
    int err = validate_dma_params(ctx, ls_offset, ea, size, tag);
    if (err != SPU_OK)
        return err;

    /* Perform the transfer: copy from main memory to local store. */
    memcpy(&ctx->ls[ls_offset], &ctx->main_mem[ea], size);

    /* Track the transfer. */
    ctx->tag_pending[tag]++;
    log_dma(ctx, SPU_DMA_GET, ls_offset, ea, size, tag);

    return SPU_OK;
}

/* ------------------------------------------------------------------ */
/*  DMA PUT (local store -> main memory)                               */
/* ------------------------------------------------------------------ */

int spu_dma_put(SpuContext *ctx, uint32_t ls_offset, uint64_t ea,
                uint32_t size, uint32_t tag)
{
    int err = validate_dma_params(ctx, ls_offset, ea, size, tag);
    if (err != SPU_OK)
        return err;

    /* Perform the transfer: copy from local store to main memory. */
    memcpy(&ctx->main_mem[ea], &ctx->ls[ls_offset], size);

    /* Track the transfer. */
    ctx->tag_pending[tag]++;
    log_dma(ctx, SPU_DMA_PUT, ls_offset, ea, size, tag);

    return SPU_OK;
}

/* ------------------------------------------------------------------ */
/*  DMA LIST GET (scatter-gather: main memory -> local store)          */
/* ------------------------------------------------------------------ */

int spu_dma_list_get(SpuContext *ctx, uint32_t ls_offset,
                     const SpuDmaListEntry *list, int count, uint32_t tag)
{
    if (!ctx || !list)
        return SPU_ERR_NULL;
    if (tag >= SPU_DMA_MAX_TAGS)
        return SPU_ERR_TAG;
    if (count <= 0 || count > SPU_DMA_LIST_MAX)
        return SPU_ERR_LIST_SIZE;
    if (!check_align(ls_offset))
        return SPU_ERR_ALIGN;

    /* Process each list entry, advancing the local store offset. */
    uint32_t ls_pos = ls_offset;
    for (int i = 0; i < count; i++) {
        uint64_t ea   = list[i].ea;
        uint32_t size = list[i].size;

        /* Validate each segment. */
        if (!check_align(ea))
            return SPU_ERR_ALIGN;
        if (size == 0 || (size & (SPU_DMA_ALIGN - 1)) != 0 || size > SPU_DMA_MAX_SIZE)
            return SPU_ERR_SIZE;
        if ((uint64_t)ls_pos + size > SPU_LS_SIZE)
            return SPU_ERR_BOUNDS;
        if (ea + size > ctx->main_mem_size)
            return SPU_ERR_BOUNDS;

        memcpy(&ctx->ls[ls_pos], &ctx->main_mem[ea], size);
        log_dma(ctx, SPU_DMA_GET, ls_pos, ea, size, tag);
        ls_pos += size;
    }

    ctx->tag_pending[tag]++;
    return SPU_OK;
}

/* ------------------------------------------------------------------ */
/*  DMA LIST PUT (scatter-gather: local store -> main memory)          */
/* ------------------------------------------------------------------ */

int spu_dma_list_put(SpuContext *ctx, uint32_t ls_offset,
                     const SpuDmaListEntry *list, int count, uint32_t tag)
{
    if (!ctx || !list)
        return SPU_ERR_NULL;
    if (tag >= SPU_DMA_MAX_TAGS)
        return SPU_ERR_TAG;
    if (count <= 0 || count > SPU_DMA_LIST_MAX)
        return SPU_ERR_LIST_SIZE;
    if (!check_align(ls_offset))
        return SPU_ERR_ALIGN;

    uint32_t ls_pos = ls_offset;
    for (int i = 0; i < count; i++) {
        uint64_t ea   = list[i].ea;
        uint32_t size = list[i].size;

        if (!check_align(ea))
            return SPU_ERR_ALIGN;
        if (size == 0 || (size & (SPU_DMA_ALIGN - 1)) != 0 || size > SPU_DMA_MAX_SIZE)
            return SPU_ERR_SIZE;
        if ((uint64_t)ls_pos + size > SPU_LS_SIZE)
            return SPU_ERR_BOUNDS;
        if (ea + size > ctx->main_mem_size)
            return SPU_ERR_BOUNDS;

        memcpy(&ctx->main_mem[ea], &ctx->ls[ls_pos], size);
        log_dma(ctx, SPU_DMA_PUT, ls_pos, ea, size, tag);
        ls_pos += size;
    }

    ctx->tag_pending[tag]++;
    return SPU_OK;
}

/* ------------------------------------------------------------------ */
/*  Synchronization                                                    */
/* ------------------------------------------------------------------ */

int spu_dma_wait_tag(SpuContext *ctx, uint32_t tag)
{
    if (!ctx)
        return SPU_ERR_NULL;
    if (tag >= SPU_DMA_MAX_TAGS)
        return SPU_ERR_TAG;

    /*
     * In this synchronous simulation, all transfers complete immediately.
     * We just reset the pending count.
     */
    ctx->tag_pending[tag] = 0;
    return SPU_OK;
}

/* ------------------------------------------------------------------ */
/*  Utility                                                            */
/* ------------------------------------------------------------------ */

const char *spu_strerror(int err)
{
    switch (err) {
    case SPU_OK:            return "OK";
    case SPU_ERR_ALIGN:     return "alignment violation";
    case SPU_ERR_SIZE:      return "invalid transfer size";
    case SPU_ERR_BOUNDS:    return "out of bounds";
    case SPU_ERR_TAG:       return "invalid tag";
    case SPU_ERR_NULL:      return "null pointer";
    case SPU_ERR_LIST_SIZE: return "DMA list too large";
    default:                return "unknown error";
    }
}

void spu_dump_dma_log(const SpuContext *ctx)
{
    if (!ctx) return;

    int total = ctx->dma_log_count;
    int start = (total > 64) ? total - 64 : 0;

    printf("DMA Transfer Log (%d total transfers, showing last %d):\n",
           total, total - start);
    printf("%-5s %-10s %-12s %-10s %-6s\n",
           "Dir", "LS Offset", "EA", "Size", "Tag");
    printf("----------------------------------------------------\n");

    for (int i = start; i < total; i++) {
        const SpuDmaRecord *rec = &ctx->dma_log[i % 64];
        printf("%-5s 0x%08X  0x%08llX  0x%08X  %u\n",
               rec->direction == SPU_DMA_GET ? "GET" : "PUT",
               rec->ls_offset,
               (unsigned long long)rec->ea,
               rec->size,
               rec->tag);
    }
}
