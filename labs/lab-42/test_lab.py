"""
Tests for Lab 42: SPU Task Scheduler
"""

import pytest
from spu_scheduler import SpuTask, SpuScheduler, NUM_SPES


# ---------------------------------------------------------------------------
# Task basics
# ---------------------------------------------------------------------------

class TestSpuTask:
    def test_defaults(self):
        t = SpuTask(0, "prog")
        assert t.task_id == 0
        assert t.status == "pending"
        assert t.assigned_spe is None
        assert t.dma_transfers == []

    def test_with_dma(self):
        t = SpuTask(1, "prog", priority=2, dma_transfers=[64, 128])
        assert t.priority == 2
        assert t.dma_transfers == [64, 128]


# ---------------------------------------------------------------------------
# Submission and dispatch
# ---------------------------------------------------------------------------

class TestSubmit:
    def test_single_task(self):
        s = SpuScheduler()
        t = SpuTask(0, "prog")
        s.submit(t)
        assert t.status == "running"
        assert t.assigned_spe is not None
        assert s.get_free_spe_count() == NUM_SPES - 1

    def test_fill_all_spes(self):
        s = SpuScheduler()
        for i in range(NUM_SPES):
            s.submit(SpuTask(i, f"prog_{i}"))
        assert s.get_free_spe_count() == 0
        assert len(s.get_running_tasks()) == NUM_SPES

    def test_overflow_to_pending(self):
        s = SpuScheduler()
        for i in range(NUM_SPES + 2):
            s.submit(SpuTask(i, f"prog_{i}"))
        assert s.get_free_spe_count() == 0
        assert len(s.pending_queue) == 2

    def test_priority_order(self):
        s = SpuScheduler()
        # Submit low-priority first, then high-priority
        t_low = SpuTask(0, "low", priority=10)
        t_high = SpuTask(1, "high", priority=1)
        s.submit(t_low)
        s.submit(t_high)
        # Both should be running (only 2 of 6 slots used)
        assert t_low.status == "running"
        assert t_high.status == "running"


class TestPriorityDispatch:
    def test_high_priority_dispatched_first(self):
        s = SpuScheduler()
        # Fill all SPEs
        tasks = [SpuTask(i, f"prog_{i}") for i in range(NUM_SPES)]
        for t in tasks:
            s.submit(t)

        # Submit two pending tasks with different priorities
        t_low = SpuTask(100, "low", priority=5)
        t_high = SpuTask(101, "high", priority=1)
        s.submit(t_low)
        s.submit(t_high)

        assert t_low.status == "pending"
        assert t_high.status == "pending"

        # Complete one running task to free a slot
        s.complete_task(0)

        # The high-priority task should have been dispatched
        assert t_high.status == "running"
        assert t_low.status == "pending"

    def test_fifo_within_same_priority(self):
        s = SpuScheduler()
        # Fill all SPEs
        for i in range(NUM_SPES):
            s.submit(SpuTask(i, f"prog_{i}"))

        # Two tasks with same priority
        t_first = SpuTask(100, "first", priority=3)
        t_second = SpuTask(101, "second", priority=3)
        s.submit(t_first)
        s.submit(t_second)

        # Free one slot
        s.complete_task(0)
        assert t_first.status == "running"
        assert t_second.status == "pending"


# ---------------------------------------------------------------------------
# DMA lifecycle
# ---------------------------------------------------------------------------

class TestDmaLifecycle:
    def test_start_dma(self):
        s = SpuScheduler()
        t = SpuTask(0, "prog", dma_transfers=[64])
        s.submit(t)
        s.start_dma(0)
        assert t.status == "waiting_dma"

    def test_complete_dma(self):
        s = SpuScheduler()
        t = SpuTask(0, "prog", dma_transfers=[64])
        s.submit(t)
        s.start_dma(0)
        s.complete_dma(0)
        assert t.status == "completed"
        assert t.assigned_spe is None
        assert s.get_free_spe_count() == NUM_SPES

    def test_start_dma_wrong_status(self):
        s = SpuScheduler()
        t = SpuTask(0, "prog")
        s.submit(t)
        s.start_dma(0)  # now waiting_dma
        with pytest.raises(ValueError):
            s.start_dma(0)  # already waiting_dma

    def test_complete_dma_wrong_status(self):
        s = SpuScheduler()
        t = SpuTask(0, "prog")
        s.submit(t)
        # Task is "running", not "waiting_dma"
        with pytest.raises(ValueError):
            s.complete_dma(0)


# ---------------------------------------------------------------------------
# Direct completion
# ---------------------------------------------------------------------------

class TestCompleteTask:
    def test_complete_running(self):
        s = SpuScheduler()
        t = SpuTask(0, "prog")
        s.submit(t)
        s.complete_task(0)
        assert t.status == "completed"
        assert s.get_free_spe_count() == NUM_SPES

    def test_dispatches_pending_after_completion(self):
        s = SpuScheduler()
        for i in range(NUM_SPES + 1):
            s.submit(SpuTask(i, f"prog_{i}"))

        assert len(s.pending_queue) == 1
        s.complete_task(0)
        # The pending task should now be running
        assert len(s.pending_queue) == 0
        assert s.get_free_spe_count() == 0


# ---------------------------------------------------------------------------
# Status lookup
# ---------------------------------------------------------------------------

class TestGetTaskStatus:
    def test_running(self):
        s = SpuScheduler()
        s.submit(SpuTask(0, "prog"))
        assert s.get_task_status(0) == "running"

    def test_pending(self):
        s = SpuScheduler()
        for i in range(NUM_SPES):
            s.submit(SpuTask(i, f"prog_{i}"))
        s.submit(SpuTask(99, "pending_prog"))
        assert s.get_task_status(99) == "pending"

    def test_completed(self):
        s = SpuScheduler()
        s.submit(SpuTask(0, "prog"))
        s.complete_task(0)
        assert s.get_task_status(0) == "completed"

    def test_not_found(self):
        s = SpuScheduler()
        assert s.get_task_status(999) is None


# ---------------------------------------------------------------------------
# Completed task list
# ---------------------------------------------------------------------------

class TestCompletedTasks:
    def test_initially_empty(self):
        s = SpuScheduler()
        assert s.get_completed_tasks() == []

    def test_after_completions(self):
        s = SpuScheduler()
        s.submit(SpuTask(0, "a"))
        s.submit(SpuTask(1, "b"))
        s.complete_task(0)
        s.complete_task(1)
        completed = s.get_completed_tasks()
        assert len(completed) == 2
        ids = [t.task_id for t in completed]
        assert 0 in ids
        assert 1 in ids
