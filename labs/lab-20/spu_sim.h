#ifndef SPU_SIM_H
#define SPU_SIM_H

#include <stdint.h>
#include <stddef.h>

/*
 * spu_sim.h -- SPU Local Store and DMA transfer simulator.
 *
 * This header defines the structures and functions for simulating the PS3
 * SPU's 256KB local store and its DMA engine.  The DMA engine moves data
 * between the SPU's local store and main memory.
 */

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

#define SPU_LS_SIZE         (256 * 1024)   /* 256 KB local store.         */
#define SPU_DMA_ALIGN       16             /* DMA alignment requirement.  */
#define SPU_DMA_MAX_SIZE    (16 * 1024)    /* Max single transfer: 16 KB. */
#define SPU_DMA_MAX_TAGS    32             /* Tag values 0-31.            */
#define SPU_DMA_LIST_MAX    16             /* Max entries in a DMA list.  */

/* ------------------------------------------------------------------ */
/*  Error codes                                                        */
/* ------------------------------------------------------------------ */

#define SPU_OK                  0
#define SPU_ERR_ALIGN           1   /* Alignment violation.             */
#define SPU_ERR_SIZE            2   /* Invalid transfer size.           */
#define SPU_ERR_BOUNDS          3   /* Out of local store bounds.       */
#define SPU_ERR_TAG             4   /* Invalid tag number.              */
#define SPU_ERR_NULL            5   /* NULL pointer.                    */
#define SPU_ERR_LIST_SIZE       6   /* DMA list too large.              */

/* ------------------------------------------------------------------ */
/*  DMA list entry                                                     */
/* ------------------------------------------------------------------ */

/*
 * A DMA list entry specifies one segment of a scatter/gather transfer.
 * Each entry gives a main-memory address and a size; the local store
 * offset advances sequentially.
 */
typedef struct {
    uint64_t ea;     /* Effective (main memory) address.     */
    uint32_t size;   /* Size of this segment in bytes.       */
} SpuDmaListEntry;

/* ------------------------------------------------------------------ */
/*  DMA transfer record (for tracking/debugging)                       */
/* ------------------------------------------------------------------ */

typedef enum {
    SPU_DMA_GET,     /* Main memory -> local store. */
    SPU_DMA_PUT,     /* Local store -> main memory. */
} SpuDmaDirection;

typedef struct {
    SpuDmaDirection direction;
    uint32_t        ls_offset;     /* Offset within local store. */
    uint64_t        ea;            /* Main memory address.       */
    uint32_t        size;          /* Transfer size in bytes.    */
    uint32_t        tag;           /* DMA tag (0-31).            */
    int             completed;     /* 1 if transfer is done.     */
} SpuDmaRecord;

/* ------------------------------------------------------------------ */
/*  SPU context                                                        */
/* ------------------------------------------------------------------ */

/*
 * SpuContext represents one SPU's state: its local store, a simulated
 * main memory buffer, and DMA tracking information.
 */
typedef struct {
    /* The 256 KB local store, 16-byte aligned. */
    uint8_t  ls[SPU_LS_SIZE] __attribute__((aligned(SPU_DMA_ALIGN)));

    /* Simulated main memory (allocated at init). */
    uint8_t *main_mem;
    size_t   main_mem_size;

    /* DMA transfer log (circular buffer for debugging). */
    SpuDmaRecord dma_log[64];
    int          dma_log_count;

    /* Per-tag transfer counts (for tag group tracking). */
    int tag_pending[SPU_DMA_MAX_TAGS];

} SpuContext;

/* ------------------------------------------------------------------ */
/*  Lifecycle                                                          */
/* ------------------------------------------------------------------ */

/*
 * Initialize an SPU context.
 *   - Zeroes the local store.
 *   - Allocates `main_mem_size` bytes of simulated main memory.
 * Returns SPU_OK on success, SPU_ERR_NULL on allocation failure.
 */
int spu_init(SpuContext *ctx, size_t main_mem_size);

/*
 * Destroy an SPU context and free simulated main memory.
 */
void spu_destroy(SpuContext *ctx);

/* ------------------------------------------------------------------ */
/*  DMA transfers                                                      */
/* ------------------------------------------------------------------ */

/*
 * DMA GET: Transfer `size` bytes from main memory at effective address `ea`
 * into the local store at offset `ls_offset`.
 *
 * Constraints:
 *   - ls_offset must be 16-byte aligned.
 *   - ea must be 16-byte aligned.
 *   - size must be 16, or a multiple of 16, and <= SPU_DMA_MAX_SIZE.
 *   - ls_offset + size must not exceed SPU_LS_SIZE.
 *   - ea + size must not exceed main_mem_size.
 *
 * Returns SPU_OK on success, or an error code.
 */
int spu_dma_get(SpuContext *ctx, uint32_t ls_offset, uint64_t ea,
                uint32_t size, uint32_t tag);

/*
 * DMA PUT: Transfer `size` bytes from the local store at offset `ls_offset`
 * to main memory at effective address `ea`.
 *
 * Same constraints as spu_dma_get.
 */
int spu_dma_put(SpuContext *ctx, uint32_t ls_offset, uint64_t ea,
                uint32_t size, uint32_t tag);

/*
 * DMA LIST GET: Scatter-gather transfer from main memory to local store.
 *
 * Transfers `count` segments described by `list` into contiguous local
 * store memory starting at `ls_offset`.
 */
int spu_dma_list_get(SpuContext *ctx, uint32_t ls_offset,
                     const SpuDmaListEntry *list, int count, uint32_t tag);

/*
 * DMA LIST PUT: Scatter-gather transfer from local store to main memory.
 */
int spu_dma_list_put(SpuContext *ctx, uint32_t ls_offset,
                     const SpuDmaListEntry *list, int count, uint32_t tag);

/* ------------------------------------------------------------------ */
/*  Synchronization (simplified)                                       */
/* ------------------------------------------------------------------ */

/*
 * Wait for all DMA transfers with the given tag to complete.
 * In this simulation, transfers are synchronous, so this is a no-op
 * that simply resets the pending count for the tag.
 */
int spu_dma_wait_tag(SpuContext *ctx, uint32_t tag);

/* ------------------------------------------------------------------ */
/*  Utility                                                            */
/* ------------------------------------------------------------------ */

/* Return a human-readable error string. */
const char *spu_strerror(int err);

/* Print the DMA transfer log. */
void spu_dump_dma_log(const SpuContext *ctx);

/* ------------------------------------------------------------------ */
/*  TODO: Advanced features                                            */
/* ------------------------------------------------------------------ */

/* TODO: DMA tag group masks (wait for any/all of a set of tags). */
/* TODO: Asynchronous DMA with completion callbacks.               */
/* TODO: SPU mailbox communication (SPU <-> PPU message passing).  */
/*       int spu_write_outbound_mbox(SpuContext *ctx, uint32_t value); */
/*       int spu_read_inbound_mbox(SpuContext *ctx, uint32_t *value);  */

#endif /* SPU_SIM_H */
