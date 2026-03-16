#ifndef DMA_BRIDGE_H
#define DMA_BRIDGE_H

#include <stdint.h>
#include <stddef.h>

/*
 * dma_bridge.h -- DMA bridge between PPU main memory and SPU local stores.
 *
 * Simulates the Cell processor's Memory Flow Controller (MFC) DMA
 * transfers for recompilation purposes.
 */

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

#define SPU_LS_SIZE         (256 * 1024)   /* 256 KB local store.        */
#define DMA_ALIGN           16             /* DMA alignment requirement. */
#define DMA_MAX_TRANSFER    (16 * 1024)    /* Max single transfer: 16KB. */
#define MAX_SPUS            6              /* Usable SPU count.          */

/* ------------------------------------------------------------------ */
/*  Error codes                                                        */
/* ------------------------------------------------------------------ */

#define DMA_OK              0
#define DMA_ERR_ALIGN       1   /* Alignment violation.            */
#define DMA_ERR_SIZE        2   /* Invalid transfer size.          */
#define DMA_ERR_BOUNDS      3   /* Out-of-bounds access.           */
#define DMA_ERR_SPU_ID      4   /* Invalid SPU index.              */
#define DMA_ERR_NULL        5   /* NULL pointer argument.          */

/* ------------------------------------------------------------------ */
/*  DMA transfer record                                                */
/* ------------------------------------------------------------------ */

typedef enum {
    DMA_DIR_PUT,    /* Main memory -> Local store. */
    DMA_DIR_GET,    /* Local store -> Main memory. */
} DmaDirection;

typedef struct {
    DmaDirection direction;
    int          spu_id;
    uint32_t     ls_offset;
    uint64_t     ea;        /* Effective (main memory) address.   */
    uint32_t     size;
} DmaRecord;

#define DMA_LOG_MAX 64

/* ------------------------------------------------------------------ */
/*  Bridge context                                                     */
/* ------------------------------------------------------------------ */

typedef struct {
    /* SPU local stores -- one per SPU. */
    uint8_t  ls[MAX_SPUS][SPU_LS_SIZE];

    /* Simulated main memory. */
    uint8_t *main_mem;
    size_t   main_mem_size;

    /* Transfer log. */
    DmaRecord log[DMA_LOG_MAX];
    int       log_count;
} DmaBridge;

/* ------------------------------------------------------------------ */
/*  Lifecycle                                                          */
/* ------------------------------------------------------------------ */

/*
 * Initialize the DMA bridge.
 *   - Zeros all local stores.
 *   - Allocates main_mem_size bytes of main memory.
 * Returns DMA_OK on success, DMA_ERR_NULL on allocation failure.
 */
int dma_bridge_init(DmaBridge *bridge, size_t main_mem_size);

/*
 * Destroy the bridge and free main memory.
 */
void dma_bridge_destroy(DmaBridge *bridge);

/* ------------------------------------------------------------------ */
/*  DMA transfers                                                      */
/* ------------------------------------------------------------------ */

/*
 * DMA PUT: Copy `size` bytes from main memory at `ea` into SPU
 * `spu_id`'s local store at `ls_offset`.
 *
 * Validates:
 *   - spu_id is 0..MAX_SPUS-1
 *   - ls_offset and ea are 16-byte aligned
 *   - size is 1, 2, 4, 8, or a multiple of 16 (and <= DMA_MAX_TRANSFER)
 *   - transfers stay within bounds
 */
int dma_put(DmaBridge *bridge, int spu_id,
            uint32_t ls_offset, uint64_t ea, uint32_t size);

/*
 * DMA GET: Copy `size` bytes from SPU `spu_id`'s local store at
 * `ls_offset` into main memory at `ea`.
 *
 * Same validation as dma_put.
 */
int dma_get(DmaBridge *bridge, int spu_id,
            uint32_t ls_offset, uint64_t ea, uint32_t size);

/*
 * DMA WAIT: Barrier -- wait for all pending transfers.
 * In this simulation, transfers are synchronous, so this just
 * validates spu_id and returns DMA_OK.
 */
int dma_wait(DmaBridge *bridge, int spu_id);

/* ------------------------------------------------------------------ */
/*  Utility                                                            */
/* ------------------------------------------------------------------ */

const char *dma_strerror(int err);
void dma_dump_log(const DmaBridge *bridge);

#endif /* DMA_BRIDGE_H */
