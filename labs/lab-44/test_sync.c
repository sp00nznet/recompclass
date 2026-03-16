/*
 * test_sync.c -- Multi-threaded test suite for sync primitives.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include "sync_shim.h"

static int tests_run    = 0;
static int tests_passed = 0;

#define CHECK(cond, msg)                                     \
    do {                                                     \
        tests_run++;                                         \
        if (cond) {                                          \
            tests_passed++;                                  \
        } else {                                             \
            printf("  FAIL: %s\n", (msg));                   \
        }                                                    \
    } while (0)

/* ------------------------------------------------------------------ */
/*  Spinlock: basic                                                    */
/* ------------------------------------------------------------------ */

static void test_spinlock_basic(void)
{
    printf("--- test_spinlock_basic ---\n");

    SpinLock lock;
    spin_init(&lock);

    /* Should be unlocked initially. */
    CHECK(spin_trylock(&lock) == 0, "trylock succeeds on unlocked");

    /* Should fail -- already locked. */
    CHECK(spin_trylock(&lock) == -1, "trylock fails on locked");

    spin_unlock(&lock);

    /* Should succeed again. */
    CHECK(spin_trylock(&lock) == 0, "trylock succeeds after unlock");
    spin_unlock(&lock);
}

/* ------------------------------------------------------------------ */
/*  Spinlock: contention with threads                                  */
/* ------------------------------------------------------------------ */

static SpinLock g_counter_lock;
static volatile int g_counter = 0;

#define INCREMENTS_PER_THREAD 10000
#define NUM_THREADS 4

static void *increment_worker(void *arg)
{
    (void)arg;
    for (int i = 0; i < INCREMENTS_PER_THREAD; i++) {
        spin_lock(&g_counter_lock);
        g_counter++;
        spin_unlock(&g_counter_lock);
    }
    return NULL;
}

static void test_spinlock_contention(void)
{
    printf("--- test_spinlock_contention ---\n");

    spin_init(&g_counter_lock);
    g_counter = 0;

    pthread_t threads[NUM_THREADS];
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, increment_worker, NULL);
    }
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    int expected = INCREMENTS_PER_THREAD * NUM_THREADS;
    CHECK(g_counter == expected, "counter matches expected after contention");
}

/* ------------------------------------------------------------------ */
/*  Event: signal/wait                                                 */
/* ------------------------------------------------------------------ */

static Event g_event;
static volatile int g_event_value = 0;

static void *event_worker(void *arg)
{
    (void)arg;
    /* Wait for the signal, then set the value. */
    event_wait(&g_event);
    g_event_value = 42;
    return NULL;
}

static void test_event_signal(void)
{
    printf("--- test_event_signal ---\n");

    event_init(&g_event);
    g_event_value = 0;

    pthread_t thread;
    pthread_create(&thread, NULL, event_worker, NULL);

    /* Small delay to ensure worker is waiting. */
    usleep(10000);
    CHECK(g_event_value == 0, "worker has not run yet (waiting)");

    /* Signal the event. */
    event_signal(&g_event);
    pthread_join(thread, NULL);

    CHECK(g_event_value == 42, "worker ran after signal");

    event_destroy(&g_event);
}

/* ------------------------------------------------------------------ */
/*  CAS: basic                                                         */
/* ------------------------------------------------------------------ */

static void test_cas_basic(void)
{
    printf("--- test_cas_basic ---\n");

    volatile uint32_t value = 10;

    /* Should succeed: value == expected. */
    int ok = atomic_cas32(&value, 10, 20);
    CHECK(ok == 1, "CAS succeeds when value matches");
    CHECK(value == 20, "value updated to 20");

    /* Should fail: value is 20, not 10. */
    ok = atomic_cas32(&value, 10, 30);
    CHECK(ok == 0, "CAS fails when value doesn't match");
    CHECK(value == 20, "value unchanged after failed CAS");
}

/* ------------------------------------------------------------------ */
/*  CAS: contention                                                    */
/* ------------------------------------------------------------------ */

static volatile uint32_t g_cas_counter = 0;

static void *cas_worker(void *arg)
{
    (void)arg;
    for (int i = 0; i < INCREMENTS_PER_THREAD; i++) {
        uint32_t old_val;
        do {
            old_val = g_cas_counter;
        } while (!atomic_cas32(&g_cas_counter, old_val, old_val + 1));
    }
    return NULL;
}

static void test_cas_contention(void)
{
    printf("--- test_cas_contention ---\n");

    g_cas_counter = 0;

    pthread_t threads[NUM_THREADS];
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, cas_worker, NULL);
    }
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    uint32_t expected = INCREMENTS_PER_THREAD * NUM_THREADS;
    CHECK(g_cas_counter == expected, "CAS counter correct after contention");
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

int main(void)
{
    printf("Thread Sync Shim -- Test Suite\n\n");

    test_spinlock_basic();
    test_spinlock_contention();
    test_event_signal();
    test_cas_basic();
    test_cas_contention();

    printf("\n%d / %d tests passed.\n", tests_passed, tests_run);
    return (tests_passed == tests_run) ? EXIT_SUCCESS : EXIT_FAILURE;
}
