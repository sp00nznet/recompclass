"""
Lab 42: SPU Task Scheduler

Simulate the PS3 Cell's SPE task scheduling.  The scheduler manages 6 SPE
contexts and a priority queue of tasks.
"""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NUM_SPES = 6


# ---------------------------------------------------------------------------
# Task class
# ---------------------------------------------------------------------------

class SpuTask:
    """Represents a task to be run on an SPE.

    Attributes
    ----------
    task_id : int
        Unique identifier.
    program : str
        Name of the SPE program (simulated).
    priority : int
        Scheduling priority (0 = highest).
    dma_transfers : list of int
        Sizes of DMA transfers the task will perform.
    status : str
        One of 'pending', 'running', 'waiting_dma', 'completed'.
    assigned_spe : int or None
        Which SPE (0-5) this task is assigned to, or None.
    """

    def __init__(self, task_id, program, priority=0, dma_transfers=None):
        self.task_id = task_id
        self.program = program
        self.priority = priority
        self.dma_transfers = dma_transfers or []
        self.status = "pending"
        self.assigned_spe = None

    def __repr__(self):
        return (f"SpuTask(id={self.task_id}, prog='{self.program}', "
                f"pri={self.priority}, status='{self.status}', "
                f"spe={self.assigned_spe})")


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class SpuScheduler:
    """Simple priority-based SPE task scheduler.

    Attributes
    ----------
    spe_slots : list
        Length-6 list; each entry is either None (free) or an SpuTask.
    pending_queue : list of SpuTask
        Tasks waiting to be dispatched.
    completed : list of SpuTask
        Tasks that have finished.
    """

    def __init__(self):
        self.spe_slots = [None] * NUM_SPES
        self.pending_queue = []
        self.completed = []

    def submit(self, task):
        """Submit a task to the scheduler.

        The task is added to the pending queue.  The scheduler should then
        attempt to dispatch it (call _try_dispatch).

        Parameters
        ----------
        task : SpuTask
        """
        # TODO:
        # 1. Set task.status to "pending".
        # 2. Append to self.pending_queue.
        # 3. Call self._try_dispatch().
        pass

    def _try_dispatch(self):
        """Try to dispatch pending tasks to free SPE slots.

        Sort the pending queue by (priority, task_id) so that:
        - Lower priority number goes first.
        - Among equal priorities, lower task_id (earlier submission) goes first.

        For each free SPE slot, pop the highest-priority pending task and
        assign it.
        """
        # TODO:
        # 1. Sort self.pending_queue by (priority, task_id).
        # 2. For each SPE slot that is None:
        #    a. If there are pending tasks, pop the first one.
        #    b. Assign it to this slot: set task.assigned_spe, set
        #       task.status to "running", store it in self.spe_slots.
        pass

    def get_free_spe_count(self):
        """Return the number of free (unoccupied) SPE slots.

        Returns
        -------
        int
        """
        # TODO: count None entries in self.spe_slots
        pass

    def get_running_tasks(self):
        """Return a list of tasks currently assigned to SPEs.

        Returns
        -------
        list of SpuTask
        """
        # TODO: return non-None entries from self.spe_slots
        pass

    def start_dma(self, task_id):
        """Transition a running task to 'waiting_dma' status.

        Parameters
        ----------
        task_id : int

        Raises
        ------
        ValueError
            If the task is not in 'running' status.
        """
        # TODO: find the task in spe_slots by task_id.
        # If found and status == "running", set status to "waiting_dma".
        # Otherwise raise ValueError.
        pass

    def complete_dma(self, task_id):
        """Complete DMA for a task, marking it done and freeing the SPE.

        Parameters
        ----------
        task_id : int

        Raises
        ------
        ValueError
            If the task is not in 'waiting_dma' status.

        After completing:
        1. Set task status to "completed".
        2. Clear task.assigned_spe.
        3. Remove it from spe_slots (set slot to None).
        4. Append it to self.completed.
        5. Call _try_dispatch() to schedule pending tasks.
        """
        # TODO: implement the steps above
        pass

    def complete_task(self, task_id):
        """Directly complete a running task (no DMA phase).

        Same as complete_dma but for tasks in 'running' status.
        """
        # TODO: same as complete_dma but check for "running" status
        pass

    def get_task_status(self, task_id):
        """Look up a task by ID and return its status string.

        Searches pending queue, SPE slots, and completed list.

        Returns
        -------
        str or None
            The task's status, or None if not found.
        """
        # TODO: search all three collections for the task_id
        pass

    def get_completed_tasks(self):
        """Return the list of completed tasks.

        Returns
        -------
        list of SpuTask
        """
        # TODO
        pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sched = SpuScheduler()

    for i in range(8):
        t = SpuTask(task_id=i, program=f"prog_{i}", priority=i % 3,
                    dma_transfers=[64, 128])
        sched.submit(t)

    print(f"Free SPEs: {sched.get_free_spe_count()}")
    print(f"Running: {sched.get_running_tasks()}")
    print(f"Pending: {len(sched.pending_queue)} tasks")

    # Complete first two tasks
    sched.start_dma(0)
    sched.complete_dma(0)
    sched.complete_task(1)

    print(f"\nAfter completions:")
    print(f"Free SPEs: {sched.get_free_spe_count()}")
    print(f"Running: {sched.get_running_tasks()}")
    print(f"Completed: {sched.get_completed_tasks()}")
