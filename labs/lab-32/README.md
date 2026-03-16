# Lab 32: Dead Code Eliminator

## Objective

Write a pass that identifies unreachable functions in a call graph. After
lifting, a recomp project often contains functions that are never called
from the entry point -- interrupt handlers that got replaced by shims,
debug routines, or code the disassembler misidentified. Removing them
shrinks compile times and binary size.

## Background

A **call graph** is a directed graph where nodes are functions and edges
represent calls. Given an entry point, any function not reachable by
following call edges from the entry is "dead code."

This is a standard graph reachability problem. You can solve it with
BFS or DFS from the entry point, then report any functions not visited.

### Input Format

The call graph is represented as JSON:

```json
{
  "entry": "main",
  "functions": {
    "main": ["init", "game_loop"],
    "init": ["load_assets"],
    "game_loop": ["update", "render"],
    "update": [],
    "render": ["draw_sprite"],
    "draw_sprite": [],
    "load_assets": [],
    "debug_dump": ["debug_print"],
    "debug_print": []
  }
}
```

In this example, `debug_dump` and `debug_print` are dead code.

## Instructions

1. Open `dead_code.py` and implement the TODO functions.
2. `load_call_graph()` -- parse the JSON call graph.
3. `find_reachable()` -- BFS/DFS from the entry point.
4. `find_dead_code()` -- return the set of unreachable functions.
5. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output

```
Entry point: main
Reachable functions (7):
  main, init, game_loop, load_assets, update, render, draw_sprite
Dead code (2):
  debug_dump, debug_print
```
