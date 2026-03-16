/*
 * sync_shim.c -- Synchronization primitives for recompiled game code.
 *
 * Complete the TODO sections using C11 atomics and pthreads.
 */

#include <sched.h>
#include "sync_shim.h"

/* ------------------------------------------------------------------ */
/*  Spinlock                                                           */
/* ------------------------------------------------------------------ */

void spin_init(SpinLock *lock)
{
    /* TODO: initialize lock->locked to 0 (unlocked).
     * Use atomic_store().
     */
}

void spin_lock(SpinLock *lock)
{
    /* TODO: busy-wait until we acquire the lock.
     *
     * Use a loop that tries to atomically swap lock->locked from 0 to 1.
     * atomic_exchange() returns the previous value -- if it was 0, we
     * got the lock.  If it was 1, someone else holds it; keep spinning.
     *
     * Hint: call sched_yield() inside the spin loop to be friendly to
     * other threads (optional but recommended).
     */
}

void spin_unlock(SpinLock *lock)
{
    /* TODO: release the lock by storing 0 into lock->locked.
     * Use atomic_store().
     */
}

int spin_trylock(SpinLock *lock)
{
    /* TODO: try to acquire the lock once (no spinning).
     *
     * Use atomic_exchange() to swap lock->locked from 0 to 1.
     * If the previous value was 0, return 0 (success).
     * Otherwise return -1 (lock was already held).
     */
    return -1;
}

/* ------------------------------------------------------------------ */
/*  Event                                                              */
/* ------------------------------------------------------------------ */

void event_init(Event *evt)
{
    /* TODO:
     * 1. Initialize evt->mutex with pthread_mutex_init.
     * 2. Initialize evt->cond with pthread_cond_init.
     * 3. Set evt->signaled to 0.
     */
}

void event_signal(Event *evt)
{
    /* TODO:
     * 1. Lock the mutex.
     * 2. Set evt->signaled to 1.
     * 3. Call pthread_cond_signal to wake one waiter.
     * 4. Unlock the mutex.
     */
}

void event_wait(Event *evt)
{
    /* TODO:
     * 1. Lock the mutex.
     * 2. While evt->signaled is 0, call pthread_cond_wait
     *    (this releases the mutex while waiting).
     * 3. Reset evt->signaled to 0 (auto-reset behavior).
     * 4. Unlock the mutex.
     */
}

void event_destroy(Event *evt)
{
    /* TODO:
     * 1. Destroy the mutex with pthread_mutex_destroy.
     * 2. Destroy the condvar with pthread_cond_destroy.
     */
}

/* ------------------------------------------------------------------ */
/*  Atomic compare-and-swap                                            */
/* ------------------------------------------------------------------ */

int atomic_cas32(volatile uint32_t *ptr, uint32_t expected, uint32_t desired)
{
    /* TODO: use atomic_compare_exchange_strong to atomically:
     *   if (*ptr == expected) { *ptr = desired; return 1; }
     *   else { return 0; }
     *
     * Note: atomic_compare_exchange_strong takes a pointer to expected
     * and may modify it.  Use a local copy.
     *
     * Cast ptr to (_Atomic uint32_t *) for C11 atomics.
     */
    return 0;
}
