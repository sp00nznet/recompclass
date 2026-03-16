#ifndef SYNC_SHIM_H
#define SYNC_SHIM_H

#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>

/*
 * sync_shim.h -- Synchronization primitives for recompiled game code.
 */

/* ------------------------------------------------------------------ */
/*  Spinlock                                                           */
/* ------------------------------------------------------------------ */

typedef struct {
    atomic_int locked;   /* 0 = unlocked, 1 = locked */
} SpinLock;

/* Initialize a spinlock (unlocked state). */
void spin_init(SpinLock *lock);

/* Acquire the spinlock (busy-wait). */
void spin_lock(SpinLock *lock);

/* Release the spinlock. */
void spin_unlock(SpinLock *lock);

/* Try to acquire without blocking.  Returns 0 on success, -1 on failure. */
int spin_trylock(SpinLock *lock);

/* ------------------------------------------------------------------ */
/*  Event                                                              */
/* ------------------------------------------------------------------ */

typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t  cond;
    int             signaled;   /* 0 = not signaled, 1 = signaled */
} Event;

/* Initialize an event (unsignaled state). */
void event_init(Event *evt);

/* Signal the event, waking one waiting thread. */
void event_signal(Event *evt);

/* Wait until the event is signaled.  Resets to unsignaled after wake. */
void event_wait(Event *evt);

/* Destroy the event (free mutex/condvar resources). */
void event_destroy(Event *evt);

/* ------------------------------------------------------------------ */
/*  Atomic compare-and-swap                                            */
/* ------------------------------------------------------------------ */

/*
 * Atomically compare *ptr with expected.  If equal, set *ptr to desired
 * and return 1.  Otherwise return 0.
 */
int atomic_cas32(volatile uint32_t *ptr, uint32_t expected, uint32_t desired);

#endif /* SYNC_SHIM_H */
