# Lab 45: Dual-CPU Interleaver

## Objective

Implement a cycle-approximate interleaver for two simulated CPUs. Many
classic consoles have multiple processors (e.g., Sega Genesis has a 68000
and a Z80, SNES has a 65816 and an SPC700). Recompilation projects must
interleave their execution based on cycle budgets to preserve timing.

By the end of this lab you will be able to:

- Model instruction streams with per-instruction cycle costs
- Interleave two CPU execution streams based on cycle budgets
- Handle synchronization points where both CPUs must align
- Produce a deterministic execution trace

## Background

In a dual-CPU system, both processors run concurrently at their own clock
rates. For recompilation we can simulate this with **round-robin
interleaving**: each CPU gets a cycle budget, runs instructions until the
budget is exhausted, then the other CPU gets its turn.

### Instruction Format

Each instruction is a dict:

```python
{"name": "mov r0, #5", "cycles": 1}
{"name": "add r1, r2", "cycles": 1}
{"name": "mul r3, r4", "cycles": 3}
{"name": "SYNC",        "cycles": 0}   # synchronization point
```

### Interleaving Rules

1. Each CPU starts with a cycle budget (e.g., 10 cycles per slice).
2. CPU A runs instructions until it exhausts its budget or hits a SYNC.
3. CPU B then runs until it exhausts its budget or hits a SYNC.
4. Repeat until both CPUs have finished their instruction streams.
5. When a CPU hits a SYNC, the other CPU must also reach its next SYNC
   (or end of stream) before either proceeds past the SYNC.

### Output

The interleaver produces an execution trace -- a list of
`(cpu_id, instruction_name, cycle_timestamp)` tuples showing the
global execution order.

## Files

| File             | Description                          |
|------------------|--------------------------------------|
| `interleaver.py` | Dual-CPU interleaver (starter code) |
| `test_lab.py`     | Pytest test suite                   |

## Instructions

1. Open `interleaver.py` and read the starter code.
2. Complete each function marked with a `TODO` comment.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## References

- Sega Genesis dual-CPU timing documentation
- SNES co-processor timing (SA-1, SPC700)
