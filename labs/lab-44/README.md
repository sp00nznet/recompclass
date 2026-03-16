# Lab 44: Thread Synchronization Shim

## Objective

Implement synchronization primitives that recompiled multi-threaded game
code can use. Many console games use custom threading and synchronization
that must be faithfully reproduced in a recomp. This lab builds the
low-level primitives: spinlocks, event signals, and atomic CAS.

By the end of this lab you will be able to:

- Implement a spinlock using C11 atomics
- Build an event signal/wait mechanism using mutexes and condition variables
- Implement atomic compare-and-swap
- Test synchronization correctness with multiple threads

## Background

Console games often rely on custom synchronization primitives provided by
the OS or kernel. When recompiling, we replace these with host-OS
equivalents. The key primitives are:

### Spinlock

A busy-wait lock. The thread spins in a tight loop until the lock becomes
available. Good for very short critical sections.

```c
void spin_lock(SpinLock *lock);    // acquire (busy-wait)
void spin_unlock(SpinLock *lock);  // release
int  spin_trylock(SpinLock *lock); // try once, return 0 on success
```

### Event

A signaling mechanism. One thread waits for an event; another thread
signals it.

```c
void event_init(Event *evt);
void event_signal(Event *evt);     // wake one waiter
void event_wait(Event *evt);       // block until signaled
void event_destroy(Event *evt);
```

### Atomic Compare-and-Swap (CAS)

Atomically: if `*ptr == expected`, set `*ptr = desired` and return 1.
Otherwise return 0.

```c
int atomic_cas32(volatile uint32_t *ptr, uint32_t expected, uint32_t desired);
```

## Files

| File          | Description                              |
|---------------|------------------------------------------|
| `sync_shim.h` | API declarations                        |
| `sync_shim.c` | Implementation (starter code)           |
| `test_sync.c`  | Multi-threaded test suite               |
| `Makefile`      | Build and test targets                  |

## Instructions

1. Read `sync_shim.h` to understand the structures and API.
2. Complete the `TODO` sections in `sync_shim.c`.
3. Build and test:
   ```bash
   make
   make test
   ```

## Expected Output

```
Thread Sync Shim -- Test Suite

--- test_spinlock_basic ---
--- test_spinlock_contention ---
--- test_event_signal ---
--- test_cas_basic ---
--- test_cas_contention ---

5 / 5 tests passed.
```

## References

- C11 `<stdatomic.h>` specification
- pthreads documentation (mutex, condvar)
