# Lab 42: SPU Task Scheduler

## Objective

Implement a simple task scheduler for the PS3's SPE (Synergistic
Processing Element) units. The PS3's Cell processor has 6 usable SPEs,
each capable of running one task at a time. A scheduler is needed to
assign tasks to available SPEs, manage priorities, and handle completion.

By the end of this lab you will be able to:

- Model SPE contexts and task queues
- Implement priority-based task scheduling
- Handle DMA completion callbacks
- Manage a pool of hardware execution units

## Background

The PS3's Cell processor has one PPU (PowerPC Processing Unit) and six
usable SPEs. Each SPE runs independently with its own local store and
instruction stream. The PPU acts as a coordinator, dispatching tasks to
SPEs and collecting results.

In a recompilation context, we simulate this scheduling to preserve the
game's concurrency model -- if the game expected 6 parallel tasks, our
recompiled version should too.

### Task Model

Each task has:

- **task_id**: unique integer identifier
- **program**: string name of the SPE program (simulated)
- **priority**: integer (lower = higher priority, 0 is highest)
- **dma_transfers**: list of simulated DMA operations, each with a size
- **status**: one of "pending", "running", "waiting_dma", "completed"

### Scheduler Rules

1. Tasks are dispatched to SPEs in priority order (lowest number first).
2. If all 6 SPEs are busy, the task stays in the pending queue.
3. When a task starts, its status becomes "running".
4. When a task initiates DMA transfers, status becomes "waiting_dma".
5. When DMA completes (simulated by calling `complete_dma`), the task
   status becomes "completed" and the SPE is freed.
6. If multiple tasks have the same priority, dispatch in FIFO order.

## Files

| File               | Description                          |
|--------------------|--------------------------------------|
| `spu_scheduler.py` | SPU task scheduler (starter code)   |
| `test_lab.py`       | Pytest test suite                   |

## Instructions

1. Open `spu_scheduler.py` and read the starter code.
2. Complete each method marked with a `TODO` comment.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## References

- Cell Broadband Engine Programming Handbook (IBM)
- libspe2 documentation
