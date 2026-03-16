# Lab 29: Mini-Project Planner

## Objective

Fill out a structured project plan template for your chosen recompilation
target. This lab is less code and more planning -- but disciplined
planning is the difference between a recomp project that ships and one
that stalls at 30%.

## Background

Every successful recompilation project starts with a clear plan:

- **What** binary are you targeting?
- **What architecture** is it for?
- **What tools** will you use (disassembler, compiler, build system)?
- **What milestones** will you hit along the way?
- **What risks** could block you?

The `analysis_checklist.py` script validates that your plan covers all
required sections. Think of it as a linter for project proposals.

## Instructions

1. Open `project_plan.md` and fill in every section marked with
   `[TODO: ...]`.
2. You can use a real target you are interested in, or pick a
   hypothetical one (e.g., a Game Boy homebrew, a GBA game, an N64
   title).
3. Run the checklist validator to confirm your plan is complete:
   ```
   python analysis_checklist.py project_plan.md
   ```
4. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Required Sections

Your project plan must contain all of these sections (as Markdown
headings):

1. `## Target Binary` -- what you are recompiling
2. `## Architecture` -- CPU architecture and key details
3. `## Tool Selection` -- disassembler, compiler, libraries
4. `## Milestones` -- at least 3 numbered milestones
5. `## Risk Assessment` -- at least 2 identified risks
6. `## Success Criteria` -- how you know you are done

## Expected Output

```
$ python analysis_checklist.py project_plan.md
Checking project_plan.md...
[PASS] Section found: Target Binary
[PASS] Section found: Architecture
[PASS] Section found: Tool Selection
[PASS] Section found: Milestones (3 items found)
[PASS] Section found: Risk Assessment (2 items found)
[PASS] Section found: Success Criteria

All checks passed! Your project plan is complete.
```
